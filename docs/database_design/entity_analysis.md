# Analisi delle Entità e Relazioni - Dataset Sanitari Italia

## Riepilogo Dataset Analizzati

| Dataset | Formato | Record | Entità Principali |
|---------|---------|--------|-------------------|
| malattie_rare_italia.json | JSON | 6.443 | Malattie rare, prevalenza, complessità |
| pdta_multidisciplinari.json | JSON | 10 | Patologie complesse, specialisti |
| segmentazione_popolazione.json | JSON | 1 | Fasce età, genere, patologie croniche |
| riepilogo_sdo_2023.json | JSON | 1 | Ricoveri, MDC, DRG |
| dimissioni_ospedaliere_*.csv | CSV | 2.727 | Istituti, dimissioni per età/sesso |

---

## Entità Identificate

### 1. PATOLOGIA (Entità Centrale)
Rappresenta una condizione medica o malattia.

**Attributi:**
- `id` (PK): Identificativo univoco
- `nome`: Nome della patologia
- `codice_icd10`: Codice ICD-10 (standard internazionale)
- `codice_orpha`: Codice Orphanet (per malattie rare)
- `tipo`: Enum (comune, rara, oncologica, autoimmune, neurologica)
- `prevalenza_classe`: Classe di prevalenza (es. "<1/1.000.000")
- `prevalenza_valore`: Valore numerico stimato
- `eta_esordio`: Età tipica di esordio
- `complessita_score`: Punteggio 0-10
- `complessita_livello`: Enum (bassa, media, alta)
- `descrizione`: Descrizione testuale
- `fonte`: Fonte dati primaria

### 2. SPECIALISTA
Rappresenta una specializzazione medica.

**Attributi:**
- `id` (PK): Identificativo univoco
- `nome`: Nome della specializzazione (es. "Cardiologo")
- `area_medica`: Area di appartenenza (es. "Cardiologia")
- `tipo`: Enum (medico, chirurgico, diagnostico, riabilitativo)

### 3. PATOLOGIA_SPECIALISTA (Relazione N:M)
Associa patologie agli specialisti coinvolti nel percorso di cura.

**Attributi:**
- `patologia_id` (FK)
- `specialista_id` (FK)
- `ruolo`: Enum (primario, consulente, supporto)
- `fase`: Enum (diagnosi, trattamento, follow_up, riabilitazione)
- `obbligatorio`: Boolean

### 4. FASCIA_ETA
Segmentazione demografica per età.

**Attributi:**
- `id` (PK)
- `codice`: Codice fascia (es. "65-74")
- `eta_min`: Età minima
- `eta_max`: Età massima
- `popolazione`: Numero abitanti
- `percentuale_popolazione`: % su totale
- `patologie_croniche_media`: Media patologie croniche

### 5. PREVALENZA_PATOLOGIA
Dati epidemiologici per patologia e segmento demografico.

**Attributi:**
- `id` (PK)
- `patologia_id` (FK)
- `fascia_eta_id` (FK)
- `genere`: Enum (M, F, tutti)
- `regione`: Codice regione (opzionale)
- `prevalenza_percentuale`: % popolazione affetta
- `popolazione_affetta`: Numero assoluto
- `anno_riferimento`: Anno del dato
- `fonte`: Fonte dati

### 6. ISTITUTO_SANITARIO
Strutture ospedaliere e sanitarie.

**Attributi:**
- `id` (PK)
- `codice_ministero`: Codice identificativo ministeriale
- `denominazione`: Nome struttura
- `regione`: Codice regione
- `provincia`: Codice provincia
- `tipo`: Enum (ospedale, IRCCS, casa_cura, ASL)

### 7. RICOVERO_AGGREGATO
Dati aggregati sui ricoveri per istituto.

**Attributi:**
- `id` (PK)
- `istituto_id` (FK)
- `anno`: Anno di riferimento
- `fascia_eta_id` (FK)
- `genere`: Enum (M, F)
- `numero_ricoveri`: Conteggio
- `tipologia_dimissione`: Enum (domicilio, decesso, altra_struttura)

### 8. MDC (Major Diagnostic Category)
Categorie diagnostiche maggiori per classificazione ricoveri.

**Attributi:**
- `id` (PK)
- `codice`: Codice MDC (es. "MDC 05")
- `descrizione`: Descrizione categoria
- `ricoveri_annui`: Numero ricoveri/anno

### 9. PDTA (Percorso Diagnostico Terapeutico Assistenziale)
Percorsi clinici standardizzati per patologie complesse.

**Attributi:**
- `id` (PK)
- `patologia_id` (FK)
- `nome`: Nome del PDTA
- `regione`: Regione di riferimento (opzionale per PDTA nazionali)
- `fonte`: Fonte normativa/linee guida

### 10. FONTE_DATI
Metadati sulle fonti dati.

**Attributi:**
- `id` (PK)
- `nome`: Nome fonte (es. "Orphadata")
- `url`: URL di riferimento
- `tipo`: Enum (istituzionale, registro, survey)
- `frequenza_aggiornamento`: Enum (annuale, trimestrale, continuo)
- `ultimo_aggiornamento`: Data

---

## Relazioni Principali

```
PATOLOGIA 1---N PATOLOGIA_SPECIALISTA N---1 SPECIALISTA
PATOLOGIA 1---N PREVALENZA_PATOLOGIA N---1 FASCIA_ETA
PATOLOGIA 1---N PDTA
ISTITUTO_SANITARIO 1---N RICOVERO_AGGREGATO N---1 FASCIA_ETA
MDC 1---N PATOLOGIA (classificazione)
FONTE_DATI 1---N PATOLOGIA (provenienza)
```

---

## Query Tipiche del Chatbot

1. **"Quali specialisti devo consultare per il diabete?"**
   - JOIN PATOLOGIA → PATOLOGIA_SPECIALISTA → SPECIALISTA
   - WHERE patologia.nome LIKE '%diabete%'

2. **"Quante persone in Italia hanno malattie rare?"**
   - SUM su PATOLOGIA WHERE tipo = 'rara'
   - JOIN PREVALENZA_PATOLOGIA

3. **"Quali sono le patologie più comuni negli over 65?"**
   - JOIN PREVALENZA_PATOLOGIA → FASCIA_ETA
   - WHERE fascia_eta.eta_min >= 65
   - ORDER BY prevalenza_percentuale DESC

4. **"Qual è la patologia che richiede più specialisti?"**
   - COUNT su PATOLOGIA_SPECIALISTA
   - GROUP BY patologia_id
   - ORDER BY count DESC

5. **"Dammi informazioni sulla sclerosi multipla"**
   - SELECT * FROM PATOLOGIA
   - JOIN PATOLOGIA_SPECIALISTA, PREVALENZA_PATOLOGIA, PDTA
   - WHERE nome = 'Sclerosi multipla'
