"""
Pipeline Orphanet / Orphadata - Malattie rare.

Scarica i dataset XML originali dal portale Orphadata.
"""

from pathlib import Path

from .common import Pipeline, PipelineResource

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DEST_DIR = BASE_DIR / "datasets" / "raw" / "orphanet"


ORPHANET_RESOURCES: list[PipelineResource] = [
    PipelineResource(
        resource_id="ORPHA_EPID_IT",
        url="https://www.orphadata.com/data/xml/it_product9_prev.xml",
        filename="orphadata_epidemiology_it.xml",
        title="Orphadata - Epidemiology dataset (italiano)",
        frequency="quarterly", category="epidemiology",
        min_size_bytes=50_000,
    ),
    PipelineResource(
        resource_id="ORPHA_NOMEN_IT",
        url="https://www.orphadata.com/data/xml/it_product1.xml",
        filename="orphadata_nomenclature_it.xml",
        title="Orphadata - Rare diseases nomenclature (italiano)",
        frequency="quarterly", category="nomenclature",
        min_size_bytes=100_000,
    ),
    PipelineResource(
        resource_id="ORPHA_CLASSIF_IT",
        url="https://www.orphadata.com/data/xml/it_product3.xml",
        filename="orphadata_classification_it.xml",
        title="Orphadata - Classification (italiano)",
        frequency="quarterly", category="classification",
        min_size_bytes=100_000,
    ),
    PipelineResource(
        resource_id="ORPHA_NATHIST_IT",
        url="https://www.orphadata.com/data/xml/it_product9_ages.xml",
        filename="orphadata_natural_history_it.xml",
        title="Orphadata - Natural history (ages of onset, inheritance)",
        frequency="quarterly", category="natural_history",
        min_size_bytes=50_000,
    ),
]


PIPELINE = Pipeline(
    pipeline_id="orphanet",
    name="Orphanet / Orphadata - Malattie rare",
    dest_dir=DEST_DIR,
    resources=ORPHANET_RESOURCES,
    description="Dataset XML Orphadata (epidemiologia, nomenclatura, storia naturale)",
)
