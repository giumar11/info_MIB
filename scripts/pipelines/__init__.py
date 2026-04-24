"""
info_MIB enrichment pipelines.

Ogni pipeline scarica i dataset e i report ORIGINALI di una categoria
(GIMBE, PDTA, AIFA, OASI, ONS, ISTAT, Orphanet, OECD/Eurostat/WHO,
governance SSN, riforme, societa scientifiche, ANIA, ecc.) e ne tiene
traccia in un manifest con hash SHA-256.

L'orchestrator giornaliero (`run_daily_enrichment.py`) le esegue tutte
secondo una frequenza configurabile per singola fonte.
"""

from .common import (
    Pipeline,
    PipelineResource,
    download_resource,
    load_manifest,
    save_manifest,
    run_pipeline,
)

__all__ = [
    "Pipeline",
    "PipelineResource",
    "download_resource",
    "load_manifest",
    "save_manifest",
    "run_pipeline",
]
