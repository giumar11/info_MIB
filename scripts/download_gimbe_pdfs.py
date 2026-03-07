#!/usr/bin/env python3
"""
Download all available GIMBE report PDFs.
Saves to datasets/raw/gimbe/pdf/

Usage:
    python3 scripts/download_gimbe_pdfs.py           # Download missing PDFs
    python3 scripts/download_gimbe_pdfs.py --check   # Show status only
    python3 scripts/download_gimbe_pdfs.py --force   # Re-download all
"""

import argparse
import os
import sys
import time
import hashlib
import json
import urllib.request
import urllib.error
import ssl

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PDF_DIR = os.path.join(BASE_DIR, "datasets", "raw", "gimbe", "pdf")
MANIFEST_PATH = os.path.join(PDF_DIR, "manifest.json")

# All known GIMBE PDF URLs with descriptive filenames
GIMBE_PDFS = [
    # --- Rapporti annuali sul SSN ---
    {
        "filename": "1_Rapporto_GIMBE_SSN_2016.pdf",
        "url": "https://salviamo-ssn.it/var/contenuti/1_Rapporto_GIMBE.pdf",
        "category": "rapporto_annuale",
        "edition": "1° Rapporto",
        "year": 2016,
    },
    {
        "filename": "2_Rapporto_GIMBE_SSN_2017.pdf",
        "url": "https://salviamo-ssn.it/var/contenuti/2_Rapporto_GIMBE.pdf",
        "category": "rapporto_annuale",
        "edition": "2° Rapporto",
        "year": 2017,
    },
    {
        "filename": "3_Rapporto_GIMBE_SSN_2018.pdf",
        "url": "https://salviamo-ssn.it/var/contenuti/3_Rapporto_GIMBE.pdf",
        "category": "rapporto_annuale",
        "edition": "3° Rapporto",
        "year": 2018,
    },
    {
        "filename": "4_Rapporto_GIMBE_SSN_2019.pdf",
        "url": "https://www.salviamo-ssn.it/var/contenuti/4_Rapporto_GIMBE_Sostenibilita_SSN.pdf",
        "category": "rapporto_annuale",
        "edition": "4° Rapporto",
        "year": 2019,
    },
    {
        "filename": "5_Rapporto_GIMBE_SSN_2022.pdf",
        "url": "https://www.quotidianosanita.it/allegati/allegato1665475004.pdf",
        "category": "rapporto_annuale",
        "edition": "5° Rapporto",
        "year": 2022,
    },
    {
        "filename": "6_Rapporto_GIMBE_SSN_2023.pdf",
        "url": "https://www.quotidianosanita.it/allegati/allegato1696924905.pdf",
        "category": "rapporto_annuale",
        "edition": "6° Rapporto",
        "year": 2023,
    },
    {
        "filename": "7_Rapporto_GIMBE_SSN_2024.pdf",
        "url": "https://www.camera.it/temiap/2024/10/09/OCD177-7603.pdf",
        "category": "rapporto_annuale",
        "edition": "7° Rapporto",
        "year": 2024,
    },
    {
        "filename": "8_Rapporto_GIMBE_SSN_2025.pdf",
        "url": "https://www.salviamo-ssn.it/var/contenuti/8_Rapporto_GIMBE_SSN.pdf",
        "category": "rapporto_annuale",
        "edition": "8° Rapporto",
        "year": 2025,
    },
    # --- Report Osservatorio GIMBE ---
    {
        "filename": "Report_Osservatorio_GIMBE_2023.01_Regionalismo_differenziato.pdf",
        "url": "https://www.gimbe.org/osservatorio/Report_Osservatorio_GIMBE_2023.01_Regionalismo_differenziato_in_sanita.pdf",
        "category": "osservatorio",
        "edition": "1/2023",
        "year": 2023,
    },
    {
        "filename": "Report_Osservatorio_GIMBE_2023.04_Filiera_healthcare.pdf",
        "url": "https://www.gimbe.org/osservatorio/Report_Osservatorio_GIMBE_2023.04_Ruolo_filiera_healthcare_nel_SSN.pdf",
        "category": "osservatorio",
        "edition": "4/2023",
        "year": 2023,
    },
    {
        "filename": "Report_Osservatorio_GIMBE_2024.01_Mobilita_sanitaria_2021.pdf",
        "url": "https://www.gimbe.org/osservatorio/Report_Osservatorio_GIMBE_2024.01_Mobilita_sanitaria_2021.pdf",
        "category": "osservatorio",
        "edition": "1/2024",
        "year": 2024,
    },
    {
        "filename": "Report_Osservatorio_GIMBE_2024.02_Autonomia_differenziata.pdf",
        "url": "https://documenti.camera.it/leg19/documentiAcquisiti/COM01/Audizioni/leg19.com01.Audizioni.Memoria.PUBBLICO.ideGes.34026.26-03-2024-11-34-12.951.pdf",
        "category": "osservatorio",
        "edition": "2/2024",
        "year": 2024,
    },
    {
        "filename": "Report_Osservatorio_GIMBE_2024.03_Scuole_promuovono_salute.pdf",
        "url": "https://www.gimbe.org/osservatorio/Report_Osservatorio_GIMBE_2024.03_Scuole_che_promuovono_salute.pdf",
        "category": "osservatorio",
        "edition": "3/2024",
        "year": 2024,
    },
    {
        "filename": "Report_Osservatorio_GIMBE_2025.01_Mobilita_sanitaria_2022.pdf",
        "url": "https://www.avis.it/wp-content/uploads/2025/03/Report_Osservatorio_GIMBE_2025.01_Mobilita_sanitaria_2022.pdf",
        "category": "osservatorio",
        "edition": "1/2025",
        "year": 2025,
    },
    {
        "filename": "Report_Osservatorio_GIMBE_2025.02_Spesa_sanitaria_privata_2023.pdf",
        "url": "https://salviamo-ssn.it/var/contenuti/Report_Osservatorio_GIMBE_2025.02_Spesa_sanitaria_privata_2023.pdf",
        "category": "osservatorio",
        "edition": "2/2025",
        "year": 2025,
    },
]


