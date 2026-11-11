#!/usr/bin/env python3
"""Controllo di coerenza tra principio attivo, canale e Nota AIFA dichiarata nella riga.

Ogni Nota AIFA ha un ambito di molecole noto: se una riga cita una Nota che non compete al suo
principio attivo, l'associazione e' sospetta ( inversione o marker applicato al farmaco sbagliato).
Il controllo e' segnalazione: non modifica nulla.

Uso: python3 audit_associazioni.py [--json output.json]
"""
from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = json.loads((ROOT / "data" / "dati_farmaci.json").read_text(encoding="utf-8"))

# ambito di molecole per Nota AIFA (dal DPC e dalle note AIFA)
AMBITO: dict[str, str] = {
    "97": r"APIXABAN|DABIGATRAN|EDOXABAN|RIVAROXABAN|WARFARIN|ACENOCUMAROL|SANTONIC",
    "98": r"ANTI-VEGF|AFLIBERCEPT|RANIBIZUMAB|BEVACIZUMAB|OCULAR|LUCENTIS|EFLUZE",
    "100": r"DAPAGLIFLOZIN|EMPAGLIFLOZIN|CANAGLIFLOZIN|ERTUGLIFLOZIN|DPP4|ALOGLIPTIN|LINAGLIPTIN|SAXAGLIPTIN|SITAGLIPTIN|VILDAGLIPTIN|METFORMINA|PIOGLITAZONE|SEMAGLUTIDE|LIRAGLUTIDE|DULAGLUTIDE|EXENATIDE|LIXISENATIDE|TIRZEPATIDE|INSULINA|GLARGINE|GLIMEPIRIDE|SITAGLIPTIN",
    "79": r"DENOSUMAB|TERIPARATIDE|ABALOPARATIDE|ALENDRONATO|IBANDRONATO|RALOXIFENE|BISFOSFONATO",
    "99": r"FORMOTEROL|SALMETEROL|BUDESONIDE|FLUTICONE|BEclometasone|TIOTROPIO|GLICOPIRRONIO|UMECLIDINIO|VILANTEROLO|INDACATEROL|CARMOTEROL|ACLIDINIO|OLODATEROL",
    "51": r"BUSERELINA|GOSERELINA|LEUPRORELINA|TRIPTORELINA|ULIPRISTAL|RELUGOLIX|DECAPEPTYL|GONAPEPTYL|SUPREFACT|ELIGARD|ZOLADEX|LEPTOPROL",
    "95": r"FLUOROURACILE|CAPECITABINE|KETOCONAZOLE|SALICILICO|IMIQUIMOD|DICLOFENAC|TIMOLOLO",
    "92": r"ANTICOAGULANT|NAO|AVK|BENZILPENICILLINA|AMOXICILLINA",
    "65": r"INTERFERON|GLATIRAMER|PEGINTERFERON|FINGOLIMOD|DIMETILFUMARATO|TERIFLUNOMIDE|NATALIZUMAB",
    "74": r"BUSERELINA|GOSERELINA|LEUPRORELINA|TRIPTORELINA|ULIPRISTAL|FOLLITROPINA|CORIFOLLITROPINA|UROFOLLITROPINA|LUTROPINA|MENOTROPINA|REKOVELLE|PERGOVERIS|FOSGONADOTROPIN",
    "85": r"DONEPEZIL|GALANTAMINA|RIVASTIGMINA|MEMANTINA",
    "8": r"ISOTRETINOINA|ACITRETINA|IGS|LEVOCARNITINA|CARNITENE",
}
# note che non hanno un ambito di molecole definito (non segnalate)
NON_VERIFICABILI = {"11", "84", "101", "4", "96"}


def note_citate(testo: str) -> set[str]:
    return set(re.findall(r"[Nn]ota\s*(?:AIFA\s*)?(\d{1,3})\b", testo or ""))


def testo_riga(r: dict) -> str:
    """Testo della riga: per lo schema 'cells' il principio attivo e' la terza cella."""
    if r.get("cells"):
        celle = [str(c) for c in r["cells"]]
        if len(celle) > 2 and not celle[2].strip():
            return ""      # nel DPC la cella del principio attivo e' vuota: nulla da verificare
        return " ".join(celle)
    parti = [str(r.get(k) or "") for k in ("descrizione", "principio_attivo", "note", "indicazioni_bpc")]
    return " ".join(parti)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", default="")
    args = ap.parse_args()

    sospetti: list[dict] = []
    conteggio = Counter()
    per_nota = defaultdict(Counter)
    for r in DATA:
        t = testo_riga(r)
        for nota in note_citate(t):
            conteggio[nota] += 1
            ambito = AMBITO.get(nota)
            if not ambito or nota in NON_VERIFICABILI:
                continue
            if not re.search(ambito, t.upper()):
                sospetti.append({
                    "aic": r.get("aic") or r.get("minsan"),
                    "descrizione": r.get("descrizione"),
                    "principio_attivo": r.get("principio_attivo"),
                    "elenco": r.get("elenco"),
                    "nota": nota,
                    "testo": t[:180],
                })
                per_nota[nota][str(r.get("principio_attivo") or "")[:40]] += 1

    print("occorrenze di Note citate nelle righe:")
    for nota, n in sorted(conteggio.items(), key=lambda kv: -kv[1]):
        amb = "verificabile" if nota in AMBITO and nota not in NON_VERIFICABILI else "non verificabile"
        print(f"   Nota {nota:<4} {n:>5}  ({amb})")
    print(f"\nassociazioni sospette (Nota che non compete al principio attivo): {len(sospetti)}")
    for s in sospetti[:40]:
        print(f"   {s['aic']} {str(s['descrizione'])[:34]:<34} PA={str(s['principio_attivo'])[:26]:<26} Nota {s['nota']} [{s['elenco']}]")
    if len(sospetti) > 40:
        print(f"   ... altre {len(sospetti) - 40}")
    if per_nota:
        print("\nper Nota, i principi attivi sospetti:")
        for nota, c in sorted(per_nota.items()):
            print(f"   Nota {nota}: " + ", ".join(f"{k} ({v})" for k, v in c.most_common(6)))

    if args.json:
        Path(args.json).write_text(json.dumps(sospetti, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\n[report] {args.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
