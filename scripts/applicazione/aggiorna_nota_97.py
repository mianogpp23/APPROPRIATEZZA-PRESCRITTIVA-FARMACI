#!/usr/bin/env python3
"""Aggiornamento note AIFA nelle liste DPC dopo la Determina AIFA 821/2026 (Nota 97).

Applica solo dopo conferma esplicita dell'utente ("CONFERMA").
Uso:
    python3 aggiorna_nota_97.py --dry-run     # mostra la patch, non scrive
    python3 aggiorna_nota_97.py --apply       # applica (JSON + HTML) con backup

Fonti:
  - Det. AIFA 17/06/2026 n. 821/2026, G.U. n. 144 del 24/06/2026, in vigore 09/07/2026
    (aggiorna Nota AIFA 97: abolita Scheda di prescrizione e valutazione / PT AIFA)
  - Det. AIFA 11/11/2025, G.U. n. 267 del 17/11/2025 (abrogazione Nota 8 e Nota 101)
  - Det. AIFA 30/09/2025, G.U. n. 230 del 03/10/2025 (abrogazione Nota 92)
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
JSON_PATH = ROOT / "data" / "dati_farmaci.json"
HTML_DIR = ROOT / "html_estratto"

DET97 = "Det. AIFA 821/2026, G.U. n. 144 del 24/06/2026"
DET8 = "Det. AIFA 11/11/2025, G.U. n. 267 del 17/11/2025"
DET92 = "Det. AIFA 30/09/2025, G.U. n. 230 del 03/10/2025"

DOAC = {
    "049099070", "049099132", "041225032", "041225095",
    "044315051", "044315188", "038451074", "038451112", "038744076",
}

NOTA97_NOTE = (
    "|max 2 m. PT AIFA |se FANV SP+Nota 97 "
    "[agg. 09/07/2026 – " + DET97 + "] "
    "Scheda di valutazione/PT AIFA abolita: per FANV erogare senza allegato PT "
    "e senza Prot.SP; per TEV/TVP-EP verificare con l'ASP se resta il PT regionale"
)
NOTA97_VAR = {
    "data": "09/07/2026",
    "fonte": DET97,
    "url_o_percorso": "G.U. n. 144 del 24/06/2026 (Determina AIFA 17/06/2026 n. 821/2026)",
    "testo_breve": "Nota AIFA 97 aggiornata: abolita la Scheda di prescrizione e valutazione "
                   "(PT AIFA) per AVK e NAO/DOAC; resta il limite di rimborso SSN alla sola FANV",
    "stato": "approvata",
}

NOTA8_NOTE = ("PT - Nota 8 [agg. 18/11/2025 – " + DET8 + "] "
              "Nota 8 abrogata: niente piu' piano terapeutico, resta nel PH-T")
NOTA8_VAR = {
    "data": "18/11/2025",
    "fonte": DET8,
    "url_o_percorso": "Circolare Federfarma 403 del 18/11/2025 (rev. 2025_403)",
    "testo_breve": "Nota AIFA 8 (carnitine) abrogata dal 18/11/2025 con abrogazione del PT; "
                   "confermato inserimento nel PH-T",
    "stato": "approvata",
}

NOTA92_NOTE = ("PT - Nota 92 [agg. 04/10/2025 – " + DET92 + "] "
               "Nota 92 abrogata: niente piu' piano terapeutico")
NOTA92_VAR = {
    "data": "04/10/2025",
    "fonte": DET92,
    "url_o_percorso": "Circolare Federfarma 333 del 06/10/2025 (rev. 2025_333)",
    "testo_breve": "Nota AIFA 92 (benzilpenicillina benzatinica) abrogata dal 04/10/2025: "
                   "medicinali prescrivibili a carico SSN senza limitazioni",
    "stato": "approvata",
}

AVK_OLD = "Nota 97 + Prot.SP"
AVK_NEW = ("Nota 97 (FANV) [agg. 09/07/2026 – " + DET97 + "] "
           "senza Prot.SP: erogare senza allegato PT")


def patch_records(records: list[dict]) -> list[str]:
    """Ritorna l'elenco delle modifiche (per dry-run)."""
    log: list[str] = []
    for r in records:
        if r.get("minsan") in DOAC and r.get("elenco") == "farmaci_dpc":
            old = r.get("note", "")
            if "agg. 09/07/2026" not in old:
                r["note"] = NOTA97_NOTE
                r.setdefault("variazioni", []).append(dict(NOTA97_VAR))
                log.append(f"DPC  {r['minsan']} {r.get('descrizione','')[:38]} :: {old!r} -> {NOTA97_NOTE!r}")
        elif r.get("minsan") == "018610079":
            old = r.get("note", "")
            if "agg. 18/11/2025" not in old:
                r["note"] = NOTA8_NOTE
                r.setdefault("variazioni", []).append(dict(NOTA8_VAR))
                log.append(f"DPC  {r['minsan']} {r.get('descrizione','')[:38]} :: {old!r} -> {NOTA8_NOTE!r}")
        elif r.get("descrizione", "").startswith("SIGMACILLINA"):
            old = r.get("note", "")
            if "agg. 04/10/2025" not in old:
                r["note"] = NOTA92_NOTE
                r.setdefault("variazioni", []).append(dict(NOTA92_VAR))
                log.append(f"DD   {r.get('aic','')} {r.get('descrizione','')[:38]} :: {old!r} -> {NOTA92_NOTE!r}")
        cells = r.get("cells")
        if isinstance(cells, list) and AVK_OLD in cells:
            i = cells.index(AVK_OLD)
            if "agg. 09/07/2026" not in cells[i]:
                cells[i] = AVK_NEW
                log.append(f"NODPC cells :: {AVK_OLD!r} -> {AVK_NEW!r}")
    return log


