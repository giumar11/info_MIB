#!/usr/bin/env python3
"""Helper condiviso per scrivere JSON in modo "stabile".

La pipeline di enrichment gira ogni giorno: senza accorgimenti, i file che
contengono la data/ora di generazione (es. ``download_date``, ``generated``,
``data_estrazione``) cambierebbero ad ogni run producendo diff e Pull Request
di solo rumore, anche quando i dati sorgente non sono cambiati.

``write_json_stable`` confronta i nuovi dati con il file esistente ignorando i
campi-data volatili: se l'unica differenza è la data di generazione, il file
viene lasciato invariato. Quando i dati cambiano davvero il file viene
riscritto per intero (con le date aggiornate).
"""

import json
import os

# Chiavi che rappresentano la data/ora di generazione, non i dati veri.
DEFAULT_VOLATILE_KEYS = frozenset({
    "download_date", "generated", "generato_il",
    "data_estrazione", "data_compilazione", "data_aggiornamento",
    "last_updated", "check_timestamp", "report_timestamp",
})


def strip_volatile(obj, volatile_keys=DEFAULT_VOLATILE_KEYS):
    """Copia ricorsiva senza i campi-data volatili (per confronto stabile)."""
    if isinstance(obj, dict):
        return {k: strip_volatile(v, volatile_keys) for k, v in obj.items()
                if k not in volatile_keys}
    if isinstance(obj, list):
        return [strip_volatile(x, volatile_keys) for x in obj]
    return obj


def write_json_stable(data, filepath, volatile_keys=DEFAULT_VOLATILE_KEYS,
                      indent=2):
    """Scrive ``data`` come JSON solo se cambia qualcosa oltre alle date.

    Restituisce ``True`` se il file è stato (ri)scritto, ``False`` se è stato
    lasciato invariato perché i dati sostanziali non sono cambiati.
    """
    filepath = os.fspath(filepath)
    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                old = json.load(f)
            if strip_volatile(old, volatile_keys) == strip_volatile(
                    data, volatile_keys):
                return False
        except (json.JSONDecodeError, OSError):
            pass
    os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=indent)
    return True
