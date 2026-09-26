# Report ANIA - Associazione Nazionale fra le Imprese Assicuratrici

## Fonte
- **Istituzione**: ANIA - Associazione Nazionale fra le Imprese Assicuratrici
- **Natura**: Associazione di categoria delle imprese di assicurazione operanti in Italia
- **URL**: https://www.ania.it/
- **Pubblicazioni**: https://www.ania.it/pubblicazioni
- **Categoria dati**: `insurance` (assicurativo)

## Rilevanza sociosanitaria
I report ANIA sono rilevanti per l'analisi dell'indirizzamento sociosanitario
perché documentano i **canali di accesso alle cure alternativi/complementari al
SSN**: assicurazioni malattia, sanità integrativa, fondi sanitari e welfare
aziendale. Contengono dati su spesa sanitaria privata, premi e prestazioni del
ramo malattia, e diffusione delle coperture salute tra famiglie e imprese.

## Pubblicazioni principali

### 1. L'assicurazione italiana (rapporto annuale)
Rapporto di riferimento del settore assicurativo italiano, pubblicato in
occasione dell'Assemblea annuale ANIA. Include un capitolo dedicato alle
**assicurazioni malattia/salute** e all'analisi della spesa sanitaria privata.
- **URL edizione 2024-2025**: https://www.ania.it/wp-content/uploads/2026/03/LAssicurazione-Italiana-2024-2025.pdf
- **Serie storica**: edizioni annuali dal 2019-2020

### 2. Italian Insurance (versione inglese)
Versione in lingua inglese del rapporto annuale.
- **URL 2024-2025 (EN)**: https://www.ania.it/wp-content/uploads/2026/03/Italian-Insurance-2025_EN-WEBFULL-4.pdf

### 3. Appendice statistica / L'assicurazione italiana in cifre
Tavole statistiche di dettaglio per ramo (vita, danni, malattia, RC auto).
- **URL**: https://www.ania.it/pubblicazioni/-/categories/53729

### 4. Report tematici salute e welfare
Analisi su sanità integrativa, fondi sanitari, spesa sanitaria privata
(out-of-pocket vs intermediata), welfare aziendale.
- **URL pubblicazioni**: https://www.ania.it/pubblicazioni/-/categories/53705

## File in questa directory
- `ania_report_completo.json` - metadati strutturati dei report ANIA (bibliografia, URL, temi)
- `pdf/` - PDF originali (scaricati dalla pipeline; vedi `pdf/manifest.json`)

## Download dei PDF originali
```bash
python3 scripts/download_ania_reports.py            # scarica i PDF mancanti
python3 scripts/download_ania_reports.py --check    # mostra lo stato
```
Oppure, integrato nella pipeline di enrichment giornaliera:
```bash
python3 scripts/daily_enrichment_pipeline.py --category insurance
```

## Licenza
I documenti ANIA sono soggetti al copyright dell'associazione e resi disponibili
per consultazione pubblica sul sito ufficiale. L'uso nel repository è a fini di
analisi e citazione della fonte.
