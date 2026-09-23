# Report ANIA - Associazione Nazionale fra le Imprese Assicuratrici

## Fonte
- **Istituzione**: ANIA - Associazione Nazionale fra le Imprese Assicuratrici
- **Natura**: Associazione di categoria delle imprese di assicurazione operanti in Italia
- **URL Principale**: https://www.ania.it/
- **URL Pubblicazioni**: https://www.ania.it/pubblicazioni

## Rilevanza per l'analisi sociosanitaria

L'assicurazione **malattia/salute** e i **fondi sanitari integrativi** costituiscono
la componente *intermediata* della spesa sanitaria privata, complementare alla
spesa *out-of-pocket* dei cittadini e alla spesa pubblica del SSN. I dati ANIA
sono quindi un comparatore diretto per il "secondo pilastro" sanitario, in
affiancamento alle analisi GIMBE (spesa privata), OASI-Bocconi e Ministero della
Salute.

## Pubblicazioni principali

### 1. L'Assicurazione Italiana (rapporto annuale)
Rapporto di riferimento sul mercato assicurativo italiano, pubblicato ogni luglio.
- **URL categoria**: https://www.ania.it/pubblicazioni/-/categories/53729
- Edizione 2024-2025: premi totali ~160 mld €, Vita 112 mld € (+21%), Danni 47 mld € (+8,9%)
- Sezioni: Executive Summary, Italia e altri Paesi a confronto, Il Vita, I Danni, La RC Auto, La distribuzione

### 2. Appendice Statistica
Conti tecnici per ramo e situazione patrimoniale del settore.
- **URL categoria**: https://www.ania.it/pubblicazioni/-/categories/53729

### 3. ANIA Trends (raccolta premi)
Statistiche periodiche sulla raccolta premi (Vita e Danni).
- **URL categoria**: https://www.ania.it/pubblicazioni/-/categories/52459
- **Premi del lavoro diretto Italiano**: https://www.ania.it/pubblicazioni/-/categories/53734
- **Nuova Produzione Vita**: https://www.ania.it/pubblicazioni/-/categories/52469
- Dati 2025: premi totali 182 mld € (+7,8%), Vita 130,9 mld € (+8,3%), Danni 51,1 mld € (+6,5%)

### 4. Salute / Welfare / Previdenza
Guide e analisi su polizze malattia, LTC (long term care), non autosufficienza,
fondi sanitari integrativi e secondo welfare.
- **URL**: https://www.ania.it/infopolizze-salute

## File nel repository
- `ania_report_completo.json` - Catalogo strutturato completo dei report ANIA
- `pdf/` - PDF originali scaricati da `scripts/download_ania_reports.py`
- `pdf/manifest.json` - Manifest con hash SHA-256 dei PDF scaricati

## Download dei PDF originali

```bash
python3 scripts/download_ania_reports.py           # scarica i PDF mancanti
python3 scripts/download_ania_reports.py --check    # stato
python3 scripts/download_ania_reports.py --dry-run   # anteprima
```

I PDF con URL diretto verificato (rapporti annuali storici) vengono scaricati in
`pdf/`. Le edizioni piu recenti sono pubblicate su pagine Liferay con token di
versione instabili: gli URL diretti vanno aggiornati nello script quando
disponibili. Il catalogo JSON documenta comunque tutte le serie e le pagine
ufficiali di riferimento.

## Licenza
Dati pubblici - ANIA. L'uso dei contenuti è soggetto ai termini del sito ania.it.