def patch_html(text: str) -> tuple[str, int]:
    n = 0
    old_doac = "|max 2 m. PT AIFA |se FANV SP+Nota 97"
    if old_doac in text and "agg. 09/07/2026" not in text:
        text = text.replace(old_doac, NOTA97_NOTE)
        n += text.count(NOTA97_NOTE)
    if ">PT - Nota 8<" in text and "agg. 18/11/2025" not in text:
        text = text.replace(">PT - Nota 8<", f">{NOTA8_NOTE}<")
        n += 1
    if ">PT - Nota 92<" in text and "agg. 04/10/2025" not in text:
        text = text.replace(">PT - Nota 92<", f">{NOTA92_NOTE}<")
        n += 1
    if f"<td>{AVK_OLD}</td>" in text and "agg. 09/07/2026" not in text:
        text = text.replace(f"<td>{AVK_OLD}</td>", f"<td>{AVK_NEW}</td>")
        n += 1
    return text, n


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="scrive i file (richiede CONFERMA)")
    ap.add_argument("--dry-run", action="store_true", help="mostra le modifiche senza scrivere")
    args = ap.parse_args()
    if not args.apply and not args.dry_run:
        ap.error("specificare --dry-run o --apply")

    data = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    changes = patch_records(data)
    print(f"[JSON] modifiche su dati_farmaci.json: {len(changes)}")
    for c in changes:
        print("   ", c)

    html_changes: list[tuple[Path, int]] = []
    for f in sorted(HTML_DIR.glob("*.html")):
        txt = f.read_text(encoding="utf-8")
        new, n = patch_html(txt)
        if n:
            html_changes.append((f, n))
            print(f"[HTML] {f.name}: {n} sostituzioni")

    if args.dry_run:
        print("\n[DRY-RUN] nessuna scrittura eseguita.")
        return 0

    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    backup = ROOT / "output" / f"backup-note-97-{stamp}"
    backup.mkdir(parents=True, exist_ok=True)
    shutil.copy2(JSON_PATH, backup / JSON_PATH.name)
    for f, _ in html_changes:
        shutil.copy2(f, backup / f.name)
    print(f"[BACKUP] {backup}")

    JSON_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for f, _ in html_changes:
        txt = f.read_text(encoding="utf-8")
        new, _ = patch_html(txt)
        f.write_text(new, encoding="utf-8")
    print(f"[DONE] applicate {len(changes)} modifiche JSON e {sum(n for _, n in html_changes)} su HTML.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
