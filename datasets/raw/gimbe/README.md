# Report Fondazione GIMBE - Catalogo Completo

## Fonte
- **Istituzione**: Fondazione GIMBE (Gruppo Italiano per la Medicina Basata sulle Evidenze)
- **Presidente**: Nino Cartabellotta
- **Anno fondazione**: 1996
- **URL Principale**: https://www.gimbe.org/
- **Campagna #SalviamoSSN**: https://salviamo-ssn.it/

## Pubblicazioni principali

### 1. Rapporto GIMBE sul SSN (annuale, dal 2016)
8 edizioni (2016-2025), presentate al Parlamento italiano ogni ottobre.
- 1° (2016), 2° (2017), 3° (2018), 4° (2019): Focus sostenibilità
- 5° (2022), 6° (2023), 7° (2024), 8° (2025): Focus crisi del SSN
- **8° Rapporto (2025)**: "La lenta agonia del SSN" - gap pro-capite 727€ vs OCSE

### 2. Report Osservatorio GIMBE (~4/anno)
Report tematici numerati per anno (es. 1/2025, 2/2025).
Temi: mobilità sanitaria, spesa privata, autonomia differenziata, scuole e salute.
- URL: https://www.gimbe.org/pagine/290/it/report-osservatorio-gimbe

### 3. Monitoraggio COVID-19 (2020-2024)
Oltre 200 report settimanali, monitoraggio vaccinale, advocacy trasparenza.
- URL: https://coronavirus.gimbe.org/

### 4. Analisi tematiche ricorrenti
- **Liste di attesa**: monitoraggio DL 73/2024 e piattaforma PNLA
- **Mobilità sanitaria**: record 5.15 mld€ nel 2023
- **Forza lavoro**: 93.000 medici fuori dal SSN, crisi infermieristica
- **PNRR M6**: solo 12.7% Case della Comunità attive con servizi
- **Sanità digitale/FSE**: solo 42% cittadini con consenso FSE
- **Sprechi**: 21.59 mld€ (19% della spesa) - tassonomia a 6 categorie
- **Autonomia differenziata**: rischi per equità sanitaria

### 5. Altre pubblicazioni
- **Evidence** (rivista open access): https://www.evidence.it/
- **Carta GIMBE**: documento programmatico per la tutela della salute
- **Conferenza Nazionale GIMBE**: 16 edizioni (2006-2023)
- **GIMBE Education**: corsi ECM su EBP, clinical governance

## File nel repository

### Rapporti annuali sul SSN — `pdf/`
Scaricati automaticamente dalla pipeline `scripts/run_daily_enrichment.py --only gimbe`.

| Edizione | Anno | File | Fonte |
|----------|------|------|-------|
| 1° | 2016 | `pdf/1_Rapporto_GIMBE_Sostenibilita_SSN_2016-2025.pdf` | salviamo-ssn.it |
| 2° | 2017 | _non disponibile come PDF integrale_ — vedi nota sotto | salviamo-ssn.it |
| 3° | 2018 | `pdf/3_Rapporto_GIMBE.pdf` | salviamo-ssn.it |
| 4° | 2019 | `pdf/4_Rapporto_GIMBE_Sostenibilita_SSN.pdf` | salviamo-ssn.it |
| 5° | 2022 | `pdf/5_Rapporto_GIMBE_SSN.pdf` | salviamo-ssn.it |
| 6° | 2023 | `pdf/6_Rapporto_GIMBE_SSN.pdf` | salviamo-ssn.it |
| 7° | 2024 | `pdf/7_Rapporto_GIMBE_SSN.pdf` | salviamo-ssn.it |
| 8° | 2025 | `pdf/8_Rapporto_GIMBE_SSN_2025.pdf` | salviamo-ssn.it |
| (latest) | n.d. | `pdf/rapporto_gimbe_ssn_latest.pdf` | resolver dinamico |

> **Nota sul 2° Rapporto GIMBE (2017):** la Fondazione GIMBE pubblica questa
> edizione esclusivamente in capitoli separati (Introduzione, Capitolo 1,
> Capitolo 2, …) sul portale salviamo-ssn.it. Non esiste un PDF integrale
> ufficiale. Per coerenza con il principio "solo documenti originali completi"
> della repository, le singole sezioni non sono state incluse nella pipeline.
> Pagina ufficiale: https://www.salviamo-ssn.it/attivita/rapporto/2-rapporto-gimbe.it-IT.html

### Report Osservatorio GIMBE — `osservatorio/`

