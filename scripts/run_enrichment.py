#!/usr/bin/env python3
"""
Orchestratore delle pipeline di enrichment giornaliere del repository info_MIB.

Esegue, per ogni categoria di documenti presente nel repository, la pipeline
corrispondente:

  * DOWNLOAD ORIGINALI  -> scarica i report / dataset ORIGINALI dalle fonti
                           istituzionali (PDF, XML, CSV) - non solo estratti.
  * RIGENERAZIONE       -> ricostruisce i dataset processati (JSON/CSV) a
                           partire dai dati grezzi.
  * CONTROLLO UPDATE    -> verifica se le fonti hanno pubblicato nuove versioni.

Ogni step viene eseguito in modo indipendente: il fallimento (es. di rete) di
una pipeline non blocca le altre. Al termine viene scritto un report in
logs/enrichment_run_YYYY-MM-DD.json e stampato un riepilogo.

Usage:
    python3 scripts/run_enrichment.py                     # tutte le categorie
    python3 scripts/run_enrichment.py --category ania      # solo una categoria
    python3 scripts/run_enrichment.py --list               # elenca le pipeline
    python3 scripts/run_enrichment.py --only-downloads     # solo i download originali
    python3 scripts/run_enrichment.py --dry-run            # mostra senza eseguire

Schedulazione: eseguito ogni giorno da .github/workflows/enrichment-daily.yml
"""

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS_DIR = os.path.join(BASE_DIR, "scripts")
LOGS_DIR = os.path.join(BASE_DIR, "logs")

PY = sys.executable or "python3"

# Tipi di step
DOWNLOAD = "download_original"   # scarica report/dataset originali dalle fonti
REGENERATE = "regenerate"        # rigenera i dataset processati
CHECK = "check"                  # controlla aggiornamenti delle fonti

# =============================================================================
# REGISTRY DELLE PIPELINE PER CATEGORIA DI DOCUMENTI
# =============================================================================
# `fetches_originals`: True se lo step carica i report/dataset ORIGINALI.
# Ordine: prima i download degli originali, poi le rigenerazioni, infine il
# controllo aggiornamenti (che segnala nuove pubblicazioni a monte per le
# categorie ancora prive di un downloader dedicato).
PIPELINES = [
    {
        "id": "gimbe",
        "category": "gimbe",
        "description": "Report GIMBE (Rapporti SSN + Osservatorio) - PDF originali",
        "kind": DOWNLOAD,
        "fetches_originals": True,
        "daily": True,
        "cmd": [PY, "scripts/download_gimbe_pdfs.py"],
    },
    {
        "id": "pdta",
        "category": "pdta",
        "description": "PDTA nazionali/regionali/locali - PDF originali",
        "kind": DOWNLOAD,
        "fetches_originals": True,
        "daily": True,
        "cmd": [PY, "scripts/download_pdta.py", "--level", "all"],
    },
    {
        "id": "ania",
        "category": "ania",
        "description": "Report ANIA (assicurativo, salute e welfare integrativo) - PDF originali",
        "kind": DOWNLOAD,
        "fetches_originals": True,
        "daily": True,
        "cmd": [PY, "scripts/download_ania_reports.py"],
    },
    {
        "id": "scientific_reports",
        "category": "scientific_reports",
        "description": "ONS, societa scientifiche IT/EU, OASI Bocconi, AIFA, GIMBE - dataset strutturati",
        "kind": REGENERATE,
        "fetches_originals": False,
        "daily": True,
        "cmd": [PY, "scripts/enrich_scientific_reports_ons.py"],
    },
    {
        "id": "sdo",
        "category": "ministero_salute",
        "description": "Riepiloghi SDO, PDTA multidisciplinari, segmentazione popolazione",
        "kind": REGENERATE,
        "fetches_originals": False,
        "daily": True,
        "cmd": [PY, "scripts/extract_sdo_data.py"],
    },
    {
        "id": "malattie_rare",
        "category": "rare_diseases",
        "description": "Malattie rare da Orphadata (epidemiologia + indice complessita)",
        "kind": REGENERATE,
        "fetches_originals": False,
        "daily": True,
        "cmd": [PY, "scripts/parse_orphadata.py"],
    },
    {
        "id": "istat_hfa",
        "category": "istat",
        "description": "Analisi ISTAT Health for All - patologie croniche multispecialistiche",
        "kind": REGENERATE,
        "fetches_originals": False,
        "daily": True,
        "cmd": [PY, "scripts/analyze_hfa_chronic.py"],
    },
    {
        "id": "update_check",
        "category": "all",
        "description": "Controllo aggiornamenti di tutte le fonti del catalogo",
        "kind": CHECK,
        "fetches_originals": False,
        "daily": True,
        "cmd": [PY, "scripts/scheduler_check_updates.py", "--force"],
    },
    {
        # Artefatto di import DB (SQL/NoSQL): non fa parte dell'enrichment
        # giornaliero dei documenti (esclusa da default per evitare churn di
        # timestamp). Eseguibile su richiesta: --id migration oppure --all.
        "id": "migration",
        "category": "migration",
        "description": "Preparazione dati pronti per database (SQL/NoSQL) - on demand",
        "kind": REGENERATE,
        "fetches_originals": False,
        "daily": False,
        "cmd": [PY, "scripts/migrate_to_database.py"],
    },
]


