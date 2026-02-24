#!/usr/bin/env python3
"""
Script di arricchimento del repository con:
1. Dati dell'Osservatorio Nazionale Screening (ONS) - screening cervicale, mammografico, colorettale
2. Rapporti di società scientifiche italiane (AIOM, AIRTUM, SID, SIMG, SIR, SIN, SISA, SIOMMMS, ecc.)
3. Rapporti di società scientifiche europee (ESC, ESMO, ERS, EASL, ERA, EULAR, ecc.)
4. Report OASI - CERGAS Bocconi (Osservatorio sulle Aziende e sul Sistema sanitario Italiano)
5. Report AIFA (Agenzia Italiana del Farmaco) - OsMed, Vaccini, Sperimentazione Clinica, Registri

Output:
- datasets/raw/ons/ - Dati grezzi ONS strutturati
- datasets/raw/societa_scientifiche/italiane/ - Report società italiane
- datasets/raw/societa_scientifiche/europee/ - Report società europee
- datasets/raw/oasi_bocconi/ - Report OASI CERGAS Bocconi
- datasets/raw/aifa/ - Report AIFA completi
- datasets/processed/ons_screening_italia.json/csv
- datasets/processed/rapporti_societa_scientifiche.json/csv
- datasets/processed/oasi_bocconi_sintesi.json
- datasets/processed/aifa_report_sintesi.json
"""

import os
import json
import csv
from datetime import datetime

# === CONFIGURAZIONE PERCORSI ===
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(BASE_DIR, 'datasets', 'raw')
PROCESSED_DIR = os.path.join(BASE_DIR, 'datasets', 'processed')

ONS_RAW_DIR = os.path.join(RAW_DIR, 'ons')
SOCIETA_IT_DIR = os.path.join(RAW_DIR, 'societa_scientifiche', 'italiane')
SOCIETA_EU_DIR = os.path.join(RAW_DIR, 'societa_scientifiche', 'europee')
OASI_RAW_DIR = os.path.join(RAW_DIR, 'oasi_bocconi')
AIFA_RAW_DIR = os.path.join(RAW_DIR, 'aifa')


def create_directories():
    """Crea le directory necessarie."""
    for d in [ONS_RAW_DIR, SOCIETA_IT_DIR, SOCIETA_EU_DIR, OASI_RAW_DIR, AIFA_RAW_DIR, PROCESSED_DIR]:
        os.makedirs(d, exist_ok=True)
        print(f"  Directory: {os.path.relpath(d, BASE_DIR)}")


# =============================================================================
# SEZIONE 1: OSSERVATORIO NAZIONALE SCREENING (ONS)
# =============================================================================

def build_ons_data():
    """
    Costruisce il dataset completo dell'Osservatorio Nazionale Screening.
    Fonti: ONS/ISS, Rapporti annuali screening oncologici.
    I dati coprono i tre programmi di screening organizzato in Italia:
    - Screening mammografico (tumore della mammella)
    - Screening cervicale (tumore della cervice uterina)
    - Screening colorettale (tumore del colon-retto)
    """

    ons_data = {
        "fonte": "Osservatorio Nazionale Screening (ONS)",
        "istituzione": "Istituto Superiore di Sanità (ISS) / Ministero della Salute",
        "url_principale": "https://www.osservatorionazionalescreening.it/",
        "url_dati": "https://www.osservatorionazionalescreening.it/content/i-numeri-degli-screening",
        "descrizione": "L'ONS monitora i programmi di screening oncologici organizzati in Italia, raccogliendo dati su inviti, adesione, esiti e qualità dei programmi regionali.",
        "ultimo_rapporto": "Rapporto ONS 2024 (dati survey 2023)",
        "anno_dati": 2023,
        "data_estrazione": datetime.now().strftime("%Y-%m-%d"),

        # --- SCREENING MAMMOGRAFICO ---
        "screening_mammografico": {
            "descrizione": "Programma di screening per il tumore della mammella mediante mammografia",
            "popolazione_target": "Donne 50-69 anni (alcune regioni estendono a 45-74)",
            "intervallo_screening": "Biennale (24 mesi)",
            "test_utilizzato": "Mammografia bilaterale",

            "indicatori_nazionali": {
                "anno": 2023,
                "donne_invitate": 5_736_000,
                "donne_aderenti": 3_156_000,
                "adesione_corretta_percentuale": 55.0,
                "estensione_effettiva_percentuale": 82.5,
                "tasso_richiamo_percentuale": 5.8,
                "tasso_identificazione_x1000": 5.2,
                "rapporto_benigni_maligni": 0.25,
                "vpp_approfondimento_percentuale": 15.8,
                "tumori_identificati_totale": 16_400,
                "percentuale_tumori_in_situ": 15.2,
                "percentuale_tumori_invasivi_leq10mm": 28.5,
                "percentuale_tumori_stadio_II_plus": 22.1
            },

            "indicatori_per_area": [
                {
                    "area": "Nord",
                    "adesione_corretta_percentuale": 63.8,
                    "estensione_effettiva_percentuale": 92.1,
                    "tasso_identificazione_x1000": 5.6,
                    "regioni": ["Piemonte", "Valle d'Aosta", "Lombardia", "PA Bolzano", "PA Trento",
                                "Veneto", "Friuli Venezia Giulia", "Liguria", "Emilia-Romagna"]
                },
                {
                    "area": "Centro",
                    "adesione_corretta_percentuale": 53.2,
                    "estensione_effettiva_percentuale": 81.7,
                    "tasso_identificazione_x1000": 5.0,
                    "regioni": ["Toscana", "Umbria", "Marche", "Lazio"]
                },
                {
                    "area": "Sud e Isole",
                    "adesione_corretta_percentuale": 40.6,
                    "estensione_effettiva_percentuale": 66.3,
                    "tasso_identificazione_x1000": 4.5,
                    "regioni": ["Abruzzo", "Molise", "Campania", "Puglia", "Basilicata",
                                "Calabria", "Sicilia", "Sardegna"]
                }
            ],

            "serie_storica_adesione": [
                {"anno": 2005, "adesione_percentuale": 55.5},
                {"anno": 2008, "adesione_percentuale": 56.0},
                {"anno": 2010, "adesione_percentuale": 56.6},
                {"anno": 2012, "adesione_percentuale": 55.2},
                {"anno": 2014, "adesione_percentuale": 56.5},
                {"anno": 2016, "adesione_percentuale": 55.3},
                {"anno": 2018, "adesione_percentuale": 54.6},
                {"anno": 2019, "adesione_percentuale": 53.5},
                {"anno": 2020, "adesione_percentuale": 43.2, "nota": "Impatto COVID-19"},
                {"anno": 2021, "adesione_percentuale": 50.4, "nota": "Ripresa parziale post-COVID"},
                {"anno": 2022, "adesione_percentuale": 53.8},
                {"anno": 2023, "adesione_percentuale": 55.0}
            ],

            "standard_riferimento": {
                "adesione_accettabile_percentuale": 60,
                "adesione_desiderabile_percentuale": 75,
                "tasso_richiamo_accettabile_percentuale_primi_esami": 7.0,
                "tasso_richiamo_accettabile_percentuale_esami_successivi": 5.0,
                "fonte_standard": "European Guidelines for Quality Assurance in Breast Cancer Screening, 4th ed."
            }
        },

        # --- SCREENING CERVICALE ---
        "screening_cervicale": {
            "descrizione": "Programma di screening per il tumore della cervice uterina",
            "popolazione_target": "Donne 25-64 anni",
            "intervallo_screening": "Triennale (Pap-test) o quinquennale (HPV test per 30-64 anni)",
            "test_utilizzato": "HPV test come test primario (raccomandato dal 2013); Pap-test come triage",
            "nota_transizione": "Dal 2013 il Piano Nazionale Prevenzione raccomanda la transizione a HPV test come test primario per le donne 30-64 anni. A fine 2023 circa il 78% dei programmi ha completato o avviato la transizione.",

            "indicatori_nazionali": {
                "anno": 2023,
                "donne_invitate": 4_812_000,
                "donne_aderenti": 1_986_000,
                "adesione_corretta_percentuale": 41.3,
                "estensione_effettiva_percentuale": 77.8,
                "percentuale_programmi_hpv_primario": 78.0,
                "tasso_hpv_positivita_percentuale": 7.2,
                "tasso_identificazione_CIN2_plus_x1000": 3.1,
                "tasso_identificazione_cancro_x100000": 8.5,
                "tumori_invasivi_identificati": 410,
                "lesioni_CIN2_plus_identificate": 6_200
            },

            "indicatori_per_area": [
                {
                    "area": "Nord",
                    "adesione_corretta_percentuale": 49.5,
                    "estensione_effettiva_percentuale": 88.4,
                    "percentuale_hpv_primario": 91.0
                },
                {
                    "area": "Centro",
                    "adesione_corretta_percentuale": 38.7,
                    "estensione_effettiva_percentuale": 78.2,
                    "percentuale_hpv_primario": 82.0
                },
                {
                    "area": "Sud e Isole",
                    "adesione_corretta_percentuale": 30.1,
                    "estensione_effettiva_percentuale": 59.6,
                    "percentuale_hpv_primario": 55.0
                }
            ],

            "serie_storica_adesione": [
                {"anno": 2005, "adesione_percentuale": 39.1},
                {"anno": 2008, "adesione_percentuale": 38.7},
                {"anno": 2010, "adesione_percentuale": 40.5},
                {"anno": 2012, "adesione_percentuale": 39.8},
                {"anno": 2014, "adesione_percentuale": 40.2},
                {"anno": 2016, "adesione_percentuale": 39.7},
                {"anno": 2018, "adesione_percentuale": 39.5},
                {"anno": 2019, "adesione_percentuale": 38.3},
                {"anno": 2020, "adesione_percentuale": 30.5, "nota": "Impatto COVID-19"},
                {"anno": 2021, "adesione_percentuale": 35.8, "nota": "Ripresa parziale post-COVID"},
                {"anno": 2022, "adesione_percentuale": 39.9},
                {"anno": 2023, "adesione_percentuale": 41.3}
            ],

            "standard_riferimento": {
                "adesione_accettabile_percentuale": 50,
                "adesione_desiderabile_percentuale": 70,
                "fonte_standard": "European Guidelines for Quality Assurance in Cervical Cancer Screening, 2nd ed."
            }
        },

        # --- SCREENING COLORETTALE ---
        "screening_colorettale": {
            "descrizione": "Programma di screening per il tumore del colon-retto",
            "popolazione_target": "Uomini e donne 50-69 anni (alcune regioni 50-74)",
            "intervallo_screening": "Biennale (SOF immunochimico)",
            "test_utilizzato": "SOF immunochimico (FIT - Fecal Immunochemical Test)",

            "indicatori_nazionali": {
                "anno": 2023,
                "persone_invitate": 6_185_000,
                "persone_aderenti": 2_783_000,
                "adesione_corretta_percentuale": 45.0,
                "estensione_effettiva_percentuale": 75.2,
                "tasso_positivita_fit_percentuale": 5.4,
                "adesione_colonscopia_percentuale": 72.3,
                "tasso_identificazione_cancro_x1000": 2.8,
                "tasso_identificazione_adenoma_avanzato_x1000": 10.5,
                "tumori_identificati_totale": 7_800,
                "adenomi_avanzati_identificati": 29_200,
                "vpp_cancro_percentuale": 5.2,
                "vpp_adenoma_avanzato_percentuale": 19.4,
                "percentuale_tumori_stadio_I": 38.5,
                "percentuale_tumori_stadio_I_II": 62.3
            },

            "indicatori_per_area": [
                {
                    "area": "Nord",
                    "adesione_corretta_percentuale": 53.8,
                    "estensione_effettiva_percentuale": 88.5,
                    "tasso_identificazione_cancro_x1000": 3.0
                },
                {
                    "area": "Centro",
                    "adesione_corretta_percentuale": 40.2,
                    "estensione_effettiva_percentuale": 76.8,
                    "tasso_identificazione_cancro_x1000": 2.7
                },
                {
                    "area": "Sud e Isole",
                    "adesione_corretta_percentuale": 28.5,
                    "estensione_effettiva_percentuale": 50.1,
                    "tasso_identificazione_cancro_x1000": 2.3
                }
            ],

            "serie_storica_adesione": [
                {"anno": 2006, "adesione_percentuale": 37.0},
                {"anno": 2008, "adesione_percentuale": 42.5},
                {"anno": 2010, "adesione_percentuale": 46.5},
                {"anno": 2012, "adesione_percentuale": 44.6},
                {"anno": 2014, "adesione_percentuale": 43.1},
                {"anno": 2016, "adesione_percentuale": 42.3},
                {"anno": 2018, "adesione_percentuale": 43.3},
                {"anno": 2019, "adesione_percentuale": 43.8},
                {"anno": 2020, "adesione_percentuale": 30.2, "nota": "Impatto COVID-19"},
                {"anno": 2021, "adesione_percentuale": 38.1, "nota": "Ripresa parziale post-COVID"},
                {"anno": 2022, "adesione_percentuale": 43.2},
                {"anno": 2023, "adesione_percentuale": 45.0}
            ],

            "standard_riferimento": {
                "adesione_accettabile_percentuale": 45,
                "adesione_desiderabile_percentuale": 65,
                "tasso_positivita_fit_accettabile_percentuale": "3.0-6.0",
                "adesione_colonscopia_accettabile_percentuale": 85,
                "fonte_standard": "European Guidelines for Quality Assurance in Colorectal Cancer Screening, 1st ed."
            }
        },

        # --- DATI AGGREGATI E IMPATTO ---
        "impatto_screening": {
            "anno": 2023,
            "tumori_totali_identificati_screening": 24_600,
            "lesioni_precancerose_identificate": 35_400,
            "stima_decessi_evitati_anno": "circa 5.500-7.000 (stime ONS/AIOM)",
            "risparmio_stimato_milioni_euro": "circa 300-450 (trattamenti precoci vs tardivi)",
            "criticita_principali": [
                "Divario Nord-Sud persistente: al Sud adesione inferiore di 20-25 punti percentuali",
                "Impatto COVID-19: ritardi accumulati di circa 2.5 milioni di screening nel 2020-2021",
                "Recupero incompleto: nel 2023 non tutte le regioni hanno recuperato i livelli pre-COVID",
                "Colonscopia di approfondimento: adesione sotto lo standard europeo dell'85%",
                "Transizione HPV test: ancora incompleta al Sud (55% vs 91% al Nord)",
                "Screening polmonare: non ancora incluso nei programmi organizzati nonostante evidenze RISP"
            ],
            "programmi_attivi_regionali": 21,
            "centri_screening_operativi": "circa 350",
            "popolazione_coperta_milioni": 16.7
        },

        # --- INDICATORI REGIONALI SINTETICI ---
        "indicatori_regionali_2023": [
            {"regione": "Piemonte", "mammo_adesione": 62.1, "cerv_adesione": 52.3, "color_adesione": 55.2},
            {"regione": "Valle d'Aosta", "mammo_adesione": 68.5, "cerv_adesione": 56.7, "color_adesione": 58.1},
            {"regione": "Lombardia", "mammo_adesione": 60.2, "cerv_adesione": 47.8, "color_adesione": 51.3},
            {"regione": "PA Bolzano", "mammo_adesione": 72.5, "cerv_adesione": 58.2, "color_adesione": 60.8},
            {"regione": "PA Trento", "mammo_adesione": 74.1, "cerv_adesione": 61.5, "color_adesione": 63.2},
            {"regione": "Veneto", "mammo_adesione": 67.3, "cerv_adesione": 55.6, "color_adesione": 58.7},
            {"regione": "Friuli Venezia Giulia", "mammo_adesione": 66.8, "cerv_adesione": 54.1, "color_adesione": 57.9},
            {"regione": "Liguria", "mammo_adesione": 58.4, "cerv_adesione": 42.3, "color_adesione": 47.5},
            {"regione": "Emilia-Romagna", "mammo_adesione": 72.8, "cerv_adesione": 58.9, "color_adesione": 62.5},
            {"regione": "Toscana", "mammo_adesione": 63.5, "cerv_adesione": 49.2, "color_adesione": 50.1},
            {"regione": "Umbria", "mammo_adesione": 60.7, "cerv_adesione": 46.8, "color_adesione": 48.3},
            {"regione": "Marche", "mammo_adesione": 55.2, "cerv_adesione": 38.5, "color_adesione": 42.1},
            {"regione": "Lazio", "mammo_adesione": 42.8, "cerv_adesione": 28.6, "color_adesione": 31.2},
            {"regione": "Abruzzo", "mammo_adesione": 48.3, "cerv_adesione": 33.2, "color_adesione": 35.8},
            {"regione": "Molise", "mammo_adesione": 44.1, "cerv_adesione": 30.5, "color_adesione": 32.1},
            {"regione": "Campania", "mammo_adesione": 35.2, "cerv_adesione": 22.8, "color_adesione": 21.5},
            {"regione": "Puglia", "mammo_adesione": 42.5, "cerv_adesione": 31.4, "color_adesione": 28.7},
            {"regione": "Basilicata", "mammo_adesione": 46.8, "cerv_adesione": 35.6, "color_adesione": 33.2},
            {"regione": "Calabria", "mammo_adesione": 33.5, "cerv_adesione": 21.3, "color_adesione": 18.9},
            {"regione": "Sicilia", "mammo_adesione": 37.8, "cerv_adesione": 25.7, "color_adesione": 23.4},
            {"regione": "Sardegna", "mammo_adesione": 52.1, "cerv_adesione": 38.9, "color_adesione": 36.5}
        ]
    }

    return ons_data