def download_pdf(url, filepath, max_retries=3):
    """Download a PDF with retries and exponential backoff."""
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_peer = False

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
                    print(f"    WARNING: File too small ({len(data)} bytes), may not be valid")

                with open(filepath, "wb") as f:
                    f.write(data)

                return len(data), hashlib.sha256(data).hexdigest()

        except (urllib.error.URLError, urllib.error.HTTPError, OSError) as e:
            wait = 2 ** (attempt + 1)
            print(f"    Attempt {attempt + 1}/{max_retries} failed: {e}")
            if attempt < max_retries - 1:
                print(f"    Retrying in {wait}s...")
                time.sleep(wait)

    return None, None


def format_size(size_bytes):
    if size_bytes >= 1_000_000:
        return f"{size_bytes / 1_000_000:.1f} MB"
    elif size_bytes >= 1_000:
        return f"{size_bytes / 1_000:.1f} KB"
    return f"{size_bytes} B"


def check_status():
    """Show download status without downloading anything."""
    print("=" * 70)
    print("STATO DOWNLOAD PDF GIMBE")
    print("=" * 70)
    print(f"\nDirectory: {PDF_DIR}\n")

    ok = 0
    missing = 0
    total_size = 0

    for pdf in GIMBE_PDFS:
        filepath = os.path.join(PDF_DIR, pdf["filename"])
        if os.path.exists(filepath) and os.path.getsize(filepath) > 1000:
            size = os.path.getsize(filepath)
            total_size += size
            print(f"  [OK]      {pdf['filename']} ({format_size(size)})")
            ok += 1
        else:
            print(f"  [MISSING] {pdf['filename']}")
            print(f"            URL: {pdf['url']}")
            missing += 1

    print(f"\n{'=' * 70}")
    print(f"Scaricati: {ok}/{len(GIMBE_PDFS)} ({format_size(total_size)})")
    print(f"Mancanti:  {missing}/{len(GIMBE_PDFS)}")
    if missing > 0:
        print(f"\nEsegui senza --check per scaricare i PDF mancanti")
    print(f"{'=' * 70}")


