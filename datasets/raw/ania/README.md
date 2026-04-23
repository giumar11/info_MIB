# ANIA - Report del mercato assicurativo italiano

**Fonte:** [ANIA - Associazione Nazionale fra le Imprese Assicuratrici](https://www.ania.it/pubblicazioni)

Questa cartella contiene i **PDF originali** dei rapporti ANIA rilevanti per
l'analisi del welfare sanitario integrativo e del mercato assicurativo
italiano, sia vita che danni.

## Categorie di report

| Categoria | Descrizione |
|-----------|-------------|
| `rapporto_annuale` | Rapporto annuale "L'Assicurazione Italiana" |
| `trends` | Trends mensili/trimestrali Vita e Danni |
| `focus_salute` | ANIA Trends Salute, welfare integrativo |
| `welfare` | Welfare Index PMI (Generali + ANIA) |
| `quaderno` | Quaderni ANIA tematici (LTC, previdenza, ecc.) |
| `auto` | Statistiche RC Auto |
| `vigilanza` | Solvency II Italia |
| `statistico` | Italian Insurance Data Bulletin (EN) |

## Aree di interesse per il progetto info_MIB

- **salute / welfare integrativo**: quota OOP coperta da polizze, fondi
  sanitari integrativi, bilancio complessivo della spesa sanitaria privata
  mediata da schemi assicurativi.
- **long term care (LTC)**: coperture non-sanitarie per anziani
  multimorbosi, interfaccia con assistenza territoriale DM 77/2022.
- **previdenza complementare**: seconda gamba del welfare, correlata con
  l'analisi della sostenibilità del SSN.

## Download

```bash
python3 scripts/download_ania.py                 # scarica i mancanti
python3 scripts/download_ania.py --force         # forza ri-download
python3 scripts/download_ania.py --year 2024     # filtra per anno
python3 scripts/download_ania.py --dry-run       # solo elenco
```

Manifest con checksum SHA-256: `ania_manifest.json`.

## Licenza

I documenti ANIA sono di proprietà dell'Associazione. Uso interno di
ricerca/analisi, citazione obbligatoria.
