#!/usr/bin/env python3
"""
Download script for publicly available PDTA (Percorsi Diagnostico-Terapeutici Assistenziali)
documents from Italian national, regional and local healthcare authorities.

Usage:
    python scripts/download_pdta.py [--dry-run] [--level nazionale|regionale|all] [--region REGION]

This script downloads PDF documents from verified public URLs to the appropriate
folder in datasets/raw/pdta/.
"""

import argparse
import json
import os
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path

# Base directory for PDTA downloads
BASE_DIR = Path(__file__).parent.parent / "datasets" / "raw" / "pdta"

# Verified publicly available PDTA PDF URLs organized by level and region
PDTA_DOWNLOADS = {
    "nazionale": {
        "agenas": [
            {
                "id": "NAZ_AGENAS_003",
                "filename": "PPDTA_BPCO_adulto_2026.pdf",
                "url": "https://www.agenas.gov.it/images/2026/hta/PPDTA_BPCO_adulto.pdf",
                "title": "PPDTA BPCO nell'adulto",
                "year": 2026
            },
            {
                "id": "NAZ_AGENAS_001",
                "filename": "PPDTA_Diabete_Mellito_adulto_2026.pdf",
                "url": "https://www.agenas.gov.it/images/2026/hta/PPDTA_Diabete_Mellito_adulto.pdf",
                "title": "PPDTA Diabete Mellito nell'adulto",
                "year": 2026
            },
            {
                "id": "NAZ_AGENAS_002",
                "filename": "PPDTA_Asma_Grave_adulto_2026.pdf",
                "url": "https://www.agenas.gov.it/images/2026/hta/PPDTA_Asma_Grave_adulto.pdf",
                "title": "PPDTA Asma Grave nell'adulto",
                "year": 2026
            },
        ],
        "ministero_salute": [
            {
                "id": "NAZ_MIN_001",
                "filename": "Piano_Nazionale_Cronicita_2016.pdf",
                "url": "https://www.salute.gov.it/imgs/C_17_pubblicazioni_2584_allegato.pdf",
                "title": "Piano Nazionale della Cronicita",
                "year": 2016
            },
            {
                "id": "NAZ_MIN_002",
                "filename": "Piano_Nazionale_Cronicita_aggiornamento_2024.pdf",
                "url": "https://www.quotidianosanita.it/allegati/allegato1737108617.pdf",
                "title": "Piano Nazionale della Cronicita - Aggiornamento 2024",
                "year": 2024
            },
        ],
        "iss": [
            {
                "id": "NAZ_ISS_001",
                "filename": "Linee_indirizzo_PDTA_Demenze_2021.pdf",
                "url": "https://www.iss.it/documents/20126/5783571/Testo+Linee+di+indirizzo+Nazionali+sui+Percorsi+Diagnostico+Terapeutici+Assistenziali+(PDTA)+per+le+demenze.pdf/d5123f6a-2161-6c42-5377-8796cce29fe0?t=1626170681347",
                "title": "Linee di indirizzo Nazionali PDTA per le Demenze",
                "year": 2021
            },
            {
                "id": "NAZ_ISS_002",
                "filename": "Manuale_metodologico_SNLG_2023.pdf",
                "url": "https://www.aiom.it/wp-content/uploads/2023/04/2023_ISS_SNLG_Manuale_Metodologico_v1.3.3.pdf",
                "title": "Manuale metodologico ISS/SNLG",
                "year": 2023
            },
        ],
        "societa_scientifiche": [
            {
                "id": "NAZ_CSR_001",
                "filename": "PDTA_MICI_Accordo_Stato_Regioni_2015.pdf",
                "url": "https://www.fnopi.it/archivio_news/attualita/1586/ACCORDO%20MICI.pdf",
                "title": "PDTA Malattie Infiammatorie Croniche Intestinali (MICI)",
                "year": 2015
            },
            {
                "id": "NAZ_CSR_002",
                "filename": "PDTA_Malattie_Reumatiche_2015.pdf",
                "url": "https://www.sifoweb.it/images/pdf/attivita/attivita-scientifica/aree_scientifiche/Contin_assistenziale_H-T/documenti/PDTA_nelle_Malattie_REUMATICHE_INFIAMMATORIE_E_AUTOIMMUNI.pdf",
                "title": "PDTA Malattie Reumatiche Infiammatorie e Autoimmuni",
                "year": 2015
            },
            {
                "id": "NAZ_CSR_004",
                "filename": "Piano_Nazionale_Malattie_Rare_2023_2026.pdf",
                "url": "https://www.malattierare.gov.it/normativa/download/792/PIANONAZIONALEMALATTIERARE2023(1).pdf",
                "title": "Piano Nazionale Malattie Rare 2023-2026",
                "year": 2023
            },
            {
                "id": "NAZ_AIOM_002",
                "filename": "AIOM_Ruolo_Oncologo_PDTA_2024.pdf",
                "url": "https://www.aiom.it/wp-content/uploads/2024/11/2024_AIOM_RUOLO-COMPETENZE-ONCOLOGO-PDTA.pdf",
                "title": "Ruolo e competenze dell'oncologo nei PDTA (AIOM)",
                "year": 2024
            },
            {
                "id": "NAZ_AMD_001",
                "filename": "PDTA_Diabete_tipo1_AMD_SID_2019.pdf",
                "url": "https://aemmedi.it/wp-content/uploads/2019/03/PDTA-Diabete-tipo-1.pdf",
                "title": "PDTA Diabete tipo 1 (AMD/SID/SIEDP)",
                "year": 2019
            },
            {
                "id": "NAZ_SID_001",
                "filename": "LG_Terapia_Diabete_tipo2_SID_AMD_2022.pdf",
                "url": "https://www.siditalia.it/pdf/LG_379_diabete_ed2022_feb2023.pdf",
                "title": "Linea Guida terapia diabete tipo 2 (SID/AMD)",
                "year": 2022
            },
            {
                "id": "NAZ_SID_002",
                "filename": "LG_Terapia_Diabete_tipo1_SID_AMD_2024.pdf",
                "url": "https://www.siditalia.it/pdf/LG-196-La-terapia-del-diabete-di-tipo-1-Ed-2024.pdf",
                "title": "Linea Guida terapia diabete tipo 1 (SID/AMD, Ed. 2024)",
                "year": 2024
            },
        ],
    },
    "regionale": {
        "lombardia": [
            {
                "id": "LOM_001",
                "filename": "PDTA_Tumore_Mammella_DGR_7755_2022.pdf",
                "url": "https://www.regione.lombardia.it/wps/wcm/connect/a7b9a031-49c4-419e-8619-07c50454975c/DGR+7755+del+28+dicembre+2022.pdf?MOD=AJPERES&CACHEID=ROOTWORKSPACE-a7b9a031-49c4-419e-8619-07c50454975c-oL9289Q",
                "title": "PDTA-R Tumore della Mammella",
                "year": 2022
            },
            {
                "id": "LOM_002",
                "filename": "PDTA_Demenze_DGR_1553_2023.pdf",
                "url": "https://www.demenze.it/documenti/geo_regioni/dgr_1553_18_12_2023.pdf",
                "title": "PDTA-R Disturbi Cognitivi e Demenze",
                "year": 2023
            },
        ],
        "veneto": [
            {
                "id": "VEN_001",
                "filename": "Guida_operativa_PPDTA_regionali_DGR_239_2025.pdf",
                "url": "https://bur.regione.veneto.it/BurvServices/pubblica/Download.aspx?name=Dgr_239_25_AllegatoB_553867.pdf&type=9&storico=False",
                "title": "Guida operativa per lo sviluppo dei PPDTA regionali",
                "year": 2025
            },
            {
                "id": "VEN_003",
                "filename": "PDTA_Demenze_Veneto_2019.pdf",
                "url": "https://www.aulss8.veneto.it/wp-content/uploads/2023/04/9328-PDTA_demenza_regione_Veneto_2019.pdf",
                "title": "PDTA Demenze Regione Veneto",
                "year": 2019
            },
        ],
        "piemonte": [
            {
                "id": "PIE_001",
                "filename": "DGR_6377_CAS_GIC_PSDTA_2022.pdf",
                "url": "https://www.regione.piemonte.it/governo/bollettino/abbonati/2023/03/attach/dgr_06377_1050_28122022.pdf",
                "title": "Regolamento CAS, GIC e PSDTA Rete Oncologica",
                "year": 2022
            },
            {
                "id": "PIE_002",
                "filename": "PDTA_Tumori_Pancreas.pdf",
                "url": "https://reteoncologica.it/wp-content/uploads/images/stories/Linee_guida_raccomandazioni_RETE/Rari_e_Sarcomi/RACC_DEF_PDTA_PANCREAS.pdf",
                "title": "PDTA Tumori del Pancreas",
                "year": None
            },
            {
                "id": "PIE_ASL_001",
                "filename": "PDTA_Mieloma_ASL_TO4_2025.pdf",
                "url": "https://www.aslto4.piemonte.it/sites/default/files/2025-02/PDTA%20Mieloma.pdf",
                "title": "PDTA Mieloma - ASL TO4",
                "year": 2025
            },
        ],
        "emilia_romagna": [
            {
                "id": "EMR_001",
                "filename": "Guida_costruzione_PDTA_ASSR_2013.pdf",
                "url": "https://assr.regione.emilia-romagna.it/pubblicazioni/rapporti-documenti/guida-valutatori-PDTA-2013/@@download/publicationFile/Linee%20Guida%20PDTA.pdf",
                "title": "Guida regionale alla costruzione dei PDTA",
                "year": 2013
            },
        ],
        "lazio": [
            {
                "id": "LAZ_002",
                "filename": "PDTA_endocrinologici_G07058_2023.pdf",
                "url": "https://www.regione.lazio.it/sites/default/files/documentazione/2024/PDTA_G07058_2023.pdf",
                "title": "PDTA Endocrinologici (obesita, tiroide, surrene, NET, paratiroidi)",
                "year": 2023
            },
            {
                "id": "LAZ_006",
                "filename": "PDTA_Demenze_Lazio_2023.pdf",
                "url": "https://www.demenze.it/documenti/geo_regioni/det_g01705_2023_pdta_demenze_regione_lazio_burl.pdf",
                "title": "PDTA Demenze - Regione Lazio",
                "year": 2023
            },
            {
                "id": "LAZ_ASL_001",
                "filename": "PDTA_Demenze_ASL_Roma1_2024.pdf",
                "url": "https://www.aslroma1.it/uploads/files/51_39_delibera_n._1705_CS_del_30.12.2024_-_PDTA_Demenze.pdf",
                "title": "PDTA Demenze - ASL Roma 1 (declinazione aziendale)",
                "year": 2024
            },
            {
                "id": "LAZ_ASL_002",
                "filename": "PDTA_Scompenso_Cardiaco_ASL_Latina.pdf",
                "url": "https://www.ausl.latina.it/attachments/article/2092/PDTA%20Scompenso%20Cardiaco%20def.pdf",
                "title": "PDTA Scompenso Cardiaco - ASL Latina",
                "year": None
            },
            {
                "id": "LAZ_ASL_003",
                "filename": "PDTA_Diabete_Mellito_ASL_Latina.pdf",
                "url": "https://www.ausl.latina.it/attachments/article/2092/Aggiornamento%20PDTA%20per%20la%20gestione%20del%20paziente%20con%20Diabete%20mellito%20e%20Rete%20diabetologica.pdf",
                "title": "PDTA Diabete Mellito - ASL Latina",
                "year": None
            },
            {
                "id": "LAZ_ASL_004",
                "filename": "PDTA_Diabete_Mellito_Adulto_ASL_Frosinone.pdf",
                "url": "https://www.asl.fr.it/wp-content/uploads/PDTA-Diabete-Mellito-adulto.pdf",
                "title": "PDTA Diabete Mellito Adulto - ASL Frosinone",
                "year": None
            },
            {
                "id": "LAZ_REG_001",
                "filename": "DCA_U00474_2015_Presa_Carico_Paziente_Cronico_Lazio.pdf",
                "url": "https://www.regione.lazio.it/sites/default/files/decreti-commissario-ad-acta/SAN_DCA_U00474_7_ottobre_2015_Linee_di_indirizzo_per_la_gestione_a_livello_territoriale_della_presa_in_carico_del_paziente_cronico_e_relativo_percorso_attuativo.pdf",
                "title": "Linee di indirizzo presa in carico paziente cronico - Lazio",
                "year": 2015
            },
        ],
        "campania": [
            {
                "id": "CAM_001",
                "filename": "Decreto_approvazione_PDTA_oncologici_2024.pdf",
                "url": "https://www.reteoncologicacampana.it/wp-content/uploads/2025/02/Decreto-18_2025-approvazione-PDTA-2024.pdf",
                "title": "Decreto approvazione PDTA oncologici ROC 2024",
                "year": 2024
            },
            {
                "id": "CAM_002",
                "filename": "PDTA_Mammella_ROC_6ed_2024.pdf",
                "url": "https://www.reteoncologicacampana.it/wp-content/uploads/2025/01/PDTA-Mammella.pdf",
                "title": "PDTA Tumore della Mammella (6a edizione ROC)",
                "year": 2024
            },
            {
                "id": "CAM_003",
                "filename": "PDTA_Ovaio_2024.pdf",
                "url": "https://www.regione.campania.it/assets/documents/04-pdta-ovaio-2024.pdf",
                "title": "PDTA Tumore dell'Ovaio",
                "year": 2024
            },
            {
                "id": "CAM_004",
                "filename": "PDTA_Sclerosi_Multipla_2024.pdf",
                "url": "https://www.regione.campania.it/assets/documents/pdta-sclerosi-multipla-2024.pdf",
                "title": "PDTA Sclerosi Multipla",
                "year": 2024
            },
            {
                "id": "CAM_005",
                "filename": "PDTA_Lesioni_Cutanee_2024.pdf",
                "url": "https://www.regione.campania.it/assets/documents/pdta-lesioni-cutanee-2024.pdf",
                "title": "PDTA Lesioni Cutanee / Piede Diabetico",
                "year": 2024
            },
            {
                "id": "CAM_POL_001",
                "filename": "PDTA_Polmone_ROC_2023.pdf",
                "url": "https://www.reteoncologicacampana.it/wp-content/uploads/2025/01/PDTA-Polmone.pdf",
                "title": "PDTA Tumore del Polmone - Campania ROC",
                "year": 2023
            },
            {
                "id": "CAM_PRO_001",
                "filename": "PDTA_Prostata_2024.pdf",
                "url": "https://www.regione.campania.it/assets/documents/09-pdta-prostata-2024.pdf",
                "title": "PDTA Tumore della Prostata - Campania",
                "year": 2024
            },
            {
                "id": "CAM_MEL_001",
                "filename": "PDTA_Melanoma_ROC_2023.pdf",
                "url": "https://www.reteoncologicacampana.it/wp-content/uploads/2023/10/PDTA-MELANOMA-2023.pdf",
                "title": "PDTA Melanoma - Campania ROC",
                "year": 2023
            },
            {
                "id": "CAM_MES_001",
                "filename": "PDTA_Mesotelioma_2023.pdf",
                "url": "https://www.regione.campania.it/assets/documents/23-pdta-mesotelioma-2023.pdf",
                "title": "PDTA Mesotelioma - Campania",
                "year": 2023
            },
            {
                "id": "CAM_HIV_001",
                "filename": "PDTA_HIV_AIDS_Campania_2018.pdf",
                "url": "https://www.regione.campania.it/assets/documents/percorso-diagnostico-terapeutico-assistenziale-2018.pdf",
                "title": "PDTA HIV/AIDS - Campania",
                "year": 2018
            },
        ],
        "toscana": [
            {
                "id": "TOS_DIA_001",
                "filename": "PDTA_Diabete_Adulto_Toscana_2019.pdf",
                "url": "https://www.regione.toscana.it/documents/10180/23793180/ALL+A+23-2019+PDTA-Diabete.pdf/f1e8ea87-145f-08c4-6c3d-16b69f5f43c2?t=1578658143393",
                "title": "PDTA Diabete nell'Adulto - Toscana",
                "year": 2019
            },
            {
                "id": "TOS_MAM_001",
                "filename": "PDTA_Tumore_Mammella_Toscana_2024.pdf",
                "url": "https://www.ispro.toscana.it/sites/default/files/ReteOncologica/Allegato%20Decreto%208098_2024.pdf",
                "title": "PDTA Tumore della Mammella - Toscana (rev. 2024)",
                "year": 2024
            },
            {
                "id": "TOS_MIO_001",
                "filename": "PDTA_Medicina_Integrata_Oncologia_Toscana_2021.pdf",
                "url": "https://www.ispro.toscana.it/sites/default/files/ReteOncologica/Decreto_n.19664_del_11-11-2021-Allegato-A.pdf",
                "title": "PDTA Medicina Integrata in Oncologia - Toscana",
                "year": 2021
            },
        ],
        "friuli_venezia_giulia": [
            {
                "id": "FVG_001",
                "filename": "Piano_Rete_Oncologica_FVG_2025_2027.pdf",
                "url": "https://arcs.sanita.fvg.it/media/uploads/2025/07/15/piano-della-rete-oncologica-regionale-fvg-2025-2027.pdf",
                "title": "Piano Rete Oncologica Regionale FVG 2025-2027",
                "year": 2025
            },
            {
                "id": "FVG_003",
                "filename": "Linee_annuali_SSR_FVG_2024.pdf",
                "url": "http://mtom.regione.fvg.it/storage//2023_2117/Allegato%201%20alla%20Delibera%202117-2023.pdf",
                "title": "Linee annuali gestione SSR FVG 2024",
                "year": 2024
            },
        ],
        "abruzzo": [
            {
                "id": "ABR_MAM_001",
                "filename": "PDTA_Tumore_Mammella_Abruzzo_DGR340_2017.pdf",
                "url": "https://lnx.asl2abruzzo.it/formazione/attachments/article/517/Pacchetto%20PDTA%20della%20mammella1.5-1%20da%20inserire.pdf",
                "title": "PDTA Tumore della Mammella - Abruzzo",
                "year": 2017
            },
            {
                "id": "ABR_COL_001",
                "filename": "PDTA_Tumore_Colon_Retto_ASL2_Abruzzo.pdf",
                "url": "https://lnx.asl2abruzzo.it/formazione/attachments/article/288/PDTAOK-PACCHETTO%20+ALLEGATI.pdf",
                "title": "PDTA Tumore Colon-Retto - ASL 2 Abruzzo",
                "year": None
            },
        ],
        "basilicata": [
            {
                "id": "BAS_MAM_001",
                "filename": "PDTA_Tumore_Mammella_Basilicata.pdf",
                "url": "https://www.regione.basilicata.it/wp-content/uploads/giunta/docs/DOCUMENT_FILE_3085806.pdf",
                "title": "PDTA Tumore della Mammella - Basilicata",
                "year": None
            },
            {
                "id": "BAS_HBV_001",
                "filename": "PDTA_Epatite_B_Basilicata.pdf",
                "url": "https://www.regione.basilicata.it/wp-content/uploads/giunta/docs/DOCUMENT_FILE_591188.pdf",
                "title": "PDTA Epatite B - Basilicata",
                "year": None
            },
            {
                "id": "BAS_ASMA_001",
                "filename": "PDTA_Asma_Bronchite_Cronica_Basilicata_2015.pdf",
                "url": "https://www.regione.basilicata.it/wp-content/uploads/giunta/docs/DOCUMENT_FILE_3085810.pdf",
                "title": "PDTA Asma e Bronchite Cronica - Basilicata",
                "year": 2015
            },
        ],
        "calabria": [
            {
                "id": "CAL_COL_001",
                "filename": "PDTA_Carcinoma_Colon_Retto_Calabria_DCA84_2022.pdf",
                "url": "https://www.regione.calabria.it/website/portalmedia/decreti/2022-08/ALLEGATO-DCA-n.84-del-16.8.2022.pdf",
                "title": "PDTA Carcinoma Colon-Retto - Calabria",
                "year": 2022
            },
            {
                "id": "CAL_SCA_001",
                "filename": "PDTA_Sindrome_Coronarica_Acuta_Calabria_2015.pdf",
                "url": "https://www.sifoweb.it/images/pdf/attivita/sezioni-regionali/calabria/Normativa/2015/dca_n._75_del_6.07.2015_-_PDTA_per_la_Sindrome_Coronarica__Acuta_SCA.pdf",
                "title": "PDTA Sindrome Coronarica Acuta - Calabria",
                "year": 2015
            },
            {
                "id": "CAL_PD_001",
                "filename": "PDTA_Piede_Diabetico_Calabria_2017.pdf",
                "url": "https://aemmedi.it/wp-content/uploads/2016/09/DCA_172_19_12_2017_piede_diabetico.pdf",
                "title": "PDTA Piede Diabetico - Calabria",
                "year": 2017
            },
            {
                "id": "CAL_TAL_001",
                "filename": "PDTA_Talassemie_Calabria_2023.pdf",
                "url": "https://www.regione.calabria.it/wp-content/uploads/2023/07/rete-talassemie_pdta.pdf",
                "title": "PDTA Talassemie e Emoglobinopatie - Calabria",
                "year": 2023
            },
        ],
        "liguria": [],
        "marche": [],
        "molise": [],
        "puglia": [
            {
                "id": "PUG_IVG_001",
                "filename": "PDTA_IVG_Puglia_DGR1738_2025.pdf",
                "url": "https://burp.regione.puglia.it/documents/20135/2715105/DEL_1738_2025.pdf",
                "title": "PDTA IVG - Puglia",
                "year": 2025
            },
        ],
        "sardegna": [
            {
                "id": "SAR_END_001",
                "filename": "PDTA_Endometriosi_Sardegna_2023.pdf",
                "url": "https://delibere.regione.sardegna.it/api/assets/9914fe92-6b7c-4361-9eac-c4b37dc33088",
                "title": "PDTA Endometriosi - Sardegna",
                "year": 2023
            },
        ],
        "sicilia": [
            {
                "id": "SIC_DIA_001",
                "filename": "PDTA_Diabete_Mellito_Adulto_Sicilia_2018.pdf",
                "url": "https://aemmedi.it/wp-content/uploads/2016/09/Sicilia_3_PDTA_AllegatoDA0602_16.04.2018_PDTA.pdf",
                "title": "PDTA Diabete Mellito Adulto - Sicilia",
                "year": 2018
            },
            {
                "id": "SIC_ONC_001",
                "filename": "PDTA_Oncologici_Sicilia_DA1077_2021.pdf",
                "url": "https://www.regione.sicilia.it/sites/default/files/2021-11/1077%2026.10.2021%20DA%20PDTA.pdf",
                "title": "PDTA Oncologici - Sicilia (DA 1077/2021)",
                "year": 2021
            },
            {
                "id": "SIC_PREV_001",
                "filename": "PDTA_Prevenzione_Oncologica_Sicilia_DA877_2025.pdf",
                "url": "https://www.regione.sicilia.it/sites/default/files/2025-09/Allegato%20al%20D.A.%20n.877%20del%208%20agosto%202025.pdf",
                "title": "PDTA Prevenzione Oncologica - Sicilia",
                "year": 2025
            },
        ],
        "trentino_alto_adige": [],
        "umbria": [
            {
                "id": "UMB_ICT_001",
                "filename": "PDTA_Ictus_Umbria_2021.pdf",
                "url": "https://isa-aii.com/wp-content/uploads/2021/06/1_PDTA_Umbria.pdf",
                "title": "PDTA Ictus - Umbria",
                "year": 2021
            },
        ],
        "valle_d_aosta": [],
    },
}


