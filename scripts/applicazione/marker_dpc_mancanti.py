#!/usr/bin/env python3
"""Aggiunge il marker di provenienza '[agg. ...]' alle 20 righe inserite dal DPC.

Le righe aggiunte non riportavano il testo del DPC con un richiamo cliccabile al provvedimento:
il marker rende esplicita la fonte (pagina del DPC regionale) e genera il link al PDF locale
docs/dpc-controllo-appropriatezza.pdf, come per le altre 375 variazioni del sito.

Uso: python3 marker_dpc_mancanti.py [--dry-run|--apply]
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
JSON_PATH = ROOT / "data" / "dati_farmaci.json"
COPIA_SITO = ROOT / "html_estratto" / "dati_farmaci.json"
LINKS_FILE = ROOT / "scripts" / "fonti_links.json"
BACKUP = ROOT / "output" / "backup"
DATA = "10/11/2026"
LINK_DPC = "docs/dpc-controllo-appropriatezza.pdf"

PAGINE = {
    "044407043": 42, "046284055": 43, "043152204": 44, "027066137": 45, "027276031": 46,
    "044905293": 47, "042241024": 48, "040261036": 49, "045597402": 51, "040510152": 52,
    "040036042": 54, "041141021": 55,
    "034525042": 58, "034525028": 58, "029610108": 59, "029610110": 59, "032887010": 60,
    "040541070": 60, "035609041": 61, "035609027": 61,
}


def marker(pagina: int) -> str:
    return f"[agg. {DATA} – DPC Regione Siciliana, pag. {pagina}]"


def main() -> int:
    ap = argparse.ArgumentParser()
    grp = ap.add_mutually_exclusive_group()
    grp.add_argument("--dry-run", action="store_true")
    grp.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    apply = args.apply and not args.dry_run

    data = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    by = {str(r.get("minsan") or r.get("aic")): r for r in data}
    modificati = []
    for codice, pagina in sorted(PAGINE.items(), key=lambda kv: (kv[1], kv[0])):
        rec = by.get(codice)
        if rec is None:
            print(f"  {codice} non presente nel JSON: salto")
            continue
        nota = str(rec.get("note") or "")
        mk = marker(pagina)
        if mk in nota:
            continue
        nuova = f"{nota} {mk}".strip() if nota else mk
        modificati.append((codice, nota, nuova))
        rec["note"] = nuova

    print(f"record con marker aggiunto: {len(modificati)}")
    for c, old, new in modificati:
        print(f"  {c}: '{old[:34]}' -> '{new[:62]}'")

    links = json.loads(LINKS_FILE.read_text(encoding="utf-8"))
    pattern = "DPC Regione Siciliana"
    presente = any(p == pattern for p, _ in links.get("link", []))
    print(f"fonti_links.json: pattern '{pattern}' {'gia' if presente else 'da aggiungere'}")

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

    if not presente:
        links.setdefault("link", []).append([pattern, LINK_DPC])
        LINKS_FILE.write_text(json.dumps(links, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print(f"[scritto] {LINKS_FILE} (+1 pattern)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