| ID | Anno | Titolo | File |
|----|------|--------|------|
| 4/2019 | 2019 | Liste d'attesa | `osservatorio/Report_Osservatorio_GIMBE_2019.04_Liste_attesa.pdf` |
| 6/2019 | 2019 | Mobilità sanitaria 2017 | `osservatorio/Report_Osservatorio_GIMBE_2019.06_Mobilita_sanitaria_2017.pdf` |
| 7/2019 | 2019 | Definanziamento SSN | `osservatorio/Report_Osservatorio_GIMBE_2019.07_Definanziamento_SSN.pdf` |
| 1/2020 | 2020 | Ticket 2019 | `osservatorio/Report_Osservatorio_GIMBE_2020.01_Ticket_2019.pdf` |
| 2/2020 | 2020 | Mobilità sanitaria 2018 | `osservatorio/Report_Osservatorio_GIMBE_2020.02_Mobilita_sanitaria_2018.pdf` |
| 1/2021 | 2021 | Impatto COVID-19 prestazioni | `osservatorio/Report_Osservatorio_GIMBE_2021.01_Impatto_COVID_19_prestazioni_sanitarie.pdf` |
| 2/2021 | 2021 | Sicurezza COVID-19 scuole | `osservatorio/Report_Osservatorio_GIMBE_2021.02_Sicurezza_COVID_19_scuole.pdf` |
| 3/2021 | 2021 | Vaccinazione antinfluenzale | `osservatorio/Report_Osservatorio_GIMBE_2021.03_Vaccinazione_antinfluenzale_in_Italia.pdf` |
| 1/2022 | 2022 | Programmi elettorali 2022 | `osservatorio/Report_Osservatorio_GIMBE_2022.01_Monitoraggio_programmi_elettorali_2022.pdf` |
| 2/2022 | 2022 | Adempimenti LEA 2010-2019 | `osservatorio/Report_Osservatorio_GIMBE_2022.02_Adempimenti_LEA_2010-2019.pdf` |
| 3/2022 | 2022 | Isterectomie fibromi uterini | `osservatorio/Report_Osservatorio_GIMBE_2022.03_Isterectomie_fibromi_uterini.pdf` |
| 1/2023 | 2023 | Regionalismo differenziato | `osservatorio/Report_Osservatorio_GIMBE_2023.01_Regionalismo_differenziato_in_sanita.pdf` |
| 2/2023 | 2023 | Mobilità sanitaria 2020 | `osservatorio/Report_Osservatorio_GIMBE_2023.02_Mobilita_sanitaria_2020.pdf` |
| 4/2023 | 2023 | Filiera healthcare nel SSN | `osservatorio/Report_Osservatorio_GIMBE_2023.04_Ruolo_filiera_healthcare_nel_SSN.pdf` |
| 1/2024 | 2024 | Mobilità sanitaria 2021 | `osservatorio/Report_Osservatorio_GIMBE_2024.01_Mobilita_sanitaria_2021.pdf` |
| 2/2024 | 2024 | Autonomia differenziata | `osservatorio/Report_Osservatorio_GIMBE_2024.02_Autonomia_differenziata_in_sanita.pdf` |
| 3/2024 | 2024 | Scuole che Promuovono Salute | `osservatorio/Report_Osservatorio_GIMBE_2024.03_Scuole_che_promuovono_salute.pdf` |
| 1/2025 | 2025 | Mobilità sanitaria 2022 | `osservatorio/Report_Osservatorio_GIMBE_2025.01_Mobilita_sanitaria_2022.pdf` |
| 2/2025 | 2025 | Spesa sanitaria privata 2023 | `osservatorio/Report_Osservatorio_GIMBE_2025.02_Spesa_sanitaria_privata_2023.pdf` |
| 1/2026 | 2026 | Mobilità sanitaria 2023 | `osservatorio/Report_Osservatorio_GIMBE_2026.01_Mobilita_sanitaria_2023.pdf` |
| 2026 | 2026 | Endometriosi (diseguaglianze regionali) | `osservatorio/Report_Osservatorio_GIMBE_2026_Endometriosi.pdf` |
| latest | dinamico | Ultimo Report Osservatorio pubblicato | `osservatorio/report_osservatorio_gimbe_latest.pdf` |

### Estratto strutturato
- `gimbe_report_completo.json` — dataset JSON con sintesi e dati chiave (rigenerato da `enrich_scientific_reports_ons.py`)

## Aggiornamento

```bash
python3 scripts/run_daily_enrichment.py --only gimbe
```

## Licenza
Dati pubblici - Fondazione GIMBE / CC-BY-NC-ND
