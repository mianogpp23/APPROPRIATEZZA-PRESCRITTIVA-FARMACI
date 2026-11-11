#!/usr/bin/env python3
"""Rende portabili gli script del progetto: la radice non e' piu' un percorso assoluto.

Gli script risolvono la cartella di progetto a partire dalla propria posizione
(Path(__file__).resolve().parents[N]), cosi' funzionano da qualsiasi checkout e non pubblicano
il percorso della macchina (il repository e' pubblico).

Uso: python3 rendi_portabili.py [--dry-run]
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"

# sostituzioni letterali dei percorsi assoluti
SOSTITUZIONI = {
    'ROOT / "html_estratto"': 'ROOT / "html_estratto"',
    'ROOT / "docs" / "dpc" / "Controllo-appropriatezza-prescrittiv1a.pdf"':
        'ROOT / "docs" / "dpc" / "Controllo-appropriatezza-prescrittiv1a.pdf"',
    'ROOT': 'ROOT',
    'str(ROOT / "html_estratto")': 'str(ROOT / "html_estratto")',
    'str(ROOT / "data" / "dati_farmaci.json")': 'str(ROOT / "data" / "dati_farmaci.json")',
    'str(ROOT)': 'str(ROOT)',
    'scripts': 'scripts',
}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    toccati = 0
    for p in sorted(SCRIPTS.rglob("*.py")):
        s = p.read_text(encoding="utf-8")
        orig = s
        profondita = len(p.relative_to(SCRIPTS).parts) - 1   # 0 = scripts/, 1 = scripts/sotto/
        for a, b in SOSTITUZIONI.items():
            s = s.replace(a, b)
        if 'ROOT = Path(__file__).resolve().parents[1]' in s:
            s = s.replace('ROOT = Path(__file__).resolve().parents[1]',
                           f'ROOT = Path(__file__).resolve().parents[{profondita + 1}]')
        if s != orig:
            toccati += 1
            print(f"  {p.relative_to(ROOT)}")
            if not args.dry_run:
                p.write_text(s, encoding="utf-8")
    # il sorgente del report AIFA sta fuori dal progetto: lo rendo opzionale e dichiarato
    print(f"script toccati: {toccati}" + ("  [DRY-RUN]" if args.dry_run else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
