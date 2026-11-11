#!/usr/bin/env python3
"""Corregge il raggruppamento delle righe usato dagli ordinamenti delle tabelle del sito DPC.

Il bug: groupRows() accorpava tutte le righe farmaco consecutive in un SOLO gruppo, quindi
l'ordinamento non aveva nulla da riordinare (il click cambiava solo l'icona della colonna).
Correzione: ogni riga farmaco e' un gruppo indipendente; le righe di nota restano agganciate
alla riga farmaco che le precede.

Uso: python3 fix_sorting_gruppi.py [--dry-run]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

HTML = ROOT / "html_estratto"

# variante con array drugs (usata dal filtro)
OLD_A = """            if (row.classList.contains("note")) {
                if (current) { current.rows.push(row); groups.push(current); current = null; }
                else { groups.push({ rows: [row], drugs: [] }); }
            } else {
                if (!current) current = { rows: [], drugs: [] };
                current.rows.push(row);
                current.drugs.push(row);
            }"""
NEW_A = """            if (row.classList.contains("note")) {
                // la riga di nota resta agganciata alla riga farmaco che la precede
                if (current) { current.rows.push(row); }
                else { current = { rows: [row], drugs: [] }; groups.push(current); }
            } else {
                // ogni riga farmaco e' un gruppo indipendente: accorpandole tutte in uno solo
                // l'ordinamento non avrebbe nulla da riordinare
                current = { rows: [row], drugs: [row] };
                groups.push(current);
            }"""

# variante senza array drugs (usata dall'ordinamento)
OLD_B = """            if (row.classList.contains("note")) {
                if (current) { current.rows.push(row); groups.push(current); current = null; }
                else { groups.push({ rows: [row] }); }
            } else {
                if (!current) current = { rows: [] };
                current.rows.push(row);
            }"""
NEW_B = """            if (row.classList.contains("note")) {
                // la riga di nota resta agganciata alla riga farmaco che la precede
                if (current) { current.rows.push(row); }
                else { current = { rows: [row] }; groups.push(current); }
            } else {
                // ogni riga farmaco e' un gruppo indipendente: accorpandole tutte in uno solo
                // l'ordinamento non avrebbe nulla da riordinare
                current = { rows: [row] };
                groups.push(current);
            }"""

PAGINE = ["farmaci_dpc.html", "distribuzione_diretta.html", "nota_99.html", "metilfenidato.html"]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    tot = 0
    for nome in PAGINE:
        p = HTML / nome
        s = p.read_text(encoding="utf-8")
        na = s.count(OLD_A)
        nb = s.count(OLD_B)
        s2 = s.replace(OLD_A, NEW_A).replace(OLD_B, NEW_B)
        if s2 != s:
            tot += na + nb
            print(f"  {nome}: corretti {na} blocchi con drugs, {nb} blocchi semplici")
            if not args.dry_run:
                p.write_text(s2, encoding="utf-8")
        else:
            print(f"  {nome}: nessun blocco da correggere")
    print(f"totale blocchi corretti: {tot}" + ("  [DRY-RUN]" if args.dry_run else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
