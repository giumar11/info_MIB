# Data Dictionary - Schede di Dimissione Ospedaliera (SDO)

**Fonte:** Ministero della Salute
**ID Fonte:** SDO_001
**URL:** https://www.dati.salute.gov.it/dati/dettaglioDataset.jsp?menu=dati&id=10

---

Questo documento descrive la struttura e le variabili dei dataset relativi alle Schede di Dimissione Ospedaliera (SDO), che tracciano l'attività di ricovero degli ospedali pubblici e privati in Italia.

## Dataset Disponibili

1.  **Dimissioni ospedaliere per fasce d'età e sesso** (`dimissioni_ospedaliere_eta_sesso.csv`)
2.  **Dimissioni ospedaliere per istituto e tipologia di dimissione** (`dimissioni_ospedaliere_tipologia.csv`)

---

### 1. `dimissioni_ospedaliere_eta_sesso.csv`

| Nome Colonna | Tipo Dati | Descrizione | Esempio |
|---|---|---|---|
| `ANNO` | Integer | Anno di riferimento della dimissione | 2023 |
| `COD_REG` | String | Codice ISTAT della Regione | 090 |
| `DESC_REG` | String | Descrizione della Regione | Lombardia |
| `ETA` | String | Fascia d'età del paziente | 45-64 anni |
| `SESSO` | String | Sesso del paziente (M/F) | F |
| `TIPO_ATTIVITA` | String | Tipologia di attività (Ricoveri ordinari, Day Hospital, Day Surgery) | Ricoveri ordinari |
| `N_DIMISSIONI` | Integer | Numero totale di dimissioni per la combinazione di variabili | 1250 |

### 2. `dimissioni_ospedaliere_tipologia.csv`

| Nome Colonna | Tipo Dati | Descrizione | Esempio |
|---|---|---|---|
| `ANNO` | Integer | Anno di riferimento della dimissione | 2023 |
| `COD_REG` | String | Codice ISTAT della Regione | 090 |
| `DESC_REG` | String | Descrizione della Regione | Lombardia |
| `COD_STRUTTURA` | String | Codice univoco della struttura ospedaliera | 030101 |
| `DESC_STRUTTURA` | String | Denominazione della struttura ospedaliera | PRESIDIO OSPEDALIERO DI SONDRIO |
| `TIPO_ISTITUTO` | String | Tipologia di istituto (Pubblico, Privato accreditato) | Pubblico |
| `TIPO_DIMISSIONE` | String | Modalità di dimissione (Ordinaria, Trasferimento, Decesso) | Ordinaria |
| `N_DIMISSIONI` | Integer | Numero totale di dimissioni per la combinazione di variabili | 850 |

---

## Note Metodologiche

- I dati sono aggregati a livello regionale e per singola struttura.
- La classificazione delle diagnosi e delle procedure segue lo standard ICD-9-CM.
- I dati sono resi disponibili annualmente, solitamente con un ritardo di circa 12-18 mesi.
