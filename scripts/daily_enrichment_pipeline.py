#!/usr/bin/env python3
"""
Pipeline di enrichment GIORNALIERA per tutte le categorie di documenti del
repository info_MIB.

La pipeline esegue, per ogni categoria di documenti, due tipi di step:

  1. DOWNLOAD ORIGINALI  -> scarica i dataset e i report ORIGINALI (PDF, CSV,
     XML, ZIP, XLSX) direttamente dalla fonte, quando esistono. Non ci si
     limita agli estratti processati: dove la fonte pubblica un file scaricabile
     lo si salva in datasets/raw/.
  2. ENRICHMENT          -> (ri)genera gli estratti processati (JSON/CSV) e i
     dataset pronti per il database a partire dagli originali.

Categorie coperte (allineate a sources_catalog.csv):
  pdta, insurance (ANIA), pharma (AIFA/OsMed), analysis (GIMBE/OASI),
  screening/surveillance (ONS/società scientifiche), epidemiology/rare_diseases
  (Orphadata), activity (SDO), statistics (ISTAT HFA), governance/finance/
  reform/international/... (download catalog-driven degli originali).

Meccanismi di download:
  - Script dedicati per famiglia (GIMBE, PDTA, ANIA).
  - Downloader GENERICO catalog-driven: per ogni fonte del catalogo il cui `url`
    e un file scaricabile e la cui destinazione locale (file_paths_in_repo) e una
    directory priva di quel file, tenta il download dell'originale.

Robustezza: ogni step e isolato in try/except; un errore di rete o una
dipendenza mancante NON interrompe la pipeline. Tutto viene registrato nel report.

Usage:
    python3 scripts/daily_enrichment_pipeline.py                 # tutto
    python3 scripts/daily_enrichment_pipeline.py --category insurance
    python3 scripts/daily_enrichment_pipeline.py --originals-only
    python3 scripts/daily_enrichment_pipeline.py --enrich-only
    python3 scripts/daily_enrichment_pipeline.py --dry-run
    python3 scripts/daily_enrichment_pipeline.py --install-cron   # cron giornaliero
    python3 scripts/daily_enrichment_pipeline.py --uninstall-cron
"""

import argparse
import csv
import hashlib
import json
import os
import ssl
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS_DIR = os.path.join(BASE_DIR, "scripts")
CATALOG_PATH = os.path.join(BASE_DIR, "sources_catalog.csv")
LOGS_DIR = os.path.join(BASE_DIR, "logs")
PYTHON = sys.executable or "python3"

DOWNLOADABLE_EXT = (".pdf", ".csv", ".xml", ".zip", ".xlsx", ".xls", ".json", ".dbf")

TODAY = datetime.now().strftime("%Y-%m-%d")


# =============================================================================
# REGISTRY DEGLI STEP
# Ogni step: (id, categorie[], kind, descrizione, comando_o_funzione)
# kind: "download" | "enrich"
# Il comando e una lista argv eseguita come subprocess; se None si usa la
# funzione dedicata (es. downloader generico catalog-driven).
# =============================================================================

def _script(name, *args):
    return [PYTHON, os.path.join(SCRIPTS_DIR, name), *args]


