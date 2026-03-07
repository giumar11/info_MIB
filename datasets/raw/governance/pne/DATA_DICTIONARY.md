# Data Dictionary - Programma Nazionale Esiti (PNE)

**Fonte:** AGENAS
**ID Fonte:** PNE_001
**URL:** https://pne.agenas.it/

---

Questo documento descrive la struttura e le variabili dei dati esportabili dal Programma Nazionale Esiti (PNE), che misura la performance degli ospedali italiani su un set di indicatori di esito, processo e volume.

## Dataset Esportabili

I dati sono esportabili in formato CSV/Excel direttamente dalla dashboard del PNE. La struttura del file esportato dipende dagli indicatori e dai filtri selezionati. Di seguito è riportata una struttura tipica.

| Nome Colonna | Tipo Dati | Descrizione | Esempio |
|---|---|---|---|
| `Anno` | Integer | Anno di riferimento | 2023 |
| `Codice Struttura` | String | Codice univoco della struttura ospedaliera | 030101 |
| `Denominazione Struttura` | String | Denominazione della struttura ospedaliera | PRESIDIO OSPEDALIERO DI SONDRIO |
| `Regione` | String | Regione della struttura | Lombardia |
| `Area Clinica` | String | Area clinica dell'indicatore | Cardiovascolare |
| `Indicatore` | String | Descrizione dell'indicatore | Mortalità a 30 giorni dall'infarto miocardico acuto (IMA) |
| `Tipo Indicatore` | String | Tipologia (Esito, Processo, Volume) | Esito |
| `Numeratore` | Integer | Numero di eventi osservati (es. decessi) | 15 |
| `Denominatore (Popolazione)` | Integer | Popolazione di riferimento (es. pazienti con IMA) | 300 |
| `Esito Aggiustato` | Float | Valore dell'indicatore aggiustato per fattori di rischio | 5.2 |
| `Limite Inferiore` | Float | Limite inferiore dell'intervallo di confidenza | 4.1 |
| `Limite Superiore` | Float | Limite superiore dell'intervallo di confidenza | 6.3 |
| `Benchmark` | Float | Valore di riferimento nazionale o internazionale | 4.5 |
| `Livello di Performance` | String | Classificazione della performance (Molto Buono, Buono, Medio, Basso, Molto Basso) | Medio |

---

## Note Metodologiche

- **Aggiustamento per Rischio**: Gli indicatori di esito sono quasi sempre "aggiustati" per tenere conto delle differenze nella complessità dei pazienti trattati (età, sesso, comorbidità). Questo permette un confronto più equo tra ospedali.
- **Volumi Minimi**: Il PNE monitora anche il rispetto delle soglie minime di volume per procedure complesse (es. interventi chirurgici oncologici), come previsto dal DM 70/2015.
- **Equità**: Una sezione specifica del PNE analizza le disuguaglianze di esito in base al livello socio-economico dei pazienti.
