#!/usr/bin/env python3
"""
Helper per scrivere file JSON in modo *deterministico* rispetto ai timestamp.

Problema risolto
----------------
Gli script di enrichment rigenerano gli estratti ad ogni esecuzione e vi
incorporano un timestamp di generazione (es. ``last_updated``, ``data_estrazione``,
``download_date``). Con la pipeline schedulata giornaliera questo faceva sì che
ogni file cambiasse *ogni giorno* anche quando i dati reali erano identici,
producendo una Pull Request di puro rumore (migliaia di righe) e vanificando il
gate "Detect changes" del workflow.

``write_json_stable`` confronta il contenuto nuovo con quello già presentre su
disco *ignorando* le chiavi volatili (timestamp). Se l'unica differenza sono i
timestamp, il file NON viene riscritto: su disco resta la versione precedente,
quindi ``git status`` non rileva modifiche. Il file viene aggiornato solo quando
cambia qualcosa di sostanziale (nuovi record, valori diversi, hash diversi...).
"""

import copy
import json
import os

# Chiavi che rappresentano un istante/data di generazione e che quindi non
# devono, da sole, contare come "modifica" del dataset.
VOLATILE_KEYS = frozenset({
    "last_updated",
    "data_estrazione",
    "data_compilazione",
    "data_generazione",
    "data_aggiornamento",
    "data_elaborazione",
    "download_date",
    "generated",
    "generato_il",
    "check_timestamp",
    "report_timestamp",
    "timestamp",
})


def _strip_volatile(obj, volatile_keys):
    """Ritorna una copia della struttura senza le chiavi volatili (ricorsiva)."""
    if isinstance(obj, dict):
        return {
            k: _strip_volatile(v, volatile_keys)
            for k, v in obj.items()
            if k not in volatile_keys
        }
    if isinstance(obj, list):
        return [_strip_volatile(v, volatile_keys) for v in obj]
    return obj


def content_differs(new_data, path, volatile_keys=VOLATILE_KEYS):
    """True se `new_data` differisce dal file in `path` a meno dei timestamp."""
    if not os.path.exists(path):
        return True
    try:
        with open(path, "r", encoding="utf-8") as f:
            old_data = json.load(f)
    except (ValueError, OSError):
        # File illeggibile/corrotto: trattalo come da riscrivere.
        return True
    return _strip_volatile(new_data, volatile_keys) != _strip_volatile(
        old_data, volatile_keys)


def write_json_stable(new_data, path, *, indent=2, ensure_ascii=False,
                      volatile_keys=VOLATILE_KEYS, newline=False):
    """
    Scrive `new_data` come JSON in `path` solo se il contenuto sostanziale
    (escluse le chiavi volatili) è cambiato rispetto al file esistente.

    Ritorna True se il file è stato (ri)scritto, False se lasciato invariato.
    """
    path = os.fspath(path)
    if not content_differs(new_data, path, volatile_keys):
        return False
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(new_data, f, indent=indent, ensure_ascii=ensure_ascii)
        if newline:
            f.write("\n")
    return True
