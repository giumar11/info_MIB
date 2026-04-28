# Pipeline di enrichment giornaliero

Questo documento descrive l'infrastruttura automatica che mantiene aggiornati
i dataset e i report ospitati in `info_MIB`. Lo scopo è garantire che il
repository contenga **sempre** sia i **dataset e report originali** dalle
fonti istituzionali, sia gli **estratti processati** (JSON/CSV) derivati.

## Architettura

```
scripts/
├── enrichment/
│   ├── base.py            # EnrichmentEngine: download HTTP, checksum, manifest
│   ├── postprocess.py     # Hook che rigenerano gli estratti (parse_orphadata, SDO, ecc.)
│   ├── sources.json       # Registry delle URL da scaricare per ogni categoria
│   └── __init__.py
└── run_daily_enrichment.py  # Orchestratore CLI
```

### EnrichmentEngine (`scripts/enrichment/base.py`)

Per ogni categoria:

1. Legge `datasets/raw/<categoria>/download_manifest.json` (se esiste).
2. Per ogni sorgente configurata esegue una GET HTTP condizionale
   (`If-None-Match` + `If-Modified-Since`) con retry esponenziale su errori
   di rete.
3. Calcola lo SHA256 del file scaricato; se identico al precedente segna
   l'entry come `unchanged` senza sovrascrivere.
4. Altrimenti sostituisce atomicamente il file in `datasets/raw/<categoria>/`
   e aggiorna il manifest con `sha256`, `etag`, `last_modified`,
   `last_checked`.
5. Al termine invoca l'eventuale **post-processor** della categoria (es.
   `parse_orphadata.py` se l'XML Orphanet è cambiato).

### Registry delle sorgenti (`scripts/enrichment/sources.json`)

Registry dichiarativa. Ogni categoria è una chiave che mappa 1:1 sulla
cartella `datasets/raw/<categoria>/`. Ogni sorgente specifica:

| Campo | Descrizione |
|-------|-------------|
| `source_id` | ID univoco nel catalog (`ANIA_001`, `ORPHA_EPI_IT`, …) |
| `title` | Titolo human-readable |
| `url` | URL diretto al file originale (fallback se il resolver fallisce) |
| `dest` | Path relativo a `datasets/raw/<categoria>/` |
| `kind` | `pdf` / `json` / `csv` / `xml` / `zip` / `html` |
| `landing_url` | URL della landing page (informativo) |
| `resolver` | Blocco opzionale per scoprire l'URL tramite scraping (vedi sotto) |
| `skip_daily` | Se `true`, il download viene saltato (risorse auth-only o landing page) |
| `notes` | Note operative |

#### Resolver da landing page

Molti portali (ANIA, AIFA, GIMBE, ISS, Ministero Salute, ecc.) pubblicano
nuove edizioni annuali con URL che cambiano (anno, timestamp nel path, ID
Liferay). Per evitare che la pipeline si rompa ad ogni nuovo rilascio, ogni
sorgente può dichiarare un blocco `resolver`:

```json
{
  "resolver": {
    "type": "landing_regex",
    "landing_url": "https://www.ania.it/pubblicazioni/-/categories/53705",
    "pattern": "Italian.Insurance.in.figures",
    "prefer_latest": true
  }
}
```

Al momento del download il motore:

1. scarica la `landing_url` come HTML;
2. estrae tutti gli `href=` dei link e li rende assoluti rispetto alla landing;
3. filtra gli URL che matchano la regex `pattern` (case-insensitive);
4. se `prefer_latest=true` ordina i match per l'anno più alto presente nell'URL
   (fallback: lunghezza dell'URL) e usa il primo; altrimenti il primo match
   testuale;
5. usa l'URL risolto come sorgente; se il resolver fallisce (nessun match /
   errore HTTP) il motore tenta comunque il fallback statico `url`.

Questa combinazione `static_url + resolver` garantisce:

- **robustezza**: se ANIA rinomina il PDF ma la categoria resta, il resolver
  trova il nuovo URL automaticamente;
- **archivio**: URL statici di edizioni storiche continuano a funzionare
  quando disponibili.

### Post-processor (`scripts/enrichment/postprocess.py`)

Mappa categoria → callable che rigenera gli estratti processati:

