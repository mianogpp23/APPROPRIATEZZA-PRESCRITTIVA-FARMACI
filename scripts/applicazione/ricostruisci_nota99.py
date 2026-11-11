#!/usr/bin/env python3
"""Ricostruisce le righe della scheda 'nota_99' direttamente dalla tabella del DPC (pagine 66-67),
con le colonne al posto giusto (AIC | Medicinale | Principio attivo | BPCO/regola | SSN non soggette).

Motivo: l'estrazione precedente aveva unito frammenti di colonne diverse (es. 'A-PT-Nota' dentro il
Principio attivo, testi lunghi al posto della nota) e non era ricostruibile dal JSON.

Uso: python3 ricostruisci_nota99.py [--dry-run]
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import shutil
import sys
from pathlib import Path

import pdfplumber

ROOT = Path(__file__).resolve().parents[2]
JSON_PATH = ROOT / "data" / "dati_farmaci.json"
PDF = ROOT / "docs" / "dpc" / "Controllo-appropriatezza-prescrittiva.pdf"
PAGES = (65, 66)   # pagine 66-67 (indici 0-based)

# marker corretto per le 3 triplici (fonte: Det. AIFA 822/2026, G.U. n. 144 del 24/06/2026)
M99 = ("[agg. 09/07/2026 – Det. AIFA 822/2026, G.U. n. 144 del 24/06/2026] triplice LAMA+LABA+ICS "
       "prescrivibile da MMG (RR), eliminata SVP")


def clean(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").replace("\n", " ")).strip()


def extract_table() -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    with pdfplumber.open(PDF) as pdf:
        for pno in PAGES:
            for table in pdf.pages[pno].find_tables():
                for row in table.extract():
                    if not row or not row[0]:
                        continue
                    aic = clean(row[0])
                    if not re.fullmatch(r"\d{9}", aic):
                        continue
                    cells = [clean(c) for c in row[1:5]]
                    cells += [""] * (4 - len(cells))
                    out[aic] = cells
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    if not args.apply and not args.dry_run:
        ap.error("specificare --dry-run o --apply")

    tab = extract_table()
    print(f"[pdf] righe estratte dalla tabella Nota 99 (pp. 66-67): {len(tab)}")

    data = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    n99 = [r for r in data if r.get("elenco") == "nota_99"]
    print(f"[json] record nota_99 attuali: {len(n99)}")

    aggiornati = mancanti = extra = 0
    for r in n99:
        aic = str(r.get("aic") or "").strip()
        if aic not in tab:
            mancanti += 1
            continue
        med, pa, bpc, ssn = tab[aic]
        var = r.get("variazioni") or []
        marker = ""
        if var:
            # i record con variazioni restano marcati nella colonna della regola (col 4)
            marker = " " + M99 if "triplice LAMA+LABA+ICS" in (var[0].get("testo_breve") or "") else ""
        nuovo = {
            "aic": aic,
            "descrizione": med,
            "principio_attivo": pa,
            "note": "",
            "indicazioni_bpc": bpc + marker,
            "ssn": ssn,
            "elenco": "nota_99",
            "variazioni": var,
        }
        if r.get("note") and not marker:
            # note preesistente non vuota: la conserviamo solo se non e' rumore di colonna
            nuovo["note"] = r["note"] if len(r["note"]) < 30 and "|" not in r["note"] else ""
        r.clear()
        r.update(nuovo)
        aggiornati += 1

    visti = {str(r.get("aic") or "") for r in n99}
    extra = len([a for a in tab if a not in visti])
    print(f"[match] aggiornati {aggiornati} | AIC delle liste non trovati nel PDF {mancanti} | righe PDF non nelle liste {extra}")
    if mancanti:
        for r in n99:
            if str(r.get("aic") or "") not in tab:
                print(f"    non trovato: {r.get('aic')} {str(r.get('descrizione'))[:40]}")
    # righe presenti nel DPC ma assenti dalle liste -> da aggiungere
    da_aggiungere = []
    for a, (med, pa, bpc, ssn) in tab.items():
        if a not in visti:
            da_aggiungere.append({
                "aic": a, "descrizione": med, "principio_attivo": pa, "note": "",
                "indicazioni_bpc": bpc, "ssn": ssn, "elenco": "nota_99", "variazioni": [],
            })
            print(f"    DA AGGIUNGERE: {a} {med[:44]} | {bpc} | {ssn}")

    if args.dry_run:
        print("\n[DRY-RUN] nessuna scrittura.")
        return 0

    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    backup = ROOT / "output" / f"backup-nota99-colonne-{stamp}"
    backup.mkdir(parents=True, exist_ok=True)
    shutil.copy2(JSON_PATH, backup / JSON_PATH.name)
    data.extend(da_aggiungere)
    JSON_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"[BACKUP] {backup}")
    print(f"[DONE] dati_farmaci.json aggiornato (colonne Nota 99 ricostruite, {len(da_aggiungere)} riga/e aggiunta/e)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
