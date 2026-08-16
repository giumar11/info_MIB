#!/usr/bin/env python3
"""
Download dei report originali ANIA (Associazione Nazionale fra le Imprese
Assicuratrici) - settore assicurativo, con focus su salute, welfare integrativo
e spesa sanitaria privata.

Scarica i PDF originali della relazione annuale "L'Assicurazione Italiana"
(che contiene la sezione salute/welfare e i dati su assicurazioni malattia),
delle relative appendici statistiche e delle edizioni in lingua inglese.

I file vengono salvati in datasets/raw/ania/pdf/ .

Usage:
    python3 scripts/download_ania_reports.py           # Scarica i PDF mancanti
    python3 scripts/download_ania_reports.py --check    # Mostra solo lo stato
    python3 scripts/download_ania_reports.py --force     # Riscarica tutto

Nota: come per gli altri downloader del repository, gli URL sono link pubblici
diretti ai PDF originali. Alcuni portali possono spostare i file: i download
falliti vengono registrati nel manifest con status "failed" senza interrompere
l'esecuzione.
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

# Report ANIA con URL pubblici diretti ai PDF originali.
# Fonte principale: portale pubblicazioni ANIA (www.ania.it) - alcune edizioni
# storiche sono servite da mirror istituzionali pubblici.
ANIA_PDFS = [
    # --- Relazione annuale "L'Assicurazione Italiana" (edizione italiana) ---
    {
        "filename": "LAssicurazione_Italiana_2025-2026.pdf",
        "url": "https://www.ania.it/wp-content/uploads/2026/07/LAssicurazione-Italiana-2025-2026.pdf",
        "category": "relazione_annuale",
        "edition": "2025-2026",
        "year": 2026,
    },
    {
        "filename": "LAssicurazione_Italiana_2024-2025.pdf",
        "url": "https://www.ania.it/wp-content/uploads/2026/03/LAssicurazione-Italiana-2024-2025.pdf",
        "category": "relazione_annuale",
        "edition": "2024-2025",
        "year": 2025,
    },
    {
        "filename": "LAssicurazione_Italiana_2023-2024.pdf",
        "url": "https://www.ania.it/wp-content/uploads/2026/03/LAssicurazione-Italiana-2023-2024.pdf",
        "category": "relazione_annuale",
        "edition": "2023-2024",
        "year": 2024,
    },
    {
        "filename": "LAssicurazione_Italiana_2022-2023.pdf",
        "url": "https://www.ania.it/wp-content/uploads/2026/03/LAssicurazione-Italiana-2022-2023.pdf",
        "category": "relazione_annuale",
        "edition": "2022-2023",
        "year": 2023,
    },
    {
        "filename": "LAssicurazione_Italiana_2021-2022.pdf",
        "url": "https://www.ania.it/wp-content/uploads/2026/03/LAssicurazione-Italiana-2021-2022.pdf",
        "category": "relazione_annuale",
        "edition": "2021-2022",
        "year": 2022,
    },
    {
        "filename": "LAssicurazione_Italiana_2020-2021.pdf",
        "url": "https://www.ania.it/documents/35135/126701/L'Assicurazione+Italiana+2020-2021.pdf/e4fa652e-dda7-8c9c-96ef-1e4468d4f903?version=1.0&t=1626333153413",
        "category": "relazione_annuale",
        "edition": "2020-2021",
        "year": 2021,
    },
    {
        "filename": "LAssicurazione_Italiana_2016-2017.pdf",
        "url": "https://www.simlaweb.it/wp-content/uploads/documenti/documenti-vari/Rapporto-ANIA-lassicurazione-italiana-2016-2017-1.pdf",
        "category": "relazione_annuale",
        "edition": "2016-2017",
        "year": 2017,
    },
    # --- Edizioni in lingua inglese "Italian Insurance" ---
    {
        "filename": "Italian_Insurance_2022-2023_EN.pdf",
        "url": "https://www.ania.it/wp-content/uploads/2026/03/Italian-Insurance-2022-2023-WEB.pdf",
        "category": "annual_report_en",
        "edition": "2022-2023 (EN)",
        "year": 2023,
    },
    {
        "filename": "Italian_Insurance_2022_EN.pdf",
        "url": "https://www.ania.it/wp-content/uploads/2026/03/ITALIAN-INSURANCE-2022-EN_WEBVER.pdf",
        "category": "annual_report_en",
        "edition": "2022 (EN)",
        "year": 2022,
    },
]

# Mirror pubblici alternativi usati come fallback se l'URL primario fallisce.
FALLBACK_URLS = {
    "LAssicurazione_Italiana_2023-2024.pdf": [
        "https://www.astrid-online.it/static/upload/lass/lassicurazione-italiana-2024_web_def.pdf",
    ],
    "LAssicurazione_Italiana_2022-2023.pdf": [
        "https://www.publicpolicy.it/wp-content/uploads/2023/07/LAssicurazione-Italiana-2022-2023.pdf",
    ],
}


def build_ssl_context():
    """Contesto TLS che tollera catene di certificati non standard dei portali."""
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx


def download_pdf(url, filepath, ctx, max_retries=3):
    """Scarica un PDF con retry ed exponential backoff."""
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
                          "potrebbe non essere valido")
                    return None, None

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
    print("STATO DOWNLOAD REPORT ANIA")
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
    if missing:
        print("\nEsegui senza --check per scaricare i PDF mancanti")
    print("=" * 70)


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
    print("DOWNLOAD REPORT ANIA - PDF ORIGINALI")
    print("=" * 70)
    print(f"\nTarget: {PDF_DIR}")
    print(f"Report totali: {len(ANIA_PDFS)}\n")

    ctx = build_ssl_context()
    manifest = []
    success = failed = skipped = 0

    for i, pdf in enumerate(ANIA_PDFS, 1):
        filepath = os.path.join(PDF_DIR, pdf["filename"])

        if not args.force and os.path.exists(filepath) and os.path.getsize(filepath) > 1000:
            size = os.path.getsize(filepath)
            with open(filepath, "rb") as fh:
                sha = hashlib.sha256(fh.read()).hexdigest()
            print(f"[{i}/{len(ANIA_PDFS)}] SKIP (esiste): {pdf['filename']} "
                  f"({format_size(size)})")
            manifest.append({**pdf, "size_bytes": size,
                             "size_human": format_size(size),
                             "sha256": sha, "status": "ok"})
            success += 1
            skipped += 1
            continue

        print(f"[{i}/{len(ANIA_PDFS)}] Download: {pdf['filename']}")
        urls = [pdf["url"]] + FALLBACK_URLS.get(pdf["filename"], [])
        size = sha = None
        used_url = pdf["url"]
        for url in urls:
            print(f"    URL: {url}")
            size, sha = download_pdf(url, filepath, ctx)
            if size:
                used_url = url
                break

        if size:
            print(f"    OK: {format_size(size)}")
            manifest.append({**pdf, "url": used_url, "size_bytes": size,
                             "size_human": format_size(size),
                             "sha256": sha, "status": "ok"})
            success += 1
        else:
            print("    FALLITO")
            manifest.append({**pdf, "size_bytes": 0, "sha256": None,
                             "status": "failed"})
            failed += 1

        if i < len(ANIA_PDFS):
            time.sleep(1)

    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump({
            "description": "Collezione report originali ANIA (settore assicurativo)",
            "source": "ANIA - Associazione Nazionale fra le Imprese Assicuratrici",
            "portal": "https://www.ania.it/pubblicazioni",
            "download_date": time.strftime("%Y-%m-%d"),
            "note": "Esegui 'python3 scripts/download_ania_reports.py' per scaricare i PDF mancanti",
            "total": len(ANIA_PDFS),
            "downloaded": success,
            "failed": failed,
            "files": manifest,
        }, f, indent=2, ensure_ascii=False)

    print(f"\n{'=' * 70}")
    downloaded = success - skipped
    print(f"RISULTATO: {success}/{len(ANIA_PDFS)} disponibili "
          f"({downloaded} nuovi, {skipped} gia' presenti)")
    if failed:
        print(f"           {failed} download falliti")
    total_size = sum(f["size_bytes"] for f in manifest)
    print(f"Dimensione totale: {format_size(total_size)}")
    print(f"Manifest: {MANIFEST_PATH}")
    print("=" * 70)

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