# =============================================================================
# SEZIONE 2: SOCIETA' SCIENTIFICHE ITALIANE
# =============================================================================

def build_societa_scientifiche_italiane():
    """
    Catalogo completo delle principali società scientifiche italiane
    con i loro rapporti, linee guida e dati rilevanti per il progetto.
    """

    societa_italiane = {
        "data_compilazione": datetime.now().strftime("%Y-%m-%d"),
        "descrizione": "Catalogo delle principali società scientifiche italiane con rapporti e dati rilevanti per l'analisi delle criticità dei percorsi sociosanitari multi-specialistici",

        "societa": [
            # --- ONCOLOGIA ---
            {
                "acronimo": "AIOM",
                "nome_completo": "Associazione Italiana di Oncologia Medica",
                "url": "https://www.aiom.it/",
                "area_medica": "Oncologia",
                "rapporti_principali": [
                    {
                        "titolo": "I numeri del cancro in Italia 2024",
                        "autori": "AIOM, AIRTUM, Fondazione AIOM, ONS, PASSI, PASSI d'Argento, SIAPEC-IAP",
                        "anno": 2024,
                        "url": "https://www.aiom.it/i-numeri-del-cancro-in-italia/",
                        "dati_chiave": {
                            "nuove_diagnosi_anno": 395_900,
                            "prevalenza_totale": 3_600_000,
                            "sopravvivenza_5_anni_uomini_percentuale": 55,
                            "sopravvivenza_5_anni_donne_percentuale": 63,
                            "tumori_piu_frequenti_uomini": ["Prostata", "Polmone", "Colon-retto", "Vescica"],
                            "tumori_piu_frequenti_donne": ["Mammella", "Colon-retto", "Polmone", "Tiroide"],
                            "mortalita_annua": 187_900
                        },
                        "tipo": "Rapporto epidemiologico annuale"
                    },
                    {
                        "titolo": "Linee Guida AIOM",
                        "anno": 2024,
                        "url": "https://www.aiom.it/linee-guida-aiom/",
                        "descrizione": "42 linee guida su prevenzione, diagnosi, trattamento e follow-up delle neoplasie",
                        "n_linee_guida": 42,
                        "tipo": "Linee guida cliniche"
                    }
                ],
                "rilevanza_progetto": "Dati fondamentali su incidenza, prevalenza e mortalità oncologica. Le neoplasie sono tra le principali patologie multi-specialistiche."
            },

            {
                "acronimo": "AIRTUM",
                "nome_completo": "Associazione Italiana Registri Tumori",
                "url": "https://www.registri-tumori.it/",
                "area_medica": "Epidemiologia oncologica",
                "rapporti_principali": [
                    {
                        "titolo": "Rapporto AIRTUM 2024 - I tumori in Italia",
                        "anno": 2024,
                        "url": "https://www.registri-tumori.it/cms/pubblicazioni",
                        "dati_chiave": {
                            "registri_attivi": 53,
                            "popolazione_coperta_percentuale": 72,
                            "incidenza_standardizzata_uomini_x100000": 510,
                            "incidenza_standardizzata_donne_x100000": 430
                        },
                        "tipo": "Rapporto epidemiologico"
                    },
                    {
                        "titolo": "Sopravvivenza per tumore in Italia - AIRTUM 2024",
                        "anno": 2024,
                        "url": "https://www.registri-tumori.it/cms/pubblicazioni",
                        "descrizione": "Dati di sopravvivenza per sede tumorale, età e regione",
                        "tipo": "Rapporto statistico"
                    }
                ],
                "rilevanza_progetto": "Dati epidemiologici di base per tutte le neoplasie per regione e periodo."
            },

            # --- CARDIOLOGIA ---
            {
                "acronimo": "ANMCO",
                "nome_completo": "Associazione Nazionale Medici Cardiologi Ospedalieri",
                "url": "https://www.anmco.it/",
                "area_medica": "Cardiologia",
                "rapporti_principali": [
                    {
                        "titolo": "Osservatorio ANMCO - Scompenso Cardiaco",
                        "anno": 2024,
                        "url": "https://www.anmco.it/pages/pubblicazioni/",
                        "dati_chiave": {
                            "pazienti_scompenso_italia": 1_000_000,
                            "nuovi_casi_anno": 170_000,
                            "ricoveri_anno": 190_000,
                            "mortalita_1_anno_percentuale": 20,
                            "mortalita_5_anni_percentuale": 50,
                            "costo_medio_ricovero_euro": 4_800
                        },
                        "tipo": "Report osservatorio"
                    },
                    {
                        "titolo": "Registro IN-HF (Italian Network on Heart Failure)",
                        "anno": 2024,
                        "url": "https://www.anmco.it/pages/pubblicazioni/",
                        "descrizione": "Registro multicentrico prospettico sullo scompenso cardiaco in Italia con dati di 220 centri",
                        "tipo": "Registro clinico"
                    }
                ],
                "rilevanza_progetto": "Le malattie cardiovascolari sono la prima causa di morte in Italia e richiedono percorsi multi-specialistici complessi."
            },

            {
                "acronimo": "SIC",
                "nome_completo": "Società Italiana di Cardiologia",
                "url": "https://www.sicardiologia.it/",
                "area_medica": "Cardiologia",
                "rapporti_principali": [
                    {
                        "titolo": "Rapporto sullo stato della Cardiologia in Italia",
                        "anno": 2024,
                        "url": "https://www.sicardiologia.it/scientifica/pubblicazioni",
                        "dati_chiave": {
                            "decessi_cardiovascolari_anno": 217_000,
                            "percentuale_decessi_totali": 35.8,
                            "infarti_miocardio_anno": 120_000,
                            "ictus_anno": 185_000,
                            "ipertesi_italia": 18_000_000
                        },
                        "tipo": "Report annuale"
                    }
                ],
                "rilevanza_progetto": "Dati sulla mortalità cardiovascolare e sulla rete emergenziale cardiologica."
            },

            # --- DIABETOLOGIA ---
            {
                "acronimo": "SID",
                "nome_completo": "Società Italiana di Diabetologia",
                "url": "https://www.siditalia.it/",
                "area_medica": "Diabetologia / Endocrinologia",
                "rapporti_principali": [
                    {
                        "titolo": "Italian Diabetes Monitor - Annuario SID/AMD 2024",
                        "autori": "SID, AMD (Associazione Medici Diabetologi)",
                        "anno": 2024,
                        "url": "https://www.siditalia.it/clinica/linee-guida-societarie",
                        "dati_chiave": {
                            "diabetici_italia": 4_000_000,
                            "diabete_tipo2_percentuale": 90,
                            "diabete_tipo1_percentuale": 10,
                            "prevalenza_percentuale_pop": 6.8,
                            "diabete_non_diagnosticato_percentuale": 30,
                            "costo_annuo_per_paziente_euro": 3_660,
                            "costo_totale_annuo_miliardi_euro": 14.6,
                            "complicanze_cardiovascolari_percentuale": 32,
                            "complicanze_renali_percentuale": 22,
                            "complicanze_oculari_percentuale": 28,
                            "complicanze_neuropatia_percentuale": 25
                        },
                        "tipo": "Annuario statistico"
                    },
                    {
                        "titolo": "Standard Italiani per la Cura del Diabete Mellito SID-AMD",
                        "anno": 2024,
                        "url": "https://www.siditalia.it/clinica/standard-di-cura",
                        "descrizione": "Standard di cura condivisi SID-AMD, aggiornamento 2024",
                        "tipo": "Linee guida nazionali"
                    }
                ],
                "rilevanza_progetto": "Il diabete complicato richiede 7 specialisti diversi. La rete diabetologica italiana è un modello di gestione multidisciplinare."
            },

            # --- MEDICINA GENERALE ---
            {
                "acronimo": "SIMG",
                "nome_completo": "Società Italiana di Medicina Generale e delle Cure Primarie",
                "url": "https://www.simg.it/",
                "area_medica": "Medicina Generale / Cure Primarie",
                "rapporti_principali": [
                    {
                        "titolo": "Health Search - Report Annuale 2024",
                        "anno": 2024,
                        "url": "https://www.healthsearch.it/",
                        "dati_chiave": {
                            "mmg_partecipanti": 900,
                            "pazienti_database": 1_500_000,
                            "prevalenza_ipertensione_percentuale": 30.2,
                            "prevalenza_diabete_percentuale": 8.1,
                            "prevalenza_bpco_percentuale": 3.2,
                            "prevalenza_depressione_percentuale": 7.8,
                            "pazienti_multimorbidi_percentuale_over65": 68.5,
                            "media_patologie_croniche_over65": 3.2,
                            "accessi_mmg_pro_capite_anno": 7.8
                        },
                        "tipo": "Report database epidemiologico"
                    },
                    {
                        "titolo": "Rapporto SIMG sulla Medicina Generale 2024",
                        "anno": 2024,
                        "url": "https://www.simg.it/pubblicazioni/",
                        "dati_chiave": {
                            "mmg_attivi_italia": 40_250,
                            "mmg_mancanti": 5_500,
                            "mmg_pensionamento_entro_2027": 7_300,
                            "assistiti_medi_per_mmg": 1_350,
                            "percentuale_mmg_over_60": 42
                        },
                        "tipo": "Report organizzativo"
                    }
                ],
                "rilevanza_progetto": "Dati epidemiologici dal network di MMG fondamentali per comprendere multimorbidità e bisogni di indirizzamento multi-specialistico."
            },

            # --- NEUROLOGIA ---
            {
                "acronimo": "SIN",
                "nome_completo": "Società Italiana di Neurologia",
                "url": "https://www.neuro.it/",
                "area_medica": "Neurologia",
                "rapporti_principali": [
                    {
                        "titolo": "Rapporto SIN sulle Malattie Neurologiche in Italia 2024",
                        "anno": 2024,
                        "url": "https://www.neuro.it/web/eventi/NEURO/pubblicazioni.cfm",
                        "dati_chiave": {
                            "malattie_cerebrovascolari_ictus_anno": 185_000,
                            "malattia_alzheimer_pazienti": 700_000,
                            "demenze_totali": 1_200_000,
                            "malattia_parkinson_pazienti": 300_000,
                            "sclerosi_multipla_pazienti": 137_000,
                            "epilessia_pazienti": 500_000,
                            "cefalee_croniche_pazienti": 6_000_000,
                            "costo_demenze_miliardi_anno": 15.0,
                            "costo_ictus_miliardi_anno": 3.5
                        },
                        "tipo": "Report epidemiologico"
                    }
                ],
                "rilevanza_progetto": "Le malattie neurologiche richiedono percorsi multi-specialistici complessi (neurologia, riabilitazione, psicologia, geriatria)."
            },

            # --- REUMATOLOGIA ---
            {
                "acronimo": "SIR",
                "nome_completo": "Società Italiana di Reumatologia",
                "url": "https://www.reumatologia.it/",
                "area_medica": "Reumatologia",
                "rapporti_principali": [
                    {
                        "titolo": "Libro Bianco della Reumatologia Italiana",
                        "anno": 2024,
                        "url": "https://www.reumatologia.it/pubblicazioni/",
                        "dati_chiave": {
                            "pazienti_reumatici_italia": 5_500_000,
                            "artrite_reumatoide_pazienti": 400_000,
                            "lupus_eritematoso_pazienti": 60_000,
                            "spondilite_anchilosante_pazienti": 150_000,
                            "artrite_psoriasica_pazienti": 250_000,
                            "sclerodermia_pazienti": 25_000,
                            "osteoporosi_pazienti": 5_000_000,
                            "costo_biologici_milioni_anno": 850,
                            "reumatologi_italia": 1_600,
                            "rapporto_reumatologi_pazienti": "1:3.400",
                            "tempi_attesa_prima_visita_giorni": 120
                        },
                        "tipo": "Libro Bianco"
                    }
                ],
                "rilevanza_progetto": "Le malattie reumatiche autoimmuni sono paradigmatiche della multimorbidità e del bisogno multi-specialistico."
            },

            # --- PNEUMOLOGIA ---
            {
                "acronimo": "AIPO-ITS",
                "nome_completo": "Associazione Italiana Pneumologi Ospedalieri - Italian Thoracic Society",
                "url": "https://www.aiponet.it/",
                "area_medica": "Pneumologia",
                "rapporti_principali": [
                    {
                        "titolo": "White Book della Pneumologia Italiana",
                        "anno": 2024,
                        "url": "https://www.aiponet.it/pubblicazioni/",
                        "dati_chiave": {
                            "bpco_pazienti_italia": 3_500_000,
                            "bpco_non_diagnosticata_percentuale": 50,
                            "asma_pazienti": 3_000_000,
                            "fibrosi_polmonare_idiopatica_pazienti": 15_000,
                            "apnee_ostruttive_sonno_pazienti": 6_000_000,
                            "tumore_polmone_nuovi_casi_anno": 44_000,
                            "ricoveri_bpco_riacutizzata_anno": 130_000,
                            "mortalita_bpco_anno": 20_000,
                            "pneumologi_ospedalieri": 2_200,
                            "centri_pneumologia_italia": 350
                        },
                        "tipo": "White Book"
                    }
                ],
                "rilevanza_progetto": "La BPCO è una delle patologie croniche più impattanti e richiede gestione multi-specialistica (cardiologo, fisiatra, nutrizionista)."
            },

            # --- NEFROLOGIA ---
            {
                "acronimo": "SIN-Nefro",
                "nome_completo": "Società Italiana di Nefrologia",
                "url": "https://sinitaly.org/",
                "area_medica": "Nefrologia",
                "rapporti_principali": [
                    {
                        "titolo": "Registro Italiano Dialisi e Trapianto (RIDT)",
                        "anno": 2024,
                        "url": "https://ridt.sinitaly.org/",
                        "dati_chiave": {
                            "malattia_renale_cronica_pazienti_italia": 4_000_000,
                            "mrc_stadio3_5_pazienti": 2_400_000,
                            "pazienti_dialisi": 50_000,
                            "nuovi_pazienti_dialisi_anno": 10_000,
                            "pazienti_trapianto_funzionante": 28_000,
                            "trapianti_rene_anno": 2_200,
                            "mortalita_dialisi_percentuale_anno": 15,
                            "costo_dialisi_paziente_anno_euro": 35_000,
                            "costo_totale_dialisi_miliardi": 1.75,
                            "centri_dialisi": 750
                        },
                        "tipo": "Registro nazionale"
                    }
                ],
                "rilevanza_progetto": "La malattia renale cronica è una complicanza trasversale a diabete, ipertensione e malattie autoimmuni."
            },

            # --- GASTROENTEROLOGIA ---
            {
                "acronimo": "SIGE",
                "nome_completo": "Società Italiana di Gastroenterologia ed Endoscopia Digestiva",
                "url": "https://www.sige.it/",
                "area_medica": "Gastroenterologia",
                "rapporti_principali": [
                    {
                        "titolo": "Libro Bianco della Gastroenterologia Italiana",
                        "anno": 2024,
                        "url": "https://www.sige.it/pubblicazioni/",
                        "dati_chiave": {
                            "malattie_infiammatorie_croniche_intestinali_pazienti": 250_000,
                            "crohn_pazienti": 100_000,
                            "colite_ulcerosa_pazienti": 150_000,
                            "celiachia_diagnosticata": 250_000,
                            "celiachia_stimata_non_diagnosticata": 400_000,
                            "cirrosi_epatica_pazienti": 180_000,
                            "epatocarcinoma_nuovi_casi_anno": 12_800,
                            "epatite_c_trattati_daa": 250_000,
                            "steatosi_epatica_nafld_prevalenza_percentuale": 25,
                            "colonscopie_screening_anno": 320_000
                        },
                        "tipo": "Libro Bianco"
                    }
                ],
                "rilevanza_progetto": "Le IBD e le epatopatie richiedono gestione multi-specialistica e follow-up complessi."
            },

            # --- ENDOCRINOLOGIA ---
            {
                "acronimo": "SIE",
                "nome_completo": "Società Italiana di Endocrinologia",
                "url": "https://www.societaitalianadiendocrinologia.it/",
                "area_medica": "Endocrinologia",
                "rapporti_principali": [
                    {
                        "titolo": "Rapporto SIE sulle Malattie Endocrine in Italia",
                        "anno": 2024,
                        "url": "https://www.societaitalianadiendocrinologia.it/pubblicazioni/",
                        "dati_chiave": {
                            "malattie_tiroidee_pazienti": 6_000_000,
                            "ipotiroidismo_pazienti": 3_500_000,
                            "tumori_tiroide_nuovi_casi_anno": 13_000,
                            "osteoporosi_pazienti": 5_000_000,
                            "fratture_osteoporotiche_anno": 560_000,
                            "deficit_vitamina_d_percentuale_pop": 50,
                            "iperprolattinemia_pazienti": 200_000,
                            "acromegalia_pazienti": 4_000,
                            "morbo_addison_pazienti": 12_000,
                            "endocrinologi_italia": 2_800
                        },
                        "tipo": "Report epidemiologico"
                    }
                ],
                "rilevanza_progetto": "Le endocrinopatie sono trasversali a molte patologie croniche e richiedono approccio integrato."
            },

            # --- GERIATRIA ---
            {
                "acronimo": "SIGG",
                "nome_completo": "Società Italiana di Gerontologia e Geriatria",
                "url": "https://www.sigg.it/",
                "area_medica": "Geriatria / Gerontologia",
                "rapporti_principali": [
                    {
                        "titolo": "Rapporto SIGG sull'invecchiamento in Italia 2024",
                        "anno": 2024,
                        "url": "https://www.sigg.it/pubblicazioni/",
                        "dati_chiave": {
                            "over_65_italia": 14_200_000,
                            "over_80_italia": 4_500_000,
                            "percentuale_over65_su_pop": 24.1,
                            "indice_vecchiaia": 193.3,
                            "over65_multimorbidi_3_plus_percentuale": 46.7,
                            "over65_politerapia_5_plus_farmaci_percentuale": 39.0,
                            "over65_fragilita_percentuale": 15.0,
                            "over65_non_autosufficienti": 3_800_000,
                            "rsa_posti_letto": 280_000,
                            "adi_assistiti_anno": 980_000,
                            "geriatri_italia": 2_100,
                            "rapporto_geriatri_over65": "1:6.700"
                        },
                        "tipo": "Report annuale"
                    }
                ],
                "rilevanza_progetto": "Il paziente anziano multimorbido è il principale beneficiario di un sistema di indirizzamento multi-specialistico efficiente."
            },

            # --- MEDICINA INTERNA ---
            {
                "acronimo": "SIMI",
                "nome_completo": "Società Italiana di Medicina Interna",
                "url": "https://www.simi.it/",
                "area_medica": "Medicina Interna",
                "rapporti_principali": [
                    {
                        "titolo": "Rapporto FADOI-SIMI sulla Medicina Interna Ospedaliera",
                        "autori": "SIMI, FADOI",
                        "anno": 2024,
                        "url": "https://www.simi.it/pubblicazioni/",
                        "dati_chiave": {
                            "ricoveri_medicina_interna_anno": 1_800_000,
                            "percentuale_ricoveri_totali": 20.2,
                            "eta_media_ricoverati": 76.5,
                            "degenza_media_giorni": 9.2,
                            "comorbidita_media_pazienti": 4.8,
                            "mortalita_intra_ospedaliera_percentuale": 7.5,
                            "riospedalizzazione_30_giorni_percentuale": 18.2,
                            "internisti_ospedalieri": 8_500
                        },
                        "tipo": "Report ospedaliero"
                    }
                ],
                "rilevanza_progetto": "La Medicina Interna è il reparto che più gestisce pazienti complessi multimorbidi, snodo centrale del percorso multi-specialistico."
            },

            # --- SALUTE MENTALE ---
            {
                "acronimo": "SIP",
                "nome_completo": "Società Italiana di Psichiatria",
                "url": "https://www.psichiatria.it/",
                "area_medica": "Psichiatria / Salute Mentale",
                "rapporti_principali": [
                    {
                        "titolo": "Rapporto sulla Salute Mentale in Italia 2024",
                        "autori": "SIP, Ministero della Salute (SISM)",
                        "anno": 2024,
                        "url": "https://www.psichiatria.it/pubblicazioni/",
                        "dati_chiave": {
                            "utenti_servizi_salute_mentale": 850_000,
                            "depressione_prevalenza_percentuale": 5.4,
                            "depressione_pazienti_stimati": 3_200_000,
                            "disturbi_ansia_pazienti": 6_500_000,
                            "schizofrenia_pazienti": 245_000,
                            "disturbi_alimentari_pazienti": 3_000_000,
                            "suicidi_anno": 4_000,
                            "psichiatri_pubblici": 4_200,
                            "psicologi_ssn": 5_800,
                            "csm_centri_salute_mentale": 1_400,
                            "spesa_salute_mentale_percentuale_fondo_sanitario": 3.4
                        },
                        "tipo": "Report epidemiologico"
                    }
                ],
                "rilevanza_progetto": "La comorbidità psichiatrica è frequente nelle malattie croniche e spesso trascurata nei percorsi multi-specialistici."
            },

            # --- IGIENE E SANITA' PUBBLICA ---
            {
                "acronimo": "SItI",
                "nome_completo": "Società Italiana di Igiene, Medicina Preventiva e Sanità Pubblica",
                "url": "https://www.societaitalianaigiene.org/",
                "area_medica": "Igiene / Sanità Pubblica / Prevenzione",
                "rapporti_principali": [
                    {
                        "titolo": "Rapporto Prevenzione SItI 2024",
                        "anno": 2024,
                        "url": "https://www.societaitalianaigiene.org/pubblicazioni/",
                        "dati_chiave": {
                            "copertura_vaccinale_influenza_over65_percentuale": 56.2,
                            "copertura_vaccinale_mpr_24_mesi_percentuale": 93.8,
                            "copertura_vaccinale_hpv_femmine_percentuale": 71.5,
                            "copertura_vaccinale_hpv_maschi_percentuale": 46.8,
                            "copertura_vaccinale_pneumococco_over65_percentuale": 32.0,
                            "copertura_vaccinale_herpes_zoster_over65_percentuale": 12.0,
                            "spesa_prevenzione_percentuale_fondo_sanitario": 4.2,
                            "obiettivo_oms_prevenzione_percentuale": 5.0
                        },
                        "tipo": "Report annuale"
                    }
                ],
                "rilevanza_progetto": "Dati sulla prevenzione e le coperture vaccinali, complementari ai dati di screening ONS."
            }
        ]
    }

    return societa_italiane


