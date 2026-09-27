# Report ANIA - Settore assicurativo italiano

## Fonte
- **Istituzione**: ANIA - Associazione Nazionale fra le Imprese Assicuratrici
- **URL**: https://www.ania.it/
- **Pubblicazioni**: https://www.ania.it/pubblicazioni/
- **Panorama Assicurativo**: https://www.panoramassicurativo.ania.it/

## Rilevanza per l'analisi sociosanitaria
ANIA è la fonte di riferimento per il settore assicurativo italiano. È rilevante
per l'analisi dell'indirizzamento sociosanitario perché documenta:

- **Ramo Salute/Malattia**: premi, nuova produzione, penetrazione delle polizze salute
- **Sanità integrativa e welfare**: ruolo delle coperture private nella spesa sanitaria
- **Spesa sanitaria privata e out-of-pocket**: complementare ai dati GIMBE/ISTAT
- **Confronti internazionali** del mercato assicurativo (edizioni in inglese)

## Pubblicazioni scaricate

### 1. L'Assicurazione Italiana (rapporto annuale)
Rapporto annuale ANIA sull'andamento del settore assicurativo (rami Vita, Danni,
Auto, Salute), con appendice statistica. Edizioni bilancio biennale (es. 2024-2025).

### 2. Report tematici
Report PAI e altri approfondimenti settoriali.

## Download
I PDF originali si scaricano con:

```bash
python3 scripts/download_ania_reports.py           # scarica i mancanti
python3 scripts/download_ania_reports.py --check    # mostra lo stato
python3 scripts/download_ania_reports.py --force     # riscarica tutto
```

Il manifest `manifest.json` (generato dallo script) elenca i file con checksum
SHA-256, dimensione ed edizione. Gli URL possono cambiare quando ANIA ripubblica
i file: lo scheduler (`scripts/scheduler_check_updates.py`) verifica periodicamente
le fonti del catalogo e segnala i link non più validi.

## Licenza
Dati e pubblicazioni ANIA - uso soggetto ai termini pubblicati su ania.it.
Materiale utilizzato a fini di analisi/ricerca con citazione della fonte.