def list_pipelines():
    print("=" * 78)
    print("PIPELINE DI ENRICHMENT DISPONIBILI")
    print("=" * 78)
    for p in PIPELINES:
        orig = "  [ORIGINALI]" if p["fetches_originals"] else ""
        sched = "giornaliera" if p.get("daily", True) else "on-demand"
        print(f"\n  {p['id']:20s} ({p['kind']}, {sched}){orig}")
        print(f"    categoria: {p['category']}")
        print(f"    {p['description']}")
        print(f"    cmd: {' '.join(p['cmd'])}")
    print("\n" + "=" * 78)
    print(f"Totale pipeline: {len(PIPELINES)}")
    print("=" * 78)


def run_step(pipeline, timeout, dry_run):
    cmd = pipeline["cmd"]
    printable = " ".join(cmd)
    print(f"\n{'-' * 78}")
    print(f">>> [{pipeline['id']}] {pipeline['description']}")
    print(f"    $ {printable}")

    if dry_run:
        print("    (dry-run: non eseguito)")
        return {"id": pipeline["id"], "status": "dry_run", "returncode": None,
                "duration_s": 0, "output_tail": []}

    start = time.time()
    try:
        proc = subprocess.run(
            cmd, cwd=BASE_DIR, capture_output=True, text=True, timeout=timeout,
        )
        duration = round(time.time() - start, 1)
        combined = (proc.stdout or "") + (proc.stderr or "")
        tail = [ln for ln in combined.splitlines() if ln.strip()][-12:]
        status = "ok" if proc.returncode == 0 else "warn"
        print(f"    -> exit {proc.returncode} in {duration}s ({status})")
        for ln in tail[-4:]:
            print(f"       {ln}")
        return {"id": pipeline["id"], "status": status,
                "returncode": proc.returncode, "duration_s": duration,
                "output_tail": tail}
    except subprocess.TimeoutExpired:
        duration = round(time.time() - start, 1)
        print(f"    -> TIMEOUT dopo {timeout}s")
        return {"id": pipeline["id"], "status": "timeout", "returncode": None,
                "duration_s": duration, "output_tail": []}
    except Exception as e:  # pragma: no cover - safety net
        duration = round(time.time() - start, 1)
        print(f"    -> ERRORE orchestratore: {e}")
        return {"id": pipeline["id"], "status": "error", "returncode": None,
                "duration_s": duration, "output_tail": [str(e)]}


def main():
    parser = argparse.ArgumentParser(
        description="Orchestratore pipeline di enrichment giornaliere info_MIB",
    )
    parser.add_argument("--category", action="append", dest="categories",
                        help="Esegui solo la/le categoria/e indicate (ripetibile)")
    parser.add_argument("--id", action="append", dest="ids",
                        help="Esegui solo la/le pipeline con questo id (ripetibile)")
    parser.add_argument("--only-downloads", action="store_true",
                        help="Esegui solo i download dei report/dataset originali")
    parser.add_argument("--all", action="store_true",
                        help="Includi anche le pipeline non giornaliere (es. migration)")
    parser.add_argument("--list", action="store_true",
                        help="Elenca le pipeline disponibili ed esci")
    parser.add_argument("--dry-run", action="store_true",
                        help="Mostra cosa verrebbe eseguito senza eseguirlo")
    parser.add_argument("--timeout", type=int, default=1800,
                        help="Timeout per singola pipeline in secondi (default 1800)")
    args = parser.parse_args()

    if args.list:
        list_pipelines()
        return 0

    explicit = bool(args.categories or args.ids)
    selected = list(PIPELINES)
    # Per default esegue solo le pipeline giornaliere; una selezione esplicita
    # (--category/--id) o --all puo' includere anche quelle non giornaliere.
    if not explicit and not args.all:
        selected = [p for p in selected if p.get("daily", True)]
    if args.only_downloads:
        selected = [p for p in selected if p["kind"] == DOWNLOAD]
    if args.categories:
        wanted = set(args.categories)
        selected = [p for p in selected if p["category"] in wanted]
    if args.ids:
        wanted = set(args.ids)
        selected = [p for p in selected if p["id"] in wanted]

    if not selected:
        print("Nessuna pipeline corrisponde ai filtri indicati.")
        return 1

    os.makedirs(LOGS_DIR, exist_ok=True)
    today = datetime.now().strftime("%Y-%m-%d")

    print("=" * 78)
    print(f"ENRICHMENT GIORNALIERO - {today}")
    print(f"Pipeline da eseguire: {len(selected)}")
    print("=" * 78)

    results = []
    for p in selected:
        results.append(run_step(p, args.timeout, args.dry_run))

    # Riepilogo
    counts = {}
    for r in results:
        counts[r["status"]] = counts.get(r["status"], 0) + 1

    report = {
        "run_date": today,
        "run_timestamp": datetime.now().isoformat(),
        "pipelines_run": len(results),
        "summary": counts,
        "results": results,
    }

    report_path = os.path.join(LOGS_DIR, f"enrichment_run_{today}.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print("\n" + "=" * 78)
    print("RIEPILOGO ENRICHMENT")
    print("=" * 78)
    for r in results:
        print(f"  [{r['status']:8s}] {r['id']:20s} ({r['duration_s']}s)")
    print(f"\n  Stati: {counts}")
    print(f"  Report: {report_path}")
    print("=" * 78)

    # L'orchestratore non fallisce per errori di rete/download delle singole
    # pipeline (attesi in ambienti con egress limitato): esce != 0 solo se
    # nessuna pipeline e' stata completata.
    completed = counts.get("ok", 0) + counts.get("warn", 0)
    return 0 if (args.dry_run or completed > 0) else 1


if __name__ == "__main__":
    sys.exit(main())
