#!/usr/bin/env python3
"""
Orchestratore delle pipeline di enrichment giornaliere (info_MIB).

Per ogni categoria di documenti del repository scarica le fonti ORIGINALI
(dataset grezzi e report PDF), verifica l'integrità dei file, aggiorna i
manifest e produce un report di esecuzione. È idempotente (salta i file già
presenti e validi) e sicuro in ambienti senza rete (registra i target non
raggiungibili senza interrompersi).

Le fonti provengono da tre origini, unificate nello stesso formato:
  1. `enrichment_registry.py`          → categorie generali + ANIA
  2. `download_gimbe_pdfs.GIMBE_PDFS`  → categoria "gimbe"
  3. `download_pdta.PDTA_DOWNLOADS`    → categoria "pdta"

Uso:
    python3 scripts/run_enrichment.py                     # esegue tutte le categorie
    python3 scripts/run_enrichment.py --category ania     # solo una categoria
    python3 scripts/run_enrichment.py --list              # elenca i target
    python3 scripts/run_enrichment.py --dry-run           # simula senza scaricare
    python3 scripts/run_enrichment.py --report-only       # solo stato dei file locali
    python3 scripts/run_enrichment.py --force             # riscarica anche se presenti

Output:
    datasets/raw/enrichment_manifest.json   (stato consolidato, versionato)
    logs/enrichment_YYYY-MM-DD.json         (report di esecuzione, gitignored)
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import ssl
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS_DIR = os.path.join(BASE_DIR, "scripts")
RAW_DIR = os.path.join(BASE_DIR, "datasets", "raw")
LOGS_DIR = os.path.join(BASE_DIR, "logs")
MANIFEST_PATH = os.path.join(RAW_DIR, "enrichment_manifest.json")

sys.path.insert(0, SCRIPTS_DIR)

import enrichment_registry as reg  # noqa: E402

TODAY = datetime.now(timezone.utc).strftime("%Y-%m-%d")
REPORT_PATH = os.path.join(LOGS_DIR, f"enrichment_{TODAY}.json")

REQUEST_TIMEOUT = 120
MAX_RETRIES = 3
DEFAULT_DELAY = 1.0
USER_AGENT = (
    "Mozilla/5.0 (compatible; InfoMIB-Enrichment/1.0; "
    "+https://github.com/giumar11/info_MIB)"
)

# Firme (magic bytes) per validare i formati scaricati.
MAGIC = {
    "pdf": b"%PDF",
    "zip": b"PK\x03\x04",
    "xlsx": b"PK\x03\x04",
    "xml": None,   # validato come testo che inizia con "<"
    "csv": None,
    "json": None,
}


def build_tls_context() -> ssl.SSLContext:
    """Contesto TLS con verifica attiva, compatibile con proxy gestiti."""
    ctx = ssl.create_default_context()
    ca_bundle = os.environ.get("SSL_CERT_FILE") or os.environ.get("REQUESTS_CA_BUNDLE")
    if ca_bundle and os.path.exists(ca_bundle):
        try:
            ctx.load_verify_locations(ca_bundle)
        except (ssl.SSLError, OSError):
            pass
    return ctx


# ----------------------------------------------------------------------------
# Costruzione dei target unificati
# ----------------------------------------------------------------------------

def _target(category, cat_label, src, dest):
    return {
        "category": category,
        "category_label": cat_label,
        "id": src["id"],
        "title": src["title"],
        "kind": src.get("kind", "report"),
        "expected": src.get("expected", "pdf"),
        "filename": src["filename"],
        "url": src.get("url"),
        "source_page": src.get("source_page"),
        "verified": bool(src.get("verified")),
        "min_bytes": src.get("min_bytes", 1000),
        "frequency": src.get("frequency", ""),
        "dest": dest,
    }


def load_registry_targets():
    targets = []
    for cat_key, cat, src in reg.iter_targets():
        dest = reg.resolve_dest(cat, src)
        targets.append(_target(cat_key, cat["label"], src, dest))
    return targets


def load_gimbe_targets():
    """Adatta la lista GIMBE_PDFS (URL diretti verificati) al formato target."""
    targets = []
    try:
        import download_gimbe_pdfs as gimbe
    except Exception as e:  # pragma: no cover
        print(f"  [warn] impossibile importare download_gimbe_pdfs: {e}")
        return targets
    dest_dir = os.path.join(RAW_DIR, "gimbe", "pdf")
    for pdf in gimbe.GIMBE_PDFS:
        src = {
            "id": f"GIMBE_{pdf['year']}_{pdf.get('category', '')}".upper().replace(" ", "_"),
            "title": f"GIMBE {pdf.get('edition', '')} ({pdf['year']})",
            "kind": "report",
            "expected": "pdf",
            "filename": pdf["filename"],
            "url": pdf["url"],
            "source_page": "https://www.gimbe.org/osservatorio",
            "verified": True,
            "min_bytes": 1000,
            "frequency": "annual",
        }
        targets.append(_target("gimbe", "Fondazione GIMBE - rapporti e osservatorio",
                               src, os.path.join(dest_dir, pdf["filename"])))
    return targets


def load_pdta_targets():
    """Adatta PDTA_DOWNLOADS (URL diretti verificati) al formato target."""
    targets = []
    try:
        import download_pdta as pdta
    except Exception as e:  # pragma: no cover
        print(f"  [warn] impossibile importare download_pdta: {e}")
        return targets
    for level, groups in pdta.PDTA_DOWNLOADS.items():
        for key, items in groups.items():
            if not items:
                continue
            if level == "nazionale":
                dest_dir = os.path.join(RAW_DIR, "pdta", "nazionale", key)
            else:
                dest_dir = os.path.join(RAW_DIR, "pdta", "regionale", key)
            for item in items:
                src = {
                    "id": item["id"],
                    "title": item["title"],
                    "kind": "report",
                    "expected": "pdf",
                    "filename": item["filename"],
                    "url": item["url"],
                    "source_page": item["url"],
                    "verified": True,
                    "min_bytes": 1000,
                    "frequency": "periodic",
                }
                targets.append(_target(
                    "pdta", f"PDTA {level}/{key}", src,
                    os.path.join(dest_dir, item["filename"])))
    return targets


def all_targets():
    return load_registry_targets() + load_gimbe_targets() + load_pdta_targets()


# ----------------------------------------------------------------------------
# Download e validazione
# ----------------------------------------------------------------------------

def validate_file(path, expected, min_bytes):
    """Verifica dimensione minima e firma del file. Ritorna (ok, motivo)."""
    if not os.path.exists(path):
        return False, "assente"
    size = os.path.getsize(path)
    if size < min_bytes:
        return False, f"troppo piccolo ({size} < {min_bytes} byte)"
    magic = MAGIC.get(expected)
    try:
        with open(path, "rb") as f:
            head = f.read(16)
    except OSError as e:
        return False, f"lettura fallita: {e}"
    if magic is not None:
        if not head.startswith(magic):
            return False, f"firma {expected} non valida"
    elif expected == "xml":
        stripped = head.lstrip()
        if not (stripped.startswith(b"<") or stripped.startswith(b"\xef\xbb\xbf<")):
            return False, "contenuto XML non valido"
    # Rifiuta pagine HTML di errore salvate come file (comune con 404 mascherati)
    if expected in ("pdf", "xml", "zip", "xlsx", "csv"):
        low = head.lstrip().lower()
        if low.startswith(b"<!doctype html") or low.startswith(b"<html"):
            return False, "ricevuto HTML invece del file atteso"
    return True, f"ok ({size} byte)"


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def download(url, dest, ctx, min_bytes):
    """Scarica url→dest con retry. Ritorna (ok, size, motivo)."""
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    tmp = dest + ".part"
    headers = {"User-Agent": USER_AGENT, "Accept": "*/*"}
    last_err = "sconosciuto"
    for attempt in range(MAX_RETRIES):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, context=ctx, timeout=REQUEST_TIMEOUT) as resp:
                data = resp.read()
            if len(data) < min_bytes:
                last_err = f"risposta troppo piccola ({len(data)} byte)"
            else:
                with open(tmp, "wb") as f:
                    f.write(data)
                os.replace(tmp, dest)
                return True, len(data), "scaricato"
        except urllib.error.HTTPError as e:
            last_err = f"HTTP {e.code}"
            if e.code in (401, 403, 404, 410):
                break
        except urllib.error.URLError as e:
            last_err = f"rete: {getattr(e, 'reason', e)}"
        except (ssl.SSLError, OSError) as e:
            last_err = f"io: {e}"
        if attempt < MAX_RETRIES - 1:
            time.sleep(2 ** (attempt + 1))
    if os.path.exists(tmp):
        try:
            os.remove(tmp)
        except OSError:
            pass
    return False, 0, last_err


# ----------------------------------------------------------------------------
# Esecuzione
# ----------------------------------------------------------------------------

def process(targets, dry_run=False, force=False, report_only=False, delay=DEFAULT_DELAY):
    ctx = build_tls_context()
    results = []
    n = len(targets)
    for i, t in enumerate(targets, 1):
        dest = t["dest"]
        rel = os.path.relpath(dest, BASE_DIR)
        entry = {
            "id": t["id"],
            "category": t["category"],
            "title": t["title"],
            "kind": t["kind"],
            "path": rel,
            "url": t["url"],
            "source_page": t["source_page"],
            "verified_url": t["verified"],
            "status": None,
            "detail": None,
            "size_bytes": None,
            "sha256": None,
        }

        exists = os.path.exists(dest)
        if exists and not force:
            ok, reason = validate_file(dest, t["expected"], t["min_bytes"])
            if ok:
                entry["status"] = "present"
                entry["detail"] = reason
                entry["size_bytes"] = os.path.getsize(dest)
                if not report_only:
                    entry["sha256"] = sha256_of(dest)
                results.append(entry)
                print(f"[{i}/{n}] PRESENT  {t['category']}/{t['id']}")
                continue
            else:
                entry["detail"] = f"presente ma non valido: {reason}"

        if report_only:
            entry["status"] = "missing" if not exists else "invalid"
            results.append(entry)
            print(f"[{i}/{n}] {entry['status'].upper():8s} {t['category']}/{t['id']}")
            continue

        if not t["url"]:
            entry["status"] = "pending_manual_url"
            entry["detail"] = "URL diretto da risolvere dalla source_page"
            results.append(entry)
            print(f"[{i}/{n}] PENDING  {t['category']}/{t['id']} (URL manuale)")
            continue

        if dry_run:
            entry["status"] = "would_download"
            entry["detail"] = f"da {t['url']}"
            results.append(entry)
            print(f"[{i}/{n}] WOULD-DL {t['category']}/{t['id']}")
            continue

        print(f"[{i}/{n}] DOWNLOAD {t['category']}/{t['id']}")
        ok, size, reason = download(t["url"], dest, ctx, t["min_bytes"])
        if ok:
            valid, vreason = validate_file(dest, t["expected"], t["min_bytes"])
            if valid:
                entry["status"] = "downloaded"
                entry["size_bytes"] = size
                entry["sha256"] = sha256_of(dest)
                entry["detail"] = vreason
                print(f"          OK ({size} byte)")
            else:
                # Rimuove file non valido per non "sporcare" il repo
                try:
                    os.remove(dest)
                except OSError:
                    pass
                entry["status"] = "invalid_download"
                entry["detail"] = vreason
                print(f"          SCARTATO: {vreason}")
        else:
            entry["status"] = "failed"
            entry["detail"] = reason
            print(f"          FALLITO: {reason}")

        results.append(entry)
        if i < n:
            time.sleep(delay)
    return results


def write_manifest(results):
    # Categorie elaborate in questa esecuzione (possono essere un sottoinsieme).
    by_cat = {}
    for r in results:
        by_cat.setdefault(r["category"], []).append(r)

    # Merge con il manifest esistente: sostituisce solo le categorie
    # effettivamente elaborate, preservando le altre (es. run --category).
    merged = {}
    if os.path.exists(MANIFEST_PATH):
        try:
            with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
                prev = json.load(f)
            for cat, info in prev.get("categories", {}).items():
                merged[cat] = list(info.get("items", []))
        except (json.JSONDecodeError, OSError):
            merged = {}
    for cat, items in by_cat.items():
        merged[cat] = items

    all_items = [it for items in merged.values() for it in items]
    counts = {}
    for r in all_items:
        counts[r["status"]] = counts.get(r["status"], 0) + 1

    manifest = {
        "description": "Manifest consolidato delle pipeline di enrichment info_MIB",
        "generated": datetime.now(timezone.utc).isoformat(),
        "run_date": TODAY,
        "last_run_categories": sorted(by_cat.keys()),
        "totals": {
            "targets": len(all_items),
            "categories": len(merged),
            "by_status": counts,
        },
        "categories": {
            cat: {
                "count": len(items),
                "items": items,
            }
            for cat, items in sorted(merged.items())
        },
    }
    os.makedirs(os.path.dirname(MANIFEST_PATH), exist_ok=True)
    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    return manifest


def write_report(results):
    os.makedirs(LOGS_DIR, exist_ok=True)
    report = {
        "run_date": TODAY,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "results": results,
    }
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)


def print_summary(manifest):
    t = manifest["totals"]
    print("\n" + "=" * 66)
    print(f"ENRICHMENT - {TODAY}")
    print("=" * 66)
    print(f"  Target totali:  {t['targets']}")
    print(f"  Categorie:      {t['categories']}")
    print("  Stato:")
    for status, count in sorted(t["by_status"].items()):
        print(f"    {status:22s} {count}")
    print(f"\n  Manifest: {os.path.relpath(MANIFEST_PATH, BASE_DIR)}")
    print(f"  Report:   {os.path.relpath(REPORT_PATH, BASE_DIR)}")
    print("=" * 66)


def main():
    p = argparse.ArgumentParser(description="Pipeline di enrichment giornaliere info_MIB")
    p.add_argument("--category", action="append", dest="categories",
                   help="Limita a una o più categorie (ripetibile)")
    p.add_argument("--list", action="store_true", help="Elenca i target ed esci")
    p.add_argument("--dry-run", action="store_true", help="Simula senza scaricare")
    p.add_argument("--force", action="store_true", help="Riscarica anche i file già presenti")
    p.add_argument("--report-only", action="store_true",
                   help="Riporta solo lo stato dei file locali (nessun download)")
    p.add_argument("--delay", type=float, default=DEFAULT_DELAY,
                   help=f"Ritardo tra richieste in secondi (default {DEFAULT_DELAY})")
    args = p.parse_args()

    targets = all_targets()
    if args.categories:
        wanted = set(args.categories)
        targets = [t for t in targets if t["category"] in wanted]

    if args.list:
        s = reg.summary()
        print(json.dumps(s, indent=2, ensure_ascii=False))
        print(f"\nTarget totali (incluso gimbe+pdta): {len(all_targets())}")
        for t in targets:
            flag = "URL" if t["url"] else "---"
            rel = os.path.relpath(t["dest"], BASE_DIR)
            print(f"  [{flag}] {t['category']:16s} {t['id']:32s} {rel}")
        return 0

    results = process(
        targets,
        dry_run=args.dry_run,
        force=args.force,
        report_only=args.report_only,
        delay=args.delay,
    )
    manifest = write_manifest(results)
    write_report(results)
    print_summary(manifest)

    # Exit code: 0 se non ci sono fallimenti "duri" (download falliti/invalidi)
    hard_fail = sum(
        1 for r in results if r["status"] in ("failed", "invalid_download")
    )
    return 1 if hard_fail else 0


if __name__ == "__main__":
    sys.exit(main())
