"""
Componenti condivisi dalle pipeline di enrichment.

- `PipelineResource` / `Pipeline`: descrivono dichiarativamente cosa scaricare.
- `download_resource`: esegue il download con retry, backoff e rate limiting,
  preservando il file originale e aggiornando un manifest JSON con metadati
  (sha256, size, fetched_at, http_headers salienti).
- `run_pipeline`: esegue una pipeline completa e restituisce un dict con
  l'esito (ok / skipped / failed) per ogni risorsa.
- `is_due`: decide se una risorsa va riscaricata oggi in base a `frequency`
  e all'ultima data di fetch registrata nel manifest.
"""

from __future__ import annotations

import dataclasses
import hashlib
import json
import logging
import os
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Callable, Iterable


# === Costanti ===

DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (compatible; InfoMIB-Enrichment/1.0; "
    "+https://github.com/giumar11/info_MIB)"
)
DEFAULT_TIMEOUT = 120
DEFAULT_MAX_RETRIES = 3
DEFAULT_RATE_LIMIT_SECONDS = 1.5

FREQUENCY_DAYS = {
    "continuous": 1,
    "daily": 1,
    "weekly": 7,
    "monthly": 30,
    "quarterly": 90,
    "annual": 180,          # controlla 2 volte l'anno
    "biennial": 365,
    "periodic": 30,
    "static": 365,
}


# === Modelli dichiarativi ===

@dataclass
class PipelineResource:
    """Una singola risorsa da scaricare (PDF, XLSX, ZIP, CSV, ecc.)."""

    resource_id: str
    url: str
    filename: str
    title: str = ""
    year: int | None = None
    frequency: str = "annual"
    category: str = ""
    subcategory: str = ""
    # Sotto-cartella rispetto a `pipeline.dest_dir`.
    subdir: str = ""
    # Se True, il file viene SEMPRE riscaricato anche se presente.
    force: bool = False
    # Dimensione minima attesa (byte) per considerarlo valido.
    min_size_bytes: int = 1000
    notes: str = ""


@dataclass
class Pipeline:
    """Definisce una categoria di enrichment (es. AIFA, ANIA, GIMBE...)."""

    pipeline_id: str
    name: str
    dest_dir: Path
    resources: list[PipelineResource]
    description: str = ""
    # Callback opzionale: invocato dopo il download di successo della risorsa.
    # Firma: fn(resource, filepath, manifest_entry) -> None.
    post_process: Callable[[PipelineResource, Path, dict], None] | None = None


# === Manifest ===

def load_manifest(manifest_path: Path) -> dict:
    if manifest_path.exists():
        with open(manifest_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"generated_at": None, "files": {}}


def save_manifest(manifest_path: Path, manifest: dict) -> None:
    manifest["generated_at"] = datetime.now().isoformat(timespec="seconds")
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2, sort_keys=True)


def is_due(resource: PipelineResource, prev_entry: dict | None) -> bool:
    """Decide se la risorsa va riscaricata oggi."""
    if resource.force:
        return True
    if not prev_entry or prev_entry.get("status") != "ok":
        return True
    fetched_at = prev_entry.get("fetched_at")
    if not fetched_at:
        return True
    try:
        last = datetime.fromisoformat(fetched_at)
    except ValueError:
        return True
    threshold = FREQUENCY_DAYS.get(resource.frequency, 30)
    return (datetime.now() - last) >= timedelta(days=threshold)


# === Download ===

