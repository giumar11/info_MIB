# ANIA — Report del settore assicurativo

Fonte: **ANIA — Associazione Nazionale fra le Imprese Assicuratrici**
Sito: https://www.ania.it/pubblicazioni/

Questa cartella raccoglie i **report originali** pubblicati da ANIA sul mercato
assicurativo italiano, con focus sull'ambito **salute/sanità** (assicurazione
malattia, RC sanitaria, welfare sanitario integrativo, fondi sanitari), rilevante
per l'analisi della spesa sanitaria privata e della sanità integrativa nel SSN.

## Contenuto

- `pdf/` — PDF originali scaricati dal portale ANIA
- `pdf/manifest.json` — manifest con URL, dimensione, SHA-256 e stato di ciascun file

## Download

```bash
python3 scripts/download_ania_reports.py           # scarica i PDF mancanti
python3 scripts/download_ania_reports.py --check   # mostra lo stato
python3 scripts/download_ania_reports.py --force   # riscarica tutto
```

Il download viene inoltre eseguito automaticamente ogni giorno dalla pipeline
`scripts/daily_enrichment.py` (categoria `insurance`), schedulata via GitHub
Actions (`.github/workflows/daily-enrichment.yml`).

## Collane / famiglie di report

| Collana | Descrizione | Pagina catalogo ANIA |
|---------|-------------|----------------------|
| **L'Assicurazione Italiana** | Rapporto annuale sull'andamento del settore | https://www.ania.it/pubblicazioni/-/categories/53729 |
| **L'Assicurazione Italiana in Cifre** | Sintesi statistica annuale (ITA/ENG) | https://www.ania.it/pubblicazioni/-/categories/53733 |
| **ANIA Trends** | Approfondimenti periodici tematici (incl. Focus RC Sanitaria) | https://www.ania.it/pubblicazioni/-/categories/52450 |
| **Report tematici / PAI** | Report su temi specifici del settore | https://www.ania.it/pubblicazioni/ |

## Nota sulle URL

Il portale ANIA (basato su Liferay) genera URL con GUID che possono cambiare nel
tempo. Quando un link diretto non è più valido, il download viene registrato come
`failed` nel manifest. Lo scheduler giornaliero monitora comunque le pagine-catalogo
ANIA (registrate in `sources_catalog.csv`) per individuare nuove edizioni; i nuovi
link diretti vanno aggiunti alla lista `ANIA_REPORTS` in
`scripts/download_ania_reports.py`.

## Licenza

I documenti sono pubblicati da ANIA e soggetti ai relativi termini d'uso. Vengono
raccolti a scopo di analisi/ricerca. Verificare sempre i termini sul sito ufficiale.
