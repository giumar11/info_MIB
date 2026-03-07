# Documentazione dei Dataset Processati

Questa documentazione descrive i dataset generati e disponibili nella cartella `/datasets/processed`.

---

## 1. Patologie Multidisciplinari (`pdta_multidisciplinari.json` e `.csv`)

Questo dataset elenca una selezione di patologie note per richiedere un approccio multidisciplinare, basato su linee guida cliniche e dati di prevalenza.

-   **Formato**: JSON, CSV
-   **Fonte Principale**: Elaborazione basata su linee guida AIOM, AMD-SID, SIR, AISM e dati ISTAT/SDO.

### Struttura dei dati (JSON)

```json
[
  {
    "patologia": "Tumore della mammella",
    "codice_icd10": "C50",
    "specialisti_coinvolti": [
      "Senologo",
      "Oncologo medico",
      "Radioterapista",
      "Chirurgo plastico",
      "Psicologo",
      "Radiologo",
      "Anatomo-patologo"
    ],
    "n_specialisti": 7,
    "prevalenza_italia": "1 donna su 8",
    "fonte": "AIOM, Rapporto SDO"
  },
  ...
]
```

### Campi

| Campo | Descrizione |
|---|---|
| `patologia` | Nome comune della patologia. |
| `codice_icd10` | Codice di classificazione internazionale delle malattie (ICD-10). |
| `specialisti_coinvolti` | Elenco degli specialisti tipicamente coinvolti nel percorso di cura. |
| `n_specialisti` | Numero di specialisti elencati. |
| `prevalenza_italia` | Stima della prevalenza o incidenza in Italia. |
| `fonte` | Fonti utilizzate per definire il percorso. |

---

## 2. Malattie Rare Italia (`malattie_rare_italia.json` e `.csv`)

Dataset completo delle malattie rare con dati epidemiologici estratti da Orphadata, arricchito con un indice di complessità.

-   **Formato**: JSON, CSV
-   **Fonte Principale**: Orphadata (Dicembre 2025)

### Struttura dei dati (JSON)

```json
[
  {
    "orpha_code": "558",
    "name": "Sindrome di Aarskog",
    "prevalence_class": "1-9 / 100 000",
    "age_of_onset": "Infancy, Neonatal",
    "complexity_score": 5,
    "complexity_level": "Alta"
  },
  ...
]
```

### Campi Principali

| Campo | Descrizione |
|---|---|
| `orpha_code` | Identificativo univoco Orphanet. |
| `name` | Nome della malattia. |
| `prevalence_class` | Classe di prevalenza (es. "<1 / 1 000 000"). |
| `age_of_onset` | Periodo tipico di esordio della malattia. |
| `complexity_score` | Punteggio numerico calcolato per stimare la complessità (basato su prevalenza ed età di esordio). |
| `complexity_level` | Categoria di complessità (Bassa, Media, Alta, Molto Alta). |

---

## 3. Segmentazione Popolazione (`segmentazione_popolazione.json`)

Fornisce dati demografici e sanitari per segmentare la popolazione italiana per rischio e carico di patologie.

-   **Formato**: JSON
-   **Fonte Principale**: Elaborazione su dati ISTAT, PASSI, PASSI d'Argento.

### Struttura dei dati

Il file JSON è strutturato in sezioni:

-   `popolazione_totale`: Popolazione italiana al 2023.
-   `per_fascia_eta`: Dati per 6 fasce d'età, con popolazione e numero medio di patologie croniche.
-   `per_genere`: Suddivisione della popolazione per maschi e femmine.
-   `multimorbidita`: Dati specifici sulle persone con 3 o più patologie croniche.
-   `patologie_croniche_prevalenti`: Elenco delle 10 patologie croniche più diffuse in Italia con stima della popolazione affetta.

---

## 4. Riepilogo SDO 2023 (`riepilogo_sdo_2023.json`)

Contiene dati aggregati estratti e rielaborati dal Rapporto annuale sull'attività di ricovero ospedaliero (SDO) per l'anno 2023.

-   **Formato**: JSON
-   **Fonte Principale**: Ministero della Salute - Rapporto SDO 2023.

### Struttura dei dati

Il file JSON è strutturato in sezioni:

-   `ricoveri_totali`: Numero totale di ricoveri suddivisi per regime (acuti, riabilitazione, etc.).
-   `principali_mdc`: Le 8 Major Diagnostic Categories con il maggior numero di ricoveri.
-   `drg_frequenti_complessi`: Una selezione di DRG (Diagnosis-Related Group) che rappresentano procedure complesse.
-   `distribuzione_eta`: Suddivisione percentuale e assoluta dei ricoveri per fascia d'età.
-   `distribuzione_genere`: Suddivisione percentuale e assoluta dei ricoveri per genere.
