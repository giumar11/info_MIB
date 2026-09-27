#!/usr/bin/env python3
"""
Orchestratore delle pipeline di enrichment giornaliere InfoMIB.

Esegue, per tutte le categorie di documenti presenti nel repository, il download
degli ORIGINALI (report e dataset) dalle fonti ufficiali e il controllo degli
aggiornamenti del catalogo. Pensato per l'esecuzione schedulata giornaliera
(GitHub Actions: .github/workflows/daily-enrichment.yml).

Ogni step è isolato: il fallimento di una fonte (es. link non raggiungibile) non
interrompe gli altri. Al termine viene scritto un report giornaliero in logs/.

Uso:
    python3 scripts/run_daily_enrichment.py                # tutti gli step
    python3 scripts/run_daily_enrichment.py --only ania     # solo uno step
    python3 scripts/run_daily_enrichment.py --skip scheduler # salta uno step
    python3 scripts/run_daily_enrichment.py --dry-run
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

# Ogni step: (nome, [argomenti dello script]). Coprono tutte le categorie di
# documenti che dispongono di originali scaricabili o di un controllo fonti.
STEPS = [
    ("gimbe",            ["download_gimbe_pdfs.py"]),
    ("pdta",             ["download_pdta.py", "--level", "all"]),
    ("ania",             ["download_ania_reports.py"]),
    ("original_reports", ["download_original_reports.py"]),
    # Il controllo aggiornamenti copre TUTTE le fonti del catalogo (governance,
    # finanza, riforme, internazionale, epidemiologia, ecc.).
    ("scheduler",        ["scheduler_check_updates.py", "--force"]),
]


def run_step(name, script_args, dry_run=False, timeout=1800):
    script_path = os.path.join(SCRIPTS_DIR, script_args[0])
    cmd = [PY, script_path] + script_args[1:]
    if dry_run:
        print(f"[DRY RUN] {name}: {' '.join(cmd)}")
        return {"step": name, "cmd": cmd, "returncode": None, "status": "dry_run"}

    print(f"\n{'#' * 70}\n# STEP: {name}\n# CMD:  {' '.join(cmd)}\n{'#' * 70}")
    start = time.time()
    try:
        proc = subprocess.run(cmd, cwd=BASE_DIR, timeout=timeout)
        rc = proc.returncode
        status = "ok" if rc == 0 else "completed_with_errors"
    except subprocess.TimeoutExpired:
        rc = None
        status = "timeout"
        print(f"    STEP {name}: TIMEOUT dopo {timeout}s")
    except Exception as exc:  # noqa: BLE001
        rc = None
        status = "error"
        print(f"    STEP {name}: ERRORE {type(exc).__name__}: {exc}")
    elapsed = round(time.time() - start, 1)
    return {"step": name, "cmd": cmd, "returncode": rc, "status": status, "seconds": elapsed}


def main():
    parser = argparse.ArgumentParser(description="Orchestratore enrichment giornaliero")
    parser.add_argument("--only", action="append", help="Esegui solo questi step (ripetibile)")
    parser.add_argument("--skip", action="append", default=[], help="Salta questi step (ripetibile)")
    parser.add_argument("--dry-run", action="store_true", help="Mostra i comandi senza eseguirli")
    parser.add_argument("--timeout", type=int, default=1800, help="Timeout per step in secondi")
    args = parser.parse_args()

    steps = STEPS
    if args.only:
        steps = [s for s in steps if s[0] in set(args.only)]
    steps = [s for s in steps if s[0] not in set(args.skip)]

    print("=" * 70)
    print(f"ENRICHMENT GIORNALIERO InfoMIB - {datetime.now().isoformat(timespec='seconds')}")
    print(f"Step: {', '.join(s[0] for s in steps)}")
    print("=" * 70)

    results = [run_step(name, sargs, dry_run=args.dry_run, timeout=args.timeout)
               for name, sargs in steps]

    if not args.dry_run:
        os.makedirs(LOGS_DIR, exist_ok=True)
        report_path = os.path.join(LOGS_DIR, f"enrichment_report_{datetime.now():%Y-%m-%d}.json")
        with open(report_path, "w", encoding="utf-8") as fh:
            json.dump({"timestamp": datetime.now().isoformat(),
                       "steps": results}, fh, indent=2, ensure_ascii=False)
        print(f"\nReport: {report_path}")

    print(f"\n{'=' * 70}\nRIEPILOGO ENRICHMENT")
    for r in results:
        print(f"  {r['step']:<18} -> {r['status']} (rc={r['returncode']})")
    print("=" * 70)

    # Non blocchiamo il workflow per fallimenti di rete di singole fonti: usciamo 0
    # a meno di un errore catastrofico dell'orchestratore stesso.
    hard_errors = [r for r in results if r["status"] == "error"]
    return 1 if hard_errors else 0


if __name__ == "__main__":
    sys.exit(main())
