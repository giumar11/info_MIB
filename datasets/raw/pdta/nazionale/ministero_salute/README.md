# PDTA Nazionali - Ministero della Salute

Documenti di indirizzo nazionale sulla cronicità e sui percorsi assistenziali.

## Documenti attesi (source_id catalogo)
- `PDTA_PNC_001` - Piano Nazionale della Cronicità
- `PDTA_PNC_002` - Piano Nazionale Cronicità (Aggiornamento 2024)

## Download
I PDF originali vengono scaricati dalla pipeline:

```bash
python3 scripts/download_pdta.py --level nazionale
# oppure, integrato nella pipeline giornaliera:
python3 scripts/daily_enrichment_pipeline.py --category pdta
```

Questa directory è il target di destinazione previsto da `sources_catalog.csv`.
