#!/usr/bin/env python3
"""
Download dei report ORIGINALI del settore assicurativo pubblicati da ANIA
(Associazione Nazionale fra le Imprese Assicuratrici).

Salva i PDF in datasets/raw/ania/ organizzati per categoria e genera un
manifest con esito, dimensione e hash SHA-256 di ogni file.

Categorie:
  - rapporto_annuale : "L'Assicurazione Italiana" (report annuale di punta,
                       contiene capitoli su salute, sanità integrativa e welfare)
  - salute_welfare   : documenti/comunicati su salute, sanità integrativa, LTC
  - statistiche      : appendici statistiche e comunicati con dati di mercato

NOTA SULLE URL
--------------
Gli URL sono stati raccolti dall'indice pubblico dei documenti ANIA. ANIA ha
migrato il sito su WordPress: i PDF canonici correnti del report di punta si
trovano sotto https://www.ania.it/wp-content/uploads/... mentre le edizioni più
vecchie usano il vecchio CMS (https://www.ania.it/documents/35135/...), che la
migrazione potrebbe aver reso obsoleto. Lo script è idempotente e tollerante
agli errori: i download che falliscono (404/403/redirect) vengono registrati
come "failed" nel manifest senza interrompere gli altri. La verifica effettiva
degli URL avviene in fase di esecuzione (es. nel runner GitHub Actions con
accesso di rete completo).

LICENZA / RIUSO
---------------
I documenti ANIA sono soggetti al copyright di ANIA ("tutti i diritti
riservati", salvo diversa indicazione sul sito). Sono liberamente scaricabili e
citabili a fini di analisi; l'eventuale ridistribuzione dei PDF va verificata
con le note legali di ANIA (https://www.ania.it).

Uso:
    python3 scripts/download_ania_reports.py           # scarica i mancanti
    python3 scripts/download_ania_reports.py --check    # solo stato
    python3 scripts/download_ania_reports.py --force     # riscarica tutto
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
MANIFEST_PATH = os.path.join(ANIA_DIR, "manifest.json")

# Report ANIA. `verify` = livello di confidenza dell'URL raccolto dall'indice
# pubblico: "high" per i PDF canonici WordPress correnti, "legacy" per i vecchi
# path del CMS Liferay da verificare/sostituire.
ANIA_REPORTS = [
    # --- L'Assicurazione Italiana (rapporto annuale di punta) ---
    {
        "filename": "L_Assicurazione_Italiana_2024-2025.pdf",
        "url": "https://www.ania.it/wp-content/uploads/2026/03/LAssicurazione-Italiana-2024-2025.pdf",
        "category": "rapporto_annuale",
        "title": "L'Assicurazione Italiana 2024-2025",
        "year": 2025,
        "confidence": "high",
    },
    {
        "filename": "L_Assicurazione_Italiana_2023-2024.pdf",
        "url": "https://www.ania.it/wp-content/uploads/2026/03/LAssicurazione-Italiana-2023-2024.pdf",
        "category": "rapporto_annuale",
        "title": "L'Assicurazione Italiana 2023-2024",
        "year": 2024,
        "confidence": "high",
    },
    {
        "filename": "L_Assicurazione_Italiana_2021-2022.pdf",
        "url": "https://www.ania.it/wp-content/uploads/2026/03/LAssicurazione-Italiana-2021-2022.pdf",
        "category": "rapporto_annuale",
        "title": "L'Assicurazione Italiana 2021-2022",
        "year": 2022,
        "confidence": "high",
    },
    {
        "filename": "Italian_Insurance_2022-2023_EN.pdf",
        "url": "https://www.ania.it/wp-content/uploads/2026/03/Italian-Insurance-2022-2023-WEB.pdf",
        "category": "rapporto_annuale",
        "title": "Italian Insurance 2022-2023 (English edition)",
        "year": 2023,
        "confidence": "high",
    },
    {
        "filename": "L_Assicurazione_Italiana_2020-2021.pdf",
        "url": "https://www.ania.it/documents/35135/126701/LAssicurazione-Italiana-2020-2021.pdf",
        "category": "rapporto_annuale",
        "title": "L'Assicurazione Italiana 2020-2021",
        "year": 2021,
        "confidence": "legacy",
    },
    {
        "filename": "L_Assicurazione_Italiana_2019-2020.pdf",
        "url": "https://www.ania.it/documents/35135/126701/LAssicurazione-Italiana-2019-2020.pdf",
        "category": "rapporto_annuale",
        "title": "L'Assicurazione Italiana 2019-2020",
        "year": 2020,
        "confidence": "legacy",
    },
    # --- Salute / sanità integrativa / welfare ---
    {
        "filename": "CS_ANIA_dati_raccolta_premi_2024.pdf",
        "url": "https://www.ania.it/documents/35135/910336/CS+ANIA+pubblica+i+dati+sulla+raccolta+premi+2024.pdf",
        "category": "statistiche",
        "title": "Comunicato stampa - Dati raccolta premi 2024",
        "year": 2025,
        "confidence": "legacy",
    },
]

# Pagine di categoria (periodici e hub) da usare come riferimento manuale:
# i singoli numeri sono PDF a rotazione, non un URL stabile.
ANIA_LANDING_PAGES = {
    "assicurazione_italiana": "https://www.ania.it/pubblicazioni/-/categories/53705",
    "appendice_statistica": "https://www.ania.it/pubblicazioni/-/categories/53729",
    "ania_trends": "https://www.ania.it/pubblicazioni/-/categories/52459",
    "ania_trends_nuova_produzione_vita": "https://www.ania.it/pubblicazioni/-/categories/52469",
    "ania_trends_bilanci": "https://www.ania.it/pubblicazioni/-/categories/52457",
    "ania_trends_sostenibilita": "https://www.ania.it/pubblicazioni/-/categories/339736",
    "salute_infopolizze": "https://www.ania.it/infopolizze-salute",
    "pubblicazioni_hub": "https://www.ania.it/pubblicazioni/",
}


def download_pdf(url, filepath, max_retries=3):
    """Scarica un PDF con retry ed exponential backoff. Verifica TLS attiva."""
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
    print("STATO DOWNLOAD REPORT ANIA")
    print("=" * 70)
    print(f"\nDirectory: {ANIA_DIR}\n")
    ok = missing = total_size = 0
    for r in ANIA_REPORTS:
        fp = os.path.join(ANIA_DIR, r["category"], r["filename"])
        if os.path.exists(fp) and os.path.getsize(fp) > 1000:
            size = os.path.getsize(fp)
            total_size += size
            ok += 1
            print(f"  [OK]      {r['category']}/{r['filename']} ({format_size(size)})")
        else:
            missing += 1
            print(f"  [MISSING] {r['category']}/{r['filename']}")
            print(f"            URL ({r['confidence']}): {r['url']}")
    print(f"\n{'=' * 70}")
    print(f"Scaricati: {ok}/{len(ANIA_REPORTS)} ({format_size(total_size)}) | Mancanti: {missing}")
    print("=" * 70)


def main():
    parser = argparse.ArgumentParser(description="Download report ANIA (settore assicurativo)")
    parser.add_argument("--check", action="store_true", help="Mostra solo lo stato")
    parser.add_argument("--force", action="store_true", help="Riscarica tutto")
    args = parser.parse_args()

    os.makedirs(ANIA_DIR, exist_ok=True)
    if args.check:
        check_status()
        return 0

    print("=" * 70)
    print("DOWNLOAD REPORT ANIA - SETTORE ASSICURATIVO")
    print("=" * 70)
    print(f"\nTarget: {ANIA_DIR}\nReport totali: {len(ANIA_REPORTS)}\n")

    manifest = []
    success = failed = skipped = 0

    for i, r in enumerate(ANIA_REPORTS, 1):
        dest_dir = os.path.join(ANIA_DIR, r["category"])
        os.makedirs(dest_dir, exist_ok=True)
        filepath = os.path.join(dest_dir, r["filename"])

        if not args.force and os.path.exists(filepath) and os.path.getsize(filepath) > 1000:
            size = os.path.getsize(filepath)
            sha = hashlib.sha256(open(filepath, "rb").read()).hexdigest()
            print(f"[{i}/{len(ANIA_REPORTS)}] SKIP (esiste): {r['filename']} ({format_size(size)})")
            manifest.append({**{k: r[k] for k in ("filename", "category", "title", "year", "url", "confidence")},
                             "size_bytes": size, "sha256": sha, "status": "ok"})
            success += 1
            skipped += 1
            continue

        print(f"[{i}/{len(ANIA_REPORTS)}] Download: {r['filename']}")
        print(f"    URL ({r['confidence']}): {r['url']}")
        size, sha = download_pdf(r["url"], filepath)
        if size:
            print(f"    OK: {format_size(size)}")
            manifest.append({**{k: r[k] for k in ("filename", "category", "title", "year", "url", "confidence")},
                             "size_bytes": size, "sha256": sha, "status": "ok"})
            success += 1
        else:
            print("    FALLITO")
            manifest.append({**{k: r[k] for k in ("filename", "category", "title", "year", "url", "confidence")},
                             "size_bytes": 0, "sha256": None, "status": "failed"})
            failed += 1
        if i < len(ANIA_REPORTS):
            time.sleep(1)

    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump({
            "description": "Manifest collezione report ANIA (settore assicurativo)",
            "download_date": time.strftime("%Y-%m-%d"),
            "note": "URL raccolti dall'indice pubblico ANIA; verificare in esecuzione (rete completa).",
            "landing_pages": ANIA_LANDING_PAGES,
            "total": len(ANIA_REPORTS),
            "downloaded": success,
            "failed": failed,
            "files": manifest,
        }, f, indent=2, ensure_ascii=False)

    print(f"\n{'=' * 70}")
    print(f"RISULTATO: {success}/{len(ANIA_REPORTS)} disponibili ({success - skipped} nuovi, {skipped} già presenti)")
    if failed:
        print(f"           {failed} download falliti (vedi manifest)")
    print(f"Manifest: {MANIFEST_PATH}")
    print("=" * 70)
    # Non consideriamo i download falliti un errore fatale: gli URL vengono
    # verificati/aggiornati nel tempo. L'orchestratore resta verde.
    return 0


if __name__ == "__main__":
    sys.exit(main())
