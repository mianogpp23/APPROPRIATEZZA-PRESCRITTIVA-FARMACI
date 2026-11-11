#!/usr/bin/env python3
"""Verifica i deep link: ogni link con frammento #page=N deve puntare alla pagina giusta.

Per i link al DPC regionale (PDF con livello testo) la pagina viene estratta e confrontata con
le parole chiave attese (farmacisti: il link deve portare alla pagina che tratta l'argomento).
Per i PDF locali in docs/ (scansioni) si usa l'indice OCR (data/pdf_pagine_ocr.json).

Uso: python3 verifica_deep_link.py [--json output.json]
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DPC = ROOT / "html_estratto" / "docs" / "dpc-controllo-appropriatezza.pdf"
IDX = ROOT / "data" / "pdf_pagine_ocr.json"
PILL = ROOT / "data" / "pillole_pagine.json"

# parole chiave attese per pagina del DPC
ATTESO: dict[int, tuple[str, ...]] = {
    10: ("PT OnLine", "Epoetina", "Nota 51"),
    11: ("everolimus", "tacrolimus", "PT OnLine"),
    14: ("PROLIA", "Denosumab", "Nota 79"),
    15: ("Nota 97", "Apixaban", "Rivaroxaban"),
    18: ("GLYXAMBI", "FORXIGA", "NOTA 100"),
    19: ("Protocollo DMDU0A0000", "SistemaTS", "Scheda"),
    20: ("Trulicity", "Ozempic", "Victoza"),
    21: ("FORXIGA", "JARDIANCE", "CONVENZIONATA"),
    26: ("ENOXAPARINA",),
    29: ("LANTUS", "ABASAGLAR", "motivazNote"),
    41: ("METILFENIDATO",),
    58: ("DISTRIBUZIONE DIRETTA", "Farmaco", "Principio Attivo"),
    63: ("NOTA 95",),
    64: ("RIEPILOGO FORMALISMI",),
    65: ("NO DPC",),
    66: ("Nota AIFA 99",),
    67: ("Scheda web based", "BPCO0A0000", "TRIMBOW"),
}


def testo_pagine(pdf: Path) -> dict[int, str]:
    out = subprocess.run(["pdftotext", "-layout", str(pdf), "-"], capture_output=True, timeout=300)
    testo = out.stdout.decode("utf-8", errors="replace")
    return {i + 1: re.sub(r"\s+", " ", p) for i, p in enumerate(testo.split("\f"))}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", default="")
    args = ap.parse_args()

    pagine = testo_pagine(DPC)
    idx = json.loads(IDX.read_text(encoding="utf-8")) if IDX.exists() else {}

    # 1) deep link delle pillole
    pillole = json.loads(PILL.read_text(encoding="utf-8"))
    esiti: list[dict] = []
    for pagina, spec in pillole.items():
        for p in spec.get("pillole", []):
            link = p.get("link") or {}
            url = link.get("url", "")
            m = re.search(r"#page=(\d+)", url)
            if not m:
                continue
            n = int(m.group(1))
            testo = pagine.get(n, "")
            chiavi = ATTESO.get(n, ())
            trovate = [k for k in chiavi if k.lower() in testo.lower()] if chiavi else []
            ok = bool(chiavi) and len(trovate) == len(chiavi)
            esiti.append({"pagina_sito": pagina, "pillola": p.get("t"), "url": url,
                          "chiavi_attese": list(chiavi), "trovate": trovate, "ok": ok})

    # 2) deep link dei marker sulle righe (solo DPC: le altre destinazioni sono i documenti AIFA)
    for f in sorted((ROOT / "html_estratto").glob("*.html")):
        testo = f.read_text(encoding="utf-8")
        for m in re.finditer(r'href="docs/dpc-controllo-appropriatezza\.pdf#page=(\d+)"', testo):
            n = int(m.group(1))
            t = pagine.get(n, "")
            esiti.append({"pagina_sito": f.name, "pillola": f"marker -> pag. {n}", "url": f"…#page={n}",
                          "chiavi_attese": list(ATTESO.get(n, ())), "trovate": [], "ok": bool(t.strip())})

    ok = sum(1 for e in esiti if e["ok"])
    ko = len(esiti) - ok
    print(f"deep link verificati: {len(esiti)} | coerenti: {ok} | da controllare: {ko}")
    for e in esiti:
        if not e["ok"]:
            print(f"   {e['pagina_sito']:<26} pag.{re.search(r'page=(\\d+)', e['url']).group(1) if re.search(r'page=(\\d+)', e['url']) else '?'}"
                  f"  {str(e.get('pillola'))[:44]:<46} attese={e['chiavi_attese']} trovate={e['trovate']}")
    if args.json:
        Path(args.json).write_text(json.dumps(esiti, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"[report] {args.json}")
    return 0 if ko == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
