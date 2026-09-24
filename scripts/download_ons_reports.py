#!/usr/bin/env python3
"""
Download dei Rapporti ORIGINALI dell'Osservatorio Nazionale Screening (ONS).

Finora il repository conteneva solo l'estratto elaborato
`datasets/raw/ons/ons_screening_completo.json`. Questo script scarica i PDF
originali dei Rapporti annuali ONS sugli screening oncologici organizzati
(mammografico, cervicale, colorettale) in datasets/raw/ons/pdf/.

NOTA SULLE URL
--------------
Gli URL sono stati raccolti dall'indice pubblico ONS (host
osservatorionazionalescreening.it, path /sites/default/files/allegati/...).
La verifica effettiva avviene in esecuzione (runner con rete completa). I
download falliti sono registrati nel manifest senza bloccare gli altri.
L'edizione 2024 è pubblicata come flipbook web senza PDF singolo: si usa la
landing page di riferimento.

Uso:
    python3 scripts/download_ons_reports.py           # scarica i mancanti
    python3 scripts/download_ons_reports.py --check     # solo stato
    python3 scripts/download_ons_reports.py --force      # riscarica tutto
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
ONS_PDF_DIR = os.path.join(BASE_DIR, "datasets", "raw", "ons", "pdf")
MANIFEST_PATH = os.path.join(ONS_PDF_DIR, "manifest.json")

ONS_REPORTS = [
    {
        "filename": "Rapporto_ONS_2023.pdf",
        "url": "https://www.osservatorionazionalescreening.it/sites/default/files/allegati/Rapporto%20Ons%202023_0.pdf",
        "title": "Rapporto ONS 2023 - Screening oncologici organizzati",
        "year": 2023,
    },
    {
        "filename": "Rapporto_ONS_2016.pdf",
        "url": "https://www.osservatorionazionalescreening.it/sites/default/files/allegati/ons%20rapporto%202016%20VI.pdf",
        "title": "Rapporto ONS 2016 (VI edizione)",
        "year": 2016,
    },
    {
        "filename": "Rapporto_ONS_2009.pdf",
        "url": "https://www.osservatorionazionalescreening.it/sites/default/files/allegati/8_Rapporto_ONS.pdf",
        "title": "Ottavo Rapporto ONS 2009",
        "year": 2009,
    },
    {
        "filename": "Screening_Regione_Toscana_25_Rapporto.pdf",
        "url": "https://www.osservatorionazionalescreening.it/sites/default/files/allegati/Volume%20intero_compressed.pdf",
        "title": "I programmi di screening della Regione Toscana - 25° Rapporto Annuale",
        "year": None,
    },
]

ONS_LANDING_PAGES = {
    "rapporti_annuali_index": "https://www.osservatorionazionalescreening.it/content/i-rapporti-annuali-dellons",
    "rapporto_2024_flipbook": "https://www.osservatorionazionalescreening.it/content/rapporto",
}


def download_pdf(url, filepath, max_retries=3):
    ctx = ssl.create_default_context()
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
                ctype = resp.headers.get("Content-Type", "")
                if len(data) < 1000:
                    print(f"    WARNING: file troppo piccolo ({len(data)} byte)")
                    return None, None
                if "html" in ctype.lower() and b"%PDF" not in data[:1024]:
                    print(f"    WARNING: risposta non-PDF (Content-Type: {ctype})")
                    return None, None
                with open(filepath, "wb") as f:
                    f.write(data)
                return len(data), hashlib.sha256(data).hexdigest()
        except (urllib.error.URLError, urllib.error.HTTPError, OSError) as e:
            print(f"    Tentativo {attempt + 1}/{max_retries} fallito: {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** (attempt + 1))
    return None, None


def format_size(n):
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f} MB"
    if n >= 1_000:
        return f"{n / 1_000:.1f} KB"
    return f"{n} B"


def check_status():
    print("=" * 70)
    print("STATO DOWNLOAD RAPPORTI ONS")
    print("=" * 70)
    print(f"\nDirectory: {ONS_PDF_DIR}\n")
    ok = missing = total_size = 0
    for r in ONS_REPORTS:
        fp = os.path.join(ONS_PDF_DIR, r["filename"])
        if os.path.exists(fp) and os.path.getsize(fp) > 1000:
            size = os.path.getsize(fp)
            total_size += size
            ok += 1
            print(f"  [OK]      {r['filename']} ({format_size(size)})")
        else:
            missing += 1
            print(f"  [MISSING] {r['filename']}")
            print(f"            URL: {r['url']}")
    print(f"\n{'=' * 70}")
    print(f"Scaricati: {ok}/{len(ONS_REPORTS)} ({format_size(total_size)}) | Mancanti: {missing}")
    print("=" * 70)


def main():
    parser = argparse.ArgumentParser(description="Download Rapporti ONS (screening oncologici)")
    parser.add_argument("--check", action="store_true", help="Mostra solo lo stato")
    parser.add_argument("--force", action="store_true", help="Riscarica tutto")
    args = parser.parse_args()

    os.makedirs(ONS_PDF_DIR, exist_ok=True)
    if args.check:
        check_status()
        return 0

    print("=" * 70)
    print("DOWNLOAD RAPPORTI ONS - OSSERVATORIO NAZIONALE SCREENING")
    print("=" * 70)
    print(f"\nTarget: {ONS_PDF_DIR}\nReport totali: {len(ONS_REPORTS)}\n")

    manifest = []
    success = failed = skipped = 0

    for i, r in enumerate(ONS_REPORTS, 1):
        filepath = os.path.join(ONS_PDF_DIR, r["filename"])
        if not args.force and os.path.exists(filepath) and os.path.getsize(filepath) > 1000:
            size = os.path.getsize(filepath)
            sha = hashlib.sha256(open(filepath, "rb").read()).hexdigest()
            print(f"[{i}/{len(ONS_REPORTS)}] SKIP (esiste): {r['filename']} ({format_size(size)})")
            manifest.append({**r, "size_bytes": size, "sha256": sha, "status": "ok"})
            success += 1
            skipped += 1
            continue

        print(f"[{i}/{len(ONS_REPORTS)}] Download: {r['filename']}")
        print(f"    URL: {r['url']}")
        size, sha = download_pdf(r["url"], filepath)
        if size:
            print(f"    OK: {format_size(size)}")
            manifest.append({**r, "size_bytes": size, "sha256": sha, "status": "ok"})
            success += 1
        else:
            print("    FALLITO")
            manifest.append({**r, "size_bytes": 0, "sha256": None, "status": "failed"})
            failed += 1
        if i < len(ONS_REPORTS):
            time.sleep(1)

    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump({
            "description": "Manifest Rapporti ONS (Osservatorio Nazionale Screening)",
            "download_date": time.strftime("%Y-%m-%d"),
            "note": "URL raccolti dall'indice pubblico ONS; verificare in esecuzione.",
            "landing_pages": ONS_LANDING_PAGES,
            "total": len(ONS_REPORTS),
            "downloaded": success,
            "failed": failed,
            "files": manifest,
        }, f, indent=2, ensure_ascii=False)

    print(f"\n{'=' * 70}")
    print(f"RISULTATO: {success}/{len(ONS_REPORTS)} disponibili ({success - skipped} nuovi, {skipped} già presenti)")
    if failed:
        print(f"           {failed} download falliti (vedi manifest)")
    print(f"Manifest: {MANIFEST_PATH}")
    print("=" * 70)
    return 0


if __name__ == "__main__":
    sys.exit(main())
