#!/usr/bin/env python3
"""Orchestratore delle pipeline di enrichment giornaliere.

Scarica gli originali per ogni categoria definita in
`scripts/enrichment/sources.json`, aggiorna i manifest per categoria,
esegue i post-processor (parsing XML, estratti SDO, enrichment report
scientifici, migrazioni database) e produce un report consolidato in
`logs/enrichment_<YYYY-MM-DD>.json`.

Usage:
    python scripts/run_daily_enrichment.py                    # tutte le categorie
    python scripts/run_daily_enrichment.py --only ania aifa  # solo alcune
    python scripts/run_daily_enrichment.py --skip istat      # tutte tranne una
    python scripts/run_daily_enrichment.py --list            # mostra categorie
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from enrichment.base import EnrichmentEngine, SourceDef  # noqa: E402
from enrichment.postprocess import POST_HOOKS  # noqa: E402


def setup_logging(log_dir: Path) -> Path:
    log_dir.mkdir(parents=True, exist_ok=True)
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    log_file = log_dir / f"enrichment_{today}.log"
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s | %(message)s",
        handlers=[logging.FileHandler(log_file, encoding="utf-8"), logging.StreamHandler()],
    )
    return log_file


def load_registry() -> dict:
    registry_path = REPO_ROOT / "scripts" / "enrichment" / "sources.json"
    with registry_path.open(encoding="utf-8") as f:
        return json.load(f)


def build_sources(category_cfg: dict) -> list[SourceDef]:
    out = []
    for item in category_cfg.get("sources", []):
        if item.get("skip_daily"):
            continue
        out.append(
            SourceDef(
                source_id=item["source_id"],
                url=item["url"],
                dest=item["dest"],
                title=item.get("title", ""),
                kind=item.get("kind", "pdf"),
                license=item.get("license", category_cfg.get("default_license", "")),
                landing_url=item.get("landing_url", ""),
                required=item.get("required", False),
                notes=item.get("notes", ""),
            )
        )
    return out


def run(categories: list[str], only: set[str] | None, skip: set[str]) -> dict:
    registry = load_registry()
    all_categories = list(registry["categories"].keys())
    if not categories:
        categories = all_categories

    log = logging.getLogger("enrichment.orchestrator")
    reports = []

    for cat in categories:
        if cat not in registry["categories"]:
            log.warning("Categoria sconosciuta: %s", cat)
            continue
        if only and cat not in only:
            continue
        if cat in skip:
            log.info("Saltata categoria: %s", cat)
            continue

        cfg = registry["categories"][cat]
        sources = build_sources(cfg)
        if not sources:
            log.info("Categoria %s senza sorgenti dirette — skip download", cat)
            # Eseguo comunque il post-hook se presente (es. ministero_salute)
            if cat in POST_HOOKS:
                log.info("[%s] Solo post-processor", cat)
                engine = EnrichmentEngine(cat, REPO_ROOT)
                report = engine.run([], POST_HOOKS[cat])
                reports.append(report.as_dict())
            continue

        engine = EnrichmentEngine(cat, REPO_ROOT)
        hook = POST_HOOKS.get(cat)
        log.info("=== Pipeline %s: %d sorgenti ===", cat, len(sources))
        report = engine.run(sources, hook)
        log.info(
            "[%s] dl=%d unchanged=%d failed=%d skipped=%d",
            cat, report.downloaded, report.unchanged, report.failed, report.skipped,
        )
        reports.append(report.as_dict())

    summary = {
        "run_at": datetime.now(timezone.utc).isoformat(),
        "categories_run": len(reports),
        "total_downloaded": sum(r["downloaded"] for r in reports),
        "total_unchanged": sum(r["unchanged"] for r in reports),
        "total_failed": sum(r["failed"] for r in reports),
        "reports": reports,
    }
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Enrichment giornaliero info_MIB")
    parser.add_argument("--only", nargs="*", default=None, help="Esegui solo queste categorie")
    parser.add_argument("--skip", nargs="*", default=[], help="Salta queste categorie")
    parser.add_argument("--list", action="store_true", help="Elenca categorie e esce")
    args = parser.parse_args()

    if args.list:
        reg = load_registry()
        for cat, cfg in reg["categories"].items():
            n = len([s for s in cfg.get("sources", []) if not s.get("skip_daily")])
            print(f"  {cat:22} {n:>3} sorgenti — {cfg.get('description','')[:80]}")
        return 0

    log_file = setup_logging(REPO_ROOT / "logs")
    only = set(args.only) if args.only else None
    skip = set(args.skip or [])

    summary = run([], only, skip)

    out_path = REPO_ROOT / "logs" / f"enrichment_{datetime.now(timezone.utc).strftime('%Y-%m-%d')}.json"
    out_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nReport: {out_path}")
    print(f"Log: {log_file}")
    print(f"Downloaded: {summary['total_downloaded']}  Unchanged: {summary['total_unchanged']}  Failed: {summary['total_failed']}")
    return 0 if summary["total_failed"] == 0 else 2


if __name__ == "__main__":
    sys.exit(main())
