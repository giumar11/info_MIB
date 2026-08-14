#!/usr/bin/env python3
"""
Download dei report ANIA (Associazione Nazionale fra le Imprese Assicuratrici).

Scarica i report ORIGINALI pubblicati da ANIA rilevanti per l'analisi del
sistema sanitario e della spesa sanitaria privata / assicurativa in Italia:

- "L'Assicurazione Italiana" (rapporto annuale, serie storica) - contiene la
  sezione "Malattia" (ramo salute) e i dati sulla spesa sanitaria intermediata
  da assicurazioni e fondi.
- Appendice Statistica al rapporto annuale.
- Report tematici su sanità integrativa, welfare e fondi sanitari.

I file vengono salvati in datasets/raw/ania/pdf/ insieme a un manifest.json.

Usage:
    python3 scripts/download_ania_reports.py           # Scarica i PDF mancanti
    python3 scripts/download_ania_reports.py --check    # Mostra solo lo stato
    python3 scripts/download_ania_reports.py --force     # Riscarica tutto

Nota: ANIA pubblica i PDF su due pattern di URL:
  1) https://www.ania.it/wp-content/uploads/<anno>/<mese>/<file>.pdf   (recente)
  2) https://www.ania.it/documents/35135/<id>/<file>.pdf/<uuid>?...     (Liferay)
Gli URL contrassegnati con "verified": True sono stati confermati; gli altri
seguono il pattern noto e vengono comunque tentati (i fallimenti sono loggati
nel manifest con status "failed", come per la pipeline GIMBE).
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

# Elenco dei report ANIA. "verified" indica URL confermato al momento della
# stesura; gli altri seguono il pattern editoriale ANIA e vengono comunque
# tentati dalla pipeline giornaliera.
ANIA_REPORTS = [
    # --- Rapporto annuale "L'Assicurazione Italiana" (serie storica) ---
    {
        "filename": "LAssicurazione_Italiana_2025-2026.pdf",
        "url": "https://www.ania.it/wp-content/uploads/2026/07/LAssicurazione-Italiana-2025-2026.pdf",
        "category": "rapporto_annuale",
        "edition": "2025-2026",
        "year": 2026,
        "verified": True,
    },
    {
        "filename": "LAssicurazione_Italiana_2024-2025.pdf",
        "url": "https://www.ania.it/wp-content/uploads/2025/07/LAssicurazione-Italiana-2024-2025.pdf",
        "category": "rapporto_annuale",
        "edition": "2024-2025",
        "year": 2025,
        "verified": False,
    },
    {
        "filename": "LAssicurazione_Italiana_2023-2024.pdf",
        "url": "https://www.sipotra.it/wp-content/uploads/2024/07/LASSICURAZIONE-ITALIANA-2023-2024.pdf",
        "category": "rapporto_annuale",
        "edition": "2023-2024",
        "year": 2024,
        "verified": True,
    },
    {
        "filename": "LAssicurazione_Italiana_2022-2023.pdf",
        "url": "https://www.ania.it/wp-content/uploads/2023/07/LAssicurazione-Italiana-2022-2023.pdf",
        "category": "rapporto_annuale",
        "edition": "2022-2023",
        "year": 2023,
        "verified": False,
    },
    {
        "filename": "LAssicurazione_Italiana_2021-2022.pdf",
        "url": "https://www.ania.it/wp-content/uploads/2022/07/LAssicurazione-Italiana-2021-2022.pdf",
        "category": "rapporto_annuale",
        "edition": "2021-2022",
        "year": 2022,
        "verified": False,
    },
    {
        "filename": "LAssicurazione_Italiana_2020-2021.pdf",
        "url": "https://www.ania.it/wp-content/uploads/2026/03/LAssicurazione-Italiana-2020-2021.pdf",
        "category": "rapporto_annuale",
        "edition": "2020-2021",
        "year": 2021,
        "verified": True,
    },
    {
        "filename": "LAssicurazione_Italiana_2012-2013.pdf",
        "url": "https://ania.it/documents/35135/0/Assicurazione-Italiana-2012-2013.pdf/1a921ad3-efd4-6073-50f3-7c05a5770b0b?t=1576519512151",
        "category": "rapporto_annuale",
        "edition": "2012-2013",
        "year": 2013,
        "verified": True,
    },
]


def download_pdf(url, filepath, max_retries=3):
    """Scarica un PDF con retry e backoff esponenziale."""
    ctx = ssl.create_default_context()
    # Diversi portali istituzionali/assicurativi usano catene TLS non standard.
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

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
                    print(f"    WARNING: file troppo piccolo ({len(data)} byte)")
                    return None, None

                # Verifica minima che sia un PDF
                if not data[:5].startswith(b"%PDF"):
                    print("    WARNING: il contenuto non sembra un PDF valido")

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
    print("STATO DOWNLOAD REPORT ANIA")
    print("=" * 70)
    print(f"\nDirectory: {PDF_DIR}\n")

    ok = missing = total_size = 0
    for r in ANIA_REPORTS:
        filepath = os.path.join(PDF_DIR, r["filename"])
        if os.path.exists(filepath) and os.path.getsize(filepath) > 1000:
            size = os.path.getsize(filepath)
            total_size += size
            print(f"  [OK]      {r['filename']} ({format_size(size)})")
            ok += 1
        else:
            flag = "" if r.get("verified") else " (url da pattern, non verificato)"
            print(f"  [MISSING] {r['filename']}{flag}")
            missing += 1

    print(f"\n{'=' * 70}")
    print(f"Scaricati: {ok}/{len(ANIA_REPORTS)} ({format_size(total_size)})")
    print(f"Mancanti:  {missing}/{len(ANIA_REPORTS)}")
    print(f"{'=' * 70}")


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
    print("DOWNLOAD REPORT ANIA - ASSICURAZIONE E SPESA SANITARIA PRIVATA")
    print("=" * 70)
    print(f"\nTarget: {PDF_DIR}")
    print(f"Report totali: {len(ANIA_REPORTS)}\n")

    manifest = []
    success = failed = skipped = 0

    for i, r in enumerate(ANIA_REPORTS, 1):
        filepath = os.path.join(PDF_DIR, r["filename"])

        if not args.force and os.path.exists(filepath) and os.path.getsize(filepath) > 1000:
            size = os.path.getsize(filepath)
            with open(filepath, "rb") as fh:
                sha = hashlib.sha256(fh.read()).hexdigest()
            print(f"[{i}/{len(ANIA_REPORTS)}] SKIP (esiste): {r['filename']} ({format_size(size)})")
            manifest.append({**{k: r[k] for k in ("filename", "category", "edition", "year", "url")},
                             "size_bytes": size, "size_human": format_size(size),
                             "sha256": sha, "status": "ok"})
            success += 1
            skipped += 1
            continue

        print(f"[{i}/{len(ANIA_REPORTS)}] Download: {r['filename']}")
        print(f"    URL: {r['url']}")
        size, sha = download_pdf(r["url"], filepath)

        if size:
            print(f"    OK: {format_size(size)}")
            manifest.append({**{k: r[k] for k in ("filename", "category", "edition", "year", "url")},
                             "size_bytes": size, "size_human": format_size(size),
                             "sha256": sha, "status": "ok"})
            success += 1
        else:
            print("    FALLITO")
            manifest.append({**{k: r[k] for k in ("filename", "category", "edition", "year", "url")},
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

    downloaded = success - skipped
    print(f"\n{'=' * 70}")
    print(f"RISULTATO: {success}/{len(ANIA_REPORTS)} disponibili ({downloaded} nuovi, {skipped} già presenti)")
    if failed:
        print(f"           {failed} download falliti (vedi manifest)")
    total_size = sum(f["size_bytes"] for f in manifest)
    print(f"Dimensione totale: {format_size(total_size)}")
    print(f"Manifest: {MANIFEST_PATH}")
    print(f"{'=' * 70}")

    # La pipeline non deve fallire se alcuni URL non verificati danno 404.
    return 0


if __name__ == "__main__":
    sys.exit(main())
