#!/usr/bin/env python3
"""Fase 2/3 - applicazione degli aggiornamenti delle Note AIFA 2024-2026 alle liste DPC.

Ogni riga viene aggiornata SOLO sulla base delle colonne della riga stessa (Minsan/AIC,
Descrizione, Principio attivo, campo PT/SM/Nota): la regola di ricerca e' multi-colonna.
Le fonti sono le determine AIFA pubblicate in G.U. (indice AGiR/medicoeleggi) e la verifica
dei testi vigenti su AIFA / Regione Siciliana.

Uso:
    python3 aggiorna_note_2025_2026.py --dry-run
    python3 aggiorna_note_2025_2026.py --apply
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

# (id regola, nota, predicato, marker, variazione)
R: list[dict] = [
    {
        "id": "nota84_abrogata",
        "nota": "84",
        "match": lambda r: bool(re.search(r"Nota\s*84\b", r.get("note") or "")),
        "marker": (" [agg. 12/04/2026 – Det. AIFA 422/2026, G.U. n. 84 del 11/04/2026] "
                   "Nota 84 abrogata: aciclovir/valaciclovir/famciclovir/brivudina prescrivibili "
                   "a carico SSN senza indicazione di nota (clausola di salvaguardia sulla spesa)"),
        "var": {
            "data": "12/04/2026",
            "fonte": "Det. AIFA 422/2026 del 01/04/2026 – G.U. n. 84 del 11/04/2026",
            "url_o_percorso": "https://www.aifa.gov.it/-/revisione-delle-note-aifa-abrogate-le-note-11-e-84",
            "testo_breve": "Nota AIFA 84 abrogata dal 12/04/2026: antivirali per herpes "
                           "(aciclovir, valaciclovir, famciclovir, brivudina) prescrivibili SSN "
                           "senza le limitazioni della nota",
            "stato": "approvata",
        },
    },
    {
        "id": "nota11_abrogata",
        "nota": "11",
        "match": lambda r: bool(re.search(r"Nota\s*11\b", r.get("note") or "")),
        "marker": (" [agg. 12/04/2026 – Det. AIFA 421/2026, G.U. n. 84 del 11/04/2026] "
                   "Nota 11 abrogata: calcio folinato non e' piu' rimborsato a carico SSN "
                   "[riga DPC con colonne disallineate: descrizione SANIFOLIN vs PA CALCIO FOLINATO]"),
        "var": {
            "data": "12/04/2026",
            "fonte": "Det. AIFA 421/2026 del 01/04/2026 – G.U. n. 84 del 11/04/2026",
            "url_o_percorso": "https://www.aifa.gov.it/-/revisione-delle-note-aifa-abrogate-le-note-11-e-84",
            "testo_breve": "Nota AIFA 11 (calcio folinato) abrogata dal 12/04/2026: i medicinali "
                           "a base di calcio folinato non sono piu' rimborsati a carico SSN",
            "stato": "approvata",
        },
    },
    {
        "id": "nota85_aggiornata",
        "nota": "85",
        "match": lambda r: bool(re.search(r"Nota\s*85\b", r.get("note") or "")),
        "marker": (" [agg. 16/02/2026 – Det. AIFA 142/2026, G.U. n. 38 del 16/02/2026] "
                   "Nota 85 aggiornata: PT AIFA aggiornato; associazione fissa "
                   "donepezil/memantina riclassificata in classe A dal 17/02/2026"),
        "var": {
            "data": "16/02/2026",
            "fonte": "Det. AIFA 142/2026 – G.U. n. 38 del 16/02/2026 (DET PRES 142-2026)",
            "url_o_percorso": "https://omceomi.it/2026/03/06/terapia-per-m-alzheimer-aggiornamento-della-nota-aifa-85/",
            "testo_breve": "Nota AIFA 85 (Alzheimer) aggiornata: nuovo PT AIFA; associazione "
                           "donepezil/memantina in classe A dal 17/02/2026",
            "stato": "approvata",
        },
    },
    {
        "id": "nota98_aggiornata",
        "nota": "98",
        "match": lambda r: bool(re.search(r"Nota\s*98\b", r.get("note") or "")),
        "marker": (" [agg. 21/11/2025 – Det. AIFA 1533/2025, G.U. n. 271 del 21/11/2025] "
                   "Nota 98 aggiornata (ultimo aggiornamento; precedenti Det. 505/2024 e "
                   "DET PRES 825/2025): anti-VEGF intravitreali per AMD e DME"),
        "var": {
            "data": "21/11/2025",
            "fonte": "Det. AIFA 1533/2025 – G.U. n. 271 del 21/11/2025",
            "url_o_percorso": "https://www.terap.it/news.html",
            "testo_breve": "Nota AIFA 98 aggiornata (anti-VEGF intravitreali per AMD e DME)",
            "stato": "approvata",
        },
    },
    {
        "id": "nota51_aggiornata",
        "nota": "51",
        "match": lambda r: bool(re.search(r"Nota\s*51\b", r.get("note") or "")),
        "marker": (" [agg. 15/05/2025 – DET PRES 624/2025, G.U. n. 111 del 15/05/2025] "
                   "Nota 51 aggiornata (precedente Det. 620/2024, G.U. n. 261 del 07/11/2024): "
                   "prostatotropi/GnRH"),
        "var": {
            "data": "15/05/2025",
            "fonte": "DET PRES 624/2025 – G.U. n. 111 del 15/05/2025",
            "url_o_percorso": "https://www.medicoeleggi.com/indici2022/nazionale-argo-farmaci-note.htm",
            "testo_breve": "Nota AIFA 51 aggiornata (prostatotropi)",
            "stato": "approvata",
        },
    },
    {
        "id": "nota79_aggiornata",
        "nota": "79",
        "match": lambda r: bool(re.search(r"Nota\s*79\b|nota79", (r.get("note") or "") + " " +
                                           " ".join(map(str, r.get("cells") or [])))),
        "marker": (" [agg. 13/09/2025 – DET PRES 1127/2025, G.U. n. 213 del 13/09/2025] "
                   "Nota 79 aggiornata: per DENOSUMAB abolito il PT web-based e resa "
                   "prescrivibile dal MMG (precedente Det. AIFA 225/2025, G.U. n. 44 del 22/02/2025: "
                   "aggiornati testo della nota e PT)"),
        "var": {
            "data": "13/09/2025",
            "fonte": "DET PRES 1127/2025 – G.U. n. 213 del 13/09/2025",
            "url_o_percorso": "https://omceomi.it/2025/09/26/aggiornamento-nota-aifa-79-e-abolizione-piano-terapeutico-per-denosumab/",
            "testo_breve": "Nota AIFA 79 aggiornata: denosumab senza PT web-based, prescrivibile dal MMG",
            "stato": "approvata",
        },
    },
    {
        "id": "nota100_aggiornata",
        "nota": "100",
        "match": lambda r: bool(re.search(r"Nota\s*100\b", r.get("note") or "")),
        "marker": (" [agg. 05/08/2025 – Det. AIFA 1037/2025, G.U. n. 180 del 05/08/2025] "
                   "Nota 100 aggiornata (di cui alla determina n. 19/2022)"),
        "var": {
            "data": "05/08/2025",
            "fonte": "Det. AIFA 1037/2025 del 31/07/2025 – G.U. n. 180 del 05/08/2025",
            "url_o_percorso": "https://www.medicoeleggi.com/indici2022/nazionale-argo-farmaci-note.htm",
            "testo_breve": "Nota AIFA 100 aggiornata (DMDU: SGLT2, GLP-1, DPP4, doppi agonisti)",
            "stato": "approvata",
        },
    },
    {
        "id": "nota39_allegato",
        "nota": "39",
        "match": lambda r: bool(re.search(r"Nota\s*39\b", r.get("note") or "")),
        "marker": (" [agg. 06/07/2026 – Det. AIFA 914/2026, G.U. n. 157 del 09/07/2026] "
                   "sostituito l'allegato della determina 819/2026 (stessa determina, PT/Nota "
                   "aggiornati)"),
        "var": {
            "data": "06/07/2026",
            "fonte": "Det. AIFA 914/2026 del 06/07/2026 – G.U. n. 157 del 09/07/2026",
            "url_o_percorso": "https://www.medicoeleggi.com/indici2022/nazionale-argo-farmaci-note.htm",
            "testo_breve": "Allegato della determina 819/2026 (Nota 39) sostituito",
            "stato": "approvata",
        },
    },
    {
        "id": "nota92_rettifica",
        "nota": "92",
        "match": lambda r: bool(re.search(r"Nota\s*92\b", r.get("note") or "")),
        "marker": (" [agg. 10/10/2025 – Det. AIFA 1322/2025, G.U. n. 241 del 16/10/2025] "
                   "rettifica della determina 1224/2025 di abrogazione"),
        "var": {
            "data": "10/10/2025",
            "fonte": "Det. AIFA 1322/2025 del 10/10/2025 – G.U. n. 241 del 16/10/2025",
            "url_o_percorso": "https://www.medicoeleggi.com/indici2022/nazionale-argo-farmaci-note.htm",
            "testo_breve": "Rettifica della determina 1224/2025 di abrogazione della Nota 92",
            "stato": "approvata",
        },
    },
]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    if not args.apply and not args.dry_run:
        ap.error("specificare --dry-run o --apply")

    data = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    touched = 0
    per_rule: dict[str, int] = {}
    for r in data:
        cells = r.get("cells")
        note = r.get("note") or ""
        full = note + " " + " ".join(map(str, cells or []))
        for rule in R:
            marker_id = rule["marker"].split("]")[0] + "]"
            if marker_id in full:
                continue
            if not rule["match"](r):
                continue
            if cells:
                cells[-1] = str(cells[-1]) + rule["marker"]
            else:
                r["note"] = note + rule["marker"]
                note = r["note"]
            r.setdefault("variazioni", []).append(dict(rule["var"]))
            full = (r.get("note") or "") + " " + " ".join(map(str, r.get("cells") or []))
            touched += 1
            per_rule[rule["id"]] = per_rule.get(rule["id"], 0) + 1

    print(f"[JSON] record aggiornati: {touched}")
    for k, v in sorted(per_rule.items(), key=lambda t: -t[1]):
        print(f"    {k}: {v}")

    if args.dry_run:
        print("\n[DRY-RUN] nessuna scrittura.")
        return 0

    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    backup = ROOT / "output" / f"backup-note-2025-2026-{stamp}"
    backup.mkdir(parents=True, exist_ok=True)
    shutil.copy2(JSON_PATH, backup / JSON_PATH.name)
    JSON_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"[BACKUP] {backup}")
    print(f"[DONE] {touched} record aggiornati in dati_farmaci.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
