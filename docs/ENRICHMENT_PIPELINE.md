# Pipeline di enrichment giornaliera

Questo documento descrive la pipeline che mantiene aggiornati i **dataset e i
report originali** della repository per **tutte le categorie di documenti**.

## Principio

Per ogni categoria vengono scaricati i **file originali** pubblicati dagli enti
proprietari (PDF, CSV, XML, ZIP), non solo gli estratti processati internamente.
Gli estratti/JSON elaborati restano in `datasets/processed/`, mentre gli
originali vivono in `datasets/raw/<categoria>/`.

## Componenti

| File | Ruolo |
|------|-------|
| `scripts/enrichment_sources.json` | Catalogo delle fonti originali scaricabili, per categoria |
| `scripts/enrich_datasets.py` | Orchestratore: scarica gli originali, scrive manifest e checksum |
| `scripts/download_gimbe_pdfs.py` | Download dedicato dei report GIMBE (delegato dall'orchestratore) |
| `scripts/download_pdta.py` | Download dedicato dei PDTA nazionali/regionali/locali (delegato) |
| `scripts/scheduler_check_updates.py` | Monitoraggio dei portali senza URL diretto (rileva nuove pubblicazioni) |
| `.github/workflows/daily-enrichment.yml` | Schedulazione giornaliera (06:30 UTC) + apertura PR con le novità |

## Categorie coperte

L'orchestratore copre le categorie con file scaricabili direttamente
(`ania`, `aifa`, `oasi_bocconi`, `osservatorio_salute`, `uniamo`, `enpam`,
`istat`, `societa_scientifiche`) e delega a script dedicati per `gimbe` e `pdta`.
Le fonti-portale rimanenti (PNE, LEA, PNGLA, OpenBDAP, comparatori internazionali,
ecc.) sono monitorate quotidianamente da `scheduler_check_updates.py`, che segnala
quando esce una nuova pubblicazione da aggiungere alla configurazione.

Elenco aggiornato:

```bash
python3 scripts/enrich_datasets.py --list
```

## Uso

```bash
# Tutte le categorie (scarica solo i file mancanti)
python3 scripts/enrich_datasets.py

# Una o più categorie specifiche
python3 scripts/enrich_datasets.py --category ania --category aifa

# Solo verifica dello stato (nessun download)
python3 scripts/enrich_datasets.py --check

# Anteprima delle azioni
python3 scripts/enrich_datasets.py --dry-run

# Riscarica tutto, anche i file già presenti
python3 scripts/enrich_datasets.py --force
```

## Schedulazione giornaliera

### GitHub Actions (consigliato)

Il workflow `daily-enrichment.yml` gira ogni giorno alle **06:30 UTC**. I runner
di GitHub hanno accesso a Internet aperto, quindi i download dai siti degli enti
funzionano anche quando l'ambiente di sviluppo usa un proxy con allowlist
ristretta. Quando trova file nuovi o aggiornati, il workflow apre una **pull
request in draft** con gli originali scaricati e i manifest aggiornati.

Avvio manuale: scheda **Actions → Daily dataset enrichment → Run workflow**
(opzionalmente indicando le categorie e/o `force`).

### cron locale

```bash
python3 scripts/enrich_datasets.py --install-cron   # ogni giorno alle 06:30
```

## Output

- `datasets/raw/<categoria>/enrichment_manifest.json` — dimensione, checksum
  SHA-256, URL e stato di ogni file scaricato.
- `logs/enrichment_report_YYYY-MM-DD.json` — report globale dell'esecuzione.

## Aggiungere una nuova fonte

1. Aggiungere una voce in `scripts/enrichment_sources.json` (in una categoria
   esistente o in una nuova con `dest_dir` + `sources`).
2. Registrare la fonte in `sources_catalog.csv`.
3. Verificare con `python3 scripts/enrich_datasets.py --category <nome> --dry-run`.
