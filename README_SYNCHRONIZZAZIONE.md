# Sincronizzazione dati ↔ HTML

- **Fonte di verita'**: `data/dati_farmaci.json` (1746 record, 408 variazioni)
- **Snapshot versionato qui**: `dati_farmaci.json` (copia generata automaticamente)
- **Marker di aggiornamento negli HTML**: 796 occorrenze `[agg. <data> – <fonte>]`
- **Rigenerazione**: `python3 scripts/sync_html_da_json.py --apply`
- **Ultima sincronizzazione**: 2026-11-11T11:34:58

Il sito statico non dipende dal JSON: il JSON serve per tracciare la versione dei dati
da cui sono state generate le pagine e per rigenerarle in futuro.