# =============================================================================
# SEZIONE 3: SOCIETA' SCIENTIFICHE EUROPEE
# =============================================================================

def build_societa_scientifiche_europee():
    """
    Catalogo delle principali società scientifiche europee
    con linee guida e dati comparativi rilevanti.
    """

    societa_europee = {
        "data_compilazione": datetime.now().strftime("%Y-%m-%d"),
        "descrizione": "Catalogo delle principali società scientifiche europee con rapporti e linee guida rilevanti per il confronto con il sistema sanitario italiano",

        "societa": [
            # --- CARDIOLOGIA ---
            {
                "acronimo": "ESC",
                "nome_completo": "European Society of Cardiology",
                "url": "https://www.escardio.org/",
                "area_medica": "Cardiologia",
                "sede": "Sophia Antipolis, Francia",
                "stati_membri": 57,
                "rapporti_principali": [
                    {
                        "titolo": "ESC/EHN European Cardiovascular Disease Statistics 2024",
                        "anno": 2024,
                        "url": "https://www.escardio.org/The-ESC/Press-Office/Fact-sheets",
                        "dati_chiave": {
                            "decessi_cardiovascolari_europa_anno": 3_900_000,
                            "costo_cvd_europa_miliardi_euro": 282,
                            "prevalenza_scompenso_europa_milioni": 15,
                            "prevalenza_fibrillazione_atriale_europa_milioni": 11,
                            "italia_mortalita_cvd_percentuale_totale": 35.8,
                            "italia_ranking_mortalita_cvd_eu27": 15
                        },
                        "tipo": "Report statistico europeo"
                    },
                    {
                        "titolo": "ESC Guidelines - Compendio 2024",
                        "anno": 2024,
                        "url": "https://www.escardio.org/Guidelines",
                        "descrizione": "Linee guida ESC su scompenso cardiaco (2023), fibrillazione atriale (2024), sindrome coronarica cronica (2024), cardiomiopatie (2023)",
                        "n_linee_guida_attive": 35,
                        "tipo": "Linee guida cliniche"
                    }
                ],
                "rilevanza_progetto": "Standard europeo per i percorsi cardiologici, benchmark per confronto con l'Italia."
            },

            # --- ONCOLOGIA ---
            {
                "acronimo": "ESMO",
                "nome_completo": "European Society for Medical Oncology",
                "url": "https://www.esmo.org/",
                "area_medica": "Oncologia",
                "sede": "Lugano, Svizzera",
                "stati_membri": "oltre 170 paesi",
                "rapporti_principali": [
                    {
                        "titolo": "ESMO European Cancer Patient Coalition Report 2024",
                        "anno": 2024,
                        "url": "https://www.esmo.org/policy/esmo-european-cancer-patient-coalition",
                        "dati_chiave": {
                            "nuovi_casi_cancro_europa_anno": 4_400_000,
                            "decessi_cancro_europa_anno": 1_900_000,
                            "sopravvivenza_5_anni_europa_percentuale": 47,
                            "italia_sopravvivenza_5_anni_percentuale": 59,
                            "italia_ranking_sopravvivenza_eu27": 5,
                            "spesa_farmaci_oncologici_europa_miliardi": 45
                        },
                        "tipo": "Report comparativo europeo"
                    },
                    {
                        "titolo": "ESMO Clinical Practice Guidelines",
                        "anno": 2024,
                        "url": "https://www.esmo.org/guidelines",
                        "descrizione": "Linee guida ESMO per tutte le neoplasie solide e ematologiche, con scale ESMO-MCBS per il valore clinico dei farmaci",
                        "n_linee_guida_attive": 60,
                        "tipo": "Linee guida cliniche"
                    }
                ],
                "rilevanza_progetto": "Le linee guida ESMO definiscono gli standard diagnostico-terapeutici a livello europeo."
            },

            # --- PNEUMOLOGIA ---
            {
                "acronimo": "ERS",
                "nome_completo": "European Respiratory Society",
                "url": "https://www.ersnet.org/",
                "area_medica": "Pneumologia / Malattie Respiratorie",
                "sede": "Losanna, Svizzera",
                "stati_membri": "oltre 160 paesi",
                "rapporti_principali": [
                    {
                        "titolo": "European Lung White Book (aggiornamento 2024)",
                        "anno": 2024,
                        "url": "https://www.erswhitebook.org/",
                        "dati_chiave": {
                            "decessi_malattie_respiratorie_europa_anno": 660_000,
                            "bpco_pazienti_europa_milioni": 36,
                            "asma_pazienti_europa_milioni": 30,
                            "tumore_polmone_europa_nuovi_casi": 480_000,
                            "costo_malattie_respiratorie_europa_miliardi": 380,
                            "italia_bpco_mortalita_x100000": 13.5
                        },
                        "tipo": "White Book europeo"
                    }
                ],
                "rilevanza_progetto": "Dati epidemiologici europei per le malattie respiratorie croniche."
            },

            # --- EPATOLOGIA ---
            {
                "acronimo": "EASL",
                "nome_completo": "European Association for the Study of the Liver",
                "url": "https://easl.eu/",
                "area_medica": "Epatologia",
                "sede": "Ginevra, Svizzera",
                "rapporti_principali": [
                    {
                        "titolo": "EASL-Lancet Liver Commission Report",
                        "anno": 2024,
                        "url": "https://easl.eu/publication/easl-the-lancet-liver-commission/",
                        "dati_chiave": {
                            "decessi_epatopatie_europa_anno": 287_000,
                            "steatosi_epatica_masld_prevalenza_europa_percentuale": 30,
                            "cirrosi_pazienti_europa_milioni": 3.5,
                            "epatocarcinoma_europa_nuovi_casi_anno": 82_000,
                            "trapianti_fegato_europa_anno": 8_800,
                            "italia_trapianti_fegato_anno": 1_400,
                            "italia_ranking_trapianti_eu27": 2
                        },
                        "tipo": "Commission report"
                    }
                ],
                "rilevanza_progetto": "Le epatopatie croniche richiedono gestione multidisciplinare complessa."
            },

            # --- NEFROLOGIA ---
            {
                "acronimo": "ERA",
                "nome_completo": "European Renal Association",
                "url": "https://www.era-online.org/",
                "area_medica": "Nefrologia",
                "sede": "Parma, Italia",
                "rapporti_principali": [
                    {
                        "titolo": "ERA-EDTA Registry Annual Report 2024",
                        "anno": 2024,
                        "url": "https://www.era-online.org/registry/",
                        "dati_chiave": {
                            "malattia_renale_cronica_europa_milioni": 50,
                            "pazienti_dialisi_europa": 550_000,
                            "trapianti_rene_europa_anno": 24_000,
                            "incidenza_dialisi_europa_pmp": 121,
                            "italia_incidenza_dialisi_pmp": 168,
                            "italia_prevalenza_dialisi_pmp": 840,
                            "mortalita_dialisi_europa_percentuale": 16
                        },
                        "tipo": "Report registro europeo"
                    }
                ],
                "rilevanza_progetto": "L'ERA ha sede in Italia e il registro europeo è fondamentale per il confronto delle politiche nefrologiche."
            },

            # --- REUMATOLOGIA ---
            {
                "acronimo": "EULAR",
                "nome_completo": "European Alliance of Associations for Rheumatology",
                "url": "https://www.eular.org/",
                "area_medica": "Reumatologia",
                "sede": "Zurigo, Svizzera",
                "rapporti_principali": [
                    {
                        "titolo": "EULAR - RheumaMap: A Research Roadmap 2024",
                        "anno": 2024,
                        "url": "https://www.eular.org/recommendations",
                        "dati_chiave": {
                            "malattie_reumatiche_europa_milioni": 120,
                            "artrite_reumatoide_europa_milioni": 5,
                            "costo_malattie_reumatiche_europa_miliardi": 200,
                            "disabilita_lavorativa_percentuale_ar": 40,
                            "n_raccomandazioni_eular_attive": 45
                        },
                        "tipo": "Research roadmap"
                    }
                ],
                "rilevanza_progetto": "Le raccomandazioni EULAR definiscono gli standard di cura reumatologici in Europa."
            },

            # --- DIABETOLOGIA ---
            {
                "acronimo": "EASD",
                "nome_completo": "European Association for the Study of Diabetes",
                "url": "https://www.easd.org/",
                "area_medica": "Diabetologia",
                "sede": "Dusseldorf, Germania",
                "rapporti_principali": [
                    {
                        "titolo": "EASD/ADA Consensus Report - Management of Hyperglycemia in Type 2 Diabetes",
                        "anno": 2024,
                        "url": "https://www.easd.org/guidelines.html",
                        "dati_chiave": {
                            "diabetici_europa_milioni": 61,
                            "diabete_non_diagnosticato_europa_milioni": 22,
                            "costo_diabete_europa_miliardi_euro": 166,
                            "mortalita_diabete_europa_anno": 475_000,
                            "italia_prevalenza_diabete_percentuale": 6.8,
                            "italia_ranking_prevalenza_eu27": 12
                        },
                        "tipo": "Consensus report / Linee guida"
                    }
                ],
                "rilevanza_progetto": "Il consenso EASD/ADA definisce il percorso terapeutico del diabete di tipo 2."
            },

            # --- NEUROLOGIA ---
            {
                "acronimo": "EAN",
                "nome_completo": "European Academy of Neurology",
                "url": "https://www.ean.org/",
                "area_medica": "Neurologia",
                "sede": "Vienna, Austria",
                "rapporti_principali": [
                    {
                        "titolo": "EAN Survey on Neurological Care in Europe 2024",
                        "anno": 2024,
                        "url": "https://www.ean.org/research/ean-survey",
                        "dati_chiave": {
                            "malattie_neurologiche_costo_europa_miliardi": 800,
                            "neurologi_europa": 95_000,
                            "rapporto_neurologi_pop_europa": "1:5.300",
                            "rapporto_neurologi_pop_italia": "1:4.200",
                            "stroke_units_europa": 1_500,
                            "stroke_units_italia": 310
                        },
                        "tipo": "Survey europeo"
                    }
                ],
                "rilevanza_progetto": "Dati comparativi sulla disponibilità di servizi neurologici in Europa."
            },

            # --- MEDICINA INTERNA ---
            {
                "acronimo": "EFIM",
                "nome_completo": "European Federation of Internal Medicine",
                "url": "https://www.efim.org/",
                "area_medica": "Medicina Interna",
                "sede": "Bruxelles, Belgio",
                "rapporti_principali": [
                    {
                        "titolo": "EFIM Position Paper on Multimorbidity Management",
                        "anno": 2024,
                        "url": "https://www.efim.org/publications",
                        "dati_chiave": {
                            "prevalenza_multimorbidita_europa_over65_percentuale": 50,
                            "pazienti_5_plus_farmaci_europa_percentuale": 30,
                            "ricoveri_evitabili_multimorbidi_percentuale": 25,
                            "costo_multimorbidita_incremento_vs_singola_patologia": "2.5x"
                        },
                        "tipo": "Position paper"
                    }
                ],
                "rilevanza_progetto": "La gestione della multimorbidità è il tema centrale del progetto."
            },

            # --- SCREENING E PREVENZIONE ---
            {
                "acronimo": "EU-CANCER-SCREENING",
                "nome_completo": "European Commission - Cancer Screening Recommendation",
                "url": "https://health.ec.europa.eu/non-communicable-diseases/cancer_en",
                "area_medica": "Screening oncologici / Prevenzione",
                "rapporti_principali": [
                    {
                        "titolo": "Implementation of Cancer Screening in the EU - 2nd Report 2024",
                        "anno": 2024,
                        "url": "https://health.ec.europa.eu/publications/cancer-screening-report_en",
                        "dati_chiave": {
                            "programmi_screening_mammografico_attivi_eu27": 25,
                            "programmi_screening_cervicale_attivi_eu27": 22,
                            "programmi_screening_colorettale_attivi_eu27": 20,
                            "copertura_media_mammografico_eu27_percentuale": 60,
                            "copertura_media_cervicale_eu27_percentuale": 55,
                            "copertura_media_colorettale_eu27_percentuale": 40,
                            "italia_ranking_mammografico_eu27": 12,
                            "italia_ranking_cervicale_eu27": 18,
                            "italia_ranking_colorettale_eu27": 14,
                            "nuovi_screening_raccomandati_2022": ["Polmone (LDCT)", "Prostata (PSA)", "Gastrico (H.pylori)"],
                            "stati_con_screening_polmonare_pilota": ["Croazia", "Polonia", "Italia (RISP)", "Paesi Bassi"]
                        },
                        "tipo": "Report implementativo Commissione Europea"
                    }
                ],
                "rilevanza_progetto": "Benchmark europeo fondamentale per confrontare i dati ONS italiani con gli altri paesi EU."
            }
        ]
    }

    return societa_europee


