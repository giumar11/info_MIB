#!/usr/bin/env python3
"""
Utility condivise per le pipeline di enrichment.

Il problema che risolve: quasi tutti gli script di enrichment scrivono negli
output un campo con la data/ora di esecuzione (``data_estrazione``,
``last_updated``, ``download_date``, ...). Rieseguendo la pipeline ogni giorno,
questi campi cambiano SEMPRE anche quando i dati di origine sono identici: il
risultato è un diff enorme (fino a decine di migliaia di righe) e una Pull
Request automatica quotidiana composta solo da timestamp.

``write_json_stable`` rende la scrittura idempotente: confronta il nuovo
contenuto con quello già presente su disco IGNORANDO i soli campi volatili
(le date). Se l'unica differenza sono quei campi, il file NON viene riscritto
e conserva i timestamp precedenti. Così la pipeline giornaliera produce un diff
(e quindi una PR) solo quando cambiano davvero i dati.
"""

import json
import os

# Chiavi "volatili": contengono la data/ora di esecuzione e non rappresentano
# un cambiamento reale dei dati. Vengono ignorate nel confronto di idempotenza.
DEFAULT_VOLATILE_KEYS = frozenset({
    "data_estrazione",
    "data_compilazione",
    "data_aggiornamento",
    "data_generazione",
    "last_updated",
    "download_date",
    "generated",
    "generato_il",
    "check_timestamp",
    "report_timestamp",
    "run_at",
    "timestamp",
})


def strip_volatile(obj, volatile_keys):
    """Ritorna una copia di ``obj`` senza le chiavi volatili (ricorsivo)."""
    if isinstance(obj, dict):
        return {
            k: strip_volatile(v, volatile_keys)
            for k, v in obj.items()
            if k not in volatile_keys
        }
    if isinstance(obj, list):
        return [strip_volatile(v, volatile_keys) for v in obj]
    return obj


def write_json_stable(data, filepath, volatile_keys=DEFAULT_VOLATILE_KEYS,
                      indent=2, ensure_ascii=False):
    """Scrive ``data`` in JSON solo se il contenuto non-volatile è cambiato.

    Ritorna True se il file è stato (ri)scritto, False se era già aggiornato
    (ignorando i campi volatili) ed è stato lasciato intatto.
    """
    filepath = os.fspath(filepath)
    parent = os.path.dirname(filepath)
    if parent:
        os.makedirs(parent, exist_ok=True)

    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                existing = json.load(f)
        except (json.JSONDecodeError, OSError):
            existing = None
        if existing is not None and (
            strip_volatile(existing, volatile_keys)
            == strip_volatile(data, volatile_keys)
        ):
            # Nessun cambiamento reale: conserva il file (e i suoi timestamp).
            return False

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=ensure_ascii, indent=indent)
    return True
