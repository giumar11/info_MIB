#!/usr/bin/env python3
"""
Script per estrarre e strutturare i dati dal Rapporto SDO 2023.
Crea dataset utilizzabili per l'analisi delle patologie multi-specialistiche.
"""

import os
import json
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MINISTERO_DIR = os.path.join(BASE_DIR, 'datasets', 'raw', 'ministero_salute')
SDO_ETA_SESSO_CSV = os.path.join(MINISTERO_DIR, 'dimissioni_ospedaliere_eta_sesso.csv')
SDO_TIPOLOGIA_CSV = os.path.join(MINISTERO_DIR, 'dimissioni_ospedaliere_tipologia.csv')

# MDC/DRG non sono presenti nei file open data aggregati del Ministero: questi
# elenchi sono riferimenti editoriali di contesto, NON calcolati dai CSV.
_MDC_RIFERIMENTO = [
    {'codice': 'MDC 08', 'descrizione': 'Malattie e disturbi del sistema muscolo-scheletrico'},
    {'codice': 'MDC 05', 'descrizione': 'Malattie e disturbi del sistema cardiocircolatorio'},
    {'codice': 'MDC 06', 'descrizione': 'Malattie e disturbi dell\'apparato digerente'},
    {'codice': 'MDC 04', 'descrizione': 'Malattie e disturbi dell\'apparato respiratorio'},
    {'codice': 'MDC 14', 'descrizione': 'Gravidanza, parto e puerperio'},
    {'codice': 'MDC 17', 'descrizione': 'Malattie e disturbi mieloproliferativi e neoplasie'},
    {'codice': 'MDC 01', 'descrizione': 'Malattie e disturbi del sistema nervoso'},
    {'codice': 'MDC 11', 'descrizione': 'Malattie e disturbi del rene e vie urinarie'},
]
_DRG_RIFERIMENTO = [
    {'drg': '470', 'descrizione': 'Sostituzione articolazione maggiore', 'complessita': 'alta'},
    {'drg': '127', 'descrizione': 'Insufficienza cardiaca e shock', 'complessita': 'alta'},
    {'drg': '089', 'descrizione': 'Polmonite semplice e pleurite', 'complessita': 'media'},
    {'drg': '014', 'descrizione': 'Malattie cerebrovascolari', 'complessita': 'alta'},
    {'drg': '410', 'descrizione': 'Chemioterapia', 'complessita': 'alta'},
    {'drg': '462', 'descrizione': 'Riabilitazione', 'complessita': 'media'},
]


def _parse_sdo_line(raw):
    """Normalizza una riga dei CSV open data SDO del Ministero.

    Il formato racchiude l'intera riga tra virgolette e separa i campi con ';';
    i campi sono a loro volta tra doppie virgolette, es.
    '"2022;""01000300"";""OSPEDALE MARIA VITTORIA"";""512"";..."'.
    """
    s = raw.rstrip('\r\n')
    if s.startswith('"') and s.endswith('"'):
        s = s[1:-1]
    fields = []
    for f in s.split(';'):
        f = f.strip()
        if f.startswith('""') and f.endswith('""'):
            f = f[2:-2]
        fields.append(f)
    return fields


def _to_int(value):
    """Converte un numero in stile italiano ('10.487') in int, 0 se non valido."""
    v = value.strip().strip('"').replace('.', '')
    if v in ('', '-', 'n.d.', 'N.D.'):
        return 0
    try:
        return int(v)
    except ValueError:
        return 0


def _read_sdo_csv(path):
    with open(path, 'r', encoding='utf-8') as f:
        lines = [ln for ln in f if ln.strip()]
    if not lines:
        return [], []
    return _parse_sdo_line(lines[0]), [_parse_sdo_line(ln) for ln in lines[1:]]


