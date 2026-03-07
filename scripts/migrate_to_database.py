#!/usr/bin/env python3
"""
Script di migrazione dati per Geen.ai
Converte i dataset JSON/CSV in formato pronto per SQL o NoSQL

Autore: Manus AI
Data: 2026-01-30
"""

import json
import csv
import os
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

# Percorsi dataset
BASE_DIR = Path(__file__).parent.parent
PROCESSED_DIR = BASE_DIR / "datasets" / "processed"
RAW_DIR = BASE_DIR / "datasets" / "raw"
OUTPUT_DIR = BASE_DIR / "datasets" / "migration_ready"


def load_json(filepath: Path) -> Any:
    """Carica un file JSON."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_json(data: Any, filepath: Path) -> None:
    """Salva dati in formato JSON."""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def extract_specialisti_unique(pdta_data: List[Dict]) -> List[Dict]:
    """Estrae la lista unica degli specialisti dai PDTA."""
    specialisti_set = set()
    for pdta in pdta_data:
        for spec in pdta.get('specialisti_coinvolti', []):
            specialisti_set.add(spec)
    
    return [
        {
            "id": i + 1,
            "nome": nome,
            "area_medica": categorizza_area_medica(nome),
            "tipo": categorizza_tipo_specialista(nome)
        }
        for i, nome in enumerate(sorted(specialisti_set))
    ]


def categorizza_area_medica(specialista: str) -> str:
    """Categorizza l'area medica di uno specialista."""
    mapping = {
        "Cardiologo": "Cardiologia",
        "Oncologo": "Oncologia",
        "Neurologo": "Neurologia",
        "Diabetologo": "Endocrinologia",
        "Reumatologo": "Reumatologia",
        "Pneumologo": "Pneumologia",
        "Nefrologo": "Nefrologia",
        "Gastroenterologo": "Gastroenterologia",
        "Geriatra": "Geriatria",
        "Fisiatra": "Medicina Fisica e Riabilitazione",
        "Psicologo": "Psicologia Clinica",
        "Chirurgo": "Chirurgia Generale",
        "Radiologo": "Radiologia",
        "Anatomo-patologo": "Anatomia Patologica",
        "Radioterapista": "Radioterapia",
        "Oculista": "Oftalmologia",
        "Dermatologo": "Dermatologia",
        "Urologo": "Urologia",
        "Genetista": "Genetica Medica",
        "Ematologo": "Ematologia",
        "Ginecologo": "Ginecologia",
        "Internista": "Medicina Interna",
        "Ortopedico": "Ortopedia",
        "Palliativista": "Cure Palliative",
        "Senologo": "Senologia",
    }
    return mapping.get(specialista, "Altra Specialità")


def categorizza_tipo_specialista(specialista: str) -> str:
    """Categorizza il tipo di specialista."""
    chirurgici = ["Chirurgo", "Ortopedico", "Senologo", "Chirurgo plastico"]
    diagnostici = ["Radiologo", "Anatomo-patologo", "Genetista"]
    riabilitativi = ["Fisiatra", "Fisioterapista", "Logopedista"]
    supporto = ["Psicologo", "Nutrizionista", "Dietista", "Podologo", "Stomaterapeuta"]
    
    if specialista in chirurgici:
        return "chirurgico"
    elif specialista in diagnostici:
        return "diagnostico"
    elif specialista in riabilitativi:
        return "riabilitativo"
    elif specialista in supporto:
        return "supporto"
    else:
        return "medico"


def transform_malattie_rare_for_sql(malattie: List[Dict]) -> List[Dict]:
    """Trasforma i dati delle malattie rare per inserimento SQL."""
    return [
        {
            "nome": m["name"],
            "codice_orpha": m["orpha_code"],
            "codice_icd10": None,  # Da arricchire con mapping esterno
            "tipo": "rara",
            "descrizione": None,
            "prevalenza_classe": m.get("prevalence_class"),
            "prevalenza_valore": None,
            "eta_esordio": m.get("age_of_onset"),
            "complessita_score": m.get("complexity_score", 0),
            "complessita_livello": m.get("complexity_level", "bassa").lower(),
            "fonte_dati": "Orphadata"
        }
        for m in malattie
    ]


