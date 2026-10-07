#!/usr/bin/env python3
"""
Download dei report ANIA (Associazione Nazionale fra le Imprese Assicuratrici).

Scarica i documenti originali pubblicati da ANIA (rapporti annuali
"L'Assicurazione Italiana", appendici statistiche, dossier tematici) nella
cartella datasets/raw/ania/.

ANIA pubblica i documenti sul proprio portale Liferay con URL "asset" opachi.
Per ogni report sono indicati:
  - url:    link diretto al PDF, quando noto e verificabile
  - page:   pagina ufficiale di pubblicazione da cui risolvere il PDF

Gli elementi con url diretto vengono scaricati; quelli con sola `page`
vengono registrati nel manifest come "pending_url" (da risolvere dalla
pagina di pubblicazione) senza scaricare HTML al posto del PDF.

Usage:
    python3 scripts/download_ania_pdfs.py            # scarica i PDF mancanti
    python3 scripts/download_ania_pdfs.py --check    # mostra solo lo stato
    python3 scripts/download_ania_pdfs.py --force    # riscarica tutto
"""

import argparse
import hashlib
import json
import os
import sys
import time
import urllib.error
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from stable_json import write_json_stable

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ANIA_DIR = os.path.join(BASE_DIR, "datasets", "raw", "ania")
PDF_DIR = os.path.join(ANIA_DIR, "pdf")
MANIFEST_PATH = os.path.join(ANIA_DIR, "download_manifest.json")

# Pagine ufficiali di pubblicazione ANIA (fonte autorevole per risolvere i PDF)
ANIA_PUBLICATIONS_PAGES = {
    "assicurazione_italiana": "https://www.ania.it/pubblicazioni/-/categories/53729",
    "pubblicazioni_generali": "https://www.ania.it/pubblicazioni/-/categories/53705",
    "home_pubblicazioni": "https://www.ania.it/pubblicazioni/",
}

