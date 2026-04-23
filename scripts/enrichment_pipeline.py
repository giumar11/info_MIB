#!/usr/bin/env python3
"""
Orchestratore delle pipelines di enrichment giornaliero del repository info_MIB.

Per ogni categoria di documenti presente nella repository questo script:

1. **Scarica/aggiorna i documenti originali** dalle rispettive fonti
   istituzionali (PDF, XML, CSV, XLSX, ZIP) e li salva sotto
   `datasets/raw/<categoria>/` conservando sempre il file originale oltre
   a eventuali estratti processati.
2. **Rigenera i dataset processed** (JSON/CSV) a partire dai raw appena
   scaricati, invocando gli script dedicati quando disponibili.
3. **Controlla gli aggiornamenti** delle fonti tramite
   `scheduler_check_updates.py` e produce un report giornaliero in
   `logs/enrichment_daily_YYYY-MM-DD.json`.

Categorie coperte (tutte quelle presenti nella repository):
    governance, finance, reform, international, activity,
    analysis, epidemiology, statistics, surveillance, rare_diseases,
    workforce, screening, pharma, pdta, access, performance, insurance

Uso:
    python3 scripts/enrichment_pipeline.py                    # tutte le categorie
    python3 scripts/enrichment_pipeline.py --category pdta
    python3 scripts/enrichment_pipeline.py --category insurance
    python3 scripts/enrichment_pipeline.py --dry-run
    python3 scripts/enrichment_pipeline.py --install-cron     # schedulazione giornaliera 05:00
    python3 scripts/enrichment_pipeline.py --uninstall-cron

Output:
    logs/enrichment_daily_<data>.log
    logs/enrichment_daily_<data>.json
    datasets/raw/<categoria>/...              (originali)
    datasets/processed/<categoria>_*.json     (estratti)
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
from typing import Callable

BASE_DIR = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = BASE_DIR / "scripts"
LOGS_DIR = BASE_DIR / "logs"
TODAY = datetime.now().strftime("%Y-%m-%d")

LOG_FILE = LOGS_DIR / f"enrichment_daily_{TODAY}.log"
REPORT_FILE = LOGS_DIR / f"enrichment_daily_{TODAY}.json"

PYTHON = sys.executable


# ============================================================================
# Definizione pipelines per categoria
# ============================================================================

def _run(cmd: list[str], timeout: int = 1800) -> tuple[int, str]:
    """Esegue un comando figlio e cattura output."""
    try:
        result = subprocess.run(
            cmd, cwd=str(BASE_DIR), capture_output=True,
            text=True, timeout=timeout
        )
        out = (result.stdout or "") + (result.stderr or "")
        return result.returncode, out[-4000:]
    except subprocess.TimeoutExpired:
        return 124, f"Timeout dopo {timeout}s: {' '.join(cmd)}"
    except FileNotFoundError as e:
        return 127, f"Comando non trovato: {e}"


def _check_source_update(source_ids: list[str]) -> tuple[int, str]:
    """Chiama scheduler_check_updates.py per le fonti specificate."""
    cmd = [PYTHON, str(SCRIPTS_DIR / "scheduler_check_updates.py")]
    for sid in source_ids:
        cmd.extend(["--source", sid])
    return _run(cmd, timeout=900)


def pipeline_pdta(dry_run: bool) -> dict:
    """Scarica tutti i PDTA nazionali e regionali come PDF originali."""
    steps = []
    if dry_run:
        rc, out = _run([PYTHON, str(SCRIPTS_DIR / "download_pdta.py"), "--dry-run"])
    else:
        rc, out = _run([PYTHON, str(SCRIPTS_DIR / "download_pdta.py"), "--level", "all"])
    steps.append({"step": "download_pdta", "rc": rc, "output_tail": out[-600:]})
    return {"category": "pdta", "steps": steps, "ok": rc == 0}


def pipeline_analysis_gimbe(dry_run: bool) -> dict:
    """Scarica rapporti GIMBE SSN e Osservatorio come PDF originali."""
    steps = []
    cmd = [PYTHON, str(SCRIPTS_DIR / "download_gimbe_pdfs.py")]
    if dry_run:
        cmd.append("--check")
    rc, out = _run(cmd)
    steps.append({"step": "download_gimbe_pdfs", "rc": rc, "output_tail": out[-600:]})

    if not dry_run:
        rc2, out2 = _check_source_update([
            "GIMBE_001", "GIMBE_SSN", "GIMBE_OSS", "GIMBE_MOB",
            "GIMBE_ATTESA", "GIMBE_WORK", "GIMBE_PNRR", "GIMBE_COVID"
        ])
        steps.append({"step": "check_updates", "rc": rc2, "output_tail": out2[-400:]})

    return {"category": "analysis_gimbe", "steps": steps, "ok": all(s["rc"] == 0 for s in steps)}


def pipeline_insurance_ania(dry_run: bool) -> dict:
    """Scarica tutti i report ANIA (mercato assicurativo italiano)."""
    steps = []
    cmd = [PYTHON, str(SCRIPTS_DIR / "download_ania.py")]
    if dry_run:
        cmd.append("--dry-run")
    rc, out = _run(cmd)
    steps.append({"step": "download_ania", "rc": rc, "output_tail": out[-600:]})
    return {"category": "insurance", "steps": steps, "ok": rc == 0}


def pipeline_screening_ons(dry_run: bool) -> dict:
    """Rigenera estratti ONS + verifica aggiornamento rapporti originali."""
    steps = []
    if not dry_run:
        rc, out = _run([PYTHON, str(SCRIPTS_DIR / "enrich_scientific_reports_ons.py")])
        steps.append({"step": "enrich_ons", "rc": rc, "output_tail": out[-600:]})
    rc2, out2 = _check_source_update(["ONS_001"])
    steps.append({"step": "check_updates", "rc": rc2, "output_tail": out2[-400:]})
    return {"category": "screening", "steps": steps, "ok": all(s["rc"] == 0 for s in steps)}


def pipeline_pharma_aifa(dry_run: bool) -> dict:
    """Verifica aggiornamento di tutti i report AIFA (OsMed, registri, PFN, ecc.)."""
    ids = [
        "AIFA_OSMED", "AIFA_OSMED_DATA", "AIFA_VACC", "AIFA_OSSC",
        "AIFA_ATT", "AIFA_REG", "AIFA_TRASP", "AIFA_PFN", "AIFA_HORIZON",
        "OSMED_001",
    ]
    rc, out = _check_source_update(ids)
    return {"category": "pharma", "steps": [{"step": "check_updates", "rc": rc, "output_tail": out[-600:]}], "ok": rc == 0}


def pipeline_epidemiology(dry_run: bool) -> dict:
    """Orphadata + società scientifiche (AIOM, AIRTUM, SID, ecc.) + ISTAT HFA."""
    steps = []
    if not dry_run:
        xml_path = BASE_DIR / "datasets" / "raw" / "orphadata" / "orphadata_epidemiology_it.xml"
        legacy_xml = BASE_DIR / "datasets" / "raw" / "orphadata_epidemiology_it.xml"
        if legacy_xml.exists() and not xml_path.exists():
            xml_path.parent.mkdir(parents=True, exist_ok=True)
            xml_path.write_bytes(legacy_xml.read_bytes())
        if xml_path.exists():
            rc, out = _run([PYTHON, str(SCRIPTS_DIR / "parse_orphadata.py")])
            steps.append({"step": "parse_orphadata", "rc": rc, "output_tail": out[-600:]})

    ids = ["ORPHA_001", "AIOM_001", "AIRTUM_001", "SID_001", "SIN_001", "ISTAT_001"]
    rc2, out2 = _check_source_update(ids)
    steps.append({"step": "check_updates", "rc": rc2, "output_tail": out2[-400:]})
    return {"category": "epidemiology", "steps": steps, "ok": all(s["rc"] == 0 for s in steps)}


def pipeline_activity_sdo(dry_run: bool) -> dict:
    """Regenera riepiloghi SDO + verifica aggiornamento dataset SDO / sperimentazioni."""
    steps = []
    if not dry_run:
        rc, out = _run([PYTHON, str(SCRIPTS_DIR / "extract_sdo_data.py")])
        steps.append({"step": "extract_sdo", "rc": rc, "output_tail": out[-600:]})
    rc2, out2 = _check_source_update(["SDO_001", "AIFA_OSSC", "AIFA_ATT"])
    steps.append({"step": "check_updates", "rc": rc2, "output_tail": out2[-400:]})
    return {"category": "activity", "steps": steps, "ok": all(s["rc"] == 0 for s in steps)}


def pipeline_statistics_istat(dry_run: bool) -> dict:
    """ISTAT Health for All + EHIS."""
    steps = []
    if not dry_run:
        hfa_dir = BASE_DIR / "datasets" / "raw" / "istat" / "HFA"
        if hfa_dir.exists():
            rc, out = _run([PYTHON, str(SCRIPTS_DIR / "analyze_hfa_chronic.py")])
            steps.append({"step": "analyze_hfa", "rc": rc, "output_tail": out[-600:]})
    rc2, out2 = _check_source_update(["ISTAT_001"])
    steps.append({"step": "check_updates", "rc": rc2, "output_tail": out2[-400:]})
    return {"category": "statistics", "steps": steps, "ok": all(s["rc"] == 0 for s in steps)}


def pipeline_governance(dry_run: bool) -> dict:
    """PNE, LEA-NSG, PNGLA."""
    ids = ["PNE_001", "LEA_001", "PNGLA_001"]
    rc, out = _check_source_update(ids)
    return {"category": "governance", "steps": [{"step": "check_updates", "rc": rc, "output_tail": out[-600:]}], "ok": rc == 0}


def pipeline_finance(dry_run: bool) -> dict:
    """OpenBDAP, OsMed, Corte dei Conti."""
    ids = ["BDAP_001", "OSMED_001", "CORTE_001"]
    rc, out = _check_source_update(ids)
    return {"category": "finance", "steps": [{"step": "check_updates", "rc": rc, "output_tail": out[-600:]}], "ok": rc == 0}


def pipeline_reform(dry_run: bool) -> dict:
    """DM77, PNRR M6, DM70."""
    ids = ["DM77_001", "PNRR_001", "DM70_001"]
    rc, out = _check_source_update(ids)
    return {"category": "reform", "steps": [{"step": "check_updates", "rc": rc, "output_tail": out[-600:]}], "ok": rc == 0}


def pipeline_international(dry_run: bool) -> dict:
    """OECD, Eurostat, WHO GHED, KFF, Commonwealth Fund, NAIC."""
    ids = ["OECD_001", "EURO_001", "GHED_001", "KFF_001", "CWF_001", "NAIC_001"]
    rc, out = _check_source_update(ids)
    return {"category": "international", "steps": [{"step": "check_updates", "rc": rc, "output_tail": out[-600:]}], "ok": rc == 0}


def pipeline_analysis(dry_run: bool) -> dict:
    """OASI Bocconi, Osservatorio Salute, CENSIS, CREA, CPI."""
    ids = ["OASI_001", "OASI_002", "OCPS_001", "OSSERV_001",
           "CENSIS_001", "CREA_001", "CPI_001"]
    rc, out = _check_source_update(ids)
    return {"category": "analysis", "steps": [{"step": "check_updates", "rc": rc, "output_tail": out[-600:]}], "ok": rc == 0}


def pipeline_surveillance(dry_run: bool) -> dict:
    """PASSI (ISS), AIFA Vaccini, SItI."""
    ids = ["PASSI_001", "AIFA_VACC", "SITI_001", "GIMBE_COVID"]
    rc, out = _check_source_update(ids)
    return {"category": "surveillance", "steps": [{"step": "check_updates", "rc": rc, "output_tail": out[-600:]}], "ok": rc == 0}


def pipeline_rare_diseases(dry_run: bool) -> dict:
    """UNIAMO + Orphanet."""
    ids = ["UNIAMO_001", "ORPHA_001"]
    rc, out = _check_source_update(ids)
    return {"category": "rare_diseases", "steps": [{"step": "check_updates", "rc": rc, "output_tail": out[-600:]}], "ok": rc == 0}


def pipeline_workforce(dry_run: bool) -> dict:
    """ENPAM + GIMBE Workforce."""
    ids = ["ENPAM_001", "GIMBE_WORK"]
    rc, out = _check_source_update(ids)
    return {"category": "workforce", "steps": [{"step": "check_updates", "rc": rc, "output_tail": out[-600:]}], "ok": rc == 0}


def pipeline_access(dry_run: bool) -> dict:
    """Liste d'attesa: PNGLA + GIMBE attese."""
    ids = ["PNGLA_001", "GIMBE_ATTESA"]
    rc, out = _check_source_update(ids)
    return {"category": "access", "steps": [{"step": "check_updates", "rc": rc, "output_tail": out[-600:]}], "ok": rc == 0}


