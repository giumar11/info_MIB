"""Post-processor hooks per le pipeline di enrichment.

Ogni hook riceve la lista di `DownloadResult` e ritorna la lista degli
artefatti generati (path relativi al repo). Se un hook fallisce, la sua
eccezione viene catturata dal motore e loggata nel report, senza bloccare
le altre pipeline.
"""

from __future__ import annotations

import logging
import shutil
import subprocess
import sys
import zipfile
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


def _extract_hfa_zip(zip_path: Path, extract_root: Path) -> bool:
    """Estrae il pacchetto HFA in extract_root/HFA/. Ritorna True se ok."""
    if not zip_path.exists():
        log.info("HFA zip non presente (%s), skip estrazione", zip_path)
        return False
    target = extract_root / "HFA"
    # Pulisco il target per garantire corrispondenza 1:1 col nuovo zip.
    if target.exists():
        shutil.rmtree(target)
    target.mkdir(parents=True, exist_ok=True)
    try:
        with zipfile.ZipFile(zip_path) as zf:
            members = zf.namelist()
            # Se il zip contiene già una directory root "HFA/", estrai direttamente;
            # altrimenti i file vengono messi dentro HFA/.
            root_dirs = {m.split("/", 1)[0] for m in members if "/" in m}
            if root_dirs == {"HFA"}:
                zf.extractall(extract_root)
            else:
                zf.extractall(target)
    except zipfile.BadZipFile as e:
        log.error("HFA zip corrotto: %s", e)
        return False
    log.info("HFA estratto in %s (%d file)", target, sum(1 for _ in target.rglob("*") if _.is_file()))
    return True


def istat_post(results: list[DownloadResult]) -> list[str]:
    produced: list[str] = []
    repo = _repo_root()
    hfa_zip = repo / "datasets" / "raw" / "istat" / "hfa" / "hfa_italia.zip"
    hfa_dir = repo / "datasets" / "raw" / "istat" / "hfa"
    hfa_changed = _any_changed(results, {"ISTAT_HFA_DB"})
    hfa_already_extracted = (hfa_dir / "HFA").exists() and any((hfa_dir / "HFA").iterdir())

    # Estrai il zip se è cambiato oppure se non è mai stato estratto.
    if hfa_changed or (hfa_zip.exists() and not hfa_already_extracted):
        if _extract_hfa_zip(hfa_zip, hfa_dir):
            produced.append(str(hfa_dir / "HFA"))

    # Rigenera gli estratti solo se il zip è stato aggiornato (evita run lenti inutili).
    if hfa_changed and (hfa_dir / "HFA").exists():
        try:
            produced.append(_run_script("analyze_hfa_chronic.py"))
        except subprocess.CalledProcessError as e:
            log.warning("analyze_hfa_chronic.py fallito: %s", e)
    return produced


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
