"""
Pipeline GIMBE - Rapporti annuali, Osservatorio, Mobilita, PNRR, COVID.

Copre la collezione gia parzialmente scaricata in
`datasets/raw/gimbe/pdf/` e la porta a aggiornamento continuo. La frequenza
per l'Osservatorio (report tematici) e 'monthly', per il rapporto annuale
sul SSN e 'annual'.
"""

from pathlib import Path

from .common import Pipeline, PipelineResource

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DEST_DIR = BASE_DIR / "datasets" / "raw" / "gimbe" / "pdf"


GIMBE_RESOURCES: list[PipelineResource] = [
    # Rapporti annuali sul SSN (1-8)
    PipelineResource(
        resource_id="GIMBE_RAPP_1_2016",
        url="https://salviamo-ssn.it/var/contenuti/1_Rapporto_GIMBE.pdf",
        filename="1_Rapporto_GIMBE_SSN_2016.pdf",
        title="1 Rapporto GIMBE sul SSN",
        year=2016, frequency="static", category="rapporto_annuale",
    ),
    PipelineResource(
        resource_id="GIMBE_RAPP_2_2017",
        url="https://salviamo-ssn.it/var/contenuti/2_Rapporto_GIMBE.pdf",
        filename="2_Rapporto_GIMBE_SSN_2017.pdf",
        title="2 Rapporto GIMBE sul SSN",
        year=2017, frequency="static", category="rapporto_annuale",
    ),
    PipelineResource(
        resource_id="GIMBE_RAPP_3_2018",
        url="https://salviamo-ssn.it/var/contenuti/3_Rapporto_GIMBE.pdf",
        filename="3_Rapporto_GIMBE_SSN_2018.pdf",
        title="3 Rapporto GIMBE sul SSN",
        year=2018, frequency="static", category="rapporto_annuale",
    ),
    PipelineResource(
        resource_id="GIMBE_RAPP_4_2019",
        url="https://www.salviamo-ssn.it/var/contenuti/4_Rapporto_GIMBE_Sostenibilita_SSN.pdf",
        filename="4_Rapporto_GIMBE_SSN_2019.pdf",
        title="4 Rapporto GIMBE sul SSN",
        year=2019, frequency="static", category="rapporto_annuale",
    ),
    PipelineResource(
        resource_id="GIMBE_RAPP_5_2022",
        url="https://www.quotidianosanita.it/allegati/allegato1665475004.pdf",
        filename="5_Rapporto_GIMBE_SSN_2022.pdf",
        title="5 Rapporto GIMBE sul SSN",
        year=2022, frequency="static", category="rapporto_annuale",
    ),
    PipelineResource(
        resource_id="GIMBE_RAPP_6_2023",
        url="https://www.quotidianosanita.it/allegati/allegato1696924905.pdf",
        filename="6_Rapporto_GIMBE_SSN_2023.pdf",
        title="6 Rapporto GIMBE sul SSN",
        year=2023, frequency="static", category="rapporto_annuale",
    ),
    PipelineResource(
        resource_id="GIMBE_RAPP_7_2024",
        url="https://www.camera.it/temiap/2024/10/09/OCD177-7603.pdf",
        filename="7_Rapporto_GIMBE_SSN_2024.pdf",
        title="7 Rapporto GIMBE sul SSN",
        year=2024, frequency="static", category="rapporto_annuale",
    ),
    PipelineResource(
        resource_id="GIMBE_RAPP_8_2025",
        url="https://www.salviamo-ssn.it/var/contenuti/8_Rapporto_GIMBE_SSN.pdf",
        filename="8_Rapporto_GIMBE_SSN_2025.pdf",
        title="8 Rapporto GIMBE sul SSN",
        year=2025, frequency="annual", category="rapporto_annuale",
    ),
    # Osservatorio (report tematici)
    PipelineResource(
        resource_id="GIMBE_OSS_2023_01",
        url="https://www.gimbe.org/osservatorio/Report_Osservatorio_GIMBE_2023.01_Regionalismo_differenziato_in_sanita.pdf",
        filename="Report_Osservatorio_GIMBE_2023.01_Regionalismo_differenziato.pdf",
        title="Osservatorio GIMBE 1/2023 - Regionalismo differenziato",
        year=2023, frequency="static", category="osservatorio",
    ),
    PipelineResource(
        resource_id="GIMBE_OSS_2023_04",
        url="https://www.gimbe.org/osservatorio/Report_Osservatorio_GIMBE_2023.04_Ruolo_filiera_healthcare_nel_SSN.pdf",
        filename="Report_Osservatorio_GIMBE_2023.04_Filiera_healthcare.pdf",
        title="Osservatorio GIMBE 4/2023 - Filiera healthcare nel SSN",
        year=2023, frequency="static", category="osservatorio",
    ),
    PipelineResource(
        resource_id="GIMBE_OSS_2024_01",
        url="https://www.gimbe.org/osservatorio/Report_Osservatorio_GIMBE_2024.01_Mobilita_sanitaria_2021.pdf",
        filename="Report_Osservatorio_GIMBE_2024.01_Mobilita_sanitaria_2021.pdf",
        title="Osservatorio GIMBE 1/2024 - Mobilita sanitaria 2021",
        year=2024, frequency="static", category="mobilita",
    ),
    PipelineResource(
        resource_id="GIMBE_OSS_2024_02",
        url="https://documenti.camera.it/leg19/documentiAcquisiti/COM01/Audizioni/leg19.com01.Audizioni.Memoria.PUBBLICO.ideGes.34026.26-03-2024-11-34-12.951.pdf",
        filename="Report_Osservatorio_GIMBE_2024.02_Autonomia_differenziata.pdf",
        title="Osservatorio GIMBE 2/2024 - Autonomia differenziata",
        year=2024, frequency="static", category="osservatorio",
    ),
    PipelineResource(
        resource_id="GIMBE_OSS_2024_03",
        url="https://www.gimbe.org/osservatorio/Report_Osservatorio_GIMBE_2024.03_Scuole_che_promuovono_salute.pdf",
        filename="Report_Osservatorio_GIMBE_2024.03_Scuole_promuovono_salute.pdf",
        title="Osservatorio GIMBE 3/2024 - Scuole che promuovono salute",
        year=2024, frequency="static", category="osservatorio",
    ),
    PipelineResource(
        resource_id="GIMBE_OSS_2025_01",
        url="https://www.avis.it/wp-content/uploads/2025/03/Report_Osservatorio_GIMBE_2025.01_Mobilita_sanitaria_2022.pdf",
        filename="Report_Osservatorio_GIMBE_2025.01_Mobilita_sanitaria_2022.pdf",
        title="Osservatorio GIMBE 1/2025 - Mobilita sanitaria 2022",
        year=2025, frequency="static", category="mobilita",
    ),
    PipelineResource(
        resource_id="GIMBE_OSS_2025_02",
        url="https://salviamo-ssn.it/var/contenuti/Report_Osservatorio_GIMBE_2025.02_Spesa_sanitaria_privata_2023.pdf",
        filename="Report_Osservatorio_GIMBE_2025.02_Spesa_sanitaria_privata_2023.pdf",
        title="Osservatorio GIMBE 2/2025 - Spesa sanitaria privata 2023",
        year=2025, frequency="monthly", category="osservatorio",
    ),
]


PIPELINE = Pipeline(
    pipeline_id="gimbe",
    name="GIMBE - Rapporti SSN e Osservatorio",
    dest_dir=DEST_DIR,
    resources=GIMBE_RESOURCES,
    description="Fondazione GIMBE - Rapporti annuali sul SSN, Osservatorio tematico, Mobilita, PNRR",
)
