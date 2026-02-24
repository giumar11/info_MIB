#!/usr/bin/env python3
"""
Scheduler mensile per il controllo aggiornamenti delle fonti dati.

Legge tutte le fonti dal catalogo sources_catalog.csv, controlla se ciascun
sito ha nuove pubblicazioni o contenuti aggiornati, e genera un report con
le variazioni rilevate.

Metodi di rilevamento:
1. HTTP HEAD → Last-Modified / ETag / Content-Length
2. HTTP GET  → hash SHA-256 del contenuto della pagina
3. Confronto con stato precedente salvato in logs/update_state.json

Schedulazione:
- Via cron:  0 9 1 * * /usr/bin/python3 /path/to/scheduler_check_updates.py
- Via flag:  --install-cron   (installa automaticamente il job cron mensile)
- Manuale:   python3 scheduler_check_updates.py [--force] [--source SOURCE_ID]

Output:
- logs/update_check_YYYY-MM-DD.log   (log dettagliato)
- logs/update_report_YYYY-MM-DD.json (report strutturato)
- logs/update_state.json             (stato persistente per confronti)
"""

import argparse
import csv
import hashlib
import json
import logging
import os
import subprocess
import sys
import time
from datetime import datetime, timedelta
from urllib.parse import urlparse

try:
    import requests
except ImportError:
    print("ERRORE: il modulo 'requests' è necessario.")
    print("Installalo con: pip install requests")
    sys.exit(1)


# === CONFIGURAZIONE ===
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CATALOG_PATH = os.path.join(BASE_DIR, 'sources_catalog.csv')
LOGS_DIR = os.path.join(BASE_DIR, 'logs')
STATE_FILE = os.path.join(LOGS_DIR, 'update_state.json')

TODAY = datetime.now().strftime('%Y-%m-%d')
LOG_FILE = os.path.join(LOGS_DIR, f'update_check_{TODAY}.log')
REPORT_FILE = os.path.join(LOGS_DIR, f'update_report_{TODAY}.json')

REQUEST_TIMEOUT = 30   # secondi
REQUEST_DELAY = 2      # secondi tra richieste (rate limiting)
MAX_RETRIES = 2
USER_AGENT = (
    'Mozilla/5.0 (compatible; InfoMIB-UpdateChecker/1.0; '
    '+https://github.com/giumar11/info_MIB)'
)

# Fonti con contenuto statico che non cambiano mai
STATIC_SOURCES = {'DM77_001', 'DM70_001'}


# === LOGGING ===

def setup_logging():
    """Configura il logging su file e console."""
    os.makedirs(LOGS_DIR, exist_ok=True)

    logger = logging.getLogger('update_checker')
    logger.setLevel(logging.DEBUG)

    # File handler
    fh = logging.FileHandler(LOG_FILE, encoding='utf-8')
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    ))
    logger.addHandler(fh)

    # Console handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(logging.Formatter('%(levelname)-8s | %(message)s'))
    logger.addHandler(ch)

    return logger


# === GESTIONE STATO PERSISTENTE ===

