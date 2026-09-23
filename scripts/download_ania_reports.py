#!/usr/bin/env python3
"""
Download dei report ANIA (Associazione Nazionale fra le Imprese Assicuratrici).

Scarica i PDF originali dei rapporti ANIA sul mercato assicurativo italiano,
con particolare attenzione alle componenti rilevanti per la spesa sanitaria
privata "intermediata" (assicurazione malattia/salute, fondi sanitari
integrativi, previdenza).

Salva in: datasets/raw/ania/pdf/

Utilizzo:
    python3 scripts/download_ania_reports.py           # Scarica i PDF mancanti
    python3 scripts/download_ania_reports.py --check    # Mostra solo lo stato
    python3 scripts/download_ania_reports.py --force     # Riscarica tutto
    python3 scripts/download_ania_reports.py --dry-run   # Mostra cosa scaricherebbe
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
ANIA_DIR = os.path.join(BASE_DIR, "datasets", "raw", "ania")
PDF_DIR = os.path.join(ANIA_DIR, "pdf")
MANIFEST_PATH = os.path.join(PDF_DIR, "manifest.json")

# Report ANIA con URL PDF diretto verificato.
# Le edizioni piu recenti sono pubblicate su pagine Liferay con token di
# versione instabili: aggiungere qui l'URL diretto quando disponibile.
ANIA_PDFS = [
    {
        "filename": "ANIA_Assicurazione_Italiana_2020-2021.pdf",
        "url": "https://www.ania.it/documents/35135/126701/L'Assicurazione+Italiana+2020-2021.pdf/e4fa652e-dda7-8c9c-96ef-1e4468d4f903?version=1.0&t=1626333153413",
        "category": "rapporto_annuale",
        "edition": "2020-2021",
        "year": 2021,
    },
    {
        "filename": "ANIA_Assicurazione_Italiana_2016-2017.pdf",
        "url": "https://www.ania.it/export/sites/default/it/pubblicazioni/rapporti-annuali/Assicurazione-Italiana/2016-2017/assicurazione_italiana_2016_2017.pdf",
        "category": "rapporto_annuale",
        "edition": "2016-2017",
        "year": 2017,
    },
    {
        "filename": "ANIA_Assicurazione_Italiana_2013-2014.pdf",
        "url": "https://www.ania.it/documents/35135/126701/LAssicurazione-italiana-2013-2014.pdf/ef32cf39-58cb-6ea0-8bcd-76cc80ae69cd?t=1575543843311",
        "category": "rapporto_annuale",
        "edition": "2013-2014",
        "year": 2014,
    },
    {
        "filename": "ANIA_Assicurazione_Italiana_2012-2013.pdf",
        "url": "https://www.ania.it/documents/35135/0/Assicurazione-Italiana-2012-2013.pdf/1a921ad3-efd4-6073-50f3-7c05a5770b0b?t=1576519512151",
        "category": "rapporto_annuale",
        "edition": "2012-2013",
        "year": 2013,
    },
    {
        "filename": "ANIA_Assicurazione_Italiana_2004-2005.pdf",
        "url": "https://www.ania.it/documents/35135/439653/Assicurazione-Italiana+2004-2005.pdf/8f77f164-e796-e7d4-8be3-6d10ed158151?version=1.1&t=1751436630852",
        "category": "rapporto_annuale",
        "edition": "2004-2005",
        "year": 2005,
    },
]


def download_pdf(url, filepath, max_retries=4):
    """Scarica un PDF con retry ed exponential backoff."""
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

            # Verifica che sia un PDF valido (magic number) e non una pagina HTML
            if not data.startswith(b"%PDF"):
                print(f"    ATTENZIONE: la risposta non e un PDF "
                      f"(primi byte: {data[:16]!r}) - salto")
                return None, None

            if len(data) < 1000:
                print(f"    ATTENZIONE: file troppo piccolo ({len(data)} byte)")

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
    """Mostra lo stato dei download senza scaricare nulla."""
    print("=" * 70)
    print("STATO DOWNLOAD PDF ANIA")
    print("=" * 70)
    print(f"\nDirectory: {PDF_DIR}\n")

    ok = 0
    missing = 0
    total_size = 0

    for pdf in ANIA_PDFS:
        filepath = os.path.join(PDF_DIR, pdf["filename"])
        if os.path.exists(filepath) and os.path.getsize(filepath) > 1000:
            size = os.path.getsize(filepath)
            total_size += size
            print(f"  [OK]      {pdf['filename']} ({format_size(size)})")
            ok += 1
        else:
            print(f"  [MANCANTE] {pdf['filename']}")
            print(f"             URL: {pdf['url']}")
            missing += 1

    print(f"\n{'=' * 70}")
    print(f"Scaricati: {ok}/{len(ANIA_PDFS)} ({format_size(total_size)})")
    print(f"Mancanti:  {missing}/{len(ANIA_PDFS)}")
    print(f"{'=' * 70}")


def main():
    parser = argparse.ArgumentParser(description="Download report ANIA (PDF)")
    parser.add_argument("--check", action="store_true", help="Mostra solo lo stato")
    parser.add_argument("--force", action="store_true", help="Riscarica tutto")
    parser.add_argument("--dry-run", action="store_true",
                        help="Mostra cosa scaricherebbe senza scaricare")
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
    success = 0
    failed = 0
    skipped = 0

    for i, pdf in enumerate(ANIA_PDFS, 1):
        filepath = os.path.join(PDF_DIR, pdf["filename"])

        if not args.force and os.path.exists(filepath) and os.path.getsize(filepath) > 1000:
            size = os.path.getsize(filepath)
            with open(filepath, "rb") as fh:
                sha = hashlib.sha256(fh.read()).hexdigest()
            print(f"[{i}/{len(ANIA_PDFS)}] SKIP (esiste): {pdf['filename']} "
                  f"({format_size(size)})")
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

        if args.dry_run:
            print(f"[{i}/{len(ANIA_PDFS)}] [DRY RUN] scaricherei: {pdf['filename']}")
            print(f"    URL: {pdf['url']}")
            continue

        print(f"[{i}/{len(ANIA_PDFS)}] Download: {pdf['filename']}")
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
            print(f"    FALLITO")
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

        if i < len(ANIA_PDFS):
            time.sleep(1)

    if args.dry_run:
        print("\n[DRY RUN] Nessun file scaricato.")
        return 0

    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump({
            "description": "ANIA report PDF collection manifest",
            "download_date": time.strftime("%Y-%m-%d"),
            "note": "Esegui 'python3 scripts/download_ania_reports.py' per i PDF mancanti",
            "total": len(ANIA_PDFS),
            "downloaded": success,
            "failed": failed,
            "files": manifest,
        }, f, indent=2, ensure_ascii=False)

    print(f"\n{'=' * 70}")
    downloaded = success - skipped
    print(f"RISULTATO: {success}/{len(ANIA_PDFS)} disponibili "
          f"({downloaded} nuovi, {skipped} gia presenti)")
    if failed > 0:
        print(f"           {failed} download falliti")
    total_size = sum(f["size_bytes"] for f in manifest)
    print(f"Dimensione totale: {format_size(total_size)}")
    print(f"Manifest: {MANIFEST_PATH}")
    print(f"{'=' * 70}")

    # I download falliti non sono un errore fatale della pipeline: gli URL ANIA
    # con token di versione possono scadere. Lo stato e comunque nel manifest.
    return 0


if __name__ == "__main__":
    sys.exit(main())
