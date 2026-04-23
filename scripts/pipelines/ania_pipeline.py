"""
Pipeline di enrichment ANIA + IVASS.

Scarica i rapporti originali dell'Associazione Nazionale Imprese Assicuratrici
(ANIA) e della Vigilanza IVASS.

I link puntano alle URL di download diretto dei PDF pubblicati sui rispettivi
siti istituzionali. Il set coperto include:

- Rapporto Annuale "L'Assicurazione Italiana" (serie 2019-2025)
- Italian Insurance (versione inglese)
- ANIA Trends (premi mensili)
- Osservatorio Sanita ANIA
- ANIA Welfare / Fondi Sanitari
- Position paper su Fondi Sanitari Integrativi
- ANIA Fondazione - Vittime della strada
- IVASS Relazione Annuale
- IVASS Statistiche trimestrali

I file vengono salvati in `datasets/raw/ania/` (ANIA) e
`datasets/raw/ania/ivass/` (IVASS). Il manifest SHA-256 e aggiornato in
`datasets/raw/ania/manifest.json`.
"""

from pathlib import Path

from .common import Pipeline, PipelineResource

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DEST_DIR = BASE_DIR / "datasets" / "raw" / "ania"


ANIA_RESOURCES: list[PipelineResource] = [
    # --- Rapporto Annuale ANIA "L'Assicurazione Italiana" ---
    PipelineResource(
        resource_id="ANIA_RAPP_2019",
        url="https://www.ania.it/documents/35135/0/Assicurazione+Italiana+2018-2019.pdf",
        filename="Rapporto_ANIA_Assicurazione_Italiana_2018_2019.pdf",
        title="L'Assicurazione Italiana 2018-2019",
        year=2019,
        frequency="annual",
        category="rapporto_annuale",
        subdir="pdf",
    ),
    PipelineResource(
        resource_id="ANIA_RAPP_2020",
        url="https://www.ania.it/documents/35135/0/Assicurazione+Italiana+2019-2020.pdf",
        filename="Rapporto_ANIA_Assicurazione_Italiana_2019_2020.pdf",
        title="L'Assicurazione Italiana 2019-2020",
        year=2020,
        frequency="annual",
        category="rapporto_annuale",
        subdir="pdf",
    ),
    PipelineResource(
        resource_id="ANIA_RAPP_2021",
        url="https://www.ania.it/documents/35135/0/Assicurazione+Italiana+2020-2021.pdf",
        filename="Rapporto_ANIA_Assicurazione_Italiana_2020_2021.pdf",
        title="L'Assicurazione Italiana 2020-2021",
        year=2021,
        frequency="annual",
        category="rapporto_annuale",
        subdir="pdf",
    ),
    PipelineResource(
        resource_id="ANIA_RAPP_2022",
        url="https://www.ania.it/documents/35135/0/Assicurazione+Italiana+2021-2022.pdf",
        filename="Rapporto_ANIA_Assicurazione_Italiana_2021_2022.pdf",
        title="L'Assicurazione Italiana 2021-2022",
        year=2022,
        frequency="annual",
        category="rapporto_annuale",
        subdir="pdf",
    ),
    PipelineResource(
        resource_id="ANIA_RAPP_2023",
        url="https://www.ania.it/documents/35135/0/Assicurazione+Italiana+2022-2023.pdf",
        filename="Rapporto_ANIA_Assicurazione_Italiana_2022_2023.pdf",
        title="L'Assicurazione Italiana 2022-2023",
        year=2023,
        frequency="annual",
        category="rapporto_annuale",
        subdir="pdf",
    ),
    PipelineResource(
        resource_id="ANIA_RAPP_2024",
        url="https://www.ania.it/documents/35135/0/Assicurazione+Italiana+2023-2024.pdf",
        filename="Rapporto_ANIA_Assicurazione_Italiana_2023_2024.pdf",
        title="L'Assicurazione Italiana 2023-2024",
        year=2024,
        frequency="annual",
        category="rapporto_annuale",
        subdir="pdf",
    ),
    PipelineResource(
        resource_id="ANIA_RAPP_2025",
        url="https://www.ania.it/documents/35135/0/Assicurazione+Italiana+2024-2025.pdf",
        filename="Rapporto_ANIA_Assicurazione_Italiana_2024_2025.pdf",
        title="L'Assicurazione Italiana 2024-2025",
        year=2025,
        frequency="annual",
        category="rapporto_annuale",
        subdir="pdf",
    ),
    # --- Italian Insurance (English) ---
    PipelineResource(
        resource_id="ANIA_ITA_INS_2024",
        url="https://www.ania.it/documents/35135/0/Italian+Insurance+2023-2024.pdf",
        filename="Italian_Insurance_2023_2024.pdf",
        title="Italian Insurance in 2023-2024",
        year=2024,
        frequency="annual",
        category="rapporto_annuale",
        subcategory="english",
        subdir="pdf",
    ),
    PipelineResource(
        resource_id="ANIA_ITA_INS_2025",
        url="https://www.ania.it/documents/35135/0/Italian+Insurance+2024-2025.pdf",
        filename="Italian_Insurance_2024_2025.pdf",
        title="Italian Insurance in 2024-2025",
        year=2025,
        frequency="annual",
        category="rapporto_annuale",
        subcategory="english",
        subdir="pdf",
    ),
    # --- ANIA Trends (premi mensili) ---
    PipelineResource(
        resource_id="ANIA_TRENDS_LATEST",
        url="https://www.ania.it/documents/35135/0/ANIA+Trends+-+Premi+lavoro+diretto+italiano.pdf",
        filename="ANIA_Trends_Premi_Lavoro_Diretto.pdf",
        title="ANIA Trends - Premi del lavoro diretto italiano",
        frequency="monthly",
        category="trends",
        subdir="pdf",
    ),
    # --- Osservatorio Sanita ANIA ---
    PipelineResource(
        resource_id="ANIA_SANITA_2024",
        url="https://www.ania.it/documents/35135/0/Osservatorio+Sanita+2024.pdf",
        filename="ANIA_Osservatorio_Sanita_2024.pdf",
        title="Osservatorio Sanita ANIA - Edizione 2024",
        year=2024,
        frequency="annual",
        category="sanita",
        subdir="pdf",
    ),
    PipelineResource(
        resource_id="ANIA_SANITA_2025",
        url="https://www.ania.it/documents/35135/0/Osservatorio+Sanita+2025.pdf",
        filename="ANIA_Osservatorio_Sanita_2025.pdf",
        title="Osservatorio Sanita ANIA - Edizione 2025",
        year=2025,
        frequency="annual",
        category="sanita",
        subdir="pdf",
    ),
    # --- Welfare ---
    PipelineResource(
        resource_id="ANIA_WELFARE_2024",
        url="https://www.ania.it/documents/35135/0/ANIA+Welfare+Previdenza+Complementare+e+Salute+2024.pdf",
        filename="ANIA_Welfare_Previdenza_Salute_2024.pdf",
        title="ANIA Welfare - Previdenza complementare e salute 2024",
        year=2024,
        frequency="annual",
        category="welfare",
        subdir="pdf",
    ),
    # --- Position Papers ---
    PipelineResource(
        resource_id="ANIA_POSPAPER_FONDI_SAN",
        url="https://www.ania.it/documents/35135/0/Position+Paper+Fondi+Sanitari+Integrativi.pdf",
        filename="ANIA_Position_Paper_Fondi_Sanitari_Integrativi.pdf",
        title="ANIA Position Paper - Fondi Sanitari Integrativi",
        frequency="periodic",
        category="position_paper",
        subdir="pdf",
    ),
    # --- ANIA Fondazione ---
    PipelineResource(
        resource_id="ANIA_FOND_VITTIME_2024",
        url="https://www.fondazioneania.it/wp-content/uploads/2024/12/Vittime-della-strada-2024.pdf",
        filename="ANIA_Fondazione_Vittime_Strada_2024.pdf",
        title="ANIA Fondazione - Rapporto vittime della strada 2024",
        year=2024,
        frequency="annual",
        category="fondazione",
        subdir="pdf",
    ),
    # --- IVASS ---
    PipelineResource(
        resource_id="IVASS_RELAZIONE_2023",
        url="https://www.ivass.it/pubblicazioni-e-statistiche/pubblicazioni/relazione-annuale/2024/relazione/Relazione-annuale-2023.pdf",
        filename="IVASS_Relazione_Annuale_2023.pdf",
        title="IVASS - Relazione Annuale sull'attivita svolta (anno 2023)",
        year=2024,
        frequency="annual",
        category="ivass",
        subdir="ivass",
    ),
    PipelineResource(
        resource_id="IVASS_RELAZIONE_2024",
        url="https://www.ivass.it/pubblicazioni-e-statistiche/pubblicazioni/relazione-annuale/2025/relazione/Relazione-annuale-2024.pdf",
        filename="IVASS_Relazione_Annuale_2024.pdf",
        title="IVASS - Relazione Annuale sull'attivita svolta (anno 2024)",
        year=2025,
        frequency="annual",
        category="ivass",
        subdir="ivass",
    ),
    PipelineResource(
        resource_id="IVASS_BOLLETTINO_STAT",
        url="https://www.ivass.it/pubblicazioni-e-statistiche/statistiche/bollettino/2025/index.html",
        filename="IVASS_Bollettino_Statistico_Index.html",
        title="IVASS - Bollettino statistico (indice ultima edizione)",
        frequency="quarterly",
        category="ivass",
        subcategory="bollettino",
        subdir="ivass",
        min_size_bytes=500,
    ),
]


PIPELINE = Pipeline(
    pipeline_id="ania",
    name="ANIA / IVASS - Settore assicurativo",
    dest_dir=DEST_DIR,
    resources=ANIA_RESOURCES,
    description="Rapporti ANIA e IVASS sull'assicurazione italiana e i fondi sanitari",
)
