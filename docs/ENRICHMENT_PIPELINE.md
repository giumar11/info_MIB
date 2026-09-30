# Pipeline di enrichment giornaliere

Questo documento descrive il sistema di **enrichment** che mantiene nel
repository i documenti ORIGINALI (dataset grezzi e report PDF) di tutte le
categorie di fonti, non solo gli estratti elaborati in `datasets/processed/`.

## Componenti

| File | Ruolo |
|------|-------|
| `scripts/enrichment_registry.py` | Registro dichiarativo: per ogni categoria, elenco delle fonti originali (dataset + report) con URL/pagina ufficiale |
| `scripts/run_enrichment.py` | Orchestratore: scarica, valida, aggiorna i manifest e produce il report di esecuzione |
| `scripts/download_gimbe_pdfs.py` | Fonte URL diretti per la categoria `gimbe` (riusata dall'orchestratore) |
| `scripts/download_pdta.py` | Fonte URL diretti per la categoria `pdta` (riusata dall'orchestratore) |
| `.github/workflows/daily-enrichment.yml` | Schedulazione **giornaliera** su GitHub Actions |
| `datasets/raw/enrichment_manifest.json` | Stato consolidato e versionato di tutti i target |
| `logs/enrichment_YYYY-MM-DD.json` | Report di esecuzione (non versionato) |

## Categorie coperte

Tutte le categorie di documenti presenti in `datasets/raw/`:

`governance`, `finanza`, `aifa`, `riforme`, `internazionale`,
`ministero_salute`, `orphadata`, `istat`, `ons`, `oasi_bocconi`, `uniamo`,
`osservatorio_salute`, `sistema_sanitario`, `enpam`, `gimbe`, `pdta` e la
nuova categoria **`ania`** (settore assicurativo).

## Utilizzo

```bash
# Esegue tutte le categorie (scarica gli originali mancanti)
python3 scripts/run_enrichment.py

# Solo una categoria
python3 scripts/run_enrichment.py --category ania

# Elenca tutti i target senza scaricare
python3 scripts/run_enrichment.py --list

# Simulazione (mostra cosa scaricherebbe)
python3 scripts/run_enrichment.py --dry-run

# Solo stato dei file locali (nessun download)
python3 scripts/run_enrichment.py --report-only

# Riscarica anche i file già presenti
python3 scripts/run_enrichment.py --force
```

## Validazione dei file

L'orchestratore rifiuta i file corrotti o non conformi:

- dimensione minima plausibile per formato (`min_bytes`);
- firma (magic bytes) per PDF (`%PDF`), ZIP/XLSX (`PK\x03\x04`), XML (`<`);
- scarto delle pagine HTML di errore salvate come PDF/dataset (404 mascherati).

I file scaricati non validi vengono eliminati e segnati come
`invalid_download` nel manifest. I file già presenti ma corrotti sono
segnati `invalid`.

### Stati possibili nel manifest

| Stato | Significato |
|-------|-------------|
| `present` | File già presente e valido |
| `downloaded` | Scaricato e validato in questa esecuzione |
| `missing` | Assente (modalità `--report-only`) |
| `invalid` | Presente ma non valido (da riscaricare) |
| `invalid_download` | Scaricato ma scartato perché non valido |
| `failed` | Download fallito (rete/HTTP) |
| `pending_manual_url` | Manca l'URL diretto: va risolto dalla `source_page` |

## Schedulazione giornaliera

### GitHub Actions (consigliata)

Il workflow `.github/workflows/daily-enrichment.yml` gira ogni giorno alle
**05:30 UTC**. Quando trova nuovi originali apre una Pull Request automatica
con i file scaricati e il manifest aggiornato, così le modifiche restano
revisionabili prima del merge. Può essere lanciato anche manualmente
(`workflow_dispatch`) scegliendo categoria e opzione `force`.

### Cron locale (alternativa)

```cron
# Ogni giorno alle 07:30 - pipeline di enrichment info_MIB
30 7 * * * cd /path/to/info_MIB && /usr/bin/python3 scripts/run_enrichment.py >> logs/enrichment_cron.log 2>&1
```

## Note operative

- La pipeline è **idempotente**: i file già validi vengono saltati.
- È **sicura offline**: senza rete i target con URL vengono segnati `failed`
  e quelli senza URL `pending_manual_url`, senza interrompere l'esecuzione.
- Gli URL diretti dei PDF istituzionali cambiano spesso a ogni edizione: per
  molte fonti il registro parte dalla `source_page` ufficiale e l'URL diretto
  va confermato (stato `pending_manual_url`). Aggiornare `enrichment_registry.py`
  quando il link diretto è noto.
