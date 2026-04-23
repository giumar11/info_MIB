"""
Pipeline ISTAT - Health for All, EHIS, multimorbidita anziani.

Scarica i dataset originali ISTAT (DBF, ZIP, PDF metodologici).
"""

from pathlib import Path

from .common import Pipeline, PipelineResource

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DEST_DIR = BASE_DIR / "datasets" / "raw" / "istat"


ISTAT_RESOURCES: list[PipelineResource] = [
    # --- Health for All Italia (database DBF) ---
    PipelineResource(
        resource_id="ISTAT_HFA_DB",
        url="https://www.istat.it/storage/sistemi-informativi/health-for-all/HFA_Italia.zip",
        filename="HFA_Italia_database.zip",
        title="ISTAT - Health for All Italia (database completo)",
        frequency="annual", category="hfa", min_size_bytes=100_000,
    ),
    # --- EHIS 2019 - microdati strutturati ---
    PipelineResource(
        resource_id="ISTAT_EHIS_TAVOLE",
        url="https://www.istat.it/it/files//2022/06/tavole_ehis_2019.zip",
        filename="tavole_ehis_2019.zip",
        title="ISTAT - EHIS 2019 tavole pubblicabili",
        year=2022, frequency="static", category="ehis", min_size_bytes=50_000,
    ),
    # --- Anziani in multimorbidita ---
    PipelineResource(
        resource_id="ISTAT_ANZIANI_MULTIMORB",
        url="https://www.istat.it/it/files//2022/07/Report-condizioni-salute-anziani-2019.pdf",
        filename="ISTAT_Anziani_Multimorbidita_2019.pdf",
        title="ISTAT - Condizioni di salute degli anziani 2019",
        year=2022, frequency="periodic", category="anziani",
    ),
    # --- Rapporto annuale ISTAT 2024 ---
    PipelineResource(
        resource_id="ISTAT_RAPPORTO_ANNUALE_2024",
        url="https://www.istat.it/it/files//2024/05/Rapporto-Annuale-2024.pdf",
        filename="ISTAT_Rapporto_Annuale_2024.pdf",
        title="ISTAT - Rapporto Annuale 2024",
        year=2024, frequency="annual", category="rapporto_annuale",
    ),
    PipelineResource(
        resource_id="ISTAT_RAPPORTO_ANNUALE_2025",
        url="https://www.istat.it/it/files//2025/05/Rapporto-Annuale-2025.pdf",
        filename="ISTAT_Rapporto_Annuale_2025.pdf",
        title="ISTAT - Rapporto Annuale 2025",
        year=2025, frequency="annual", category="rapporto_annuale",
    ),
]


PIPELINE = Pipeline(
    pipeline_id="istat",
    name="ISTAT - Health for All, EHIS, Rapporti Annuali",
    dest_dir=DEST_DIR,
    resources=ISTAT_RESOURCES,
    description="Dataset ISTAT originali sulla salute della popolazione",
)