def create_sdo_summary():
    """Aggrega i dati REALI dai CSV open data SDO del Ministero della Salute.

    I totali sono calcolati sommando i valori per-istituto dei file originali in
    datasets/raw/ministero_salute/ (non stime). Se i file non sono presenti lo
    script segnala il problema e restituisce una struttura vuota, senza
    inventare dati.
    """
    if not (os.path.exists(SDO_ETA_SESSO_CSV) and os.path.exists(SDO_TIPOLOGIA_CSV)):
        print(f"  ATTENZIONE: CSV open data SDO non trovati in {MINISTERO_DIR}.")
        print("  Riepilogo SDO vuoto: nessun dato viene inventato.")
        return {
            'fonte': 'Ministero della Salute - Open Data SDO',
            'stato': 'file_sorgente_mancante',
            'file_attesi': [
                os.path.relpath(SDO_ETA_SESSO_CSV, BASE_DIR),
                os.path.relpath(SDO_TIPOLOGIA_CSV, BASE_DIR),
            ],
        }

    eta_header, eta_rows = _read_sdo_csv(SDO_ETA_SESSO_CSV)
    tip_header, tip_rows = _read_sdo_csv(SDO_TIPOLOGIA_CSV)

    age_cols = eta_header[4:]
    by_age = {c: 0 for c in age_cols}
    by_sex = {}
    institutions = set()
    anni = set()
    grand = 0
    for r in eta_rows:
        if len(r) < 4:
            continue
        anni.add(r[0])
        institutions.add(r[1])
        sesso = r[3] or 'Non Definito'
        for i, c in enumerate(age_cols):
            idx = 4 + i
            if idx < len(r):
                val = _to_int(r[idx])
                by_age[c] += val
                by_sex[sesso] = by_sex.get(sesso, 0) + val
                grand += val

    tip_cols = tip_header[3:]
    tip_tot = {c: 0 for c in tip_cols}
    for r in tip_rows:
        if len(r) < 4:
            continue
        for i, c in enumerate(tip_cols):
            idx = 3 + i
            if idx < len(r):
                tip_tot[c] += _to_int(r[idx])

    anno = sorted(anni)[-1] if anni else None

    def _pct(part):
        return round(100 * part / grand, 1) if grand else 0.0

    return {
        'anno': int(anno) if anno and anno.isdigit() else anno,
        'fonte': 'Ministero della Salute - Open Data SDO (dimissioni ospedaliere)',
        'url': 'https://www.dati.salute.gov.it/',
        'metodo': ('Aggregazione dei valori per-istituto dai file open data '
                   'originali in datasets/raw/ministero_salute/.'),
        'file_sorgente': [
            os.path.basename(SDO_ETA_SESSO_CSV),
            os.path.basename(SDO_TIPOLOGIA_CSV),
        ],
        'strutture_conteggiate': len(institutions),
        'dimissioni_totali': grand,
        'distribuzione_eta': {
            c.replace('Cl_età_', ''): {'ricoveri': by_age[c], 'percentuale': _pct(by_age[c])}
            for c in age_cols
        },
        'distribuzione_genere': {
            s: {'ricoveri': v, 'percentuale': _pct(v)} for s, v in sorted(by_sex.items())
        },
        'tipologia_dimissione': dict(tip_tot),
        'riferimenti_curati': {
            'nota': ('MDC e DRG non sono presenti nei file open data aggregati; '
                     'questi elenchi sono riferimenti editoriali di contesto, '
                     'non calcolati dai CSV.'),
            'principali_mdc': _MDC_RIFERIMENTO,
            'drg_frequenti_complessi': _DRG_RIFERIMENTO,
        },
    }

