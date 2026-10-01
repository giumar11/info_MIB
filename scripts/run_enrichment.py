#!/usr/bin/env python3
"""
Orchestratore delle pipeline di enrichment per tutte le categorie di documenti
presenti nel repository.

Ogni categoria mappa una sequenza di comandi (script Python del repository) che
scaricano i documenti/dataset originali e/o rigenerano gli estratti elaborati.
È il punto di ingresso usato dalla pipeline schedulata (.github/workflows/
daily-enrichment.yml) e può essere eseguito anche manualmente.

Usage:
    python3 scripts/run_enrichment.py --list                 # elenca le categorie
    python3 scripts/run_enrichment.py --all                  # esegue tutte le categorie
    python3 scripts/run_enrichment.py --category gimbe        # una sola categoria
    python3 scripts/run_enrichment.py --all --dry-run         # mostra i comandi
    python3 scripts/run_enrichment.py --all --continue-on-error

Report:
    logs/enrichment_run_YYYY-MM-DD.json
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

# Registro delle pipeline: categoria -> metadati + sequenza di comandi.
# `steps` è una lista di liste di argomenti (passati a Python). L'ordine è
# significativo: prima il download degli originali, poi l'elaborazione.
PIPELINES = {
    "sources_monitor": {
        "description": "Controllo aggiornamenti di tutte le fonti del catalogo",
        "kind": "monitor",
        "steps": [["scheduler_check_updates.py"]],
    },
    "gimbe": {
        "description": "Rapporti GIMBE (PDF originali)",
        "kind": "download",
        "steps": [["download_gimbe_pdfs.py"]],
    },
    "pdta": {
        "description": "PDTA nazionali/regionali (PDF originali)",
        "kind": "download",
        "steps": [["download_pdta.py", "--level", "all"]],
    },
    "ania": {
        "description": "Report ANIA - assicurativo (PDF originali)",
        "kind": "download",
        "steps": [["download_ania_pdfs.py"]],
    },
    "scientific_reports": {
        "description": "ONS, società scientifiche, OASI Bocconi, AIFA (estratti)",
        "kind": "enrich",
        "steps": [["enrich_scientific_reports_ons.py"]],
    },
    "sdo_ministero": {
        "description": "SDO / Ministero della Salute (estratti e PDTA sintesi)",
        "kind": "enrich",
        "steps": [["extract_sdo_data.py"]],
    },
    "malattie_rare": {
        "description": "Orphadata - malattie rare (parsing XML originale)",
        "kind": "enrich",
        "steps": [["parse_orphadata.py"]],
    },
    "istat_hfa": {
        "description": "ISTAT Health for All - patologie croniche (estratti)",
        "kind": "enrich",
        "steps": [["analyze_hfa_chronic.py"]],
    },
    # La migrazione consolida gli estratti rigenerati: va eseguita per ultima.
    "migration": {
        "description": "Consolidamento dataset -> formati migration_ready",
        "kind": "consolidate",
        "steps": [["migrate_to_database.py"]],
    },
}

# Ordine di esecuzione con --all (download/monitor prima, consolidamento ultimo).
RUN_ORDER = [
    "sources_monitor",
    "gimbe",
    "pdta",
    "ania",
    "scientific_reports",
    "sdo_ministero",
    "malattie_rare",
    "istat_hfa",
    "migration",
]


def run_step(argv, dry_run=False):
    """Esegue un singolo step (script Python) e restituisce il risultato."""
    script = os.path.join(SCRIPTS_DIR, argv[0])
    cmd = [sys.executable, script] + list(argv[1:])
    printable = "python3 scripts/" + " ".join(argv)
    if dry_run:
        print(f"    [DRY RUN] {printable}")
        return {"cmd": printable, "returncode": None, "status": "dry_run"}

    print(f"    $ {printable}")
    start = time.time()
    try:
        proc = subprocess.run(cmd, cwd=BASE_DIR)
        rc = proc.returncode
    except Exception as e:  # pragma: no cover - difensivo
        print(f"    ERRORE nell'avvio: {e}")
        return {"cmd": printable, "returncode": None, "status": "error",
                "error": str(e)}
    elapsed = round(time.time() - start, 1)
    status = "ok" if rc == 0 else "failed"
    print(f"    -> {status} (rc={rc}, {elapsed}s)")
    return {"cmd": printable, "returncode": rc, "status": status,
            "elapsed_s": elapsed}


def run_category(name, dry_run=False):
    pipeline = PIPELINES[name]
    print(f"\n{'=' * 70}")
    print(f"  CATEGORIA: {name}  [{pipeline['kind']}]")
    print(f"  {pipeline['description']}")
    print(f"{'=' * 70}")
    results = [run_step(step, dry_run=dry_run) for step in pipeline["steps"]]
    ok = all(r["status"] in ("ok", "dry_run") for r in results)
    return {"category": name, "kind": pipeline["kind"],
            "description": pipeline["description"], "ok": ok, "steps": results}


def main():
    parser = argparse.ArgumentParser(
        description="Orchestratore pipeline di enrichment (tutte le categorie)")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--all", action="store_true",
                       help="Esegue tutte le categorie nell'ordine previsto")
    group.add_argument("--category", choices=sorted(PIPELINES.keys()),
                       help="Esegue una sola categoria")
    group.add_argument("--list", action="store_true",
                       help="Elenca le categorie disponibili")
    parser.add_argument("--dry-run", action="store_true",
                        help="Mostra i comandi senza eseguirli")
    parser.add_argument("--continue-on-error", action="store_true",
                        help="Prosegue anche se una categoria fallisce")
    args = parser.parse_args()

    if args.list:
        print("Categorie di enrichment disponibili:\n")
        for name in RUN_ORDER:
            p = PIPELINES[name]
            print(f"  {name:20s} [{p['kind']:11s}] {p['description']}")
        return 0

    categories = RUN_ORDER if args.all else [args.category]

    print("=" * 70)
    print("  PIPELINE DI ENRICHMENT - info_MIB")
    print(f"  Avvio: {datetime.now().isoformat(timespec='seconds')}")
    print(f"  Categorie: {', '.join(categories)}")
    print("=" * 70)

    results = []
    for name in categories:
        res = run_category(name, dry_run=args.dry_run)
        results.append(res)
        if not res["ok"] and not args.continue_on_error and not args.dry_run:
            print(f"\n[STOP] La categoria '{name}' è fallita "
                  f"(usa --continue-on-error per proseguire).")
            break

    ok_count = sum(1 for r in results if r["ok"])
    failed = [r["category"] for r in results if not r["ok"]]

    print(f"\n{'=' * 70}")
    print("  RIEPILOGO ENRICHMENT")
    print(f"  Categorie eseguite: {len(results)}  |  OK: {ok_count}  |  "
          f"Fallite: {len(failed)}")
    if failed:
        print(f"  Fallite: {', '.join(failed)}")
    print(f"{'=' * 70}")

    if not args.dry_run:
        os.makedirs(LOGS_DIR, exist_ok=True)
        report_path = os.path.join(
            LOGS_DIR, f"enrichment_run_{datetime.now():%Y-%m-%d}.json")
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump({
                "run_at": datetime.now().isoformat(timespec="seconds"),
                "categories_run": categories,
                "ok": ok_count,
                "failed": failed,
                "results": results,
            }, f, indent=2, ensure_ascii=False)
        print(f"Report: {report_path}")

    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
