"""
Pipeline Osservatorio Nazionale sulla Salute nelle Regioni Italiane.
"""

from pathlib import Path

from .common import Pipeline, PipelineResource

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DEST_DIR = BASE_DIR / "datasets" / "raw" / "osservatorio_salute"


OSS_SALUTE_RESOURCES: list[PipelineResource] = [
    PipelineResource(
        resource_id="OSS_SALUTE_2022",
        url="https://osservatoriosullasalute.it/wp-content/uploads/2022/05/Rapporto-Osservasalute-2022.pdf",
        filename="Rapporto_Osservasalute_2022.pdf",
        title="Osservatorio Nazionale sulla Salute - Rapporto 2022",
        year=2022, frequency="static", category="rapporto_annuale",
    ),
    PipelineResource(
        resource_id="OSS_SALUTE_2023",
        url="https://osservatoriosullasalute.it/wp-content/uploads/2023/05/Rapporto-Osservasalute-2023.pdf",
        filename="Rapporto_Osservasalute_2023.pdf",
        title="Osservatorio Nazionale sulla Salute - Rapporto 2023",
        year=2023, frequency="static", category="rapporto_annuale",
    ),
    PipelineResource(
        resource_id="OSS_SALUTE_2024",
        url="https://osservatoriosullasalute.it/wp-content/uploads/2024/05/Rapporto-Osservasalute-2024.pdf",
        filename="Rapporto_Osservasalute_2024.pdf",
        title="Osservatorio Nazionale sulla Salute - Rapporto 2024",
        year=2024, frequency="annual", category="rapporto_annuale",
    ),
    PipelineResource(
        resource_id="OSS_SALUTE_2025",
        url="https://osservatoriosullasalute.it/wp-content/uploads/2025/05/Rapporto-Osservasalute-2025.pdf",
        filename="Rapporto_Osservasalute_2025.pdf",
        title="Osservatorio Nazionale sulla Salute - Rapporto 2025",
        year=2025, frequency="annual", category="rapporto_annuale",
    ),
]


PIPELINE = Pipeline(
    pipeline_id="osservatorio_salute",
    name="Osservatorio Nazionale sulla Salute nelle Regioni Italiane",
    dest_dir=DEST_DIR,
    resources=OSS_SALUTE_RESOURCES,
    description="Rapporti annuali Osservasalute (Universita Cattolica)",
)