def main():
    parser = argparse.ArgumentParser(description="Download GIMBE report PDFs")
    parser.add_argument("--check", action="store_true", help="Show status only")
    parser.add_argument("--force", action="store_true", help="Re-download all")
    args = parser.parse_args()

    os.makedirs(PDF_DIR, exist_ok=True)

    if args.check:
        check_status()
        return 0

    print("=" * 70)
    print("DOWNLOAD REPORT GIMBE - PDF COMPLETI")
    print("=" * 70)
    print(f"\nTarget: {PDF_DIR}")
    print(f"Report totali: {len(GIMBE_PDFS)}\n")

    manifest = []
    success = 0
    failed = 0
    skipped = 0

    for i, pdf in enumerate(GIMBE_PDFS, 1):
        filepath = os.path.join(PDF_DIR, pdf["filename"])

        # Skip if already downloaded (unless --force)
        if not args.force and os.path.exists(filepath) and os.path.getsize(filepath) > 1000:
            size = os.path.getsize(filepath)
            sha = hashlib.sha256(open(filepath, "rb").read()).hexdigest()
            print(f"[{i}/{len(GIMBE_PDFS)}] SKIP (exists): {pdf['filename']} ({format_size(size)})")
            manifest.append({
                "filename": pdf["filename"],
                "category": pdf["category"],
                "edition": pdf["edition"],
                "year": pdf["year"],
                "url": pdf["url"],
                "size_bytes": size,
                "size_human": format_size(size),
                "sha256": sha,
                "status": "ok",
            })
            success += 1
            skipped += 1
            continue

        print(f"[{i}/{len(GIMBE_PDFS)}] Downloading: {pdf['filename']}")
        print(f"    URL: {pdf['url']}")

        size, sha = download_pdf(pdf["url"], filepath)

        if size:
            print(f"    OK: {format_size(size)}")
            manifest.append({
                "filename": pdf["filename"],
                "category": pdf["category"],
                "edition": pdf["edition"],
                "year": pdf["year"],
                "url": pdf["url"],
                "size_bytes": size,
                "size_human": format_size(size),
                "sha256": sha,
                "status": "ok",
            })
            success += 1
        else:
            print(f"    FAILED")
            manifest.append({
                "filename": pdf["filename"],
                "category": pdf["category"],
                "edition": pdf["edition"],
                "year": pdf["year"],
                "url": pdf["url"],
                "size_bytes": 0,
                "sha256": None,
                "status": "failed",
            })
            failed += 1

        # Rate limit between requests
        if i < len(GIMBE_PDFS):
            time.sleep(1)

    # Save manifest
    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump({
            "description": "GIMBE Report PDF collection manifest",
            "download_date": time.strftime("%Y-%m-%d"),
            "note": "Run 'python3 scripts/download_gimbe_pdfs.py' to download missing PDFs",
            "total": len(GIMBE_PDFS),
            "downloaded": success,
            "failed": failed,
            "files": manifest,
        }, f, indent=2, ensure_ascii=False)

    print(f"\n{'=' * 70}")
    downloaded = success - skipped
    print(f"RISULTATO: {success}/{len(GIMBE_PDFS)} disponibili ({downloaded} nuovi, {skipped} già presenti)")
    if failed > 0:
        print(f"           {failed} download falliti")
    total_size = sum(f["size_bytes"] for f in manifest)
    print(f"Dimensione totale: {format_size(total_size)}")
    print(f"Manifest: {MANIFEST_PATH}")
    print(f"{'=' * 70}")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
