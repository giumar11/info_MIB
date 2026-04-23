"""
Pipeline ONS - Osservatorio Nazionale Screening (cervice, mammella, colon retto).
"""

from pathlib import Path

from .common import Pipeline, PipelineResource

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DEST_DIR = BASE_DIR / "datasets" / "raw" / "ons"


ONS_RESOURCES: list[PipelineResource] = [
    PipelineResource(
        resource_id="ONS_RAPPORTO_2022",
        url="https://www.osservatorionazionalescreening.it/sites/default/files/allegati/Rapporto_ONS_2022.pdf",
        filename="Rapporto_ONS_2022.pdf",
        title="ONS - Rapporto annuale 2022",
        year=2023, frequency="static", category="rapporto",
    ),
    PipelineResource(
        resource_id="ONS_RAPPORTO_2023",
        url="https://www.osservatorionazionalescreening.it/sites/default/files/allegati/Rapporto_ONS_2023.pdf",
        filename="Rapporto_ONS_2023.pdf",
        title="ONS - Rapporto annuale 2023",
        year=2024, frequency="annual", category="rapporto",
    ),
    PipelineResource(
        resource_id="ONS_RAPPORTO_2024",
        url="https://www.osservatorionazionalescreening.it/sites/default/files/allegati/Rapporto_ONS_2024.pdf",
        filename="Rapporto_ONS_2024.pdf",
        title="ONS - Rapporto annuale 2024",
        year=2025, frequency="annual", category="rapporto",
    ),
]


PIPELINE = Pipeline(
    pipeline_id="ons",
    name="ONS - Osservatorio Nazionale Screening",
    dest_dir=DEST_DIR,
    resources=ONS_RESOURCES,
    description="Rapporti ONS sugli screening oncologici",
)
