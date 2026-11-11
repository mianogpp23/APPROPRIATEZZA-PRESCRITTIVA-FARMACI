#!/usr/bin/env python3
"""Audit geometrico (per coordinate x) delle tabelle DPC senza linee verticali.

Le pagine 42-56 (farmaci in DPC) e 58-62 (distribuzione diretta) hanno solo bordi orizzontali:
pdfplumber.find_tables() unisce quindi tutto in una cella. Qui si lavora a livello di parole:
ogni parola viene assegnata alla colonna il cui intestazione (x0) e' il piu' vicino a sinistra.
Confronto finale riga per riga con data/dati_farmaci.json.
Uso: python3 audit_geometrico_dpc.py
"""
from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from pathlib import Path

import pdfplumber

ROOT = Path(__file__).resolve().parents[2]
PDF = ROOT / "docs" / "dpc" / "Controllo-appropriatezza-prescrittiva.pdf"
JSON_PATH = ROOT / "data" / "dati_farmaci.json"

SPEC = {
    "farmaci_dpc": {
        "pagine": range(42, 57),
        "header": ["Minsan", "Descrizione", "Principio", "PT"],
        "campi": {"descrizione": 1, "principio_attivo": 2, "note": 3},
    },
    "distribuzione_diretta": {
        "pagine": range(58, 63),
        "header": ["AIC", "Farmaco", "ATC", "Principio", "PT"],
        "campi": {"descrizione": 1, "atc": 2, "principio_attivo": 3, "note": 4},
    },
}


def clean(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").replace("\n", " ")).strip()


def norm(s: str) -> str:
    s = clean(s).replace(" ", " ")
    for a, b in (("’", "'"), ("‘", "'"), ("“", '"'), ("”", '"'),
                  ("–", "-"), ("—", "-"), (" ", " ")):
        s = s.replace(a, b)
    return s.strip()


def righe_pagina(page) -> list[list[dict]]:
    words = page.extract_words()
    rows: list[list[dict]] = []
    for w in sorted(words, key=lambda x: (x["top"], x["x0"])):
        placed = False
        for r in rows:
            if abs(r[0]["top"] - w["top"]) <= 3:
                r.append(w)
                placed = True
                break
        if not placed:
            rows.append([w])
    return rows


def colonne_header(rows) -> list[float]:
    """x0 delle intestazioni di colonna (dal primo header trovato)."""
    for r in rows:
        txt = " ".join(w["text"] for w in r).upper()
        if ("MINSAN" in txt or "AIC" in txt) and ("DESCRIZIONE" in txt or "FARMACO" in txt):
            cols = []
            for w in sorted(r, key=lambda x: x["x0"]):
                t = w["text"].upper()
                if t in ("MINSAN", "AIC", "DESCRIZIONE", "FARMACO", "PRINCIPIO", "ATIVO", "ATTIVO", "PT/SM/NOT", "PT/NOTA", "NOTA", "PT"):
                    cols.append(w["x0"])
            if len(cols) >= 3:
                return cols
    return []


def main() -> int:
    data = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    by_elenco = defaultdict(list)
    for r in data:
        by_elenco[r.get("elenco")].append(r)

    problemi = 0
    for elenco, spec in SPEC.items():
        pdf_rows: dict[str, list[str]] = {}
        with pdfplumber.open(PDF) as pdf:
            for p in spec["pagine"]:
                page = pdf.pages[p - 1]
                rows = righe_pagina(page)
                cols = colonne_header(rows)
                if not cols:
                    continue
                bounds = cols[1:]  # x di inizio delle colonne 2..n
                for r in rows:
                    if not r or not re.fullmatch(r"\d{9}", r[0]["text"]):
                        continue
                    cells = [[] for _ in range(len(bounds) + 1)]
                    for w in sorted(r, key=lambda x: x["x0"]):
                        col = 0
                        for i, b in enumerate(bounds):
                            if w["x0"] >= b - 3:
                                col = i + 1
                        cells[col].append(w["text"])
                    pdf_rows[r[0]["text"]] = [" ".join(c).strip() for c in cells]

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
            for field, idx in spec["campi"].items():
                got = norm(rec.get(field) or "")
                want = norm(row[idx] if idx < len(row) else "")
                if got != want:
                    diffs.append((a, field, want, got))
        print(f"\n### {elenco}: record JSON {len(recs)} | righe PDF {len(pdf_rows)}")
        print(f"    record senza riga nel PDF: {len(mancanti)} | righe PDF senza record: {len(extra)} | celle diverse: {len(diffs)}")
        for a in mancanti[:6]:
            print(f"      SOLO-NEL-JSON {a} {str(json_by_aic[a].get('descrizione'))[:42]}")
        for a in extra[:6]:
            print(f"      SOLO-NEL-PDF  {a} {(pdf_rows[a][1] if len(pdf_rows[a])>1 else '')[:42]}")
        for d in diffs[:14]:
            print(f"      DIFF {d[0]} [{d[1]}]\n            PDF : {d[2][:80]}\n            JSON: {d[3][:80]}")
        problemi += len(mancanti) + len(extra) + len(diffs)

    print(f"\n=== TOTALE incoerenze: {problemi} ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
