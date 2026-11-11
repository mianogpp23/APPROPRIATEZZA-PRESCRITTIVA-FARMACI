# Sincronizzazione dati ↔ HTML

- **Fonte di verita'**: `/media/k10/BTRFS 741/dpc/data/dati_farmaci.json` (1746 record, 408 variazioni)
- **Snapshot versionato qui**: `dati_farmaci.json` (copia generata automaticamente)
- **Marker di aggiornamento negli HTML**: 796 occorrenze `[agg. <data> – <fonte>]`
- **Rigenerazione**: `python3 scripts/sync_html_da_json.py --apply`
- **Ultima sincronizzazione**: 2026-11-11T09:18:46

Il sito statico non dipende dal JSON: il JSON serve per tracciare la versione dei dati
da cui sono state generate le pagine e per rigenerarle in futuro.