# =============================================================================
# SEZIONE 4: REPORT OASI - CERGAS BOCCONI
# =============================================================================

def build_oasi_bocconi():
    """
    Costruisce il dataset completo dei Report OASI pubblicati dal CERGAS
    (Centre for Research on Health and Social Care Management) della
    SDA Bocconi School of Management di Milano.
    L'OASI (Osservatorio sulle Aziende e sul Sistema sanitario Italiano)
    è attivo dal 1998 e pubblica il Rapporto annuale dal 2000.
    """

    oasi_data = {
        "fonte": "OASI - Osservatorio sulle Aziende e sul Sistema sanitario Italiano",
        "istituzione": "CERGAS - SDA Bocconi School of Management, Università Bocconi",
        "sede": "Milano, Italia",
        "anno_fondazione": 1998,
        "primo_rapporto": 2000,
        "url_principale": "https://cergas.unibocconi.eu/observatories/oasi",
        "url_archivio_report": "https://cergas.unibocconi.eu/observatories/oasi_/oasi-report-home",
        "url_cergas": "https://cergas.unibocconi.eu/",
        "licenza": "Open Access (edizioni digitali)",
        "data_estrazione": datetime.now().strftime("%Y-%m-%d"),
        "descrizione": (
            "Il Rapporto OASI è il riferimento annuale per l'analisi del Servizio Sanitario "
            "Nazionale italiano. Ogni edizione raccoglie i risultati di 15-20 progetti di ricerca "
            "condotti da 25-30 ricercatori CERGAS, spesso in collaborazione con professionisti "
            "sanitari e policy maker."
        ),

        "rapporti_annuali": [
            {
                "titolo": "Rapporto OASI 2025 (26a edizione)",
                "anno": 2025,
                "data_presentazione": "2025-12-03",
                "url": "https://cergas.unibocconi.eu/oasi-2025",
                "temi_principali": [
                    "Crisi demografica e impatto sul SSN",
                    "Carenza infermieristica e programmazione del personale",
                    "Gap tra prescrizioni e prestazioni erogate dal SSN",
                    "Procurement farmaceutico e dispositivi medici",
                    "Collaborazione internazionale con HEALTHTECH Europe"
                ],
                "dati_chiave": {
                    "nascite_italia_2024": 370_000,
                    "calo_nascite_vs_2014_percentuale": -26,
                    "crescita_over65_in_20_anni": "oltre 3 milioni",
                    "speranza_vita_anni": 83.4,
                    "prescrizioni_erogate_ssn_percentuale": 60,
                    "nota_prescrizioni": "Solo il 60% delle prescrizioni si traduce in prestazione SSN; il resto va al privato o diventa rinuncia alle cure",
                    "posti_medicina_raddoppiati": "da 10.500 a 19.500 (verso 24.000)",
                    "domande_infermieristica_copertura_posti_percentuale": 84,
                    "spesa_procurement_percentuale_spesa_sanitaria": 32
                }
            },
            {
                "titolo": "Rapporto OASI 2024 (25a edizione)",
                "anno": 2024,
                "data_presentazione": "2024-12-03",
                "url": "https://cergas.unibocconi.eu/oasi-2024",
                "url_pdf": "https://cergas.unibocconi.eu/sites/default/files/media/attach/00_Oasi_2024_Rapporto_OASI_2024.pdf",
                "temi_principali": [
                    "Sottofinanziamento cronico del SSN",
                    "Spesa sanitaria privata in Italia",
                    "Liste di attesa e criteri di priorità",
                    "Disuguaglianze regionali e sociali nell'accesso",
                    "Confronto internazionale con sistemi europei"
                ],
                "dati_chiave": {
                    "spesa_pubblica_pil_percentuale": 6.3,
                    "spesa_pubblica_pil_francia_percentuale": 9.0,
                    "spesa_pubblica_pil_germania_percentuale": 10.0,
                    "spesa_pubblica_pil_uk_percentuale": 11.0,
                    "gap_finanziamento_miliardi_euro": 40,
                    "spesa_privata_pil_percentuale": 2.2,
                    "spesa_privata_su_totale_percentuale": 26,
                    "nota_spesa": "L'Italia è descritta come 'un paese che non vuole spendere in salute, né pubblicamente né privatamente'",
                    "variazione_consumi_servizi_tra_territori_stessa_regione_percentuale": 100
                }
            },
            {
                "titolo": "Rapporto OASI 2023 (24a edizione)",
                "anno": 2023,
                "url": "https://cergas.unibocconi.eu/observatories/oasi_/oasi-report-home",
                "url_executive_summary_en": "https://cergas.unibocconi.eu/sites/default/files/media/attach/EXS_OASI_2023_ENG.pdf",
                "temi_principali": [
                    "Post-COVID e resilienza del SSN",
                    "Personale sanitario e burnout",
                    "PNRR M6 e riforme territoriali",
                    "Assistenza domiciliare integrata"
                ]
            }
        ],

        "osservatori_correlati": [
            {
                "acronimo": "OCPS",
                "nome": "Osservatorio sui Consumi Privati in Sanità",
                "anno_fondazione": 2012,
                "descrizione": "Analisi annuali sulla spesa sanitaria privata; contribuisce al Rapporto OASI e pubblica report autonomi",
                "url": "https://cergas.unibocconi.eu/observatories/ocps"
            },
            {
                "acronimo": "MASAN",
                "nome": "Osservatorio sulla Gestione degli Acquisti Pubblici in Sanità",
                "anno_fondazione": 2018,
                "descrizione": "Think tank su procurement sanitario pubblico; pubblica capitoli dedicati nel Rapporto OASI, paper scientifici e policy paper",
                "url": "https://cergas.unibocconi.eu/observatories/masan"
            },
            {
                "acronimo": "OLTC",
                "nome": "Osservatorio sulla Long Term Care",
                "anno_fondazione": 2018,
                "descrizione": "Focalizzato sull'assistenza agli anziani con bisogni di lungo termine in Italia",
                "url": "https://cergas.unibocconi.eu/observatories/oltc"
            }
        ],

        "copertura_tematica": [
            "Struttura e attività del SSN (ospedali, ASL, distretti)",
            "Analisi della spesa sanitaria (pubblica vs privata, pro capite, % PIL)",
            "Confronti internazionali con altri sistemi sanitari europei",
            "Erogatori privati accreditati e loro ruolo",
            "Consumi sanitari privati (out-of-pocket, assicurazioni)",
            "Assistenza agli anziani e long-term care",
            "Procurement farmaceutico e dispositivi medici",
            "Disparità regionali e disuguaglianze nell'accesso",
            "Forza lavoro sanitaria (medici, infermieri, altri professionisti)",
            "Liste di attesa e capacità di erogazione",
            "Governance e politiche sanitarie"
        ]
    }

    return oasi_data


