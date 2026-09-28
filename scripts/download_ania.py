#!/usr/bin/env python3
"""
Download delle pubblicazioni ANIA (Associazione Nazionale fra le Imprese
Assicuratrici) - report del settore assicurativo italiano.

Strategia:
  1. Legge le categorie di pubblicazione ufficiali da
     datasets/raw/ania/ania_sources.json.
  2. Per ogni categoria, scarica la pagina di elenco ANIA e ne estrae gli href
     verso i documenti/PDF (portale Liferay: link /documents/... e *.pdf).
  3. Scarica ogni PDF originale in datasets/raw/ania/<slug>/.
  4. Scarica anche gli URL diretti gia' verificati elencati in "direct_pdfs".
  5. Aggiorna datasets/raw/ania/manifest.json.

Note:
  - Il portale ANIA blocca l'accesso da alcune reti (es. proxy egress delle
    sessioni cloud). Questo script e' pensato per girare in un ambiente con
    rete aperta (es. GitHub Actions).
  - Se lo scraping non individua alcun PDF (elenchi resi via JavaScript o
    struttura pagina cambiata), lo script termina senza errori e lo segnala:
    popolare "direct_pdfs" in ania_sources.json con gli URL verificati.
  - La verifica del certificato resta attiva (default sicuro).

Uso:
    python3 scripts/download_ania.py                 # scarica i mancanti
    python3 scripts/download_ania.py --check         # solo stato
    python3 scripts/download_ania.py --dry-run       # mostra cosa farebbe
    python3 scripts/download_ania.py --category assicurazione_italiana
    python3 scripts/download_ania.py --force         # ri-scarica tutto
"""

import argparse
import hashlib
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ANIA_DIR = os.path.join(BASE_DIR, "datasets", "raw", "ania")
SOURCES_PATH = os.path.join(ANIA_DIR, "ania_sources.json")
MANIFEST_PATH = os.path.join(ANIA_DIR, "manifest.json")

REQUEST_TIMEOUT = 90
RATE_LIMIT_SECONDS = 1.5
MAX_RETRIES = 3
USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)


class LinkExtractor(HTMLParser):
    """Estrae tutti gli href da una pagina HTML."""

    def __init__(self):
        super().__init__()
        self.hrefs = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            for name, value in attrs:
                if name == "href" and value:
                    self.hrefs.append(value)


def _open(url):
    """Esegue una GET restituendo (status, bytes, content_type)."""
    req = urllib.request.Request(url, headers={
        "User-Agent": USER_AGENT,
        "Accept": "text/html,application/pdf,*/*",
    })
    with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as resp:
        return resp.getcode(), resp.read(), resp.headers.get("Content-Type", "")


def fetch_html(url):
    """Scarica una pagina HTML con retry; ritorna il testo o None."""
    for attempt in range(MAX_RETRIES):
        try:
            code, data, _ = _open(url)
            if code == 200:
                return data.decode("utf-8", errors="replace")
            print(f"    [WARN] HTTP {code} su {url}")
            return None
        except urllib.error.HTTPError as e:
            print(f"    [WARN] HTTP {e.code} su {url}")
            if e.code in (403, 404):
                return None
        except (urllib.error.URLError, OSError) as e:
            print(f"    [WARN] tentativo {attempt + 1}/{MAX_RETRIES} fallito: {e}")
        if attempt < MAX_RETRIES - 1:
            time.sleep(2 ** (attempt + 1))
    return None


def discover_pdf_links(page_url):
    """Trova i link a documenti/PDF in una pagina di categoria ANIA."""
    html = fetch_html(page_url)
    if not html:
        return []
    parser = LinkExtractor()
    parser.feed(html)

    found = []
    for href in parser.hrefs:
        low = href.lower().split("?")[0]
        # Documenti Liferay (/documents/...) o PDF diretti
        if low.endswith(".pdf") or "/documents/" in low:
            found.append(urljoin(page_url, href))
    # Deduplica preservando l'ordine
    seen = set()
    unique = []
    for u in found:
        if u not in seen:
            seen.add(u)
            unique.append(u)
    return unique


def safe_filename(url, fallback_prefix="ania_doc"):
    """Ricava un filename sicuro da un URL di documento."""
    path = urlparse(url).path
    name = os.path.basename(path.rstrip("/"))
    if not name or not name.lower().endswith(".pdf"):
        # Liferay: il nome del file puo' precedere l'uuid finale
        segs = [s for s in path.split("/") if s]
        pdf_seg = next((s for s in segs if s.lower().endswith(".pdf")), None)
        name = pdf_seg or f"{fallback_prefix}_{hashlib.sha1(url.encode()).hexdigest()[:10]}.pdf"
    name = re.sub(r"[^A-Za-z0-9._-]", "_", name)
    return name