def transform_pdta_for_sql(pdta_data: List[Dict]) -> tuple:
    """Trasforma i PDTA in tabelle SQL separate."""
    patologie = []
    patologie_specialisti = []
    
    for i, pdta in enumerate(pdta_data, start=1):
        patologie.append({
            "id": i,
            "nome": pdta["patologia"],
            "codice_icd10": pdta.get("codice_icd10"),
            "tipo": categorizza_tipo_patologia(pdta["patologia"]),
            "descrizione": None,
            "prevalenza_classe": pdta.get("prevalenza_italia"),
            "complessita_score": pdta.get("n_specialisti", 5),
            "complessita_livello": "alta" if pdta.get("n_specialisti", 0) >= 6 else "media",
            "fonte_dati": pdta.get("fonte")
        })
        
        for spec in pdta.get("specialisti_coinvolti", []):
            patologie_specialisti.append({
                "patologia_nome": pdta["patologia"],
                "specialista_nome": spec,
                "ruolo": "primario" if spec == pdta["specialisti_coinvolti"][0] else "consulente",
                "obbligatorio": True
            })
    
    return patologie, patologie_specialisti


def categorizza_tipo_patologia(nome: str) -> str:
    """Categorizza il tipo di patologia dal nome."""
    nome_lower = nome.lower()
    if "tumore" in nome_lower or "cancro" in nome_lower:
        return "oncologica"
    elif "lupus" in nome_lower or "artrite" in nome_lower:
        return "autoimmune"
    elif "sclerosi" in nome_lower or "parkinson" in nome_lower:
        return "neurologica"
    elif "diabete" in nome_lower:
        return "comune"
    elif "scompenso" in nome_lower or "cardiaco" in nome_lower:
        return "cardiovascolare"
    elif "bpco" in nome_lower or "respiratoria" in nome_lower:
        return "respiratoria"
    elif "fibrosi" in nome_lower:
        return "rara"
    else:
        return "comune"


def transform_for_nosql(malattie: List[Dict], pdta_data: List[Dict], 
                        segmentazione: Dict) -> List[Dict]:
    """Crea documenti denormalizzati per NoSQL."""
    documents = []
    
    # Aggiungi malattie rare
    for m in malattie:
        doc = {
            "nome": m["name"],
            "codice_orpha": m["orpha_code"],
            "tipo": "rara",
            "complessita": {
                "score": m.get("complexity_score", 0),
                "livello": m.get("complexity_level", "bassa").lower()
            },
            "prevalenza": {
                "classe": m.get("prevalence_class"),
                "geo": m.get("prevalence_geo"),
                "fonte": "Orphadata"
            },
            "specialisti": [],  # Da arricchire
            "fonti": [{"nome": "Orphadata", "url": m.get("expert_link")}],
            "last_updated": datetime.now().isoformat()
        }
        documents.append(doc)
    
    # Aggiungi patologie PDTA (con specialisti)
    for pdta in pdta_data:
        doc = {
            "nome": pdta["patologia"],
            "codice_icd10": pdta.get("codice_icd10"),
            "tipo": categorizza_tipo_patologia(pdta["patologia"]),
            "complessita": {
                "score": pdta.get("n_specialisti", 5),
                "livello": "alta" if pdta.get("n_specialisti", 0) >= 6 else "media"
            },
            "prevalenza": {
                "classe": pdta.get("prevalenza_italia"),
                "geo": "Italia",
                "fonte": pdta.get("fonte")
            },
            "specialisti": [
                {
                    "nome": spec,
                    "ruolo": "primario" if i == 0 else "consulente"
                }
                for i, spec in enumerate(pdta.get("specialisti_coinvolti", []))
            ],
            "fonti": [{"nome": pdta.get("fonte", ""), "url": None}],
            "last_updated": datetime.now().isoformat()
        }
        documents.append(doc)
    
    return documents


