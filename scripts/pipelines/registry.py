"""
Registry centrale di tutte le pipeline di enrichment.

Aggiungere una nuova categoria == creare `xxx_pipeline.py` esportante la
variabile `PIPELINE` e registrarla qui sotto.
"""

from .aifa_pipeline import PIPELINE as AIFA_PIPELINE
from .ania_pipeline import PIPELINE as ANIA_PIPELINE
from .gimbe_pipeline import PIPELINE as GIMBE_PIPELINE
from .governance_pipeline import PIPELINE as GOVERNANCE_PIPELINE
from .international_pipeline import PIPELINE as INTERNATIONAL_PIPELINE
from .istat_pipeline import PIPELINE as ISTAT_PIPELINE
from .ministero_salute_pipeline import PIPELINE as MIN_SALUTE_PIPELINE
from .oasi_pipeline import PIPELINE as OASI_PIPELINE
from .ons_pipeline import PIPELINE as ONS_PIPELINE
from .orphanet_pipeline import PIPELINE as ORPHANET_PIPELINE
from .osservatorio_salute_pipeline import PIPELINE as OSS_SALUTE_PIPELINE
from .pdta_pipeline import PIPELINE as PDTA_PIPELINE
from .reform_pipeline import PIPELINE as REFORM_PIPELINE
from .scientific_societies_pipeline import PIPELINE as SOCIETY_PIPELINE

ALL_PIPELINES = [
    AIFA_PIPELINE,
    ANIA_PIPELINE,
    GIMBE_PIPELINE,
    GOVERNANCE_PIPELINE,
    INTERNATIONAL_PIPELINE,
    ISTAT_PIPELINE,
    MIN_SALUTE_PIPELINE,
    OASI_PIPELINE,
    ONS_PIPELINE,
    ORPHANET_PIPELINE,
    OSS_SALUTE_PIPELINE,
    PDTA_PIPELINE,
    REFORM_PIPELINE,
    SOCIETY_PIPELINE,
]

PIPELINES_BY_ID = {p.pipeline_id: p for p in ALL_PIPELINES}

__all__ = ["ALL_PIPELINES", "PIPELINES_BY_ID"]
