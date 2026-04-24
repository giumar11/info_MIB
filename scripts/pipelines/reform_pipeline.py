"""
Pipeline riforme strutturali SSN - DM 77/2022, DM 70/2015, PNRR Missione 6.
"""

from pathlib import Path

from .common import Pipeline, PipelineResource

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DEST_DIR = BASE_DIR / "datasets" / "raw" / "riforme"


REFORM_RESOURCES: list[PipelineResource] = [
    # DM 77/2022 - gia presente come PDF, mantengo per completezza manifest
    PipelineResource(
        resource_id="DM_77_2022",
        url="https://www.gazzettaufficiale.it/do/atto/serie_generale/caricaPdf?cdimg=22A0371800100010110001&dgu=2022-06-22&art.dataPubblicazioneGazzetta=2022-06-22&art.codiceRedazionale=22A03718&art.num=1&art.tiposerie=SG",
        filename="DM_77_2022_GazzettaUfficiale.pdf",
        title="DM 77/2022 - Assistenza territoriale (Gazzetta Ufficiale)",
        year=2022, frequency="static", category="dm77", subdir="dm77_2022",
    ),
    # DM 70/2015
    PipelineResource(
        resource_id="DM_70_2015",
        url="https://www.gazzettaufficiale.it/do/atto/serie_generale/caricaPdf?cdimg=15A0422700100010110001&dgu=2015-06-04&art.dataPubblicazioneGazzetta=2015-06-04&art.codiceRedazionale=15A04227&art.num=1&art.tiposerie=SG",
        filename="DM_70_2015_GazzettaUfficiale.pdf",
        title="DM 70/2015 - Standard Ospedalieri (Gazzetta Ufficiale)",
        year=2015, frequency="static", category="dm70", subdir="dm70_2015",
    ),
    # PNRR Missione 6 - testo ufficiale
    PipelineResource(
        resource_id="PNRR_M6_TESTO",
        url="https://www.governo.it/sites/governo.it/files/PNRR.pdf",
        filename="PNRR_Italia_testo_completo.pdf",
        title="Piano Nazionale di Ripresa e Resilienza - testo",
        year=2021, frequency="static", category="pnrr", subdir="pnrr_m6",
    ),
    PipelineResource(
        resource_id="PNRR_M6_MONITOR_2024",
        url="https://www.italiadomani.gov.it/content/dam/sogei-ng/documenti/Relazione%20annuale%20al%20Parlamento%20PNRR%202024.pdf",
        filename="PNRR_Relazione_Parlamento_2024.pdf",
        title="PNRR - Relazione annuale al Parlamento 2024",
        year=2024, frequency="annual", category="pnrr", subdir="pnrr_m6",
    ),
]


PIPELINE = Pipeline(
    pipeline_id="riforme",
    name="Riforme strutturali SSN - DM 77, DM 70, PNRR M6",
    dest_dir=DEST_DIR,
    resources=REFORM_RESOURCES,
    description="Testi normativi di riforma e monitoraggio attuativo",
)
