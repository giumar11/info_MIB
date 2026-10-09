# Report ANIA - Associazione Nazionale fra le Imprese Assicuratrici

## Fonte
- **Istituzione**: ANIA - Associazione Nazionale fra le Imprese Assicuratrici
- **Natura**: Associazione di categoria del settore assicurativo italiano
- **URL**: https://www.ania.it/
- **URL Pubblicazioni**: https://www.ania.it/pubblicazioni/
- **Settore**: Assicurativo (vita, danni, RC auto, welfare integrativo, sanità integrativa)

## Rilevanza per il progetto
Il settore assicurativo è una componente del welfare sanitario integrativo
italiano (fondi sanitari, polizze salute, LTC). I report ANIA forniscono dati
di contesto su spesa sanitaria privata intermediata, previdenza e protezione,
complementari alle fonti SSN del repository (GIMBE, OASI, AIFA).

## Pubblicazioni principali

### 1. L'Assicurazione Italiana (relazione annuale)
Rapporto annuale sull'andamento dell'attività assicurativa in Italia (vita e
danni), presentato all'Assemblea annuale ANIA.
- **URL**: https://www.ania.it/pubblicazioni/-/categories/53729
- Edizioni recenti: 2024-2025, 2023-2024, 2022-2023, ...

### 2. Appendice Statistica alla Relazione Annuale
Conti tecnici per ramo e situazione patrimoniale del settore (dati di bilancio).
- **URL**: https://www.ania.it/pubblicazioni/-/categories/53729

### 3. Italian Insurance (estratto in inglese)
Executive summary in lingua inglese della relazione annuale.
- **URL**: https://www.ania.it/pubblicazioni/-/categories/53705

### 4. Dossier e report tematici
RC Auto, welfare e salute integrativa, previdenza complementare, LTC, clima e
catastrofi naturali, ecc.
- **URL**: https://www.ania.it/pubblicazioni/

## Download
I PDF originali si scaricano con:

```bash
python3 scripts/download_ania_pdfs.py            # scarica i PDF mancanti
python3 scripts/download_ania_pdfs.py --check    # mostra solo lo stato
python3 scripts/download_ania_pdfs.py --force    # riscarica tutto
```

I file vengono salvati in `datasets/raw/ania/pdf/` e tracciati in
`datasets/raw/ania/download_manifest.json`.

## Report tracciati
Lo script `scripts/download_ania_pdfs.py` traccia (oltre alle relazioni annuali
"L'Assicurazione Italiana", l'Appendice Statistica e l'estratto in inglese) i
dossier tematici del settore assicurativo rilevanti per il welfare sanitario:

- **Welfare Index PMI** (welfare e salute integrativa)
- **Salute e sanità integrativa** (fondi e polizze salute)
- **RC Auto** (prezzi, sinistri, frodi)
- **Long Term Care** (non autosufficienza)
- **Previdenza complementare e protezione**
- **ANIA Trends** (premi e raccolta rami danni e vita)

### Nota sugli URL e risoluzione automatica
Il portale ANIA (Liferay) usa URL "asset" con identificativi opachi che
cambiano nel tempo. Per le edizioni senza link diretto stabile è indicata la
pagina ufficiale di pubblicazione (`page`): lo script tenta di **risolvere
automaticamente** il PDF scaricando l'HTML della pagina e cercando i link ai
PDF/asset (preferendo quelli che contengono l'anno/edizione). Se la risoluzione
fallisce, l'elemento resta `pending_url` nel manifest. Il download verifica
l'intestazione `%PDF-` e scarta eventuali pagine HTML di errore.

### Nota sull'ambiente di esecuzione
Nel sandbox Claude Code il dominio `www.ania.it` è **bloccato dalla policy di
egress** dell'organizzazione (risposta 403): il download non è eseguibile da lì.
La pipeline giornaliera `.github/workflows/daily-enrichment.yml` gira su runner
GitHub Actions con accesso di rete completo ed è quella che scarica
effettivamente i PDF ANIA.

## Licenza
Dati e pubblicazioni ANIA - uso soggetto ai termini del sito ania.it.
I documenti sono resi pubblici da ANIA a fini informativi.
