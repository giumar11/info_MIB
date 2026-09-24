#!/usr/bin/env python3
"""
Download dei report ORIGINALI (PDF) delle società scientifiche italiane.

Finora il repository conteneva solo gli estratti elaborati
`datasets/raw/societa_scientifiche/italiane/rapporti_societa_italiane.json` e
`.../europee/rapporti_societa_europee.json`, con i soli URL alle pagine di
atterraggio. Questo script scarica i PDF originali dei rapporti di punta in
datasets/raw/societa_scientifiche/italiane/pdf/<societa>/.

NOTA SULLE URL
--------------
Gli URL sono stati raccolti dall'indice pubblico delle rispettive società
(AIOM, AIRTUM, SIMG, SID/AMD, Ministero della Salute per i rapporti nazionali di
riferimento su salute mentale e oncologia, ecc.). La verifica avviene in
esecuzione (runner con rete completa). I download falliti sono registrati nel
manifest senza bloccare gli altri. Molte società (cardiologia, neurologia)
non pubblicano un PDF nazionale scaricabile: per queste si rimanda alla landing
page indicata nel catalogo/JSON.

Uso:
    python3 scripts/download_societa_reports.py           # scarica i mancanti
    python3 scripts/download_societa_reports.py --check     # solo stato
    python3 scripts/download_societa_reports.py --force      # riscarica tutto
"""

import argparse
import hashlib
import json
import os
import ssl
import sys
import time
import urllib.error
import urllib.request

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IT_PDF_DIR = os.path.join(BASE_DIR, "datasets", "raw", "societa_scientifiche", "italiane", "pdf")
MANIFEST_PATH = os.path.join(IT_PDF_DIR, "manifest.json")

# Report di punta delle società scientifiche italiane (+ rapporti nazionali di
# riferimento del Ministero della Salute). `societa` determina la sottocartella.
SOCIETA_REPORTS = [
    {
        "societa": "aiom",
        "filename": "I_numeri_del_cancro_in_Italia_2025.pdf",
        "url": "https://www.aiom.it/wp-content/uploads/2025/12/2025_NDC_web.pdf",
        "title": "I numeri del cancro in Italia 2025",
        "year": 2025,
    },
    {
        "societa": "aiom",
        "filename": "I_numeri_del_cancro_in_Italia_2024.pdf",
        "url": "https://www.aiom.it/wp-content/uploads/2025/01/2024_NDC_web-def.pdf",
        "title": "I numeri del cancro in Italia 2024",
        "year": 2024,
    },
    {
        "societa": "airtum",
        "filename": "AIRTUM_I_tumori_in_Italia_2017_sopravvivenza.pdf",
        "url": "https://www.registri-tumori.it/PDF/AIRTUM2017/AIRTUM2017_full.pdf",
        "title": "I tumori in Italia - Rapporto 2016/2017 (La sopravvivenza)",
        "year": 2017,
    },
    {
        "societa": "simg",
        "filename": "Health_Search_Report_XV.pdf",
        "url": "https://www.simg.it/hs-report/XV.pdf",
        "title": "XV Report Health Search (SIMG)",
        "year": 2022,
    },
    {
        "societa": "simg",
        "filename": "Health_Search_Report_IX.pdf",
        "url": "https://www.simg.it/hs-report/IX.pdf",
        "title": "IX Report Health Search (SIMG)",
        "year": None,
    },
    {
        "societa": "sid_amd",
        "filename": "Standard_Cura_Diabete_AMD_SID_2018.pdf",
        "url": "https://aemmedi.it/wp-content/uploads/2009/06/AMD-Standard-unico1.pdf",
        "title": "Standard italiani per la cura del diabete mellito 2018 (AMD/SID)",
        "year": 2018,
    },
    {
        "societa": "sid_amd",
        "filename": "LG_Terapia_Diabete_tipo1_SID_2024.pdf",
        "url": "https://www.siditalia.it/pdf/LG-196-La-terapia-del-diabete-di-tipo-1-Ed-2024.pdf",
        "title": "Linea guida - La terapia del diabete di tipo 1, Ed. 2024 (SID)",
        "year": 2024,
    },
    {
        "societa": "sid_amd",
        "filename": "Protocollo_Annali_AMD_v3_2025.pdf",
        "url": "https://aemmedi.it/wp-content/uploads/2026/01/Protocollo-Annali-AMD_V3.0_1giu2025.pdf",
        "title": "Protocollo Annali AMD v3.0 (monitoraggio assistenza diabetologica)",
        "year": 2025,
    },
    {
        "societa": "salute_mentale",
        "filename": "Rapporto_Salute_Mentale_2024.pdf",
        "url": "https://www.salute.gov.it/new/sites/default/files/2026-04/Rapporto%20Salute%20Mentale%20Anno%202024%20ver.2.3_def.pdf",
        "title": "Rapporto Salute Mentale - Anno 2024 (Ministero della Salute)",
        "year": 2024,
    },
    {
        "societa": "salute_mentale",
        "filename": "Rapporto_Salute_Mentale_2023.pdf",
        "url": "https://www.salute.gov.it/new/sites/default/files/imported/C_17_pubblicazioni_3369_allegato.pdf",
        "title": "Rapporto Salute Mentale - dati 2022 (Ministero della Salute)",
        "year": 2023,
    },
    {
        "societa": "neurologia",
        "filename": "Libro_Bianco_Epilessia_Italia_2021.pdf",
        "url": "https://www.fiepilessie.it/wp-content/uploads/2021/06/Libro_bianco.pdf",
        "title": "Il Libro Bianco dell'Epilessia in Italia (FIE)",
        "year": 2021,
    },
]