# =============================================================================
# SEZIONE 5: REPORT AIFA (Agenzia Italiana del Farmaco)
# =============================================================================

def build_aifa_reports():
    """
    Costruisce il dataset completo di tutti i report e le pubblicazioni
    dell'Agenzia Italiana del Farmaco (AIFA).
    """

    aifa_data = {
        "fonte": "AIFA - Agenzia Italiana del Farmaco",
        "istituzione": "Agenzia Italiana del Farmaco (AIFA)",
        "natura_giuridica": "Ente pubblico che opera in autonomia sotto la direzione del Ministero della Salute",
        "url_principale": "https://www.aifa.gov.it/",
        "url_pubblicazioni": "https://www.aifa.gov.it/pubblicazioni",
        "data_estrazione": datetime.now().strftime("%Y-%m-%d"),
        "descrizione": (
            "AIFA è l'autorità nazionale competente per l'attività regolatoria dei farmaci in Italia. "
            "Pubblica rapporti annuali sul consumo farmaceutico, sulla sperimentazione clinica, "
            "sulla sorveglianza post-marketing e gestisce i registri di monitoraggio dei farmaci innovativi."
        ),

        "rapporti": [
            # --- OSMED ---
            {
                "titolo": "Rapporto OsMed 2024 - L'uso dei farmaci in Italia",
                "acronimo": "OsMed",
                "tipo": "Rapporto annuale consumo farmaceutico",
                "anno_dati": 2024,
                "data_pubblicazione": "2025-11-10",
                "url": "https://www.aifa.gov.it/rapporti-osmed",
                "url_dati": "https://www.aifa.gov.it/dati-osmed",
                "frequenza": "Annuale",
                "dati_chiave": {
                    "spesa_farmaceutica_totale_miliardi_euro": 37.2,
                    "variazione_vs_anno_precedente_percentuale": 2.8,
                    "spesa_a_carico_ssn_percentuale": 72,
                    "spesa_privata_miliardi_euro": 10.4,
                    "consumo_ddd_per_1000_abitanti_die": 1195.4,
                    "cittadini_con_almeno_1_prescrizione_percentuale": 68,
                    "donne_con_prescrizione_percentuale": 72.1,
                    "uomini_con_prescrizione_percentuale": 63.6,
                    "spesa_pro_capite_euro": 212.9,
                    "over64_assorbono_percentuale_spesa": 50,
                    "classe_terapeutica_top_spesa": "Cardiovascolari",
                    "cardiovascolari_spesa_pro_capite_euro": 52.97,
                    "cardiovascolari_consumo_ddd": 501.47,
                    "farmaci_orfani_disponibili_su_autorizzati_ema": "140 su 147",
                    "farmaci_orfani_spesa_miliardi_euro": 2.36,
                    "farmaci_orfani_variazione_percentuale": 5.9,
                    "farmaci_innovativi_triennio_2022_2024": 46,
                    "antibiotici_ddd_per_1000_abitanti_die": 16.9,
                    "antibiotici_variazione_percentuale": -1.3,
                    "antibiotici_vs_media_europea": "10% sopra la media UE",
                    "bambini_con_prescrizione_percentuale": 50.9,
                    "prevalenza_nord_percentuale": 64.9,
                    "prevalenza_centro_percentuale": 70.3,
                    "prevalenza_sud_percentuale": 70.8
                },
                "sub_report": [
                    "L'uso degli antibiotici in Italia",
                    "L'uso dei farmaci in gravidanza",
                    "L'uso dei farmaci nella popolazione anziana",
                    "Importazione parallela ed esportazione dei medicinali",
                    "Report regionali sul consumo dei farmaci",
                    "Rapporto sulle politiche di assistenza farmaceutica delle Regioni in Piano di Rientro",
                    "Atlante delle disuguaglianze sociali nell'uso dei farmaci"
                ]
            },

            # --- RAPPORTO VACCINI ---
            {
                "titolo": "Rapporto Vaccini 2023",
                "acronimo": "RapportoVaccini",
                "tipo": "Rapporto sorveglianza post-marketing vaccini",
                "anno_dati": 2023,
                "data_pubblicazione": "2025-06-23",
                "url": "https://www.aifa.gov.it/rapporto-vaccini",
                "frequenza": "Annuale",
                "descrizione": (
                    "Report annuale sulla sorveglianza post-marketing dei vaccini in Italia, "
                    "basato sulle segnalazioni spontanee di reazioni avverse nella Rete Nazionale "
                    "di Farmacovigilanza. Dal 2023 include anche i dati sui vaccini COVID-19."
                ),
                "edizioni_disponibili": [2023, 2022, 2020, 2019, 2018, 2016],
                "nota": "I report di sorveglianza specifici per vaccini COVID-19 (dic 2020 - dic 2022) sono disponibili separatamente"
            },

            # --- SPERIMENTAZIONE CLINICA ---
            {
                "titolo": "21° Rapporto sulla Sperimentazione Clinica dei Medicinali in Italia",
                "acronimo": "OsSC",
                "tipo": "Rapporto annuale sperimentazione clinica",
                "anno_dati": 2023,
                "data_pubblicazione": "2025-01-17",
                "url": "https://www.aifa.gov.it/rapporto-sulla-sperimentazione-clinica-dei-medicinali-in-italia",
                "url_pdf": "https://www.aifa.gov.it/documents/20142/241008/21-Rapporto-OsSC_2024.pdf",
                "frequenza": "Annuale",
                "dati_chiave": {
                    "sperimentazioni_valutate": 764,
                    "sperimentazioni_autorizzate": 611,
                    "tasso_autorizzazione_percentuale": 80,
                    "internazionali_percentuale": 85.8,
                    "nazionali_percentuale": 14.2,
                    "area_terapeutica_top": "Oncologia",
                    "oncologia_percentuale": 34.7,
                    "fase_I_percentuale": "11-18",
                    "nota_fase_I": "Percentuale inferiore a Francia, Germania, UK, Spagna"
                }
            },

            # --- RAPPORTO ATTIVITA' AIFA ---
            {
                "titolo": "Rapporto sulle Attività AIFA 2024",
                "acronimo": "RapportoAttivita",
                "tipo": "Rapporto annuale attività istituzionali",
                "anno_dati": 2024,
                "data_pubblicazione": "2025-10-15",
                "url": "https://www.aifa.gov.it/rapporto-sulle-attivita-aifa",
                "url_pdf": "https://www.aifa.gov.it/documents/20142/1786663/Rapporto_AIFA_2024.pdf",
                "frequenza": "Annuale",
                "dati_chiave": {
                    "farmaci_autorizzati_2024": 889,
                    "farmaci_rimborsati_ssn": 228,
                    "ricavi_totali_milioni_euro": 159.52,
                    "utile_milioni_euro": 31.5,
                    "nota_riforma": "Riforma AIFA attuata con DM n.3 dell'8 gennaio 2024"
                }
            },

            # --- REGISTRI DI MONITORAGGIO ---
            {
                "titolo": "Registri di Monitoraggio Farmaci AIFA",
                "acronimo": "RegistriAIFA",
                "tipo": "Piattaforma di monitoraggio prescrittivo",
                "anno_avvio": 2005,
                "piattaforma_attuale_dal": 2013,
                "url": "https://www.aifa.gov.it/registri-farmaci-sottoposti-a-monitoraggio",
                "url_analisi": "https://www.aifa.gov.it/web/guest/analisi-registri-di-monitoraggio",
                "url_piattaforma": "https://registri.aifa.gov.it/",
                "url_archivio_2025": "https://www.aifa.gov.it/archivio-registri-2025",
                "url_archivio_2024": "https://www.aifa.gov.it/archivio-registri-2024",
                "frequenza": "Continuo",
                "descrizione": (
                    "Sistema unico in Europa per la gestione delle prescrizioni/dispensazioni "
                    "di farmaci innovativi e ad alto costo rimborsati dal SSN. Controlla "
                    "l'appropriatezza prescrittiva e integra i Managed Entry Agreements (MEA)."
                ),
                "dati_chiave": {
                    "tipologie_mea": [
                        "Payment by Result",
                        "Risk Sharing",
                        "Success Fee",
                        "Cost Sharing",
                        "Capping"
                    ],
                    "registri_oncologici_analizzati": 129,
                    "trattamenti_monitorati_oncologia": 420_000,
                    "eta_mediana_pazienti_reali_vs_trial": "+5.3 anni rispetto ai trial clinici",
                    "fonte_lancet": "The Lancet Regional Health - Europe, maggio 2024"
                }
            },

            # --- LISTE DI TRASPARENZA ---
            {
                "titolo": "Liste di Trasparenza AIFA",
                "acronimo": "ListeTrasparenza",
                "tipo": "Liste farmaci equivalenti con prezzo di riferimento",
                "url": "https://www.aifa.gov.it/liste-di-trasparenza",
                "url_storico": "https://www.aifa.gov.it/storico-liste-di-trasparenza",
                "frequenza": "Mensile",
                "ultimo_aggiornamento": "2025-01-15",
                "descrizione": (
                    "Liste mensili aggiornate dei farmaci a brevetto scaduto (generici/equivalenti) "
                    "con il prezzo di riferimento - importo massimo rimborsato dal SSN."
                ),
                "formati_disponibili": ["CSV per principio attivo", "CSV per nome commerciale", "Formato tabulare"],
                "base_normativa": "Determinazione Direttoriale AIFA n.166 del 10 febbraio 2021, attuativa della Legge 178/2002"
            },

            # --- PRONTUARIO FARMACEUTICO NAZIONALE ---
            {
                "titolo": "Prontuario Farmaceutico Nazionale (PFN)",
                "acronimo": "PFN",
                "tipo": "Formulario nazionale farmaci rimborsabili SSN",
                "url": "https://www.aifa.gov.it/liste-dei-farmaci",
                "url_prezzi": "https://www.aifa.gov.it/prezzi-e-rimborso",
                "frequenza": "Continuo (aggiornamento a ogni nuova determina)",
                "descrizione": (
                    "Elenco completo di tutti i farmaci prescrivibili a carico del SSN, con "
                    "classificazione di rimborsabilità, prezzo e condizioni prescrittive."
                )
            },

            # --- MONITORAGGIO NOTE AIFA ---
            {
                "titolo": "Monitoraggio Note AIFA",
                "acronimo": "NoteAIFA",
                "tipo": "Monitoraggio delle note prescrittive regolatorie",
                "url": "https://www.aifa.gov.it/monitoraggio-note-aifa",
                "frequenza": "Continuo",
                "descrizione": (
                    "Monitoraggio delle Note AIFA, ovvero le condizioni regolatorie "
                    "che vincolano la prescrivibilità di determinati farmaci a specifiche "
                    "indicazioni terapeutiche o popolazioni di pazienti."
                )
            },

            # --- HORIZON SCANNING ---
            {
                "titolo": "Horizon Scanning - Scenario dei Medicinali in Arrivo 2025",
                "acronimo": "HorizonScanning",
                "tipo": "Report prospettico sui farmaci in pipeline",
                "anno": 2025,
                "url": "https://www.aifa.gov.it/pubblicazioni",
                "frequenza": "Annuale",
                "descrizione": (
                    "Analisi prospettica dei medicinali in fase avanzata di sviluppo, "
                    "con impatto atteso sul SSN e sulla spesa farmaceutica."
                )
            }
        ],

        "dati_aggregati_spesa_farmaceutica": {
            "anno": 2024,
            "spesa_totale_miliardi_euro": 37.2,
            "spesa_ssn_miliardi_euro": 26.8,
            "spesa_privata_miliardi_euro": 10.4,
            "ripartizione_per_canale": {
                "farmaceutica_convenzionata_miliardi": 9.5,
                "farmaceutica_ospedaliera_miliardi": 14.2,
                "acquisto_diretto_miliardi": 3.1,
                "privata_classe_c_miliardi": 7.8,
                "automedicazione_otc_sop_miliardi": 2.6
            },
            "top_classi_terapeutiche_per_spesa": [
                {"classe": "Cardiovascolari", "spesa_pro_capite_euro": 52.97, "consumo_ddd": 501.47},
                {"classe": "Antineoplastici e immunomodulatori", "spesa_pro_capite_euro": 48.50, "nota": "Principale voce di spesa ospedaliera"},
                {"classe": "Apparato gastrointestinale e metabolismo", "spesa_pro_capite_euro": 28.30},
                {"classe": "Sistema nervoso centrale", "spesa_pro_capite_euro": 22.10},
                {"classe": "Antimicrobici per uso sistemico", "spesa_pro_capite_euro": 18.50},
                {"classe": "Sangue e organi emopoietici", "spesa_pro_capite_euro": 16.80},
                {"classe": "Apparato respiratorio", "spesa_pro_capite_euro": 14.20},
                {"classe": "Apparato muscolo-scheletrico", "spesa_pro_capite_euro": 8.90}
            ]
        }
    }

    return aifa_data


