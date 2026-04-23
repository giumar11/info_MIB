"""Post-processor hooks per le pipeline di enrichment.

Ogni hook riceve la lista di `DownloadResult` e ritorna la lista degli
artefatti generati (path relativi al repo). Se un hook fallisce, la sua
eccezione viene catturata dal motore e loggata nel report, senza bloccare
le altre pipeline.
"""

from __future__ import annotations

import logging
import subprocess
import sys
from pathlib import Path
from typing import Callable

from .base import DownloadResult

log = logging.getLogger("enrichment.postprocess")


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _any_changed(results: list[DownloadResult], source_ids: set[str] | None = None) -> bool:
    for r in results:
        if r.status == "downloaded" and (source_ids is None or r.source_id in source_ids):
            return True
    return False


def _run_script(script: str, args: list[str] | None = None) -> str:
    """Esegue uno script Python del repo; ritorna il path come stringa se ok."""
    cmd = [sys.executable, str(_repo_root() / "scripts" / script)] + (args or [])
    log.info("Eseguo: %s", " ".join(cmd))
    subprocess.run(cmd, check=True)
    return f"scripts/{script}"


def orphadata_post(results: list[DownloadResult]) -> list[str]:
    if not _any_changed(results, {"ORPHA_EPI_IT"}):
        log.info("Orphadata IT invariato, skip parse")
        return []
    return [_run_script("parse_orphadata.py")]


def ministero_salute_post(results: list[DownloadResult]) -> list[str]:
    # Ricostruisci gli estratti SDO (script non dipende da input file cambiati)
    return [_run_script("extract_sdo_data.py")]


def istat_post(results: list[DownloadResult]) -> list[str]:
    if not _any_changed(results, {"ISTAT_HFA_DB"}):
        return []
    # Nota: analyze_hfa_chronic.py richiede l'HFA già decompresso in datasets/raw/istat/hfa/HFA/
    try:
        return [_run_script("analyze_hfa_chronic.py")]
    except subprocess.CalledProcessError as e:
        log.warning("analyze_hfa_chronic.py fallito (probabile HFA non decompresso): %s", e)
        return []


def scientific_reports_post(results: list[DownloadResult]) -> list[str]:
    """Rigenera gli estratti per ONS, OASI, AIFA, GIMBE, società scientifiche."""
    try:
        return [_run_script("enrich_scientific_reports_ons.py")]
    except subprocess.CalledProcessError as e:
        log.warning("enrich_scientific_reports_ons.py fallito: %s", e)
        return []


def migrate_db_post(results: list[DownloadResult]) -> list[str]:
    return [_run_script("migrate_to_database.py")]


# Registry categoria → hook
POST_HOOKS: dict[str, Callable[[list[DownloadResult]], list[str]]] = {
    "orphadata": orphadata_post,
    "ministero_salute": ministero_salute_post,
    "istat": istat_post,
    "ons": scientific_reports_post,
    "oasi_bocconi": scientific_reports_post,
    "aifa": scientific_reports_post,
    "gimbe": scientific_reports_post,
    "societa_scientifiche": scientific_reports_post,
}