def _sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def download_resource(
    resource: PipelineResource,
    dest_dir: Path,
    logger: logging.Logger,
    user_agent: str = DEFAULT_USER_AGENT,
    timeout: int = DEFAULT_TIMEOUT,
    max_retries: int = DEFAULT_MAX_RETRIES,
) -> dict:
    """
    Scarica una singola risorsa. Preserva il file originale nel filesystem.

    Returns un dict con:
      status:        ok | failed | skipped
      path:          path relativo al dest_dir
      size_bytes:    int
      sha256:        hex string
      http_status:   int (ultimo ricevuto)
      fetched_at:    ISO-8601 timestamp
      error:         stringa errore (se presente)
    """
    subdir = dest_dir / resource.subdir if resource.subdir else dest_dir
    subdir.mkdir(parents=True, exist_ok=True)
    filepath = subdir / resource.filename

    entry: dict[str, Any] = {
        "resource_id": resource.resource_id,
        "url": resource.url,
        "title": resource.title,
        "year": resource.year,
        "category": resource.category,
        "subcategory": resource.subcategory,
        "frequency": resource.frequency,
        "path": str(filepath.relative_to(dest_dir)) if dest_dir in filepath.parents or filepath.parent == dest_dir else str(filepath),
        "status": "failed",
        "size_bytes": 0,
        "sha256": None,
        "http_status": None,
        "fetched_at": None,
        "error": None,
    }

    headers = {
        "User-Agent": user_agent,
        "Accept": "application/pdf,application/octet-stream,*/*",
    }

    last_error = None
    for attempt in range(1, max_retries + 1):
        try:
            req = urllib.request.Request(resource.url, headers=headers)
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                entry["http_status"] = resp.status
                data = resp.read()
                if len(data) < resource.min_size_bytes:
                    last_error = f"File troppo piccolo ({len(data)} byte < {resource.min_size_bytes})"
                    logger.warning(f"  [{resource.resource_id}] {last_error}")
                else:
                    with open(filepath, "wb") as f:
                        f.write(data)
                    entry["status"] = "ok"
                    entry["size_bytes"] = len(data)
                    entry["sha256"] = hashlib.sha256(data).hexdigest()
                    entry["fetched_at"] = datetime.now().isoformat(timespec="seconds")
                    logger.info(
                        f"  [{resource.resource_id}] OK {filepath.name} "
                        f"({len(data) / 1024:.0f} KB)"
                    )
                    return entry
        except urllib.error.HTTPError as e:
            entry["http_status"] = e.code
            last_error = f"HTTP {e.code}: {e.reason}"
            logger.warning(f"  [{resource.resource_id}] attempt {attempt}/{max_retries} {last_error}")
            # 403/404 sono permanenti: non retry
            if e.code in (403, 404, 410):
                break
        except urllib.error.URLError as e:
            last_error = f"URLError: {e.reason}"
            logger.warning(f"  [{resource.resource_id}] attempt {attempt}/{max_retries} {last_error}")
        except (TimeoutError, OSError) as e:
            last_error = f"{type(e).__name__}: {e}"
            logger.warning(f"  [{resource.resource_id}] attempt {attempt}/{max_retries} {last_error}")

        if attempt < max_retries:
            wait = min(2 ** attempt, 30)
            time.sleep(wait)

    entry["error"] = last_error
    return entry


# === Runner ===

def run_pipeline(
    pipeline: Pipeline,
    logger: logging.Logger,
    force: bool = False,
    rate_limit_seconds: float = DEFAULT_RATE_LIMIT_SECONDS,
    dry_run: bool = False,
) -> dict:
    """Esegue una pipeline completa scaricando solo le risorse dovute."""
    dest_dir = Path(pipeline.dest_dir)
    dest_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = dest_dir / "manifest.json"
    manifest = load_manifest(manifest_path)
    files_manifest: dict[str, dict] = manifest.setdefault("files", {})

    summary = {
        "pipeline_id": pipeline.pipeline_id,
        "name": pipeline.name,
        "dest_dir": str(dest_dir),
        "total": len(pipeline.resources),
        "ok": 0,
        "skipped": 0,
        "failed": 0,
        "not_due": 0,
        "resources": [],
    }

    logger.info(f"[{pipeline.pipeline_id}] {pipeline.name} -> {dest_dir}")
    logger.info(f"  {len(pipeline.resources)} risorse")

    for i, res in enumerate(pipeline.resources, 1):
        prev = files_manifest.get(res.resource_id)
        if not force and not is_due(res, prev):
            summary["not_due"] += 1
            summary["resources"].append({
                "resource_id": res.resource_id,
                "status": "not_due",
                "last_fetched": prev.get("fetched_at") if prev else None,
            })
            continue

        if dry_run:
            logger.info(f"  [DRY-RUN] would fetch [{res.resource_id}] {res.url}")
            summary["resources"].append({
                "resource_id": res.resource_id,
                "status": "dry_run",
            })
            continue

        entry = download_resource(res, dest_dir, logger)
        files_manifest[res.resource_id] = entry
        summary["resources"].append(entry)

        if entry["status"] == "ok":
            summary["ok"] += 1
            if pipeline.post_process:
                try:
                    pipeline.post_process(res, dest_dir / entry["path"], entry)
                except Exception as e:
                    logger.exception(f"post_process fallito per {res.resource_id}: {e}")
        else:
            summary["failed"] += 1

        if i < len(pipeline.resources):
            time.sleep(rate_limit_seconds)

    if not dry_run:
        save_manifest(manifest_path, manifest)
    logger.info(
        f"[{pipeline.pipeline_id}] done - ok={summary['ok']} "
        f"not_due={summary['not_due']} failed={summary['failed']}"
    )
    return summary
