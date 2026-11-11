#!/usr/bin/env python3
"""Estrazione meccanica dei 3 elenchi dal PDF 2023 (Federfarma Messina, agg. 17/07/2023).

Sezioni:
  - DPC        : pp. 44-58
  - DIRETTA ASP: pp. 59-63
  - NOTA 99    : pp. 66-67

Strategia (misurata sui dati, vedi LOG.md e scripts/diag*.py):
  - Le bande-riga sono ricavate dalle hlines orizzontali del page (edges orientation='h').
  - I caratteri sono assegnati alle colonne PRIMA di ricostruire il testo, così le
    righe con testo sovrapposto (es. riga COVID) non producono stringhe corrotte.
  - DPC: la dimensione del font separa i campi (7.7 = descrizione, 6.1 = Minsan/PA/Note).
  - DIRETTA / NOTA 99: separazione geometrica per x0 (i bordi delle celle sono noti).

Output: data/dpc.json, data/diretta.json, data/nota99.json, qc_report.json, csv/*
"""
import csv
import json
import os
import re
import sys
import time
from datetime import datetime, timezone, timedelta

import pdfplumber

BASE = str(ROOT)
PDF = os.path.join(BASE, "Controllo-appropriatezza-prescrittiv1a.pdf")
DATA = os.path.join(BASE, "data")
CSV_DIR = os.path.join(BASE, "csv")
PROGRESS = os.path.join(BASE, "progress.json")
LOG = os.path.join(BASE, "LOG.md")
TZ = timezone(timedelta(hours=1))

SECTIONS = {
    "dpc": dict(pages=range(44, 59), prefix="dpc"),
    "diretta": dict(pages=range(59, 64), prefix="diretta"),
    "nota99": dict(pages=range(66, 68), prefix="nota99"),
}

AIC9 = re.compile(r"^\d{9}$")
ATC_OK = re.compile(r"^[A-Z]\d{2}[A-Z][A-Z0-9]\d{2}$")
# soglie derivate dai dati (scripts/applicazione/estrai_2023.py)
DPC_DESC_SIZE = 7.7
DPC_OTHER_SIZE = 6.1
DPC_MIN = (30, 68)        # Minsan
DPC_PA = (262, 483)       # Principio attivo
DPC_NOTE = (483, 563)     # PT / SM / Nota AIFA / CAP
DIR_AIC = (0, 60)
DIR_FARMACO = (60, 199)
DIR_ATC = (199, 236)
DIR_PA = (236, 526)
DIR_NOTE = (526, 578)
N99_AIC = (0, 56)
N99_MED = (56, 306)
N99_PA = (306, 510)
N99_RIMB = (510, 546)
N99_IND = (546, 578)


def now_iso():
    return datetime.now(TZ).isoformat(timespec="seconds")


def hbands(pg):
    """Bande-riga: cluster delle linee orizzontali del page."""
    ys = sorted({round(e["top"], 1) for e in pg.edges if e["orientation"] == "h"})
    groups = []
    for y in ys:
        if groups and y - groups[-1][-1] <= 1.2:
            groups[-1].append(y)
        else:
            groups.append([y])
    c = [sum(x) / len(x) for x in groups]
    return [(c[i], c[i + 1]) for i in range(len(c) - 1)]


def band_chars(pg, b0, b1, ymin):
    return [c for c in pg.chars if b0 - 0.6 <= c["top"] < b1 - 0.6 and c["top"] > ymin]


def bucket_text(chars):
    """Ricostruisce il testo di un bucket: righe ordinate, parole con gli spazi reali del PDF."""
    if not chars:
        return ""
    lines = {}
    for c in chars:
        lines.setdefault(round(c["top"], 1), []).append(c)
    out = []
    for top in sorted(lines):
        s = "".join(ch["text"] for ch in sorted(lines[top], key=lambda c: c["x0"]))
        if s.strip():
            out.append(s.strip())
    return " ".join(out)


def norm(s):
    return re.sub(r"\s+", " ", (s or "")).strip()


def classify(chars, ranges):
    """Assegna i char ai bucket in base a x0 (ranges = [(nome, (lo, hi)), ...])."""
    out = {}
    for name, (lo, hi) in ranges:
        out[name] = [c for c in chars if lo <= c["x0"] < hi]
    return out


