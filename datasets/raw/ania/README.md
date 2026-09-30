# ANIA - Assicurazione (settore assicurativo)

Fonti del comparto assicurativo italiano, con focus su sanità integrativa,
spesa privata coperta da polizze e statistiche di settore. Complementari ai
dati sul SSN pubblico (GIMBE, OASI, Ministero della Salute).

## Fonte principale: ANIA

- **Istituzione**: ANIA - Associazione Nazionale fra le Imprese Assicuratrici
- **Natura**: associazione di categoria delle imprese di assicurazione italiane
- **Sito**: https://www.ania.it/
- **Pubblicazioni**: https://www.ania.it/pubblicazioni
- **Statistiche e dati**: https://www.ania.it/statistiche-e-dati

### Pubblicazioni monitorate

| # | Pubblicazione | Frequenza | Contenuto |
|---|---------------|-----------|-----------|
| 1 | **L'Assicurazione Italiana** (Relazione annuale) | annuale | Rapporto di riferimento sul mercato assicurativo italiano: premi, sinistri, rami vita/danni, scenario macro |
| 2 | **Italian Insurance in Figures / L'assicurazione in cifre** | annuale | Sintesi statistica con i principali indicatori di mercato |
| 3 | **ANIA Trends - Premi del lavoro diretto italiano** | trimestrale/mensile | Andamento della raccolta premi per ramo |
| 4 | **ANIA Trends - Rami danni / malattia e salute** | trimestrale | Andamento dei rami danni, incluso il ramo malattia (sanità integrativa) |
| 5 | **Osservatorio R.C. Auto** | periodico | Statistiche sinistri e premi R.C. Auto |

## Fonte complementare: IVASS

- **Istituzione**: IVASS - Istituto per la Vigilanza sulle Assicurazioni
- **Natura**: autorità pubblica di vigilanza sul settore assicurativo
- **Bollettino statistico**: https://www.ivass.it/pubblicazioni-e-statistiche/statistiche/bollettino-statistico/

Il bollettino statistico IVASS fornisce dati ufficiali di vigilanza,
utili come riscontro pubblico ai dati associativi ANIA.

## Rilevanza per il progetto

Il settore assicurativo è la principale forma di **intermediazione della
spesa sanitaria privata** (fondi sanitari, polizze malattia collettive e
individuali). Questi dati integrano l'analisi delle criticità di
indirizzamento: quota di spesa out-of-pocket vs. intermediata, diffusione
della sanità integrativa, copertura per area geografica.

## Modalità di acquisizione

I documenti originali vengono scaricati dalla pipeline di enrichment
(`scripts/run_enrichment.py`, categoria `ania`). Gli URL diretti dei PDF
cambiano a ogni edizione: la pipeline parte dalle pagine ufficiali di
pubblicazione (`source_page`) elencate in `scripts/enrichment_registry.py`.
Finché l'URL diretto non è risolto, il file risulta `pending_manual_url`
nel manifest `datasets/raw/enrichment_manifest.json`.

## Licenza

Dati e pubblicazioni ANIA/IVASS soggetti alle rispettive condizioni d'uso.
Uso a fini di analisi e ricerca, con citazione della fonte.
