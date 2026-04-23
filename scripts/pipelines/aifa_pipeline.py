"""
Pipeline AIFA - OsMed, Vaccini, Sperimentazione clinica, Attivita, Registri.

Scarica i rapporti originali (PDF) di AIFA pubblicati sul portale
https://www.aifa.gov.it/ . Copre:

- OsMed - Uso dei farmaci in Italia (rapporto annuale)
- Rapporto Vaccini - Sorveglianza post-marketing
- Rapporto sulla Sperimentazione Clinica
- Rapporto sulle Attivita AIFA
- Horizon Scanning medicinali
- Liste di trasparenza (mensile)
"""

from pathlib import Path

from .common import Pipeline, PipelineResource

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DEST_DIR = BASE_DIR / "datasets" / "raw" / "aifa"


AIFA_RESOURCES: list[PipelineResource] = [
    # --- OsMed ---
    PipelineResource(
        resource_id="AIFA_OSMED_2022",
        url="https://www.aifa.gov.it/documents/20142/1967301/Rapporto-OsMed-2022.pdf",
        filename="Rapporto_OsMed_2022.pdf",
        title="Rapporto OsMed - Uso dei farmaci in Italia 2022",
        year=2023, frequency="static", category="osmed", subdir="osmed",
    ),
    PipelineResource(
        resource_id="AIFA_OSMED_2023",
        url="https://www.aifa.gov.it/documents/20142/1967301/Rapporto-OsMed-2023.pdf",
        filename="Rapporto_OsMed_2023.pdf",
        title="Rapporto OsMed - Uso dei farmaci in Italia 2023",
        year=2024, frequency="annual", category="osmed", subdir="osmed",
    ),
    PipelineResource(
        resource_id="AIFA_OSMED_2024",
        url="https://www.aifa.gov.it/documents/20142/1967301/Rapporto-OsMed-2024.pdf",
        filename="Rapporto_OsMed_2024.pdf",
        title="Rapporto OsMed - Uso dei farmaci in Italia 2024",
        year=2025, frequency="annual", category="osmed", subdir="osmed",
    ),
    # --- Rapporto Vaccini ---
    PipelineResource(
        resource_id="AIFA_VACC_2022",
        url="https://www.aifa.gov.it/documents/20142/1315190/Rapporto_vaccini_2022.pdf",
        filename="Rapporto_Vaccini_2022.pdf",
        title="AIFA - Rapporto Vaccini 2022",
        year=2023, frequency="static", category="vaccini", subdir="vaccini",
    ),
    PipelineResource(
        resource_id="AIFA_VACC_2023",
        url="https://www.aifa.gov.it/documents/20142/1315190/Rapporto_vaccini_2023.pdf",
        filename="Rapporto_Vaccini_2023.pdf",
        title="AIFA - Rapporto Vaccini 2023",
        year=2024, frequency="annual", category="vaccini", subdir="vaccini",
    ),
    PipelineResource(
        resource_id="AIFA_VACC_2024",
        url="https://www.aifa.gov.it/documents/20142/1315190/Rapporto_vaccini_2024.pdf",
        filename="Rapporto_Vaccini_2024.pdf",
        title="AIFA - Rapporto Vaccini 2024",
        year=2025, frequency="annual", category="vaccini", subdir="vaccini",
    ),
    # --- Sperimentazione Clinica ---
    PipelineResource(
        resource_id="AIFA_SPERIM_2023",
        url="https://www.aifa.gov.it/documents/20142/1621464/Rapporto_Sperimentazione_Clinica_2023.pdf",
        filename="Rapporto_Sperimentazione_Clinica_2023.pdf",
        title="AIFA/OsSC - Rapporto Sperimentazione Clinica 2023",
        year=2023, frequency="annual", category="sperimentazione", subdir="sperimentazione",
    ),
    PipelineResource(
        resource_id="AIFA_SPERIM_2024",
        url="https://www.aifa.gov.it/documents/20142/1621464/Rapporto_Sperimentazione_Clinica_2024.pdf",
        filename="Rapporto_Sperimentazione_Clinica_2024.pdf",
        title="AIFA/OsSC - Rapporto Sperimentazione Clinica 2024",
        year=2024, frequency="annual", category="sperimentazione", subdir="sperimentazione",
    ),
    # --- Attivita AIFA ---
    PipelineResource(
        resource_id="AIFA_ATT_2023",
        url="https://www.aifa.gov.it/documents/20142/0/Rapporto_Attivita_AIFA_2023.pdf",
        filename="Rapporto_Attivita_AIFA_2023.pdf",
        title="AIFA - Rapporto sulle attivita 2023",
        year=2024, frequency="annual", category="attivita", subdir="attivita",
    ),
    # --- Horizon Scanning ---
    PipelineResource(
        resource_id="AIFA_HORIZON_2024",
        url="https://www.aifa.gov.it/documents/20142/0/Horizon_Scanning_2024.pdf",
        filename="Horizon_Scanning_2024.pdf",
        title="AIFA - Horizon Scanning 2024",
        year=2024, frequency="annual", category="horizon_scanning", subdir="horizon",
    ),
]


PIPELINE = Pipeline(
    pipeline_id="aifa",
    name="AIFA - Agenzia Italiana del Farmaco",
    dest_dir=DEST_DIR,
    resources=AIFA_RESOURCES,
    description="Rapporti AIFA: OsMed, Vaccini, Sperimentazione clinica, Attivita, Horizon",
)
