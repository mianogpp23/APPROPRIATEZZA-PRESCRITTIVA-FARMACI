#!/usr/bin/env python3
"""Ripulisce le entita' HTML residue nel JSON dei dati (nessun valore perde informazione).

  &nbsp; -> spazio (U+00A0),  &quot; -> "

Backup automatico; il JSON resta identico byte per byte a parte le entita' sostituite.
Uso: python3 pulisci_entita_json.py [--dry-run|--apply]
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
BACKUP = ROOT / "output" / "backup"
SOSTITUZIONI = (("&nbsp;", "\u00a0"), ("&quot;", '"'), ("&amp;", "&"), ("&lt;", "<"), ("&gt;", ">"))

CAMPI = ("descrizione", "principio_attivo", "note", "atc", "indicazioni_bpc", "ssn")


def pulisci_valore(v: str) -> str:
    for a, b in SOSTITUZIONI:
        v = v.replace(a, b)
    return v


def main() -> int:
    ap = argparse.ArgumentParser()
    grp = ap.add_mutually_exclusive_group()
    grp.add_argument("--dry-run", action="store_true")
    grp.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    apply = args.apply and not args.dry_run

    data = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    cambi = []
    for r in data:
        for campo in CAMPI:
            v = r.get(campo)
            if isinstance(v, str) and any(a in v for a, _ in SOSTITUZIONI):
                nuovo = pulisci_valore(v)
                if nuovo != v:
                    cambi.append((r.get("minsan") or r.get("aic"), campo, v[:60], nuovo[:60]))
                    r[campo] = nuovo
        for i, c in enumerate(r.get("cells") or []):
            if isinstance(c, str) and any(a in c for a, _ in SOSTITUZIONI):
                nuovo = pulisci_valore(c)
                if nuovo != c:
                    cambi.append((r.get("minsan") or r.get("aic"), f"cells[{i}]", c[:60], nuovo[:60]))
                    r["cells"][i] = nuovo

    print(f"valori ripuliti: {len(cambi)}")
    for c, camp, old, new in cambi:
        print(f"  {c} [{camp}]\n     prima: {old}\n     dopo : {new}")
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
