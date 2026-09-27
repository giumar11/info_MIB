#!/usr/bin/env python3
"""
Download dei report ANIA (Associazione Nazionale fra le Imprese Assicuratrici).

ANIA è la fonte di riferimento per il settore assicurativo italiano, incluse le
coperture del ramo Salute/Malattia e la sanità integrativa, rilevanti per
l'analisi della spesa sanitaria privata e del welfare integrativo.

Scarica i report ORIGINALI in PDF (non estratti elaborati) in
datasets/raw/ania/ e genera un manifest con checksum.

Uso:
    python3 scripts/download_ania_reports.py            # scarica i mancanti
    python3 scripts/download_ania_reports.py --check     # solo stato
    python3 scripts/download_ania_reports.py --force      # riscarica tutto

Note: alcuni URL ania.it possono cambiare quando l'ente ripubblica i file. Lo
scheduler (scripts/scheduler_check_updates.py) verifica periodicamente le fonti
del catalogo e segnala i link non più validi.
"""

import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from enrichment_common import (  # noqa: E402
    download_file, existing_ok, format_size, sha256_of_file,
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ANIA_DIR = os.path.join(BASE_DIR, "datasets", "raw", "ania")
MANIFEST_PATH = os.path.join(ANIA_DIR, "manifest.json")

# Report ANIA pubblici. URL raccolti dalle pubblicazioni ufficiali ania.it.
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
        "filename": "LAssicurazione_Italiana_2023-2024.pdf",
        "url": "https://www.ania.it/wp-content/uploads/2026/03/LAssicurazione-Italiana-2023-2024.pdf",
        "category": "rapporto_annuale",
        "edition": "2023-2024",
        "year": 2024,
        "title": "L'Assicurazione Italiana 2023-2024",
    },
    {
        "filename": "LAssicurazione_Italiana_2021-2022.pdf",
        "url": "https://www.ania.it/wp-content/uploads/2026/03/LAssicurazione-Italiana-2021-2022.pdf",
        "category": "rapporto_annuale",
        "edition": "2021-2022",
        "year": 2022,
        "title": "L'Assicurazione Italiana 2021-2022",
    },
    {
        "filename": "LAssicurazione_Italiana_2020-2021.pdf",
        "url": "https://ania.it/documents/35135/439653/L'Assicurazione+Italiana+2020-2021.pdf/e4fa652e-dda7-8c9c-96ef-1e4468d4f903?t=1631084761328",
        "category": "rapporto_annuale",
        "edition": "2020-2021",
        "year": 2021,
        "title": "L'Assicurazione Italiana 2020-2021",
    },
    {
        "filename": "Italian_Insurance_2022-2023_EN.pdf",
        "url": "https://ania.it/wp-content/uploads/2026/03/Italian-Insurance-2022-2023-WEB.pdf",
        "category": "rapporto_annuale",
        "edition": "2022-2023 (EN)",
        "year": 2023,
        "title": "Italian Insurance 2022-2023 (English edition)",
    },
    # --- Report tematici ---
    {
        "filename": "Report_PAI_settore_assicurativo_italiano.pdf",
        "url": "https://ania.it/documents/35135/144872/Report+PAI+del+settore+assicurativo+italiano.pdf/6296a5e1-ceea-f192-648f-0f2d6173257b?t=1756818641521&version=1.0",
        "category": "report_tematico",
        "edition": "PAI",
        "year": None,
        "title": "Report PAI del settore assicurativo italiano",
    },
]


def check_status():
    print("=" * 70)
    print("STATO DOWNLOAD REPORT ANIA")
    print("=" * 70)
    print(f"\nDirectory: {ANIA_DIR}\n")
    ok = missing = 0
    total_size = 0
    for rep in ANIA_REPORTS:
        path = os.path.join(ANIA_DIR, rep["filename"])
        if existing_ok(path):
            size = os.path.getsize(path)
            total_size += size
            print(f"  [OK]      {rep['filename']} ({format_size(size)})")
            ok += 1
        else:
            print(f"  [MANCANTE] {rep['filename']}")
            print(f"             URL: {rep['url']}")
            missing += 1
    print(f"\n{'=' * 70}")
    print(f"Presenti: {ok}/{len(ANIA_REPORTS)} ({format_size(total_size)})")
    print(f"Mancanti: {missing}/{len(ANIA_REPORTS)}")
    print("=" * 70)


def write_manifest(entries, success, failed):
    manifest = {
        "description": "Report ANIA (settore assicurativo italiano) - collezione originali",
        "owner": "ANIA - Associazione Nazionale fra le Imprese Assicuratrici",
        "source": "https://www.ania.it/pubblicazioni/",
        "download_date": time.strftime("%Y-%m-%d"),
        "total": len(ANIA_REPORTS),
        "downloaded": success,
        "failed": failed,
        "files": entries,
    }
    os.makedirs(ANIA_DIR, exist_ok=True)
    with open(MANIFEST_PATH, "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2, ensure_ascii=False)


def main():
    parser = argparse.ArgumentParser(description="Download report ANIA (assicurativo)")
    parser.add_argument("--check", action="store_true", help="Mostra solo lo stato")
    parser.add_argument("--force", action="store_true", help="Riscarica tutti i file")
    parser.add_argument("--insecure", action="store_true",
                        help="Disattiva la verifica TLS (per host con catena CA incompleta)")
    args = parser.parse_args()

    os.makedirs(ANIA_DIR, exist_ok=True)

    if args.check:
        check_status()
        return 0

    print("=" * 70)
    print("DOWNLOAD REPORT ANIA - ORIGINALI PDF")
    print("=" * 70)
    print(f"\nTarget: {ANIA_DIR}\nReport totali: {len(ANIA_REPORTS)}\n")

    entries = []
    success = failed = skipped = 0

    for i, rep in enumerate(ANIA_REPORTS, 1):
        path = os.path.join(ANIA_DIR, rep["filename"])

        if not args.force and existing_ok(path):
            size = os.path.getsize(path)
            print(f"[{i}/{len(ANIA_REPORTS)}] SKIP (presente): {rep['filename']} ({format_size(size)})")
            entries.append({**{k: rep[k] for k in ("filename", "category", "edition", "year", "title", "url")},
                            "size_bytes": size, "sha256": sha256_of_file(path), "status": "ok"})
            success += 1
            skipped += 1
            continue

        print(f"[{i}/{len(ANIA_REPORTS)}] Download: {rep['filename']}")
        print(f"    URL: {rep['url']}")
        res = download_file(rep["url"], path, expect_pdf=True, insecure=args.insecure)

        entry = {k: rep[k] for k in ("filename", "category", "edition", "year", "title", "url")}
        entry.update({"size_bytes": res["size_bytes"], "sha256": res["sha256"], "status": res["status"]})
        entries.append(entry)

        if res["status"] == "ok":
            print(f"    OK: {format_size(res['size_bytes'])}")
            success += 1
        else:
            print(f"    FALLITO: {res.get('error')}")
            failed += 1

        if i < len(ANIA_REPORTS):
            time.sleep(1)

    write_manifest(entries, success, failed)

    print(f"\n{'=' * 70}")
    print(f"RISULTATO: {success}/{len(ANIA_REPORTS)} disponibili "
          f"({success - skipped} nuovi, {skipped} già presenti)")
    if failed:
        print(f"           {failed} download falliti")
    print(f"Manifest: {MANIFEST_PATH}")
    print("=" * 70)
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
