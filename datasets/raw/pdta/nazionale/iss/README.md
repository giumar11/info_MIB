# PDTA Nazionali - ISS

Linee di indirizzo nazionali sui Percorsi Diagnostico-Terapeutici Assistenziali
elaborate dall'Istituto Superiore di Sanità.

## Documenti attesi (source_id catalogo)
- `PDTA_ISS_001` - Linee di indirizzo Nazionali PDTA Demenze

## Download
I PDF originali vengono scaricati dalla pipeline:

```bash
python3 scripts/download_pdta.py --level nazionale
# oppure, integrato nella pipeline giornaliera:
python3 scripts/daily_enrichment_pipeline.py --category pdta
```

Questa directory è il target di destinazione previsto da `sources_catalog.csv`.
