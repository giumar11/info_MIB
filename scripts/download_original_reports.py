#!/usr/bin/env python3
"""
Download degli ORIGINALI (report e dataset) per le categorie di documenti che
nel repository sono presenti solo come estratti elaborati o come placeholder.

Obiettivo (richiesta esplicita): quando esistono, caricare i dataset e i report
ORIGINALI, non solo gli estratti processati da noi.

Il downloader è guidato da un registro (REGISTRY) organizzato per categoria.
Ogni voce specifica l'URL della fonte ufficiale e il percorso di destinazione
nel repository. È estendibile: per aggiungere una fonte basta aggiungere una
voce alla categoria pertinente.

Uso:
    python3 scripts/download_original_reports.py                 # tutte le categorie
    python3 scripts/download_original_reports.py --category aifa  # solo una categoria
    python3 scripts/download_original_reports.py --list           # elenca le categorie
    python3 scripts/download_original_reports.py --check           # solo stato
    python3 scripts/download_original_reports.py --force           # riscarica tutto
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
MANIFEST_PATH = os.path.join(BASE_DIR, "datasets", "raw", "original_reports_manifest.json")


def _p(*parts):
    """Percorso assoluto relativo alla root del repo."""
    return os.path.join(BASE_DIR, *parts)


# Registro delle fonti originali per categoria.
# dest è relativo alla root del repository. expect_pdf attiva la validazione PDF.
REGISTRY = {
    # AIFA - Osservatorio Nazionale sull'Impiego dei Medicinali (report ufficiali)
    "aifa": [
        {
            "title": "Rapporto OsMed 2023 - L'uso dei farmaci in Italia",
            "url": "https://www.aifa.gov.it/documents/20142/2594020/AIFA_Rapporto%20OsMed_2023.pdf",
            "dest": "datasets/raw/aifa/AIFA_Rapporto_OsMed_2023.pdf",
            "expect_pdf": True,
            "year": 2023,
        },
        {
            "title": "Rapporto OsMed 2025 - L'uso dei farmaci in Italia",
            "url": "https://www.aifa.gov.it/documents/20142/3941839/AIFA_Rapporto_OsMed_2025.pdf",
            "dest": "datasets/raw/aifa/AIFA_Rapporto_OsMed_2025.pdf",
            "expect_pdf": True,
            "year": 2025,
        },
    ],
    # OsMed sotto finanza (sostituisce il placeholder da 0 byte con l'originale)
    "osmed": [
        {
            "title": "Rapporto OsMed 2023 (spesa farmaceutica)",
            "url": "https://www.aifa.gov.it/documents/20142/2594020/AIFA_Rapporto%20OsMed_2023.pdf",
            "dest": "datasets/raw/finanza/osmed/rapporto_osmed_2023.pdf",
            "expect_pdf": True,
            "year": 2023,
        },
    ],
}


def iter_entries(category=None):
    for cat, items in REGISTRY.items():
        if category and cat != category:
            continue
        for item in items:
            yield cat, item


def do_check(category):
    print("=" * 70)
    print("STATO DOWNLOAD REPORT/ORIGINALI")
    print("=" * 70)
    ok = missing = 0
    for cat, item in iter_entries(category):
        path = _p(item["dest"])
        if existing_ok(path):
            print(f"  [OK]      [{cat}] {item['dest']} ({format_size(os.path.getsize(path))})")
            ok += 1
        else:
            print(f"  [MANCANTE] [{cat}] {item['dest']}")
            print(f"             URL: {item['url']}")
            missing += 1
    print(f"\nPresenti: {ok} | Mancanti: {missing}")
    print("=" * 70)


def main():
    parser = argparse.ArgumentParser(description="Download report/dataset originali per categoria")
    parser.add_argument("--category", help="Scarica solo una categoria (es: aifa, osmed)")
    parser.add_argument("--list", action="store_true", help="Elenca le categorie disponibili")
    parser.add_argument("--check", action="store_true", help="Mostra solo lo stato")
    parser.add_argument("--force", action="store_true", help="Riscarica tutti i file")
    parser.add_argument("--insecure", action="store_true", help="Disattiva la verifica TLS")
    args = parser.parse_args()

    if args.list:
        print("Categorie disponibili:")
        for cat, items in REGISTRY.items():
            print(f"  - {cat} ({len(items)} file)")
        return 0

    if args.category and args.category not in REGISTRY:
        print(f"Categoria sconosciuta: {args.category}. Usa --list per l'elenco.")
        return 2

    if args.check:
        do_check(args.category)
        return 0

    entries = []
    success = failed = skipped = 0
    all_items = list(iter_entries(args.category))

    print("=" * 70)
    print("DOWNLOAD REPORT/DATASET ORIGINALI")
    print("=" * 70)
    print(f"File totali: {len(all_items)}\n")

    for i, (cat, item) in enumerate(all_items, 1):
        path = _p(item["dest"])
        if not args.force and existing_ok(path):
            size = os.path.getsize(path)
            print(f"[{i}/{len(all_items)}] SKIP (presente): {item['dest']} ({format_size(size)})")
            entries.append({"category": cat, "dest": item["dest"], "url": item["url"],
                            "title": item.get("title"), "year": item.get("year"),
                            "size_bytes": size, "sha256": sha256_of_file(path), "status": "ok"})
            success += 1
            skipped += 1
            continue

        print(f"[{i}/{len(all_items)}] [{cat}] {item.get('title')}")
        print(f"    URL: {item['url']}")
        res = download_file(item["url"], path,
                            expect_pdf=item.get("expect_pdf", False), insecure=args.insecure)
        entries.append({"category": cat, "dest": item["dest"], "url": item["url"],
                        "title": item.get("title"), "year": item.get("year"),
                        "size_bytes": res["size_bytes"], "sha256": res["sha256"], "status": res["status"]})
        if res["status"] == "ok":
            print(f"    OK: {format_size(res['size_bytes'])}")
            success += 1
        else:
            print(f"    FALLITO: {res.get('error')}")
            failed += 1
        if i < len(all_items):
            time.sleep(1)

    # Manifest cumulativo (unione con eventuali voci esistenti di altre categorie)
    manifest = {"description": "Report e dataset originali (fonti ufficiali)",
                "download_date": time.strftime("%Y-%m-%d"),
                "files": entries}
    os.makedirs(os.path.dirname(MANIFEST_PATH), exist_ok=True)
    with open(MANIFEST_PATH, "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2, ensure_ascii=False)

    print(f"\n{'=' * 70}")
    print(f"RISULTATO: {success} disponibili ({success - skipped} nuovi, {skipped} già presenti), {failed} falliti")
    print(f"Manifest: {MANIFEST_PATH}")
    print("=" * 70)
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
