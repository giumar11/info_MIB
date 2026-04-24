"""
Pipeline Societa Scientifiche (italiane + europee).

Scarica i white book, report annuali e registri delle principali societa
scientifiche coinvolte nei PDTA e nell'analisi delle patologie complesse.
"""

from pathlib import Path

from .common import Pipeline, PipelineResource

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DEST_DIR = BASE_DIR / "datasets" / "raw" / "societa_scientifiche"


SCIENTIFIC_RESOURCES: list[PipelineResource] = [
    # --- Italiane ---
    PipelineResource(
        resource_id="AIOM_NUMERI_CANCRO_2024",
        url="https://www.aiom.it/wp-content/uploads/2024/10/2024_NumeriCancro_operatori.pdf",
        filename="AIOM_Numeri_Cancro_Italia_2024.pdf",
        title="AIOM/AIRTUM - I numeri del cancro in Italia 2024",
        year=2024, frequency="annual", category="oncologia",
        subdir="italiane",
    ),
    PipelineResource(
        resource_id="AIRTUM_2023",
        url="https://www.registri-tumori.it/PDF/AIOM2023/Numeri_Cancro_Italia_2023.pdf",
        filename="AIRTUM_Numeri_Cancro_2023.pdf",
        title="AIRTUM - Rapporto 2023",
        year=2023, frequency="static", category="oncologia",
        subdir="italiane",
    ),
    PipelineResource(
        resource_id="SID_ANNUARIO_2024",
        url="https://www.siditalia.it/pdf/Annuario-Italian-Diabetes-Monitor-2024.pdf",
        filename="SID_Annuario_Diabete_2024.pdf",
        title="SID/AMD - Italian Diabetes Monitor 2024",
        year=2024, frequency="annual", category="diabete",
        subdir="italiane",
    ),
    PipelineResource(
        resource_id="SIN_RAPP_NEURO_2023",
        url="https://www.neuro.it/web/eventi/NEURO/docs/Rapporto_Malattie_Neurologiche_2023.pdf",
        filename="SIN_Malattie_Neurologiche_2023.pdf",
        title="SIN - Rapporto Malattie Neurologiche 2023",
        year=2023, frequency="static", category="neurologia",
        subdir="italiane",
    ),
    PipelineResource(
        resource_id="SIR_LIBRO_BIANCO_REUMA",
        url="https://www.reumatologia.it/cmssir/allegati/Libro-Bianco-Reumatologia.pdf",
        filename="SIR_Libro_Bianco_Reumatologia.pdf",
        title="SIR - Libro Bianco Reumatologia Italiana",
        frequency="periodic", category="reumatologia",
        subdir="italiane",
    ),
    PipelineResource(
        resource_id="AIPO_WHITEBOOK_PNEUMO",
        url="https://www.aiponet.it/images/stories/documenti/AIPO_WhiteBook_Pneumologia_Italiana.pdf",
        filename="AIPO_WhiteBook_Pneumologia.pdf",
        title="AIPO-ITS - White Book Pneumologia Italiana",
        frequency="periodic", category="pneumologia",
        subdir="italiane",
    ),
    PipelineResource(
        resource_id="RIDT_2023",
        url="https://ridt.sinitaly.org/wp-content/uploads/2024/06/RIDT_Report_2023.pdf",
        filename="RIDT_Report_2023.pdf",
        title="SIN-Nefrologia - Registro Italiano Dialisi e Trapianto 2023",
        year=2023, frequency="annual", category="nefrologia",
        subdir="italiane",
    ),
    PipelineResource(
        resource_id="SIP_RAPP_SALUTE_MENTALE_2024",
        url="https://www.psichiatria.it/wp-content/uploads/2024/10/Rapporto-Salute-Mentale-2024.pdf",
        filename="SIP_Salute_Mentale_2024.pdf",
        title="SIP - Rapporto Salute Mentale in Italia 2024",
        year=2024, frequency="annual", category="salute_mentale",
        subdir="italiane",
    ),
    # --- Europee ---
    PipelineResource(
        resource_id="ESC_CV_STATS_2023",
        url="https://www.escardio.org/static-file/Escardio/Media-center/press-releases/2023/European%20Cardiovascular%20Disease%20Statistics%202023.pdf",
        filename="ESC_CV_Statistics_2023.pdf",
        title="ESC/EHN - European Cardiovascular Disease Statistics 2023",
        year=2023, frequency="periodic", category="cardiologia",
        subdir="europee",
    ),
    PipelineResource(
        resource_id="ERA_REGISTRY_2023",
        url="https://www.era-online.org/wp-content/uploads/2024/07/ERA-Registry-Annual-Report-2023.pdf",
        filename="ERA_Registry_Annual_Report_2023.pdf",
        title="ERA Registry - Annual Report 2023",
        year=2023, frequency="annual", category="nefrologia",
        subdir="europee",
    ),
    PipelineResource(
        resource_id="ERS_WHITEBOOK",
        url="https://www.erswhitebook.org/files/public/Chapters/ERS_WhiteBook_Chapter1.pdf",
        filename="ERS_European_Lung_WhiteBook.pdf",
        title="ERS - European Lung White Book",
        frequency="periodic", category="pneumologia",
        subdir="europee",
    ),
]


PIPELINE = Pipeline(
    pipeline_id="scientific_societies",
    name="Societa scientifiche (italiane + europee)",
    dest_dir=DEST_DIR,
    resources=SCIENTIFIC_RESOURCES,
    description="White book, rapporti annuali e registri delle societa scientifiche",
)
