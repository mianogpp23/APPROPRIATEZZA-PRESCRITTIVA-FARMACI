#!/usr/bin/env python3
"""QA incrociato: confronto 2023 (nuova estrazione) vs 2024 (output/pp41-67_verificato.csv).

Confronta, per ogni Minsan presente in entrambi:
  - descrizione (normalizzata)
  - principio attivo (normalizzato)
  - ATC (solo diretta)
  - note/PT (confronto per token, non per stringa esatta)
Produce un report di concordanza + elenco delle discrepanze.
"""
import csv, json, re, os, collections, unicodedata

BASE = str(ROOT)

def norm(s):
    s = unicodedata.normalize("NFKD", (s or ""))
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.upper()
    s = re.sub(r"[^A-Z0-9]+", " ", s)
    return " ".join(s.split())

def tok(s):
    return set(norm(s).split())

rows24 = list(csv.DictReader(open(os.path.join(BASE, "output/pp41-67_verificato.csv"), encoding="utf-8-sig")))
by24 = {r["minsan"]: r for r in rows24 if r.get("minsan")}

# 2024: le colonne sono state parzialmente spostate per ATC non standard; ricostruisco
# principio attico usando la logica originale (mid tokens) quando atc e' vuoto.
sec24 = {"42-56_dpc_specialita": "dpc", "58-62_diretta_ASP": "diretta", "66-67_nota99_bpco": "nota99"}

report = {}
for sez in ("dpc", "diretta", "nota99"):
    new = json.load(open(os.path.join(BASE, "data", f"{sez}.json"), encoding="utf-8"))
    n_common = n_desc = n_pa = n_atc = n_note = 0
    diff_desc, diff_pa, diff_atc, diff_note = [], [], [], []
    only23, only24 = [], []
    m23 = set()
    for r in new:
        m = r["minsan"]; m23.add(m)
        o = by24.get(m)
        if not o:
            only23.append((m, r["descrizione"][:60]))
            continue
        if sec24.get(o["sezione"]) != sez:
            diff_desc.append((m, "sezione diversa", o["sezione"]))
            continue
        n_common += 1
        if norm(r["descrizione"]) == norm(o["descrizione"]):
            n_desc += 1
        else:
            diff_desc.append((m, r["descrizione"], o["descrizione"]))
        # principio attivo
        pa24 = o.get("principio_attivo", "")
        if norm(pa24) == norm(r["principio_attivo"]):
            n_pa += 1
        elif tok(pa24) & tok(r["principio_attivo"]):
            n_pa += 1  # stessa sostanza, solo refuso/ordine diverso
        else:
            diff_pa.append((m, r["principio_attivo"], pa24))
        if sez == "diretta":
            a23 = r.get("atc", "")
            a24 = o.get("atc", "") or (pa24 if len(norm(pa24)) == 7 and pa24[:1].isalpha() else "")
            if norm(a23) == norm(a24):
                n_atc += 1
            else:
                diff_atc.append((m, a23, a24))
        # note: confronto per token
        t23 = tok(r["note"]); t24 = tok(o.get("pt_sm_nota", "")) | tok(o.get("note_cap", "")) | tok(o.get("note_testuali", ""))
        if not t23 or not t24 or (t23 & t24):
            n_note += 1
        else:
            diff_note.append((m, r["note"], o.get("pt_sm_nota", "")))
    only24 = [m for m in by24 if m not in m23 and sec24.get(by24[m]["sezione"]) == sez]
    report[sez] = dict(
        righe_2023=len(new), comuni=n_common,
        descrizione_uguale=n_desc, descrizione_div=n_desc and len(diff_desc) or len(diff_desc),
        principio_attivo_uguale=n_pa,
        atc_uguale=n_atc if sez == "diretta" else None,
        note_con_token_comuni=n_note,
        solo_2023=len(only23), solo_2024=len(only24),
        esempi_desc_divergente=diff_desc[:6],
        esempi_pa_divergente=diff_pa[:6],
        esempi_atc_divergente=diff_atc[:6] if sez == "diretta" else [],
        esempi_note_divergente=diff_note[:6],
    )
    report[sez]["_diff_desc"] = diff_desc
    report[sez]["_diff_pa"] = diff_pa

with open(os.path.join(BASE, "qa_crosscheck_23_24.json"), "w", encoding="utf-8") as f:
    json.dump(report, f, ensure_ascii=False, indent=2)

for sez, r in report.items():
    print(f"== {sez}: 2023={r['righe_2023']} comuni={r['comuni']} "
          f"desc_ok={r['descrizione_uguale']} pa_ok={r['principio_attivo_uguale']} "
          f"atc_ok={r['atc_uguale']} note_ok={r['note_con_token_comuni']} "
          f"solo23={r['solo_2023']} solo24={r['solo_2024']}")
    if r["esempi_desc_divergente"]:
        print("   desc divergenti:", r["esempi_desc_divergente"][:3])
    if r["esempi_pa_divergente"]:
        print("   PA divergenti:", r["esempi_pa_divergente"][:3])
    if r.get("esempi_atc_divergente"):
        print("   ATC divergenti:", r["esempi_atc_divergente"][:3])
