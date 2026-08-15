# ANIA - Associazione Nazionale fra le Imprese Assicuratrici

Fonte primaria sul mercato assicurativo italiano, incluso il **ramo salute /
malattia** e la **sanita' integrativa** (fondi sanitari, welfare aziendale),
rilevanti per l'analisi della spesa sanitaria privata e del secondo/terzo
pilastro sanitario in Italia.

- **Sito**: https://www.ania.it/
- **Pubblicazioni**: https://www.ania.it/pubblicazioni
- **Licenza**: contenuti ANIA riservati, uso citazionale/di ricerca

## Report inclusi

Il rapporto di punta e' **"L'Assicurazione Italiana"**, pubblicazione annuale
che analizza l'intero mercato (Vita, Danni, Auto, Salute) con appendice
statistica e confronto internazionale.

| Edizione | Anno | Tipo |
|----------|------|------|
| L'Assicurazione Italiana 2025-2026 | 2026 | Rapporto annuale |
| L'Assicurazione Italiana 2024-2025 | 2025 | Rapporto annuale |
| L'Assicurazione Italiana 2022-2023 | 2023 | Rapporto annuale |
| L'Assicurazione Italiana 2020-2021 | 2021 | Rapporto annuale |
| L'Assicurazione Italiana 2019-2020 | 2020 | Rapporto annuale |
| L'Assicurazione Italiana 2012-2013 | 2013 | Rapporto annuale |
| L'Assicurazione Italiana in cifre  | 2016 | Sintesi cifre chiave |

## Download

I PDF **originali** vengono scaricati in `pdf/` da:

```bash
python3 scripts/download_ania_reports.py          # scarica i mancanti
python3 scripts/download_ania_reports.py --check  # stato
python3 scripts/download_ania_reports.py --force  # ri-scarica tutto
```

Lo script salva anche `pdf/manifest.json` con dimensioni e hash SHA-256 di
ogni file. La pipeline giornaliera (`scripts/run_daily_enrichment.py`) esegue
questo download automaticamente.

## Rilevanza per il progetto

Il ramo malattia/salute e i fondi sanitari integrativi (secondo pilastro)
rappresentano la componente assicurativa della spesa sanitaria privata,
complementare ai dati GIMBE sulla spesa out-of-pocket e ai dati ISTAT sulla
rinuncia alle cure. I dati ANIA permettono di quantificare quanto della spesa
sanitaria privata italiana passi attraverso schemi assicurativi vs pagamento
diretto.
