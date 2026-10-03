#!/usr/bin/env python3
"""
Test di unita' (senza rete) per le utility di enrichment.

Verifica:
  - idempotenza di write_json_stable (nessuna riscrittura se cambiano solo le
    date; riscrittura quando cambia il contenuto reale);
  - estrazione dei link PDF dalle pagine di pubblicazione ANIA.

Esecuzione:
    python3 scripts/test_enrich.py
"""

import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from enrich_utils import write_json_stable, strip_volatile
from download_ania_pdfs import extract_pdf_links


def test_strip_volatile_nested():
    data = {
        "data_estrazione": "2026-01-01",
        "nome": "x",
        "items": [{"last_updated": "t1", "v": 1}, {"last_updated": "t2", "v": 2}],
    }
    stripped = strip_volatile(data, {"data_estrazione", "last_updated"})
    assert stripped == {"nome": "x", "items": [{"v": 1}, {"v": 2}]}, stripped


def test_write_json_stable_idempotent_on_dates():
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "out.json")
        v1 = {"data_estrazione": "2026-01-01", "payload": {"a": 1}}
        assert write_json_stable(v1, path) is True          # prima scrittura
        mtime1 = os.path.getmtime(path)

        # Stesso contenuto, data diversa -> NON deve riscrivere.
        v2 = {"data_estrazione": "2026-10-03", "payload": {"a": 1}}
        assert write_json_stable(v2, path) is False
        on_disk = json.load(open(path, encoding="utf-8"))
        assert on_disk["data_estrazione"] == "2026-01-01", on_disk  # data vecchia preservata
        assert os.path.getmtime(path) == mtime1               # file intatto


def test_write_json_stable_rewrites_on_real_change():
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "out.json")
        write_json_stable({"data_estrazione": "2026-01-01", "payload": {"a": 1}}, path)
        # Contenuto reale cambiato -> deve riscrivere e aggiornare la data.
        v2 = {"data_estrazione": "2026-10-03", "payload": {"a": 2}}
        assert write_json_stable(v2, path) is True
        on_disk = json.load(open(path, encoding="utf-8"))
        assert on_disk["payload"]["a"] == 2
        assert on_disk["data_estrazione"] == "2026-10-03"


def test_write_json_stable_handles_corrupt_existing():
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "out.json")
        with open(path, "w", encoding="utf-8") as f:
            f.write("{ not valid json")
        assert write_json_stable({"payload": 1}, path) is True
        assert json.load(open(path, encoding="utf-8")) == {"payload": 1}


def test_extract_pdf_links_basic():
    html = '''
      <a href="/documents/35135/439653/Assicurazione-Italiana-2006.pdf/abc?t=1">A</a>
      <a href="https://www.ania.it/export/sites/default/report_2017.pdf">B</a>
      <a href="/pubblicazioni/altro">non-pdf</a>
      <a href="relativo/file.PDF?v=2">C</a>
    '''
    links = extract_pdf_links(html, "https://www.ania.it/pubblicazioni/")
    assert "https://www.ania.it/documents/35135/439653/Assicurazione-Italiana-2006.pdf/abc?t=1" in links
    assert "https://www.ania.it/export/sites/default/report_2017.pdf" in links
    assert "https://www.ania.it/pubblicazioni/relativo/file.PDF?v=2" in links
    assert all("non-pdf" not in link for link in links)


def test_extract_pdf_links_dedup_and_empty():
    html = '<a href="a.pdf">1</a><a href="a.pdf">dup</a>'
    links = extract_pdf_links(html, "https://x.it/")
    assert links == ["https://x.it/a.pdf"], links
    assert extract_pdf_links("<html>no links</html>", "https://x.it/") == []


def main():
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    failed = 0
    for t in tests:
        try:
            t()
            print(f"  PASS  {t.__name__}")
        except AssertionError as e:
            failed += 1
            print(f"  FAIL  {t.__name__}: {e}")
        except Exception as e:  # pragma: no cover
            failed += 1
            print(f"  ERROR {t.__name__}: {type(e).__name__}: {e}")
    print(f"\n{len(tests) - failed}/{len(tests)} test superati")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
