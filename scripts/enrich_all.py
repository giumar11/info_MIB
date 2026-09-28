#!/usr/bin/env python3
"""
Orchestratore della pipeline di enrichment giornaliera per info_MIB.

Acquisisce i **dataset e i report ORIGINALI** di tutte le categorie di documenti
del repository (non solo gli estratti processati) e, opzionalmente, rigenera gli
estratti processati a partire dagli originali.

Fasi:
  1. Download catalog-driven: per ogni fonte in sources_catalog.csv il cui `url`
     punta a un file scaricabile (.pdf/.csv/.xml/.zip/.xlsx/.xls/.json/.dbf),
     scarica l'originale in `file_paths_in_repo` se mancante.
  2. Scraper specializzati per fonti multi-file:
       - GIMBE   -> scripts/download_gimbe_pdfs.py
       - PDTA    -> scripts/download_pdta.py
       - ANIA    -> scripts/download_ania.py   (settore assicurativo)
  3. (opzionale, --process) Rigenerazione degli estratti processati dagli
     originali (parse_orphadata, extract_sdo_data, ...).

Caratteristiche:
  - La verifica dei certificati resta ATTIVA (default sicuro).
  - Nessun passo fa fallire l'intera pipeline: gli errori vengono raccolti e
    riportati nel log JSON, l'orchestratore continua.
  - Pensato per girare quotidianamente su GitHub Actions (rete aperta). Nelle
    sessioni cloud con proxy egress ristretto i download falliranno in modo
    controllato.

Uso:
    python3 scripts/enrich_all.py                    # tutte le categorie
    python3 scripts/enrich_all.py --dry-run
    python3 scripts/enrich_all.py --category insurance
    python3 scripts/enrich_all.py --only-catalog     # salta gli scraper
    python3 scripts/enrich_all.py --process          # rigenera anche i processed
    python3 scripts/enrich_all.py --force            # ri-scarica gli originali
"""

import argparse
import csv
import hashlib
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime
from urllib.parse import urlparse

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CATALOG_PATH = os.path.join(BASE_DIR, "sources_catalog.csv")
SCRIPTS_DIR = os.path.join(BASE_DIR, "scripts")
LOGS_DIR = os.path.join(BASE_DIR, "logs")

DOWNLOADABLE_EXT = (".pdf", ".csv", ".xml", ".zip", ".xlsx", ".xls", ".dbf")
REQUEST_TIMEOUT = 120
MAX_RETRIES = 3
RATE_LIMIT_SECONDS = 1.5
USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)

# Scraper specializzati: (script, categorie catalogo coperte)
SCRAPERS = [
    ("download_gimbe_pdfs.py", {"analysis", "finance"}),
    ("download_pdta.py", {"pdta"}),
    ("download_ania.py", {"insurance"}),
]

# Passi opzionali di rigenerazione degli estratti processati dagli originali.
PROCESSORS = [
    "parse_orphadata.py",
    "extract_sdo_data.py",
    "analyze_hfa_chronic.py",
    "enrich_scientific_reports_ons.py",
    "migrate_to_database.py",
]