def pipeline_performance(dry_run: bool) -> dict:
    """Performance: PNE, CREA."""
    ids = ["PNE_001", "CREA_001"]
    rc, out = _check_source_update(ids)
    return {"category": "performance", "steps": [{"step": "check_updates", "rc": rc, "output_tail": out[-600:]}], "ok": rc == 0}


# ============================================================================
# Registry categorie -> pipeline
# ============================================================================

PIPELINES: dict[str, Callable[[bool], dict]] = {
    "governance": pipeline_governance,
    "finance": pipeline_finance,
    "reform": pipeline_reform,
    "international": pipeline_international,
    "activity": pipeline_activity_sdo,
    "analysis": pipeline_analysis,
    "analysis_gimbe": pipeline_analysis_gimbe,
    "epidemiology": pipeline_epidemiology,
    "statistics": pipeline_statistics_istat,
    "surveillance": pipeline_surveillance,
    "rare_diseases": pipeline_rare_diseases,
    "workforce": pipeline_workforce,
    "screening": pipeline_screening_ons,
    "pharma": pipeline_pharma_aifa,
    "pdta": pipeline_pdta,
    "access": pipeline_access,
    "performance": pipeline_performance,
    "insurance": pipeline_insurance_ania,
}


# ============================================================================
# Cron / logging
# ============================================================================