def download_file(url, dest_path, dry_run=False, force=False):
    """Scarica un file; ritorna dict con esito."""
    result = {"url": url, "path": os.path.relpath(dest_path, BASE_DIR)}
    if dry_run:
        print(f"    [DRY RUN] scaricherebbe: {url}")
        result["status"] = "dry_run"
        return result

    if not force and os.path.exists(dest_path) and os.path.getsize(dest_path) > 1000:
        size = os.path.getsize(dest_path)
        with open(dest_path, "rb") as f:
            sha = hashlib.sha256(f.read()).hexdigest()
        print(f"    [SKIP] gia' presente: {os.path.basename(dest_path)} ({size} B)")
        result.update(status="ok", size_bytes=size, sha256=sha, downloaded=False)
        return result

    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    for attempt in range(MAX_RETRIES):
        try:
            code, data, ctype = _open(url)
            if code != 200:
                print(f"    [WARN] HTTP {code}")
                result["status"] = "http_error"
                return result
            if len(data) < 1000:
                print(f"    [WARN] file troppo piccolo ({len(data)} B), forse non valido")
            with open(dest_path, "wb") as f:
                f.write(data)
            sha = hashlib.sha256(data).hexdigest()
            print(f"    [OK] {os.path.basename(dest_path)} ({len(data)} B)")
            result.update(status="ok", size_bytes=len(data), sha256=sha,
                          content_type=ctype, downloaded=True)
            return result
        except urllib.error.HTTPError as e:
            print(f"    [WARN] HTTP {e.code}")
            if e.code in (403, 404):
                result["status"] = f"http_{e.code}"
                return result
        except (urllib.error.URLError, OSError) as e:
            print(f"    [WARN] tentativo {attempt + 1}/{MAX_RETRIES}: {e}")
        if attempt < MAX_RETRIES - 1:
            time.sleep(2 ** (attempt + 1))
    result["status"] = "failed"
    return result


def load_sources():
    with open(SOURCES_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    parser = argparse.ArgumentParser(description="Download pubblicazioni ANIA")
    parser.add_argument("--check", action="store_true", help="Mostra solo lo stato")
    parser.add_argument("--dry-run", action="store_true", help="Non scarica nulla")
    parser.add_argument("--force", action="store_true", help="Ri-scarica tutto")
    parser.add_argument("--category", type=str, default=None,
                        help="Solo la categoria con questo slug")
    args = parser.parse_args()

    if not os.path.exists(SOURCES_PATH):
        print(f"ERRORE: manca {SOURCES_PATH}")
        return 1

    sources = load_sources()
    categories = sources.get("categories", [])
    direct_pdfs = sources.get("direct_pdfs", [])
    if args.category:
        categories = [c for c in categories if c["slug"] == args.category]
        direct_pdfs = [d for d in direct_pdfs if d.get("slug") == args.category]

    print("=" * 70)
    print("  DOWNLOAD PUBBLICAZIONI ANIA (settore assicurativo)")
    print("=" * 70)

    if args.check:
        n = len([p for _, _, p in _iter_existing()])
        print(f"\nFile ANIA presenti: {n}")
        for slug, name, path in _iter_existing():
            print(f"  [{slug}] {name} ({os.path.getsize(path)} B)")
        return 0

    manifest = {
        "description": "Manifest pubblicazioni ANIA scaricate",
        "download_date": time.strftime("%Y-%m-%d"),
        "source_portal": sources.get("base_url", "https://www.ania.it"),
        "files": [],
        "categories_processed": [],
    }
    total_found = 0

    # 1) Scraping delle pagine di categoria
    for cat in categories:
        slug = cat["slug"]
        landing = cat.get("landing_page")
        print(f"\n[{slug}] {cat.get('title', '')}")
        cat_record = {"slug": slug, "landing_page": landing, "pdf_links_found": 0}
        if landing:
            print(f"    pagina: {landing}")
            links = discover_pdf_links(landing)
            cat_record["pdf_links_found"] = len(links)
            total_found += len(links)
            if not links:
                print("    [INFO] nessun PDF individuato nella pagina di categoria")
            for link in links:
                dest = os.path.join(ANIA_DIR, slug, safe_filename(link, slug))
                res = download_file(link, dest, dry_run=args.dry_run, force=args.force)
                res["slug"] = slug
                res["origin"] = "category_scrape"
                manifest["files"].append(res)
                time.sleep(RATE_LIMIT_SECONDS)
        manifest["categories_processed"].append(cat_record)

    # 2) URL diretti verificati
    if direct_pdfs:
        print(f"\n[direct_pdfs] {len(direct_pdfs)} URL verificati")
    for entry in direct_pdfs:
        slug = entry.get("slug", "misc")
        url = entry.get("url")
        if not url:
            continue
        fname = entry.get("filename") or safe_filename(url, slug)
        dest = os.path.join(ANIA_DIR, slug, fname)
        print(f"  {entry.get('title', fname)}")
        res = download_file(url, dest, dry_run=args.dry_run, force=args.force)
        res["slug"] = slug
        res["title"] = entry.get("title")
        res["year"] = entry.get("year")
        res["origin"] = "direct"
        manifest["files"].append(res)
        time.sleep(RATE_LIMIT_SECONDS)

    ok = [f for f in manifest["files"] if f.get("status") == "ok"]
    manifest["total_files"] = len(manifest["files"])
    manifest["downloaded_ok"] = len(ok)

    if not args.dry_run:
        os.makedirs(ANIA_DIR, exist_ok=True)
        with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
            json.dump(manifest, f, ensure_ascii=False, indent=2)

    print(f"\n{'=' * 70}")
    print(f"PDF individuati (scraping): {total_found}")
    print(f"File disponibili/scaricati: {len(ok)}")
    if total_found == 0 and not direct_pdfs:
        print("\nNESSUN documento individuato. Il portale ANIA potrebbe rendere")
        print("gli elenchi via JavaScript o bloccare la rete corrente.")
        print("Popolare 'direct_pdfs' in ania_sources.json con gli URL verificati.")
    print(f"Manifest: {MANIFEST_PATH}")
    print("=" * 70)
    return 0


def _iter_existing():
    if not os.path.isdir(ANIA_DIR):
        return
    for root, _dirs, files in os.walk(ANIA_DIR):
        for name in files:
            if name.lower().endswith(".pdf"):
                slug = os.path.relpath(root, ANIA_DIR).split(os.sep)[0]
                yield slug, name, os.path.join(root, name)


if __name__ == "__main__":
    sys.exit(main())
