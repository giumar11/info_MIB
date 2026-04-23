"""Motore generico di download e manifest per le pipeline di enrichment.

Principi:
- Ogni categoria possiede una lista di `SourceDef` (URL diretto al file ORIGINALE
  + destinazione relativa a datasets/raw/<categoria>/).
- Il motore effettua HTTP GET con If-Modified-Since / If-None-Match quando il
  manifest contiene metadata precedenti, sfruttando il 304 per evitare
  scaricamenti ridondanti.
- SHA256 viene calcolato su ogni file e confrontato con la versione precedente
  per rilevare cambi di contenuto indipendentemente dagli header.
- Errori di rete non interrompono l'intera pipeline: vengono loggati e inclusi
  nel report finale.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Iterable

try:
    import requests
except ImportError as e:  # pragma: no cover
    raise SystemExit("Il pacchetto 'requests' è richiesto (pip install -r requirements.txt)") from e


USER_AGENT = "info-MIB-enrichment/1.0 (+https://github.com/giumar11/info_mib)"
DEFAULT_TIMEOUT = 60
MAX_RETRIES = 4
RETRY_BACKOFF_BASE = 2.0


@dataclass
class SourceDef:
    """Descrive una singola risorsa scaricabile."""

    source_id: str
    url: str
    dest: str  # Relativo a datasets/raw/<category>/
    title: str = ""
    kind: str = "pdf"  # pdf | json | csv | xml | zip | html
    license: str = ""
    landing_url: str = ""
    required: bool = False  # Se True, il fallimento viene considerato errore
    notes: str = ""


@dataclass
class DownloadResult:
    source_id: str
    url: str
    path: str
    status: str  # downloaded | unchanged | skipped | failed
    http_status: int | None = None
    bytes: int = 0
    sha256: str = ""
    etag: str = ""
    last_modified: str = ""
    error: str = ""
    fetched_at: str = ""


@dataclass
class PipelineReport:
    category: str
    started_at: str
    finished_at: str
    downloaded: int = 0
    unchanged: int = 0
    skipped: int = 0
    failed: int = 0
    results: list[DownloadResult] = field(default_factory=list)
    post_processed: list[str] = field(default_factory=list)
    error: str = ""

    def as_dict(self) -> dict:
        d = asdict(self)
        d["results"] = [asdict(r) for r in self.results]
        return d


def _sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


class EnrichmentEngine:
    """Scarica una lista di `SourceDef` in datasets/raw/<category>/ aggiornando il manifest."""

    def __init__(
        self,
        category: str,
        repo_root: Path,
        logger: logging.Logger | None = None,
        session: requests.Session | None = None,
    ) -> None:
        self.category = category
        self.repo_root = repo_root
        self.raw_dir = repo_root / "datasets" / "raw" / category
        self.processed_dir = repo_root / "datasets" / "processed"
        self.manifest_path = self.raw_dir / "download_manifest.json"
        self.logger = logger or logging.getLogger(f"enrichment.{category}")
        self.session = session or requests.Session()
        self.session.headers.setdefault("User-Agent", USER_AGENT)

    # ---------------- manifest ----------------
    def _load_manifest(self) -> dict:
        if not self.manifest_path.exists():
            return {"category": self.category, "entries": {}}
        try:
            return json.loads(self.manifest_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as e:
            self.logger.warning("Manifest non leggibile (%s), riparto da zero", e)
            return {"category": self.category, "entries": {}}

    def _save_manifest(self, manifest: dict) -> None:
        manifest["updated_at"] = datetime.now(timezone.utc).isoformat()
        self.manifest_path.parent.mkdir(parents=True, exist_ok=True)
        self.manifest_path.write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=False),
            encoding="utf-8",
        )

    # ---------------- HTTP ----------------
    def _http_get(
        self, url: str, headers: dict, dest_path: Path
    ) -> tuple[int, dict, Path | None, str]:
        """Esegue una GET con retry e scrive il body su file temporaneo.

        Ritorna (status_code, response_headers, tmp_path_or_None, error_message).
        Il tmp_path è None se 304 o errore.
        """
        last_error = ""
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                with self.session.get(
                    url, headers=headers, timeout=DEFAULT_TIMEOUT, stream=True, allow_redirects=True
                ) as resp:
                    if resp.status_code == 304:
                        return resp.status_code, dict(resp.headers), None, ""
                    resp.raise_for_status()
                    tmp = dest_path.with_suffix(dest_path.suffix + ".part")
                    tmp.parent.mkdir(parents=True, exist_ok=True)
                    with tmp.open("wb") as f:
                        for chunk in resp.iter_content(chunk_size=1 << 16):
                            if chunk:
                                f.write(chunk)
                    return resp.status_code, dict(resp.headers), tmp, ""
            except requests.RequestException as e:
                last_error = str(e)
                if attempt < MAX_RETRIES:
                    wait = RETRY_BACKOFF_BASE ** attempt
                    self.logger.warning(
                        "Tentativo %d/%d fallito per %s: %s — retry in %.0fs",
                        attempt, MAX_RETRIES, url, e, wait,
                    )
                    time.sleep(wait)
        return 0, {}, None, last_error

    # ---------------- download loop ----------------
    def download(self, source: SourceDef, manifest_entries: dict) -> DownloadResult:
        dest_path = self.raw_dir / source.dest
        prior = manifest_entries.get(source.source_id, {})
        conditional_headers: dict[str, str] = {}
        if dest_path.exists():
            if prior.get("etag"):
                conditional_headers["If-None-Match"] = prior["etag"]
            if prior.get("last_modified"):
                conditional_headers["If-Modified-Since"] = prior["last_modified"]

        status, headers, tmp, err = self._http_get(source.url, conditional_headers, dest_path)
        now = datetime.now(timezone.utc).isoformat()

        if err:
            return DownloadResult(
                source_id=source.source_id, url=source.url, path=str(dest_path),
                status="failed", error=err, fetched_at=now,
            )
        if status == 304 or tmp is None:
            return DownloadResult(
                source_id=source.source_id, url=source.url, path=str(dest_path),
                status="unchanged", http_status=status,
                sha256=prior.get("sha256", ""),
                etag=prior.get("etag", ""),
                last_modified=prior.get("last_modified", ""),
                fetched_at=now,
            )

        # Confronto checksum: se identico al precedente, promuoviamo lo stato ad "unchanged"
        new_sha = _sha256_of(tmp)
        size = tmp.stat().st_size
        etag = headers.get("ETag", "")
        lm = headers.get("Last-Modified", "")

        if prior.get("sha256") == new_sha and dest_path.exists():
            tmp.unlink(missing_ok=True)
            return DownloadResult(
                source_id=source.source_id, url=source.url, path=str(dest_path),
                status="unchanged", http_status=status, bytes=size,
                sha256=new_sha, etag=etag, last_modified=lm, fetched_at=now,
            )

        dest_path.parent.mkdir(parents=True, exist_ok=True)
        os.replace(tmp, dest_path)
        return DownloadResult(
            source_id=source.source_id, url=source.url, path=str(dest_path),
            status="downloaded", http_status=status, bytes=size,
            sha256=new_sha, etag=etag, last_modified=lm, fetched_at=now,
        )

    def run(
        self,
        sources: Iterable[SourceDef],
        post_process: Callable[[list[DownloadResult]], list[str]] | None = None,
    ) -> PipelineReport:
        started = datetime.now(timezone.utc).isoformat()
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        manifest = self._load_manifest()
        entries = manifest.setdefault("entries", {})

        report = PipelineReport(category=self.category, started_at=started, finished_at="")

        for src in sources:
            self.logger.info("[%s] %s → %s", self.category, src.source_id, src.dest)
            res = self.download(src, entries)
            report.results.append(res)
            if res.status == "downloaded":
                report.downloaded += 1
            elif res.status == "unchanged":
                report.unchanged += 1
            elif res.status == "skipped":
                report.skipped += 1
            elif res.status == "failed":
                report.failed += 1
                if src.required:
                    self.logger.error(
                        "Sorgente required %s fallita: %s", src.source_id, res.error
                    )

            if res.status in ("downloaded", "unchanged") and res.sha256:
                entries[src.source_id] = {
                    "title": src.title,
                    "url": src.url,
                    "dest": src.dest,
                    "sha256": res.sha256,
                    "etag": res.etag,
                    "last_modified": res.last_modified,
                    "bytes": res.bytes or entries.get(src.source_id, {}).get("bytes", 0),
                    "last_checked": res.fetched_at,
                }

        if post_process:
            try:
                report.post_processed = list(post_process(report.results) or [])
            except Exception as e:  # pragma: no cover - logged into report
                self.logger.exception("Post-process fallito per %s", self.category)
                report.error = f"post-process: {e}"

        manifest["last_report"] = {
            "downloaded": report.downloaded,
            "unchanged": report.unchanged,
            "skipped": report.skipped,
            "failed": report.failed,
        }
        self._save_manifest(manifest)
        report.finished_at = datetime.now(timezone.utc).isoformat()
        return report