PIPELINE_STEPS = [
    # --- DOWNLOAD ORIGINALI (report/dataset) ---
    {
        "id": "download_gimbe",
        "categories": ["analysis"],
        "kind": "download",
        "desc": "Download PDF originali dei report GIMBE",
        "cmd": _script("download_gimbe_pdfs.py"),
    },
    {
        "id": "download_pdta",
        "categories": ["pdta"],
        "kind": "download",
        "desc": "Download PDF originali dei PDTA (nazionali/regionali)",
        "cmd": _script("download_pdta.py", "--level", "all"),
    },
    {
        "id": "download_ania",
        "categories": ["insurance"],
        "kind": "download",
        "desc": "Download PDF originali dei report ANIA (assicurativo)",
        "cmd": _script("download_ania_reports.py"),
    },
    {
        "id": "download_catalog_originals",
        "categories": ["*"],
        "kind": "download",
        "desc": "Downloader generico catalog-driven: scarica gli originali mancanti "
                "per tutte le fonti con un file scaricabile",
        "cmd": None,  # funzione dedicata
    },
    # --- ENRICHMENT / PROCESSING ---
    {
        "id": "enrich_scientific_ons",
        "categories": ["screening", "surveillance", "analysis", "pharma"],
        "kind": "enrich",
        "desc": "Enrichment ONS + società scientifiche + OASI + AIFA + GIMBE",
        "cmd": _script("enrich_scientific_reports_ons.py"),
    },
    {
        "id": "extract_sdo",
        "categories": ["activity"],
        "kind": "enrich",
        "desc": "Estrazione dati SDO (ricoveri ospedalieri)",
        "cmd": _script("extract_sdo_data.py"),
        "requires": ["pandas"],
    },
    {
        "id": "parse_orphadata",
        "categories": ["epidemiology", "rare_diseases"],
        "kind": "enrich",
        "desc": "Parsing Orphadata malattie rare",
        "cmd": _script("parse_orphadata.py"),
        "requires": ["pandas"],
    },
    {
        "id": "migrate_to_database",
        "categories": ["*"],
        "kind": "enrich",
        "desc": "Generazione dataset migration_ready (SQL/NoSQL)",
        "cmd": _script("migrate_to_database.py"),
    },
]


# =============================================================================
# UTILITY
# =============================================================================

def _ssl_context():
    ctx = ssl.create_default_context()
    ca_bundle = os.environ.get("REQUESTS_CA_BUNDLE") or os.environ.get("SSL_CERT_FILE")
    if ca_bundle and os.path.exists(ca_bundle):
        try:
            ctx.load_verify_locations(ca_bundle)
        except Exception:
            pass
    return ctx


def _has_module(mod):
    try:
        __import__(mod)
        return True
    except Exception:
        return False


def load_catalog():
    with open(CATALOG_PATH, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def filename_from_url(url):
    name = url.split("?")[0].rstrip("/").split("/")[-1]
    if not name or "." not in name:
        name = hashlib.sha1(url.encode()).hexdigest()[:12] + ".pdf"
    return name


def download_file(url, filepath, max_retries=4):
    """Scarica un file con retry/backoff. Ritorna (size, sha256) o (None, None)."""
    ctx = _ssl_context()
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; InfoMIB-DataBot/1.0; "
                      "+https://github.com/giumar11/info_MIB)"
    }
    for attempt in range(max_retries):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, context=ctx, timeout=120) as resp:
                data = resp.read()
            if len(data) < 1000:
                return None, None
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, "wb") as f:
                f.write(data)
            return len(data), hashlib.sha256(data).hexdigest()
        except (urllib.error.URLError, urllib.error.HTTPError, OSError):
            if attempt < max_retries - 1:
                time.sleep(2 ** (attempt + 1))
    return None, None


# =============================================================================
# DOWNLOADER GENERICO CATALOG-DRIVEN
# =============================================================================

def run_catalog_originals(categories, dry_run, logger):
    """
    Per ogni fonte del catalogo con un URL scaricabile e una destinazione
    directory priva del file, scarica l'originale. Copre TUTTE le categorie non
    gestite da script dedicati (governance, finance, reform, epidemiology, ...).
    """
    catalog = load_catalog()
    handled_dirs = ("gimbe/pdf", "pdta/", "ania/pdf")  # gestiti da script dedicati
    attempted = downloaded = skipped = failed = 0
    details = []

    for row in catalog:
        cat = row.get("category", "")
        if categories != ["*"] and cat not in categories:
            continue
        url = (row.get("url") or "").strip()
        dest = (row.get("file_paths_in_repo") or "").strip()
        if not url or not dest or not url.lower().startswith("http"):
            continue
        if not url.lower().split("?")[0].endswith(DOWNLOADABLE_EXT):
            continue  # landing page, non un file diretto
        # destinazione: solo directory (i file singoli gia esistenti sono originali)
        if not (dest.endswith("/") or os.path.isdir(os.path.join(BASE_DIR, dest))):
            continue
        if any(h in dest for h in handled_dirs):
            continue  # gestito da script dedicato
        target_dir = os.path.join(BASE_DIR, dest)
        fname = filename_from_url(url)
        target_file = os.path.join(target_dir, fname)
        if os.path.exists(target_file) and os.path.getsize(target_file) > 1000:
            skipped += 1
            continue
        attempted += 1
        if dry_run:
            logger(f"    [DRY] {row['source_id']}: {url} -> {dest}{fname}")
            details.append({"source_id": row["source_id"], "url": url,
                            "target": os.path.relpath(target_file, BASE_DIR),
                            "status": "would_download"})
            continue
        logger(f"    download {row['source_id']}: {fname}")
        size, sha = download_file(url, target_file)
        if size:
            downloaded += 1
            details.append({"source_id": row["source_id"], "url": url,
                            "target": os.path.relpath(target_file, BASE_DIR),
                            "size_bytes": size, "sha256": sha, "status": "ok"})
        else:
            failed += 1
            details.append({"source_id": row["source_id"], "url": url,
                            "status": "failed"})
        time.sleep(1)

    return {
        "attempted": attempted, "downloaded": downloaded,
        "skipped_existing": skipped, "failed": failed, "details": details,
    }


