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
        ],
        "toscana": [],
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
        "abruzzo": [],
        "basilicata": [],
        "calabria": [],
        "liguria": [],
        "marche": [],
        "molise": [],
        "puglia": [],
        "sardegna": [],
        "sicilia": [],
        "trentino_alto_adige": [],
        "umbria": [],
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
