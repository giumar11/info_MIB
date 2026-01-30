# Geen.ai - Analisi delle patologie a elevata complessità assistenziale in Italia

Questo repository contiene l'applicazione Geen.ai e un'analisi delle patologie che richiedono un elevato livello di complessità assistenziale in Italia, con un focus sull'identificazione di condizioni che necessitano della consultazione di molteplici specialisti. L'obiettivo è fornire una base di dati strutturata per lo sviluppo di strumenti informativi, come un chatbot, in grado di navigare queste informazioni.

Il progetto si basa su fonti dati istituzionali pubbliche e aggiornate, tra cui ISTAT, Ministero della Salute, Istituto Superiore di Sanità (ISS) e Orphanet.

---

## Applicazione React

### Getting started

```bash
npm i
npm start
```

### Managing the database

```bash
npx prisma studio
```

---

## Dataset Sanitari

### Metodologia

Per stimare quali patologie richiedano il consulto del maggior numero di specialisti, abbiamo utilizzato un approccio basato su **indicatori proxy**. Non esistendo un dato diretto sul "numero di specialisti per patologia", abbiamo identificato delle categorie di condizioni che, per loro natura, implicano un percorso di cura e diagnosi complesso e multidisciplinare.

I principali proxy utilizzati sono:

1.  **Malattie Rare**: Per definizione, queste patologie hanno una bassa prevalenza, il che comporta spesso un'odissea diagnostica e la necessità di consultare numerosi specialisti e centri di riferimento.
2.  **Patologie Oncologiche**: I tumori richiedono un approccio gestito da un team multidisciplinare (GOM o MDT) che include oncologo, chirurgo, radioterapista, anatomo-patologo e altri specialisti d'organo.
3.  **Multimorbidità negli Anziani**: La coesistenza di tre o più patologie croniche nella popolazione anziana (over 65) implica la gestione coordinata da parte di più medici (MMG, geriatra, specialisti d'organo).
4.  **Patologie Croniche Complesse**: Condizioni come il diabete con complicanze, lo scompenso cardiaco o le malattie autoimmuni sistemiche colpiscono più organi e apparati, rendendo necessario l'intervento di diversi specialisti.

### Fonti Dati

Sono state raccolte e analizzate le seguenti fonti dati istituzionali:

| Fonte | Dataset | Descrizione | Anno | Formato Originale |
|---|---|---|---|---|
| **Orphanet** | Dati epidemiologici malattie rare | Contiene dati di prevalenza, incidenza, età di esordio e classificazione per 6.443 malattie rare. | 2025 | XML |
| **Ministero della Salute** | Rapporto annuale SDO | Dati sui ricoveri ospedalieri, classificati per MDC (Major Diagnostic Category) e DRG. | 2023 | PDF, XLSX |
| **ISTAT** | Health for All (HFA) | Database con 4.000 indicatori su salute e sanità, incluse le patologie croniche dichiarate. | 2025 | DBF/Proprietario |
| **ISTAT** | Report "Condizioni di salute degli anziani" | Analisi sulla multimorbidità e le condizioni di vita della popolazione over 65. | 2019 | PDF |
| **ISS** | Sorveglianza PASSI e PASSI d'Argento | Dati su fattori di rischio e prevalenza delle patologie croniche nella popolazione adulta e anziana. | Vari | Web/PDF |
| **GIMBE** | 8° Rapporto sul SSN | Analisi critica su spesa sanitaria, mobilità sanitaria, rinuncia alle cure. | 2024 | PDF |
| **UNIAMO** | Report Malattie Rare 2024 | Federazione Italiana Malattie Rare - Report annuale. | 2024 | PDF |
| **Osservatorio sulla Salute** | Rapporto 2025 | Stato di salute delle regioni italiane. | 2025 | PDF |
| **ENPAM** | Guida Specialisti Ambulatoriali | Accordo Collettivo Nazionale, medicina territoriale. | 2024 | PDF |
| **AGENAS** | Portale Statistico | Volumi prestazioni specialistiche, tempi di attesa. | 2025 | Dashboard |

### Risultati Principali

Dall'analisi dei dati sono emersi i seguenti cluster di patologie a elevata complessità assistenziale, che rappresentano un buon proxy per le condizioni che richiedono il maggior numero di specialisti.

#### Patologie a Maggiore Complessità per Numero Medio di Specialisti

| Categoria di Patologia | N. Medio Specialisti Coinvolti | Specialisti Tipici | Fonte Dati Primaria |
|---|---|---|---|
| **Malattie Rare** | 6-7+ | Genetista, Specialisti d'organo multipli, Centro di Riferimento | Orphadata, Registro Malattie Rare |
| **Tumori Solidi Complessi** | 5-7 | Oncologo, Chirurgo, Radioterapista, Anatomo-patologo, Radiologo | Rapporto SDO, Linee Guida AIOM |
| **Malattie Autoimmuni Sistemiche** | 5-6 | Reumatologo, Immunologo, Nefrologo, Dermatologo, Pneumologo | ISTAT HFA, Registri di patologia |
| **Multimorbidità nell'Anziano (3+ patologie)** | 5+ | Geriatra, Medico di Medicina Generale, Cardiologo, Diabetologo, Fisiatra | ISTAT Report Anziani, PASSI d'Argento |
| **Diabete con Complicanze Multiple** | 4-6 | Diabetologo, Cardiologo, Nefrologo, Oculista, Neurologo, Podologo | Standard AMD-SID, PASSI |
| **Scompenso Cardiaco Cronico Avanzato** | 4-6 | Cardiologo, Internista, Nefrologo, Pneumologo, Geriatra, Palliativista | Rapporto SDO, Linee Guida ESC |

#### Segmentazione per Età e Carico di Patologie Croniche

| Fascia d'Età | Popolazione (2023) | % Popolazione | N. Medio Patologie Croniche | Note |
|---|---|---|---|---|
| 0-14 | 7.500.000 | 12.7% | 0.2 | Prevalenza di malattie rare e congenite. |
| 15-44 | 19.000.000 | 32.2% | 0.4 | Bassa prevalenza di cronicità. |
| 45-64 | 17.500.000 | 29.7% | 1.2 | Aumento incidenza tumori e malattie cardiovascolari. |
| **65-74** | 7.200.000 | 12.2% | **2.3** | Inizio della multimorbidità. |
| **75+** | 7.800.000 | 13.2% | **3.5+** | Elevata prevalenza di multimorbidità e non autosufficienza. |

*Fonte: Elaborazione su dati ISTAT, PASSI, PASSI d'Argento.*

### Struttura dei Dataset

-   `/datasets/raw`: Contiene i dataset originali scaricati dalle fonti istituzionali.
-   `/datasets/processed`: Contiene i dataset puliti, strutturati e arricchiti in formato CSV e JSON, pronti per essere utilizzati.
-   `/scripts`: Contiene gli script Python utilizzati per il download, la pulizia, l'analisi e la generazione dei dataset processati.
-   `/docs`: Documentazione di dettaglio sui singoli dataset e sulle variabili.
-   `/docs/FONTI_DATI.md`: Elenco completo di tutte le fonti dati istituzionali con URL e descrizioni.

### Come Utilizzare i Dati per il Chatbot

I dataset nella cartella `/datasets/processed` sono il punto di partenza ideale per alimentare un chatbot o altri sistemi informativi. In particolare:

-   `pdta_multidisciplinari.json`: Fornisce un elenco di patologie complesse con gli specialisti tipicamente coinvolti.
-   `malattie_rare_italia.json`: Contiene l'elenco delle malattie rare con dati di prevalenza e un punteggio di complessità calcolato.
-   `segmentazione_popolazione.json`: Offre dati aggregati per segmentare la popolazione per età, genere e carico di patologie.

---

*Questo progetto è stato realizzato a scopo dimostrativo per l'analisi di dati sanitari pubblici. I dati aggregati e le analisi prodotte sono il risultato di elaborazioni e non sostituiscono una valutazione medica o rappresentano fonti ufficiali.*
