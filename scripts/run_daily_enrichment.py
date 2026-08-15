#!/usr/bin/env python3
"""
Orchestratore delle PIPELINE DI ENRICHMENT GIORNALIERE.

Esegue in sequenza, per TUTTE le categorie di documenti del repository:

  1. RE-BUILD degli estratti processati (nessuna rete):
       - enrich_scientific_reports_ons.py   (ONS, societa' scientifiche, OASI, AIFA, GIMBE)
       - extract_sdo_data.py                (SDO Ministero Salute)
       - parse_orphadata.py                 (Orphanet malattie rare)
       - analyze_hfa_chronic.py             (ISTAT Health For All)
       - migrate_to_database.py             (dataset migration_ready SQL/NoSQL)

  2. DOWNLOAD dei DOCUMENTI e DATASET ORIGINALI (richiede rete):
       - download_gimbe_pdfs.py             (rapporti GIMBE - PDF originali)
       - download_pdta.py                   (PDTA nazionali/regionali - PDF originali)
       - download_ania_reports.py           (report ANIA assicurativo - PDF originali)
       - download_original_reports.py       (AIFA/ONS/societa' - PDF originali via registro)

  3. MONITORAGGIO aggiornamenti fonti:
       - scheduler_check_updates.py --force  (rileva nuove pubblicazioni)

Il principio: dove il documento/dataset ORIGINALE esiste ed e' scaricabile, la
pipeline scarica l'originale (PDF, XML, CSV), non solo l'estratto processato.

I passi di download che falliscono per problemi di rete NON bloccano la
pipeline (sono "non critici"): vengono segnalati nel report. I passi di
re-build degli estratti sono critici.

Output:
  logs/enrichment_YYYY-MM-DD.log          (log dettagliato)
  logs/enrichment_report_YYYY-MM-DD.json  (report strutturato)

Usage:
    python3 scripts/run_daily_enrichment.py                 # pipeline completa
    python3 scripts/run_daily_enrichment.py --no-network    # solo re-build estratti
    python3 scripts/run_daily_enrichment.py --only download  # solo i download
    python3 scripts/run_daily_enrichment.py --only enrich     # solo gli estratti
    python3 scripts/run_daily_enrichment.py --dry-run         # elenca i passi
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
TODAY = datetime.now().strftime("%Y-%m-%d")
LOG_FILE = os.path.join(LOGS_DIR, f"enrichment_{TODAY}.log")
REPORT_FILE = os.path.join(LOGS_DIR, f"enrichment_report_{TODAY}.json")

PYTHON = sys.executable or "python3"

# Definizione dei passi della pipeline.
#   phase:    'enrich' (re-build estratti) | 'download' (originali) | 'monitor'
#   critical: se True, un fallimento fa uscire la pipeline con codice != 0
#   network:  se True, il passo richiede accesso a Internet
STEPS = [
    # --- FASE 1: re-build estratti processati (offline) ---
    {"name": "enrich_reports", "phase": "enrich", "critical": True, "network": False,
     "script": "enrich_scientific_reports_ons.py", "args": [],
     "desc": "Estratti ONS/societa'/OASI/AIFA/GIMBE"},
    {"name": "extract_sdo", "phase": "enrich", "critical": True, "network": False,
     "script": "extract_sdo_data.py", "args": [],
     "desc": "Estratti SDO Ministero Salute"},
    {"name": "parse_orphadata", "phase": "enrich", "critical": True, "network": False,
     "script": "parse_orphadata.py", "args": [],
     "desc": "Estratti Orphanet malattie rare"},
    {"name": "analyze_hfa", "phase": "enrich", "critical": False, "network": False,
     "script": "analyze_hfa_chronic.py", "args": [],
     "desc": "Analisi ISTAT Health For All"},
    {"name": "migrate_db", "phase": "enrich", "critical": False, "network": False,
     "script": "migrate_to_database.py", "args": [],
     "desc": "Dataset migration_ready SQL/NoSQL"},

    # --- FASE 2: download documenti/dataset originali (richiede rete) ---
    {"name": "download_gimbe", "phase": "download", "critical": False, "network": True,
     "script": "download_gimbe_pdfs.py", "args": [],
     "desc": "Rapporti GIMBE (PDF originali)"},
    {"name": "download_pdta", "phase": "download", "critical": False, "network": True,
     "script": "download_pdta.py", "args": [],
     "desc": "PDTA nazionali/regionali (PDF originali)"},
    {"name": "download_ania", "phase": "download", "critical": False, "network": True,
     "script": "download_ania_reports.py", "args": [],
     "desc": "Report ANIA assicurativo (PDF originali)"},
    {"name": "download_originals", "phase": "download", "critical": False, "network": True,
     "script": "download_original_reports.py", "args": [],
     "desc": "AIFA/ONS/societa' - originali via registro"},

    # --- FASE 3: monitoraggio aggiornamenti fonti ---
    {"name": "check_updates", "phase": "monitor", "critical": False, "network": True,
     "script": "scheduler_check_updates.py", "args": ["--force"],
     "desc": "Rilevamento nuove pubblicazioni fonti"},
]


def log(handle, msg):
    line = f"{datetime.now().strftime('%H:%M:%S')} | {msg}"
    print(line)
    handle.write(line + "\n")
    handle.flush()


def run_step(step, handle):
    """Esegue un passo come subprocess. Ritorna un dict risultato."""
    script_path = os.path.join(SCRIPTS_DIR, step["script"])
    cmd = [PYTHON, script_path] + step["args"]
    log(handle, f"[{step['name']}] START - {step['desc']}")
    log(handle, f"    cmd: {' '.join(cmd)}")

    start = time.time()
    try:
        proc = subprocess.run(
            cmd, cwd=BASE_DIR, capture_output=True, text=True, timeout=1800
        )
        rc = proc.returncode
        # Ultime righe di output nel log dettagliato
        tail = "\n".join((proc.stdout or "").strip().splitlines()[-8:])
        if tail:
            handle.write(tail + "\n")
        if proc.returncode != 0 and proc.stderr:
            handle.write("STDERR: " + proc.stderr.strip()[-800:] + "\n")
    except subprocess.TimeoutExpired:
        rc = -1
        log(handle, f"[{step['name']}] TIMEOUT dopo 1800s")
    except Exception as e:  # noqa: BLE001
        rc = -2
        log(handle, f"[{step['name']}] ERRORE esecuzione: {e}")

    elapsed = round(time.time() - start, 1)
    status = "ok" if rc == 0 else "failed"
    log(handle, f"[{step['name']}] {status.upper()} (rc={rc}, {elapsed}s)")
    return {
        "name": step["name"],
        "phase": step["phase"],
        "script": step["script"],
        "critical": step["critical"],
        "network": step["network"],
        "returncode": rc,
        "status": status,
        "elapsed_s": elapsed,
    }


def main():
    parser = argparse.ArgumentParser(description="Pipeline enrichment giornaliere")
    parser.add_argument("--no-network", action="store_true",
                        help="Salta i passi che richiedono rete (solo re-build estratti)")
    parser.add_argument("--only", choices=["enrich", "download", "monitor"],
                        help="Esegui solo una fase")
    parser.add_argument("--dry-run", action="store_true",
                        help="Elenca i passi senza eseguirli")
    args = parser.parse_args()

    steps = STEPS
    if args.only:
        steps = [s for s in steps if s["phase"] == args.only]
    if args.no_network:
        steps = [s for s in steps if not s["network"]]

    if args.dry_run:
        print(f"[DRY RUN] {len(steps)} passi che verrebbero eseguiti:\n")
        for s in steps:
            net = "rete" if s["network"] else "offline"
            crit = "critico" if s["critical"] else "non-critico"
            print(f"  [{s['phase']:8}] {s['name']:20} ({net}, {crit}) - {s['desc']}")
        return 0

    os.makedirs(LOGS_DIR, exist_ok=True)
    with open(LOG_FILE, "w", encoding="utf-8") as handle:
        log(handle, "=" * 60)
        log(handle, f"PIPELINE ENRICHMENT GIORNALIERA - {TODAY}")
        log(handle, "=" * 60)
        log(handle, f"Passi da eseguire: {len(steps)}")

        results = []
        for step in steps:
            results.append(run_step(step, handle))

        ok = [r for r in results if r["status"] == "ok"]
        failed = [r for r in results if r["status"] != "ok"]
        critical_failed = [r for r in failed if r["critical"]]

        report = {
            "date": TODAY,
            "timestamp": datetime.now().isoformat(),
            "total_steps": len(results),
            "ok": len(ok),
            "failed": len(failed),
            "critical_failed": len(critical_failed),
            "results": results,
        }
        with open(REPORT_FILE, "w", encoding="utf-8") as rf:
            json.dump(report, rf, ensure_ascii=False, indent=2)

        log(handle, "-" * 60)
        log(handle, f"RIEPILOGO: {len(ok)} ok, {len(failed)} falliti "
                    f"({len(critical_failed)} critici)")
        for r in failed:
            tag = "CRITICO" if r["critical"] else "non-critico"
            log(handle, f"  FALLITO [{tag}] {r['name']} (rc={r['returncode']})")
        log(handle, f"Report: {REPORT_FILE}")
        log(handle, "=" * 60)

    # Esce con errore solo se un passo CRITICO e' fallito.
    return 1 if critical_failed else 0


if __name__ == "__main__":
    sys.exit(main())
