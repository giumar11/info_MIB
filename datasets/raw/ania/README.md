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

### Report principali

| File | Descrizione | Aggiornamento |
|------|-------------|---------------|
| `assicurazione_italiana_<anno>.pdf` | Rapporto annuale "L'Assicurazione Italiana" — overview del mercato assicurativo | annuale (giugno) |
| `italian_insurance_in_figures_<anno>.pdf` | Statistical yearbook in inglese | annuale |
| `ania_trends_rca.pdf` | Monitoraggio mercato RC Auto (prezzi, sinistri, frequenza) | trimestrale |
| `assistenza_sanitaria_integrativa.pdf` | Analisi welfare e sanità integrativa privata | annuale |
| `welfare_integrativo.pdf` | Report su previdenza complementare e welfare aziendale | periodico |
| `premi_lavoro_italiano.pdf` | Statistiche trimestrali su premi vita e danni | trimestrale |

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