def setup_logging() -> logging.Logger:
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("enrichment_pipeline")
    logger.setLevel(logging.DEBUG)

    fh = logging.FileHandler(LOG_FILE, encoding="utf-8")
    fh.setFormatter(logging.Formatter(
        "%(asctime)s | %(levelname)-7s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    ))
    logger.addHandler(fh)

    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter("%(levelname)-7s | %(message)s"))
    logger.addHandler(ch)
    return logger


def install_cron() -> None:
    script_path = Path(__file__).resolve()
    log_path = LOGS_DIR / "cron_enrichment.log"
    cron_line = f"0 5 * * * {PYTHON} {script_path} >> {log_path} 2>&1"
    comment = "# InfoMIB - Enrichment giornaliero fonti dati"

    try:
        current = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
        existing = current.stdout if current.returncode == 0 else ""
        if "enrichment_pipeline.py" in existing:
            print("Cron già installato.")
            return
        new = existing.rstrip("\n") + ("\n" if existing else "") + f"{comment}\n{cron_line}\n"
        proc = subprocess.Popen(["crontab", "-"], stdin=subprocess.PIPE, text=True)
        proc.communicate(input=new)
        if proc.returncode == 0:
            print(f"Cron installato (giornaliero 05:00):\n  {cron_line}")
        else:
            print("Errore installazione cron. Manuale:")
            print(f"  {cron_line}")
    except FileNotFoundError:
        print("crontab non disponibile. Linea manuale:")
        print(f"  {cron_line}")


def uninstall_cron() -> None:
    try:
        current = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
        if current.returncode != 0:
            return
        kept = [
            line for line in current.stdout.split("\n")
            if "enrichment_pipeline.py" not in line
            and "InfoMIB - Enrichment giornaliero" not in line
        ]
        proc = subprocess.Popen(["crontab", "-"], stdin=subprocess.PIPE, text=True)
        proc.communicate(input="\n".join(kept))
        print("Cron rimosso.")
    except FileNotFoundError:
        pass


# ============================================================================
# Main
# ============================================================================

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Pipeline di enrichment giornaliero info_MIB",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--category", action="append",
                        choices=sorted(PIPELINES.keys()),
                        help="Categorie da eseguire (ripetibile). Default: tutte.")
    parser.add_argument("--dry-run", action="store_true",
                        help="Esegue solo i controlli, senza scaricare o rigenerare file.")
    parser.add_argument("--install-cron", action="store_true",
                        help="Installa cron giornaliero (05:00)")
    parser.add_argument("--uninstall-cron", action="store_true")
    args = parser.parse_args()

    if args.install_cron:
        install_cron()
        return 0
    if args.uninstall_cron:
        uninstall_cron()
        return 0

    logger = setup_logging()
    logger.info("=" * 60)
    logger.info(f"ENRICHMENT PIPELINE - {TODAY}")
    logger.info("=" * 60)

    categories = args.category or list(PIPELINES.keys())
    logger.info(f"Categorie: {', '.join(categories)}")

    results = []
    for cat in categories:
        logger.info(f"[{cat}] inizio")
        try:
            out = PIPELINES[cat](args.dry_run)
        except Exception as exc:  # safety: una pipeline rotta non ferma le altre
            logger.exception(f"[{cat}] errore imprevisto")
            out = {"category": cat, "steps": [], "ok": False, "error": str(exc)}
        status = "OK" if out.get("ok") else "FAIL"
        logger.info(f"[{cat}] fine -> {status}")
        results.append(out)

    summary = {
        "date": TODAY,
        "timestamp": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "dry_run": args.dry_run,
        "categories_run": len(results),
        "categories_ok": sum(1 for r in results if r.get("ok")),
        "categories_failed": sum(1 for r in results if not r.get("ok")),
        "results": results,
    }
    REPORT_FILE.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    logger.info(f"Report: {REPORT_FILE}")
    logger.info(f"Log:    {LOG_FILE}")

    return 0 if summary["categories_failed"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