def load_state():
    """Carica lo stato precedente dal file JSON."""
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def save_state(state):
    """Salva lo stato aggiornato su file JSON."""
    with open(STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


# === LETTURA CATALOGO ===

def load_catalog():
    """Legge tutte le fonti dal catalogo CSV."""
    sources = []
    with open(CATALOG_PATH, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get('source_id') and row.get('url'):
                sources.append(row)
    return sources


# === CONTROLLO SINGOLA FONTE ===

def check_source(source, previous_state, logger):
    """
    Controlla una singola fonte per aggiornamenti.

    Strategia a 3 livelli:
    1. HEAD request → controlla Last-Modified, ETag, Content-Length
    2. GET request  → calcola hash SHA-256 del body
    3. Confronto con lo stato precedente

    Returns:
        dict con risultato del controllo
    """
    source_id = source['source_id']
    url = source['url']
    title = source['title']

    result = {
        'source_id': source_id,
        'title': title,
        'url': url,
        'owner': source.get('owner', ''),
        'category': source.get('category', ''),
        'update_frequency': source.get('update_frequency', ''),
        'check_timestamp': datetime.now().isoformat(),
        'status': 'unknown',
        'changed': False,
        'change_details': [],
        'http_status': None,
        'error': None
    }

    # Salta fonti statiche
    if source_id in STATIC_SOURCES:
        result['status'] = 'skipped_static'
        logger.info(f"[{source_id}] {title} - Fonte statica, skip")
        return result

    prev = previous_state.get(source_id, {})
    headers = {'User-Agent': USER_AGENT}

    # --- FASE 1: HEAD request ---
    head_data = {}
    for attempt in range(MAX_RETRIES + 1):
        try:
            resp = requests.head(
                url,
                headers=headers,
                timeout=REQUEST_TIMEOUT,
                allow_redirects=True
            )
            result['http_status'] = resp.status_code

            if resp.status_code == 405:
                # HEAD non supportato, passo direttamente a GET
                logger.debug(f"[{source_id}] HEAD non supportato (405), provo GET")
                break

            if resp.status_code >= 400:
                if attempt < MAX_RETRIES:
                    time.sleep(2 ** (attempt + 1))
                    continue
                result['status'] = 'http_error'
                result['error'] = f"HTTP {resp.status_code}"
                logger.warning(f"[{source_id}] {title} - HTTP {resp.status_code}")
                return result

            head_data = {
                'last_modified': resp.headers.get('Last-Modified', ''),
                'etag': resp.headers.get('ETag', ''),
                'content_length': resp.headers.get('Content-Length', ''),
                'content_type': resp.headers.get('Content-Type', ''),
            }
            break

        except requests.exceptions.Timeout:
            if attempt < MAX_RETRIES:
                time.sleep(2 ** (attempt + 1))
                continue
            result['status'] = 'timeout'
            result['error'] = f"Timeout dopo {REQUEST_TIMEOUT}s"
            logger.warning(f"[{source_id}] {title} - Timeout")
            return result

        except requests.exceptions.ConnectionError as e:
            if attempt < MAX_RETRIES:
                time.sleep(2 ** (attempt + 1))
                continue
            result['status'] = 'connection_error'
            result['error'] = str(e)[:200]
            logger.warning(f"[{source_id}] {title} - Errore connessione: {str(e)[:100]}")
            return result

        except requests.exceptions.RequestException as e:
            result['status'] = 'request_error'
            result['error'] = str(e)[:200]
            logger.warning(f"[{source_id}] {title} - Errore: {str(e)[:100]}")
            return result

    # Confronto header con stato precedente
    changes = []
    if head_data:
        if prev.get('last_modified') and head_data['last_modified']:
            if head_data['last_modified'] != prev['last_modified']:
                changes.append(f"Last-Modified cambiato: {prev['last_modified']} -> {head_data['last_modified']}")

        if prev.get('etag') and head_data['etag']:
            if head_data['etag'] != prev['etag']:
                changes.append(f"ETag cambiato: {prev['etag'][:30]}... -> {head_data['etag'][:30]}...")

        if prev.get('content_length') and head_data['content_length']:
            if head_data['content_length'] != prev['content_length']:
                changes.append(f"Content-Length cambiato: {prev['content_length']} -> {head_data['content_length']}")

    # --- FASE 2: GET request per hash contenuto ---
    content_hash = None
    for attempt in range(MAX_RETRIES + 1):
        try:
            resp = requests.get(
                url,
                headers=headers,
                timeout=REQUEST_TIMEOUT,
                allow_redirects=True
            )
            result['http_status'] = resp.status_code

            if resp.status_code >= 400:
                if attempt < MAX_RETRIES:
                    time.sleep(2 ** (attempt + 1))
                    continue
                # Se HEAD era ok ma GET fallisce, usa i risultati HEAD
                if head_data:
                    break
                result['status'] = 'http_error'
                result['error'] = f"HTTP {resp.status_code}"
                logger.warning(f"[{source_id}] {title} - GET HTTP {resp.status_code}")
                return result

            # Calcola hash del contenuto
            content_hash = hashlib.sha256(resp.content).hexdigest()

            if prev.get('content_hash') and content_hash != prev['content_hash']:
                changes.append(f"Contenuto pagina modificato (hash diverso)")

            break

        except requests.exceptions.RequestException:
            if attempt < MAX_RETRIES:
                time.sleep(2 ** (attempt + 1))
                continue
            # Se HEAD era ok, accetta i risultati parziali
            if head_data:
                break
            result['status'] = 'request_error'
            result['error'] = 'GET fallito dopo retry'
            logger.warning(f"[{source_id}] {title} - GET fallito")
            return result

    # --- FASE 3: Valutazione risultato ---
    if changes:
        result['status'] = 'updated'
        result['changed'] = True
        result['change_details'] = changes
        logger.info(f"[{source_id}] {title} - AGGIORNAMENTO RILEVATO: {'; '.join(changes)}")
    elif not prev:
        result['status'] = 'first_check'
        result['changed'] = False
        logger.info(f"[{source_id}] {title} - Prima verifica, stato salvato")
    else:
        result['status'] = 'unchanged'
        result['changed'] = False
        logger.info(f"[{source_id}] {title} - Nessun cambiamento")

    # Aggiorna stato per prossimo confronto
    new_state = {
        'last_checked': TODAY,
        'http_status': result['http_status'],
        'content_hash': content_hash,
    }
    if head_data:
        new_state.update(head_data)

    return result, new_state


# === CONTROLLO DUE DATE (fonti da controllare) ===

def is_check_due(source, state):
    """
    Determina se una fonte è da controllare in base alla frequenza
    di aggiornamento e alla data dell'ultimo controllo.
    """
    source_id = source['source_id']
    frequency = source.get('update_frequency', 'annual')
    prev = state.get(source_id, {})
    last_checked = prev.get('last_checked', '')

    if not last_checked:
        return True  # Mai controllata

    try:
        last_date = datetime.strptime(last_checked, '%Y-%m-%d')
    except ValueError:
        return True

    now = datetime.now()
    days_since = (now - last_date).days

    # Intervalli di controllo basati sulla frequenza della fonte
    thresholds = {
        'continuous': 7,     # settimanale
        'quarterly': 30,     # mensile
        'annual': 30,        # mensile
        'biennial': 60,      # bimestrale
        'periodic': 30,      # mensile
        'static': 365,       # annuale (ma le statiche vengono comunque skippate)
    }

    threshold = thresholds.get(frequency, 30)
    return days_since >= threshold


# === GENERAZIONE REPORT ===

def generate_report(results, logger):
    """Genera il report strutturato dei controlli."""
    updated = [r for r in results if r.get('changed')]
    errors = [r for r in results if r.get('status') in ('http_error', 'timeout', 'connection_error', 'request_error')]
    first_checks = [r for r in results if r.get('status') == 'first_check']
    unchanged = [r for r in results if r.get('status') == 'unchanged']
    skipped = [r for r in results if r.get('status') == 'skipped_static']

    report = {
        'report_date': TODAY,
        'report_timestamp': datetime.now().isoformat(),
        'summary': {
            'total_sources': len(results),
            'updated': len(updated),
            'unchanged': len(unchanged),
            'first_check': len(first_checks),
            'errors': len(errors),
            'skipped_static': len(skipped),
        },
        'updates_found': [
            {
                'source_id': r['source_id'],
                'title': r['title'],
                'owner': r['owner'],
                'url': r['url'],
                'changes': r.get('change_details', [])
            }
            for r in updated
        ],
        'errors_found': [
            {
                'source_id': r['source_id'],
                'title': r['title'],
                'url': r['url'],
                'error': r.get('error', ''),
                'status': r.get('status', '')
            }
            for r in errors
        ],
        'sources_due_for_review': [],
        'all_results': results
    }

    # Identifica fonti che per frequenza dovrebbero avere nuovi dati
    for r in results:
        freq = r.get('update_frequency', '')
        if freq == 'annual':
            report['sources_due_for_review'].append({
                'source_id': r['source_id'],
                'title': r['title'],
                'note': 'Fonte annuale - verificare se è uscito il nuovo rapporto'
            })

    # Salva report
    with open(REPORT_FILE, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    logger.info(f"Report salvato: {REPORT_FILE}")

    return report


def print_summary(report):
    """Stampa un riepilogo leggibile del report."""
    s = report['summary']

    print("\n" + "=" * 70)
    print(f"REPORT CONTROLLO AGGIORNAMENTI - {TODAY}")
    print("=" * 70)

    print(f"\n  Fonti controllate:     {s['total_sources']}")
    print(f"  Aggiornamenti trovati: {s['updated']}")
    print(f"  Invariate:             {s['unchanged']}")
    print(f"  Prima verifica:        {s['first_check']}")
    print(f"  Errori:                {s['errors']}")
    print(f"  Statiche (skip):       {s['skipped_static']}")

    if report['updates_found']:
        print(f"\n{'─' * 70}")
        print("AGGIORNAMENTI RILEVATI:")
        print(f"{'─' * 70}")
        for u in report['updates_found']:
            print(f"\n  [{u['source_id']}] {u['title']}")
            print(f"  Owner: {u['owner']}")
            print(f"  URL:   {u['url']}")
            for change in u['changes']:
                print(f"    -> {change}")

    if report['errors_found']:
        print(f"\n{'─' * 70}")
        print("ERRORI:")
        print(f"{'─' * 70}")
        for e in report['errors_found']:
            print(f"\n  [{e['source_id']}] {e['title']}")
            print(f"    Stato: {e['status']} - {e['error']}")

    print(f"\n{'─' * 70}")
    print(f"Log completo: {LOG_FILE}")
    print(f"Report JSON:  {REPORT_FILE}")
    print(f"Stato fonti:  {STATE_FILE}")
    print("=" * 70)


# === AGGIORNAMENTO CATALOGO ===

def update_catalog_last_checked(checked_ids):
    """
    Aggiorna la colonna last_checked nel catalogo CSV
    per le fonti appena controllate.
    """
    rows = []
    fieldnames = None

    with open(CATALOG_PATH, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        for row in reader:
            if row.get('source_id') in checked_ids:
                row['last_checked'] = TODAY
            rows.append(row)

    with open(CATALOG_PATH, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


# === INSTALLAZIONE CRON ===

def install_cron():
    """Installa un job cron mensile per l'esecuzione automatica."""
    script_path = os.path.abspath(__file__)
    python_path = sys.executable
    log_path = os.path.join(LOGS_DIR, 'cron_output.log')

    # Job cron: ogni 1° del mese alle 09:00
    cron_line = f'0 9 1 * * {python_path} {script_path} >> {log_path} 2>&1'
    cron_comment = '# InfoMIB - Controllo mensile aggiornamenti fonti dati'

    try:
        # Leggi crontab attuale
        result = subprocess.run(
            ['crontab', '-l'],
            capture_output=True, text=True
        )
        current_crontab = result.stdout if result.returncode == 0 else ''

        # Controlla se già installato
        if 'scheduler_check_updates.py' in current_crontab:
            print("Job cron già installato. Crontab attuale:")
            print(current_crontab)
            return

        # Aggiungi il nuovo job
        new_crontab = current_crontab.rstrip('\n')
        if new_crontab:
            new_crontab += '\n'
        new_crontab += f'\n{cron_comment}\n{cron_line}\n'

        # Installa
        process = subprocess.Popen(
            ['crontab', '-'],
            stdin=subprocess.PIPE, text=True
        )
        process.communicate(input=new_crontab)

        if process.returncode == 0:
            print("Job cron installato con successo.")
            print(f"  Schedulazione: ogni 1° del mese alle 09:00")
            print(f"  Comando:       {cron_line}")
            print(f"  Log cron:      {log_path}")
        else:
            print("Errore nell'installazione del job cron.")
            print("Puoi aggiungerlo manualmente con 'crontab -e':")
            print(f"  {cron_line}")

    except FileNotFoundError:
        print("'crontab' non trovato. Puoi schedulare manualmente:")
        print(f"  {cron_line}")
        print("\nAlternativa con systemd timer:")
        print(f"  ExecStart={python_path} {script_path}")


def uninstall_cron():
    """Rimuove il job cron mensile."""
    try:
        result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
        if result.returncode != 0:
            print("Nessun crontab trovato.")
            return

        lines = result.stdout.split('\n')
        new_lines = [
            line for line in lines
            if 'scheduler_check_updates.py' not in line
            and 'InfoMIB - Controllo mensile' not in line
        ]
        new_crontab = '\n'.join(new_lines)

        process = subprocess.Popen(['crontab', '-'], stdin=subprocess.PIPE, text=True)
        process.communicate(input=new_crontab)

        if process.returncode == 0:
            print("Job cron rimosso con successo.")
        else:
            print("Errore nella rimozione. Rimuovi manualmente con 'crontab -e'.")

    except FileNotFoundError:
        print("'crontab' non disponibile su questo sistema.")


# === MAIN ===

def main():
    parser = argparse.ArgumentParser(
        description='Controllo aggiornamenti fonti dati InfoMIB',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Esempi:
  python3 scheduler_check_updates.py                  # Controlla tutte le fonti
  python3 scheduler_check_updates.py --force           # Forza controllo anche se recente
  python3 scheduler_check_updates.py --source AIOM_001 # Controlla solo una fonte
  python3 scheduler_check_updates.py --source AIOM_001 --source ONS_001
  python3 scheduler_check_updates.py --category screening
  python3 scheduler_check_updates.py --install-cron    # Installa job cron mensile
  python3 scheduler_check_updates.py --uninstall-cron  # Rimuovi job cron
  python3 scheduler_check_updates.py --dry-run         # Mostra cosa farebbe senza eseguire
        """
    )
    parser.add_argument(
        '--force', action='store_true',
        help='Forza il controllo di tutte le fonti, ignorando la data ultimo controllo'
    )
    parser.add_argument(
        '--source', action='append', dest='sources',
        help='Controlla solo le fonti specificate (ripetibile). Es: --source AIOM_001'
    )
    parser.add_argument(
        '--category', type=str,
        help='Controlla solo le fonti di una categoria. Es: --category screening'
    )
    parser.add_argument(
        '--dry-run', action='store_true',
        help='Mostra le fonti che verrebbero controllate senza eseguire i check'
    )
    parser.add_argument(
        '--install-cron', action='store_true',
        help='Installa il job cron per esecuzione mensile automatica (1° del mese ore 09:00)'
    )
    parser.add_argument(
        '--uninstall-cron', action='store_true',
        help='Rimuovi il job cron mensile'
    )
    parser.add_argument(
        '--delay', type=float, default=REQUEST_DELAY,
        help=f'Ritardo in secondi tra le richieste (default: {REQUEST_DELAY})'
    )

    args = parser.parse_args()

    # Gestione cron
    if args.install_cron:
        install_cron()
        return
    if args.uninstall_cron:
        uninstall_cron()
        return

    # Setup
    logger = setup_logging()
    logger.info("=" * 60)
    logger.info("AVVIO CONTROLLO AGGIORNAMENTI FONTI DATI")
    logger.info("=" * 60)

    # Carica catalogo e stato
    catalog = load_catalog()
    state = load_state()

    logger.info(f"Fonti nel catalogo: {len(catalog)}")
    logger.info(f"Fonti con stato precedente: {len(state)}")

    # Filtra per source_id se specificato
    if args.sources:
        catalog = [s for s in catalog if s['source_id'] in args.sources]
        logger.info(f"Filtro per source_id: {args.sources} -> {len(catalog)} fonti")

    # Filtra per categoria se specificata
    if args.category:
        catalog = [s for s in catalog if s.get('category') == args.category]
        logger.info(f"Filtro per categoria '{args.category}': {len(catalog)} fonti")

    # Determina quali fonti controllare
    if args.force:
        sources_to_check = catalog
    else:
        sources_to_check = [s for s in catalog if is_check_due(s, state)]

    logger.info(f"Fonti da controllare: {len(sources_to_check)}")

    # Dry run
    if args.dry_run:
        print(f"\n[DRY RUN] Fonti che verrebbero controllate: {len(sources_to_check)}\n")
        for s in sources_to_check:
            freq = s.get('update_frequency', '?')
            last = state.get(s['source_id'], {}).get('last_checked', 'mai')
            print(f"  [{s['source_id']}] {s['title']}")
            print(f"    Frequenza: {freq} | Ultimo check: {last}")
            print(f"    URL: {s['url']}")
        print(f"\nFonti NON da controllare: {len(catalog) - len(sources_to_check)}")
        for s in catalog:
            if s not in sources_to_check:
                last = state.get(s['source_id'], {}).get('last_checked', 'mai')
                print(f"  [{s['source_id']}] ultimo check: {last}")
        return

    if not sources_to_check:
        logger.info("Nessuna fonte da controllare in questo ciclo.")
        print("Nessuna fonte da controllare. Usa --force per forzare il controllo.")
        return

    # Esegui i controlli
    results = []
    checked_ids = set()

    for i, source in enumerate(sources_to_check, 1):
        source_id = source['source_id']
        logger.info(f"[{i}/{len(sources_to_check)}] Controllo {source_id}...")

        check_result = check_source(source, state, logger)

        # check_source ritorna (result, new_state) oppure solo result per skip/errori
        if isinstance(check_result, tuple):
            result, new_state = check_result
            state[source_id] = new_state
        else:
            result = check_result
            # Per fonti skippate/errori, aggiorna solo last_checked
            if source_id not in state:
                state[source_id] = {}
            state[source_id]['last_checked'] = TODAY

        results.append(result)
        checked_ids.add(source_id)

        # Rate limiting tra le richieste
        if i < len(sources_to_check):
            time.sleep(args.delay)

    # Salva stato aggiornato
    save_state(state)
    logger.info(f"Stato salvato: {STATE_FILE}")

    # Aggiorna last_checked nel catalogo CSV
    update_catalog_last_checked(checked_ids)
    logger.info(f"Catalogo aggiornato: {CATALOG_PATH}")

    # Genera e stampa report
    report = generate_report(results, logger)
    print_summary(report)

    logger.info("Controllo completato.")


if __name__ == '__main__':
    main()
