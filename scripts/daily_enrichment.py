#!/usr/bin/env python3
"""
Orchestratore delle pipeline di enrichment giornaliere InfoMIB.

Esegue, per ogni categoria di documenti presente nel repository, la pipeline
corrispondente:
  - i passi di tipo "download" scaricano i DOCUMENTI/DATASET ORIGINALI (PDF, CSV,
    ...) dalle fonti ufficiali;
  - i passi di tipo "process" rigenerano gli estratti strutturati a partire dagli
    originali;
  - il passo "sources_update" verifica su tutte le fonti del catalogo se sono
    uscite nuove pubblicazioni.

Ogni pipeline è isolata: un errore su una categoria non blocca le altre. Al
termine viene salvato un report JSON in logs/.

Schedulazione: giornaliera via GitHub Actions (.github/workflows/daily-enrichment.yml).

Usage:
    python3 scripts/daily_enrichment.py                       # tutte le categorie
    python3 scripts/daily_enrichment.py --list                # elenca le pipeline
    python3 scripts/daily_enrichment.py --dry-run             # mostra cosa farebbe
    python3 scripts/daily_enrichment.py --category gimbe      # una sola categoria
    python3 scripts/daily_enrichment.py --category gimbe --category pdta
    python3 scripts/daily_enrichment.py --only-downloads      # solo i download originali
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
TODAY = datetime.now().strftime("%Y-%m-%d")
REPORT_FILE = os.path.join(LOGS_DIR, f"enrichment_report_{TODAY}.json")

DEFAULT_TIMEOUT = 1800  # 30 minuti per pipeline

# Registro delle pipeline di enrichment per categoria di documenti.
# type: "download" (scarica originali) | "process" (rigenera estratti) | "monitor"
PIPELINES = [
    {
        "category": "gimbe",
        "type": "download",
        "desc": "Report GIMBE sul SSN (PDF originali)",
        "cmd": ["download_gimbe_pdfs.py"],
    },
    {
        "category": "pdta",
        "type": "download",
        "desc": "PDTA nazionali e regionali (PDF originali)",
        "cmd": ["download_pdta.py", "--level", "all"],
    },
    {
        "category": "insurance",
        "type": "download",
        "desc": "Report ANIA - settore assicurativo (PDF originali)",
        "cmd": ["download_ania_reports.py"],
    },
    {
        "category": "scientific_reports",
        "type": "process",
        "desc": "Estratti report scientifici (ONS, società scientifiche, GIMBE, OASI, AIFA)",
        "cmd": ["enrich_scientific_reports_ons.py"],
    },
    {
        "category": "sdo",
        "type": "process",
        "desc": "Dataset SDO - schede dimissione ospedaliera",
        "cmd": ["extract_sdo_data.py"],
    },
    {
        "category": "istat_hfa",
        "type": "process",
        "desc": "Indicatori ISTAT Health for All (malattie croniche)",
        "cmd": ["analyze_hfa_chronic.py"],
    },
    {
        "category": "orphadata",
        "type": "process",
        "desc": "Malattie rare Orphanet (epidemiologia)",
        "cmd": ["parse_orphadata.py"],
    },
    {
        "category": "sources_update",
        "type": "monitor",
        "desc": "Controllo aggiornamenti su tutte le fonti del catalogo",
        "cmd": ["scheduler_check_updates.py", "--force"],
    },
]


def run_pipeline(pipeline, timeout, dry_run=False):
    """Esegue una singola pipeline come sottoprocesso isolato."""
    script = pipeline["cmd"][0]
    extra_args = pipeline["cmd"][1:]
    script_path = os.path.join(SCRIPTS_DIR, script)
    cmd = [sys.executable, script_path, *extra_args]

    result = {
        "category": pipeline["category"],
        "type": pipeline["type"],
        "description": pipeline["desc"],
        "command": " ".join([os.path.basename(sys.executable), script, *extra_args]),
        "started_at": datetime.now().isoformat(),
        "status": "unknown",
        "returncode": None,
        "duration_seconds": None,
        "output_tail": "",
        "error": None,
    }

    if not os.path.exists(script_path):
        result["status"] = "missing_script"
        result["error"] = f"Script non trovato: {script}"
        return result

    if dry_run:
        result["status"] = "dry_run"
        return result

    start = time.time()
    try:
        proc = subprocess.run(
            cmd,
            cwd=BASE_DIR,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        result["returncode"] = proc.returncode
        combined = (proc.stdout or "") + (proc.stderr or "")
        # Conserva solo la coda dell'output per contenere la dimensione del report
        result["output_tail"] = "\n".join(combined.strip().splitlines()[-25:])
        result["status"] = "ok" if proc.returncode == 0 else "failed"
    except subprocess.TimeoutExpired:
        result["status"] = "timeout"
        result["error"] = f"Timeout dopo {timeout}s"
    except Exception as e:  # robustezza: nessun errore deve fermare l'orchestratore
        result["status"] = "error"
        result["error"] = str(e)[:500]

    result["duration_seconds"] = round(time.time() - start, 1)
    return result


def main():
    parser = argparse.ArgumentParser(
        description="Orchestratore pipeline di enrichment giornaliere InfoMIB",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--list", action="store_true",
                        help="Elenca le pipeline disponibili ed esci")
    parser.add_argument("--dry-run", action="store_true",
                        help="Mostra le pipeline che verrebbero eseguite senza eseguirle")
    parser.add_argument("--category", action="append", dest="categories",
                        help="Esegui solo la/e categoria/e indicata/e (ripetibile)")
    parser.add_argument("--only-downloads", action="store_true",
                        help="Esegui solo i passi di download degli originali")
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT,
                        help=f"Timeout per pipeline in secondi (default: {DEFAULT_TIMEOUT})")
    args = parser.parse_args()

    if args.list:
        print("Pipeline di enrichment disponibili:\n")
        for p in PIPELINES:
            print(f"  [{p['type']:<8}] {p['category']:<18} {p['desc']}")
        return 0

    pipelines = PIPELINES
    if args.only_downloads:
        pipelines = [p for p in pipelines if p["type"] == "download"]
    if args.categories:
        wanted = set(args.categories)
        pipelines = [p for p in pipelines if p["category"] in wanted]
        unknown = wanted - {p["category"] for p in PIPELINES}
        if unknown:
            print(f"ATTENZIONE: categorie sconosciute ignorate: {', '.join(sorted(unknown))}")

    if not pipelines:
        print("Nessuna pipeline da eseguire.")
        return 0

    os.makedirs(LOGS_DIR, exist_ok=True)

    print("=" * 70)
    print(f"ENRICHMENT GIORNALIERO INFOMIB - {TODAY}")
    print("=" * 70)
    print(f"Pipeline da eseguire: {len(pipelines)}\n")

    results = []
    for i, pipeline in enumerate(pipelines, 1):
        print(f"[{i}/{len(pipelines)}] {pipeline['category']} "
              f"({pipeline['type']}) - {pipeline['desc']}")
        res = run_pipeline(pipeline, args.timeout, dry_run=args.dry_run)
        status = res["status"]
        dur = res.get("duration_seconds")
        suffix = f" ({dur}s)" if dur is not None else ""
        print(f"      -> {status}{suffix}")
        if res.get("error"):
            print(f"         {res['error']}")
        results.append(res)

    ok = sum(1 for r in results if r["status"] in ("ok", "dry_run"))
    failed = [r for r in results if r["status"] not in ("ok", "dry_run", "missing_script")]

    report = {
        "report_date": TODAY,
        "report_timestamp": datetime.now().isoformat(),
        "summary": {
            "total": len(results),
            "ok": ok,
            "failed": len(failed),
            "missing_script": sum(1 for r in results if r["status"] == "missing_script"),
        },
        "results": results,
    }

    if not args.dry_run:
        with open(REPORT_FILE, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"\n{'=' * 70}")
    print(f"RISULTATO: {ok}/{len(results)} pipeline ok, {len(failed)} con problemi")
    if failed:
        for r in failed:
            print(f"  [{r['status']}] {r['category']}: {r.get('error') or 'vedi output_tail'}")
    if not args.dry_run:
        print(f"Report: {REPORT_FILE}")
    print(f"{'=' * 70}")

    # Exit 0 anche in presenza di fallimenti su singole categorie: il report
    # documenta lo stato. Ritorna non-zero solo se TUTTE le pipeline falliscono.
    return 0 if ok > 0 or not results else 1


if __name__ == "__main__":
    sys.exit(main())