def download_file(url, dest_path, dry_run=False):
    """Download a file from a URL with retry logic."""
    if dry_run:
        print(f"  [DRY RUN] Would download: {url}")
        print(f"            To: {dest_path}")
        return True

    dest_path.parent.mkdir(parents=True, exist_ok=True)

    if dest_path.exists():
        print(f"  [SKIP] Already exists: {dest_path.name}")
        return True

    headers = {
        "User-Agent": "Mozilla/5.0 (research-bot; info_MIB project)"
    }

    max_retries = 3
    for attempt in range(max_retries):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=60) as response:
                content = response.read()
                with open(dest_path, "wb") as f:
                    f.write(content)
                size_kb = len(content) / 1024
                print(f"  [OK] Downloaded: {dest_path.name} ({size_kb:.0f} KB)")
                return True
        except urllib.error.HTTPError as e:
            print(f"  [ERROR] HTTP {e.code}: {url}")
            if e.code in (403, 404):
                return False
        except urllib.error.URLError as e:
            print(f"  [ERROR] Network error (attempt {attempt + 1}/{max_retries}): {e.reason}")
        except Exception as e:
            print(f"  [ERROR] Unexpected error (attempt {attempt + 1}/{max_retries}): {e}")

        if attempt < max_retries - 1:
            wait = 2 ** (attempt + 1)
            print(f"  Retrying in {wait}s...")
            time.sleep(wait)

    return False


