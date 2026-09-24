#!/usr/bin/env python3
"""
Orchestratore delle pipeline di enrichment giornaliere.

Esegue, per ogni categoria di documenti presente nel repository, la relativa
pipeline di download/enrichment. L'obiettivo è mantenere aggiornati i
**dataset e i report ORIGINALI** (PDF, archivi, open data) e non soltanto gli
estratti in JSON/CSV elaborati internamente.

Ogni pipeline è idempotente: scarica solo i file mancanti (a meno di --force),
quindi l'esecuzione giornaliera aggiunge unicamente i nuovi documenti
pubblicati dalle fonti.

Categorie coperte (una pipeline per categoria):
  - gimbe                  -> scripts/download_gimbe_pdfs.py
  - pdta                   -> scripts/download_pdta.py
  - ania (assicurativo)    -> scripts/download_ania_reports.py
  - societa_scientifiche   -> scripts/download_societa_reports.py
  - ons (screening)        -> scripts/download_ons_reports.py

Uso:
    python3 scripts/run_daily_enrichment.py               # esegue tutte le pipeline
    python3 scripts/run_daily_enrichment.py --only ania   # solo una categoria (ripetibile)
    python3 scripts/run_daily_enrichment.py --skip pdta   # salta una categoria (ripetibile)
    python3 scripts/run_daily_enrichment.py --list        # elenca le pipeline registrate
    python3 scripts/run_daily_enrichment.py --force       # forza il ri-download dove supportato
    python3 scripts/run_daily_enrichment.py --dry-run     # mostra i comandi senza eseguirli

Output:
  - logs/enrichment_YYYY-MM-DD.log        (log dettagliato, gitignored)
  - datasets/enrichment_status.json       (stato sintetico ultima esecuzione, committato)
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS_DIR = os.path.join(BASE_DIR, "scripts")
LOGS_DIR = os.path.join(BASE_DIR, "logs")
STATUS_FILE = os.path.join(BASE_DIR, "datasets", "enrichment_status.json")

# Registro delle pipeline di enrichment: una per categoria di documenti.
# `supports_force` indica se lo script accetta il flag --force.
PIPELINES = [
    {
        "name": "gimbe",
        "description": "Rapporti GIMBE sul SSN + Osservatorio (PDF originali)",
        "script": "download_gimbe_pdfs.py",
        "args": [],
        "supports_force": True,
    },
    {
        "name": "pdta",
        "description": "Percorsi Diagnostico-Terapeutici Assistenziali nazionali e regionali (PDF originali)",
        "script": "download_pdta.py",
        "args": [],
        "supports_force": False,
    },
    {
        "name": "ania",
        "description": "Report del settore assicurativo ANIA (PDF originali)",
        "script": "download_ania_reports.py",
        "args": [],
        "supports_force": True,
    },
    {
        "name": "societa_scientifiche",
        "description": "Report originali delle società scientifiche italiane ed europee (PDF)",
        "script": "download_societa_reports.py",
        "args": [],
        "supports_force": True,
    },
    {
        "name": "ons",
        "description": "Rapporti annuali Osservatorio Nazionale Screening (PDF originali)",
        "script": "download_ons_reports.py",
        "args": [],
        "supports_force": True,
    },
]


def available_pipelines():
    """Ritorna solo le pipeline il cui script esiste su disco."""
    result = []
    for p in PIPELINES:
        script_path = os.path.join(SCRIPTS_DIR, p["script"])
        p = dict(p)
        p["script_path"] = script_path
        p["exists"] = os.path.exists(script_path)
        result.append(p)
    return result


def run_pipeline(pipeline, force=False, dry_run=False):
    """Esegue una singola pipeline come sottoprocesso."""
    cmd = [sys.executable, pipeline["script_path"]]
    if force and pipeline.get("supports_force"):
        cmd.append("--force")
    cmd += pipeline.get("args", [])

    entry = {
        "name": pipeline["name"],
        "description": pipeline["description"],
        "command": " ".join(cmd),
        "started_at": datetime.now(timezone.utc).isoformat(),
    }

    if not pipeline["exists"]:
        entry.update(status="missing_script", returncode=None, ended_at=entry["started_at"])
        print(f"[SKIP] {pipeline['name']}: script non trovato ({pipeline['script']})")
        return entry

    if dry_run:
        entry.update(status="dry_run", returncode=None, ended_at=entry["started_at"])
        print(f"[DRY RUN] {pipeline['name']}: {' '.join(cmd)}")
        return entry

    print("\n" + "=" * 70)
    print(f"PIPELINE: {pipeline['name']} — {pipeline['description']}")
    print("=" * 70)

    try:
        proc = subprocess.run(cmd, cwd=BASE_DIR, capture_output=True, text=True)
        # Rilancia l'output della pipeline per il log complessivo
        if proc.stdout:
            print(proc.stdout)
        if proc.stderr:
            print(proc.stderr, file=sys.stderr)
        entry.update(
            status="ok" if proc.returncode == 0 else "error",
            returncode=proc.returncode,
            stdout_tail="\n".join(proc.stdout.splitlines()[-15:]) if proc.stdout else "",
            stderr_tail="\n".join(proc.stderr.splitlines()[-15:]) if proc.stderr else "",
        )
    except Exception as e:  # noqa: BLE001 - vogliamo che una pipeline non blocchi le altre
        entry.update(status="exception", returncode=None, error=str(e)[:500])
        print(f"[ERRORE] {pipeline['name']}: {e}", file=sys.stderr)

    entry["ended_at"] = datetime.now(timezone.utc).isoformat()
    return entry


def main():
    parser = argparse.ArgumentParser(
        description="Orchestratore delle pipeline di enrichment giornaliere InfoMIB",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--only", action="append", dest="only",
                        help="Esegui solo le categorie indicate (ripetibile)")
    parser.add_argument("--skip", action="append", dest="skip",
                        help="Salta le categorie indicate (ripetibile)")
    parser.add_argument("--force", action="store_true",
                        help="Forza il ri-download dove supportato")
    parser.add_argument("--dry-run", action="store_true",
                        help="Mostra i comandi senza eseguirli")
    parser.add_argument("--list", action="store_true",
                        help="Elenca le pipeline registrate ed esci")
    args = parser.parse_args()

    pipelines = available_pipelines()

    if args.list:
        print("Pipeline di enrichment registrate:\n")
        for p in pipelines:
            flag = "ok " if p["exists"] else "MISSING"
            print(f"  [{flag}] {p['name']:<22} {p['description']}")
        return 0

    if args.only:
        wanted = set(args.only)
        pipelines = [p for p in pipelines if p["name"] in wanted]
    if args.skip:
        unwanted = set(args.skip)
        pipelines = [p for p in pipelines if p["name"] not in unwanted]

    if not pipelines:
        print("Nessuna pipeline selezionata.")
        return 1

    os.makedirs(LOGS_DIR, exist_ok=True)
    os.makedirs(os.path.dirname(STATUS_FILE), exist_ok=True)

    print("=" * 70)
    print(f"ENRICHMENT GIORNALIERO — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Pipeline da eseguire: {', '.join(p['name'] for p in pipelines)}")
    print("=" * 70)

    results = [run_pipeline(p, force=args.force, dry_run=args.dry_run) for p in pipelines]

    summary = {
        "run_date": datetime.now().strftime("%Y-%m-%d"),
        "run_timestamp": datetime.now(timezone.utc).isoformat(),
        "dry_run": args.dry_run,
        "forced": args.force,
        "totals": {
            "pipelines": len(results),
            "ok": sum(1 for r in results if r["status"] == "ok"),
            "error": sum(1 for r in results if r["status"] in ("error", "exception")),
            "missing": sum(1 for r in results if r["status"] == "missing_script"),
        },
        "pipelines": results,
    }

    if not args.dry_run:
        with open(STATUS_FILE, "w", encoding="utf-8") as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)

    print("\n" + "=" * 70)
    print("RIEPILOGO ENRICHMENT")
    print("=" * 70)
    for r in results:
        print(f"  [{r['status'].upper():<14}] {r['name']}")
    t = summary["totals"]
    print(f"\n  Totale: {t['pipelines']} | OK: {t['ok']} | Errori: {t['error']} | Script mancanti: {t['missing']}")
    if not args.dry_run:
        print(f"  Stato salvato in: {os.path.relpath(STATUS_FILE, BASE_DIR)}")
    print("=" * 70)

    # returncode diverso da 0 solo se una pipeline è andata in errore effettivo
    return 0 if t["error"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
