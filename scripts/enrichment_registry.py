#!/usr/bin/env python3
"""
Registro dichiarativo delle fonti di enrichment (info_MIB).

Questo modulo definisce, per OGNI categoria di documenti presente nel
repository, l'elenco delle fonti ORIGINALI da scaricare: sia i *dataset*
grezzi (CSV/XML/ZIP/XLSX) sia i *report* originali (PDF) pubblicati dalle
istituzioni. L'obiettivo è mantenere nel repository i documenti primari e
non solo gli estratti elaborati (`datasets/processed/`).

Il modulo è consumato da `scripts/run_enrichment.py`, che esegue il
download idempotente, la validazione e la generazione dei manifest.

Schema di un target (dizionario):

    {
        "id":          identificativo univoco della fonte,
        "title":       titolo leggibile,
        "kind":        "report" | "dataset",
        "expected":    "pdf" | "csv" | "xml" | "zip" | "xlsx" | "json",
        "filename":    nome file di destinazione,
        "url":         URL diretto al file (None se va risolto a mano),
        "source_page": pagina/portale ufficiale di pubblicazione,
        "verified":    True se l'URL diretto è stato verificato in passato
                       (es. file già presente nel repo), False altrimenti,
        "min_bytes":   dimensione minima plausibile del file valido,
        "frequency":   frequenza di aggiornamento della fonte,
    }

Le categorie riflettono le sottocartelle di `datasets/raw/`.
Gli URL diretti "verified" per GIMBE e PDTA sono riusati dai rispettivi
script di download (`download_gimbe_pdfs.py`, `download_pdta.py`) tramite
gli adattatori in `run_enrichment.py`, quindi non vengono duplicati qui.
"""

from __future__ import annotations

import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(BASE_DIR, "datasets", "raw")


