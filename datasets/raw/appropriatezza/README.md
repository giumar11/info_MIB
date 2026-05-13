# Appropriatezza e inappropriatezza prescrittiva

Catalogo strutturato delle fonti primarie istituzionali sull'**appropriatezza prescrittiva** in Italia, con focus su livello nazionale (Ministero della Salute, ISS, AGENAS, AIFA) e sulla **Regione Puglia** (atti regionali, studi AReSS).

L'arricchimento di questa sezione nasce dall'articolo de Il Sole 24 Ore *"Liste d'attesa, troppe ricette per visite ed esami: parte la caccia all'appropriatezza"* (codice articolo `AIAwJSTC`), che riporta i numeri-chiave:

- **20%** delle visite ed esami richiesti in Italia è considerato **inappropriato** (dichiarazione Ministro Schillaci) → circa **20 miliardi di euro/anno** di spesa potenzialmente non necessaria.
- Studio AReSS Puglia su **17.000+ prescrizioni**: solo **38,9%** pienamente appropriate, **43%** generalmente inappropriate.
- **1.569,5** prescrizioni per 1.000 abitanti nel Lazio (2025), contro **889,7** in Veneto e **1.328,4** in Puglia.

## Struttura della cartella

| Sotto-cartella | Contenuto |
|---|---|
| [`ministero_salute/`](ministero_salute/) | Decreti ministeriali, decreti-legge, leggi statali, circolari |
| [`regione_puglia/`](regione_puglia/) | Deliberazioni di Giunta Regionale (DGR), piani regionali, linee guida operative |
| [`iss/`](iss/) | Sistema Nazionale Linee Guida (SNLG) e manuali metodologici |
| [`aress_puglia/`](aress_puglia/) | Studi e progetti AReSS Puglia (incluso algoritmo AI su appropriatezza diagnostica) |

## Cornice concettuale

L'appropriatezza prescrittiva si misura lungo tre assi:

1. **Appropriatezza clinica** — la prestazione è indicata per la condizione del paziente in base a evidenze scientifiche / linee guida (SNLG-ISS).
2. **Appropriatezza organizzativa** — la prestazione è erogata nel setting più idoneo (ambulatoriale vs. ricovero, classe di priorità RAO U/B/D/P).
3. **Appropriatezza prescrittiva (regolatoria)** — la prestazione rispetta le condizioni di erogabilità a carico SSN definite dal DM 9/12/2015 e successive integrazioni nei LEA (DPCM 12/1/2017).

## Strumenti di misurazione attuali

| Strumento | Ente | Granularità |
|---|---|---|
| Tessera Sanitaria — Ricetta Dematerializzata | MEF / Sogei | Prescrizione singola |
| Quesito diagnostico ICD-9-CM in ricetta | Ministero / DL 73/2024 | Prescrizione singola |
| Sistema TS — Monitoraggio condizioni di erogabilità | MEF / Ministero Salute | Prescrizione singola |
| Piattaforma Nazionale Liste d'Attesa (PNLA) | AGENAS | ASL / Regione |
| Note AIFA | AIFA | Farmaci |
| Indicatori OsMed | AIFA | Spesa farmaceutica regionale |

## Riferimenti articolo

- Il Sole 24 Ore — Versione italiana (paywall): `https://www.ilsole24ore.com/art/liste-d-attesa-troppe-ricette-visite-ed-esami-parte-caccia-appropriatezza-AIAwJSTC`
- Il Sole 24 Ore — Versione inglese: `https://en.ilsole24ore.com/art/waiting-lists-too-many-prescriptions-visits-and-examinations-part-of-the-hunt-for-appropriateness-AIAwJSTC`

> **Nota tecnica:** in questa sandbox il download diretto di PDF istituzionali (Gazzetta Ufficiale, sanita.puglia.it, sistemats1, iss.it) restituisce HTTP 403. I documenti sono pertanto catalogati con URL canonici, metadati completi e citazioni testuali; il download può essere effettuato manualmente dagli URL elencati nei singoli README.
