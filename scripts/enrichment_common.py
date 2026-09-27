#!/usr/bin/env python3
"""
Utility condivise per le pipeline di enrichment InfoMIB.

Fornisce un downloader robusto e riutilizzabile usato da tutti gli script di
download degli originali (report e dataset). Caratteristiche:

- Usa `requests` se disponibile (rispetta le variabili d'ambiente HTTP(S)_PROXY
  e REQUESTS_CA_BUNDLE), con fallback su urllib della standard library.
- Gestione TLS corretta: la verifica dei certificati è attiva per default.
  Alcuni portali della PA italiana hanno catene di certificati incomplete: in
  questi casi la verifica può essere disattivata in modo esplicito e corretto
  impostando la variabile d'ambiente INFOMIB_INSECURE_TLS=1 (oppure passando
  insecure=True). Questo sostituisce il vecchio `ctx.verify_peer = False`, che
  era un attributo inesistente su ssl.SSLContext e quindi un no-op silenzioso.
- Retry con backoff esponenziale.
- Validazione della dimensione minima e (opzionale) dei magic bytes PDF.
- Calcolo dello sha256 e reporting strutturato.
"""

import hashlib
import os
import ssl
import sys
import time
import urllib.error
import urllib.request

try:
    import requests  # type: ignore
    HAVE_REQUESTS = True
except ImportError:  # pragma: no cover - fallback puro standard library
    requests = None
    HAVE_REQUESTS = False


DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 "
    "InfoMIB-Enrichment/1.0 (+https://github.com/giumar11/info_MIB)"
)

MIN_VALID_BYTES = 1024
PDF_MAGIC = b"%PDF"


def _insecure_requested(insecure):
    """True se la verifica TLS deve essere disattivata (flag o env var)."""
    if insecure:
        return True
    return os.environ.get("INFOMIB_INSECURE_TLS", "").strip() in ("1", "true", "yes")


def format_size(size_bytes):
    if size_bytes >= 1_000_000:
        return f"{size_bytes / 1_000_000:.1f} MB"
    if size_bytes >= 1_000:
        return f"{size_bytes / 1_000:.1f} KB"
    return f"{size_bytes} B"


def _make_ssl_context(insecure):
    """Crea un SSLContext. Se insecure, disattiva la verifica nel modo CORRETTO."""
    ctx = ssl.create_default_context()
    if insecure:
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
    return ctx


def _download_requests(url, headers, timeout, insecure):
    verify = not _insecure_requested(insecure)
    if not verify:
        try:
            import urllib3  # type: ignore
            urllib3.disable_warnings()
        except Exception:
            pass
    resp = requests.get(
        url, headers=headers, timeout=timeout, allow_redirects=True, verify=verify
    )
    resp.raise_for_status()
    return resp.content


def _download_urllib(url, headers, timeout, insecure):
    ctx = _make_ssl_context(_insecure_requested(insecure))
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, context=ctx, timeout=timeout) as resp:
        return resp.read()


def download_file(url, dest_path, *, expect_pdf=False, min_bytes=MIN_VALID_BYTES,
                  max_retries=3, timeout=120, insecure=False, user_agent=None,
                  logger=print):
    """
    Scarica un file da `url` a `dest_path` con retry e validazione.

    Returns:
        dict con chiavi: status ('ok'|'too_small'|'invalid_pdf'|'failed'),
        size_bytes, sha256, url, error.
    """
    headers = {
        "User-Agent": user_agent or DEFAULT_USER_AGENT,
        "Accept": "application/pdf,application/octet-stream,*/*",
    }

    last_error = None
    for attempt in range(1, max_retries + 1):
        try:
            if HAVE_REQUESTS:
                data = _download_requests(url, headers, timeout, insecure)
            else:
                data = _download_urllib(url, headers, timeout, insecure)

            if len(data) < min_bytes:
                last_error = f"file troppo piccolo ({len(data)} byte)"
                logger(f"    ATTENZIONE: {last_error}")
                # non ritentiamo: probabilmente è una pagina di errore
                return {"status": "too_small", "size_bytes": len(data),
                        "sha256": None, "url": url, "error": last_error}

            if expect_pdf and not data[:4] == PDF_MAGIC:
                last_error = "contenuto non è un PDF valido (magic bytes assenti)"
                logger(f"    ATTENZIONE: {last_error}")
                return {"status": "invalid_pdf", "size_bytes": len(data),
                        "sha256": None, "url": url, "error": last_error}

            os.makedirs(os.path.dirname(os.path.abspath(dest_path)), exist_ok=True)
            with open(dest_path, "wb") as fh:
                fh.write(data)

            return {
                "status": "ok",
                "size_bytes": len(data),
                "sha256": hashlib.sha256(data).hexdigest(),
                "url": url,
                "error": None,
            }

        except Exception as exc:  # noqa: BLE001 - vogliamo ritentare su qualsiasi errore di rete
            last_error = f"{type(exc).__name__}: {str(exc)[:200]}"
            logger(f"    Tentativo {attempt}/{max_retries} fallito: {last_error}")
            if attempt < max_retries:
                wait = 2 ** attempt
                logger(f"    Riprovo tra {wait}s...")
                time.sleep(wait)

    return {"status": "failed", "size_bytes": 0, "sha256": None,
            "url": url, "error": last_error}


def sha256_of_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def existing_ok(path, min_bytes=MIN_VALID_BYTES):
    """True se il file esiste ed è plausibilmente valido (non vuoto/placeholder)."""
    return os.path.exists(path) and os.path.getsize(path) >= min_bytes