def load_catalog():
    with open(CATALOG_PATH, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def is_downloadable(url):
    if not url:
        return False
    path = urlparse(url).path.lower()
    return path.endswith(DOWNLOADABLE_EXT)


def dest_for(source):
    """Determina il percorso di destinazione dell'originale per una fonte."""
    fpath = (source.get("file_paths_in_repo") or "").split(";")[0].strip()
    url = source["url"]
    fname = os.path.basename(urlparse(url).path) or f"{source['source_id']}.bin"
    if not fpath:
        # fallback: cartella per categoria
        return os.path.join(BASE_DIR, "datasets", "raw", source.get("category", "misc"), fname)
    abs_fpath = os.path.join(BASE_DIR, fpath)
    if fpath.endswith("/") or os.path.isdir(abs_fpath):
        return os.path.join(abs_fpath, fname)
    # e' un percorso file: se manca l'estensione, trattalo come cartella
    if os.path.splitext(fpath)[1]:
        return abs_fpath
    return os.path.join(abs_fpath, fname)


def download(url, dest, dry_run=False, force=False):
    result = {"url": url, "dest": os.path.relpath(dest, BASE_DIR)}
    if dry_run:
        result["status"] = "dry_run"
        print(f"    [DRY RUN] {url} -> {result['dest']}")
        return result
    if not force and os.path.exists(dest) and os.path.getsize(dest) > 1000:
        result["status"] = "exists"
        result["downloaded"] = False
        print(f"    [SKIP] gia' presente: {os.path.basename(dest)}")
        return result

    os.makedirs(os.path.dirname(dest), exist_ok=True)
    req = urllib.request.Request(url, headers={
        "User-Agent": USER_AGENT, "Accept": "application/pdf,*/*"})
    for attempt in range(MAX_RETRIES):
        try:
            # Verifica certificati ATTIVA (contesto di default).
            with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as resp:
                data = resp.read()
            if len(data) < 1000:
                print(f"    [WARN] file piccolo ({len(data)} B): {url}")
            with open(dest, "wb") as f:
                f.write(data)
            result.update(status="ok", downloaded=True, size_bytes=len(data),
                          sha256=hashlib.sha256(data).hexdigest())
            print(f"    [OK] {os.path.basename(dest)} ({len(data)} B)")
            return result
        except urllib.error.HTTPError as e:
            print(f"    [WARN] HTTP {e.code}: {url}")
            if e.code in (403, 404, 410):
                result["status"] = f"http_{e.code}"
                return result
        except (urllib.error.URLError, OSError) as e:
            print(f"    [WARN] tentativo {attempt + 1}/{MAX_RETRIES}: {e}")
        if attempt < MAX_RETRIES - 1:
            time.sleep(2 ** (attempt + 1))
    result["status"] = "failed"
    return result


def run_catalog_downloads(catalog, category, dry_run, force):
    print("\n" + "=" * 70)
    print("  FASE 1: DOWNLOAD ORIGINALI (catalog-driven)")
    print("=" * 70)
    results = []
    targets = [s for s in catalog if is_downloadable(s["url"])]
    if category:
        targets = [s for s in targets if s.get("category") == category]
    print(f"Fonti con file diretto scaricabile: {len(targets)}")
    for i, source in enumerate(targets, 1):
        print(f"\n[{i}/{len(targets)}] [{source['source_id']}] {source['title'][:60]}")
        dest = dest_for(source)
        res = download(source["url"], dest, dry_run=dry_run, force=force)
        res["source_id"] = source["source_id"]
        res["category"] = source.get("category", "")
        results.append(res)
        if not dry_run and i < len(targets):
            time.sleep(RATE_LIMIT_SECONDS)
    return results


def run_script(script, extra_args=None):
    path = os.path.join(SCRIPTS_DIR, script)
    if not os.path.exists(path):
        return {"script": script, "status": "missing"}
    cmd = [sys.executable, path] + (extra_args or [])
    print(f"\n>>> {' '.join(cmd)}")
    try:
        proc = subprocess.run(cmd, cwd=BASE_DIR, timeout=1800)
        return {"script": script, "status": "ok" if proc.returncode == 0 else "nonzero_exit",
                "returncode": proc.returncode}
    except subprocess.TimeoutExpired:
        return {"script": script, "status": "timeout"}
    except Exception as e:  # noqa: BLE001 - la pipeline non deve fermarsi
        return {"script": script, "status": "error", "error": str(e)[:200]}


def run_scrapers(category, dry_run, force):
    print("\n" + "=" * 70)
    print("  FASE 2: SCRAPER SPECIALIZZATI (multi-file)")
    print("=" * 70)
    results = []
    for script, cats in SCRAPERS:
        if category and category not in cats:
            print(f"  [skip] {script} (categoria != {category})")
            continue
        args = []
        if dry_run:
            args.append("--dry-run")
        if force and script != "download_pdta.py":  # download_pdta non ha --force
            args.append("--force")
        results.append(run_script(script, args))
    return results


def run_processors(dry_run):
    print("\n" + "=" * 70)
    print("  FASE 3: RIGENERAZIONE ESTRATTI PROCESSATI (dagli originali)")
    print("=" * 70)
    if dry_run:
        print("  [DRY RUN] salto l'esecuzione dei processori")
        return [{"script": s, "status": "dry_run"} for s in PROCESSORS]
    results = []
    for script in PROCESSORS:
        results.append(run_script(script))
    return results


def main():
    parser = argparse.ArgumentParser(description="Pipeline di enrichment info_MIB")
    parser.add_argument("--dry-run", action="store_true", help="Non scarica/esegue nulla")
    parser.add_argument("--category", type=str, default=None,
                        help="Limita a una categoria del catalogo (es. insurance, pdta)")
    parser.add_argument("--only-catalog", action="store_true",
                        help="Esegui solo la Fase 1 (download originali da catalogo)")
    parser.add_argument("--process", action="store_true",
                        help="Esegui anche la Fase 3 (rigenerazione estratti)")
    parser.add_argument("--force", action="store_true",
                        help="Ri-scarica gli originali anche se presenti")
    args = parser.parse_args()

    started = datetime.now()
    print("=" * 70)
    print("  PIPELINE DI ENRICHMENT info_MIB")
    print(f"  Avvio: {started.isoformat(timespec='seconds')}")
    if args.category:
        print(f"  Categoria: {args.category}")
    print("=" * 70)

    catalog = load_catalog()
    summary = {
        "run_timestamp": started.isoformat(),
        "category_filter": args.category,
        "dry_run": args.dry_run,
        "catalog_downloads": [],
        "scrapers": [],
        "processors": [],
    }

    summary["catalog_downloads"] = run_catalog_downloads(
        catalog, args.category, args.dry_run, args.force)

    if not args.only_catalog:
        summary["scrapers"] = run_scrapers(args.category, args.dry_run, args.force)

    if args.process:
        summary["processors"] = run_processors(args.dry_run)

    # Riepilogo
    dl = summary["catalog_downloads"]
    ok = [r for r in dl if r.get("status") == "ok"]
    exists = [r for r in dl if r.get("status") == "exists"]
    failed = [r for r in dl if r.get("status") not in ("ok", "exists", "dry_run")]
    summary["totals"] = {
        "catalog_targets": len(dl),
        "downloaded_new": len(ok),
        "already_present": len(exists),
        "failed": len(failed),
    }

    if not args.dry_run:
        os.makedirs(LOGS_DIR, exist_ok=True)
        log_path = os.path.join(LOGS_DIR, f"enrichment_{started.strftime('%Y-%m-%d')}.json")
        with open(log_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        print(f"\nLog salvato: {log_path}")

    print("\n" + "=" * 70)
    print("  RIEPILOGO ENRICHMENT")
    print("=" * 70)
    print(f"  Target catalogo:     {summary['totals']['catalog_targets']}")
    print(f"  Scaricati (nuovi):   {summary['totals']['downloaded_new']}")
    print(f"  Gia' presenti:       {summary['totals']['already_present']}")
    print(f"  Falliti:             {summary['totals']['failed']}")
    if failed:
        print("\n  Download falliti:")
        for r in failed:
            print(f"    - [{r.get('source_id')}] {r.get('status')}: {r['url'][:70]}")
    print("=" * 70)
    return 0


if __name__ == "__main__":
    sys.exit(main())
