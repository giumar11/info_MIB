# ANIA - Report del settore assicurativo

Questa cartella raccoglie i report **originali** pubblicati da **ANIA**
(Associazione Nazionale fra le Imprese Assicuratrici), rilevanti per l'analisi
del welfare sanitario, della sanità integrativa e della spesa sanitaria privata
in Italia.

## Contenuto

| Sottocartella | Contenuto |
|---------------|-----------|
| `rapporto_annuale/` | "L'Assicurazione Italiana" — rapporto annuale di punta (contiene capitoli su salute, sanità integrativa, LTC e welfare) |
| `salute_welfare/` | Documenti su salute, sanità integrativa, long-term care |
| `statistiche/` | Appendici statistiche e comunicati con dati di mercato (premi, danni, vita) |

## Download

I PDF vengono scaricati automaticamente dalla pipeline di enrichment:

```bash
python3 scripts/download_ania_reports.py            # scarica i report mancanti
python3 scripts/download_ania_reports.py --check     # mostra solo lo stato
python3 scripts/download_ania_reports.py --force      # riscarica tutto
```

La pipeline è eseguita anche ogni giorno dal workflow
`.github/workflows/daily-enrichment.yml` (orchestratore
`scripts/run_daily_enrichment.py`).

Il file `manifest.json` (generato in questa cartella dopo il primo download)
riporta esito, dimensione e hash SHA-256 di ogni file.

## Pagine di riferimento

- Pubblicazioni ANIA: https://www.ania.it/pubblicazioni/
- "L'Assicurazione Italiana" (categoria): https://www.ania.it/pubblicazioni/-/categories/53705
- ANIA Trends (bollettini statistici periodici): https://www.ania.it/pubblicazioni/-/categories/52459
- Appendice Statistica: https://www.ania.it/pubblicazioni/-/categories/53729
- Info polizze salute: https://www.ania.it/infopolizze-salute

## Note sulle URL

Gli URL della pipeline sono stati raccolti dall'indice pubblico dei documenti
ANIA. ANIA ha migrato il sito su WordPress: i PDF canonici correnti del report
di punta si trovano sotto `https://www.ania.it/wp-content/uploads/...`, mentre le
edizioni più vecchie usano il vecchio CMS (`https://www.ania.it/documents/35135/...`),
che la migrazione potrebbe aver reso obsoleto. La verifica effettiva degli URL
avviene in fase di esecuzione: i download falliti vengono registrati nel
manifest senza interrompere gli altri.

## Licenza / riuso

I documenti ANIA sono soggetti al copyright di ANIA ("tutti i diritti
riservati", salvo diversa indicazione). Sono liberamente scaricabili e citabili
a fini di analisi; l'eventuale ridistribuzione dei PDF va verificata con le note
legali di ANIA. **Attenzione:** il report "Welfare, Italia" (Welfare Italia
Index) NON è pubblicato da ANIA ma da UnipolSai + The European House–Ambrosetti;
non va attribuito ad ANIA.
