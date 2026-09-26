#!/usr/bin/env python3
"""
Download dei report ANIA (Associazione Nazionale fra le Imprese Assicuratrici).

Scarica i documenti ORIGINALI pubblici pubblicati da ANIA sul settore
assicurativo italiano, con particolare rilievo per l'assicurazione salute /
sanità integrativa e il welfare, in coerenza con il focus sociosanitario del
repository.

Salva in: datasets/raw/ania/pdf/

Usage:
    python3 scripts/download_ania_reports.py            # scarica i PDF mancanti
    python3 scripts/download_ania_reports.py --check    # mostra solo lo stato
    python3 scripts/download_ania_reports.py --force     # riscarica tutto

I report annuali "L'assicurazione italiana" contengono un capitolo dedicato
alle assicurazioni malattia/salute e all'analisi della spesa sanitaria privata
e della sanità integrativa, dati utili per l'analisi dell'indirizzamento
sociosanitario (canali di accesso alle cure diversi dal SSN).
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
PDF_DIR = os.path.join(BASE_DIR, "datasets", "raw", "ania", "pdf")
MANIFEST_PATH = os.path.join(PDF_DIR, "manifest.json")

# Report ANIA pubblici con URL verificati (fonte: www.ania.it/pubblicazioni).
# category:
#   rapporto_annuale       -> "L'assicurazione italiana" (rapporto di riferimento)
#   rapporto_annuale_eng   -> versione inglese "Italian Insurance"
ANIA_PDFS = [
    {
        "filename": "LAssicurazione_Italiana_2024-2025.pdf",
        "url": "https://www.ania.it/wp-content/uploads/2026/03/LAssicurazione-Italiana-2024-2025.pdf",
        "category": "rapporto_annuale",
        "edition": "L'assicurazione italiana 2024-2025",
        "year": 2025,
    },
    {
        "filename": "LAssicurazione_Italiana_2023-2024.pdf",
        "url": "https://www.ania.it/wp-content/uploads/2026/03/LAssicurazione-Italiana-2023-2024.pdf",
        "category": "rapporto_annuale",
        "edition": "L'assicurazione italiana 2023-2024",
        "year": 2024,
    },
    {
        "filename": "LAssicurazione_Italiana_2021-2022.pdf",
        "url": "https://www.ania.it/wp-content/uploads/2026/03/LAssicurazione-Italiana-2021-2022.pdf",
        "category": "rapporto_annuale",
        "edition": "L'assicurazione italiana 2021-2022",
        "year": 2022,
    },
    {
        "filename": "LAssicurazione_Italiana_2019-2020.pdf",
        "url": "https://www.ania.it/documents/35135/126701/LAssicurazione-Italiana-2019-2020.pdf",
        "category": "rapporto_annuale",
        "edition": "L'assicurazione italiana 2019-2020",
        "year": 2020,
    },
    {
        "filename": "Italian_Insurance_2024-2025_EN.pdf",
        "url": "https://www.ania.it/wp-content/uploads/2026/03/Italian-Insurance-2025_EN-WEBFULL-4.pdf",
        "category": "rapporto_annuale_eng",
        "edition": "Italian Insurance 2024-2025 (EN)",
        "year": 2025,
    },
    {
        "filename": "Italian_Insurance_2022-2023_EN.pdf",
        "url": "https://ania.it/wp-content/uploads/2026/03/Italian-Insurance-2022-2023-WEB.pdf",
        "category": "rapporto_annuale_eng",
        "edition": "Italian Insurance 2022-2023 (EN)",
        "year": 2023,
    },
]


def download_pdf(url, filepath, max_retries=4):
    """Scarica un PDF con retry ed exponential backoff. Ritorna (size, sha256)."""
    ctx = ssl.create_default_context()
    # Rispetta il CA bundle del proxy se presente (ambienti gestiti)
    ca_bundle = os.environ.get("REQUESTS_CA_BUNDLE") or os.environ.get("SSL_CERT_FILE")
    if ca_bundle and os.path.exists(ca_bundle):
        try:
            ctx.load_verify_locations(ca_bundle)
        except Exception:
            pass
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; InfoMIB-DataBot/1.0; +https://github.com/giumar11/info_MIB)"
    }
    for attempt in range(max_retries):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, context=ctx, timeout=120) as resp:
                data = resp.read()
                if len(data) < 1000:
                    print(f"    WARNING: file troppo piccolo ({len(data)} byte)")
                with open(filepath, "wb") as f:
                    f.write(data)
                return len(data), hashlib.sha256(data).hexdigest()
        except (urllib.error.URLError, urllib.error.HTTPError, OSError) as e:
            wait = 2 ** (attempt + 1)
            print(f"    Tentativo {attempt + 1}/{max_retries} fallito: {e}")
            if attempt < max_retries - 1:
                print(f"    Riprovo tra {wait}s...")
                time.sleep(wait)
    return None, None


def format_size(size_bytes):
    if size_bytes >= 1_000_000:
        return f"{size_bytes / 1_000_000:.1f} MB"
    if size_bytes >= 1_000:
        return f"{size_bytes / 1_000:.1f} KB"
    return f"{size_bytes} B"


def check_status():
    print("=" * 70)
    print("STATO DOWNLOAD PDF ANIA")
    print("=" * 70)
    print(f"\nDirectory: {PDF_DIR}\n")
    ok = missing = total_size = 0
    for pdf in ANIA_PDFS:
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
    print(f"Scaricati: {ok}/{len(ANIA_PDFS)} ({format_size(total_size)})")
    print(f"Mancanti:  {missing}/{len(ANIA_PDFS)}")
    print(f"{'=' * 70}")


def write_manifest(manifest, success, failed):
    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(
            {
                "description": "ANIA report PDF collection manifest",
                "owner": "ANIA - Associazione Nazionale fra le Imprese Assicuratrici",
                "source_url": "https://www.ania.it/pubblicazioni",
                "download_date": time.strftime("%Y-%m-%d"),
                "note": "Esegui 'python3 scripts/download_ania_reports.py' per scaricare i PDF mancanti",
                "total": len(ANIA_PDFS),
                "downloaded": success,
                "failed": failed,
                "files": manifest,
            },
            f,
            indent=2,
            ensure_ascii=False,
        )


def main():
    parser = argparse.ArgumentParser(description="Download report ANIA")
    parser.add_argument("--check", action="store_true", help="Mostra solo lo stato")
    parser.add_argument("--force", action="store_true", help="Riscarica tutto")
    args = parser.parse_args()

    os.makedirs(PDF_DIR, exist_ok=True)

    if args.check:
        check_status()
        return 0

    print("=" * 70)
    print("DOWNLOAD REPORT ANIA - PDF ORIGINALI")
    print("=" * 70)
    print(f"\nTarget: {PDF_DIR}")
    print(f"Report totali: {len(ANIA_PDFS)}\n")

    manifest = []
    success = failed = skipped = 0

    for i, pdf in enumerate(ANIA_PDFS, 1):
        filepath = os.path.join(PDF_DIR, pdf["filename"])
        if not args.force and os.path.exists(filepath) and os.path.getsize(filepath) > 1000:
            size = os.path.getsize(filepath)
            sha = hashlib.sha256(open(filepath, "rb").read()).hexdigest()
            print(f"[{i}/{len(ANIA_PDFS)}] SKIP (esiste): {pdf['filename']} ({format_size(size)})")
            manifest.append({**pdf, "size_bytes": size, "size_human": format_size(size),
                             "sha256": sha, "status": "ok"})
            success += 1
            skipped += 1
            continue

        print(f"[{i}/{len(ANIA_PDFS)}] Download: {pdf['filename']}")
        print(f"    URL: {pdf['url']}")
        size, sha = download_pdf(pdf["url"], filepath)
        if size:
            print(f"    OK: {format_size(size)}")
            manifest.append({**pdf, "size_bytes": size, "size_human": format_size(size),
                             "sha256": sha, "status": "ok"})
            success += 1
        else:
            print("    FALLITO")
            manifest.append({**pdf, "size_bytes": 0, "sha256": None, "status": "failed"})
            failed += 1

        if i < len(ANIA_PDFS):
            time.sleep(1)

    write_manifest(manifest, success, failed)

    print(f"\n{'=' * 70}")
    downloaded = success - skipped
    print(f"RISULTATO: {success}/{len(ANIA_PDFS)} disponibili ({downloaded} nuovi, {skipped} già presenti)")
    if failed:
        print(f"           {failed} download falliti")
    print(f"Manifest: {MANIFEST_PATH}")
    print(f"{'=' * 70}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
