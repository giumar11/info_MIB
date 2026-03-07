#!/usr/bin/env python3
"""
Script per analizzare i dati ISTAT Health for All sulle malattie croniche.
Estrae indicatori rilevanti per la segmentazione della popolazione.
"""

import os
import pandas as pd
import json
from pathlib import Path

def read_hfa_titles(titles_path):
    """
    Legge i titoli degli indicatori HFA.
    """
    indicators = {}
    try:
        with open(titles_path, 'r', encoding='latin-1') as f:
            for line in f:
                line = line.strip()
                if ',' in line:
                    parts = line.split(',', 1)
                    if len(parts) == 2:
                        code = parts[0].strip()
                        title = parts[1].strip()
                        indicators[code] = title
    except Exception as e:
        print(f"Errore lettura titoli: {e}")
    return indicators

def analyze_hfa_structure(hfa_dir):
    """
    Analizza la struttura dei dati HFA e identifica indicatori rilevanti.
    """
    data_dir = Path(hfa_dir) / 'Data'
    
    # Leggi titoli
    titles_path = Path(hfa_dir) / 'TITLES' / 'TITLES.TXT'
    indicators = read_hfa_titles(titles_path)
    
    # Trova tutti i file .ind (definizioni indicatori)
    ind_files = list(data_dir.glob('*.ind'))
    
    # Indicatori rilevanti per malattie croniche e multi-specialistiche
    relevant_keywords = [
        'diabete', 'ipertensione', 'cardiopat', 'tumore', 'cancro',
        'cronico', 'cronica', 'malattia', 'patologia', 'ospedalier',
        'ricovero', 'dimission', 'specialist', 'visita', 'ambulatori',
        'diagnosi', 'mortalità', 'prevalenza', 'incidenza',
        'anzian', 'età', 'genere', 'sesso', 'maschi', 'femmin'
    ]
    
    relevant_indicators = {}
    
    for code, title in indicators.items():
        title_lower = title.lower()
        for keyword in relevant_keywords:
            if keyword in title_lower:
                relevant_indicators[code] = title
                break
    
    return indicators, relevant_indicators

def extract_chronic_disease_data(hfa_dir):
    """
    Estrae dati specifici sulle malattie croniche dal database HFA.
    """
    # Gruppi tematici rilevanti basati sulla struttura HFA
    chronic_disease_groups = {
        'Gruppo 5': 'Malattie croniche e infettive',
        'Gruppo 6': 'Limiti funzionali e dipendenze',
        'Gruppo 7': 'Condizioni di salute e speranza di vita',
        'Gruppo 8': 'Assistenza sanitaria'
    }
    
    # Indicatori chiave per il nostro obiettivo
    key_indicators = {
        # Malattie croniche dichiarate
        'diabete': 'Persone con diabete',
        'ipertensione': 'Persone con ipertensione',
        'cardiopatia': 'Persone con malattie cardiache',
        'bronchite_cronica': 'Persone con bronchite cronica/BPCO',
        'artrosi': 'Persone con artrosi/artrite',
        'osteoporosi': 'Persone con osteoporosi',
        'tumore': 'Persone con tumore',
        'alzheimer': 'Persone con Alzheimer/demenza',
        
        # Visite specialistiche
        'visite_specialistiche': 'Visite mediche specialistiche',
        'accertamenti_diagnostici': 'Accertamenti diagnostici',
        
        # Ricoveri
        'ricoveri_acuti': 'Ricoveri per acuti',
        'ricoveri_riabilitazione': 'Ricoveri riabilitazione',
        'giornate_degenza': 'Giornate di degenza'
    }
    
    return chronic_disease_groups, key_indicators

