# Analisi criticità indirizzamento servizi sociosanitari Italia

Questo repository contiene un'analisi dei problemi di indirizzamento in ambito sociosanitario in Italia. L'obiettivo è fornire una base di dati strutturata per lo sviluppo di strumenti informativi in grado di navigare queste informazioni.

Il progetto si basa su fonti dati istituzionali pubbliche e aggiornate, tra cui ISTAT, Ministero della Salute, Istituto Superiore di Sanità (ISS), AGENAS, AIFA e Orphanet.

---

## Catalogo fonti machine-readable

Il file `sources_catalog.csv` nella root del repository contiene un catalogo strutturato di tutte le fonti dati con i seguenti campi:

| Campo | Descrizione |
|-------|-------------|
| `source_id` | Identificativo univoco della fonte |
| `title` | Titolo della fonte |
| `owner` | Ente proprietario |
| `category` | Categoria (governance, finance, reform, international, etc.) |
| `url` | URL di accesso |
| `license` | Licenza d'uso |
| `update_frequency` | Frequenza di aggiornamento |
| `geography` | Copertura geografica |
| `granularity` | Livello di dettaglio (national, regional, hospital, etc.) |
| `file_paths_in_repo` | Percorsi dei file nel repository |
| `last_checked` | Data ultimo controllo |

---

## Sezione 1: Governance e performance SSN

### A) Open data del SSN

| Fonte | Descrizione | URL |
|-------|-------------|-----|
| **dati.salute.gov.it** | Portale Open Data Ministero della Salute con dataset normalizzati | https://www.dati.salute.gov.it/ |
| **SDO - Dimissioni Ospedaliere** | Dataset su ricoveri per età, sesso, tipologia | `datasets/raw/ministero_salute/` |

### B) Esiti e performance (PNE)

| Fonte | Descrizione | URL |
|-------|-------------|-----|
| **AGENAS - Programma Nazionale Esiti** | Indicatori di esito, processo e volume per struttura ospedaliera | https://pne.agenas.it/ |

**Percorso:** `datasets/raw/governance/pne/`

### C) LEA e nuovo sistema di garanzia

| Fonte | Descrizione | URL |
|-------|-------------|-----|
| **Monitoraggio LEA / NSG** | KPI istituzionali per accountability e qualità minima regionale | https://www.salute.gov.it/portale/lea/ |

**Percorso:** `datasets/raw/governance/lea_nsg/`

### D) Liste d'attesa (PNGLA)

| Fonte | Descrizione | URL |
|-------|-------------|-----|
| **Piano Nazionale Gestione Liste Attesa** | Monitoraggio tempi di attesa per prestazioni ambulatoriali e ricoveri | https://pnla.agenas.it/ |

**Percorso:** `datasets/raw/governance/pngla/`

---

## Sezione 2: Finanza del SSN

### E) OpenBDAP - Finanza enti SSN

| Fonte | Descrizione | URL |
|-------|-------------|-----|
| **OpenBDAP (RGS/MEF)** | Dati di bilancio e spesa degli enti del SSN, conto economico consolidato | https://openbdap.rgs.mef.gov.it/ |

**Percorso:** `datasets/raw/finanza/openbdap/`

### F) Spesa farmaceutica (OsMed)

| Fonte | Descrizione | URL |
|-------|-------------|-----|
| **AIFA - OsMed** | Monitoraggio spesa farmaceutica nazionale e regionale, aderenza terapie | https://www.aifa.gov.it/osmed |

**Percorso:** `datasets/raw/finanza/osmed/`

---

## Sezione 3: Riforme strutturali

### G) DM 77/2022 - Assistenza territoriale

| Elemento | Descrizione |
|----------|-------------|
| **Case della Comunità** | Hub per l'assistenza primaria |
| **Ospedali di Comunità** | Degenza breve a bassa intensità |
| **COT** | Centrali Operative Territoriali |
| **IFeC** | Infermiere di Famiglia e Comunità (1 ogni 3.000 abitanti) |

**Percorso:** `datasets/raw/riforme/dm77_2022/`

### H) PNRR Missione 6 - Salute

| Componente | Budget | Obiettivi |
|------------|--------|-----------|
| **M6C1** - Reti di prossimità | 7 mld € | 1.350 CdC, 400 OdC, 600 COT, Telemedicina |
| **M6C2** - Innovazione | 8,63 mld € | Ammodernamento tecnologico, FSE, Ricerca |

**Percorso:** `datasets/raw/riforme/pnrr_m6/`

### I) DM 70/2015 - Standard Ospedalieri

| Standard | Valore |
|----------|--------|
| Posti letto | 3,7 per 1.000 abitanti |
| Tasso ospedalizzazione | 160 per 1.000 abitanti |
| Volumi minimi | Soglie per procedure complesse |

**Percorso:** `datasets/raw/riforme/dm70_2015/`