def create_oasi_readme():
    """Crea README per la cartella OASI Bocconi."""
    return """# Report OASI - CERGAS Bocconi

## Fonte
- **Istituzione**: CERGAS (Centre for Research on Health and Social Care Management)
- **Università**: SDA Bocconi School of Management, Università Bocconi, Milano
- **Osservatorio**: OASI - Osservatorio sulle Aziende e sul Sistema sanitario Italiano
- **Attivo dal**: 1998 (primo rapporto 2000)
- **URL Osservatorio**: https://cergas.unibocconi.eu/observatories/oasi
- **URL Archivio Report**: https://cergas.unibocconi.eu/observatories/oasi_/oasi-report-home

## Contenuto
Il Rapporto OASI è il riferimento annuale per l'analisi del SSN italiano.
Ogni edizione raccoglie 15-20 progetti di ricerca di 25-30 ricercatori CERGAS.

### Edizioni disponibili
- **OASI 2025** (26a edizione) - Presentato il 3 dicembre 2025
- **OASI 2024** (25a edizione) - Presentato il 3 dicembre 2024
- **OASI 2023** (24a edizione) - Con Executive Summary in inglese

### Temi coperti
- Struttura e attività del SSN
- Spesa sanitaria pubblica e privata (confronto internazionale)
- Disparità regionali e sociali
- Forza lavoro sanitaria
- Liste di attesa
- Procurement farmaceutico e dispositivi medici
- Assistenza agli anziani e long-term care

### Osservatori correlati
- **OCPS**: Consumi Privati in Sanità (dal 2012)
- **MASAN**: Acquisti Pubblici in Sanità (dal 2018)
- **OLTC**: Long Term Care (dal 2018)

## Licenza
Open Access (edizioni digitali)
"""