def download_level(level, region=None, dry_run=False):
    """Download PDTA documents for a given level."""
    downloads = PDTA_DOWNLOADS.get(level, {})
    total = 0
    success = 0
    failed = 0

    for key, items in downloads.items():
        if region and key != region:
            continue

        if not items:
            continue

        if level == "nazionale":
            dest_dir = BASE_DIR / "nazionale" / key
        else:
            dest_dir = BASE_DIR / "regionale" / key

        print(f"\n{'=' * 60}")
        print(f"  {key.upper()} ({len(items)} files)")
        print(f"{'=' * 60}")

        for item in items:
            total += 1
            dest_path = dest_dir / item["filename"]
            print(f"\n  [{item['id']}] {item['title']}")

            if download_file(item["url"], dest_path, dry_run):
                success += 1
            else:
                failed += 1

    return total, success, failed


def create_manifest(dry_run=False):
    """Create a manifest of all downloaded files."""
    if dry_run:
        return

    manifest = {"generated": time.strftime("%Y-%m-%d %H:%M:%S"), "files": []}

    for pdf_path in sorted(BASE_DIR.rglob("*.pdf")):
        rel_path = pdf_path.relative_to(BASE_DIR)
        manifest["files"].append({
            "path": str(rel_path),
            "size_bytes": pdf_path.stat().st_size,
            "level": str(rel_path.parts[0]) if rel_path.parts else "unknown",
        })

    manifest_path = BASE_DIR / "download_manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    print(f"\nManifest saved to: {manifest_path}")
    print(f"Total PDFs: {len(manifest['files'])}")