SOCIETA_LANDING_PAGES = {
    "aiom_numeri": "https://www.aiom.it/i-numeri-del-cancro-in-italia/",
    "airtum_pubblicazioni": "https://www.registri-tumori.it/cms/a2-tipo-pubblicazioni/i-tumori-italia",
    "simg_health_search": "https://www.simg.it/pubblicazioni/report-health-search/",
    "amd_standard": "https://aemmedi.it/standard-di-cura/",
    "sid_standard": "https://www.siditalia.it/clinica/standard-di-cura-e-linee-guida-sid",
    "passi_nazionali": "https://www.epicentro.iss.it/passi/comunicazione/nazionali/nazionali",
}


def download_pdf(url, filepath, max_retries=3):
    ctx = ssl.create_default_context()
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/pdf,*/*",
    }
    for attempt in range(max_retries):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, context=ctx, timeout=120) as resp:
                data = resp.read()
                ctype = resp.headers.get("Content-Type", "")
                if len(data) < 1000:
                    print(f"    WARNING: file troppo piccolo ({len(data)} byte)")
                    return None, None
                if "html" in ctype.lower() and b"%PDF" not in data[:1024]:
                    print(f"    WARNING: risposta non-PDF (Content-Type: {ctype})")
                    return None, None
                with open(filepath, "wb") as f:
                    f.write(data)
                return len(data), hashlib.sha256(data).hexdigest()
        except (urllib.error.URLError, urllib.error.HTTPError, OSError) as e:
            print(f"    Tentativo {attempt + 1}/{max_retries} fallito: {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** (attempt + 1))
    return None, None


def format_size(n):
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f} MB"
    if n >= 1_000:
        return f"{n / 1_000:.1f} KB"
    return f"{n} B"


def check_status():
    print("=" * 70)
    print("STATO DOWNLOAD REPORT SOCIETÀ SCIENTIFICHE")
    print("=" * 70)
    print(f"\nDirectory: {IT_PDF_DIR}\n")
    ok = missing = total_size = 0
    for r in SOCIETA_REPORTS:
        fp = os.path.join(IT_PDF_DIR, r["societa"], r["filename"])
        if os.path.exists(fp) and os.path.getsize(fp) > 1000:
            size = os.path.getsize(fp)
            total_size += size
            ok += 1
            print(f"  [OK]      {r['societa']}/{r['filename']} ({format_size(size)})")
        else:
            missing += 1
            print(f"  [MISSING] {r['societa']}/{r['filename']}")
            print(f"            URL: {r['url']}")
    print(f"\n{'=' * 70}")
    print(f"Scaricati: {ok}/{len(SOCIETA_REPORTS)} ({format_size(total_size)}) | Mancanti: {missing}")
    print("=" * 70)


def main():
    parser = argparse.ArgumentParser(description="Download report società scientifiche italiane")
    parser.add_argument("--check", action="store_true", help="Mostra solo lo stato")
    parser.add_argument("--force", action="store_true", help="Riscarica tutto")
    args = parser.parse_args()

    os.makedirs(IT_PDF_DIR, exist_ok=True)
    if args.check:
        check_status()
        return 0

    print("=" * 70)
    print("DOWNLOAD REPORT SOCIETÀ SCIENTIFICHE ITALIANE")
    print("=" * 70)
    print(f"\nTarget: {IT_PDF_DIR}\nReport totali: {len(SOCIETA_REPORTS)}\n")

    manifest = []
    success = failed = skipped = 0

    for i, r in enumerate(SOCIETA_REPORTS, 1):
        dest_dir = os.path.join(IT_PDF_DIR, r["societa"])
        os.makedirs(dest_dir, exist_ok=True)
        filepath = os.path.join(dest_dir, r["filename"])

        if not args.force and os.path.exists(filepath) and os.path.getsize(filepath) > 1000:
            size = os.path.getsize(filepath)
            sha = hashlib.sha256(open(filepath, "rb").read()).hexdigest()
            print(f"[{i}/{len(SOCIETA_REPORTS)}] SKIP (esiste): {r['societa']}/{r['filename']} ({format_size(size)})")
            manifest.append({**r, "size_bytes": size, "sha256": sha, "status": "ok"})
            success += 1
            skipped += 1
            continue

        print(f"[{i}/{len(SOCIETA_REPORTS)}] Download: {r['societa']}/{r['filename']}")
        print(f"    URL: {r['url']}")
        size, sha = download_pdf(r["url"], filepath)
        if size:
            print(f"    OK: {format_size(size)}")
            manifest.append({**r, "size_bytes": size, "sha256": sha, "status": "ok"})
            success += 1
        else:
            print("    FALLITO")
            manifest.append({**r, "size_bytes": 0, "sha256": None, "status": "failed"})
            failed += 1
        if i < len(SOCIETA_REPORTS):
            time.sleep(1)

    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump({
            "description": "Manifest report originali società scientifiche italiane",
            "download_date": time.strftime("%Y-%m-%d"),
            "note": "URL raccolti dall'indice pubblico delle società; verificare in esecuzione.",
            "landing_pages": SOCIETA_LANDING_PAGES,
            "total": len(SOCIETA_REPORTS),
            "downloaded": success,
            "failed": failed,
            "files": manifest,
        }, f, indent=2, ensure_ascii=False)

    print(f"\n{'=' * 70}")
    print(f"RISULTATO: {success}/{len(SOCIETA_REPORTS)} disponibili ({success - skipped} nuovi, {skipped} già presenti)")
    if failed:
        print(f"           {failed} download falliti (vedi manifest)")
    print(f"Manifest: {MANIFEST_PATH}")
    print("=" * 70)
    return 0


if __name__ == "__main__":
    sys.exit(main())
