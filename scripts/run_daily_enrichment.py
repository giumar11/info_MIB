#!/usr/bin/env python3
"""
Orchestrator giornaliero dell'enrichment info_MIB.

Esegue tutte le pipeline registrate in `scripts/pipelines/registry.py`
(GIMBE, PDTA, AIFA, OASI, ONS, ISTAT, Orphanet, OECD/Eurostat/WHO,
governance SSN, riforme, osservatorio salute, societa scientifiche, ANIA).

Ciascuna pipeline decide autonomamente quali risorse scaricare nella
giornata, in base a `frequency` + ultima data di fetch (vedi
`pipelines/common.py::is_due`).

Schedulazione:

    # Installa il cron giornaliero (ogni giorno alle 07:00)
    python3 scripts/run_daily_enrichment.py --install-cron

    # Esecuzione manuale
    python3 scripts/run_daily_enrichment.py
    python3 scripts/run_daily_enrichment.py --pipeline ania
    python3 scripts/run_daily_enrichment.py --dry-run
    python3 scripts/run_daily_enrichment.py --force

Output:
- logs/enrichment_YYYY-MM-DD.log
- logs/enrichment_report_YYYY-MM-DD.json
- datasets/raw/<category>/manifest.json         (per pipeline)
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR / "scripts"))

from pipelines.common import run_pipeline
from pipelines.registry import ALL_PIPELINES, PIPELINES_BY_ID


LOGS_DIR = BASE_DIR / "logs"
TODAY = datetime.now().strftime("%Y-%m-%d")
LOG_FILE = LOGS_DIR / f"enrichment_{TODAY}.log"
REPORT_FILE = LOGS_DIR / f"enrichment_report_{TODAY}.json"


def setup_logging(verbose: bool = False) -> logging.Logger:
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("enrichment")
    logger.setLevel(logging.DEBUG)
    logger.handlers.clear()

    fh = logging.FileHandler(LOG_FILE, encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(logging.Formatter(
        "%(asctime)s | %(levelname)-7s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    ))
    logger.addHandler(fh)

    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG if verbose else logging.INFO)
    ch.setFormatter(logging.Formatter("%(levelname)-7s | %(message)s"))
    logger.addHandler(ch)
    return logger


def install_cron(hour: int = 7, minute: int = 0) -> None:
    """Installa un cron GIORNALIERO per eseguire l'enrichment."""
    script = Path(__file__).resolve()
    python = sys.executable
    log_path = LOGS_DIR / "cron_enrichment.log"
    LOGS_DIR.mkdir(parents=True, exist_ok=True)

    cron_line = (
        f"{minute} {hour} * * * {python} {script} "
        f">> {log_path} 2>&1"
    )
    tag = "# info_MIB - Enrichment giornaliero"

    try:
        current = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
        current_cron = current.stdout if current.returncode == 0 else ""
        if "run_daily_enrichment.py" in current_cron:
            print("Job cron gia installato:")
            print(current_cron)
            return
        new = current_cron.rstrip("\n")
        if new:
            new += "\n"
        new += f"\n{tag}\n{cron_line}\n"
        proc = subprocess.Popen(["crontab", "-"], stdin=subprocess.PIPE, text=True)
        proc.communicate(input=new)
        if proc.returncode == 0:
            print(f"Cron installato: ogni giorno alle {hour:02d}:{minute:02d}")
            print(f"  {cron_line}")
        else:
            print("Errore installazione cron. Riga da aggiungere manualmente:")
            print(f"  {cron_line}")
    except FileNotFoundError:
        print("'crontab' non disponibile sul sistema.")
        print("Su sistemi senza cron usa systemd timer o un job scheduler esterno:")
        print(f"  ExecStart={python} {script}")


def uninstall_cron() -> None:
    try:
        res = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
        if res.returncode != 0:
            print("Nessun crontab presente.")
            return
        lines = [
            ln for ln in res.stdout.split("\n")
            if "run_daily_enrichment.py" not in ln
            and "info_MIB - Enrichment giornaliero" not in ln
        ]
        proc = subprocess.Popen(["crontab", "-"], stdin=subprocess.PIPE, text=True)
        proc.communicate(input="\n".join(lines))
        if proc.returncode == 0:
            print("Cron rimosso.")
    except FileNotFoundError:
        print("'crontab' non disponibile.")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Enrichment giornaliero info_MIB",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--pipeline", action="append", dest="pipelines",
        help="Esegui solo le pipeline indicate (ripetibile). Es: --pipeline ania",
    )
    parser.add_argument(
        "--list", action="store_true",
        help="Elenca le pipeline registrate ed esce",
    )
    parser.add_argument(
        "--force", action="store_true",
        help="Forza il download anche delle risorse non ancora dovute",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Non scarica nulla, stampa solo cio che verrebbe fatto",
    )
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument(
        "--install-cron", action="store_true",
        help="Installa il cron giornaliero (07:00 di default)",
    )
    parser.add_argument(
        "--uninstall-cron", action="store_true",
    )
    parser.add_argument("--cron-hour", type=int, default=7)
    parser.add_argument("--cron-minute", type=int, default=0)
    args = parser.parse_args()

    if args.install_cron:
        install_cron(args.cron_hour, args.cron_minute)
        return 0
    if args.uninstall_cron:
        uninstall_cron()
        return 0
    if args.list:
        print(f"{'ID':<22} {'NAME':<55} RESOURCES")
        print("-" * 90)
        for p in ALL_PIPELINES:
            print(f"{p.pipeline_id:<22} {p.name:<55} {len(p.resources)}")
        return 0

    logger = setup_logging(args.verbose)
    logger.info("=" * 70)
    logger.info(f"START enrichment {TODAY}")
    logger.info("=" * 70)

    if args.pipelines:
        try:
            targets = [PIPELINES_BY_ID[p] for p in args.pipelines]
        except KeyError as e:
            logger.error(f"Pipeline sconosciuta: {e}")
            return 2
    else:
        targets = ALL_PIPELINES

    overall = {
        "date": TODAY,
        "started_at": datetime.now().isoformat(timespec="seconds"),
        "pipelines": [],
        "totals": {"pipelines": len(targets), "ok": 0, "failed": 0, "not_due": 0},
    }

    for pipeline in targets:
        try:
            summary = run_pipeline(
                pipeline,
                logger,
                force=args.force,
                dry_run=args.dry_run,
            )
        except Exception as e:
            logger.exception(f"Errore fatale in pipeline {pipeline.pipeline_id}: {e}")
            summary = {
                "pipeline_id": pipeline.pipeline_id,
                "name": pipeline.name,
                "error": str(e),
                "ok": 0, "failed": len(pipeline.resources), "not_due": 0,
                "resources": [],
            }
        overall["pipelines"].append(summary)
        overall["totals"]["ok"] += summary.get("ok", 0)
        overall["totals"]["failed"] += summary.get("failed", 0)
        overall["totals"]["not_due"] += summary.get("not_due", 0)

    overall["ended_at"] = datetime.now().isoformat(timespec="seconds")

    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        json.dump(overall, f, ensure_ascii=False, indent=2)

    t = overall["totals"]
    logger.info("-" * 70)
    logger.info(
        f"SUMMARY pipelines={t['pipelines']} ok={t['ok']} "
        f"not_due={t['not_due']} failed={t['failed']}"
    )
    logger.info(f"Log:    {LOG_FILE}")
    logger.info(f"Report: {REPORT_FILE}")

    return 0 if t["failed"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