| Categoria | Post-processor |
|-----------|----------------|
| `orphadata` | `parse_orphadata.py` (rigenera `malattie_rare_italia.{json,csv}`) |
| `ministero_salute` | `extract_sdo_data.py` (rigenera riepilogo SDO, PDTA, segmentazione) |
| `istat` | Estrazione automatica di `hfa_italia.zip` in `datasets/raw/istat/hfa/HFA/` → `analyze_hfa_chronic.py` |
| `ons`, `oasi_bocconi`, `aifa`, `gimbe`, `societa_scientifiche` | `enrich_scientific_reports_ons.py` |

## CLI

```bash
# Esegui tutte le categorie
python3 scripts/run_daily_enrichment.py

# Solo alcune
python3 scripts/run_daily_enrichment.py --only ania aifa

# Tutte tranne quelle indicate
python3 scripts/run_daily_enrichment.py --skip istat

# Elenco delle categorie disponibili
python3 scripts/run_daily_enrichment.py --list
```

Output:

- `logs/enrichment_<YYYY-MM-DD>.log` — log testuale
- `logs/enrichment_<YYYY-MM-DD>.json` — report JSON con stato per sorgente
- `datasets/raw/<categoria>/download_manifest.json` — manifest aggiornato
- `datasets/raw/<categoria>/<file>` — originali aggiornati
- `datasets/processed/*.{json,csv}` — estratti rigenerati

## Automazione CI

`.github/workflows/daily_enrichment.yml` schedula il job ogni giorno alle
04:00 UTC (cron `0 4 * * *`). Ogni categoria gira in parallelo (matrix,
max 4 in contemporanea) e committa eventuali aggiornamenti di file sul
branch corrente con messaggio `chore(enrichment): daily update <cat> [skip ci]`.

Il job finale `summary` produce uno `GITHUB_STEP_SUMMARY` tabellare con
download/unchanged/failed per ogni categoria.

### Trigger manuale

Dal tab *Actions* su GitHub è possibile lanciare `workflow_dispatch` con
due input opzionali:

- `only`: lista di categorie (separate da spazio) da eseguire
- `skip`: lista di categorie da saltare

## Categorie coperte

| Categoria | Sorgenti | Note |
|-----------|---------:|------|
| orphadata | 3 | Malattie rare epidemiologia IT/EN + prevalence |
| ania | 8 | **Nuova categoria** — rapporti assicurazione italiana, sanità integrativa, welfare |
| aifa | 4 | OsMed, vaccini, sperimentazioni cliniche |
| gimbe | 3 | Rapporti annuali sul SSN |
| uniamo | 2 | MonitoRARE malattie rare |
| osservatorio_salute | 1 | Rapporto Osservasalute annuale |
| enpam | 1 | Guida specialisti ambulatoriali |
| finanza | 1 | OpenBDAP SSN |
| ministero_salute | 1 | Rapporto SDO |
| istat | 2 | Health for All, EHIS microdati |
| ons | 1 | Rapporto screening oncologico |
| oasi_bocconi | 1 | Rapporto OASI annuale |
| internazionale | 2 | OECD country profile, WHO GHED |
| iss | 2 | PASSI, PASSI d'Argento |
| societa_scientifiche | 0 | Gestite da `enrich_scientific_reports_ons.py` |
| governance | 0 | Landing page, download parziale gestito nei sotto-README |
| pdta | 0 | Gestita da `scripts/download_pdta.py` |
| sistema_sanitario | 0 | Download manuali |
| riforme | 0 | Gazzetta Ufficiale, scaricamento manuale |

Totale sorgenti automatizzate: **32**.

## Aggiungere una nuova sorgente

1. Aggiungere entry a `scripts/enrichment/sources.json` sotto la categoria
   corretta.
2. Aggiungere riga a `sources_catalog.csv` con lo stesso `source_id` e
   `file_paths_in_repo` allineato a `datasets/raw/<categoria>/<dest>`.
3. Testare localmente: `python3 scripts/run_daily_enrichment.py --only <categoria>`.
4. Se è necessario un nuovo post-processor, registrarlo in
   `scripts/enrichment/postprocess.py` → `POST_HOOKS`.

## Bug fix inclusi in questa iterazione

- **Path hardcoded** `/home/ubuntu/progetto_sanitario/` rimossi da
  `analyze_hfa_chronic.py`, `extract_sdo_data.py`, `parse_orphadata.py`.
  Ora tutti gli script derivano il repo root da `Path(__file__)`.
- `requirements.txt` aggiunto (solo `pandas` e `requests`, entrambi già
  richiesti implicitamente).
- `.gitignore` esteso con `__pycache__/`, `*.pyc`, virtual env.
- Workflow CI `lint.yml` valida compilazione Python e JSON.