def create_multidisciplinary_pathways():
    """
    Crea dataset sui percorsi diagnostico-terapeutici assistenziali (PDTA)
    che richiedono approccio multidisciplinare.
    """
    
    pdta_multidisciplinari = [
        {
            'patologia': 'Tumore della mammella',
            'codice_icd10': 'C50',
            'specialisti_coinvolti': ['Senologo', 'Oncologo medico', 'Radioterapista', 'Chirurgo plastico', 'Psicologo', 'Radiologo', 'Anatomo-patologo'],
            'n_specialisti': 7,
            'prevalenza_italia': '1 donna su 8',
            'fonte': 'AIOM, Rapporto SDO'
        },
        {
            'patologia': 'Tumore del colon-retto',
            'codice_icd10': 'C18-C20',
            'specialisti_coinvolti': ['Gastroenterologo', 'Chirurgo', 'Oncologo', 'Radioterapista', 'Nutrizionista', 'Stomaterapeuta'],
            'n_specialisti': 6,
            'prevalenza_italia': '50.000 nuovi casi/anno',
            'fonte': 'AIOM, Rapporto SDO'
        },
        {
            'patologia': 'Diabete mellito tipo 2 complicato',
            'codice_icd10': 'E11',
            'specialisti_coinvolti': ['Diabetologo', 'Cardiologo', 'Nefrologo', 'Oculista', 'Neurologo', 'Podologo', 'Dietista'],
            'n_specialisti': 7,
            'prevalenza_italia': '3.5 milioni di persone',
            'fonte': 'AMD-SID, ISTAT'
        },
        {
            'patologia': 'Scompenso cardiaco cronico',
            'codice_icd10': 'I50',
            'specialisti_coinvolti': ['Cardiologo', 'Internista', 'Nefrologo', 'Pneumologo', 'Geriatra', 'Palliativista'],
            'n_specialisti': 6,
            'prevalenza_italia': '1 milione di persone',
            'fonte': 'ESC, Rapporto SDO'
        },
        {
            'patologia': 'Sclerosi multipla',
            'codice_icd10': 'G35',
            'specialisti_coinvolti': ['Neurologo', 'Fisiatra', 'Urologo', 'Psicologo', 'Oculista', 'Fisioterapista'],
            'n_specialisti': 6,
            'prevalenza_italia': '130.000 persone',
            'fonte': 'AISM, Orphanet'
        },
        {
            'patologia': 'Artrite reumatoide',
            'codice_icd10': 'M05-M06',
            'specialisti_coinvolti': ['Reumatologo', 'Ortopedico', 'Fisiatra', 'Dermatologo', 'Pneumologo', 'Cardiologo'],
            'n_specialisti': 6,
            'prevalenza_italia': '400.000 persone',
            'fonte': 'SIR, ISTAT'
        },
        {
            'patologia': 'BPCO con insufficienza respiratoria',
            'codice_icd10': 'J44',
            'specialisti_coinvolti': ['Pneumologo', 'Cardiologo', 'Fisiatra', 'Nutrizionista', 'Palliativista'],
            'n_specialisti': 5,
            'prevalenza_italia': '3.5 milioni di persone',
            'fonte': 'AIPO, ISTAT'
        },
        {
            'patologia': 'Malattia di Parkinson',
            'codice_icd10': 'G20',
            'specialisti_coinvolti': ['Neurologo', 'Geriatra', 'Fisiatra', 'Logopedista', 'Psicologo', 'Nutrizionista'],
            'n_specialisti': 6,
            'prevalenza_italia': '300.000 persone',
            'fonte': 'SIN, ISTAT'
        },
        {
            'patologia': 'Lupus eritematoso sistemico',
            'codice_icd10': 'M32',
            'specialisti_coinvolti': ['Reumatologo', 'Nefrologo', 'Dermatologo', 'Cardiologo', 'Pneumologo', 'Ematologo', 'Ginecologo'],
            'n_specialisti': 7,
            'prevalenza_italia': '60.000 persone',
            'fonte': 'SIR, Orphanet'
        },
        {
            'patologia': 'Fibrosi cistica',
            'codice_icd10': 'E84',
            'specialisti_coinvolti': ['Pneumologo', 'Gastroenterologo', 'Endocrinologo', 'Nutrizionista', 'Fisioterapista', 'Psicologo', 'Genetista'],
            'n_specialisti': 7,
            'prevalenza_italia': '6.000 persone',
            'fonte': 'Registro FC, Orphanet'
        }
    ]
    
    return pdta_multidisciplinari

