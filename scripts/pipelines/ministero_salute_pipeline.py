"""
Pipeline Ministero della Salute - SDO, Open Data, rapporti ospedalieri.
"""

from pathlib import Path

from .common import Pipeline, PipelineResource

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DEST_DIR = BASE_DIR / "datasets" / "raw" / "ministero_salute"


MIN_SALUTE_RESOURCES: list[PipelineResource] = [
    # --- SDO Rapporto annuale ---
    PipelineResource(
        resource_id="SDO_RAPPORTO_2023",
        url="https://www.salute.gov.it/imgs/C_17_pubblicazioni_3378_allegato.pdf",
        filename="Rapporto_SDO_2023.pdf",
        title="Ministero Salute - Rapporto annuale SDO 2023",
        year=2024, frequency="static", category="sdo", subdir="sdo",
    ),
    PipelineResource(
        resource_id="SDO_RAPPORTO_2024",
        url="https://www.salute.gov.it/imgs/C_17_pubblicazioni_3450_allegato.pdf",
        filename="Rapporto_SDO_2024.pdf",
        title="Ministero Salute - Rapporto annuale SDO 2024",
        year=2025, frequency="annual", category="sdo", subdir="sdo",
    ),
    # --- Open Data SDO ---
    PipelineResource(
        resource_id="SDO_OPENDATA_ETA_SESSO",
        url="https://www.dati.salute.gov.it/imgs/C_17_dataset_19_0_upFile.csv",
        filename="OpenData_SDO_eta_sesso.csv",
        title="Open Data - SDO per fasce di eta e sesso",
        frequency="annual", category="opendata_sdo", subdir="opendata",
        min_size_bytes=5000,
    ),
    PipelineResource(
        resource_id="SDO_OPENDATA_DIMISSIONI",
        url="https://www.dati.salute.gov.it/imgs/C_17_dataset_20_0_upFile.csv",
        filename="OpenData_SDO_tipologia_dimissione.csv",
        title="Open Data - SDO per tipologia dimissione",
        frequency="annual", category="opendata_sdo", subdir="opendata",
        min_size_bytes=5000,
    ),
    # --- Annuario statistico SSN ---
    PipelineResource(
        resource_id="ANNUARIO_SSN_2022",
        url="https://www.salute.gov.it/imgs/C_17_pubblicazioni_3280_allegato.pdf",
        filename="Annuario_Statistico_SSN_2022.pdf",
        title="Ministero Salute - Annuario Statistico SSN 2022",
        year=2024, frequency="annual", category="annuario", subdir="annuario",
    ),
]


PIPELINE = Pipeline(
    pipeline_id="ministero_salute",
    name="Ministero della Salute - SDO, Open Data, Annuario",
    dest_dir=DEST_DIR,
    resources=MIN_SALUTE_RESOURCES,
    description="Dataset ospedalieri e rapporti annuali del Ministero della Salute",
)
