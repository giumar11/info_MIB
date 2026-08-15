#!/usr/bin/env python3
"""
Download dei report ORIGINALI di ANIA (Associazione Nazionale fra le Imprese
Assicuratrici).

ANIA e' l'associazione di categoria delle imprese assicurative operanti in
Italia. I suoi rapporti sono la fonte primaria sul mercato assicurativo
italiano, incluso il ramo salute/malattia e la sanita' integrativa (fondi
sanitari, welfare aziendale) - dati rilevanti per l'analisi della spesa
sanitaria privata e del secondo/terzo pilastro sanitario.

Il rapporto di punta e' "L'Assicurazione Italiana", pubblicazione annuale che
copre l'intero mercato (Vita, Danni, Auto, Salute) con appendice statistica.

Salva i PDF originali in datasets/raw/ania/pdf/ e genera un manifest.

Usage:
    python3 scripts/download_ania_reports.py           # Scarica i PDF mancanti
    python3 scripts/download_ania_reports.py --check   # Mostra solo lo stato
    python3 scripts/download_ania_reports.py --force    # Ri-scarica tutto
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

# Report ANIA con URL diretti verificati.
# "url" e' la fonte primaria (ania.it); "mirror" e' una copia pubblica di
# riserva usata solo se la primaria non risponde.
ANIA_REPORTS = [
    # --- Rapporto annuale "L'Assicurazione Italiana" ---
    {
        "filename": "LAssicurazione_Italiana_2025-2026.pdf",
        "url": "https://www.ania.it/wp-content/uploads/2026/07/LAssicurazione-Italiana-2025-2026.pdf",
        "category": "rapporto_annuale",
        "edition": "2025-2026",
        "year": 2026,
        "title": "L'Assicurazione Italiana 2025-2026",
    },
    {
        "filename": "LAssicurazione_Italiana_2024-2025.pdf",
        "url": "https://www.ania.it/wp-content/uploads/2026/03/LAssicurazione-Italiana-2024-2025.pdf",
        "category": "rapporto_annuale",
        "edition": "2024-2025",
        "year": 2025,
        "title": "L'Assicurazione Italiana 2024-2025",
    },
    {
        "filename": "LAssicurazione_Italiana_2022-2023.pdf",
        "url": "https://www.ania.it/documents/35135/0/LAssicurazione-Italiana-2022-2023.pdf",
        "mirror": "https://www.publicpolicy.it/wp-content/uploads/2023/07/LAssicurazione-Italiana-2022-2023.pdf",
        "category": "rapporto_annuale",
        "edition": "2022-2023",
        "year": 2023,
        "title": "L'Assicurazione Italiana 2022-2023",
    },
    {
        "filename": "LAssicurazione_Italiana_2020-2021.pdf",
        "url": "https://www.ania.it/wp-content/uploads/2026/03/LAssicurazione-Italiana-2020-2021.pdf",
        "category": "rapporto_annuale",
        "edition": "2020-2021",
        "year": 2021,
        "title": "L'Assicurazione Italiana 2020-2021",
    },
    {
        "filename": "LAssicurazione_Italiana_2019-2020.pdf",
        "url": "https://www.ania.it/wp-content/uploads/2026/03/LAssicurazione-Italiana-2019-2020.pdf",
        "category": "rapporto_annuale",
        "edition": "2019-2020",
        "year": 2020,
        "title": "L'Assicurazione Italiana 2019-2020",
    },
    {
        "filename": "LAssicurazione_Italiana_2012-2013.pdf",
        "url": "https://www.ania.it/documents/35135/0/Assicurazione-Italiana-2012-2013.pdf",
        "category": "rapporto_annuale",
        "edition": "2012-2013",
        "year": 2013,
        "title": "L'Assicurazione Italiana 2012-2013",
    },
    # --- Sintesi / cifre chiave ---
    {
        "filename": "LAssicurazione_Italiana_in_cifre_2016.pdf",
        "url": "https://www.ania.it/documents/35135/343147/LAssicurazione-Italiana-in-cifre-ed.-2016.pdf",
        "category": "cifre_chiave",
        "edition": "2016",
        "year": 2016,
        "title": "L'Assicurazione Italiana in cifre - ed. 2016",
    },
]


def build_ssl_context():
    """Contesto SSL tollerante verso catene TLS mal configurate su alcuni host."""
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
            print(f"  [MISSING] {rep['filename']}")
            print(f"            URL: {rep['url']}")
            missing += 1

    print(f"\n{'=' * 70}")
    print(f"Scaricati: {ok}/{len(ANIA_REPORTS)} ({format_size(total_size)})")
    print(f"Mancanti:  {missing}/{len(ANIA_REPORTS)}")
    print(f"{'=' * 70}")


def main():
    parser = argparse.ArgumentParser(description="Download report ANIA (originali)")
    parser.add_argument("--check", action="store_true", help="Mostra solo lo stato")
    parser.add_argument("--force", action="store_true", help="Ri-scarica tutto")
    args = parser.parse_args()

    os.makedirs(PDF_DIR, exist_ok=True)

    if args.check:
        check_status()
        return 0

    print("=" * 70)
    print("DOWNLOAD REPORT ANIA - PDF ORIGINALI")
    print("=" * 70)
    print(f"\nTarget: {PDF_DIR}")
    print(f"Report totali: {len(ANIA_REPORTS)}\n")

    ctx = build_ssl_context()
    manifest = []
    success = failed = skipped = 0

    for i, rep in enumerate(ANIA_REPORTS, 1):
        filepath = os.path.join(PDF_DIR, rep["filename"])

        if not args.force and os.path.exists(filepath) and os.path.getsize(filepath) > 1000:
            size = os.path.getsize(filepath)
            with open(filepath, "rb") as fh:
                sha = hashlib.sha256(fh.read()).hexdigest()
            print(f"[{i}/{len(ANIA_REPORTS)}] SKIP (esiste): {rep['filename']} "
                  f"({format_size(size)})")
            manifest.append({**_meta(rep), "size_bytes": size,
                             "size_human": format_size(size), "sha256": sha,
                             "status": "ok"})
            success += 1
            skipped += 1
            continue

        print(f"[{i}/{len(ANIA_REPORTS)}] Download: {rep['filename']}")
        print(f"    URL: {rep['url']}")
        size, sha = download_pdf(rep["url"], filepath, ctx)

        # Fallback sul mirror se la fonte primaria non risponde
        if not size and rep.get("mirror"):
            print(f"    Fonte primaria non disponibile, provo il mirror...")
            print(f"    MIRROR: {rep['mirror']}")
            size, sha = download_pdf(rep["mirror"], filepath, ctx)

        if size:
            print(f"    OK: {format_size(size)}")
            manifest.append({**_meta(rep), "size_bytes": size,
                             "size_human": format_size(size), "sha256": sha,
                             "status": "ok"})
            success += 1
        else:
            print("    FAILED")
            manifest.append({**_meta(rep), "size_bytes": 0, "sha256": None,
                             "status": "failed"})
            failed += 1

        if i < len(ANIA_REPORTS):
            time.sleep(1)

    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump({
            "description": "ANIA report PDF collection manifest",
            "owner": "ANIA - Associazione Nazionale fra le Imprese Assicuratrici",
            "source": "https://www.ania.it/pubblicazioni",
            "download_date": time.strftime("%Y-%m-%d"),
            "note": "Esegui 'python3 scripts/download_ania_reports.py' per i PDF mancanti",
            "total": len(ANIA_REPORTS),
            "downloaded": success,
            "failed": failed,
            "files": manifest,
        }, f, indent=2, ensure_ascii=False)

    downloaded = success - skipped
    print(f"\n{'=' * 70}")
    print(f"RISULTATO: {success}/{len(ANIA_REPORTS)} disponibili "
          f"({downloaded} nuovi, {skipped} gia' presenti)")
    if failed:
        print(f"           {failed} download falliti")
    total_size = sum(f["size_bytes"] for f in manifest)
    print(f"Dimensione totale: {format_size(total_size)}")
    print(f"Manifest: {MANIFEST_PATH}")
    print(f"{'=' * 70}")

    return 0 if failed == 0 else 1


def _meta(rep):
    """Estrae i campi descrittivi (senza url tecnici) per il manifest."""
    return {
        "filename": rep["filename"],
        "title": rep["title"],
        "category": rep["category"],
        "edition": rep["edition"],
        "year": rep["year"],
        "url": rep["url"],
    }


if __name__ == "__main__":
    sys.exit(main())