# =============================================================================
# ESECUZIONE STEP
# =============================================================================

def run_subprocess_step(step, logger):
    cmd = step["cmd"]
    logger(f"    $ {' '.join(cmd)}")
    try:
        proc = subprocess.run(cmd, cwd=BASE_DIR, capture_output=True, text=True,
                              timeout=3600)
        ok = proc.returncode == 0
        tail = (proc.stdout or "").strip().splitlines()[-8:]
        for line in tail:
            logger(f"      | {line}")
        if proc.returncode != 0 and proc.stderr:
            for line in proc.stderr.strip().splitlines()[-8:]:
                logger(f"      ! {line}")
        return {"returncode": proc.returncode,
                "status": "ok" if ok else "error",
                "stdout_tail": tail,
                "stderr_tail": (proc.stderr or "").strip().splitlines()[-8:]}
    except subprocess.TimeoutExpired:
        logger("      ! timeout")
        return {"status": "timeout"}
    except Exception as e:  # noqa: BLE001
        logger(f"      ! eccezione: {e}")
        return {"status": "exception", "error": str(e)}


def step_selected(step, categories, kind_filter):
    if kind_filter and step["kind"] != kind_filter:
        return False
    if categories == ["*"]:
        return True
    if step["categories"] == ["*"]:
        return True
    return any(c in categories for c in step["categories"])


def run_pipeline(categories, kind_filter, dry_run):
    os.makedirs(LOGS_DIR, exist_ok=True)
    log_path = os.path.join(LOGS_DIR, f"enrichment_{TODAY}.log")
    report_path = os.path.join(LOGS_DIR, f"enrichment_report_{TODAY}.json")
    log_lines = []

    def logger(msg):
        line = msg
        print(line)
        log_lines.append(line)

    logger("=" * 70)
    logger(f"PIPELINE DI ENRICHMENT GIORNALIERA - {datetime.now().isoformat()}")
    logger(f"Categorie: {categories} | kind: {kind_filter or 'all'} | dry_run: {dry_run}")
    logger("=" * 70)

    results = []
    for step in PIPELINE_STEPS:
        if not step_selected(step, categories, kind_filter):
            continue
        logger(f"\n[{step['kind'].upper()}] {step['id']} - {step['desc']}")

        # Dipendenze mancanti -> skip gestito
        missing = [m for m in step.get("requires", []) if not _has_module(m)]
        if missing:
            logger(f"    SKIP: dipendenze mancanti {missing} "
                   f"(installa con: pip install {' '.join(missing)})")
            results.append({"id": step["id"], "kind": step["kind"],
                           "status": "skipped_missing_deps", "missing": missing})
            continue

        if step["cmd"] is None and step["id"] == "download_catalog_originals":
            if dry_run:
                logger("    [DRY] downloader generico catalog-driven")
            res = run_catalog_originals(categories, dry_run, logger)
            res.update({"id": step["id"], "kind": step["kind"],
                        "status": "ok" if not res["failed"] else "partial"})
            results.append(res)
            continue

        if dry_run:
            logger(f"    [DRY] {' '.join(step['cmd'])}")
            results.append({"id": step["id"], "kind": step["kind"], "status": "dry_run"})
            continue

        res = run_subprocess_step(step, logger)
        # I download parziali (rete non raggiungibile per alcune fonti) sono un
        # "partial", non un errore duro: la pipeline giornaliera non deve fallire
        # per hiccup di rete. Un errore in uno step di ENRICHMENT resta invece duro.
        if step["kind"] == "download" and res.get("status") == "error":
            res["status"] = "partial"
        res.update({"id": step["id"], "kind": step["kind"], "desc": step["desc"]})
        results.append(res)

    # Riepilogo
    logger("\n" + "=" * 70)
    logger("RIEPILOGO")
    for r in results:
        logger(f"  [{r.get('status'):22}] {r['id']}")
    logger("=" * 70)

    report = {
        "pipeline": "daily_enrichment",
        "date": TODAY,
        "timestamp": datetime.now().isoformat(),
        "categories": categories,
        "kind_filter": kind_filter,
        "dry_run": dry_run,
        "steps": results,
    }
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    with open(log_path, "w", encoding="utf-8") as f:
        f.write("\n".join(log_lines) + "\n")

    print(f"\nReport: {os.path.relpath(report_path, BASE_DIR)}")
    print(f"Log:    {os.path.relpath(log_path, BASE_DIR)}")

    # exit code: 0 se nessuno step in errore duro
    hard_errors = [r for r in results if r.get("status") in ("error", "exception", "timeout")]
    return 0 if not hard_errors else 1


