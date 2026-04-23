#!/usr/bin/env python3
"""
Download dei report ufficiali ANIA (Associazione Nazionale fra le Imprese
Assicuratrici) relativi al mercato assicurativo italiano con focus su Vita,
Danni, Salute/Welfare integrativo, Previdenza complementare, Responsabilità
civile e mobilità.

I PDF sono scaricati in `datasets/raw/ania/` mantenendo sempre gli originali
(Rapporti annuali "L'Assicurazione Italiana", Trends, Welfare Index PMI,
Quaderni ANIA, Focus Salute). Il manifest `ania_manifest.json` raccoglie
metadati e checksum per ogni file scaricato.

Uso:
    python3 scripts/download_ania.py                 # download incrementale
    python3 scripts/download_ania.py --force         # ri-scarica tutto
    python3 scripts/download_ania.py --dry-run       # elenca senza scaricare
    python3 scripts/download_ania.py --year 2024     # filtra per anno

Variabili d'ambiente:
    INFO_MIB_INSECURE_SSL=1   disabilita verifica certificati (sconsigliato)
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import ssl
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
ANIA_DIR = BASE_DIR / "datasets" / "raw" / "ania"
MANIFEST_PATH = ANIA_DIR / "ania_manifest.json"

USER_AGENT = (
    "Mozilla/5.0 (compatible; InfoMIB-AniaDownloader/1.0; "
    "+https://github.com/giumar11/info_MIB)"
)

# ============================================================================
# Catalogo report ANIA pubblici
# ============================================================================
# Le URL puntano alla sezione "pubblicazioni" del sito ANIA e a risorse
# correlate. Se un URL diretto non è più disponibile (ANIA riorganizza spesso
# i path), il fallback_url viene tentato dopo l'errore 404.
# ============================================================================

ANIA_REPORTS = [
    # ---------------- Rapporto annuale "L'Assicurazione Italiana" ----------
    {
        "id": "ANIA_ASSIT_2024",
        "filename": "Assicurazione_Italiana_2023_2024.pdf",
        "url": "https://www.ania.it/documents/35135/0/L+Assicurazione+Italiana+2023-2024.pdf",
        "fallback_url": "https://www.ania.it/pubblicazioni",
        "category": "rapporto_annuale",
        "title": "L'Assicurazione Italiana 2023-2024",
        "year": 2024,
        "area": "mercato_totale",
    },
    {
        "id": "ANIA_ASSIT_2023",
        "filename": "Assicurazione_Italiana_2022_2023.pdf",
        "url": "https://www.ania.it/documents/35135/0/L+Assicurazione+Italiana+2022-2023.pdf",
        "fallback_url": "https://www.ania.it/pubblicazioni",
        "category": "rapporto_annuale",
        "title": "L'Assicurazione Italiana 2022-2023",
        "year": 2023,
        "area": "mercato_totale",
    },
    {
        "id": "ANIA_ASSIT_2022",
        "filename": "Assicurazione_Italiana_2021_2022.pdf",
        "url": "https://www.ania.it/documents/35135/0/L+Assicurazione+Italiana+2021-2022.pdf",
        "fallback_url": "https://www.ania.it/pubblicazioni",
        "category": "rapporto_annuale",
        "title": "L'Assicurazione Italiana 2021-2022",
        "year": 2022,
        "area": "mercato_totale",
    },
    {
        "id": "ANIA_ASSIT_2021",
        "filename": "Assicurazione_Italiana_2020_2021.pdf",
        "url": "https://www.ania.it/documents/35135/0/L+Assicurazione+Italiana+2020-2021.pdf",
        "fallback_url": "https://www.ania.it/pubblicazioni",
        "category": "rapporto_annuale",
        "title": "L'Assicurazione Italiana 2020-2021",
        "year": 2021,
        "area": "mercato_totale",
    },
    # ---------------- Trends - Nuova produzione Vita ----------------------
    {
        "id": "ANIA_TRENDS_VITA_2024",
        "filename": "Trends_Nuova_Produzione_Vita_2024.pdf",
        "url": "https://www.ania.it/documents/35135/0/Trends-Nuova-Produzione-Vita-2024.pdf",
        "fallback_url": "https://www.ania.it/vita",
        "category": "trends",
        "title": "Trends - Nuova Produzione Vita 2024",
        "year": 2024,
        "area": "vita",
    },
    {
        "id": "ANIA_TRENDS_VITA_2023",
        "filename": "Trends_Nuova_Produzione_Vita_2023.pdf",
        "url": "https://www.ania.it/documents/35135/0/Trends-Nuova-Produzione-Vita-2023.pdf",
        "fallback_url": "https://www.ania.it/vita",
        "category": "trends",
        "title": "Trends - Nuova Produzione Vita 2023",
        "year": 2023,
        "area": "vita",
    },
    # ---------------- Premi Danni ------------------------------------------
    {
        "id": "ANIA_PREMI_DANNI_2024",
        "filename": "Premi_Danni_2024.pdf",
        "url": "https://www.ania.it/documents/35135/0/Premi-Rami-Danni-2024.pdf",
        "fallback_url": "https://www.ania.it/danni",
        "category": "trends",
        "title": "Premi Rami Danni 2024",
        "year": 2024,
        "area": "danni",
    },
    # ---------------- ANIA Trends Salute -----------------------------------
    {
        "id": "ANIA_SALUTE_2024",
        "filename": "ANIA_Trends_Salute_2024.pdf",
        "url": "https://www.ania.it/documents/35135/0/ANIA-Trends-Salute-2024.pdf",
        "fallback_url": "https://www.ania.it/salute",
        "category": "focus_salute",
        "title": "ANIA Trends Salute 2024 (welfare integrativo)",
        "year": 2024,
        "area": "salute",
    },
    {
        "id": "ANIA_SALUTE_2023",
        "filename": "ANIA_Trends_Salute_2023.pdf",
        "url": "https://www.ania.it/documents/35135/0/ANIA-Trends-Salute-2023.pdf",
        "fallback_url": "https://www.ania.it/salute",
        "category": "focus_salute",
        "title": "ANIA Trends Salute 2023 (welfare integrativo)",
        "year": 2023,
        "area": "salute",
    },
    {
        "id": "ANIA_WELFARE_INDEX_2024",
        "filename": "Welfare_Index_PMI_2024.pdf",
        "url": "https://www.welfareindexpmi.it/wp-content/uploads/2024/10/Rapporto-Welfare-Index-PMI-2024.pdf",
        "fallback_url": "https://www.welfareindexpmi.it/rapporti/",
        "category": "welfare",
        "title": "Welfare Index PMI 2024 (Generali + ANIA)",
        "year": 2024,
        "area": "welfare",
    },
    {
        "id": "ANIA_WELFARE_INDEX_2023",
        "filename": "Welfare_Index_PMI_2023.pdf",
        "url": "https://www.welfareindexpmi.it/wp-content/uploads/2023/10/Rapporto-Welfare-Index-PMI-2023.pdf",
        "fallback_url": "https://www.welfareindexpmi.it/rapporti/",
        "category": "welfare",
        "title": "Welfare Index PMI 2023 (Generali + ANIA)",
        "year": 2023,
        "area": "welfare",
    },
    # ---------------- Quaderni ANIA ----------------------------------------
    {
        "id": "ANIA_QUAD_LTC_2024",
        "filename": "Quaderno_ANIA_Long_Term_Care_2024.pdf",
        "url": "https://www.ania.it/documents/35135/0/Quaderno-ANIA-LTC-2024.pdf",
        "fallback_url": "https://www.ania.it/quaderni-ania",
        "category": "quaderno",
        "title": "Quaderno ANIA - Long Term Care 2024",
        "year": 2024,
        "area": "ltc",
    },
    {
        "id": "ANIA_QUAD_PREV_2024",
        "filename": "Quaderno_ANIA_Previdenza_Complementare_2024.pdf",
        "url": "https://www.ania.it/documents/35135/0/Quaderno-ANIA-Previdenza-2024.pdf",
        "fallback_url": "https://www.ania.it/quaderni-ania",
        "category": "quaderno",
        "title": "Quaderno ANIA - Previdenza complementare 2024",
        "year": 2024,
        "area": "previdenza",
    },
    # ---------------- RC Auto ----------------------------------------------
    {
        "id": "ANIA_RCAUTO_2024",
        "filename": "ANIA_RC_Auto_Statistiche_2024.pdf",
        "url": "https://www.ania.it/documents/35135/0/ANIA-RC-Auto-2024.pdf",
        "fallback_url": "https://www.ania.it/rc-auto",
        "category": "auto",
        "title": "ANIA - RC Auto statistiche 2024",
        "year": 2024,
        "area": "rc_auto",
    },
    # ---------------- Solvency II Italia -----------------------------------
    {
        "id": "ANIA_SOLVENCY_2024",
        "filename": "ANIA_Solvency_Italia_2024.pdf",
        "url": "https://www.ania.it/documents/35135/0/ANIA-Solvency-Italia-2024.pdf",
        "fallback_url": "https://www.ania.it/documents",
        "category": "vigilanza",
        "title": "ANIA - Solvency II Italia 2024",
        "year": 2024,
        "area": "solvency",
    },
    # ---------------- Statistical Data Bulletin ----------------------------
    {
        "id": "ANIA_SDB_2024",
        "filename": "ANIA_Italian_Insurance_Data_Bulletin_2024.pdf",
        "url": "https://www.ania.it/documents/35135/0/Italian-Insurance-Data-Bulletin-2024.pdf",
        "fallback_url": "https://www.ania.it/italian-insurance-data-bulletin",
        "category": "statistico",
        "title": "Italian Insurance Data Bulletin 2024 (EN)",
        "year": 2024,
        "area": "mercato_totale",
    },
]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def build_ssl_context() -> ssl.SSLContext:
    if os.environ.get("INFO_MIB_INSECURE_SSL") == "1":
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        return ctx
    return ssl.create_default_context()


def download(url: str, dest: Path, ctx: ssl.SSLContext, max_retries: int = 3) -> bool:
    req = urllib.request.Request(url, headers={
        "User-Agent": USER_AGENT,
        "Accept": "application/pdf,*/*",
    })
    for attempt in range(max_retries):
        try:
            with urllib.request.urlopen(req, context=ctx, timeout=120) as resp:
                data = resp.read()
                if len(data) < 1024:
                    return False
                dest.parent.mkdir(parents=True, exist_ok=True)
                with open(dest, "wb") as f:
                    f.write(data)
                return True
        except urllib.error.HTTPError as e:
            if e.code in (403, 404):
                return False
        except (urllib.error.URLError, OSError):
            pass
        if attempt < max_retries - 1:
            time.sleep(2 ** (attempt + 1))
    return False


def run(force: bool = False, dry_run: bool = False, year_filter: int | None = None) -> int:
    ANIA_DIR.mkdir(parents=True, exist_ok=True)

    manifest: dict = {}
    if MANIFEST_PATH.exists():
        try:
            manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            manifest = {}
    files_meta = manifest.get("files", {})

    ctx = build_ssl_context()
    ok = skipped = failed = 0

    for item in ANIA_REPORTS:
        if year_filter and item["year"] != year_filter:
            continue

        dest = ANIA_DIR / item["filename"]
        label = f"[{item['id']}] {item['title']}"

        if dest.exists() and not force:
            print(f"  [SKIP] {label}")
            skipped += 1
            continue

        if dry_run:
            print(f"  [DRY] {label} -> {dest.relative_to(BASE_DIR)}")
            continue

        print(f"  [GET] {label}")
        success = download(item["url"], dest, ctx)
        if not success and item.get("fallback_url"):
            print(f"        fallback -> {item['fallback_url']}")
            success = download(item["fallback_url"], dest, ctx)

        if success:
            files_meta[item["id"]] = {
                "filename": item["filename"],
                "title": item["title"],
                "year": item["year"],
                "area": item["area"],
                "category": item["category"],
                "url": item["url"],
                "size_bytes": dest.stat().st_size,
                "sha256": sha256_file(dest),
                "downloaded_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
            }
            ok += 1
            print(f"        OK ({dest.stat().st_size / 1024:.0f} KB)")
        else:
            failed += 1
            print(f"        FAILED")

    if not dry_run:
        manifest = {
            "source": "ANIA - Associazione Nazionale fra le Imprese Assicuratrici",
            "homepage": "https://www.ania.it/pubblicazioni",
            "generated_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
            "total_reports_catalogued": len(ANIA_REPORTS),
            "files": files_meta,
        }
        MANIFEST_PATH.write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    print(f"\nANIA download: ok={ok} skipped={skipped} failed={failed}")
    return 0 if failed == 0 else 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Download report ANIA (assicurativo)")
    parser.add_argument("--force", action="store_true", help="Ri-scarica anche i file già presenti")
    parser.add_argument("--dry-run", action="store_true", help="Mostra senza scaricare")
    parser.add_argument("--year", type=int, default=None, help="Filtra per anno")
    args = parser.parse_args()
    return run(force=args.force, dry_run=args.dry_run, year_filter=args.year)


if __name__ == "__main__":
    sys.exit(main())
