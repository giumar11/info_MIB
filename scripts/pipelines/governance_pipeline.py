"""
Pipeline Governance SSN - PNE, LEA/NSG, PNGLA, OpenBDAP.

Scarica i rapporti istituzionali AGENAS, Ministero della Salute e RGS/MEF
relativi a performance, qualita, liste d'attesa e finanza pubblica sanitaria.
"""

from pathlib import Path

from .common import Pipeline, PipelineResource

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DEST_DIR = BASE_DIR / "datasets" / "raw" / "governance"


GOVERNANCE_RESOURCES: list[PipelineResource] = [
    # --- PNE - Programma Nazionale Esiti ---
    PipelineResource(
        resource_id="PNE_2023",
        url="https://pne.agenas.it/assets/documentation/report/Report_PNE_2023.pdf",
        filename="Report_PNE_2023.pdf",
        title="AGENAS - Programma Nazionale Esiti 2023",
        year=2023, frequency="static", category="pne", subdir="pne",
    ),
    PipelineResource(
        resource_id="PNE_2024",
        url="https://pne.agenas.it/assets/documentation/report/Report_PNE_2024.pdf",
        filename="Report_PNE_2024.pdf",
        title="AGENAS - Programma Nazionale Esiti 2024",
        year=2024, frequency="annual", category="pne", subdir="pne",
    ),
    # --- LEA ---
    PipelineResource(
        resource_id="LEA_2022",
        url="https://www.salute.gov.it/imgs/C_17_pubblicazioni_3329_allegato.pdf",
        filename="Monitoraggio_LEA_2022.pdf",
        title="Ministero Salute - Monitoraggio LEA 2022",
        year=2024, frequency="static", category="lea", subdir="lea_nsg",
    ),
    PipelineResource(
        resource_id="LEA_2023",
        url="https://www.salute.gov.it/imgs/C_17_pubblicazioni_3400_allegato.pdf",
        filename="Monitoraggio_LEA_2023.pdf",
        title="Ministero Salute - Monitoraggio LEA 2023",
        year=2025, frequency="annual", category="lea", subdir="lea_nsg",
    ),
    # --- PNGLA (Liste d'attesa) ---
    PipelineResource(
        resource_id="PNGLA_MONITOR_2024",
        url="https://pnla.agenas.it/assets/documentation/report_monitoraggio_2024.pdf",
        filename="Report_Monitoraggio_PNGLA_2024.pdf",
        title="AGENAS - Monitoraggio Liste d'Attesa 2024",
        year=2024, frequency="quarterly", category="liste_attesa", subdir="pngla",
    ),
    # --- OpenBDAP ---
    PipelineResource(
        resource_id="BDAP_SSN_CONTO_ECONOMICO",
        url="https://openbdap.rgs.mef.gov.it/opendata/SSN_ConEco_aggregato.csv",
        filename="OpenBDAP_SSN_ContoEconomico.csv",
        title="OpenBDAP - Conto Economico SSN aggregato",
        frequency="quarterly", category="bdap", subdir="openbdap",
    ),
]


PIPELINE = Pipeline(
    pipeline_id="governance",
    name="Governance SSN - PNE, LEA, PNGLA, OpenBDAP",
    dest_dir=DEST_DIR,
    resources=GOVERNANCE_RESOURCES,
    description="Performance, qualita, liste d'attesa e finanza pubblica SSN",
)