# Catalogo report ANIA.
#   - url  : link diretto al PDF (verrà scaricato se presente)
#   - page : pagina ufficiale da cui risolvere il PDF (per i "pending_url")
ANIA_REPORTS = [
    # --- Rapporto annuale "L'Assicurazione Italiana" ---
    {
        "filename": "ANIA_Assicurazione_Italiana_2024_2025.pdf",
        "category": "rapporto_annuale",
        "edition": "2024-2025",
        "year": 2025,
        "title": "L'Assicurazione Italiana 2024-2025",
        "url": None,
        "page": "https://www.ania.it/pubblicazioni/-/categories/53729",
    },
    {
        "filename": "ANIA_Assicurazione_Italiana_2023_2024.pdf",
        "category": "rapporto_annuale",
        "edition": "2023-2024",
        "year": 2024,
        "title": "L'Assicurazione Italiana 2023-2024",
        "url": None,
        "page": "https://www.ania.it/pubblicazioni/-/categories/53729",
    },
    {
        "filename": "ANIA_Assicurazione_Italiana_2022_2023.pdf",
        "category": "rapporto_annuale",
        "edition": "2022-2023",
        "year": 2023,
        "title": "L'Assicurazione Italiana 2022-2023",
        "url": None,
        "page": "https://www.ania.it/dettaglio/-/asset_publisher/sj4agTtNdEk3/document/id/689939",
    },
    {
        "filename": "ANIA_Assicurazione_Italiana_2021_2022.pdf",
        "category": "rapporto_annuale",
        "edition": "2021-2022",
        "year": 2022,
        "title": "L'Assicurazione Italiana 2021-2022",
        "url": None,
        "page": "https://www.ania.it/pubblicazioni/-/categories/53729",
    },
    {
        "filename": "ANIA_Assicurazione_Italiana_2020_2021.pdf",
        "category": "rapporto_annuale",
        "edition": "2020-2021",
        "year": 2021,
        "title": "L'Assicurazione Italiana 2020-2021",
        "url": None,
        "page": "https://www.ania.it/pubblicazioni/-/categories/53729",
    },
    {
        "filename": "ANIA_Assicurazione_Italiana_2019_2020.pdf",
        "category": "rapporto_annuale",
        "edition": "2019-2020",
        "year": 2020,
        "title": "L'Assicurazione Italiana 2019-2020",
        "url": None,
        "page": "https://www.ania.it/pubblicazioni/-/categories/53729",
    },
    {
        "filename": "ANIA_Assicurazione_Italiana_2018_2019.pdf",
        "category": "rapporto_annuale",
        "edition": "2018-2019",
        "year": 2019,
        "title": "L'Assicurazione Italiana 2018-2019",
        "url": None,
        "page": "https://www.ania.it/pubblicazioni/-/categories/53729",
    },
    {
        "filename": "ANIA_Assicurazione_Italiana_2017_2018.pdf",
        "category": "rapporto_annuale",
        "edition": "2017-2018",
        "year": 2018,
        "title": "L'Assicurazione Italiana 2017-2018",
        "url": None,
        "page": "https://www.ania.it/pubblicazioni/-/categories/53729",
    },
    {
        "filename": "ANIA_Assicurazione_Italiana_2016_2017.pdf",
        "category": "rapporto_annuale",
        "edition": "2016-2017",
        "year": 2017,
        "title": "L'Assicurazione Italiana 2016-2017",
        "url": "https://www.ania.it/export/sites/default/it/pubblicazioni/rapporti-annuali/"
               "Assicurazione-Italiana/2016-2017/assicurazione_italiana_2016_2017.pdf",
        "page": "https://www.ania.it/pubblicazioni/-/categories/53729",
    },
    {
        "filename": "ANIA_Assicurazione_Italiana_2005_2006.pdf",
        "category": "rapporto_annuale",
        "edition": "2005-2006",
        "year": 2006,
        "title": "L'Assicurazione Italiana 2005-2006",
        "url": "https://www.ania.it/documents/35135/439653/Assicurazione-Italiana-2006.pdf/"
               "5b3ffd4c-8f53-c082-3d29-33521f8ded57?t=1631084720137",
        "page": "https://www.ania.it/pubblicazioni/-/categories/53729",
    },
    {
        "filename": "ANIA_Assicurazione_Italiana_2004_2005.pdf",
        "category": "rapporto_annuale",
        "edition": "2004-2005",
        "year": 2005,
        "title": "L'Assicurazione Italiana 2004-2005",
        "url": "https://www.ania.it/documents/35135/439653/Assicurazione-Italiana+2004-2005.pdf/"
               "8f77f164-e796-e7d4-8be3-6d10ed158151?version=1.1&t=1751436630852",
        "page": "https://www.ania.it/pubblicazioni/-/categories/53729",
    },
    # --- Appendice Statistica alla Relazione Annuale ---
    {
        "filename": "ANIA_Appendice_Statistica_2024_2025.pdf",
        "category": "appendice_statistica",
        "edition": "2024-2025",
        "year": 2025,
        "title": "Appendice Statistica alla Relazione Annuale 2024-2025",
        "url": None,
        "page": "https://www.ania.it/pubblicazioni/-/categories/53729",
    },
    {
        "filename": "ANIA_Appendice_Statistica_2023_2024.pdf",
        "category": "appendice_statistica",
        "edition": "2023-2024",
        "year": 2024,
        "title": "Appendice Statistica alla Relazione Annuale 2023-2024",
        "url": None,
        "page": "https://www.ania.it/pubblicazioni/-/categories/53729",
    },
    # --- Dossier tematici welfare e salute integrativa (rilevanti per il SSN) ---
    {
        "filename": "ANIA_Welfare_Salute_Integrativa.pdf",
        "category": "dossier_welfare_salute",
        "edition": "ultima",
        "year": 2025,
        "title": "Welfare e salute integrativa - dossier tematico ANIA",
        "url": None,
        "page": "https://www.ania.it/pubblicazioni/",
    },
    # --- Estratto in inglese ---
    {
        "filename": "ANIA_Italian_Insurance_2024_2025_EN.pdf",
        "category": "english_extract",
        "edition": "2024-2025",
        "year": 2026,
        "title": "Italian Insurance in 2024-2025 (English extract)",
        "url": None,
        "page": "https://www.ania.it/pubblicazioni/-/categories/53705",
    },
]