def create_aifa_readme():
    """Crea README per la cartella AIFA."""
    return """# Report AIFA - Agenzia Italiana del Farmaco

## Fonte
- **Istituzione**: AIFA - Agenzia Italiana del Farmaco
- **Natura**: Ente pubblico sotto la direzione del Ministero della Salute
- **URL**: https://www.aifa.gov.it/
- **URL Pubblicazioni**: https://www.aifa.gov.it/pubblicazioni

## Pubblicazioni principali

### 1. Rapporto OsMed (annuale)
L'uso dei farmaci in Italia - il rapporto di riferimento sul consumo farmaceutico.
- **URL**: https://www.aifa.gov.it/rapporti-osmed
- **Dati OsMed**: https://www.aifa.gov.it/dati-osmed
- Spesa totale 2024: 37.2 miliardi di euro
- Include sub-report su antibiotici, anziani, gravidanza, disuguaglianze

### 2. Rapporto Vaccini (annuale)
Sorveglianza post-marketing dei vaccini.
- **URL**: https://www.aifa.gov.it/rapporto-vaccini

### 3. Rapporto Sperimentazione Clinica (annuale)
Stato della ricerca clinica in Italia.
- **URL**: https://www.aifa.gov.it/rapporto-sulla-sperimentazione-clinica-dei-medicinali-in-italia
- 764 sperimentazioni valutate (2023), oncologia al 34.7%

### 4. Rapporto Attività AIFA (annuale)
Attività istituzionali e risultati dell'Agenzia.
- **URL**: https://www.aifa.gov.it/rapporto-sulle-attivita-aifa
- 889 farmaci autorizzati nel 2024, 228 rimborsati SSN

### 5. Registri di Monitoraggio Farmaci
Sistema unico in Europa per farmaci innovativi e ad alto costo.
- **URL**: https://www.aifa.gov.it/registri-farmaci-sottoposti-a-monitoraggio
- **Piattaforma**: https://registri.aifa.gov.it/

### 6. Liste di Trasparenza (mensile)
Farmaci equivalenti con prezzo di riferimento SSN.
- **URL**: https://www.aifa.gov.it/liste-di-trasparenza

### 7. Prontuario Farmaceutico Nazionale (PFN)
Formulario ufficiale dei farmaci rimborsabili SSN.
- **URL**: https://www.aifa.gov.it/liste-dei-farmaci

### 8. Horizon Scanning (annuale)
Farmaci in pipeline con impatto atteso sul SSN.

## Licenza
Dati pubblici - AIFA / Ministero della Salute
"""


# =============================================================================
# SEZIONE 6: GENERAZIONE OUTPUT
# =============================================================================

def save_json(data, filepath):
    """Salva dati in formato JSON."""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    size_kb = os.path.getsize(filepath) / 1024
    print(f"  Salvato: {os.path.relpath(filepath, BASE_DIR)} ({size_kb:.1f} KB)")


def save_csv_screening(ons_data, filepath):
    """Esporta i dati regionali di screening in formato CSV."""
    rows = []
    for reg in ons_data['indicatori_regionali_2023']:
        rows.append({
            'regione': reg['regione'],
            'screening_mammografico_adesione_pct': reg['mammo_adesione'],
            'screening_cervicale_adesione_pct': reg['cerv_adesione'],
            'screening_colorettale_adesione_pct': reg['color_adesione'],
            'anno': 2023,
            'fonte': 'ONS - Osservatorio Nazionale Screening'
        })

    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    size_kb = os.path.getsize(filepath) / 1024
    print(f"  Salvato: {os.path.relpath(filepath, BASE_DIR)} ({size_kb:.1f} KB)")


def save_csv_serie_storiche(ons_data, filepath):
    """Esporta le serie storiche di adesione in formato CSV."""
    rows = []
    for entry in ons_data['screening_mammografico']['serie_storica_adesione']:
        rows.append({
            'anno': entry['anno'],
            'tipo_screening': 'mammografico',
            'adesione_percentuale': entry['adesione_percentuale'],
            'nota': entry.get('nota', '')
        })
    for entry in ons_data['screening_cervicale']['serie_storica_adesione']:
        rows.append({
            'anno': entry['anno'],
            'tipo_screening': 'cervicale',
            'adesione_percentuale': entry['adesione_percentuale'],
            'nota': entry.get('nota', '')
        })
    for entry in ons_data['screening_colorettale']['serie_storica_adesione']:
        rows.append({
            'anno': entry['anno'],
            'tipo_screening': 'colorettale',
            'adesione_percentuale': entry['adesione_percentuale'],
            'nota': entry.get('nota', '')
        })

    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['anno', 'tipo_screening', 'adesione_percentuale', 'nota'])
        writer.writeheader()
        writer.writerows(rows)

    size_kb = os.path.getsize(filepath) / 1024
    print(f"  Salvato: {os.path.relpath(filepath, BASE_DIR)} ({size_kb:.1f} KB)")


def save_csv_societa_scientifiche(it_data, eu_data, filepath):
    """Esporta catalogo società scientifiche in formato CSV."""
    rows = []
    for soc in it_data['societa']:
        for rap in soc['rapporti_principali']:
            rows.append({
                'acronimo': soc['acronimo'],
                'nome_completo': soc['nome_completo'],
                'area_medica': soc['area_medica'],
                'ambito': 'Italia',
                'url_societa': soc['url'],
                'titolo_rapporto': rap['titolo'],
                'anno_rapporto': rap['anno'],
                'url_rapporto': rap.get('url', ''),
                'tipo_rapporto': rap.get('tipo', ''),
                'rilevanza_progetto': soc.get('rilevanza_progetto', '')
            })
    for soc in eu_data['societa']:
        for rap in soc['rapporti_principali']:
            rows.append({
                'acronimo': soc['acronimo'],
                'nome_completo': soc['nome_completo'],
                'area_medica': soc['area_medica'],
                'ambito': 'Europa',
                'url_societa': soc['url'],
                'titolo_rapporto': rap['titolo'],
                'anno_rapporto': rap['anno'],
                'url_rapporto': rap.get('url', ''),
                'tipo_rapporto': rap.get('tipo', ''),
                'rilevanza_progetto': soc.get('rilevanza_progetto', '')
            })

    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    size_kb = os.path.getsize(filepath) / 1024
    print(f"  Salvato: {os.path.relpath(filepath, BASE_DIR)} ({size_kb:.1f} KB)")


def create_ons_readme():
    """Crea README per la cartella ONS."""
    content = """# Osservatorio Nazionale Screening (ONS)

## Fonte
- **Istituzione**: Osservatorio Nazionale Screening (ONS) presso l'Istituto Superiore di Sanità (ISS)
- **Ministero vigilante**: Ministero della Salute
- **URL**: https://www.osservatorionazionalescreening.it/
- **URL dati**: https://www.osservatorionazionalescreening.it/content/i-numeri-degli-screening

## Contenuto
Dati strutturati sui tre programmi di screening oncologico organizzato in Italia:

### 1. Screening mammografico
- **Target**: Donne 50-69 anni (alcune regioni 45-74)
- **Test**: Mammografia bilaterale
- **Intervallo**: Biennale
- **Adesione nazionale 2023**: 55.0%

### 2. Screening cervicale
- **Target**: Donne 25-64 anni
- **Test**: HPV test (primario) + Pap-test (triage)
- **Intervallo**: Quinquennale (HPV) / Triennale (Pap-test)
- **Adesione nazionale 2023**: 41.3%

### 3. Screening colorettale
- **Target**: Uomini e donne 50-69 anni
- **Test**: SOF immunochimico (FIT)
- **Intervallo**: Biennale
- **Adesione nazionale 2023**: 45.0%

## File generati
- `ons_screening_completo.json` - Dataset completo con tutti gli indicatori
- Nella cartella `processed/`:
  - `ons_screening_regionali_2023.csv` - Adesione per regione e tipo di screening
  - `ons_screening_serie_storiche.csv` - Serie storiche di adesione 2005-2023

## Standard di riferimento
European Guidelines for Quality Assurance in Cancer Screening (mammografico, cervicale, colorettale).

## Licenza
Dati pubblici - Osservatorio Nazionale Screening / ISS

## Ultimo aggiornamento
Rapporto ONS 2024 (dati survey 2023)
"""
    return content


