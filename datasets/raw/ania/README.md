# ANIA — Associazione Nazionale fra le Imprese Assicuratrici

Fonte: https://www.ania.it

ANIA è l'associazione di categoria che rappresenta le imprese di assicurazione
operanti in Italia. Pubblica periodicamente rapporti statistici, analisi di
mercato e approfondimenti tematici rilevanti per l'ecosistema finanziario,
previdenziale e sanitario integrativo.

## Contenuto di questa cartella

Questa cartella raccoglie i report ANIA **originali** scaricati dalla pipeline
`scripts/run_daily_enrichment.py --only ania`. Il manifest `download_manifest.json`
traccia per ciascun file: URL sorgente, SHA256, ETag, Last-Modified e data
ultimo check.

### Report principali (solo pubblicazioni integrali — primary sources)

| File | Descrizione | Aggiornamento |
|------|-------------|---------------|
| `assicurazione_italiana_<anno>.pdf` | Rapporto annuale "L'Assicurazione Italiana" — overview del mercato assicurativo (edizioni 2020-2021, 2022-2023, 2023-2024, 2024-2025) | annuale (giugno-luglio) |
| `italian_insurance_in_figures_2017.pdf` | Statistical yearbook in inglese (edizione storica disponibile pubblicamente) | annuale |
| `ania_trends_rca_2024.pdf` | ANIA Trends — monitoraggio mercato RC Auto al 31.12.2024 (prezzi, sinistri, frequenza) | trimestrale |
| `ania_trends_prezzi_rca.pdf` | ANIA Trends — focus prezzi RC Auto (giugno 2024) | trimestrale |
| `ania_newsletter_danni_t2_2025.pdf` | Newsletter Danni — 2° trimestre 2025, statistiche premi diretti rami danni | trimestrale |
| `ania_newsletter_vita.pdf` | Newsletter Vita — flussi e riserve dell'assicurazione vita (ultima edizione) | trimestrale |

### Documenti non inclusi
Per rispettare il principio "solo documenti originali integrali", la pipeline
**non scarica**: comunicati stampa (CS, Aniaflash flash), abstract/sintesi,
estratti per capitoli. Quando una statistica è citata da un comunicato, il dato
primario è disponibile nei rapporti annuali ("L'Assicurazione Italiana") o
nelle Newsletter Vita/Danni elencate sopra.

## Rilevanza per info_MIB

Benché ANIA sia un'associazione del settore assicurativo, i suoi dati sono
rilevanti per l'analisi delle criticità del SSN perché:

1. **Sanità integrativa**: quantificano la spesa privata intermediata da polizze
   collettive (fondi sanitari, welfare aziendale) a integrazione del SSN.
2. **Out-of-pocket**: offrono un contraltare ai dati ISTAT/OsMed sulla spesa
   sanitaria sostenuta direttamente dalle famiglie (41,3 mld € nel 2024).
3. **Long Term Care**: rilevano la penetrazione di coperture LTC, tema cruciale
   per la non-autosufficienza e la multimorbidità dell'anziano.
4. **Responsabilità civile sanitaria**: i dati RC professionale (medici,
   strutture) intercettano il contenzioso sanitario, proxy di criticità.

## Licenza

I contenuti ANIA sono coperti da copyright; la pipeline li scarica per usi di
analisi conformi alle condizioni di accesso pubblico delle pubblicazioni
istituzionali. Qualora un file non risulti più disponibile all'URL
pubblicato, la pipeline segnalerà il failure nel log giornaliero
(`logs/enrichment_<YYYY-MM-DD>.json`) e l'URL andrà aggiornato in
`scripts/enrichment/sources.json`.

## Come rigenerare

```bash
python3 scripts/run_daily_enrichment.py --only ania
```
