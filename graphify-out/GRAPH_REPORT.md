# Graph Report - dpc-repo  (2026-11-15)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 223 nodes · 531 edges · 10 communities (9 shown, 1 thin omitted)
- Extraction: 99% EXTRACTED · 1% INFERRED · 0% AMBIGUOUS · INFERRED: 7 edges (avg confidence: 0.85)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `e431126c`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- json
- sync_html_da_json.py
- re
- estrai_2023.py
- ricostruisci_nota99.py
- audit_estratore_vs_json.py
- build_dpc_convenzionata.py
- aggiorna_norme_2026.py
- consent.js
- theme.js

## God Nodes (most connected - your core abstractions)
1. `sync_page()` - 13 edges
2. `main()` - 13 edges
3. `esc()` - 7 edges
4. `insert_missing_rows()` - 7 edges
5. `main()` - 7 edges
6. `render_note()` - 7 edges
7. `extract_diretta()` - 7 edges
8. `extract_nota99()` - 7 edges
9. `main()` - 7 edges
10. `main()` - 6 edges

## Surprising Connections (you probably didn't know these)
- `export_rows()` --calls--> `re`  [EXTRACTED]
  scripts/applicazione/aggiorna_convenzionata.py →   _Bridges community 0 → community 2_
- `main()` --calls--> `json`  [EXTRACTED]
  scripts/applicazione/estrai_2023.py →   _Bridges community 3 → community 0_
- `main()` --calls--> `pdfplumber`  [EXTRACTED]
  scripts/applicazione/estrai_2023.py →   _Bridges community 3 → community 4_
- `norm()` --calls--> `re`  [EXTRACTED]
  scripts/applicazione/estrai_2023.py →   _Bridges community 3 → community 2_
- `clean()` --calls--> `re`  [EXTRACTED]
  scripts/applicazione/ricostruisci_nota99.py →   _Bridges community 4 → community 2_

## Import Cycles
- None detected.

## Communities (10 total, 1 thin omitted)

### Community 0 - "json"
Cohesion: 0.10
Nodes (17): main(), export_rows(), main(), main(), main(), variazione(), main(), patch_html() (+9 more)

### Community 1 - "sync_html_da_json.py"
Cohesion: 0.09
Nodes (25): apply_note_pagina(), apply_pillole_pagina(), build_row(), cells_of(), contesto_riga(), esc(), indice_pagine(), insert_missing_rows() (+17 more)

### Community 2 - "re"
Cohesion: 0.10
Nodes (15): main(), repl_style(), tokenize(), main(), normalizza(), testo_pdf(), main(), note_citate() (+7 more)

### Community 3 - "estrai_2023.py"
Cohesion: 0.15
Nodes (13): band_chars(), bucket_text(), check_pause(), classify(), extract_diretta(), extract_dpc(), extract_nota99(), hbands() (+5 more)

### Community 4 - "ricostruisci_nota99.py"
Cohesion: 0.17
Nodes (12): clean(), extract_table(), main(), clean(), colonne_header(), main(), norm(), righe_pagina() (+4 more)

### Community 5 - "audit_estratore_vs_json.py"
Cohesion: 0.13
Nodes (4): main(), pulisci(), norm(), tok()

### Community 6 - "build_dpc_convenzionata.py"
Cohesion: 0.31
Nodes (6): esc(), main(), confezioni(), riga(), norm_cella(), tabelle_pdf()

### Community 7 - "aggiorna_norme_2026.py"
Cohesion: 0.29
Nodes (6): main(), patch_html(), fix_row(), repl(), patch_records(), rules_for_note()

### Community 9 - "theme.js"
Cohesion: 0.67
Nodes (5): apply(), build(), current(), propagate(), saved()

## Knowledge Gaps
- **1 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Should `json` be split into smaller, more focused modules?**
  _Cohesion score 0.10459183673469388 - nodes in this community are weakly interconnected._
- **Should `sync_html_da_json.py` be split into smaller, more focused modules?**
  _Cohesion score 0.09390243902439024 - nodes in this community are weakly interconnected._
- **Should `re` be split into smaller, more focused modules?**
  _Cohesion score 0.10252100840336134 - nodes in this community are weakly interconnected._
- **Should `estrai_2023.py` be split into smaller, more focused modules?**
  _Cohesion score 0.1455026455026455 - nodes in this community are weakly interconnected._
- **Should `audit_estratore_vs_json.py` be split into smaller, more focused modules?**
  _Cohesion score 0.13071895424836602 - nodes in this community are weakly interconnected._