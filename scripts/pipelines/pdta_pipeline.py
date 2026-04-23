"""
Pipeline PDTA - Percorsi Diagnostico-Terapeutici Assistenziali.

Wrappa il database URL gia definito in `scripts/download_pdta.py` e lo
espone come `Pipeline` standard cosi puo partecipare all'enrichment
giornaliero. Copre il livello nazionale (AGENAS, ISS, Ministero) e
regionale (tutte le regioni + province autonome).
"""

from pathlib import Path
import importlib.util
import sys

from .common import Pipeline, PipelineResource

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DEST_DIR = BASE_DIR / "datasets" / "raw" / "pdta"

# Riuso il dict PDTA_DOWNLOADS dallo script legacy per evitare duplicazione.
_DL_PATH = BASE_DIR / "scripts" / "download_pdta.py"
_spec = importlib.util.spec_from_file_location("download_pdta_legacy", _DL_PATH)
_legacy = importlib.util.module_from_spec(_spec)
sys.modules["download_pdta_legacy"] = _legacy
_spec.loader.exec_module(_legacy)


def _build_pdta_resources() -> list[PipelineResource]:
    resources: list[PipelineResource] = []
    for level, groups in _legacy.PDTA_DOWNLOADS.items():
        for group_key, items in groups.items():
            if not items:
                continue
            subdir = f"{level}/{group_key}"
            for item in items:
                resources.append(PipelineResource(
                    resource_id=item["id"],
                    url=item["url"],
                    filename=item["filename"],
                    title=item.get("title", ""),
                    year=item.get("year"),
                    frequency="periodic",
                    category="pdta",
                    subcategory=level,
                    subdir=subdir,
                ))
    return resources


PDTA_RESOURCES = _build_pdta_resources()

PIPELINE = Pipeline(
    pipeline_id="pdta",
    name="PDTA - Percorsi nazionali e regionali",
    dest_dir=DEST_DIR,
    resources=PDTA_RESOURCES,
    description=(
        "PDTA nazionali (AGENAS, ISS, Conferenza Stato-Regioni) e regionali "
        "(tutte le regioni + PA)"
    ),
)