def main():
    parser = argparse.ArgumentParser(
        description="Download publicly available PDTA documents"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Show what would be downloaded without actually downloading"
    )
    parser.add_argument(
        "--level", choices=["nazionale", "regionale", "all"], default="all",
        help="Download level (default: all)"
    )
    parser.add_argument(
        "--region", type=str, default=None,
        help="Specific region to download (e.g., lombardia, campania)"
    )
    args = parser.parse_args()

    print("=" * 60)
    print("  PDTA Document Downloader")
    print("  Percorsi Diagnostico-Terapeutici Assistenziali")
    print("=" * 60)

    if args.dry_run:
        print("\n  *** DRY RUN MODE - No files will be downloaded ***\n")

    total = 0
    success = 0
    failed = 0

    if args.level in ("nazionale", "all"):
        t, s, f = download_level("nazionale", dry_run=args.dry_run)
        total += t
        success += s
        failed += f

    if args.level in ("regionale", "all"):
        t, s, f = download_level("regionale", region=args.region, dry_run=args.dry_run)
        total += t
        success += s
        failed += f

    print(f"\n{'=' * 60}")
    print(f"  SUMMARY")
    print(f"  Total: {total} | Success: {success} | Failed: {failed}")
    print(f"{'=' * 60}")

    if not args.dry_run:
        create_manifest()

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
