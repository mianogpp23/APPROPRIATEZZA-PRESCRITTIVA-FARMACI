#!/usr/bin/env python3
"""Correzioni di rigor sulle associazioni principi attivi / canali / note.

1) Spillover di colonna: in 10 record della scheda DPC il campo 'principio attivo' termina con
   un frammento di nota (es. 'TRIPTORELINA |max 1'): il frammento torna nella nota, dove il DPC
   lo colloca (stessa tabella, pag. 55-56).
2) Refuso/offset di colonna nella distribuzione diretta (DPC pag. 59): JARDIANCE 28cpr 25MG
   (AIC 043443047) ha nel PDF la cella 'AIFA'; il principio attivo corretto e' EMPAGLIFLOZIN
   (ATC A10BD11, marchio JARDIANCE).
3) XARELTO: il riepilogo del DPC (pag. 15, 'FARMACI CON O SENZA NOTA 97') colloca TUTTE le
   confezioni di XARELTO in regime FANV sotto Nota 97; la tabella di pag. 56 riporta per la 15MG
   'Nota 98' (che riguarda gli anti-VEGF per AMD/DME) e per la 20MG 'Nota 100' (che riguarda i
   farmaci per il diabete di tipo 2). Il testo del DPC viene conservato e accompagnato dalla
   precisazione, con link diretto alla pagina del riepilogo.

Uso: python3 correggi_associazioni.py [--dry-run|--apply]
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
JSON_PATH = ROOT / "data" / "dati_farmaci.json"
COPIA_SITO = ROOT / "html_estratto" / "dati_farmaci.json"
BACKUP = ROOT / "output" / "backup"
DATA = "11/11/2026"
DPC = "DPC Regione Siciliana"

# 3) XARELTO: testo DPC da conservare + precisazione con link alla pagina del riepilogo
XARELTO = {
    "038744138": (
        "|max 2 m. PT AIFA |se FANV SP+Nota 98",
        "Attenzione: nel riepilogo del DPC (pag. 15, «FARMACI CON O SENZA NOTA 97») tutte le "
        "confezioni di XARELTO in regime FANV sono a Nota 97; la voce «Nota 98» della tabella "
        "(pag. 56) e' incongruente, perche' la Nota 98 riguarda gli anti-VEGF intravitreali "
        "per AMD e DME. Vale il riepilogo: FANV = Nota 97.",
        15,
        "Nota 98 incongruente per XARELTO: nel riepilogo DPC (pag. 15) FANV = Nota 97",
    ),
    "038744189": (
        "|max 2 m. PT AIFA |se FANV SP+Nota 100",
        "Attenzione: nel riepilogo del DPC (pag. 15, «FARMACI CON O SENZA NOTA 97») tutte le "
        "confezioni di XARELTO in regime FANV sono a Nota 97; la voce «Nota 100» della tabella "
        "(pag. 56) e' incongruente, perche' la Nota 100 riguarda i farmaci per il diabete di "
        "tipo 2. Vale il riepilogo: FANV = Nota 97.",
        15,
        "Nota 100 incongruente per XARELTO: nel riepilogo DPC (pag. 15) FANV = Nota 97",
    ),
}

MARKER = "[agg. " + DATA + " – " + DPC + ", pag. {pag}]"


def main() -> int:
    ap = argparse.ArgumentParser()
    grp = ap.add_mutually_exclusive_group()
    grp.add_argument("--dry-run", action="store_true")
    grp.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    apply = args.apply and not args.dry_run

    data = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    modifiche: list[tuple[str, str, str, str]] = []

    for r in data:
        aic = str(r.get("aic") or r.get("minsan") or "")
        pa = str(r.get("principio_attivo") or "")
        note = str(r.get("note") or "")

        # 1) spillover: il PA termina con un frammento di nota
        m = re.match(r"^(?P<pa>[^|]+?)\s*\|(?P<fr>max.*)$", pa)
        if m:
            nuovo_pa = m.group("pa").strip()
            nuovo_note = f"|{m.group('fr').strip()} {note}".strip()
            modifiche.append((aic, "principio_attivo", pa, nuovo_pa))
            modifiche.append((aic, "note", note[:60], nuovo_note[:60]))
            r["principio_attivo"] = nuovo_pa
            r["note"] = nuovo_note
            r.setdefault("variazioni", []).append({
                "data": DATA,
                "fonte": DPC + " (tabella farmaci in DPC, pag. 55-56)",
                "url_o_percorso": "docs/dpc-controllo-appropriatezza.pdf#page=55",
                "testo_breve": "Principio attivo ripulito dal frammento di nota che nel DPC e' nella colonla nota",
                "stato": "correzione",
            })
            continue

        # 2) refuso/offset nella distribuzione diretta
        if aic == "043443047" and r.get("elenco") == "distribuzione_diretta" and pa == "AEMIFAPAGLIFLOZIN":
            modifiche.append((aic, "principio_attivo", pa, "EMPAGLIFLOZIN"))
            r["principio_attivo"] = "EMPAGLIFLOZIN"
            r.setdefault("variazioni", []).append({
                "data": DATA,
                "fonte": DPC + " (distribuzione diretta, pag. 59: cella del PDF difettosa «AIFA»/«AEMIFAPAGLIFLOZIN»)",
                "url_o_percorso": "docs/dpc-controllo-appropriatezza.pdf#page=59",
                "testo_breve": "Principio attivo corretto in EMPAGLIFLOZIN (ATC A10BD11, JARDIANCE 25MG)",
                "stato": "correzione",
            })
            continue

        # 3) XARELTO: conservo il testo del DPC e aggiungo la precisazione con link alla pagina 15
        if aic in XARELTO and r.get("elenco") == "farmaci_dpc":
            testo_dpc, precisazione, pagina, breve = XARELTO[aic]
            # si ricostruisce la nota dal testo del DPC: il marker e la spiegazione precedenti
            # (Nota 98 anti-VEGF / Nota 100 diabete) non pertinenti per rivaroxaban
            nuovo = f"{testo_dpc} {MARKER.format(pag=pagina)} {precisazione}"
            modifiche.append((aic, "note", note[:70], nuovo[:70]))
            r["note"] = nuovo
            r.setdefault("variazioni", []).append({
                "data": DATA,
                "fonte": DPC + " — riepilogo «FARMACI CON O SENZA NOTA 97», pag. 15",
                "url_o_percorso": f"docs/dpc-controllo-appropriatezza.pdf#page={pagina}",
                "testo_breve": breve,
                "stato": "correzione",
            })

    for aic, campo, old, new in modifiche:
        print(f"  {aic} [{campo}]")
        print(f"     prima: {old}")
        print(f"     dopo : {new}")
    print(f"\ncorrezioni: {len(modifiche)} campi su {len({m[0] for m in modifiche})} record")

    if not apply:
        print("\n[DRY-RUN] nessuna scrittura")
        return 0

    BACKUP.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    bak = BACKUP / f"dati_farmaci.json.{ts}.bak"
    shutil.copy2(JSON_PATH, bak)
    JSON_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    shutil.copy2(JSON_PATH, COPIA_SITO)
    print(f"\n[backup] {bak}\n[scritto] {JSON_PATH} e {COPIA_SITO}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
