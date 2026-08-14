# Pipeline di enrichment giornaliera

Questo documento descrive la pipeline che mantiene aggiornato il repository
scaricando **report e dataset originali** e rigenerando gli estratti processati.

## Principio guida

> Quando esistono, si caricano i **dataset originali e i report originali**,
> non solo gli estratti processati da noi.

Ogni categoria ha quindi due fasi:

1. **Download originali** — recupero dei file sorgente (PDF, XML, CSV, DBF)
   dalle fonti ufficiali in `datasets/raw/<categoria>/`.
2. **Enrichment / processing** — generazione degli estratti strutturati
   (JSON/CSV) in `datasets/processed/` a partire dagli originali.

## Componenti

| File | Ruolo |
|------|-------|
| `scripts/enrichment_pipeline.py` | Orchestratore: esegue tutte le categorie |
| `scripts/download_gimbe_pdfs.py` | Scarica i PDF originali dei rapporti GIMBE |
| `scripts/download_pdta.py` | Scarica i PDF originali dei PDTA (naz./reg.) |
| `scripts/download_ania_reports.py` | Scarica i report originali ANIA |
| `scripts/parse_orphadata.py` | Processa l'XML Orphadata → malattie rare |
| `scripts/extract_sdo_data.py` | Processa i dati SDO Ministero Salute |
| `scripts/analyze_hfa_chronic.py` | Processa i dati ISTAT Health for All |
| `scripts/enrich_scientific_reports_ons.py` | ONS, società scientifiche, OASI, AIFA |
| `scripts/scheduler_check_updates.py` | Controlla aggiornamenti delle fonti del catalogo |
| `.github/workflows/enrichment-daily.yml` | Schedulazione giornaliera in CI |

## Categorie

| Categoria | Originali | Processing |
|-----------|-----------|------------|
| `gimbe` | download PDF rapporti/osservatorio | — |
| `pdta` | download PDF PDTA | — |
| `ania` | download PDF report ANIA | — |
| `orphadata` | XML già presente | `parse_orphadata.py` |
| `sdo` | CSV già presenti | `extract_sdo_data.py` |
| `istat_hfa` | dataset HFA (DBF) da caricare | `analyze_hfa_chronic.py` |
| `scientific_reports` | — | `enrich_scientific_reports_ons.py` |
| `sources_check` | — | `scheduler_check_updates.py --force` |

## Uso

```bash
# Tutte le categorie
python3 scripts/enrichment_pipeline.py

# Elenco categorie
python3 scripts/enrichment_pipeline.py --list

# Una sola categoria
python3 scripts/enrichment_pipeline.py --category ania

# Anteprima senza eseguire
python3 scripts/enrichment_pipeline.py --dry-run

# Solo processing/check, senza riscaricare gli originali
python3 scripts/enrichment_pipeline.py --skip-download
```

## Schedulazione (GitHub Actions)

Il workflow `enrichment-daily.yml`:

- gira ogni giorno alle **05:00 UTC** (`schedule: cron: '0 5 * * *'`);
- può essere avviato manualmente (`workflow_dispatch`), scegliendo una singola
  categoria e/o saltando il download;
- installa `requests`, `pandas`, `lxml`;
- esegue `scripts/enrichment_pipeline.py`;
- committa e pusha gli originali scaricati e gli estratti aggiornati
  (`datasets/`, `sources_catalog.csv`). La cartella `logs/` è in `.gitignore`.

## Robustezza

- Il fallimento di una categoria **non blocca** le altre.
- I downloader hanno retry con backoff esponenziale e loggano i fallimenti nei
  rispettivi `manifest.json` (status `failed`), senza interrompere la pipeline.
- Ogni run produce `logs/enrichment_YYYY-MM-DD.json` con l'esito di ogni step.

## Estendere la pipeline

Per aggiungere una nuova categoria è sufficiente inserire una voce nel dizionario
`CATEGORIES` di `scripts/enrichment_pipeline.py`, indicando i comandi di
`download` (originali) e `process` (estratti).
