# ANIA - Report del settore assicurativo italiano

Questa cartella raccoglie i **report e i dataset originali** pubblicati da
**ANIA** (Associazione Nazionale fra le Imprese Assicuratrici), la principale
fonte statistica sul settore assicurativo italiano — rilevante per l'analisi
del welfare integrativo, della sanità integrativa e della spesa sanitaria
privata coperta da polizze.

## Fonte

- **Ente:** ANIA — Associazione Nazionale fra le Imprese Assicuratrici
- **Portale pubblicazioni:** https://www.ania.it/pubblicazioni
- **Licenza:** consultazione pubblica © ANIA (uso a scopo di ricerca/analisi)

## Report acquisiti

| Categoria | Descrizione | Frequenza | Pagina ufficiale |
|-----------|-------------|-----------|------------------|
| `assicurazione_italiana/` | **L'Assicurazione Italiana** — relazione annuale sull'evoluzione e l'andamento dell'attività assicurativa (Vita, Danni, distribuzione, confronto internazionale) + Appendice Statistica | Annuale (luglio) | https://www.ania.it/pubblicazioni/-/categories/53729 |
| `pubblicazioni_generali/` | Studi e rapporti tematici ANIA (welfare, sanità integrativa, previdenza, protezione) | Periodica | https://www.ania.it/pubblicazioni/-/categories/53705 |
| `ania_trends/` | **ANIA Trends** — bollettini statistici periodici (nuova produzione Vita, premi Danni, RC Auto) | Mensile/Trimestrale | https://www.ania.it/ania-trends |

Le categorie e gli eventuali URL diretti sono elencati in
[`ania_sources.json`](./ania_sources.json). Il file
[`manifest.json`](./manifest.json) (generato dallo script) riporta i file
effettivamente scaricati con dimensione e checksum SHA-256.

## Come acquisire i report

```bash
# Scarica i report ANIA mancanti (richiede rete verso ania.it)
python3 scripts/download_ania.py

# Solo verifica di cosa verrebbe scaricato
python3 scripts/download_ania.py --dry-run

# Stato dei file già presenti
python3 scripts/download_ania.py --check
```

Lo script analizza le pagine di categoria del portale ANIA ed estrae i link ai
PDF originali (portale Liferay), scaricandoli in queste sottocartelle.

## Note importanti

- **Rete:** il portale ANIA non è raggiungibile dalle sessioni cloud con proxy
  egress ristretto. L'acquisizione avviene nella **pipeline di enrichment
  giornaliera su GitHub Actions** (`.github/workflows/daily_enrichment.yml`),
  che gira in un ambiente con rete aperta.
- **Elenchi JavaScript:** se il portale rende gli elenchi via JavaScript e lo
  scraping non individua PDF, aggiungere gli URL verificati nel campo
  `direct_pdfs` di `ania_sources.json` — lo script li scaricherà direttamente.
- **Originali, non estratti:** in coerenza con il resto del repository, qui si
  conservano i **PDF/dataset originali** di ANIA; eventuali sintesi elaborate
  vanno in `datasets/processed/`.