def create_fasce_eta_data(segmentazione: Dict) -> List[Dict]:
    """Crea i dati per la tabella fasce_eta."""
    fasce = []
    for i, fascia in enumerate(segmentazione.get("per_fascia_eta", []), start=1):
        eta_range = fascia["fascia"].split("-")
        fasce.append({
            "id": i,
            "codice": fascia["fascia"],
            "eta_min": int(eta_range[0]) if eta_range[0].isdigit() else 75,
            "eta_max": int(eta_range[1]) if len(eta_range) > 1 and eta_range[1].isdigit() else 120,
            "popolazione": fascia["popolazione"],
            "percentuale_popolazione": fascia["percentuale"],
            "patologie_croniche_media": fascia["patologie_croniche_media"]
        })
    return fasce


def main():
    """Funzione principale di migrazione."""
    print("=== Migrazione Dati Geen.ai ===\n")
    
    # Carica dataset
    print("Caricamento dataset...")
    malattie_rare = load_json(PROCESSED_DIR / "malattie_rare_italia.json")
    pdta_data = load_json(PROCESSED_DIR / "pdta_multidisciplinari.json")
    segmentazione = load_json(PROCESSED_DIR / "segmentazione_popolazione.json")
    
    print(f"  - Malattie rare: {len(malattie_rare)} record")
    print(f"  - PDTA: {len(pdta_data)} record")
    
    # Trasforma per SQL
    print("\nTrasformazione per SQL...")
    sql_data = {
        "fonti_dati": [
            {"id": 1, "nome": "Orphadata", "url": "https://www.orphadata.com/epidemiology/", 
             "tipo": "registro", "frequenza_aggiornamento": "trimestrale"},
            {"id": 2, "nome": "Ministero della Salute - SDO", 
             "url": "https://www.salute.gov.it/", "tipo": "istituzionale", 
             "frequenza_aggiornamento": "annuale"},
            {"id": 3, "nome": "ISTAT", "url": "https://www.istat.it/", 
             "tipo": "istituzionale", "frequenza_aggiornamento": "annuale"},
        ],
        "specialisti": extract_specialisti_unique(pdta_data),
        "fasce_eta": create_fasce_eta_data(segmentazione),
        "patologie_rare": transform_malattie_rare_for_sql(malattie_rare),
    }
    
    patologie_pdta, patologie_specialisti = transform_pdta_for_sql(pdta_data)
    sql_data["patologie_pdta"] = patologie_pdta
    sql_data["patologie_specialisti"] = patologie_specialisti
    
    save_json(sql_data, OUTPUT_DIR / "sql_import_data.json")
    print(f"  - Salvato: {OUTPUT_DIR / 'sql_import_data.json'}")
    
    # Trasforma per NoSQL
    print("\nTrasformazione per NoSQL...")
    nosql_documents = transform_for_nosql(malattie_rare, pdta_data, segmentazione)
    save_json(nosql_documents, OUTPUT_DIR / "nosql_patologie_collection.json")
    print(f"  - Salvato: {OUTPUT_DIR / 'nosql_patologie_collection.json'}")
    print(f"  - Documenti totali: {len(nosql_documents)}")
    
    # Crea collection segmenti popolazione
    segmenti_nosql = []
    for fascia in segmentazione.get("per_fascia_eta", []):
        segmenti_nosql.append({
            "anno_riferimento": segmentazione.get("anno_riferimento", 2023),
            "tipo_segmento": "fascia_eta",
            "segmento": fascia["fascia"],
            "popolazione": fascia["popolazione"],
            "percentuale": fascia["percentuale"],
            "patologie_croniche_media": fascia["patologie_croniche_media"]
        })
    
    save_json(segmenti_nosql, OUTPUT_DIR / "nosql_segmenti_collection.json")
    print(f"  - Salvato: {OUTPUT_DIR / 'nosql_segmenti_collection.json'}")
    
    print("\n=== Migrazione completata ===")


if __name__ == "__main__":
    main()