# =============================================================================
# CRON
# =============================================================================

def install_cron():
    script_path = os.path.abspath(__file__)
    log_path = os.path.join(LOGS_DIR, "cron_enrichment.log")
    cron_line = f"0 6 * * * {PYTHON} {script_path} >> {log_path} 2>&1"
    comment = "# InfoMIB - Pipeline enrichment giornaliera"
    try:
        cur = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
        current = cur.stdout if cur.returncode == 0 else ""
        if "daily_enrichment_pipeline.py" in current:
            print("Job cron gia installato:")
            print(current)
            return
        new = current.rstrip("\n")
        new = (new + "\n" if new else "") + f"\n{comment}\n{cron_line}\n"
        p = subprocess.Popen(["crontab", "-"], stdin=subprocess.PIPE, text=True)
        p.communicate(input=new)
        if p.returncode == 0:
            print("Job cron installato: ogni giorno alle 06:00")
            print(f"  {cron_line}")
        else:
            print("Errore installazione cron. Aggiungi manualmente:")
            print(f"  {cron_line}")
    except FileNotFoundError:
        print("'crontab' non disponibile. Schedulazione manuale:")
        print(f"  {cron_line}")


def uninstall_cron():
    try:
        cur = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
        if cur.returncode != 0:
            print("Nessun crontab trovato.")
            return
        lines = cur.stdout.splitlines()
        keep = [l for l in lines
                if "daily_enrichment_pipeline.py" not in l
                and "Pipeline enrichment giornaliera" not in l]
        p = subprocess.Popen(["crontab", "-"], stdin=subprocess.PIPE, text=True)
        p.communicate(input="\n".join(keep) + "\n")
        print("Job cron rimosso." if p.returncode == 0 else "Errore rimozione cron.")
    except FileNotFoundError:
        print("'crontab' non disponibile.")


def main():
    parser = argparse.ArgumentParser(description="Pipeline di enrichment giornaliera")
    parser.add_argument("--category", action="append",
                        help="Filtra per categoria (ripetibile). Default: tutte.")
    parser.add_argument("--originals-only", action="store_true",
                        help="Esegui solo i download degli originali")
    parser.add_argument("--enrich-only", action="store_true",
                        help="Esegui solo gli step di enrichment/processing")
    parser.add_argument("--dry-run", action="store_true",
                        help="Mostra cosa verrebbe eseguito senza agire")
    parser.add_argument("--install-cron", action="store_true",
                        help="Installa il job cron giornaliero (06:00)")
    parser.add_argument("--uninstall-cron", action="store_true")
    args = parser.parse_args()

    if args.install_cron:
        install_cron()
        return 0
    if args.uninstall_cron:
        uninstall_cron()
        return 0

    categories = args.category if args.category else ["*"]
    kind_filter = None
    if args.originals_only:
        kind_filter = "download"
    elif args.enrich_only:
        kind_filter = "enrich"

    return run_pipeline(categories, kind_filter, args.dry_run)


if __name__ == "__main__":
    sys.exit(main())
