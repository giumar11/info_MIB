# Proposta Schema Database per Geen.ai

**Autore:** Manus AI  
**Data:** 30 Gennaio 2026  
**Versione:** 1.0

---

## Sommario Esecutivo

Questo documento presenta la proposta di schema database per il progetto Geen.ai, un sistema informativo che raccoglie dati sanitari istituzionali italiani per identificare le patologie che richiedono la consultazione di più specialisti. Lo schema è stato progettato per supportare un chatbot conversazionale che permetta agli utenti di interrogare informazioni su patologie, specialisti coinvolti e segmentazione della popolazione italiana.

L'analisi dei dataset disponibili ha identificato **6.453 patologie** (di cui 6.443 malattie rare da Orphadata e 10 patologie complesse con PDTA definiti), **32 specializzazioni mediche** e dati demografici su **59 milioni di abitanti** segmentati per età, genere e prevalenza di patologie croniche.

---

## Dataset Analizzati

| Dataset | Formato | Record | Contenuto Principale |
|---------|---------|--------|----------------------|
| malattie_rare_italia.json | JSON | 6.443 | Malattie rare con codice Orphanet, prevalenza, complessità |
| pdta_multidisciplinari.json | JSON | 10 | Patologie complesse con elenco specialisti coinvolti |
| segmentazione_popolazione.json | JSON | 1 | Dati demografici ISTAT per fasce d'età e genere |
| riepilogo_sdo_2023.json | JSON | 1 | Ricoveri ospedalieri per MDC e DRG |
| dimissioni_ospedaliere_*.csv | CSV | 2.727 | Dimissioni per istituto, età, sesso, tipologia |

---

## Architettura Proposta

Per il chatbot Geen.ai si raccomanda un'architettura **ibrida** che combini i vantaggi di entrambi i paradigmi:

| Aspetto | SQL (PostgreSQL) | NoSQL (MongoDB) |
|---------|------------------|-----------------|
| **Uso principale** | Data warehouse, analytics | API chatbot, query real-time |
| **Struttura** | Normalizzata (3NF) | Denormalizzata (documenti) |
| **Query tipiche** | Aggregazioni, JOIN complessi | Lookup per patologia/specialista |
| **Scalabilità** | Verticale | Orizzontale |
| **Consistenza** | ACID | Eventual consistency |

La raccomandazione è di utilizzare **MongoDB** come database primario per il chatbot, grazie alla sua capacità di gestire documenti denormalizzati che contengono tutte le informazioni necessarie per rispondere a una query in un singolo accesso. PostgreSQL può essere utilizzato come data warehouse per analisi più complesse e per alimentare periodicamente MongoDB con dati aggregati.

---

## Schema SQL Relazionale

Lo schema SQL è stato progettato seguendo la terza forma normale (3NF) per garantire integrità referenziale e minimizzare la ridondanza dei dati. Le tabelle principali sono:

### Tabelle Principali

**patologie** - Tabella centrale che contiene tutte le patologie, sia comuni che rare. Include campi per codici ICD-10 e Orphanet, classificazione per tipo, dati di prevalenza e un punteggio di complessità (0-10) che indica quanti specialisti sono tipicamente coinvolti nel percorso di cura.

**specialisti** - Elenco delle specializzazioni mediche con classificazione per area medica (es. Cardiologia, Neurologia) e tipo (medico, chirurgico, diagnostico, riabilitativo, supporto).

**patologie_specialisti** - Tabella di relazione many-to-many che associa ogni patologia agli specialisti coinvolti, specificando il ruolo (primario, consulente) e la fase del percorso (diagnosi, trattamento, follow-up, riabilitazione).

**fasce_eta** - Segmentazione demografica della popolazione italiana per fasce d'età, con dati su popolazione totale, percentuale e media di patologie croniche per fascia.

**prevalenze** - Dati epidemiologici che collegano patologie e fasce d'età, con possibilità di segmentare per genere e regione.

### Indici Ottimizzati

Per supportare le query tipiche del chatbot, sono stati definiti indici su:
- Full-text search sul nome delle patologie (GIN index con dizionario italiano)
- Tipo di patologia per filtri rapidi
- Relazioni patologia-specialista per JOIN efficienti
- Fascia d'età e genere per query demografiche

Lo schema SQL completo è disponibile nel file `schema.sql`.

---

## Schema NoSQL per Chatbot

Lo schema NoSQL è stato progettato per massimizzare le performance delle query conversazionali, denormalizzando i dati in documenti auto-contenuti.

### Collection "patologie"

Ogni documento rappresenta una singola patologia e contiene tutte le informazioni necessarie per rispondere alle domande più comuni:

