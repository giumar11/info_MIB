#!/usr/bin/env python3
"""
Pipeline di enrichment giornaliera per tutte le categorie di documenti.

Scarica i DATASET e i REPORT ORIGINALI (PDF, CSV, XML, ZIP) dai siti degli enti
proprietari e li salva sotto datasets/raw/<categoria>/. A differenza degli script
di sola elaborazione, questa pipeline conserva i file originali e non solo gli
estratti processati internamente.

Le fonti sono descritte in scripts/enrichment_sources.json:
  - categorie con chiave "script"  -> delega allo script dedicato (es. GIMBE, PDTA)
  - categorie con chiave "sources" -> scarica direttamente i file elencati

Per ogni categoria viene aggiornato un manifest (enrichment_manifest.json nella
cartella di destinazione) con dimensione, checksum SHA-256, URL e stato.
Un report globale viene salvato in logs/enrichment_report_YYYY-MM-DD.json.

Uso:
    python3 scripts/enrich_datasets.py                       # tutte le categorie
    python3 scripts/enrich_datasets.py --category ania       # solo una categoria
    python3 scripts/enrich_datasets.py --category ania --category aifa
    python3 scripts/enrich_datasets.py --list                # elenca le categorie
    python3 scripts/enrich_datasets.py --dry-run             # mostra cosa farebbe
    python3 scripts/enrich_datasets.py --check               # solo stato (no download)
    python3 scripts/enrich_datasets.py --force               # riscarica anche gli esistenti

Schedulazione giornaliera:
    - GitHub Actions:  .github/workflows/daily-enrichment.yml
    - cron:            python3 scripts/enrich_datasets.py --install-cron
"""

import argparse
import hashlib
import json
import os
import ssl
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS_DIR = os.path.join(BASE_DIR, "scripts")
CONFIG_PATH = os.path.join(SCRIPTS_DIR, "enrichment_sources.json")
LOGS_DIR = os.path.join(BASE_DIR, "logs")

TODAY = datetime.now().strftime("%Y-%m-%d")
REPORT_FILE = os.path.join(LOGS_DIR, f"enrichment_report_{TODAY}.json")

REQUEST_TIMEOUT = 120        # secondi
REQUEST_DELAY = 1            # secondi tra i download (rate limiting)
MAX_RETRIES = 3
MIN_VALID_BYTES = 1000       # sotto questa soglia il file è considerato non valido
USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)


# --- utilità ---------------------------------------------------------------

def format_size(size_bytes):
    if size_bytes >= 1_000_000:
        return f"{size_bytes / 1_000_000:.1f} MB"
    if size_bytes >= 1_000:
        return f"{size_bytes / 1_000:.1f} KB"
    return f"{size_bytes} B"


def sha256_of(filepath):
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _ssl_context():
    """Contesto SSL con verifica dei certificati abilitata.

    Rispetta un eventuale CA bundle personalizzato indicato dall'ambiente
    (REQUESTS_CA_BUNDLE / SSL_CERT_FILE), utile dietro proxy aziendali.
    """
    ca_bundle = os.environ.get("REQUESTS_CA_BUNDLE") or os.environ.get("SSL_CERT_FILE")
    if ca_bundle and os.path.exists(ca_bundle):
        return ssl.create_default_context(cafile=ca_bundle)
    return ssl.create_default_context()


# --- download di un singolo file ------------------------------------------

