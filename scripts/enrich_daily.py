#!/usr/bin/env python3
"""
Orchestratore delle pipeline di arricchimento giornaliere.

Esegue, per ogni categoria di documenti presente nella repository, lo step di
arricchimento corrispondente:

  * DOWNLOAD  -> scarica i dataset/report ORIGINALI (PDF, dataset grezzi) dalle
                 fonti ufficiali. Gli script scaricano solo i file mancanti,
                 quindi ogni giorno si aggiungono solo le nuove pubblicazioni.
  * PROCESS   -> rigenera i dataset processati/estratti a partire dai grezzi.
  * CHECK     -> interroga le fonti del catalogo per rilevare aggiornamenti
                 (per le categorie senza downloader diretto).

L'orchestratore e' pensato per essere eseguito ogni giorno (vedi
.github/workflows/daily-enrichment.yml) e produce un report in
logs/enrichment_YYYY-MM-DD.json.

Utilizzo:
    python3 scripts/enrich_daily.py                 # tutte le categorie
    python3 scripts/enrich_daily.py --list           # elenca gli step
    python3 scripts/enrich_daily.py --category ania   # solo una categoria
    python3 scripts/enrich_daily.py --dry-run         # mostra cosa farebbe
    python3 scripts/enrich_daily.py --skip-download    # solo processing + check
    python3 scripts/enrich_daily.py --skip-check       # niente controllo fonti
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
PY = sys.executable or "python3"

# Registro degli step di arricchimento.
# type: download | process | check
# category: chiave logica della categoria di documenti
# Ogni step e' una lista di argomenti passata a subprocess (relativa a SCRIPTS_DIR).
STEPS = [
    # --- DOWNLOAD DEI REPORT/DATASET ORIGINALI ---
    {
        "name": "GIMBE (rapporti SSN + Osservatorio)",
        "category": "gimbe",
        "type": "download",
        "script": "download_gimbe_pdfs.py",
        "args": [],
        "description": "Scarica i PDF originali dei rapporti GIMBE",
    },
    {
        "name": "PDTA (nazionali, regionali, locali)",
        "category": "pdta",
        "type": "download",
        "script": "download_pdta.py",
        "args": ["--level", "all"],
        "description": "Scarica i PDF originali dei Percorsi Diagnostico-Terapeutici",
    },
    {
        "name": "ANIA (assicurativo/salute)",
        "category": "ania",
        "type": "download",
        "script": "download_ania_reports.py",
        "args": [],
        "description": "Scarica i PDF originali dei report ANIA",
    },
    # --- ARRICCHIMENTO CATALOGHI (ONS, societa scientifiche, OASI, AIFA, GIMBE) ---
    {
        "name": "Report scientifici (ONS/AIOM/AIFA/OASI/GIMBE)",
        "category": "scientific_reports",
        "type": "process",
        "script": "enrich_scientific_reports_ons.py",
        "args": [],
        "description": "Rigenera i cataloghi strutturati dei report scientifici",
    },
    # --- RIGENERAZIONE DATASET PROCESSATI DA GREZZI ---
    {
        "name": "Malattie rare (Orphadata)",
        "category": "orphanet",
        "type": "process",
        "script": "parse_orphadata.py",
        "args": [],
        "description": "Rielabora l'XML Orphadata in CSV/JSON malattie rare",
    },
    {
        "name": "SDO - Dimissioni ospedaliere",
        "category": "sdo",
        "type": "process",
        "script": "extract_sdo_data.py",
        "args": [],
        "description": "Rigenera il riepilogo SDO e i PDTA multidisciplinari",
    },
    {
        "name": "ISTAT Health for All - croniche",
        "category": "istat",
        "type": "process",
        "script": "analyze_hfa_chronic.py",
        "args": [],
        "description": "Analizza gli indicatori ISTAT per le malattie croniche",
    },
    {
        "name": "Migrazione dati (SQL/NoSQL ready)",
        "category": "migration",
        "type": "process",
        "script": "migrate_to_database.py",
        "args": [],
        "description": "Rigenera i dataset pronti per l'import in database",
    },
    # --- CONTROLLO AGGIORNAMENTI FONTI (categorie senza downloader diretto) ---
    {
        "name": "Controllo aggiornamenti fonti (catalogo completo)",
        "category": "sources_check",
        "type": "check",
        "script": "scheduler_check_updates.py",
        "args": ["--force"],
        "description": "Rileva nuove pubblicazioni per tutte le fonti del catalogo",
    },
]


def run_step(step, dry_run=False):
    """Esegue un singolo step e ritorna un dizionario con l'esito."""
    script_path = os.path.join(SCRIPTS_DIR, step["script"])
    cmd = [PY, script_path] + step["args"]

    result = {
        "name": step["name"],
        "category": step["category"],
        "type": step["type"],
        "script": step["script"],
        "command": " ".join([os.path.basename(PY), step["script"]] + step["args"]),
        "started_at": datetime.now().isoformat(timespec="seconds"),
    }

    if dry_run:
        print(f"  [DRY RUN] {step['name']}")
        print(f"            -> {result['command']}")
        result["status"] = "dry_run"
        return result

    if not os.path.exists(script_path):
        print(f"  [SKIP] Script non trovato: {step['script']}")
        result["status"] = "missing_script"
        return result

    print(f"\n{'-' * 70}")
    print(f"  {step['name']}  [{step['type'].upper()}]")
    print(f"  {step['description']}")
    print(f"{'-' * 70}")

    start = time.time()
    try:
        proc = subprocess.run(
            cmd,
            cwd=BASE_DIR,
            capture_output=True,
            text=True,
            timeout=3600,
        )
        result["returncode"] = proc.returncode
        result["status"] = "ok" if proc.returncode == 0 else "error"
        # Conserva solo la coda dell'output per non gonfiare il report
        tail = (proc.stdout or "").strip().splitlines()[-15:]
        result["output_tail"] = tail
        if proc.returncode != 0:
            err_tail = (proc.stderr or "").strip().splitlines()[-15:]
            result["stderr_tail"] = err_tail
        # Stampa a video l'output completo dello step
        if proc.stdout:
            print(proc.stdout.rstrip())
        if proc.returncode != 0 and proc.stderr:
            print("STDERR:", proc.stderr.rstrip())
    except subprocess.TimeoutExpired:
        result["status"] = "timeout"
        print("  [TIMEOUT] step interrotto dopo 3600s")
    except Exception as e:  # noqa: BLE001 - vogliamo continuare con gli altri step
        result["status"] = "exception"
        result["error"] = str(e)
        print(f"  [EXCEPTION] {e}")

    result["duration_seconds"] = round(time.time() - start, 1)
    print(f"  -> esito: {result['status']} ({result.get('duration_seconds', 0)}s)")
    return result


