"""
Pipeline comparatori internazionali - OECD, Eurostat, WHO GHED, KFF,
Commonwealth Fund, NAIC, EU Country Health Profile.
"""

from pathlib import Path

from .common import Pipeline, PipelineResource

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DEST_DIR = BASE_DIR / "datasets" / "raw" / "internazionale"


INTL_RESOURCES: list[PipelineResource] = [
    # --- OECD Health at a Glance ---
    PipelineResource(
        resource_id="OECD_HAAG_2023",
        url="https://www.oecd.org/health/health-at-a-glance/Health-at-a-Glance-2023.pdf",
        filename="OECD_Health_at_a_Glance_2023.pdf",
        title="OECD - Health at a Glance 2023",
        year=2023, frequency="static", category="oecd", subdir="oecd",
    ),
    PipelineResource(
        resource_id="OECD_HSI_ITA_2024",
        url="https://www.oecd.org/italy/health-systems-at-a-glance-italy-2024.pdf",
        filename="OECD_Health_Systems_Italy_2024.pdf",
        title="OECD - Health Systems at a Glance: Italy 2024",
        year=2024, frequency="biennial", category="oecd", subdir="oecd",
    ),
    # --- Eurostat ---
    PipelineResource(
        resource_id="EUROSTAT_SHA_LATEST",
        url="https://ec.europa.eu/eurostat/databrowser/view/hlth_sha11_hc/default/table?lang=en",
        filename="Eurostat_SHA_HC_index.html",
        title="Eurostat - System of Health Accounts (indice tabella)",
        frequency="annual", category="eurostat", subdir="eurostat",
        min_size_bytes=500,
    ),
    # --- WHO GHED ---
    PipelineResource(
        resource_id="WHO_GHED_DATA",
        url="https://apps.who.int/nha/database/DocumentationCentre/GetFile/62380571/en",
        filename="WHO_GHED_Indicators.xlsx",
        title="WHO - Global Health Expenditure Database (indicators XLSX)",
        frequency="annual", category="who_ghed", subdir="who_ghed",
        min_size_bytes=5000,
    ),
    # --- EU Country Health Profile Italy ---
    PipelineResource(
        resource_id="EU_CHP_ITALY_2023",
        url="https://health.ec.europa.eu/system/files/2023-12/2023_chp_it_italian.pdf",
        filename="EU_Country_Health_Profile_Italy_2023.pdf",
        title="Commissione UE/OECD - State of Health in the EU: Italy 2023",
        year=2023, frequency="biennial", category="eu_chp", subdir="eu",
    ),
    # --- Commonwealth Fund ---
    PipelineResource(
        resource_id="CWF_MIRROR_2024",
        url="https://www.commonwealthfund.org/sites/default/files/2024-09/Blumenthal_mirror_mirror_2024.pdf",
        filename="Commonwealth_Fund_Mirror_Mirror_2024.pdf",
        title="Commonwealth Fund - Mirror Mirror 2024",
        year=2024, frequency="biennial", category="cwf", subdir="commonwealth",
    ),
    # --- KFF ---
    PipelineResource(
        resource_id="KFF_EHBS_2024",
        url="https://files.kff.org/attachment/Report-Employer-Health-Benefits-Survey-2024.pdf",
        filename="KFF_Employer_Health_Benefits_2024.pdf",
        title="KFF - Employer Health Benefits Survey 2024",
        year=2024, frequency="annual", category="kff", subdir="kff",
    ),
    # --- NAIC ---
    PipelineResource(
        resource_id="NAIC_2024",
        url="https://content.naic.org/sites/default/files/publication-hlt-lr-health-insurance-industry-analysis-report.pdf",
        filename="NAIC_Health_Insurance_Industry_Analysis_2024.pdf",
        title="NAIC - Health Insurance Industry Analysis Report 2024",
        year=2024, frequency="annual", category="naic", subdir="naic",
    ),
]


PIPELINE = Pipeline(
    pipeline_id="international",
    name="Comparatori internazionali (OECD, Eurostat, WHO, KFF, CWF, NAIC, EU CHP)",
    dest_dir=DEST_DIR,
    resources=INTL_RESOURCES,
    description="Benchmark internazionali su spesa, performance e copertura sanitaria",
)