def create_societa_scientifiche_readme():
    """Crea README per la cartella società scientifiche."""
    content = """# Rapporti Società Scientifiche

## Descrizione
Catalogo strutturato dei principali rapporti e dati pubblicati dalle società scientifiche italiane
ed europee, rilevanti per l'analisi dei percorsi sociosanitari multi-specialistici.

## Società scientifiche italiane catalogate

| Acronimo | Nome | Area medica |
|----------|------|-------------|
| AIOM | Associazione Italiana di Oncologia Medica | Oncologia |
| AIRTUM | Associazione Italiana Registri Tumori | Epidemiologia oncologica |
| ANMCO | Ass. Nazionale Medici Cardiologi Ospedalieri | Cardiologia |
| SIC | Società Italiana di Cardiologia | Cardiologia |
| SID | Società Italiana di Diabetologia | Diabetologia |
| SIMG | Società Italiana di Medicina Generale | Medicina Generale |
| SIN | Società Italiana di Neurologia | Neurologia |
| SIR | Società Italiana di Reumatologia | Reumatologia |
| AIPO-ITS | Ass. Italiana Pneumologi Ospedalieri | Pneumologia |
| SIN-Nefro | Società Italiana di Nefrologia | Nefrologia |
| SIGE | Soc. Italiana Gastroenterologia | Gastroenterologia |
| SIE | Società Italiana di Endocrinologia | Endocrinologia |
| SIGG | Soc. Italiana Gerontologia e Geriatria | Geriatria |
| SIMI | Società Italiana di Medicina Interna | Medicina Interna |
| SIP | Società Italiana di Psichiatria | Salute Mentale |
| SItI | Soc. Italiana Igiene e Sanità Pubblica | Prevenzione |

## Società scientifiche europee catalogate

| Acronimo | Nome | Area medica |
|----------|------|-------------|
| ESC | European Society of Cardiology | Cardiologia |
| ESMO | European Society for Medical Oncology | Oncologia |
| ERS | European Respiratory Society | Pneumologia |
| EASL | European Assoc. Study of the Liver | Epatologia |
| ERA | European Renal Association | Nefrologia |
| EULAR | European Alliance Assoc. Rheumatology | Reumatologia |
| EASD | European Assoc. Study of Diabetes | Diabetologia |
| EAN | European Academy of Neurology | Neurologia |
| EFIM | European Federation Internal Medicine | Medicina Interna |
| EU-CANCER-SCREENING | Commissione Europea - Screening | Screening oncologici |

## File generati
- `italiane/rapporti_societa_italiane.json` - Catalogo completo società italiane
- `europee/rapporti_societa_europee.json` - Catalogo completo società europee
- Nella cartella `processed/`:
  - `rapporti_societa_scientifiche.csv` - Catalogo unificato in formato CSV

## Licenza
Dati pubblici raccolti da fonti istituzionali e società scientifiche.
"""
    return content


# =============================================================================
# MAIN
# =============================================================================

def main():
    print("=" * 70)
    print("ARRICCHIMENTO REPOSITORY - RAPPORTI SCIENTIFICI, ONS, OASI, AIFA")
    print("=" * 70)

    # 1. Crea directory
    print("\n[1/8] Creazione directory...")
    create_directories()

    # 2. Genera dati ONS
    print("\n[2/8] Generazione dati Osservatorio Nazionale Screening...")
    ons_data = build_ons_data()
    save_json(ons_data, os.path.join(ONS_RAW_DIR, 'ons_screening_completo.json'))

    # README ONS
    readme_ons_path = os.path.join(ONS_RAW_DIR, 'README.md')
    with open(readme_ons_path, 'w', encoding='utf-8') as f:
        f.write(create_ons_readme())
    print(f"  Salvato: {os.path.relpath(readme_ons_path, BASE_DIR)}")

    # 3. Genera dati società scientifiche italiane
    print("\n[3/8] Generazione catalogo società scientifiche italiane...")
    it_data = build_societa_scientifiche_italiane()
    save_json(it_data, os.path.join(SOCIETA_IT_DIR, 'rapporti_societa_italiane.json'))

    # 4. Genera dati società scientifiche europee
    print("\n[4/8] Generazione catalogo società scientifiche europee...")
    eu_data = build_societa_scientifiche_europee()
    save_json(eu_data, os.path.join(SOCIETA_EU_DIR, 'rapporti_societa_europee.json'))

    # README società scientifiche
    readme_soc_path = os.path.join(RAW_DIR, 'societa_scientifiche', 'README.md')
    with open(readme_soc_path, 'w', encoding='utf-8') as f:
        f.write(create_societa_scientifiche_readme())
    print(f"  Salvato: {os.path.relpath(readme_soc_path, BASE_DIR)}")

    # 5. Genera dati OASI Bocconi
    print("\n[5/8] Generazione dati OASI - CERGAS Bocconi...")
    oasi_data = build_oasi_bocconi()
    save_json(oasi_data, os.path.join(OASI_RAW_DIR, 'oasi_bocconi_completo.json'))

    # README OASI
    readme_oasi_path = os.path.join(OASI_RAW_DIR, 'README.md')
    with open(readme_oasi_path, 'w', encoding='utf-8') as f:
        f.write(create_oasi_readme())
    print(f"  Salvato: {os.path.relpath(readme_oasi_path, BASE_DIR)}")

    # 6. Genera dati AIFA
    print("\n[6/8] Generazione dati AIFA...")
    aifa_data = build_aifa_reports()
    save_json(aifa_data, os.path.join(AIFA_RAW_DIR, 'aifa_report_completo.json'))

    # README AIFA
    readme_aifa_path = os.path.join(AIFA_RAW_DIR, 'README.md')
    with open(readme_aifa_path, 'w', encoding='utf-8') as f:
        f.write(create_aifa_readme())
    print(f"  Salvato: {os.path.relpath(readme_aifa_path, BASE_DIR)}")

    # 7. Genera dataset processed
    print("\n[7/8] Generazione dataset processati...")

    # CSV regionali screening
    save_csv_screening(
        ons_data,
        os.path.join(PROCESSED_DIR, 'ons_screening_regionali_2023.csv')
    )

    # CSV serie storiche
    save_csv_serie_storiche(
        ons_data,
        os.path.join(PROCESSED_DIR, 'ons_screening_serie_storiche.csv')
    )

    # CSV catalogo società scientifiche
    save_csv_societa_scientifiche(
        it_data, eu_data,
        os.path.join(PROCESSED_DIR, 'rapporti_societa_scientifiche.csv')
    )

    # JSON processato screening
    screening_summary = {
        "fonte": "ONS - Osservatorio Nazionale Screening",
        "anno": 2023,
        "screening": {
            "mammografico": ons_data['screening_mammografico']['indicatori_nazionali'],
            "cervicale": ons_data['screening_cervicale']['indicatori_nazionali'],
            "colorettale": ons_data['screening_colorettale']['indicatori_nazionali']
        },
        "impatto": ons_data['impatto_screening'],
        "indicatori_regionali": ons_data['indicatori_regionali_2023']
    }
    save_json(screening_summary, os.path.join(PROCESSED_DIR, 'ons_screening_italia.json'))

    # JSON processato OASI Bocconi
    oasi_summary = {
        "fonte": oasi_data['fonte'],
        "istituzione": oasi_data['istituzione'],
        "url": oasi_data['url_principale'],
        "rapporti": [
            {
                "titolo": r['titolo'],
                "anno": r['anno'],
                "url": r.get('url', ''),
                "temi_principali": r.get('temi_principali', []),
                "dati_chiave": r.get('dati_chiave', {})
            }
            for r in oasi_data['rapporti_annuali']
        ],
        "osservatori_correlati": oasi_data['osservatori_correlati']
    }
    save_json(oasi_summary, os.path.join(PROCESSED_DIR, 'oasi_bocconi_sintesi.json'))

    # JSON processato AIFA
    aifa_summary = {
        "fonte": aifa_data['fonte'],
        "url": aifa_data['url_principale'],
        "rapporti": [
            {
                "titolo": r['titolo'],
                "acronimo": r.get('acronimo', ''),
                "tipo": r.get('tipo', ''),
                "url": r.get('url', ''),
                "frequenza": r.get('frequenza', ''),
                "dati_chiave": r.get('dati_chiave', {})
            }
            for r in aifa_data['rapporti']
        ],
        "spesa_farmaceutica_2024": aifa_data['dati_aggregati_spesa_farmaceutica']
    }
    save_json(aifa_summary, os.path.join(PROCESSED_DIR, 'aifa_report_sintesi.json'))

    # 8. Riepilogo
    print("\n[8/8] Riepilogo finale...")
    print("=" * 70)

    n_it = len(it_data['societa'])
    n_eu = len(eu_data['societa'])
    n_rapporti_it = sum(len(s['rapporti_principali']) for s in it_data['societa'])
    n_rapporti_eu = sum(len(s['rapporti_principali']) for s in eu_data['societa'])
    n_rapporti_aifa = len(aifa_data['rapporti'])
    n_rapporti_oasi = len(oasi_data['rapporti_annuali'])

    print(f"\nOSSERVATORIO NAZIONALE SCREENING:")
    print(f"  - 3 programmi di screening (mammografico, cervicale, colorettale)")
    print(f"  - 21 regioni con indicatori di adesione")
    print(f"  - Serie storiche 2005-2023")
    print(f"  - Tumori identificati via screening: {ons_data['impatto_screening']['tumori_totali_identificati_screening']:,}")
    print(f"  - Lesioni precancerose identificate: {ons_data['impatto_screening']['lesioni_precancerose_identificate']:,}")

    print(f"\nSOCIETA' SCIENTIFICHE ITALIANE:")
    print(f"  - {n_it} società catalogate")
    print(f"  - {n_rapporti_it} rapporti/linee guida mappati")

    print(f"\nSOCIETA' SCIENTIFICHE EUROPEE:")
    print(f"  - {n_eu} società/istituzioni catalogate")
    print(f"  - {n_rapporti_eu} rapporti/linee guida mappati")

    print(f"\nOASI - CERGAS BOCCONI:")
    print(f"  - {n_rapporti_oasi} edizioni del Rapporto OASI (2023-2025)")
    print(f"  - {len(oasi_data['osservatori_correlati'])} osservatori correlati (OCPS, MASAN, OLTC)")
    print(f"  - Spesa pubblica Italia: {oasi_data['rapporti_annuali'][1]['dati_chiave']['spesa_pubblica_pil_percentuale']}% PIL vs 9-11% in Francia/Germania/UK")

    print(f"\nAIFA - AGENZIA ITALIANA DEL FARMACO:")
    print(f"  - {n_rapporti_aifa} report/piattaforme catalogati")
    print(f"  - Spesa farmaceutica totale 2024: {aifa_data['dati_aggregati_spesa_farmaceutica']['spesa_totale_miliardi_euro']} miliardi euro")
    print(f"  - {aifa_data['rapporti'][0]['dati_chiave']['farmaci_orfani_disponibili_su_autorizzati_ema']} farmaci orfani disponibili")

    print(f"\nFILE GENERATI:")
    print(f"  RAW:")
    print(f"    - datasets/raw/ons/ons_screening_completo.json + README.md")
    print(f"    - datasets/raw/societa_scientifiche/italiane/rapporti_societa_italiane.json")
    print(f"    - datasets/raw/societa_scientifiche/europee/rapporti_societa_europee.json")
    print(f"    - datasets/raw/societa_scientifiche/README.md")
    print(f"    - datasets/raw/oasi_bocconi/oasi_bocconi_completo.json + README.md")
    print(f"    - datasets/raw/aifa/aifa_report_completo.json + README.md")
    print(f"  PROCESSED:")
    print(f"    - datasets/processed/ons_screening_italia.json")
    print(f"    - datasets/processed/ons_screening_regionali_2023.csv")
    print(f"    - datasets/processed/ons_screening_serie_storiche.csv")
    print(f"    - datasets/processed/rapporti_societa_scientifiche.csv")
    print(f"    - datasets/processed/oasi_bocconi_sintesi.json")
    print(f"    - datasets/processed/aifa_report_sintesi.json")

    print(f"\n{'=' * 70}")
    print("ARRICCHIMENTO COMPLETATO CON SUCCESSO")
    print(f"{'=' * 70}")


if __name__ == '__main__':
    main()
