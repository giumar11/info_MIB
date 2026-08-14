#!/usr/bin/env python3
"""
Pipeline di enrichment giornaliera per il repository info_MIB.

Orchestratore unico che, per OGNI categoria di documenti presente nel
repository, esegue:

  1. RAW / ORIGINALI  -> scarica i dataset e i report ORIGINALI (PDF, XML, CSV)
                         dalle fonti ufficiali, quando disponibili. Non ci si
                         limita agli estratti processati da noi.
  2. ENRICH / PROCESS -> (ri)genera gli estratti processati (JSON/CSV) a partire
                         dagli originali.
  3. CHECK            -> verifica aggiornamenti delle fonti (scheduler_check_updates).

Ogni step è isolato: il fallimento di una categoria non blocca le altre.
Al termine viene scritto un manifest in logs/enrichment_YYYY-MM-DD.json.

Categorie coperte (allineate a datasets/raw/ e a sources_catalog.csv):
  gimbe, pdta, ania, orphadata, sdo, istat_hfa, scientific_reports,
  sources_check

Usage:
    python3 scripts/enrichment_pipeline.py                 # tutte le categorie
    python3 scripts/enrichment_pipeline.py --category ania # solo una categoria
    python3 scripts/enrichment_pipeline.py --list          # elenca le categorie
    python3 scripts/enrichment_pipeline.py --dry-run       # mostra senza eseguire
    python3 scripts/enrichment_pipeline.py --skip-download # solo processing/check
"""

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS_DIR = os.path.join(BASE_DIR, "scripts")
LOGS_DIR = os.path.join(BASE_DIR, "logs")
PY = sys.executable


def _script(name):
    return os.path.join(SCRIPTS_DIR, name)


# Registro delle categorie di documenti.
#   download: comandi che recuperano gli ORIGINALI (report/dataset)
#   process : comandi che rigenerano gli estratti processati
# I comandi sono liste-di-liste (ognuno è un argv per subprocess).
CATEGORIES = {
    "gimbe": {
        "title": "Fondazione GIMBE - Rapporti SSN e Osservatorio",
        "download": [[PY, _script("download_gimbe_pdfs.py")]],
        "process": [],
    },
    "pdta": {
        "title": "PDTA nazionali, regionali e società scientifiche",
        "download": [[PY, _script("download_pdta.py"), "--level", "all"]],
        "process": [],
    },
    "ania": {
        "title": "ANIA - Assicurazione e spesa sanitaria privata",
        "download": [[PY, _script("download_ania_reports.py")]],
        "process": [],
    },
    "orphadata": {
        "title": "Orphadata - Epidemiologia malattie rare",
        "download": [],  # XML originale già presente in datasets/raw/
        "process": [[PY, _script("parse_orphadata.py")]],
    },
    "sdo": {
        "title": "Ministero Salute - Schede Dimissione Ospedaliera",
        "download": [],  # CSV originali già presenti in datasets/raw/ministero_salute/
        "process": [[PY, _script("extract_sdo_data.py")]],
    },
    "istat_hfa": {
        "title": "ISTAT - Health for All / malattie croniche",
        "download": [],  # dataset HFA (DBF) da caricare in datasets/raw/hfa_istat/
        "process": [[PY, _script("analyze_hfa_chronic.py")]],
    },
    "scientific_reports": {
        "title": "ONS, società scientifiche IT/EU, OASI, AIFA",
        "download": [],
        "process": [[PY, _script("enrich_scientific_reports_ons.py")]],
    },
    "sources_check": {
        "title": "Controllo aggiornamenti di tutte le fonti del catalogo",
        "download": [],
        "process": [[PY, _script("scheduler_check_updates.py"), "--force"]],
    },
}


