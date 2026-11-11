#!/usr/bin/env python3
"""Allinea il link delle variazioni delle 20 righe inserite dal DPC alla pagina dell'Assessorato.

Opzione B: per le righe il cui testo coincide gia' con il DPC il link leggero alla pagina
dell'Assessorato (dove e' pubblicato il DPC) e' sufficiente; il PDF integrale del DPC resta per
le note di pagina della Nota 99, che ne citano il testo alla lettera.

Uso: python3 aggiorna_link_mancanti.py [--dry-run|--apply]
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
ASSESSORATO = ("https://www.regione.sicilia.it/istituzioni/regione/strutture-regionali/"
               "assessorato-salute/dipartimento-pianificazione-strategica/appropriatezza-d-uso-farmaci")
VECCHIO = "docs/dpc-controllo-appropriatezza.pdf"

CODICI = {
    "044407043", "046284055", "043152204", "027066137", "027276031", "044905293",
    "042241024", "040261036", "045597402", "040510152", "040036042", "041141021",
    "034525042", "034525028", "029610108", "029610110", "032887010", "040541070",
    "035609041", "035609027",
}


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
        codice = str(r.get("minsan") or r.get("aic") or "")
        if codice not in CODICI:
            continue
        for v in r.get("variazioni") or []:
            if v.get("url_o_percorso") == VECCHIO:
                cambi.append((codice, v.get("url_o_percorso"), ASSESSORATO))
                v["url_o_percorso"] = ASSESSORATO

    print(f"variazioni aggiornate: {len(cambi)}")
    for c, old, new in cambi[:4]:
        print(f"  {c}: {old} -> {new[:60]}...")
    if len(cambi) > 4:
        print(f"  ... altre {len(cambi) - 4}")
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