def create_population_segmentation():
    """
    Crea dataset per la segmentazione della popolazione italiana
    per età, genere e carico di patologia.
    """
    
    # Dati ISTAT popolazione 2023
    segmentazione = {
        'fonte': 'ISTAT, PASSI, PASSI d\'Argento',
        'anno_riferimento': 2023,
        
        'popolazione_totale': 58997201,
        
        'per_fascia_eta': [
            {'fascia': '0-14', 'popolazione': 7500000, 'percentuale': 12.7, 'patologie_croniche_media': 0.2},
            {'fascia': '15-24', 'popolazione': 5800000, 'percentuale': 9.8, 'patologie_croniche_media': 0.3},
            {'fascia': '25-44', 'popolazione': 13200000, 'percentuale': 22.4, 'patologie_croniche_media': 0.5},
            {'fascia': '45-64', 'popolazione': 17500000, 'percentuale': 29.7, 'patologie_croniche_media': 1.2},
            {'fascia': '65-74', 'popolazione': 7200000, 'percentuale': 12.2, 'patologie_croniche_media': 2.3},
            {'fascia': '75+', 'popolazione': 7800000, 'percentuale': 13.2, 'patologie_croniche_media': 3.5}
        ],
        
        'per_genere': {
            'maschi': {'popolazione': 28800000, 'percentuale': 48.8},
            'femmine': {'popolazione': 30200000, 'percentuale': 51.2}
        },
        
        'multimorbidita': {
            'descrizione': 'Persone con 3+ patologie croniche',
            'over_65': {
                'totale': 7000000,
                'percentuale_over65': 46.7,
                'fonte': 'ISTAT Report Anziani 2019'
            },
            'distribuzione_n_patologie': {
                '0': {'percentuale': 35, 'descrizione': 'Nessuna patologia cronica'},
                '1': {'percentuale': 25, 'descrizione': 'Una patologia cronica'},
                '2': {'percentuale': 18, 'descrizione': 'Due patologie croniche'},
                '3+': {'percentuale': 22, 'descrizione': 'Tre o più patologie croniche (multimorbidità)'}
            }
        },
        
        'patologie_croniche_prevalenti': [
            {'patologia': 'Ipertensione', 'prevalenza_percentuale': 17.4, 'popolazione_affetta': 10270000},
            {'patologia': 'Artrosi/artrite', 'prevalenza_percentuale': 16.1, 'popolazione_affetta': 9500000},
            {'patologia': 'Malattie allergiche', 'prevalenza_percentuale': 10.7, 'popolazione_affetta': 6310000},
            {'patologia': 'Osteoporosi', 'prevalenza_percentuale': 8.1, 'popolazione_affetta': 4780000},
            {'patologia': 'Diabete', 'prevalenza_percentuale': 5.8, 'popolazione_affetta': 3420000},
            {'patologia': 'Bronchite cronica/BPCO', 'prevalenza_percentuale': 5.6, 'popolazione_affetta': 3300000},
            {'patologia': 'Malattie cardiache', 'prevalenza_percentuale': 4.4, 'popolazione_affetta': 2600000},
            {'patologia': 'Disturbi nervosi', 'prevalenza_percentuale': 4.2, 'popolazione_affetta': 2480000},
            {'patologia': 'Ulcera gastrica/duodenale', 'prevalenza_percentuale': 2.8, 'popolazione_affetta': 1650000},
            {'patologia': 'Tumore', 'prevalenza_percentuale': 2.7, 'popolazione_affetta': 1590000}
        ]
    }
    
    return segmentazione

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_dir = os.path.join(base_dir, 'datasets', 'processed')
    os.makedirs(output_dir, exist_ok=True)
    
    print("=== ESTRAZIONE DATI SDO E CREAZIONE DATASET ===\n")
    
    # Crea riepilogo SDO dai file open data originali del Ministero
    sdo_summary = create_sdo_summary()
    sdo_path = os.path.join(output_dir, 'riepilogo_sdo.json')
    with open(sdo_path, 'w', encoding='utf-8') as f:
        json.dump(sdo_summary, f, ensure_ascii=False, indent=2)
    print(f"Salvato: {sdo_path}")
    
    # Crea PDTA multidisciplinari
    pdta = create_multidisciplinary_pathways()
    pdta_path = os.path.join(output_dir, 'pdta_multidisciplinari.json')
    with open(pdta_path, 'w', encoding='utf-8') as f:
        json.dump(pdta, f, ensure_ascii=False, indent=2)
    print(f"Salvato: {pdta_path}")
    
    # Crea anche CSV per PDTA
    pdta_df = pd.DataFrame(pdta)
    pdta_df['specialisti_coinvolti'] = pdta_df['specialisti_coinvolti'].apply(lambda x: ', '.join(x))
    pdta_csv_path = os.path.join(output_dir, 'pdta_multidisciplinari.csv')
    pdta_df.to_csv(pdta_csv_path, index=False, encoding='utf-8')
    print(f"Salvato: {pdta_csv_path}")
    
    # Crea segmentazione popolazione
    segmentazione = create_population_segmentation()
    seg_path = os.path.join(output_dir, 'segmentazione_popolazione.json')
    with open(seg_path, 'w', encoding='utf-8') as f:
        json.dump(segmentazione, f, ensure_ascii=False, indent=2)
    print(f"Salvato: {seg_path}")
    
    # Stampa riepilogo
    print("\n=== RIEPILOGO DATASET CREATI ===")
    if sdo_summary.get('stato') == 'file_sorgente_mancante':
        print("\n1. Riepilogo SDO: NON generato (file open data mancanti).")
    else:
        print(f"\n1. Riepilogo SDO (anno {sdo_summary.get('anno')}, da open data originali):")
        print(f"   - Dimissioni totali: {sdo_summary['dimissioni_totali']:,}")
        print(f"   - Strutture conteggiate: {sdo_summary['strutture_conteggiate']:,}")
    
    print(f"\n2. PDTA Multidisciplinari:")
    print(f"   - Patologie mappate: {len(pdta)}")
    print(f"   - Media specialisti per patologia: {sum(p['n_specialisti'] for p in pdta)/len(pdta):.1f}")
    
    print(f"\n3. Segmentazione Popolazione:")
    print(f"   - Popolazione totale: {segmentazione['popolazione_totale']:,}")
    print(f"   - Over 65 con multimorbidità: {segmentazione['multimorbidita']['over_65']['totale']:,}")

if __name__ == '__main__':
    main()