def create_proxy_analysis():
    """
    Crea l'analisi proxy per identificare patologie multi-specialistiche.
    
    Criteri per identificare patologie che richiedono più specialisti:
    1. Patologie sistemiche (coinvolgono più organi/apparati)
    2. Patologie croniche con complicanze multiple
    3. Patologie rare (difficoltà diagnostica)
    4. Patologie oncologiche (team multidisciplinare)
    5. Patologie geriatriche con multimorbidità
    """
    
    # Categorie di patologie multi-specialistiche
    multi_specialist_conditions = {
        'oncologiche': {
            'descrizione': 'Tumori e neoplasie',
            'specialisti_tipici': ['Oncologo', 'Chirurgo', 'Radioterapista', 'Anatomo-patologo', 'Radiologo'],
            'n_specialisti_medio': 5,
            'fonte': 'PDTA oncologici regionali, Rapporto SDO'
        },
        'diabete_complicato': {
            'descrizione': 'Diabete con complicanze',
            'specialisti_tipici': ['Diabetologo', 'Cardiologo', 'Nefrologo', 'Oculista', 'Neurologo', 'Podologo'],
            'n_specialisti_medio': 4,
            'fonte': 'Standard AMD-SID, PASSI'
        },
        'malattie_rare': {
            'descrizione': 'Malattie rare (Orphanet)',
            'specialisti_tipici': ['Centro di riferimento', 'Genetista', 'Specialisti d\'organo multipli'],
            'n_specialisti_medio': 6,
            'fonte': 'Orphadata, Registro Nazionale Malattie Rare'
        },
        'cardiopatie_complesse': {
            'descrizione': 'Cardiopatie con comorbidità',
            'specialisti_tipici': ['Cardiologo', 'Cardiochirurgo', 'Nefrologo', 'Pneumologo'],
            'n_specialisti_medio': 4,
            'fonte': 'Rapporto SDO, PASSI'
        },
        'malattie_autoimmuni': {
            'descrizione': 'Malattie autoimmuni sistemiche',
            'specialisti_tipici': ['Reumatologo', 'Immunologo', 'Dermatologo', 'Nefrologo', 'Pneumologo'],
            'n_specialisti_medio': 5,
            'fonte': 'ISTAT HFA, Registro malattie autoimmuni'
        },
        'malattie_neurologiche': {
            'descrizione': 'Malattie neurodegenerative',
            'specialisti_tipici': ['Neurologo', 'Geriatra', 'Fisiatra', 'Psichiatra', 'Logopedista'],
            'n_specialisti_medio': 4,
            'fonte': 'PASSI d\'Argento, ISTAT'
        },
        'multimorbidita_anziani': {
            'descrizione': 'Anziani con 3+ patologie croniche',
            'specialisti_tipici': ['MMG', 'Geriatra', 'Cardiologo', 'Diabetologo', 'Nefrologo', 'Fisiatra'],
            'n_specialisti_medio': 5,
            'fonte': 'ISTAT Report Anziani, PASSI d\'Argento'
        },
        'malattie_respiratorie_croniche': {
            'descrizione': 'BPCO e insufficienza respiratoria',
            'specialisti_tipici': ['Pneumologo', 'Cardiologo', 'Fisiatra', 'Nutrizionista'],
            'n_specialisti_medio': 3,
            'fonte': 'ISTAT HFA, Rapporto SDO'
        }
    }
    
    return multi_specialist_conditions

def main():
    output_dir = '/home/ubuntu/progetto_sanitario/datasets/processed'
    hfa_dir = '/home/ubuntu/progetto_sanitario/datasets/raw/hfa_istat/HFA'
    
    os.makedirs(output_dir, exist_ok=True)
    
    print("=== ANALISI DATI HFA ISTAT ===\n")
    
    # Analizza struttura HFA
    all_indicators, relevant_indicators = analyze_hfa_structure(hfa_dir)
    print(f"Indicatori totali trovati: {len(all_indicators)}")
    print(f"Indicatori rilevanti per malattie croniche: {len(relevant_indicators)}")
    
    # Estrai categorie malattie croniche
    groups, key_indicators = extract_chronic_disease_data(hfa_dir)
    
    # Crea analisi proxy
    multi_specialist = create_proxy_analysis()
    
    # Salva risultati
    results = {
        'indicatori_hfa_rilevanti': relevant_indicators,
        'gruppi_tematici': groups,
        'indicatori_chiave': key_indicators,
        'patologie_multi_specialistiche': multi_specialist
    }
    
    output_path = os.path.join(output_dir, 'analisi_patologie_multispecialistiche.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\nSalvato: {output_path}")
    
    # Stampa riepilogo
    print("\n=== PATOLOGIE CHE RICHIEDONO PIÙ SPECIALISTI ===\n")
    for cat, info in multi_specialist.items():
        print(f"📋 {info['descrizione']}")
        print(f"   Specialisti tipici: {', '.join(info['specialisti_tipici'])}")
        print(f"   N. medio specialisti: {info['n_specialisti_medio']}")
        print(f"   Fonte dati: {info['fonte']}")
        print()

if __name__ == '__main__':
    main()