---

## Sezione 4: Comparatori internazionali

| Fonte | Descrizione | Copertura | URL |
|-------|-------------|-----------|-----|
| **OECD Health Statistics** | Database comparativo sistemi sanitari OECD | 38 paesi | https://stats.oecd.org/ |
| **Eurostat SHA 2011** | Statistiche sanitarie armonizzate UE | 27 paesi UE | https://ec.europa.eu/eurostat/ |
| **WHO GHED** | Global Health Expenditure Database | 194 paesi | https://apps.who.int/nha/database |
| **KFF Employer Health Benefits** | Survey assicurazioni sanitarie USA | USA | https://www.kff.org/ |
| **Commonwealth Fund Mirror Mirror** | Confronto performance 10 sistemi sanitari | 10 paesi | https://www.commonwealthfund.org/ |

**Percorso:** `datasets/raw/internazionale/`

---

## Sezione 5: Criticità sistema sanitario

Questa sezione contiene report e analisi sulle principali problematiche del SSN italiano.

**Tematiche:**
- Carenza di personale medico e infermieristico
- Liste d'attesa e rinuncia alle cure
- Spesa sanitaria out-of-pocket e privatizzazione
- Welfare sanitario e fondi integrativi
- Performance e disuguaglianze regionali

**Fonti principali:**

| Fonte | Descrizione | Percorso |
|-------|-------------|----------|
| **Fondazione GIMBE** | Rapporti annuali sul SSN | `datasets/raw/gimbe/` |
| **Osservatorio sulla Salute** | Rapporto annuale regioni | `datasets/raw/osservatorio_salute/` |
| **CENSIS** | Rapporto annuale sanità | Link in catalogo |
| **CREA Sanità** | Performance regionali | Link in catalogo |
| **Corte dei Conti** | Relazione sulla gestione finanziaria | Link in catalogo |

**Documentazione:** `docs/sistema_sanitario/CATALOGO_FONTI.md`

---

## Sezione 6: Patologie a elevata complessità

### Metodologia

Per stimare quali patologie richiedano il consulto del maggior numero di specialisti, abbiamo utilizzato un approccio basato su **indicatori proxy**:

1. **Malattie rare**: Odissea diagnostica e necessità di centri di riferimento
2. **Patologie oncologiche**: Team multidisciplinare (GOM/MDT)
3. **Multimorbidità anziani**: Gestione coordinata 3+ patologie croniche
4. **Patologie croniche complesse**: Coinvolgimento multi-organo

### Fonti dati patologie

| Fonte | Dataset | Anno | Formato |
|-------|---------|------|---------|
| **Orphanet** | Epidemiologia 6.443 malattie rare | 2025 | XML |
| **Ministero Salute** | Rapporto SDO | 2023 | PDF, XLSX |
| **ISTAT** | Health for All (4.000 indicatori) | 2025 | DBF |
| **ISS** | Sorveglianza PASSI | Vari | Web/PDF |
| **UNIAMO** | Report malattie rare | 2024 | PDF |

**Percorso:** `datasets/raw/` e `datasets/processed/`

---

## Struttura repository

```
info_MIB/
├── sources_catalog.csv          # Catalogo machine-readable fonti
├── README.md
├── datasets/
│   ├── raw/
│   │   ├── governance/          # PNE, LEA, PNGLA
│   │   ├── finanza/             # OpenBDAP, OsMed
│   │   ├── riforme/             # DM 77, PNRR M6, DM 70
│   │   ├── internazionale/      # OECD, Eurostat, WHO
│   │   ├── ministero_salute/    # SDO, Open Data
│   │   ├── gimbe/               # Rapporti GIMBE
│   │   ├── istat/               # Health for All, EHIS
│   │   └── sistema_sanitario/   # Report criticità
│   ├── processed/               # Dataset elaborati (JSON, CSV)
│   └── migration_ready/         # Dati pronti per database
├── docs/
│   ├── database_design/         # Schema SQL/NoSQL
│   ├── sistema_sanitario/       # Catalogo fonti criticità
│   └── FONTI_DATI.md
└── scripts/                     # Script Python elaborazione
```

---

## Data dictionary

Per i dataset core sono disponibili dizionari dati dettagliati:

- `datasets/raw/ministero_salute/DATA_DICTIONARY.md` - SDO
- `datasets/raw/governance/pne/DATA_DICTIONARY.md` - PNE

---

## Licenza e disclaimer

*Questo progetto è stato realizzato da Geen.ai SRL a scopo dimostrativo per l'analisi di dati sanitari pubblici. I dati aggregati e le analisi prodotte sono il risultato di elaborazioni e non sostituiscono una valutazione medica o rappresentano fonti ufficiali.*

Le fonti dati utilizzate sono soggette alle rispettive licenze indicate nel file `sources_catalog.csv`.