def run_command(cmd, dry_run):
    """Esegue un comando e ritorna un dict con l'esito (non solleva eccezioni)."""
    printable = " ".join(cmd)
    if dry_run:
        print(f"    [DRY RUN] {printable}")
        return {"cmd": printable, "status": "dry_run", "returncode": None}

    print(f"    $ {printable}")
    start = time.time()
    try:
        proc = subprocess.run(
            cmd, cwd=BASE_DIR, capture_output=True, text=True, timeout=3600
        )
        elapsed = round(time.time() - start, 1)
        status = "ok" if proc.returncode == 0 else "error"
        tail = (proc.stdout or "")[-400:] + (proc.stderr or "")[-400:]
        print(f"      -> {status} ({elapsed}s, rc={proc.returncode})")
        return {
            "cmd": printable,
            "status": status,
            "returncode": proc.returncode,
            "elapsed_s": elapsed,
            "output_tail": tail.strip(),
        }
    except subprocess.TimeoutExpired:
        print("      -> timeout")
        return {"cmd": printable, "status": "timeout", "returncode": None}
    except FileNotFoundError as e:
        print(f"      -> script mancante: {e}")
        return {"cmd": printable, "status": "missing_script", "error": str(e)}


def run_category(name, cfg, dry_run, skip_download):
    print(f"\n{'=' * 70}")
    print(f"  [{name}] {cfg['title']}")
    print(f"{'=' * 70}")

    steps = []
    if not skip_download:
        for cmd in cfg.get("download", []):
            steps.append(("download", run_command(cmd, dry_run)))
    for cmd in cfg.get("process", []):
        steps.append(("process", run_command(cmd, dry_run)))

    if not steps:
        print("    (nessuno step configurato)")

    return {
        "category": name,
        "title": cfg["title"],
        "steps": [{"phase": ph, **res} for ph, res in steps],
    }


def main():
    parser = argparse.ArgumentParser(
        description="Pipeline di enrichment giornaliera info_MIB"
    )
    parser.add_argument("--category", action="append", dest="categories",
                        help="Esegue solo la/e categoria/e indicate (ripetibile)")
    parser.add_argument("--list", action="store_true", help="Elenca le categorie")
    parser.add_argument("--dry-run", action="store_true",
                        help="Mostra i comandi senza eseguirli")
    parser.add_argument("--skip-download", action="store_true",
                        help="Salta il download degli originali, esegue solo process/check")
    args = parser.parse_args()

    if args.list:
        print("Categorie disponibili:")
        for name, cfg in CATEGORIES.items():
            print(f"  - {name:20s} {cfg['title']}")
        return 0

    selected = CATEGORIES
    if args.categories:
        unknown = [c for c in args.categories if c not in CATEGORIES]
        if unknown:
            print(f"ERRORE: categorie sconosciute: {unknown}")
            print(f"Disponibili: {list(CATEGORIES)}")
            return 2
        selected = {c: CATEGORIES[c] for c in args.categories}

    os.makedirs(LOGS_DIR, exist_ok=True)
    today = datetime.now().strftime("%Y-%m-%d")

    print("=" * 70)
    print("PIPELINE DI ENRICHMENT GIORNALIERA - info_MIB")
    print(f"Data: {today} | Categorie: {len(selected)}")
    if args.dry_run:
        print("*** DRY RUN - nessun comando verrà eseguito ***")
    print("=" * 70)

    results = []
    for name, cfg in selected.items():
        results.append(run_category(name, cfg, args.dry_run, args.skip_download))

    # Riepilogo
    all_steps = [s for r in results for s in r["steps"]]
    ok = sum(1 for s in all_steps if s["status"] in ("ok", "dry_run"))
    errors = sum(1 for s in all_steps if s["status"] in ("error", "timeout", "missing_script"))

    manifest = {
        "pipeline": "enrichment_daily",
        "date": today,
        "timestamp": datetime.now().isoformat(),
        "categories_run": list(selected),
        "summary": {"steps_total": len(all_steps), "ok": ok, "errors": errors},
        "results": results,
    }

    if not args.dry_run:
        report_path = os.path.join(LOGS_DIR, f"enrichment_{today}.json")
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, ensure_ascii=False, indent=2)
        print(f"\nManifest salvato: {report_path}")

    print(f"\n{'=' * 70}")
    print(f"COMPLETATO - step OK: {ok} | errori: {errors}")
    print(f"{'=' * 70}")

    # Non fallire l'intera pipeline per errori di singole categorie: gli errori
    # sono tracciati nel manifest. Ritorna 0 così la CI committa comunque i log.
    return 0


if __name__ == "__main__":
    sys.exit(main())
