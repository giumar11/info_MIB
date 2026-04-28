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
import html
import json
import logging
import os
import re
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Iterable
from urllib.parse import urljoin

try:
    import requests
except ImportError as e:  # pragma: no cover
    raise SystemExit("Il pacchetto 'requests' è richiesto (pip install -r requirements.txt)") from e


# Alcuni portali (gimbe.org, salviamo-ssn.it, ania.it, aifa.gov.it) restituiscono
# 403 a User-Agent non-browser. Usiamo un UA Chrome-on-Linux che combacia con
# quello dei browser reali. Manteniamo comunque l'identificazione del progetto
# come Accept-Language / commento secondario per onestà di logging server.
USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 "
    "info-MIB-enrichment/1.0"
)
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
    resolver: dict | None = None  # type=landing_regex + landing_url + pattern + prefer_latest


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

    # ---------------- resolver ----------------
    _HREF_RE = re.compile(r'href\s*=\s*["\']([^"\']+?)["\']', re.IGNORECASE)

    def _resolve_from_landing(self, resolver: dict) -> tuple[str, str]:
        """Scarica la landing page e torna (url_risolto, errore).

        resolver = {
            "type": "landing_regex",
            "landing_url": "https://...",
            "pattern": "regex match sull'URL del PDF",
            "prefer_latest": bool  # se True, sceglie l'URL con anno più recente
        }
        """
        landing = resolver.get("landing_url", "")
        pattern = resolver.get("pattern", r"\.pdf(\?|$)")
        if not landing:
            return "", "resolver senza landing_url"
        try:
            resp = self.session.get(landing, timeout=DEFAULT_TIMEOUT, allow_redirects=True)
            resp.raise_for_status()
        except requests.RequestException as e:
            return "", f"landing GET fallito: {e}"

        body = resp.text
        hrefs = [html.unescape(m.group(1)) for m in self._HREF_RE.finditer(body)]
        # Risolvi URL relativi rispetto alla landing
        abs_urls = [urljoin(resp.url, h) for h in hrefs]
        # Filtra: devono essere PDF e matchare il pattern utente
        regex = re.compile(pattern, re.IGNORECASE)
        candidates = [u for u in abs_urls if regex.search(u)]
        if not candidates:
            return "", f"nessun URL match per pattern {pattern!r} in {landing}"

        if resolver.get("prefer_latest"):
            # Euristica: massimizza la sequenza di 4 cifre (anno) trovata nell'URL
            def year_key(u: str) -> tuple[int, int]:
                years = [int(y) for y in re.findall(r"(20\d{2})", u)]
                return (max(years) if years else 0, len(u))
            candidates.sort(key=year_key, reverse=True)

        return candidates[0], ""

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

        # Se è definito un resolver, prova a risolvere l'URL prima di scaricare.
        # Se la risoluzione fallisce, si prova comunque l'URL statico `source.url`.
        effective_url = source.url
        resolver_note = ""
        if source.resolver and source.resolver.get("type") == "landing_regex":
            resolved, rerr = self._resolve_from_landing(source.resolver)
            if resolved:
                effective_url = resolved
                self.logger.info(
                    "[%s] resolver: %s → %s", self.category, source.source_id, resolved
                )
            else:
                resolver_note = f"resolver: {rerr}"
                self.logger.warning("[%s] %s; uso URL statico", self.category, resolver_note)

        conditional_headers: dict[str, str] = {}
        if dest_path.exists():
            if prior.get("etag"):
                conditional_headers["If-None-Match"] = prior["etag"]
            if prior.get("last_modified"):
                conditional_headers["If-Modified-Since"] = prior["last_modified"]

        status, headers, tmp, err = self._http_get(effective_url, conditional_headers, dest_path)
        now = datetime.now(timezone.utc).isoformat()

        if err:
            combined_err = err if not resolver_note else f"{err} ({resolver_note})"
            return DownloadResult(
                source_id=source.source_id, url=effective_url, path=str(dest_path),
                status="failed", error=combined_err, fetched_at=now,
            )
        if status == 304 or tmp is None:
            return DownloadResult(
                source_id=source.source_id, url=effective_url, path=str(dest_path),
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
                source_id=source.source_id, url=effective_url, path=str(dest_path),
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