# Ordine e metadati delle categorie di documenti del repository.
# `dir` è relativo a datasets/raw/. `external_module` indica che i target
# provengono da uno script di download dedicato (gestito dall'orchestratore).
CATEGORIES: dict[str, dict] = {
    # === Governance e performance SSN ===
    "governance": {
        "label": "Governance e performance SSN (PNE, LEA, PNGLA)",
        "dir": "governance",
        "sources": [
            {
                "id": "PNE_2024_REPORT",
                "title": "AGENAS - Programma Nazionale Esiti (rapporto)",
                "kind": "report",
                "expected": "pdf",
                "filename": "pne/rapporto_pne_2024.pdf",
                "url": None,
                "source_page": "https://pne.agenas.it/",
                "verified": False,
                "min_bytes": 100_000,
                "frequency": "annual",
            },
            {
                "id": "LEA_2023_REPORT",
                "title": "Monitoraggio LEA / Nuovo Sistema di Garanzia (rapporto)",
                "kind": "report",
                "expected": "pdf",
                "filename": "lea_nsg/monitoraggio_lea_2023.pdf",
                "url": None,
                "source_page": "https://www.salute.gov.it/portale/lea/",
                "verified": False,
                "min_bytes": 100_000,
                "frequency": "annual",
            },
            {
                "id": "PNGLA_REPORT",
                "title": "Piano Nazionale Gestione Liste di Attesa - monitoraggio",
                "kind": "report",
                "expected": "pdf",
                "filename": "pngla/monitoraggio_pngla.pdf",
                "url": None,
                "source_page": "https://pnla.agenas.it/",
                "verified": False,
                "min_bytes": 50_000,
                "frequency": "continuous",
            },
        ],
    },

    # === Finanza del SSN ===
    "finanza": {
        "label": "Finanza del SSN (OpenBDAP, OsMed)",
        "dir": "finanza",
        "sources": [
            {
                "id": "OSMED_2023_REPORT",
                "title": "AIFA - Rapporto OsMed (uso dei farmaci in Italia)",
                "kind": "report",
                "expected": "pdf",
                "filename": "osmed/rapporto_osmed_2023.pdf",
                "url": None,
                "source_page": "https://www.aifa.gov.it/rapporti-osmed",
                "verified": False,
                "min_bytes": 500_000,
                "frequency": "annual",
            },
            {
                "id": "BDAP_SSN_DATASET",
                "title": "OpenBDAP (RGS/MEF) - conto economico enti SSN",
                "kind": "dataset",
                "expected": "csv",
                "filename": "openbdap/conto_economico_ssn.csv",
                "url": None,
                "source_page": "https://openbdap.rgs.mef.gov.it/",
                "verified": False,
                "min_bytes": 10_000,
                "frequency": "quarterly",
            },
        ],
    },

    # === Farmaceutica (AIFA) - report originali oltre agli estratti JSON ===
    "aifa": {
        "label": "AIFA - Agenzia Italiana del Farmaco",
        "dir": "aifa",
        "sources": [
            {
                "id": "AIFA_OSMED_REPORT",
                "title": "Rapporto OsMed - L'uso dei farmaci in Italia",
                "kind": "report",
                "expected": "pdf",
                "filename": "rapporto_osmed_2023.pdf",
                "url": None,
                "source_page": "https://www.aifa.gov.it/rapporti-osmed",
                "verified": False,
                "min_bytes": 500_000,
                "frequency": "annual",
            },
            {
                "id": "AIFA_VACCINI_REPORT",
                "title": "Rapporto Vaccini - sorveglianza post-marketing",
                "kind": "report",
                "expected": "pdf",
                "filename": "rapporto_vaccini_2023.pdf",
                "url": None,
                "source_page": "https://www.aifa.gov.it/rapporto-vaccini",
                "verified": False,
                "min_bytes": 300_000,
                "frequency": "annual",
            },
            {
                "id": "AIFA_SPERIMENTAZIONE_REPORT",
                "title": "Rapporto sulla Sperimentazione Clinica dei medicinali",
                "kind": "report",
                "expected": "pdf",
                "filename": "rapporto_sperimentazione_clinica_2023.pdf",
                "url": None,
                "source_page": "https://www.aifa.gov.it/rapporto-sulla-sperimentazione-clinica-dei-medicinali-in-italia",
                "verified": False,
                "min_bytes": 300_000,
                "frequency": "annual",
            },
            {
                "id": "AIFA_ATTIVITA_REPORT",
                "title": "Rapporto sulle Attività AIFA",
                "kind": "report",
                "expected": "pdf",
                "filename": "rapporto_attivita_aifa_2024.pdf",
                "url": None,
                "source_page": "https://www.aifa.gov.it/rapporto-sulle-attivita-aifa",
                "verified": False,
                "min_bytes": 300_000,
                "frequency": "annual",
            },
            {
                "id": "AIFA_LISTE_TRASPARENZA",
                "title": "Liste di Trasparenza - farmaci equivalenti (dataset)",
                "kind": "dataset",
                "expected": "pdf",
                "filename": "liste_trasparenza.pdf",
                "url": None,
                "source_page": "https://www.aifa.gov.it/liste-di-trasparenza",
                "verified": False,
                "min_bytes": 50_000,
                "frequency": "monthly",
            },
        ],
    },

    # === Riforme strutturali ===
    "riforme": {
        "label": "Riforme strutturali (DM 77/2022, PNRR M6, DM 70/2015)",
        "dir": "riforme",
        "sources": [
            {
                "id": "DM77_2022_GAZZETTA",
                "title": "DM 77/2022 - Assistenza territoriale (Gazzetta Ufficiale)",
                "kind": "report",
                "expected": "pdf",
                "filename": "dm77_2022/dm_77_2022_gazzetta.pdf",
                "url": "https://www.gazzettaufficiale.it/eli/id/2022/06/22/22G00085/sg",
                "source_page": "https://www.gazzettaufficiale.it/eli/id/2022/06/22/22G00085/sg",
                "verified": False,
                "min_bytes": 100_000,
                "frequency": "static",
            },
            {
                "id": "PNRR_M6_SALUTE",
                "title": "PNRR Missione 6 Salute - documento ufficiale",
                "kind": "report",
                "expected": "pdf",
                "filename": "pnrr_m6/pnrr_missione6_salute.pdf",
                "url": None,
                "source_page": "https://www.salute.gov.it/portale/pnrr/",
                "verified": False,
                "min_bytes": 100_000,
                "frequency": "quarterly",
            },
        ],
    },

    # === Comparatori internazionali ===
    "internazionale": {
        "label": "Comparatori internazionali (OECD, Eurostat, WHO)",
        "dir": "internazionale",
        "sources": [
            {
                "id": "OECD_HEALTH_AT_GLANCE",
                "title": "OECD Health at a Glance: Europe (report)",
                "kind": "report",
                "expected": "pdf",
                "filename": "oecd/health_at_a_glance_europe.pdf",
                "url": None,
                "source_page": "https://www.oecd.org/health/health-at-a-glance-europe/",
                "verified": False,
                "min_bytes": 500_000,
                "frequency": "biennial",
            },
            {
                "id": "WHO_GHED_DATASET",
                "title": "WHO Global Health Expenditure Database (export)",
                "kind": "dataset",
                "expected": "xlsx",
                "filename": "who_ghed/ghed_export.xlsx",
                "url": None,
                "source_page": "https://apps.who.int/nha/database",
                "verified": False,
                "min_bytes": 100_000,
                "frequency": "annual",
            },
            {
                "id": "EUROSTAT_SHA_DATASET",
                "title": "Eurostat - Health care expenditure (SHA) dataset",
                "kind": "dataset",
                "expected": "csv",
                "filename": "eurostat/health_expenditure_sha.csv",
                "url": None,
                "source_page": "https://ec.europa.eu/eurostat/web/health/data/database",
                "verified": False,
                "min_bytes": 10_000,
                "frequency": "annual",
            },
        ],
    },

    # === Ministero Salute - SDO (dataset originali + rapporto) ===
    "ministero_salute": {
        "label": "Ministero della Salute - SDO e Open Data",
        "dir": "ministero_salute",
        "sources": [
            {
                "id": "SDO_2023_REPORT",
                "title": "Rapporto annuale attività di ricovero ospedaliero (SDO)",
                "kind": "report",
                "expected": "pdf",
                "filename": "rapporto_sdo_2023_completo.pdf",
                "url": None,
                "source_page": "https://www.salute.gov.it/new/it/tema/ricoveri-ospedalieri-sdo/",
                "verified": False,
                "min_bytes": 500_000,
                "frequency": "annual",
            },
            {
                "id": "SDO_OPENDATA_ETA_SESSO",
                "title": "Open Data SDO - dimissioni per fasce età e sesso",
                "kind": "dataset",
                "expected": "csv",
                "filename": "Open_data_-_SDO_per_fasce_età_e_sesso_oscurata_DEF.csv",
                "url": None,
                "source_page": "https://www.dati.salute.gov.it/",
                "verified": False,
                "min_bytes": 5_000,
                "frequency": "annual",
            },
        ],
    },

    # === Epidemiologia malattie rare (Orphadata) ===
    "orphadata": {
        "label": "Orphanet / Orphadata - epidemiologia malattie rare",
        "dir": ".",
        "sources": [
            {
                "id": "ORPHADATA_PREVALENCE",
                "title": "Orphadata - Rare disease epidemiology (product9_prev)",
                "kind": "dataset",
                "expected": "xml",
                "filename": "orphadata_epidemiology_it.xml",
                "url": "https://www.orphadata.com/data/xml/en_product9_prev.xml",
                "source_page": "https://www.orphadata.com/epidemiology/",
                "verified": False,
                "min_bytes": 500_000,
                "frequency": "quarterly",
            },
        ],
    },

    # === ISTAT (EHIS, Health for All) ===
    "istat": {
        "label": "ISTAT - EHIS e Health for All",
        "dir": "istat",
        "sources": [
            {
                "id": "ISTAT_EHIS_TAVOLE",
                "title": "ISTAT - Tavole EHIS 2019",
                "kind": "dataset",
                "expected": "zip",
                "filename": "tavole_ehis_2019.zip",
                "url": None,
                "source_page": "https://www.istat.it/it/archivio/EHIS",
                "verified": False,
                "min_bytes": 50_000,
                "frequency": "biennial",
            },
        ],
    },

    # === Screening oncologici (ONS) ===
    "ons": {
        "label": "Osservatorio Nazionale Screening (ONS)",
        "dir": "ons",
        "sources": [
            {
                "id": "ONS_REPORT",
                "title": "ONS - Rapporto annuale screening oncologici",
                "kind": "report",
                "expected": "pdf",
                "filename": "rapporto_ons_screening.pdf",
                "url": None,
                "source_page": "https://www.osservatorionazionalescreening.it/",
                "verified": False,
                "min_bytes": 200_000,
                "frequency": "annual",
            },
        ],
    },

    # === OASI / CERGAS Bocconi ===
    "oasi_bocconi": {
        "label": "CERGAS - SDA Bocconi - Rapporto OASI",
        "dir": "oasi_bocconi",
        "sources": [
            {
                "id": "OASI_SINTESI",
                "title": "Rapporto OASI - sintesi/executive summary",
                "kind": "report",
                "expected": "pdf",
                "filename": "oasi_executive_summary.pdf",
                "url": None,
                "source_page": "https://cergas.unibocconi.eu/observatories/oasi_/rapporto-oasi",
                "verified": False,
                "min_bytes": 100_000,
                "frequency": "annual",
            },
        ],
    },

    # === UNIAMO - malattie rare ===
    "uniamo": {
        "label": "UNIAMO - Rapporto MonitoRare",
        "dir": "uniamo",
        "sources": [
            {
                "id": "UNIAMO_MONITORARE",
                "title": "UNIAMO - Rapporto MonitoRare sulle malattie rare",
                "kind": "report",
                "expected": "pdf",
                "filename": "report_malattie_rare_2024.pdf",
                "url": None,
                "source_page": "https://uniamo.org/monitorare/",
                "verified": False,
                "min_bytes": 200_000,
                "frequency": "annual",
            },
        ],
    },

    # === Osservatorio Nazionale sulla Salute nelle Regioni ===
    "osservatorio_salute": {
        "label": "Osservatorio Nazionale sulla Salute nelle Regioni",
        "dir": "osservatorio_salute",
        "sources": [
            {
                "id": "OSSERVATORIO_REPORT",
                "title": "Rapporto Osservatorio Salute nelle Regioni",
                "kind": "report",
                "expected": "pdf",
                "filename": "rapporto_osservatorio_2025.pdf",
                "url": None,
                "source_page": "https://www.osservatoriosullasalute.it/",
                "verified": False,
                "min_bytes": 500_000,
                "frequency": "annual",
            },
        ],
    },

    # === Sistema sanitario (report Italia + internazionali) ===
    "sistema_sanitario": {
        "label": "Sistema sanitario - report criticità (Italia e internazionali)",
        "dir": "sistema_sanitario",
        "sources": [
            {
                "id": "ITALY_HEALTH_PROFILE_EU",
                "title": "State of Health in the EU - Italy Country Health Profile",
                "kind": "report",
                "expected": "pdf",
                "filename": "internazionale/italy_health_profile_2025_eu.pdf",
                "url": None,
                "source_page": "https://health.ec.europa.eu/state-health-eu/country-health-profiles_en",
                "verified": False,
                "min_bytes": 500_000,
                "frequency": "biennial",
            },
        ],
    },

    # === ENPAM - workforce ===
    "enpam": {
        "label": "ENPAM - specialisti ambulatoriali e workforce",
        "dir": "enpam",
        "sources": [
            {
                "id": "ENPAM_GUIDA_SPECIALISTI",
                "title": "ENPAM - Guida specialisti ambulatoriali",
                "kind": "report",
                "expected": "pdf",
                "filename": "guida_specialisti_ambulatoriali_2024.pdf",
                "url": None,
                "source_page": "https://www.enpam.it/",
                "verified": False,
                "min_bytes": 100_000,
                "frequency": "periodic",
            },
        ],
    },

    # === ASSICURATIVO - ANIA (nuova categoria) ===
    "ania": {
        "label": "ANIA - Associazione Nazionale fra le Imprese Assicuratrici",
        "dir": "ania",
        "sources": [
            {
                "id": "ANIA_RELAZIONE_ANNUALE",
                "title": "L'Assicurazione Italiana - Relazione annuale ANIA",
                "kind": "report",
                "expected": "pdf",
                "filename": "ania_relazione_annuale_2023_2024.pdf",
                "url": None,
                "source_page": "https://www.ania.it/pubblicazioni",
                "verified": False,
                "min_bytes": 500_000,
                "frequency": "annual",
            },
            {
                "id": "ANIA_ITALIAN_INSURANCE_FIGURES",
                "title": "Italian Insurance in Figures / L'assicurazione in cifre",
                "kind": "report",
                "expected": "pdf",
                "filename": "ania_assicurazione_in_cifre_2024.pdf",
                "url": None,
                "source_page": "https://www.ania.it/pubblicazioni",
                "verified": False,
                "min_bytes": 200_000,
                "frequency": "annual",
            },
            {
                "id": "ANIA_TRENDS_PREMI",
                "title": "ANIA Trends - Premi del lavoro diretto italiano",
                "kind": "report",
                "expected": "pdf",
                "filename": "ania_trends_premi.pdf",
                "url": None,
                "source_page": "https://www.ania.it/statistiche-e-dati",
                "verified": False,
                "min_bytes": 100_000,
                "frequency": "quarterly",
            },
            {
                "id": "ANIA_TRENDS_SALUTE",
                "title": "ANIA Trends - Rami danni / assicurazione malattia e salute",
                "kind": "report",
                "expected": "pdf",
                "filename": "ania_trends_salute.pdf",
                "url": None,
                "source_page": "https://www.ania.it/statistiche-e-dati",
                "verified": False,
                "min_bytes": 100_000,
                "frequency": "quarterly",
            },
            {
                "id": "ANIA_RC_AUTO",
                "title": "ANIA - Osservatorio R.C. Auto",
                "kind": "report",
                "expected": "pdf",
                "filename": "ania_rc_auto.pdf",
                "url": None,
                "source_page": "https://www.ania.it/statistiche-e-dati",
                "verified": False,
                "min_bytes": 100_000,
                "frequency": "periodic",
            },
            {
                "id": "IVASS_BOLLETTINO_STATISTICO",
                "title": "IVASS - Bollettino statistico (autorità di vigilanza)",
                "kind": "report",
                "expected": "pdf",
                "filename": "ivass_bollettino_statistico.pdf",
                "url": None,
                "source_page": "https://www.ivass.it/pubblicazioni-e-statistiche/statistiche/bollettino-statistico/",
                "verified": False,
                "min_bytes": 100_000,
                "frequency": "periodic",
            },
        ],
    },
}


