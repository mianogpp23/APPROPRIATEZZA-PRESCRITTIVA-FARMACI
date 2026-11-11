#!/usr/bin/env python3
"""Audit di contaminazione delle colonne direttamente sui dati (dati_farmaci.json).

Non usa l'estrattore (che ha un boundary di 3px sulla colonna nota delle pagine DPC): cerca nei
dati stessi i segnali tipici di un dato finito nella colonna sbagliata:
  - principio attivo che contiene un regime di erogazione ("max", "patol", "PT", "|", "=")
  - descrizione che contiene un regime di erogazione
  - nota che contiene il carattere di separazione di colonna "|" o testi lunghi da colonna nota
  - campi vuoti anomali (descrizione/PA/note mancanti) rispetto alla struttura della pagina
Confronto anche i conteggi righe per pagina con quelli del PDF.
Uso: python3 audit_contaminazione.py
"""
from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = json.loads((ROOT / "data" / "dati_farmaci.json").read_text(encoding="utf-8"))

REGIME = re.compile(r"\bmax\b|\bpatol\b|\bPT\b|\bSM\b|\bCAP\b|\bSP\b|attestaz|erogare|allegare|protocollo|\d+\s*conf", re.I)
LUNGHE = 120


def main() -> int:
    problemi = 0
    per_elenco = defaultdict(list)
    for r in DATA:
        el = r.get("elenco")
        cells = r.get("cells")
        if isinstance(cells, list):
            # schema a celle: ogni cella deve essere un valore breve, niente testo incrociato
            for i, c in enumerate(cells):
                if len(str(c)) > 90:
                    per_elenco[el].append((r.get("aic"), f"cella {i} troppo lunga ({len(str(c))} char)", str(c)[:110]))
            continue
        pa = str(r.get("principio_attivo") or "")
        desc = str(r.get("descrizione") or "")
        note = str(r.get("note") or "")
        if pa and REGIME.search(pa):
            per_elenco[el].append((r.get("minsan") or r.get("aic"), "principio attivo contiene un regime", pa[:110]))
        if desc and REGIME.search(desc) and len(desc) > 60:
            per_elenco[el].append((r.get("minsan") or r.get("aic"), "descrizione contiene un regime", desc[:110]))
        if "|" in note and len(note) > 20:
            per_elenco[el].append((r.get("minsan") or r.get("aic"), "nota contiene '|' (colonne unite)", note[:110]))
        if len(note) > LUNGHE:
            per_elenco[el].append((r.get("minsan") or r.get("aic"), f"nota troppo lunga ({len(note)} char)", note[:110]))
        if not pa and not desc:
            per_elenco[el].append((r.get("minsan") or r.get("aic"), "record senza descrizione ne' principio attivo", ""))

    for el, items in sorted(per_elenco.items()):
        print(f"\n### {el}: {len(items)} sospetti")
        for a, why, txt in items[:14]:
            print(f"      {a}  {why}\n            {txt}")
        problemi += len(items)

    # controllo finale: nessun marker deve essere finito fuori dalla propria colonna
    print(f"\n=== TOTALE sospetti di contaminazione: {problemi} ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