```json
{
  "nome": "Diabete mellito tipo 2 complicato",
  "codice_icd10": "E11",
  "tipo": "comune",
  "complessita": {
    "score": 7,
    "livello": "alta"
  },
  "specialisti": [
    {"nome": "Diabetologo", "ruolo": "primario"},
    {"nome": "Cardiologo", "ruolo": "consulente"},
    {"nome": "Nefrologo", "ruolo": "consulente"},
    {"nome": "Oculista", "ruolo": "consulente"},
    {"nome": "Neurologo", "ruolo": "consulente"},
    {"nome": "Podologo", "ruolo": "supporto"},
    {"nome": "Dietista", "ruolo": "supporto"}
  ],
  "prevalenza": {
    "classe": "3.5 milioni di persone",
    "geo": "Italia",
    "fonte": "AMD-SID, ISTAT"
  },
  "fonti": [
    {"nome": "AMD-SID", "url": null},
    {"nome": "ISTAT", "url": "https://www.istat.it"}
  ]
}
```

Questa struttura permette di rispondere a domande come "Quali specialisti devo consultare per il diabete?" con una singola query, senza necessità di JOIN.

### Collection "popolazione_segmenti"

Contiene dati aggregati sulla popolazione italiana per supportare query demografiche:

```json
{
  "anno_riferimento": 2023,
  "tipo_segmento": "fascia_eta",
  "segmento": "75+",
  "popolazione": 7800000,
  "percentuale": 13.2,
  "patologie_croniche_media": 3.5
}
```

Lo schema NoSQL completo è disponibile nel file `schema_nosql.json`.

---

## Query Tipiche del Chatbot

La tabella seguente mostra come le query conversazionali più comuni vengono tradotte in operazioni database:

| Domanda Utente | Query MongoDB | Complessità |
|----------------|---------------|-------------|
| "Quali specialisti per il diabete?" | `db.patologie.findOne({nome: /diabete/i}, {specialisti: 1})` | O(1) |
| "Quante persone hanno malattie rare?" | `db.patologie.aggregate([{$match: {tipo: "rara"}}, {$group: {_id: null, tot: {$sum: "$prevalenza.valore_stimato"}}}])` | O(n) |
| "Patologie più comuni negli over 65?" | `db.patologie.find({"segmenti_demografici.fascia_eta": "65-74"}).sort({"segmenti_demografici.prevalenza_percentuale": -1})` | O(log n) |
| "Patologia con più specialisti?" | `db.patologie.find().sort({"complessita.score": -1}).limit(1)` | O(log n) |

---

## Script di Migrazione

È stato creato lo script `scripts/migrate_to_database.py` che trasforma i dataset JSON/CSV originali nei formati pronti per l'importazione:

| File Output | Contenuto | Record |
|-------------|-----------|--------|
| sql_import_data.json | Dati normalizzati per PostgreSQL | 6.500+ |
| nosql_patologie_collection.json | Documenti denormalizzati per MongoDB | 6.453 |
| nosql_segmenti_collection.json | Segmenti demografici | 6 |

Per eseguire la migrazione:

```bash
cd /home/ubuntu/Geen.ai
python3 scripts/migrate_to_database.py
```

---

## Raccomandazioni per il Chatbot

### Architettura Consigliata

Per il chatbot conversazionale si raccomanda la seguente architettura:

1. **Database primario**: MongoDB Atlas (managed service) per semplicità operativa e scalabilità automatica
2. **Ricerca full-text**: MongoDB Atlas Search con analizzatore italiano per query in linguaggio naturale
3. **Cache**: Redis per caching delle query più frequenti (es. "diabete", "tumore")
4. **Vector database** (opzionale): Pinecone o MongoDB Atlas Vector Search per semantic search con embeddings

### Modularità Regionale

Seguendo il principio di architettura modulare, lo schema supporta l'estensione con dati regionali:

- **Modulo base**: Patologie, specialisti, prevalenze nazionali (già implementato)
- **Modulo regionale**: Aggiungere campo `regione_codice` alle prevalenze e ai PDTA per dati specifici per regione
- **Modulo istituzionale**: Collegare istituti sanitari e centri di riferimento per malattie rare

### Prossimi Passi

1. Creare un'istanza MongoDB Atlas e importare i dati con `mongoimport`
2. Configurare gli indici full-text con analizzatore italiano
3. Sviluppare l'API REST per il chatbot (FastAPI consigliato)
4. Integrare con un LLM (GPT-4, Claude) per la comprensione del linguaggio naturale
5. Arricchire i dati con mapping ICD-10 completo per le malattie rare

---

## File Inclusi

| File | Descrizione |
|------|-------------|
| `docs/database_design/schema.sql` | Schema SQL completo per PostgreSQL |
| `docs/database_design/schema_nosql.json` | Schema NoSQL per MongoDB |
| `docs/database_design/entity_analysis.md` | Analisi dettagliata delle entità |
| `scripts/migrate_to_database.py` | Script Python per la migrazione |
| `datasets/migration_ready/` | Dati pronti per l'importazione |

---

## Riferimenti

[1] Orphadata - Epidemiology of rare diseases: https://www.orphadata.com/epidemiology/  
[2] Ministero della Salute - Rapporto SDO 2023: https://www.salute.gov.it/  
[3] ISTAT - Health for All Italia: https://www.istat.it/sistema-informativo-6/health-for-all-italia/  
[4] MongoDB Documentation - Data Modeling: https://www.mongodb.com/docs/manual/core/data-modeling-introduction/  
[5] PostgreSQL Documentation - Full Text Search: https://www.postgresql.org/docs/current/textsearch.html