def iter_targets():
    """Genera tutti i target del registro come tuple (category_key, source)."""
    for cat_key, cat in CATEGORIES.items():
        for src in cat["sources"]:
            yield cat_key, cat, src


def resolve_dest(cat: dict, src: dict) -> str:
    """Restituisce il percorso assoluto di destinazione per un target."""
    cat_dir = cat["dir"]
    if cat_dir == ".":
        return os.path.join(RAW_DIR, src["filename"])
    return os.path.join(RAW_DIR, cat_dir, src["filename"])


def summary() -> dict:
    """Riepilogo del registro: numero di categorie e target."""
    n_targets = sum(len(c["sources"]) for c in CATEGORIES.values())
    n_verified = sum(
        1 for _, _, s in iter_targets() if s.get("verified")
    )
    n_with_url = sum(1 for _, _, s in iter_targets() if s.get("url"))
    return {
        "categories": len(CATEGORIES),
        "targets": n_targets,
        "with_direct_url": n_with_url,
        "verified_urls": n_verified,
        "needs_manual_url": n_targets - n_with_url,
    }


if __name__ == "__main__":
    import json

    print(json.dumps(summary(), indent=2, ensure_ascii=False))
    for cat_key, cat, src in iter_targets():
        flag = "URL" if src.get("url") else "---"
        print(f"  [{flag}] {cat_key:20s} {src['id']:32s} {src['kind']:8s} {src['filename']}")
