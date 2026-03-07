#!/usr/bin/env python3
"""
Script per elaborare i dati Orphadata sulle malattie rare in Italia.
Estrae informazioni epidemiologiche e classifica le malattie per complessità.
"""

import xml.etree.ElementTree as ET
import pandas as pd
import json
import os

def parse_orphadata_epidemiology(xml_path):
    """
    Parsa il file XML di Orphadata con dati epidemiologici delle malattie rare.
    """
    print(f"Parsing {xml_path}...")
    
    tree = ET.parse(xml_path)
    root = tree.getroot()
    
    diseases = []
    
    # Trova tutti i disorder
    for disorder in root.iter('Disorder'):
        disease_data = {
            'orpha_code': None,
            'name': None,
            'expert_link': None,
            'disorder_type': None,
            'disorder_group': None,
            'prevalence_class': None,
            'prevalence_geo': None,
            'prevalence_value': None,
            'inheritance': None,
            'age_of_onset': None,
            'average_age_onset': None,
            'average_age_death': None
        }
        
        # OrphaCode
        orpha_code = disorder.find('OrphaCode')
        if orpha_code is not None:
            disease_data['orpha_code'] = orpha_code.text
        
        # Nome
        name = disorder.find('Name')
        if name is not None:
            disease_data['name'] = name.text
        
        # Expert Link
        expert_link = disorder.find('ExpertLink')
        if expert_link is not None:
            disease_data['expert_link'] = expert_link.text
        
        # Disorder Type
        disorder_type = disorder.find('.//DisorderType/Name')
        if disorder_type is not None:
            disease_data['disorder_type'] = disorder_type.text
        
        # Disorder Group
        disorder_group = disorder.find('.//DisorderGroup/Name')
        if disorder_group is not None:
            disease_data['disorder_group'] = disorder_group.text
        
        # Prevalence data
        prevalence_list = disorder.find('PrevalenceList')
        if prevalence_list is not None:
            for prevalence in prevalence_list.findall('Prevalence'):
                # Prevalence Class
                prev_class = prevalence.find('.//PrevalenceClass/Name')
                if prev_class is not None:
                    disease_data['prevalence_class'] = prev_class.text
                
                # Geographic
                prev_geo = prevalence.find('.//PrevalenceGeographic/Name')
                if prev_geo is not None:
                    disease_data['prevalence_geo'] = prev_geo.text
                
                # Value
                prev_value = prevalence.find('PrevalenceValMoy')
                if prev_value is not None:
                    disease_data['prevalence_value'] = prev_value.text
                
                # Prendi solo il primo record di prevalenza
                break
        
        # Age of onset
        age_onset_list = disorder.find('AverageAgeOfOnsetList')
        if age_onset_list is not None:
            ages = []
            for age in age_onset_list.findall('.//Name'):
                if age.text:
                    ages.append(age.text)
            disease_data['age_of_onset'] = ', '.join(ages) if ages else None
        
        # Average age of onset
        avg_onset = disorder.find('.//AverageAgeOfOnsets/AverageAgeOfOnset/Name')
        if avg_onset is not None:
            disease_data['average_age_onset'] = avg_onset.text
        
        # Average age of death
        avg_death = disorder.find('.//AverageAgeOfDeaths/AverageAgeOfDeath/Name')
        if avg_death is not None:
            disease_data['average_age_death'] = avg_death.text
        
        diseases.append(disease_data)
    
    return diseases

def classify_complexity(df):
    """
    Classifica le malattie per complessità basandosi su indicatori proxy.
    
    Criteri di complessità (proxy per numero di specialisti):
    - Malattie con prevalenza molto bassa (difficili da diagnosticare)
    - Malattie con esordio in età pediatrica (richiedono transizione cure)
    - Malattie croniche/progressive
    - Malattie sistemiche (coinvolgono più organi)
    """
    
    # Crea colonna di complessità
    df['complexity_score'] = 0
    
    # Prevalenza molto bassa = difficoltà diagnostica = più specialisti consultati
    prevalence_scores = {
        '<1 / 1 000 000': 5,
        '1-9 / 1 000 000': 4,
        '1-9 / 100 000': 3,
        '1-5 / 10 000': 2,
        '6-9 / 10 000': 1,
        '>1 / 1000': 0
    }
    
    for prev, score in prevalence_scores.items():
        df.loc[df['prevalence_class'] == prev, 'complexity_score'] += score
    
    # Esordio in età pediatrica = transizione cure
    pediatric_onset = ['Infancy', 'Neonatal', 'Childhood', 'Adolescence', 'Antenatal']
    df.loc[df['age_of_onset'].str.contains('|'.join(pediatric_onset), na=False, case=False), 'complexity_score'] += 2
    
    # Classificazione finale
    df['complexity_level'] = pd.cut(
        df['complexity_score'],
        bins=[-1, 2, 4, 6, 10],
        labels=['Bassa', 'Media', 'Alta', 'Molto Alta']
    )
    
    return df

def main():
    # Percorsi
    input_path = '/home/ubuntu/progetto_sanitario/datasets/raw/orphadata_epidemiology_it.xml'
    output_dir = '/home/ubuntu/progetto_sanitario/datasets/processed'
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Parse XML
    diseases = parse_orphadata_epidemiology(input_path)
    print(f"Trovate {len(diseases)} malattie rare")
    
    # Crea DataFrame
    df = pd.DataFrame(diseases)
    
    # Rimuovi righe senza OrphaCode
    df = df.dropna(subset=['orpha_code'])
    print(f"Malattie con OrphaCode valido: {len(df)}")
    
    # Classifica per complessità
    df = classify_complexity(df)
    
    # Salva CSV
    csv_path = os.path.join(output_dir, 'malattie_rare_italia.csv')
    df.to_csv(csv_path, index=False, encoding='utf-8')
    print(f"Salvato: {csv_path}")
    
    # Salva JSON
    json_path = os.path.join(output_dir, 'malattie_rare_italia.json')
    df.to_json(json_path, orient='records', force_ascii=False, indent=2)
    print(f"Salvato: {json_path}")
    
    # Statistiche
    print("\n=== STATISTICHE ===")
    print(f"Totale malattie rare: {len(df)}")
    print(f"\nDistribuzione per complessità:")
    print(df['complexity_level'].value_counts())
    print(f"\nDistribuzione per tipo di disturbo:")
    print(df['disorder_type'].value_counts().head(10))
    print(f"\nDistribuzione per classe di prevalenza:")
    print(df['prevalence_class'].value_counts())
    
    # Salva statistiche
    stats = {
        'totale_malattie': len(df),
        'distribuzione_complessita': df['complexity_level'].value_counts().to_dict(),
        'distribuzione_tipo': df['disorder_type'].value_counts().to_dict(),
        'distribuzione_prevalenza': df['prevalence_class'].value_counts().to_dict()
    }
    
    stats_path = os.path.join(output_dir, 'statistiche_malattie_rare.json')
    with open(stats_path, 'w', encoding='utf-8') as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)
    print(f"\nSalvato: {stats_path}")

if __name__ == '__main__':
    main()
