# ANIA — Report del settore assicurativo

Questa cartella raccoglie i **report originali di ANIA** (Associazione Nazionale
fra le Imprese Assicuratrici), il principale ente di riferimento per il settore
assicurativo italiano. I report sono rilevanti per l'analisi del **welfare
sanitario integrativo**, della **spesa sanitaria privata** e dei **fondi
assicurativi malattia/salute** che affiancano il SSN.

## Contenuto

Serie principale: **"L'Assicurazione Italiana"** — rapporto annuale sull'andamento
del settore assicurativo (rami Vita e Danni, incluso il ramo malattia/salute),
con conti tecnici, dati di raccolta premi e confronti europei.

I file vengono scaricati automaticamente dalla pipeline di enrichment:

```bash
python3 scripts/enrich_datasets.py --category ania          # scarica gli originali
python3 scripts/enrich_datasets.py --category ania --check  # verifica lo stato
```

L'elenco completo degli URL originali è definito in
`scripts/enrichment_sources.json` (categoria `ania`). Dopo il download, il file
`enrichment_manifest.json` in questa cartella riporta dimensione, checksum
SHA-256 e stato di ciascun file.

## Fonte

- **Ente:** ANIA — Associazione Nazionale fra le Imprese Assicuratrici
- **Portale pubblicazioni:** https://www.ania.it/pubblicazioni
- **Serie "L'Assicurazione Italiana" / Appendice Statistica:** https://www.ania.it/pubblicazioni/-/categories/53729
- **Licenza:** consultare le condizioni d'uso pubblicate da ANIA

## Nota

Le edizioni più recenti (es. 2022-2023, 2024-2025) sono pubblicate tramite il
document library del sito ANIA; gli URL diretti dei PDF vanno risolti dalle
rispettive pagine di dettaglio del portale (vedi `portal_references` nel
manifest di categoria). Le edizioni con URL diretto verificato sono già presenti
nella configurazione della pipeline.
