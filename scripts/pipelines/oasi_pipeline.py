"""
Pipeline OASI - CERGAS SDA Bocconi.

Scarica il rapporto OASI annuale e l'archivio dei capitoli (2019-2025),
con aggiornamento annuale.
"""

from pathlib import Path

from .common import Pipeline, PipelineResource

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DEST_DIR = BASE_DIR / "datasets" / "raw" / "oasi_bocconi"


OASI_RESOURCES: list[PipelineResource] = [
    PipelineResource(
        resource_id="OASI_2019",
        url="https://cergas.unibocconi.eu/sites/default/files/files/OASI-2019-Sintesi.pdf",
        filename="OASI_2019_Sintesi.pdf",
        title="Rapporto OASI 2019 - Sintesi",
        year=2019, frequency="static", category="rapporto_sintesi",
    ),
    PipelineResource(
        resource_id="OASI_2020",
        url="https://cergas.unibocconi.eu/sites/default/files/files/OASI-2020-Sintesi.pdf",
        filename="OASI_2020_Sintesi.pdf",
        title="Rapporto OASI 2020 - Sintesi",
        year=2020, frequency="static", category="rapporto_sintesi",
    ),
    PipelineResource(
        resource_id="OASI_2021",
        url="https://cergas.unibocconi.eu/sites/default/files/files/OASI-2021-Sintesi.pdf",
        filename="OASI_2021_Sintesi.pdf",
        title="Rapporto OASI 2021 - Sintesi",
        year=2021, frequency="static", category="rapporto_sintesi",
    ),
    PipelineResource(
        resource_id="OASI_2022",
        url="https://cergas.unibocconi.eu/sites/default/files/files/OASI-2022-Sintesi.pdf",
        filename="OASI_2022_Sintesi.pdf",
        title="Rapporto OASI 2022 - Sintesi",
        year=2022, frequency="static", category="rapporto_sintesi",
    ),
    PipelineResource(
        resource_id="OASI_2023",
        url="https://cergas.unibocconi.eu/sites/default/files/files/OASI-2023-Sintesi.pdf",
        filename="OASI_2023_Sintesi.pdf",
        title="Rapporto OASI 2023 - Sintesi",
        year=2023, frequency="static", category="rapporto_sintesi",
    ),
    PipelineResource(
        resource_id="OASI_2024",
        url="https://cergas.unibocconi.eu/sites/default/files/files/OASI-2024-Sintesi.pdf",
        filename="OASI_2024_Sintesi.pdf",
        title="Rapporto OASI 2024 - Sintesi",
        year=2024, frequency="static", category="rapporto_sintesi",
    ),
    PipelineResource(
        resource_id="OASI_2025",
        url="https://cergas.unibocconi.eu/sites/default/files/files/OASI-2025-Sintesi.pdf",
        filename="OASI_2025_Sintesi.pdf",
        title="Rapporto OASI 2025 - Sintesi",
        year=2025, frequency="annual", category="rapporto_sintesi",
    ),
]


PIPELINE = Pipeline(
    pipeline_id="oasi",
    name="OASI - CERGAS SDA Bocconi",
    dest_dir=DEST_DIR,
    resources=OASI_RESOURCES,
    description="Rapporti OASI sulle Aziende e sul Sistema Sanitario Italiano",
)