def download_file(url, filepath, max_retries=MAX_RETRIES):
    """Scarica un file con retry ed exponential backoff.

    Ritorna (size_bytes, sha256) in caso di successo, altrimenti (None, errore).
    """
    ctx = _ssl_context()
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/pdf,application/octet-stream,text/csv,*/*",
    }

    last_error = None
    for attempt in range(max_retries):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, context=ctx, timeout=REQUEST_TIMEOUT) as resp:
                data = resp.read()

            if len(data) < MIN_VALID_BYTES:
                last_error = f"file troppo piccolo ({len(data)} byte)"
                raise ValueError(last_error)

            tmp_path = filepath + ".part"
            with open(tmp_path, "wb") as f:
                f.write(data)
            os.replace(tmp_path, filepath)

            return len(data), hashlib.sha256(data).hexdigest()

        except (urllib.error.URLError, urllib.error.HTTPError, OSError, ValueError) as e:
            last_error = str(e)
            wait = 2 ** (attempt + 1)
            print(f"      tentativo {attempt + 1}/{max_retries} fallito: {e}")
            if attempt < max_retries - 1:
                print(f"      nuovo tentativo tra {wait}s...")
                time.sleep(wait)

    return None, last_error


# --- gestione di una categoria "diretta" ----------------------------------

def process_direct_category(name, cfg, args):
    """Scarica i file diretti di una categoria e aggiorna il manifest."""
    dest_dir = os.path.join(BASE_DIR, cfg["dest_dir"])
    os.makedirs(dest_dir, exist_ok=True)
    sources = cfg.get("sources", [])

    print(f"\n[{name}] {cfg.get('description', '')}")
    print(f"  destinazione: {cfg['dest_dir']}  ({len(sources)} file originali)")

    manifest_entries = []
    counters = {"ok": 0, "new": 0, "skipped": 0, "failed": 0}

    for i, src in enumerate(sources, 1):
        filepath = os.path.join(dest_dir, src["filename"])
        exists = os.path.exists(filepath) and os.path.getsize(filepath) > MIN_VALID_BYTES

        if args.check or args.dry_run:
            state = "presente" if exists else "MANCANTE"
            print(f"  [{i}/{len(sources)}] {state}: {src['filename']}")
            if not exists:
                print(f"            URL: {src['url']}")
            continue

        if exists and not args.force:
            size = os.path.getsize(filepath)
            print(f"  [{i}/{len(sources)}] SKIP (già presente): {src['filename']} ({format_size(size)})")
            manifest_entries.append({
                **{k: src[k] for k in ("id", "filename", "title", "year", "url") if k in src},
                "size_bytes": size,
                "size_human": format_size(size),
                "sha256": sha256_of(filepath),
                "status": "ok",
            })
            counters["ok"] += 1
            counters["skipped"] += 1
            continue

        print(f"  [{i}/{len(sources)}] Download: {src['filename']}")
        print(f"            URL: {src['url']}")
        size, sha_or_err = download_file(src["url"], filepath)

        if size:
            print(f"            OK: {format_size(size)}")
            manifest_entries.append({
                **{k: src[k] for k in ("id", "filename", "title", "year", "url") if k in src},
                "size_bytes": size,
                "size_human": format_size(size),
                "sha256": sha_or_err,
                "status": "ok",
            })
            counters["ok"] += 1
            counters["new"] += 1
        else:
            print(f"            FALLITO: {sha_or_err}")
            manifest_entries.append({
                **{k: src[k] for k in ("id", "filename", "title", "year", "url") if k in src},
                "size_bytes": 0,
                "sha256": None,
                "status": "failed",
                "error": sha_or_err,
            })
            counters["failed"] += 1

        if i < len(sources):
            time.sleep(args.delay)

    # Scrive il manifest della categoria (non in dry-run/check)
    if not args.check and not args.dry_run:
        manifest_path = os.path.join(dest_dir, "enrichment_manifest.json")
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump({
                "category": name,
                "description": cfg.get("description", ""),
                "updated": TODAY,
                "total": len(sources),
                "downloaded_ok": counters["ok"],
                "failed": counters["failed"],
                "portal_references": cfg.get("portal_references", []),
                "files": manifest_entries,
            }, f, indent=2, ensure_ascii=False)
        print(f"  manifest: {os.path.relpath(manifest_path, BASE_DIR)}")

    return {
        "category": name,
        "type": "direct",
        "total": len(sources),
        **counters,
    }


# --- gestione di una categoria "delegata a script" ------------------------

def process_script_category(name, cfg, args):
    """Delega il download a uno script dedicato (es. GIMBE, PDTA)."""
    script = cfg["script"]
    script_path = os.path.join(SCRIPTS_DIR, script)

    # Ogni script usa flag diverse per la modalità di sola verifica
    # (GIMBE: --check, PDTA: --dry-run): sono configurabili in "check_args".
    if args.check or args.dry_run:
        cmd = [sys.executable, script_path] + list(cfg.get("check_args", ["--check"]))
    else:
        cmd = [sys.executable, script_path] + list(cfg.get("script_args", []))
        force_arg = cfg.get("force_arg", "--force")
        if args.force and force_arg:
            cmd.append(force_arg)

    print(f"\n[{name}] {cfg.get('description', '')}")
    print(f"  delega a: {script}")
    print(f"  comando:  {' '.join(cmd[1:])}")

    if not os.path.exists(script_path):
        print(f"  ERRORE: script non trovato: {script_path}")
        return {"category": name, "type": "script", "status": "script_not_found", "failed": 1}

    try:
        result = subprocess.run(cmd, cwd=BASE_DIR, timeout=3600)
        status = "ok" if result.returncode == 0 else "errori"
        return {
            "category": name,
            "type": "script",
            "script": script,
            "returncode": result.returncode,
            "status": status,
        }
    except subprocess.TimeoutExpired:
        print(f"  ERRORE: timeout esecuzione script {script}")
        return {"category": name, "type": "script", "script": script, "status": "timeout"}


# --- cron ------------------------------------------------------------------

def install_cron():
    script_path = os.path.abspath(__file__)
    log_path = os.path.join(LOGS_DIR, "enrichment_cron.log")
    cron_line = f"30 6 * * * {sys.executable} {script_path} >> {log_path} 2>&1"
    comment = "# InfoMIB - Enrichment giornaliero dataset e report originali"
    try:
        current = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
        crontab = current.stdout if current.returncode == 0 else ""
        if "enrich_datasets.py" in crontab:
            print("Job cron già installato:")
            print(crontab)
            return
        new = crontab.rstrip("\n")
        new += ("\n" if new else "") + f"\n{comment}\n{cron_line}\n"
        proc = subprocess.Popen(["crontab", "-"], stdin=subprocess.PIPE, text=True)
        proc.communicate(input=new)
        if proc.returncode == 0:
            print("Job cron installato: ogni giorno alle 06:30")
            print(f"  {cron_line}")
        else:
            print("Installazione fallita. Aggiungi manualmente con 'crontab -e':")
            print(f"  {cron_line}")
    except FileNotFoundError:
        print("'crontab' non disponibile. Riga cron suggerita:")
        print(f"  {cron_line}")


# --- main ------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Pipeline di enrichment: scarica dataset e report ORIGINALI per categoria",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--category", action="append", dest="categories",
                        help="Elabora solo la/e categoria/e indicata/e (ripetibile)")
    parser.add_argument("--list", action="store_true", help="Elenca le categorie disponibili")
    parser.add_argument("--dry-run", action="store_true", help="Mostra le azioni senza scaricare")
    parser.add_argument("--check", action="store_true", help="Mostra solo lo stato dei file")
    parser.add_argument("--force", action="store_true", help="Riscarica anche i file già presenti")
    parser.add_argument("--delay", type=float, default=REQUEST_DELAY,
                        help=f"Ritardo tra i download in secondi (default {REQUEST_DELAY})")
    parser.add_argument("--install-cron", action="store_true",
                        help="Installa il job cron giornaliero (06:30)")
    args = parser.parse_args()

    if args.install_cron:
        install_cron()
        return 0

    config = load_config()
    categories = config["categories"]

    if args.list:
        print("Categorie di enrichment disponibili:\n")
        for name, cfg in categories.items():
            kind = "script" if "script" in cfg else "diretta"
            n = len(cfg.get("sources", [])) if "sources" in cfg else "-"
            print(f"  {name:22} [{kind:8}] file: {n:>3}  | {cfg.get('description', '')}")
        return 0

    selected = args.categories or list(categories.keys())
    unknown = [c for c in selected if c not in categories]
    if unknown:
        print(f"ERRORE: categorie sconosciute: {unknown}")
        print(f"Disponibili: {list(categories.keys())}")
        return 1

    os.makedirs(LOGS_DIR, exist_ok=True)

    print("=" * 70)
    print(f"ENRICHMENT DATASET/REPORT ORIGINALI - {TODAY}")
    print("=" * 70)
    print(f"Categorie selezionate: {', '.join(selected)}")
    if args.dry_run:
        print("Modalità: DRY-RUN (nessun download)")
    elif args.check:
        print("Modalità: CHECK (solo stato)")

    results = []
    for name in selected:
        cfg = categories[name]
        if "script" in cfg:
            results.append(process_script_category(name, cfg, args))
        else:
            results.append(process_direct_category(name, cfg, args))

    # Report globale (solo su esecuzione reale)
    if not args.dry_run and not args.check:
        report = {
            "report_date": TODAY,
            "report_timestamp": datetime.now().isoformat(),
            "categories_processed": selected,
            "results": results,
        }
        with open(REPORT_FILE, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 70)
    print("RIEPILOGO")
    print("=" * 70)
    total_failed = 0
    for r in results:
        if r.get("type") == "direct":
            print(f"  {r['category']:22} ok={r.get('ok', 0):>3} nuovi={r.get('new', 0):>3} "
                  f"skip={r.get('skipped', 0):>3} falliti={r.get('failed', 0):>3}")
            total_failed += r.get("failed", 0)
        else:
            print(f"  {r['category']:22} [script] stato={r.get('status', '?')}")
            if r.get("status") not in ("ok", None):
                total_failed += 1
    if not args.dry_run and not args.check:
        print(f"\nReport: {os.path.relpath(REPORT_FILE, BASE_DIR)}")
    print("=" * 70)

    return 0 if total_failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
