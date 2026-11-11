#!/usr/bin/env python3
"""Marca come 'in convenzionata dal 15/10/2025' le confezioni dei farmaci di diabete tipo 2
a Nota AIFA 100 elencati nella circolare Federfarma Sicilia n. 90 del 15/10/2025.

Fonte regolamentare:
  - Determine AIFA del 2 luglio 2025, G.U. n. 153 del 4 luglio 2025 (riclassificazione A-PHT -> A)
  - D.A. n. 367/2025 del 3 aprile 2025 (Accordo per la Distribuzione Per Conto dei farmaci di cui al PHT)
  - nota prot. Assessorato Salute - Servizio 7 n. 34212 del 18 luglio 2025
  - circolare Federfarma Sicilia n. 90 del 15 ottobre 2025 (prot. PRES. TS n. 218)
Regola operativa: non compilare e allegare la Scheda di Valutazione e Prescrizione, non verificare
la presenza del Protocollo DMDU, erogare nel canale della Convenzionata con ricetta a Nota AIFA 100.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
JSON_PATH = ROOT / "data" / "dati_farmaci.json"
# export AIFA "Nota 100 obbligatoria": percorso configurabile (fuori dal progetto).
# Se assente il generatore continua con i dati delle liste regionali.
EXPORT = Path(os.environ.get("DPC_EXPORT_NOTA100",
                     str(ROOT / "docs" / "fonti_normative" / "export-nota100-obbligatoria.md")))

GU153 = "https://www.gazzettaufficiale.it/eli/id/2025/07/04/153G0001/singola"
MARKER = (" [agg. 15/10/2025 – Fed. Sicilia 90/2025] in convenzionata dal 15/10/2025: "
          "non compilare e allegare la Scheda di Valutazione e Prescrizione, non verificare il Protocollo "
          "DMDU, erogare nel canale della Convenzionata con ricetta a Nota AIFA 100")
VAR = {
    "data": "15/10/2025",
    "fonte": "circolare Federfarma Sicilia n. 90 del 15/10/2025 – nota prot. Assessorato 34212 del 18/07/2025 "
              "– D.A. 367/2025 – Determine AIFA del 02/07/2025 (G.U. n. 153 del 04/07/2025)",
    "url_o_percorso": GU153,
    "testo_breve": "Farmaci di diabete tipo 2 a Nota AIFA 100 passati in convenzionata dal 15/10/2025: "
                   "niente Scheda di Valutazione e Prescrizione, niente Protocollo DMDU, erogazione in "
                   "canale Convenzionata con ricetta a Nota AIFA 100",
    "stato": "approvata",
}

# i nomi commerciali della tabella ufficiale (dal testo della circolare)
BRANDS = [
    "VIPIDIA", "TRAJENTA", "ONGLYZA", "JANUVIA", "MELIGLIX", "SITAGLIPTIN", "TESAVEL", "XELEVIA",
    "GALVUS", "VILDAGLIPTIN", "XILIARX", "VIPDOMET", "JENTADUETO", "KOMBOGLYZE", "DIESMIT", "EFFICIB",
    "JANUMET", "VELMETIA", "EUCREAS", "ZOMARIST", "INCRESYNC", "GLYXAMBI", "STEGLUJAN", "QTERN",
    "INVOKANA", "FORXIGA", "JARDIANCE", "STEGLATRO", "VOKANAMET", "EBYMECT", "XIGDUO", "SEGLUROMET",
    "SYNJARDY",
]


def export_rows() -> dict[str, tuple[str, str]]:
    """AIC -> (descrizione, Nota 100 obbligatoria Si/No) dall'export AIFA."""
    out: dict[str, tuple[str, str]] = {}
    if EXPORT.exists():
        txt = EXPORT.read_text(encoding="utf-8")
        for m in re.finditer(r"^(\d{9,10})\s*\|\s*([^|]+?)\s*\|\s*(Si|No)\s*$", txt, re.M):
            out[m.group(1)] = (m.group(2).strip(), m.group(3))
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    if not args.apply and not args.dry_run:
        ap.error("specificare --dry-run o --apply")

    data = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    exp = export_rows()

    # AIC delle confezioni dei prodotti in convenzionata (dal export AIFA)
    target_aics: dict[str, str] = {}
    for aic, (desc, flag) in exp.items():
        for b in BRANDS:
            if re.search(r"\b" + re.escape(b) + r"\b", desc, re.I):
                target_aics[aic] = desc
                break

    changed = []
    for r in data:
        aic = str(r.get("aic") or r.get("minsan") or "").strip()
        if aic not in target_aics:
            continue
        nota = r.get("note") or ""
        cells = r.get("cells") or []
        testo = nota if nota else (" ".join(map(str, cells)) if cells else "")
        if "agg. 15/10/2025" in testo:
            continue
        if nota:
            r["note"] = nota + MARKER
        elif cells:
            cells[-1] = str(cells[-1]) + MARKER
        else:
            continue
        r.setdefault("variazioni", []).append(dict(VAR))
        changed.append((aic, r.get("elenco"), str(r.get("descrizione") or "")[:38]))

    print(f"[JSON] record marcati 'in convenzionata dal 15/10/2025': {len(changed)}")
    for aic, el, desc in changed:
        print(f"    {aic:<10} {el:<20} {desc}")

    if args.dry_run:
        print("\n[DRY-RUN] nessuna scrittura.")
        return 0

    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    backup = ROOT / "output" / f"backup-convenzionata-{stamp}"
    backup.mkdir(parents=True, exist_ok=True)
    shutil.copy2(JSON_PATH, backup / JSON_PATH.name)
    JSON_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"[BACKUP] {backup}")
    print("[DONE] aggiornato dati_farmaci.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
