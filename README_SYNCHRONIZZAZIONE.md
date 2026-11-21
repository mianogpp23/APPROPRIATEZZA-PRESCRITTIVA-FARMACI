# Sincronizzazione dati ↔ HTML

- **JSON canonico (layout clone/root attuale)**: `dati_farmaci.json` (1744 record, 406 variazioni in 325 record).
- **Risoluzione percorso**: `scripts/config.py` preferisce `data/dati_farmaci.json` se presente, altrimenti usa il root; gli script leggono il percorso da config.
- **Marker di aggiornamento negli HTML**: 186 occorrenze `[agg. <data> – <fonte>]` (dato storico nel file).
- **Rigenerazione (dry-run prima)**: `python3 scripts/sync_html_da_json.py --dry-run` poi `--apply` solo dopo verifica.
- **Ultima sincronizzazione registrata nel file**: 2026-11-20T06:38:09

Il sito statico non dipende dal JSON: il JSON serve per tracciare la versione dei dati
da cui sono state generate le pagine e per rigenerarle in futuro.