def select_steps(args):
    """Filtra gli step in base agli argomenti CLI."""
    steps = STEPS
    if args.categories:
        wanted = set(args.categories)
        steps = [s for s in steps if s["category"] in wanted]
    if args.skip_download:
        steps = [s for s in steps if s["type"] != "download"]
    if args.skip_check:
        steps = [s for s in steps if s["type"] != "check"]
    return steps


def main():
    parser = argparse.ArgumentParser(
        description="Orchestratore delle pipeline di arricchimento giornaliere",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--category", action="append", dest="categories",
                        help="Esegue solo la categoria indicata (ripetibile)")
    parser.add_argument("--list", action="store_true",
                        help="Elenca gli step disponibili e termina")
    parser.add_argument("--dry-run", action="store_true",
                        help="Mostra cosa verrebbe eseguito senza eseguirlo")
    parser.add_argument("--skip-download", action="store_true",
                        help="Salta gli step di download (solo processing/check)")
    parser.add_argument("--skip-check", action="store_true",
                        help="Salta il controllo aggiornamenti delle fonti")
    args = parser.parse_args()

    if args.list:
        print("Step di arricchimento disponibili:\n")
        for s in STEPS:
            print(f"  [{s['type']:8}] {s['category']:18} {s['name']}")
        return 0

    steps = select_steps(args)

    print("=" * 70)
    print("PIPELINE DI ARRICCHIMENTO GIORNALIERA - info_MIB")
    print("=" * 70)
    print(f"Data: {datetime.now().isoformat(timespec='seconds')}")
    print(f"Step da eseguire: {len(steps)}")
    if not steps:
        print("Nessuno step selezionato.")
        return 0

    results = []
    for step in steps:
        results.append(run_step(step, dry_run=args.dry_run))

    # Report
    summary = {
        "run_date": datetime.now().strftime("%Y-%m-%d"),
        "run_timestamp": datetime.now().isoformat(timespec="seconds"),
        "steps_total": len(results),
        "steps_ok": sum(1 for r in results if r.get("status") == "ok"),
        "steps_error": sum(1 for r in results if r.get("status") in
                           ("error", "timeout", "exception")),
        "steps": results,
    }

    print(f"\n{'=' * 70}")
    print("RIEPILOGO ARRICCHIMENTO")
    print("=" * 70)
    for r in results:
        print(f"  [{r.get('status', '?'):8}] {r['name']}")
    print(f"\n  OK: {summary['steps_ok']}/{summary['steps_total']}  "
          f"Errori: {summary['steps_error']}")

    if not args.dry_run:
        os.makedirs(LOGS_DIR, exist_ok=True)
        report_path = os.path.join(LOGS_DIR, f"enrichment_{summary['run_date']}.json")
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        print(f"\n  Report salvato: {report_path}")

    # Uscita 0 anche con download falliti (volatilita di rete/URL): il report
    # traccia comunque gli esiti. Non fallisce la pipeline schedulata.
    return 0


if __name__ == "__main__":
    sys.exit(main())
