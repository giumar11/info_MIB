#!/usr/bin/env python3
"""
Download dei report/dataset ORIGINALI (PDF e file diretti) per le categorie
di documenti che nel repository dispongono solo di estratti processati (JSON/CSV)
ma non del documento originale.

A differenza degli script specializzati (download_gimbe_pdfs.py,
download_pdta.py, download_ania_reports.py), questo e' guidato da un registro
esterno: datasets/raw/_catalog/original_reports.json. Per aggiungere un nuovo
originale basta aggiungere una voce a quel file - non serve toccare il codice.

Ogni voce del registro:
  {
    "id": "...",            # identificativo univoco
    "category": "...",       # categoria (aifa, ons, societa_scientifiche, ...)
    "title": "...",
    "url": "...",            # URL diretto al PDF/file
    "dest": "datasets/raw/.../file.pdf"   # percorso relativo alla root repo
  }

Usage:
    python3 scripts/download_original_reports.py                 # tutti
    python3 scripts/download_original_reports.py --category aifa # solo categoria
    python3 scripts/download_original_reports.py --check         # stato
    python3 scripts/download_original_reports.py --force         # ri-scarica
"""

import argparse
import hashlib
import json
import os
import ssl
import sys
import time
import urllib.error
import urllib.request

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REGISTRY_PATH = os.path.join(
    BASE_DIR, "datasets", "raw", "_catalog", "original_reports.json"
)
MANIFEST_PATH = os.path.join(
    BASE_DIR, "datasets", "raw", "_catalog", "original_reports_manifest.json"
)


def load_registry():
    with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("reports", [])


def build_ssl_context():
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx


def format_size(size_bytes):
    if size_bytes >= 1_000_000:
        return f"{size_bytes / 1_000_000:.1f} MB"
    if size_bytes >= 1_000:
        return f"{size_bytes / 1_000:.1f} KB"
    return f"{size_bytes} B"


def download(url, dest_path, ctx, max_retries=3):
    """Scarica un file con retry ed exponential backoff. Ritorna (size, sha256)."""
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/pdf,*/*",
    }
    for attempt in range(max_retries):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, context=ctx, timeout=120) as resp:
                data = resp.read()
            if len(data) < 1000:
                print(f"    WARNING: file troppo piccolo ({len(data)} byte)")
                return None, None
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            with open(dest_path, "wb") as f:
                f.write(data)
            return len(data), hashlib.sha256(data).hexdigest()
        except (urllib.error.URLError, urllib.error.HTTPError, OSError) as e:
            wait = 2 ** (attempt + 1)
            print(f"    Tentativo {attempt + 1}/{max_retries} fallito: {e}")
            if attempt < max_retries - 1:
                print(f"    Nuovo tentativo tra {wait}s...")
                time.sleep(wait)
    return None, None


def check_status(reports):
    print("=" * 70)
    print("STATO DOWNLOAD REPORT ORIGINALI")
    print("=" * 70)
    ok = missing = 0
    for rep in reports:
        dest = os.path.join(BASE_DIR, rep["dest"])
        if os.path.exists(dest) and os.path.getsize(dest) > 1000:
            print(f"  [OK]      [{rep['category']}] {rep['id']} "
                  f"({format_size(os.path.getsize(dest))})")
            ok += 1
        else:
            print(f"  [MISSING] [{rep['category']}] {rep['id']}")
            print(f"            {rep['url']}")
            missing += 1
    print(f"\nScaricati: {ok}/{len(reports)} | Mancanti: {missing}")


def main():
    parser = argparse.ArgumentParser(description="Download report originali (registro)")
    parser.add_argument("--category", help="Filtra per categoria")
    parser.add_argument("--check", action="store_true", help="Mostra solo lo stato")
    parser.add_argument("--force", action="store_true", help="Ri-scarica tutto")
    args = parser.parse_args()

    reports = load_registry()
    if args.category:
        reports = [r for r in reports if r.get("category") == args.category]

    if not reports:
        print("Nessun report nel registro (per la categoria richiesta).")
        return 0

    if args.check:
        check_status(reports)
        return 0

    print("=" * 70)
    print(f"DOWNLOAD REPORT ORIGINALI - {len(reports)} voci dal registro")
    print("=" * 70)

    ctx = build_ssl_context()
    manifest = []
    success = failed = skipped = 0

    for i, rep in enumerate(reports, 1):
        dest = os.path.join(BASE_DIR, rep["dest"])
        print(f"\n[{i}/{len(reports)}] [{rep['category']}] {rep['id']}: {rep['title']}")

        if not args.force and os.path.exists(dest) and os.path.getsize(dest) > 1000:
            size = os.path.getsize(dest)
            print(f"    SKIP (esiste): {format_size(size)}")
            with open(dest, "rb") as fh:
                sha = hashlib.sha256(fh.read()).hexdigest()
            manifest.append({**_meta(rep), "size_bytes": size,
                             "sha256": sha, "status": "ok"})
            success += 1
            skipped += 1
            continue

        print(f"    URL: {rep['url']}")
        size, sha = download(rep["url"], dest, ctx)
        if size:
            print(f"    OK: {format_size(size)}")
            manifest.append({**_meta(rep), "size_bytes": size,
                             "sha256": sha, "status": "ok"})
            success += 1
        else:
            print("    FAILED")
            manifest.append({**_meta(rep), "size_bytes": 0,
                             "sha256": None, "status": "failed"})
            failed += 1

        if i < len(reports):
            time.sleep(1)

    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump({
            "download_date": time.strftime("%Y-%m-%d"),
            "total": len(reports),
            "downloaded": success,
            "failed": failed,
            "files": manifest,
        }, f, indent=2, ensure_ascii=False)

    downloaded = success - skipped
    print(f"\n{'=' * 70}")
    print(f"RISULTATO: {success}/{len(reports)} disponibili "
          f"({downloaded} nuovi, {skipped} gia' presenti)")
    if failed:
        print(f"           {failed} download falliti")
    print(f"Manifest: {MANIFEST_PATH}")
    print(f"{'=' * 70}")
    return 0 if failed == 0 else 1


def _meta(rep):
    return {
        "id": rep["id"],
        "category": rep["category"],
        "title": rep["title"],
        "year": rep.get("year"),
        "url": rep["url"],
        "dest": rep["dest"],
    }


if __name__ == "__main__":
    sys.exit(main())
