# ANIA - Report assicurativi (settore salute e welfare integrativo)

Fonte: **ANIA - Associazione Nazionale fra le Imprese Assicuratrici**
Portale pubblicazioni: https://www.ania.it/pubblicazioni

Questa cartella raccoglie i **report originali** ANIA rilevanti per l'analisi
del sistema sanitario italiano, in particolare per la componente di spesa
sanitaria privata, welfare integrativo e assicurazioni malattia.

## Contenuto

| Categoria | Descrizione |
|-----------|-------------|
| `relazione_annuale` | "L'Assicurazione Italiana" - relazione annuale ANIA. Contiene la sezione salute/welfare, i dati sulle assicurazioni malattia (ramo danni) e le previdenze integrative (ramo vita). |
| `annual_report_en` | Edizioni in lingua inglese ("Italian Insurance"). |

I PDF originali vengono salvati in `pdf/` insieme a un `manifest.json` con
dimensioni, hash SHA-256 e URL sorgente di ciascun file.

## Download

```bash
python3 scripts/download_ania_reports.py           # scarica i PDF mancanti
python3 scripts/download_ania_reports.py --check    # mostra lo stato
python3 scripts/download_ania_reports.py --force     # riscarica tutto
```

Il download avviene tramite la pipeline di enrichment giornaliera
(`.github/workflows/enrichment-daily.yml`, categoria `ania`).

## Licenza

I documenti sono pubblicati da ANIA sul proprio portale istituzionale a fini
informativi. L'uso è soggetto ai termini indicati da ANIA. Nel repository sono
tracciati come fonte con `license = proprietary` nel `sources_catalog.csv`.

## Rilevanza per l'analisi sociosanitaria

I report ANIA forniscono la prospettiva del **secondo pilastro** (assicurazioni
private e fondi sanitari integrativi) complementare ai dati pubblici SSN,
GIMBE e Corte dei Conti già presenti nel repository. Utili per quantificare la
quota di spesa sanitaria intermediata da assicurazioni e la diffusione del
welfare sanitario integrativo.
