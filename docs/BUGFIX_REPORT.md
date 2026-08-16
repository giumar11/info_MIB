# Check del repository - Bug e problematiche individuate

Report dell'analisi dell'intero repository con i problemi individuati e le
correzioni applicate, insieme alle nuove pipeline di enrichment automatiche.

## Bug corretti

### 1. Path assoluti hardcoded (portabilità) — bloccante

Tre script usavano percorsi assoluti della macchina dell'autore originale
(`/home/ubuntu/progetto_sanitario/...`), rendendoli **ineseguibili** in
qualsiasi altro ambiente (repository, CI, altre macchine):

| Script | Problema | Correzione |
|--------|----------|-----------|
| `scripts/parse_orphadata.py` | input **e** output hardcoded → `FileNotFoundError` sull'input | percorsi relativi a `BASE_DIR` + controllo esistenza input |
| `scripts/extract_sdo_data.py` | output hardcoded | percorsi relativi a `BASE_DIR` |
| `scripts/analyze_hfa_chronic.py` | input **e** output hardcoded | percorsi relativi a `BASE_DIR` |

### 2. `analyze_hfa_chronic.py` — sovrascrittura di dati validi

Oltre al path, lo script scriveva l'output anche quando la sorgente ISTAT HFA
non era presente (non è nel repository), **sovrascrivendo con sezioni vuote** il
file `datasets/processed/analisi_patologie_multispecialistiche.json` già
popolato. Corretto: se la sorgente HFA manca, l'output esistente viene
**preservato** e lo script esce senza errore.

### 3. `download_gimbe_pdfs.py` — verifica TLS non disabilitata come previsto

```python
ctx.verify_peer = False   # attributo INESISTENTE di ssl.SSLContext: no-op
```

`verify_peer` non è un attributo valido di `ssl.SSLContext`: l'assegnazione era
un no-op silenzioso e la verifica del certificato restava attiva, contrariamente
all'intento. Corretto usando l'API corretta:

```python
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
```

### 4. Non-determinismo delle rigenerazioni (churn nella pipeline giornaliera)

`migrate_to_database.py` ed `enrich_scientific_reports_ons.py` inserivano
`datetime.now()` in ogni record/dataset, producendo **diff spurie ad ogni
esecuzione** anche senza modifiche reali ai dati — problematico per una pipeline
che committa ogni giorno. Corretto introducendo una data di build deterministica
`INFO_MIB_BUILD_DATE` (override via variabile d'ambiente, default data odierna).
Una **guardia di determinismo** in CI verifica che la rigenerazione non
introduca diff inattese.

## Problematiche infrastrutturali risolte

- **Assenza di `requirements.txt`** → aggiunto (`requests`, `pandas`).
- **Assenza di CI** → aggiunto `.github/workflows/ci.yml` (compilazione, smoke
  test, guardia di determinismo).
- **Nessuna automazione di enrichment** → aggiunto orchestratore
  `scripts/run_enrichment.py` e workflow giornaliero
  `.github/workflows/enrichment-daily.yml`.

## Novità funzionali

- **Report ANIA (settore assicurativo)**: nuovo downloader
  `scripts/download_ania_reports.py` per i report **originali** ANIA (relazione
  annuale *"L'Assicurazione Italiana"* con sezione salute/welfare, edizioni EN),
  cartella `datasets/raw/ania/` e voci nel `sources_catalog.csv` (categoria
  `insurance`).
- **Pipeline giornaliere per tutte le categorie** che caricano i **report e
  dataset originali** (non solo estratti processati). Dettagli nel README,
  sezione *"Automazione: pipeline di enrichment giornaliere"*.

## Note / gap noti

- Il dataset ISTAT **Health for All (HFA)** non è presente nel repository:
  `analyze_hfa_chronic.py` ora lo segnala e preserva l'output esistente.
- Categorie oggi rigenerate da dati embedded (ONS, società scientifiche, AIFA)
  non hanno ancora un downloader dedicato dei PDF originali: il controllo
  aggiornamenti (`scheduler_check_updates.py`) segnala nuove pubblicazioni a
  monte. Sono i naturali candidati per estendere l'elenco dei downloader di
  originali in `scripts/run_enrichment.py`.