def extract_dpc(pg, pno, anomalies):
    rows = []
    for b0, b1 in hbands(pg):
        chars = band_chars(pg, b0, b1, 32)
        if not chars:
            continue
        big = [c for c in chars if c["size"] >= 7.0]
        small = [c for c in chars if c["size"] < 7.0]
        mins = [c for c in small if DPC_MIN[0] <= c["x0"] < DPC_MIN[1]]
        if not mins:
            anomalies.append(dict(pagina=pno, tipo="banda_senza_minsan", top=round(b0, 1)))
            continue
        mtext = norm(bucket_text(mins))
        if not AIC9.match(mtext):
            anomalies.append(dict(pagina=pno, tipo="minsan_non_valido", valore=mtext, top=round(b0, 1)))
            continue
        pa = [c for c in small if DPC_PA[0] <= c["x0"] < DPC_PA[1]]
        note = [c for c in small if DPC_NOTE[0] <= c["x0"] < DPC_NOTE[1]]
        desc = norm(bucket_text(big))
        pa_t = norm(bucket_text(pa))
        note_t = norm(bucket_text(note))
        if not desc:
            anomalies.append(dict(pagina=pno, tipo="descrizione_vuota", minsan=mtext, top=round(b0, 1)))
        if not pa_t:
            anomalies.append(dict(pagina=pno, tipo="principio_attivo_vuoto", minsan=mtext, top=round(b0, 1)))
        rows.append(dict(pagina=pno, minsan=mtext, descrizione=desc,
                         principio_attivo=pa_t, note=note_t, y=round(b0, 1)))
    return rows


def extract_diretta(pg, pno, anomalies):
    rows = []
    for b0, b1 in hbands(pg):
        chars = band_chars(pg, b0, b1, 45)
        if not chars:
            continue
        b = classify(chars, [("aic", DIR_AIC), ("farmaco", DIR_FARMACO), ("atc", DIR_ATC),
                             ("pa", DIR_PA), ("note", DIR_NOTE)])
        aic = norm(bucket_text(b["aic"]))
        if not aic:
            anomalies.append(dict(pagina=pno, tipo="banda_senza_minsan", top=round(b0, 1)))
            continue
        if not AIC9.match(aic):
            anomalies.append(dict(pagina=pno, tipo="minsan_non_valido", valore=aic, top=round(b0, 1)))
            continue
        atc = norm(bucket_text(b["atc"]))
        if not ATC_OK.match(atc):
            anomalies.append(dict(pagina=pno, tipo="atc_non_standard", minsan=aic, valore=atc,
                                  top=round(b0, 1)))
        rows.append(dict(pagina=pno, minsan=aic, descrizione=norm(bucket_text(b["farmaco"])),
                         atc=atc, principio_attivo=norm(bucket_text(b["pa"])),
                         note=norm(bucket_text(b["note"])), y=round(b0, 1)))
    return rows


def extract_nota99(pg, pno, anomalies):
    rows = []
    for b0, b1 in hbands(pg):
        chars = band_chars(pg, b0, b1, 48)
        if not chars:
            continue
        b = classify(chars, [("aic", N99_AIC), ("med", N99_MED), ("pa", N99_PA),
                             ("rimb", N99_RIMB), ("ind", N99_IND)])
        aic = norm(bucket_text(b["aic"]))
        if not aic:
            anomalies.append(dict(pagina=pno, tipo="banda_senza_minsan", top=round(b0, 1)))
            continue
        if not AIC9.match(aic):
            anomalies.append(dict(pagina=pno, tipo="minsan_non_valido", valore=aic, top=round(b0, 1)))
            continue
        rimb = norm(bucket_text(b["rimb"]))
        ind = norm(bucket_text(b["ind"]))
        if rimb not in ("NO", "A-Nota 99", "A-PT-Nota 99"):
            anomalies.append(dict(pagina=pno, tipo="rimborso_non_standard", minsan=aic, valore=rimb,
                                  top=round(b0, 1)))
        rows.append(dict(pagina=pno, minsan=aic, descrizione=norm(bucket_text(b["med"])),
                         principio_attivo=norm(bucket_text(b["pa"])),
                         rimborso=rimb, indicazioni=ind, y=round(b0, 1)))
    return rows


def check_pause():
    for name in ("PAUSE", "PAUSE.md", "STOP"):
        p = os.path.join(BASE, name)
        if os.path.exists(p):
            return p
    return None


def save_progress(step, stato, counters, note):
    data = {
        "step_corrente": step,
        "stato": stato,
        "ultima_riga_processata": counters,
        "via_libera_run_completo": False,
        "timestamp": now_iso(),
        "note": note,
    }
    tmp = PROGRESS + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp, PROGRESS)


