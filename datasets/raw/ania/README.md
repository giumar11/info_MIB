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

### Nota sugli URL
Il portale ANIA (Liferay) usa URL "asset" con identificativi opachi che
cambiano nel tempo. Per le edizioni recenti è indicata solo la pagina
ufficiale di pubblicazione (`page`).

Lo script prova a **risolvere automaticamente** il link diretto al PDF dalla
pagina di pubblicazione (estrae gli href a `.pdf` e gli asset Liferay
`/documents/` e `/export/sites/`). Se la risoluzione riesce, il report viene
scaricato e il manifest registra `url_resolved_from_page: true`; se non riesce,
l'elemento resta `pending_url` e va risolto manualmente dalla pagina.
Il download verifica l'intestazione `%PDF-` e **scarta** (non salva) le pagine
HTML di errore, così da non spacciarle per PDF validi.

### Nota sull'ambiente di esecuzione
Il dominio `www.ania.it` è bloccato dal proxy di egress delle sessioni Claude
sul web: in quell'ambiente il download non parte (403). Il download effettivo
avviene nella **pipeline schedulata su GitHub Actions**
(`.github/workflows/daily-enrichment.yml`), dove la rete è aperta.

## Licenza
Dati e pubblicazioni ANIA - uso soggetto ai termini del sito ania.it.
I documenti sono resi pubblici da ANIA a fini informativi.
