# ANIA - Associazione Nazionale fra le Imprese Assicuratrici

Report e dati originali pubblicati da **ANIA** rilevanti per l'analisi del
sistema sanitario italiano, con particolare riferimento alla **spesa sanitaria
privata intermediata** da assicurazioni, fondi sanitari integrativi e società
di mutuo soccorso, e al **ramo Malattia** (salute).

## Contenuto

| Documento | Descrizione | Frequenza |
|-----------|-------------|-----------|
| **L'Assicurazione Italiana** | Rapporto annuale ANIA. Include la sezione "Malattia" (ramo salute), dati su premi, sinistri e spesa sanitaria intermediata | annuale (giugno/luglio) |
| **Appendice Statistica** | Tavole statistiche di dettaglio a corredo del rapporto annuale | annuale |
| **Report tematici sanità/welfare** | Analisi su sanità integrativa, fondi sanitari, welfare aziendale | periodico |

I PDF originali sono salvati in `pdf/` con un `manifest.json` che traccia
dimensione, hash SHA-256 e stato di ogni file.

## Perché ANIA nel repository sanitario

La spesa sanitaria privata in Italia (~40 mld €) è in parte intermediata da
polizze assicurative e fondi sanitari. ANIA è la fonte primaria per:

- quota della spesa sanitaria coperta da assicurazioni (~7%) e fondi (~3%);
- andamento premi e sinistri del ramo Malattia;
- diffusione della sanità integrativa e del welfare aziendale.

Questi dati completano le fonti sul finanziamento del SSN (GIMBE, OASI Bocconi,
Corte dei Conti, ISTAT) con la prospettiva del "secondo e terzo pilastro".

## Download

```bash
python3 scripts/download_ania_reports.py            # scarica i PDF mancanti
python3 scripts/download_ania_reports.py --check     # stato
python3 scripts/download_ania_reports.py --force      # riscarica tutto
```

Il download è integrato nella pipeline di enrichment giornaliera
(`scripts/enrichment_pipeline.py`, categoria `ania`).

## Fonti

- Portale pubblicazioni ANIA: https://www.ania.it/pubblicazioni
- Rapporto annuale "L'Assicurazione Italiana": https://www.ania.it/pubblicazioni/-/categories/53705
- Appendice Statistica: https://www.ania.it/pubblicazioni/-/categories/53729
- Sezione Salute: https://www.ania.it/infopolizze-salute

## Licenza

I documenti sono di proprietà di ANIA e soggetti alle relative condizioni
d'uso. Sono raccolti a soli fini di ricerca e analisi. Verificare i termini
sul sito ufficiale prima di qualsiasi ridistribuzione.
