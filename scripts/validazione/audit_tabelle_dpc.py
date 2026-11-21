#!/usr/bin/env python3
"""Audit geometrico delle tabelle DPC contro i dati (dati_farmaci.json).

Ri-estrae ogni tabella dal PDF con pdfplumber.find_tables() e la confronta riga per riga con i
record JSON: segnala differenze nelle colonne, record mancanti e righe in piu'.
Uso: python3 audit_tabelle_dpc.py
"""
from __future__ import annotations
import sys as _sys
from pathlib import Path as _Path
_REPO_ROOT = _Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in _sys.path:
    _sys.path.insert(0, str(_REPO_ROOT))
from scripts.config import ROOT, HTML, JSON, DOCS, PDF_DPC

# Fase 1: guard --help/--dry-run per evitare esecuzioni accidentali su path mancanti
import sys as _sys_guard
if any(a in ('--help', '-h') for a in _sys_guard.argv[1:]):
    print(f'Uso: python3 {_sys_guard.argv[0]} [opzioni]')
    print('Script storico/applicativo: vedere docstring e README_SYNCHRONIZZAZIONE.md')
    raise SystemExit(0)


import json
import re
import sys
from collections import defaultdict
from pathlib import Path

import pdfplumber

# ROOT fornito da scripts.config
PDF = PDF_DPC or (DOCS / "dpc-controllo-appropriatezza.pdf")  # da scripts.config
JSON_PATH = JSON
# elenco -> (pagine 1-based, [(indice cella, campo json)], etichetta)
TABELLE = {
    "farmaci_dpc":       (range(42, 57), [(1, "descrizione"), (2, "principio_attivo"), (3, "note")], "Minsan|Descrizione|Principio Attivo|PT"),
    "distribuzione_diretta": (range(58, 63), [(1, "descrizione"), (2, "atc"), (3, "principio_attivo"), (4, "note")], "AIC|Farmaco|ATC|Principio Attivo|PT"),
}


def clean(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").replace("\n", " ")).strip()


def norm(s: str) -> str:
    s = clean(s)
    s = s.replace(" ", " ").replace("’", "'").replace("‘", "'")
    s = s.replace("“", '"').replace("”", '"').replace("–", "-").replace("—", "-")
    return s.strip()


def estrai(pagine) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    with pdfplumber.open(PDF) as pdf:
        for p in pagine:
            page = pdf.pages[p - 1]
            for t in page.find_tables():
                for row in t.extract():
                    if not row or not row[0]:
                        continue
                    code = clean(row[0])
                    if not re.fullmatch(r"\d{9}", code):
                        continue
                    out[code] = [clean(c) for c in row]
    return out


def main() -> int:
    data = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    by_elenco = defaultdict(list)
    for r in data:
        by_elenco[r.get("elenco")].append(r)

    problemi = 0
    for elenco, (pagine, cols_map, _) in TABELLE.items():
        pdf_rows = estrai(pagine)
        recs = by_elenco.get(elenco, [])
        json_by_aic = {}
        for r in recs:
            a = str(r.get("aic") or r.get("minsan") or "").strip()
            if a:
                json_by_aic.setdefault(a, r)
        mancanti = [a for a in json_by_aic if a not in pdf_rows]
        extra = [a for a in pdf_rows if a not in json_by_aic]
        diffs = []
        for a, rec in json_by_aic.items():
            row = pdf_rows.get(a)
            if not row:
                continue
            for idx, field in cols_map:
                if idx >= len(row):
                    continue
                got = norm(rec.get(field) or "")
                want = norm(row[idx])
                if got != want:
                    diffs.append((a, field, want[:70], got[:70]))
        print(f"\n### {elenco}: record JSON {len(recs)} | righe PDF {len(pdf_rows)}")
        print(f"    record senza riga nel PDF: {len(mancanti)} | righe PDF senza record: {len(extra)} | celle diverse: {len(diffs)}")
        for a in mancanti[:8]:
            print(f"      SOLO-NEL-JSON {a} {str(json_by_aic[a].get('descrizione'))[:40]}")
        for a in extra[:8]:
            print(f"      SOLO-NEL-PDF  {a} {pdf_rows[a][1][:44] if len(pdf_rows[a])>1 else ''}")
        for d in diffs[:12]:
            print(f"      DIFF {d[0]} [{d[1]}]\n            PDF : {d[2]}\n            JSON: {d[3]}")
        problemi += len(mancanti) + len(extra) + len(diffs)

    print(f"\n=== TOTALE incoerenze: {problemi} ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
