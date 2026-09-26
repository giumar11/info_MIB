# ISS - Istituto Superiore di Sanità

## Fonte
- **Istituzione**: ISS - Istituto Superiore di Sanità
- **URL**: https://www.iss.it/
- **Sorveglianza PASSI**: https://www.epicentro.iss.it/passi/

## Contenuto atteso
Report e dati della sorveglianza PASSI (Progressi delle Aziende Sanitarie per
la Salute in Italia) su stili di vita, fattori di rischio comportamentali e
adesione a programmi di prevenzione della popolazione adulta (18-69 anni).

## Download
I documenti originali vengono scaricati automaticamente dalla pipeline di
enrichment giornaliera:

```bash
python3 scripts/daily_enrichment_pipeline.py --category surveillance
```

I PDF/dati originali non sono ancora presenti nel repository (download in
attesa); questa directory è il target di destinazione previsto dal catalogo
`sources_catalog.csv` (source_id `PASSI_001`).
