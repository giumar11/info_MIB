```sql
-- Schema SQL per il database Geen.ai
-- Dialetto: PostgreSQL

-- Enum Types per consistenza dati
CREATE TYPE tipo_patologia AS ENUM (
    'comune',
    'rara',
    'oncologica',
    'autoimmune',
    'neurologica',
    'cardiovascolare',
    'respiratoria'
);

CREATE TYPE livello_complessita AS ENUM ('bassa', 'media', 'alta');
CREATE TYPE tipo_specialista AS ENUM ('medico', 'chirurgico', 'diagnostico', 'riabilitativo', 'supporto');
CREATE TYPE ruolo_specialista AS ENUM ('primario', 'consulente', 'supporto');
CREATE TYPE fase_pdta AS ENUM ('diagnosi', 'trattamento', 'follow_up', 'riabilitazione');

-- Tabella centrale delle patologie
CREATE TABLE patologie (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(255) NOT NULL UNIQUE,
    codice_icd10 VARCHAR(20),
    codice_orpha VARCHAR(20) UNIQUE,
    tipo tipo_patologia DEFAULT 'comune',
    descrizione TEXT,
    prevalenza_classe VARCHAR(50),
    prevalenza_valore INT,
    eta_esordio VARCHAR(100),
    complessita_score SMALLINT CHECK (complessita_score >= 0 AND complessita_score <= 10),
    complessita_livello livello_complessita,
    fonte_dati_id INT REFERENCES fonti_dati(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tabella degli specialisti
CREATE TABLE specialisti (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL UNIQUE,
    area_medica VARCHAR(100),
    tipo tipo_specialista
);

-- Tabella di relazione N:M tra patologie e specialisti
CREATE TABLE patologie_specialisti (
    patologia_id INT REFERENCES patologie(id) ON DELETE CASCADE,
    specialista_id INT REFERENCES specialisti(id) ON DELETE CASCADE,
    ruolo ruolo_specialista DEFAULT 'consulente',
    fase fase_pdta,
    obbligatorio BOOLEAN DEFAULT FALSE,
    note TEXT,
    PRIMARY KEY (patologia_id, specialista_id)
);

-- Tabella per la segmentazione demografica
CREATE TABLE fasce_eta (
    id SERIAL PRIMARY KEY,
    codice VARCHAR(10) NOT NULL UNIQUE, -- es. '65-74'
    eta_min SMALLINT,
    eta_max SMALLINT,
    popolazione BIGINT,
    percentuale_popolazione NUMERIC(5, 2),
    patologie_croniche_media NUMERIC(4, 2)
);

-- Tabella per i dati di prevalenza
CREATE TABLE prevalenze (
    id SERIAL PRIMARY KEY,
    patologia_id INT REFERENCES patologie(id) ON DELETE CASCADE,
    fascia_eta_id INT REFERENCES fasce_eta(id),
    genere CHAR(1) CHECK (genere IN ('M', 'F', 'A')), -- A = Tutti
    regione_codice VARCHAR(3), -- Codice ISTAT regione
    prevalenza_percentuale NUMERIC(6, 3),
    popolazione_affetta INT,
    anno_riferimento SMALLINT,
    fonte_dati_id INT REFERENCES fonti_dati(id)
);

-- Tabella per le fonti dati
CREATE TABLE fonti_dati (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(150) NOT NULL UNIQUE,
    url VARCHAR(512),
    tipo VARCHAR(50),
    frequenza_aggiornamento VARCHAR(50),
    ultimo_aggiornamento DATE
);

-- Tabella per gli istituti sanitari
CREATE TABLE istituti_sanitari (
    id SERIAL PRIMARY KEY,
    codice_ministero VARCHAR(20) NOT NULL UNIQUE,
    denominazione VARCHAR(255),
    regione_codice VARCHAR(3),
    provincia_codice VARCHAR(3)
);

-- Tabella per i dati aggregati sui ricoveri
CREATE TABLE ricoveri_aggregati (
    id SERIAL PRIMARY KEY,
    istituto_id INT REFERENCES istituti_sanitari(id),
    anno SMALLINT,
    fascia_eta_id INT REFERENCES fasce_eta(id),
    genere CHAR(1) CHECK (genere IN ('M', 'F')),
    numero_ricoveri INT,
    numero_decessi INT,
    numero_dimissioni_domicilio INT,
    numero_dimissioni_altra_struttura INT
);

-- Tabella per le Major Diagnostic Categories (MDC)
CREATE TABLE mdc (
    id SERIAL PRIMARY KEY,
    codice VARCHAR(10) NOT NULL UNIQUE,
    descrizione VARCHAR(255),
    ricoveri_annui INT
);

-- Relazione tra patologie e MDC
CREATE TABLE patologie_mdc (
    patologia_id INT REFERENCES patologie(id) ON DELETE CASCADE,
    mdc_id INT REFERENCES mdc(id) ON DELETE CASCADE,
    PRIMARY KEY (patologia_id, mdc_id)
);

-- Indici per ottimizzare le query del chatbot
CREATE INDEX idx_patologie_nome ON patologie USING gin(to_tsvector('italian', nome));
CREATE INDEX idx_patologie_tipo ON patologie(tipo);
CREATE INDEX idx_patologie_specialisti_patologia ON patologie_specialisti(patologia_id);
CREATE INDEX idx_patologie_specialisti_specialista ON patologie_specialisti(specialista_id);
CREATE INDEX idx_prevalenze_patologia ON prevalenze(patologia_id);
CREATE INDEX idx_prevalenze_fascia_eta ON prevalenze(fascia_eta_id);

-- Funzione per aggiornare timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
   NEW.updated_at = NOW();
   RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_patologie_updated_at
BEFORE UPDATE ON patologie
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

```
