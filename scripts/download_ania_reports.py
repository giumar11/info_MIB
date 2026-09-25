#!/usr/bin/env python3
"""
Download dei report ANIA (Associazione Nazionale fra le Imprese Assicuratrici).

Scarica i documenti ORIGINALI (PDF) pubblicati da ANIA sul mercato assicurativo
italiano, con particolare attenzione all'ambito salute/sanità (assicurazione
malattia, RC sanitaria, welfare integrativo).

I file vengono salvati in: datasets/raw/ania/pdf/

Usage:
    python3 scripts/download_ania_reports.py            # Scarica i PDF mancanti
    python3 scripts/download_ania_reports.py --check    # Mostra solo lo stato
    python3 scripts/download_ania_reports.py --force     # Riscarica tutto

Nota sulle URL:
    Il portale ANIA (Liferay) usa URL con GUID che possono ruotare nel tempo.
    Quando un download fallisce viene registrato nel manifest con status "failed":
    lo scheduler giornaliero (scripts/daily_enrichment.py) monitora comunque le
    pagine-catalogo ANIA (vedi sources_catalog.csv) per individuare nuove
    edizioni, i cui link diretti vanno poi aggiunti alla lista ANIA_REPORTS.
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

# Report ANIA con link diretti verificati.
# category:  rapporto_annuale | in_cifre | ania_trends | tematico
ANIA_REPORTS = [
    # --- L'Assicurazione Italiana (rapporto annuale) ---
    {
        "filename": "Assicurazione_Italiana_2016_2017.pdf",
        "url": "http://www.ania.it/export/sites/default/it/pubblicazioni/rapporti-annuali/Assicurazione-Italiana/2016-2017/assicurazione_italiana_2016_2017.pdf",
        "category": "rapporto_annuale",
        "edition": "2016-2017",
        "year": 2017,
    },
    {
        "filename": "Assicurazione_Italiana_2020_2021.pdf",
        "url": "https://www.ania.it/documents/35135/126701/L'Assicurazione+Italiana+2020-2021.pdf/e4fa652e-dda7-8c9c-96ef-1e4468d4f903?version=1.0&t=1626333153413",
        "category": "rapporto_annuale",
        "edition": "2020-2021",
        "year": 2021,
    },
    # --- L'Assicurazione Italiana in Cifre / Italian Insurance in Figures ---
    {
        "filename": "Assicurazione_Italiana_in_Cifre_2015_ita.pdf",
        "url": "https://ania.it/wp-content/uploads/2026/03/Ass-in-cifre-15x21-2015-ita-web.pdf",
        "category": "in_cifre",
        "edition": "2015 (ITA)",
        "year": 2015,
    },
    {
        "filename": "Italian_Insurance_in_Figures_2015_eng.pdf",
        "url": "https://www.ania.it/documents/35135/126704/Ass-in-cifre-15x21-2015-ingl-web.pdf/fc5d128f-4699-bb51-d57c-b735a3e067f2?t=1575556097957",
        "category": "in_cifre",
        "edition": "2015 (ENG)",
        "year": 2015,
    },
    # --- ANIA Trends (collane periodiche) ---
    {
        "filename": "ANIA_Trends_Focus_RC_Sanitaria.pdf",
        "url": "http://www.ania.it/export/sites/default/it/pubblicazioni/COLLANE-PERIODICHE/ANIA-Trends/ANIA-Trends-Focus-RC-Sanitaria/Ania-Trends-Focus-RC-Sanitaria.pdf",
        "category": "ania_trends",
        "edition": "Focus RC Sanitaria",
        "year": 2019,
    },
    # --- Report tematici ---
    {
        "filename": "Report_PAI_settore_assicurativo_italiano.pdf",
        "url": "https://ania.it/documents/35135/144872/Report+PAI+del+settore+assicurativo+italiano.pdf/6296a5e1-ceea-f192-648f-0f2d6173257b?t=1756818641521&version=1.0",
        "category": "tematico",
        "edition": "Report PAI",
        "year": 2025,
    },
]


def download_pdf(url, filepath, max_retries=3):
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

                if len(data) < 1000:
                    print(f"    WARNING: file troppo piccolo ({len(data)} byte), "
                          f"potrebbe non essere valido")

                with open(filepath, "wb") as f:
                    f.write(data)

                return len(data), hashlib.sha256(data).hexdigest()

        except (urllib.error.URLError, urllib.error.HTTPError, OSError) as e:
            wait = 2 ** (attempt + 1)
            print(f"    Tentativo {attempt + 1}/{max_retries} fallito: {e}")
            if attempt < max_retries - 1:
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
    """Mostra lo stato dei download senza scaricare nulla."""
    print("=" * 70)
    print("STATO DOWNLOAD REPORT ANIA")
    print("=" * 70)
    print(f"\nDirectory: {PDF_DIR}\n")

    ok = missing = total_size = 0
    for rep in ANIA_REPORTS:
        filepath = os.path.join(PDF_DIR, rep["filename"])
        if os.path.exists(filepath) and os.path.getsize(filepath) > 1000:
            size = os.path.getsize(filepath)
            total_size += size
            print(f"  [OK]      {rep['filename']} ({format_size(size)})")
            ok += 1
        else:
            print(f"  [MANCANTE] {rep['filename']}")
            print(f"             URL: {rep['url']}")
            missing += 1

    print(f"\n{'=' * 70}")
    print(f"Scaricati: {ok}/{len(ANIA_REPORTS)} ({format_size(total_size)})")
    print(f"Mancanti:  {missing}/{len(ANIA_REPORTS)}")
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
    success = failed = skipped = 0

    for i, rep in enumerate(ANIA_REPORTS, 1):
        filepath = os.path.join(PDF_DIR, rep["filename"])

        if not args.force and os.path.exists(filepath) and os.path.getsize(filepath) > 1000:
            size = os.path.getsize(filepath)
            with open(filepath, "rb") as f:
                sha = hashlib.sha256(f.read()).hexdigest()
            print(f"[{i}/{len(ANIA_REPORTS)}] SKIP (esiste): {rep['filename']} "
                  f"({format_size(size)})")
            manifest.append({**{k: rep[k] for k in ("filename", "category", "edition", "year", "url")},
                             "size_bytes": size, "size_human": format_size(size),
                             "sha256": sha, "status": "ok"})
            success += 1
            skipped += 1
            continue

        print(f"[{i}/{len(ANIA_REPORTS)}] Download: {rep['filename']}")
        print(f"    URL: {rep['url']}")
        size, sha = download_pdf(rep["url"], filepath)

        if size:
            print(f"    OK: {format_size(size)}")
            manifest.append({**{k: rep[k] for k in ("filename", "category", "edition", "year", "url")},
                             "size_bytes": size, "size_human": format_size(size),
                             "sha256": sha, "status": "ok"})
            success += 1
        else:
            print(f"    FALLITO")
            manifest.append({**{k: rep[k] for k in ("filename", "category", "edition", "year", "url")},
                             "size_bytes": 0, "sha256": None, "status": "failed"})
            failed += 1

        if i < len(ANIA_REPORTS):
            time.sleep(1)

    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump({
            "description": "ANIA report PDF collection manifest",
            "download_date": time.strftime("%Y-%m-%d"),
            "note": "Esegui 'python3 scripts/download_ania_reports.py' per scaricare i PDF mancanti",
            "total": len(ANIA_REPORTS),
            "downloaded": success,
            "failed": failed,
            "files": manifest,
        }, f, indent=2, ensure_ascii=False)

    print(f"\n{'=' * 70}")
    downloaded = success - skipped
    print(f"RISULTATO: {success}/{len(ANIA_REPORTS)} disponibili "
          f"({downloaded} nuovi, {skipped} già presenti)")
    if failed:
        print(f"           {failed} download falliti")
    total_size = sum(f["size_bytes"] for f in manifest)
    print(f"Dimensione totale: {format_size(total_size)}")
    print(f"Manifest: {MANIFEST_PATH}")
    print(f"{'=' * 70}")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