def main():
    os.makedirs(DATA, exist_ok=True)
    os.makedirs(CSV_DIR, exist_ok=True)
    pause = check_pause()
    if pause:
        print(f"PAUSE presente ({pause}): estrazione interrotta.")
        return 2

    qc = dict(generato=now_iso(), pdf=os.path.basename(PDF), sezioni={})
    all_rows = {}
    t0 = time.time()
    with pdfplumber.open(PDF) as pdf:
        for sez, cfg in SECTIONS.items():
            anomalies = []
            rows = []
            per_page = {}
            for pno in cfg["pages"]:
                pg = pdf.pages[pno - 1]
                if sez == "dpc":
                    got = extract_dpc(pg, pno, anomalies)
                elif sez == "diretta":
                    got = extract_diretta(pg, pno, anomalies)
                else:
                    got = extract_nota99(pg, pno, anomalies)
                per_page[str(pno)] = len(got)
                rows.extend(got)
                save_progress(1, "running", {sez: len(rows)},
                              f"Step 1 estrazione {sez}: pagina {pno} elaborata ({len(got)} righe)")
                if check_pause():
                    print(f"PAUSE rilevato durante {sez} p{pno}: stop con stato salvato.")
                    return 2

            # normalizzazione e id
            out = []
            seen = {}
            for i, r in enumerate(rows, start=1):
                rid = f"{cfg['prefix']}-{i:04d}"
                if r["minsan"] in seen:
                    anomalies.append(dict(pagina=r["pagina"], tipo="minsan_duplicato",
                                          minsan=r["minsan"], ids=[seen[r["minsan"]], rid]))
                seen[r["minsan"]] = rid
                if sez == "nota99":
                    note = norm(" - ".join(x for x in (r["rimborso"], r["indicazioni"]) if x))
                else:
                    note = norm(r["note"])
                item = {
                    "id": rid,
                    "minsan": r["minsan"],
                    "descrizione": r["descrizione"],
                    "principio_attivo": r["principio_attivo"],
                    "note": note,
                    "note_originale": note,
                    "aggiornato": None,
                    "pagina": r["pagina"],
                }
                if sez == "diretta":
                    item["atc"] = r["atc"]
                if not item["descrizione"]:
                    anomalies.append(dict(pagina=r["pagina"], tipo="descrizione_vuota",
                                          minsan=r["minsan"], id=rid))
                out.append(item)

            with open(os.path.join(DATA, f"{sez}.json"), "w", encoding="utf-8") as f:
                json.dump(out, f, ensure_ascii=False, indent=2)

            fields = ["id", "minsan", "descrizione", "principio_attivo", "note", "note_originale",
                      "aggiornato", "pagina"]
            if sez == "diretta":
                fields.insert(4, "atc")
            with open(os.path.join(CSV_DIR, f"{sez}.csv"), "w", encoding="utf-8", newline="") as f:
                w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
                w.writeheader()
                for item in out:
                    w.writerow({k: (json.dumps(item[k], ensure_ascii=False) if isinstance(item[k], (dict, list))
                                    else item[k]) for k in fields})

            qc["sezioni"][sez] = dict(
                pagine=sorted(per_page, key=int),
                righe_per_pagina=per_page,
                totale=len(out),
                ids_duplicati=len(out) - len(set(i["id"] for i in out)),
                minsan_duplicati=len(out) - len(set(i["minsan"] for i in out)),
                descrizioni_vuote=sum(1 for i in out if not i["descrizione"]),
                principi_attivi_vuoti=sum(1 for i in out if not i["principio_attivo"]),
                note_vuote=sum(1 for i in out if not i["note"]),
                anomalie=anomalies,
            )
            all_rows[sez] = out

    qc["tempo_secondi"] = round(time.time() - t0, 1)
    qc["totale_righe"] = sum(len(v) for v in all_rows.values())
    with open(os.path.join(BASE, "qc_report.json"), "w", encoding="utf-8") as f:
        json.dump(qc, f, ensure_ascii=False, indent=2)

    save_progress(1, "running", {k: len(v) for k, v in all_rows.items()},
                  "Step 1 estrazione meccanica completata su DPC, DIRETTA e NOTA 99")
    print(json.dumps({k: dict(totale=len(v), per_pagina=qc["sezioni"][k]["righe_per_pagina"],
                              anomalie=len(qc["sezioni"][k]["anomalie"]))
                      for k, v in all_rows.items()}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
