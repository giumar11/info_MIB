Analisi criticità indirizzamento servizi sociosanitari Italia

Questo repository contiene un'analisi dei problemi di indirizzamento in ambito sociosanitario in Italia. L'obiettivo è fornire una base di dati strutturata per lo sviluppo di strumenti informativi in grado di navigare queste informazioni.

Il progetto si basa su fonti dati istituzionali pubbliche e aggiornate, tra cui ISTAT, Ministero della Salute, Istituto Superiore di Sanità (ISS) e Orphanet.

---

## Sezione 1: Analisi criticità sistema sanitario

Questa sezione contiene una raccolta di report e fonti dati che analizzano le principali problematiche del sistema sanitario italiano e lo confrontano con altri paesi.

**Tematiche:**
- Carenza di personale medico e infermieristico
- Liste d'attesa e rinuncia alle cure
- Spesa sanitaria out-of-pocket e privatizzazione
- Welfare sanitario e fondi integrativi
- Performance e disuguaglianze regionali
- Confronti internazionali (USA, Europa)

**Documentazione:**
- `docs/sistema_sanitario/CATALOGO_FONTI.md`: Catalogo completo delle fonti dati con link e analisi.

**Dataset:**
- `datasets/raw/sistema_sanitario/`: Cartella contenente i report originali in formato PDF (oltre 100 MB di dati).

---
  
## Sezione 2: Patologie a elevata complessità

### Metodologia

Per stimare quali patologie richiedano il consulto del maggior numero di specialisti, abbiamo utilizzato un approccio basato su **indicatori proxy**. Non esistendo un dato diretto sul "numero di specialisti per patologia", abbiamo identificato delle categorie di condizioni che, per loro natura, implicano un percorso di cura e diagnosi complesso e multidisciplinare.

I principali proxy utilizzati sono:

1.  **Malattie rare**: Per definizione, queste patologie hanno una bassa prevalenza, il che comporta spesso un'odissea diagnostica e la necessità di consultare numerosi specialisti e centri di riferimento.
2.  **Patologie oncologiche**: I tumori richiedono un approccio gestito da un team multidisciplinare (GOM o MDT) che include oncologo, chirurgo, radioterapista, anatomo-patologo e altri specialisti d'organo.
3.  **Multimorbidità negli anziani**: La coesistenza di tre o più patologie croniche nella popolazione anziana (over 65) implica la gestione coordinata da parte di più medici (MMG, geriatra, specialisti d'organo).
4.  **Patologie croniche complesse**: Condizioni come il diabete con complicanze, lo scompenso cardiaco o le malattie autoimmuni sistemiche colpiscono più organi e apparati, rendendo necessario l'intervento di diversi specialisti.

### Fonti dati

Sono state raccolte e analizzate le seguenti fonti dati istituzionali:

| Fonte | Dataset | Descrizione | Anno | Formato originale |
|---|---|---|---|---|
| **Orphanet** | Dati epidemiologici malattie rare | Contiene dati di prevalenza, incidenza, età di esordio e classificazione per 6.443 malattie rare. | 2025 | XML |
| **Ministero della Salute** | Rapporto annuale SDO | Dati sui ricoveri ospedalieri, classificati per MDC (Major Diagnostic Category) e DRG. | 2023 | PDF, XLSX |
| **ISTAT** | Health for All (HFA) | Database con 4.000 indicatori su salute e sanità, incluse le patologie croniche dichiarate. | 2025 | DBF/Proprietario |
| **ISTAT** | Report "Condizioni di salute degli anziani" | Analisi sulla multimorbidità e le condizioni di vita della popolazione over 65. | 2019 | PDF |
| **ISS** | Sorveglianza PASSI e PASSI d'Argento | Dati su fattori di rischio e prevalenza delle patologie croniche nella popolazione adulta e anziana. | Vari | Web/PDF |

### Struttura dei dataset

-   `/datasets/raw`: Contiene i dataset originali scaricati dalle fonti istituzionali.
-   `/datasets/processed`: Contiene i dataset puliti, strutturati e arricchiti in formato CSV e JSON, pronti per essere utilizzati.
-   `/scripts`: Contiene gli script Python utilizzati per il download, la pulizia, l'analisi e la generazione dei dataset processati.
-   `/docs`: Documentazione di dettaglio sui singoli dataset e sulle variabili.
-   `/docs/FONTI_DATI.md`: Elenco completo di tutte le fonti dati istituzionali con URL e descrizioni.


---

*Questo progetto è stato realizzato da Geen.ai SRL a scopo dimostrativo per l'analisi di dati sanitari pubblici. I dati aggregati e le analisi prodotte sono il risultato di elaborazioni e non sostituiscono una valutazione medica o rappresentano fonti ufficiali.*
