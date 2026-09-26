# PDTA Nazionali - AGENAS / ALTEMS

Percorsi Diagnostico-Terapeutici Assistenziali (PPDTA) di livello nazionale
elaborati da AGENAS nell'ambito delle attività di HTA.

## Documenti attesi (source_id catalogo)
- `PDTA_AGENAS_001` - PPDTA Diabete Mellito nell'adulto
- `PDTA_AGENAS_002` - PPDTA Asma Grave nell'adulto
- `PDTA_AGENAS_003` - PPDTA BPCO nell'adulto

## Download
I PDF originali vengono scaricati dalla pipeline:

```bash
python3 scripts/download_pdta.py --level nazionale
# oppure, integrato nella pipeline giornaliera:
python3 scripts/daily_enrichment_pipeline.py --category pdta
```

Questa directory è il target di destinazione previsto da `sources_catalog.csv`.
