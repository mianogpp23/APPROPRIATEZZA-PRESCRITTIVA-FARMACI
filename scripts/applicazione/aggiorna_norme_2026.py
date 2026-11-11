#!/usr/bin/env python3
"""Aggiornamenti normativi 2026 sulle liste DPC (giro post-indicizzazione dell'archivio documentale).

Fonti:
  - Det. AIFA 819/2026 (Nota 39, GH) e 820/2026 (Nota 74, infertilita') - G.U. n. 144 del 24/06/2026,
    in vigore dal 09/07/2026 (prot. Regione Siciliana 35765 del 09/07/2026 e nota su PT Nota 39).
  - Circolare Federfarma 420 del 27/11/2025 "Nota 100 - Precisazioni" (elenco eccezioni).
  - Revoche AIC: determina AIFA del 02/01/2026 (SANIFOLIN) e del 09/12/2025 (ZOMACTON).

Uso:
    python3 aggiorna_norme_2026.py --dry-run
    python3 aggiorna_norme_2026.py --apply      (richiede CONFERMA dell'utente)
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

M39 = " [agg. 09/07/2026 – Det. AIFA 819/2026, G.U. n. 144 del 24/06/2026] modello PT unico (prot. Reg. Sic. 09/07/2026): i PT emessi prima restano esibili fino a scadenza"
V39 = {
    "data": "09/07/2026",
    "fonte": "Det. AIFA 819/2026 (G.U. n. 144 del 24/06/2026) – prot. Regione Siciliana 09/07/2026",
    "url_o_percorso": "https://www.regione.sicilia.it/istituzioni/regione/strutture-regionali/assessorato-salute/dipartimento-pianificazione-strategica/appropriatezza-d-uso-farmaci",
    "testo_breve": "Nota AIFA 39 (ormone somatotropo) aggiornata: nuovi criteri diagnostici e prescrittivi; "
                   "modelli di PT unici obbligatori dal 09/07/2026",
    "stato": "approvata",
}

M74 = " [agg. 09/07/2026 – Det. AIFA 820/2026, G.U. n. 144 del 24/06/2026] limite di eta' della donna per la rimborsabilita' SSN elevato da 45 a 46 anni"
V74 = {
    "data": "09/07/2026",
    "fonte": "Det. AIFA 820/2026 (G.U. n. 144 del 24/06/2026) – prot. Regione Siciliana 35765 del 09/07/2026",
    "url_o_percorso": "https://www.regione.sicilia.it/istituzioni/regione/strutture-regionali/assessorato-salute/dipartimento-pianificazione-strategica/appropriatezza-d-uso-farmaci",
    "testo_breve": "Nota AIFA 74 (infertilita') aggiornata: limite di eta' della donna 45 -> 46 anni (LEA 2025); "
                   "PT informatizzato confermato",
    "stato": "approvata",
}

REV_SANIFOLIN = " [agg. 02/01/2026 – revoca AIC AIFA, circ. Fed. 4/2026] AIC revocato su rinuncia del titolare: scorte esauribili entro 180 gg dalla G.U."
REV_ZOMACTON = " [agg. 09/12/2025 – revoca AIC AIFA, circ. Fed. 429/2025] AIC revocato su rinuncia del titolare: scorte esauribili entro 180 gg dalla G.U."

V_REV_SAN = {
    "data": "02/01/2026",
    "fonte": "Revoca AIC AIFA (determine del 02/01/2026) – circolare Federfarma 4 del 02/01/2026",
    "url_o_percorso": "raw/sources/SRC-2026-11-10-197",
    "testo_breve": "SANIFOLIN 1 fiala IM EV 50 mg (AIC 027683046) e 10 cpr 15 mg (AIC 027683010): AIC revocati su rinuncia",
    "stato": "approvata",
}
V_REV_ZOMA = {
    "data": "09/12/2025",
    "fonte": "Revoca AIC AIFA (determine del 09/12/2025) – circolare Federfarma 429 del 09/12/2025",
    "url_o_percorso": "raw/sources/SRC-2026-11-10-263",
    "testo_breve": "ZOMACTON 1 flaconcino SC 4 mg (AIC 027743032) e confezioni 10 mg: AIC revocati su rinuncia",
    "stato": "approvata",
}

M100_OK = " [agg. 27/11/2025 – circ. Fed. 420/2025] eccezione alla Nota 100: prescrivibile SSN anche senza nota 100 per indicazioni diverse dal diabete T2"
M100_ATT = " [agg. 27/11/2025 – circ. Fed. 420/2025] ATTENZIONE: non rientra nelle eccezioni alla Nota 100 (solo FORXIGA 5/10 mg e JARDIANCE 10 mg): per il diabete T2 la Nota 100 resta obbligatoria"
V100 = {
    "data": "27/11/2025",
    "fonte": "Circolare Federfarma 420 del 27/11/2025 – Nota 100 Precisazioni (allegato n.1)",
    "url_o_percorso": "raw/sources/SRC-2026-11-10-269",
    "testo_breve": "Nota 100 confermata obbligatoria; eccezioni: FORXIGA 5 mg (042494029), FORXIGA 10 mg (042494070), "
                   "JARDIANCE 10 mg (043443136)",
    "stato": "approvata",
}

SGLT2_OK = {"042494029", "042494070", "043443136"}
SGLT2_ATT = {"043443047"}

NOTA99_SCHEDA = (
    '<p class="scheda-nota"><strong>Aggiornamento 09/07/2026 – Det. AIFA 822/2026 (G.U. n. 144 del 24/06/2026), '
    'prot. Regione Siciliana 35765 del 09/07/2026:</strong> testo della Nota 99 aggiornato sulle linee guida GOLD; '
    '<strong>abrogata la Scheda di Valutazione e Prescrizione Specialistica (SVP)</strong> per i medicinali BPCO '
    '(LABA, LAMA, ICS in singolo erogatore o in associazione) e regime di fornitura riclassificato da RRL a RR. '
    'Le triplici associazioni LAMA+LABA+ICS sono prescrivibili dal MMG in ricetta rossa ripetibile (v. variazioni del 09/07/2026).</p>'
)


def rules_for_note(note: str, aic: str) -> tuple[str, list[dict]]:
    """Restituisce (testo da accodare, variazioni) per una nota JSON."""
    suffix, vars_ = "", []
    if "Nota 39" in note and "agg. 09/07/2026 – Det. AIFA 819/2026" not in note:
        suffix += M39
        vars_.append(dict(V39))
    if "Nota 74" in note and "agg. 09/07/2026 – Det. AIFA 820/2026" not in note:
        suffix += M74
        vars_.append(dict(V74))
    if aic == "027683046" and "revoca AIC AIFA, circ. Fed. 4/2026" not in note:
        suffix += REV_SANIFOLIN
        vars_.append(dict(V_REV_SAN))
    if aic == "027743032" and "revoca AIC AIFA, circ. Fed. 429/2025" not in note:
        suffix += REV_ZOMACTON
        vars_.append(dict(V_REV_ZOMA))
    if aic in SGLT2_OK and "circ. Fed. 420/2025" not in note:
        suffix += M100_OK
        vars_.append(dict(V100))
    if aic in SGLT2_ATT and "circ. Fed. 420/2025" not in note:
        suffix += M100_ATT
        vars_.append(dict(V100))
    return suffix, vars_


def patch_records(records: list[dict]) -> list[str]:
    log = []
    for r in records:
        note = r.get("note") or ""
        aic = str(r.get("aic") or r.get("minsan") or "").strip()
        suffix, vars_ = rules_for_note(note, aic)
        if suffix:
            r["note"] = note + suffix
            r.setdefault("variazioni", []).extend(vars_)
            log.append(f"{r.get('elenco'):<20} {aic} {str(r.get('descrizione'))[:34]:<34} :: {note[:42]!r}")
    return log


def patch_html(text: str) -> tuple[str, int]:
    """Applica le regole cella per cella, usando l'AIC della riga (<tr>) come contesto."""
    n = 0

    def fix_row(m):
        nonlocal n
        row = m.group(0)
        aic_m = re.search(r"<td[^>]*>\s*(\d{9,10})\s*</td>", row)
        aic = aic_m.group(1) if aic_m else ""

        def repl(cm):
            nonlocal n
            tag, inner, close = cm.group(1), cm.group(2), cm.group(3)
            if "class=\"pt\"" not in tag:
                return cm.group(0)
            suffix, _ = rules_for_note(inner, aic)
            if suffix:
                n += 1
                return f"{tag}{inner}{suffix}{close}"
            return cm.group(0)

        return re.sub(r"(<td[^>]*>)([^<>]*)(</td>)", repl, row)

    text = re.sub(r"<tr\b.*?</tr>", fix_row, text, flags=re.S)
    return text, n


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    if not args.apply and not args.dry_run:
        ap.error("specificare --dry-run o --apply")

    data = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    changes = patch_records(data)
    print(f"[JSON] record aggiornati: {len(changes)}")
    for c in changes[:40]:
        print("   ", c)
    if len(changes) > 40:
        print(f"    ... altri {len(changes)-40}")

    html_changes = []
    for f in sorted(HTML_DIR.glob("*.html")):
        txt = f.read_text(encoding="utf-8")
        new, n = patch_html(txt)
        if n:
            html_changes.append((f, n))
            print(f"[HTML] {f.name}: {n} celle")

    # nota di scheda Nota 99
    f99 = HTML_DIR / "nota_99.html"
    if f99.exists():
        t = f99.read_text(encoding="utf-8")
        if "scheda-nota" not in t:
            html_changes.append((f99, 0))
            print("[HTML] nota_99.html: inserita nota di scheda (SVP abolita, RRL->RR)")

    if args.dry_run:
        print("\n[DRY-RUN] nessuna scrittura.")
        return 0

    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    backup = ROOT / "output" / f"backup-norme-2026-{stamp}"
    backup.mkdir(parents=True, exist_ok=True)
    shutil.copy2(JSON_PATH, backup / JSON_PATH.name)
    for f, _ in html_changes:
        shutil.copy2(f, backup / f.name)
    print(f"[BACKUP] {backup}")

    JSON_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for f, _ in html_changes:
        txt = f.read_text(encoding="utf-8")
        new, _ = patch_html(txt)
        if f.name == "nota_99.html" and "scheda-nota" not in new:
            new = new.replace(
                '<h1 class="page-title">NOTA 99 - CONFEZIONI MEDICINALI PER USO INALATORIO</h1>',
                '<h1 class="page-title">NOTA 99 - CONFEZIONI MEDICINALI PER USO INALATORIO</h1>\n    ' + NOTA99_SCHEDA,
                1,
            )
        f.write_text(new, encoding="utf-8")
    print(f"[DONE] {len(changes)} record JSON e {sum(n for _, n in html_changes)} celle HTML aggiornati.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
