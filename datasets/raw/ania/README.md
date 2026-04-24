# ANIA - Associazione Nazionale fra le Imprese Assicuratrici

Questa cartella contiene i rapporti e i dataset originali pubblicati dall'ANIA
(Associazione Nazionale fra le Imprese Assicuratrici) e dall'autorita di
vigilanza IVASS, rilevanti per l'analisi del sistema sanitario italiano sul
lato privato/integrativo (fondi sanitari, polizze salute, welfare aziendale,
spesa out-of-pocket).

## Fonti coperte

| Rapporto | Frequenza | URL di riferimento |
|----------|-----------|--------------------|
| L'Assicurazione Italiana - Rapporto Annuale ANIA | annuale | https://www.ania.it/web/guest/pubblicazioni/rapporto-annuale |
| Italian Insurance - Annual Report (English) | annuale | https://www.ania.it/web/guest/pubblicazioni/italian-insurance |
| ANIA Trends - Premi del lavoro diretto italiano | mensile | https://www.ania.it/web/guest/servizi/centro-studi/ania-trends |
| Osservatorio Sanita ANIA | annuale | https://www.ania.it/web/guest/servizi/centro-studi/osservatorio-sanita |
| ANIA R.C. Auto Osservatorio | trimestrale | https://www.ania.it/web/guest/servizi/centro-studi/osservatorio-rca |
| ANIA Welfare - Previdenza complementare e salute | annuale | https://www.ania.it/web/guest/servizi/centro-studi/welfare |
| ANIA Fondazione - Vittime della strada | annuale | https://www.fondazioneania.it/ |
| ANIA Position Paper - Fondi Sanitari Integrativi | periodica | https://www.ania.it/web/guest/pubblicazioni/position-paper |
| IVASS Relazione Annuale | annuale | https://www.ivass.it/pubblicazioni-e-statistiche/pubblicazioni/relazione-annuale/index.html |
| IVASS Statistiche assicurative | trimestrale | https://www.ivass.it/pubblicazioni-e-statistiche/statistiche/index.html |

## Struttura

```
ania/
|-- README.md
|-- pdf/                       # Rapporti originali (PDF)
|-- ivass/                     # Pubblicazioni IVASS
|-- manifest.json              # Generato dalla pipeline di download
```

## Pipeline

Il download e l'aggiornamento giornaliero sono gestiti da:

```
scripts/pipelines/ania_pipeline.py
scripts/run_daily_enrichment.py   # orchestrator (cron 0 7 * * *)
```

## Rilevanza per il progetto info_MIB

Il settore assicurativo privato intercetta una quota crescente della spesa
sanitaria italiana (out-of-pocket + intermediata da fondi) e completa il
quadro della sostenibilita del SSN fornito da fonti come GIMBE, OASI Bocconi
e OsMed.

## Licenza

I rapporti ANIA sono CC-BY-NC. Le pubblicazioni IVASS sono government/open.
Verificare sempre le condizioni di utilizzo sulla pagina della singola
pubblicazione.