def download_pdf(url, filepath, max_retries=3):
    """Scarica un PDF con retry ed exponential backoff. Rispetta HTTPS_PROXY."""
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/pdf,*/*",
    }
    for attempt in range(max_retries):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=120) as resp:
                data = resp.read()
            if len(data) < 1000:
                print(f"    WARNING: file troppo piccolo ({len(data)} byte), "
                      f"potrebbe non essere un PDF valido")
            if not data[:5].startswith(b"%PDF-"):
                print("    WARNING: il contenuto non inizia con %PDF- "
                      "(potrebbe essere una pagina HTML)")
            with open(filepath, "wb") as f:
                f.write(data)
            return len(data), hashlib.sha256(data).hexdigest()
        except (urllib.error.URLError, urllib.error.HTTPError, OSError) as e:
            print(f"    Tentativo {attempt + 1}/{max_retries} fallito: {e}")
            if attempt < max_retries - 1:
                wait = 2 ** (attempt + 1)
                print(f"    Nuovo tentativo tra {wait}s...")
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
    print("STATO DOWNLOAD REPORT ANIA")
    print("=" * 70)
    print(f"\nDirectory: {PDF_DIR}\n")
    ok = missing = pending = 0
    total_size = 0
    for rep in ANIA_REPORTS:
        filepath = os.path.join(PDF_DIR, rep["filename"])
        if os.path.exists(filepath) and os.path.getsize(filepath) > 1000:
            size = os.path.getsize(filepath)
            total_size += size
            print(f"  [OK]       {rep['filename']} ({format_size(size)})")
            ok += 1
        elif rep.get("url"):
            print(f"  [MISSING]  {rep['filename']}")
            missing += 1
        else:
            print(f"  [PENDING]  {rep['filename']} (url da risolvere da: {rep['page']})")
            pending += 1
    print(f"\n{'=' * 70}")
    print(f"Scaricati:        {ok}/{len(ANIA_REPORTS)} ({format_size(total_size)})")
    print(f"Mancanti (url ok): {missing}")
    print(f"Pending (no url):  {pending}")
    print(f"{'=' * 70}")


def main():
    parser = argparse.ArgumentParser(description="Download report ANIA (assicurativo)")
    parser.add_argument("--check", action="store_true", help="Mostra solo lo stato")
    parser.add_argument("--force", action="store_true", help="Riscarica tutto")
    args = parser.parse_args()

    os.makedirs(PDF_DIR, exist_ok=True)

    if args.check:
        check_status()
        return 0

    print("=" * 70)
    print("DOWNLOAD REPORT ANIA - ASSICURATIVO")
    print("=" * 70)
    print(f"\nTarget: {PDF_DIR}")
    print(f"Report totali: {len(ANIA_REPORTS)}\n")

    manifest = []
    success = failed = skipped = pending = 0

    for i, rep in enumerate(ANIA_REPORTS, 1):
        filepath = os.path.join(PDF_DIR, rep["filename"])
        entry = {
            "filename": rep["filename"],
            "category": rep["category"],
            "edition": rep["edition"],
            "year": rep["year"],
            "title": rep["title"],
            "url": rep.get("url"),
            "page": rep.get("page"),
        }

        if not args.force and os.path.exists(filepath) and os.path.getsize(filepath) > 1000:
            size = os.path.getsize(filepath)
            with open(filepath, "rb") as fh:
                sha = hashlib.sha256(fh.read()).hexdigest()
            print(f"[{i}/{len(ANIA_REPORTS)}] SKIP (esiste): {rep['filename']} "
                  f"({format_size(size)})")
            entry.update({"size_bytes": size, "size_human": format_size(size),
                          "sha256": sha, "status": "ok"})
            manifest.append(entry)
            success += 1
            skipped += 1
            continue

        if not rep.get("url"):
            print(f"[{i}/{len(ANIA_REPORTS)}] PENDING (nessun url diretto): "
                  f"{rep['filename']}")
            print(f"    Risolvi il PDF da: {rep['page']}")
            entry.update({"size_bytes": 0, "sha256": None, "status": "pending_url"})
            manifest.append(entry)
            pending += 1
            continue

        print(f"[{i}/{len(ANIA_REPORTS)}] Download: {rep['filename']}")
        print(f"    URL: {rep['url']}")
        size, sha = download_pdf(rep["url"], filepath)
        if size:
            print(f"    OK: {format_size(size)}")
            entry.update({"size_bytes": size, "size_human": format_size(size),
                          "sha256": sha, "status": "ok"})
            success += 1
        else:
            print("    FALLITO")
            entry.update({"size_bytes": 0, "sha256": None, "status": "failed"})
            failed += 1
        manifest.append(entry)
        if i < len(ANIA_REPORTS):
            time.sleep(1)

    write_json_stable({
        "description": "ANIA report collection manifest (assicurativo)",
        "owner": "ANIA - Associazione Nazionale fra le Imprese Assicuratrici",
        "publications_pages": ANIA_PUBLICATIONS_PAGES,
        "download_date": time.strftime("%Y-%m-%d"),
        "total": len(ANIA_REPORTS),
        "downloaded": success,
        "failed": failed,
        "pending_url": pending,
        "files": manifest,
    }, MANIFEST_PATH)

    print(f"\n{'=' * 70}")
    downloaded = success - skipped
    print(f"RISULTATO: {success}/{len(ANIA_REPORTS)} disponibili "
          f"({downloaded} nuovi, {skipped} già presenti)")
    if pending:
        print(f"           {pending} in attesa di url diretto (vedi manifest)")
    if failed:
        print(f"           {failed} download falliti")
    print(f"Manifest: {MANIFEST_PATH}")
    print(f"{'=' * 70}")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
