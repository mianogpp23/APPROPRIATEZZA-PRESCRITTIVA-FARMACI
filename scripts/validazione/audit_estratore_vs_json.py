#!/usr/bin/env python3
"""Audit definitivo: re-estrae le tabelle DPC con l'estrattore geometrico del progetto
(scripts/estrai_2023.py) e le confronta riga per riga con data/dati_farmaci.json.

Le differenze attese sono solo i marker di aggiornamento '[agg. ...]' aggiunti alle note:
vengono rimossi dal lato JSON prima del confronto.
Uso: python3 audit_estratore_vs_json.py
"""
from __future__ import annotations

import importlib.util
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
spec = importlib.util.spec_from_file_location("estrai_2023", HERE / "estrai_2023.py")
E = importlib.util.module_from_spec(spec)
spec.loader.exec_module(E)

DATA = json.loads((ROOT / "data" / "dati_farmaci.json").read_text(encoding="utf-8"))
MARK = re.compile(r"\s*\[agg\.[^\]]*\]")


def pulisci(s: str) -> str:
    s = MARK.sub("", s or "")
    s = re.sub(r"\s+", " ", s).strip()
    return s


def main() -> int:
    import pdfplumber
    anomalies = []
    pdf_rows = {}
    with pdfplumber.open(str(ROOT / "docs" / "dpc" / "Controllo-appropriatezza-prescrittiva.pdf")) as pdf:
        for pno in range(42, 57):
            for r in E.extract_dpc(pdf.pages[pno - 1], pno, anomalies):
                pdf_rows[r["minsan"]] = ("farmaci_dpc", r)
        for pno in range(58, 63):
            for r in E.extract_diretta(pdf.pages[pno - 1], pno, anomalies):
                pdf_rows[r["minsan"]] = ("distribuzione_diretta", r)
        for pno in range(66, 68):
            for r in E.extract_nota99(pdf.pages[pno - 1], pno, anomalies):
                pdf_rows[r["minsan"]] = ("nota_99", r)
    print(f"[pdf] righe estratte: {len(pdf_rows)} | anomalie del parser: {len(anomalies)}")

    by_elenco = defaultdict(dict)
    for r in DATA:
        a = str(r.get("aic") or r.get("minsan") or "").strip()
        if a:
            by_elenco[r.get("elenco")].setdefault(a, r)

    campi = {
        "farmaci_dpc": ("descrizione", "principio_attivo", "note"),
        "distribuzione_diretta": ("descrizione", "principio_attivo", "note"),
        "nota_99": ("descrizione", "principio_attivo", None),
    }

    tot_diff = tot_manc = tot_extra = 0
    for elenco, campi_elenco in campi.items():
        recs = by_elenco.get(elenco, {})
        pdf_el = {a: v for a, (el, v) in pdf_rows.items() if el == elenco}
        mancanti = [a for a in recs if a not in pdf_el]
        extra = [a for a in pdf_el if a not in recs]
        diffs = []
        for a, rec in recs.items():
            pr = pdf_el.get(a)
            if not pr:
                continue
            for f in campi_elenco:
                if f is None:
                    continue
                got = pulisci(str(rec.get(f) or ""))
                want = pulisci(str(pr.get(f) or ""))
                if got != want:
                    diffs.append((a, f, want, got))
        print(f"\n### {elenco}: JSON {len(recs)} | PDF {len(pdf_el)} | mancanti {len(mancanti)} | extra {len(extra)} | celle diverse {len(diffs)}")
        for a in mancanti[:8]:
            print(f"      SOLO-NEL-JSON {a} {str(recs[a].get('descrizione'))[:44]}")
        for a in extra[:8]:
            print(f"      SOLO-NEL-PDF  {a} {str(pdf_el[a].get('descrizione'))[:44]}")
        for d in diffs[:12]:
            print(f"      DIFF {d[0]} [{d[1]}]\n            PDF : {d[2][:84]}\n            JSON: {d[3][:84]}")
        tot_diff += len(diffs); tot_manc += len(mancanti); tot_extra += len(extra)

    print(f"\n=== TOTALE: celle diverse {tot_diff} | record solo nel JSON {tot_manc} | righe solo nel PDF {tot_extra} ===")
    if anomalies:
        from collections import Counter
        print("anomalie del parser:", dict(Counter(a["tipo"] for a in anomalies)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
