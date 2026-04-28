"""Framework di enrichment per info_MIB.

Ogni pipeline di categoria scarica i dataset/report ORIGINALI dalle fonti
ufficiali in datasets/raw/<categoria>/ e aggiorna un manifest con checksum
SHA256, ETag e Last-Modified per permettere re-run incrementali idempotenti.
"""

from .base import EnrichmentEngine, PipelineReport, SourceDef  # noqa: F401
