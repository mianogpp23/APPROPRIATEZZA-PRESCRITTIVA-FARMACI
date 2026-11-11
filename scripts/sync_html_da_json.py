#!/usr/bin/env python3
"""Sincronizza TUTTI gli HTML di html_estratto con la fonte di verita' data/dati_farmaci.json.

Per ogni pagina:
  - schema standard (record con minsan/aic + descrizione/principio_attivo/note): ogni <td> viene
    confrontato con il valore JSON (normalizzato: entity HTML e spazi) e riscritto solo se diverso;
  - schema 'cells' (record con array cells[]): le celle della riga vengono allineate al record;
  - colonne multiple (nota_99: indicazioni_bpc + ssn): ogni colonna e' confrontata con il campo JSON
    corrispondente, non con la stringa 'note' aggregata.
Le righe HTML senza record corrispondente e i record senza riga vengono segnalati.

Uso:
    python3 sync_html_da_json.py --dry-run     (verifica, non scrive)
    python3 sync_html_da_json.py --apply       (scrive)
"""
from __future__ import annotations

import argparse
import html as htmllib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "html_estratto"
DATA = ROOT / "data" / "dati_farmaci.json"

# pagina -> (elenchi, [(classe td, campo json)], id_field)
PAGES: dict[str, dict] = {
    "metilfenidato.html": {
        "elenchi": ["metilfenidato"],
        "id": "minsan",
        "cols": [("minsan", "minsan"), ("descr", "descrizione"),
                 ("princ", "principio_attivo"), ("atc", "atc"), ("pt", "note")],
    },
    "farmaci_dpc.html": {
        "elenchi": ["farmaci_dpc"],
        "id": "minsan",
        "cols": [("minsan", "minsan"), ("descr", "descrizione"),
                 ("princ", "principio_attivo"), ("pt", "note")],
        # le 9 righe METILFENIDATO ospitate nella pagina DPC hanno testo proprio nel DPC
        # ("METILFENIDATO CLORIDRATO EROGARE IN CONVENZIONATA"): non si sovrascrivono,
        # ma la nota aggiornata va propagata anche li'.
        "note_only_map": {"metilfenidato": ("pt", "note")},
    },
    "distribuzione_diretta.html": {
        "elenchi": ["distribuzione_diretta"],
        "id": "aic",
        "cols": [("aic", "aic"), ("farm", "descrizione"), ("atc", "atc"),
                 ("princ", "principio_attivo"), ("pt", "note")],
    },
    "nota_99.html": {
        "elenchi": ["nota_99"],
        "id": "aic",
        # la colonna 'bpc' mostra la nota (con eventuale marker) quando c'e', altrimenti indicazioni_bpc
        "cols": [("aic", "aic"), ("med", "descrizione"), ("princ", "principio_attivo"),
                 ("bpc", "@bpc"), ("ssn", "ssn")],
        "skip_note": True,
    },
    "farmaci_no_dpc.html": {"elenchi": ["farmaci_no_dpc"], "cells_schema": True},
    "formalismi.html": {"elenchi": ["formalismi"], "cells_schema": True},
    # pagina generata dal suo generatore (scripts/build_dpc_convenzionata.py): si applicano solo
    # note e pillole, la sincronizzazione delle righe e' gestita dal generatore
    "dpc_convenzionata.html": {"elenchi": [], "solo_note": True},
}


def norm(s: str) -> str:
    s = htmllib.unescape(s or "")
    s = re.sub(r"<br\s*/?>", " ", s, flags=re.I)
    s = re.sub(r"<[^>]+>", "", s)
    s = s.replace("\xa0", " ")
    return re.sub(r"\s+", " ", s).strip()


def esc(s: str, quote: bool = True) -> str:
    return htmllib.escape(s or "", quote=quote)


NOTE_TOKEN_RE = re.compile(r"(\[[^\]]*\]|\*\*[^*]+\*\*)")


def render_note_html(text: str) -> str:
    """Testo di nota: **grassetto**, marker [agg. ...] reso cliccabile, resto escaped."""
    out: list[str] = []
    for part in NOTE_TOKEN_RE.split(text or ""):
        if not part:
            continue
        if part.startswith("[") and part.endswith("]") and "[agg." in part:
            out.append(render_note(part))
        elif part.startswith("**") and part.endswith("**"):
            out.append(f"<strong>{esc(part[2:-2])}</strong>")
        else:
            out.append(esc(part))
    return "".join(out)


def load_note_pagine() -> dict:
    try:
        return json.loads(NOTE_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def load_pillole_pagine() -> dict:
    try:
        return json.loads(PILLOLE_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def apply_pillole_pagina(text: str, fname: str, pillole: dict) -> str:
    """Inserisce/aggiorna il blocco di pillole operative (regole in primo piano)."""
    spec = pillole.get(fname)
    if not spec or not spec.get("pillole"):
        return text
    parti = [PILL_BEGIN]
    if spec.get("titolo"):
        parti.append(f'    <div class="pills-title">{esc(spec["titolo"])}</div>\n')
    parti.append('    <div class="pills">\n')
    for p in spec["pillole"]:
        link = p.get("link") or {}
        rif = ""
        if link.get("url"):
            rif = (f' &middot; <a class="pill-link" href="{link["url"]}" target="_blank" '
                   f'rel="noopener">{esc(link.get("t") or link["url"])}</a>')
        parti.append(
            f'      <div class="pill"><b>{esc(p.get("t", ""))}</b>'
            f'<span class="pill-d">{esc(p.get("d", ""))}{rif}</span></div>\n')
    parti.append("    </div>\n")
    parti.append(PILL_END)
    blocco = "".join(parti)
    if PILL_BEGIN in text and PILL_END in text:
        inizio = text.index(PILL_BEGIN)
        fine = text.index(PILL_END) + len(PILL_END)
        return text[:inizio] + blocco + text[fine:]
    # inserimento dopo il titolo h1 (o prima del primo <table>)
    ancore = [text.find("</h1>"), text.find("<table")]
    ancore = [a for a in ancore if a != -1]
    if not ancore:
        return text
    pos = min(ancore) + (len("</h1>") if min(ancore) == text.find("</h1>") else 0)
    return text[:pos] + "\n\n" + blocco + text[pos:]


def apply_note_pagina(text: str, fname: str, note_pagine: dict) -> str:
    """Inserisce/aggiorna il blocco di note di pagina (dal file data/note_pagine.json)."""
    spec = note_pagine.get(fname)
    if not spec or not spec.get("note"):
        return text
    parti = [NOTE_BEGIN]
    for nota in spec["note"]:
        if nota.get("h"):
            parti.append(f"    <h2>{esc(nota['h'])}</h2>\n")
        if nota.get("p"):
            parti.append(f"    <p>{render_note_html(nota['p'])}</p>\n")
    parti.append(NOTE_END)
    blocco = "".join(parti)

    if NOTE_BEGIN in text and NOTE_END in text:
        inizio = text.index(NOTE_BEGIN)
        fine = text.index(NOTE_END) + len(NOTE_END)
        return text[:inizio] + blocco + text[fine:]
    fine = text.find("</table>")
    if fine == -1:
        return text
    fine += len("</table>")
    return text[:fine] + "\n\n" + blocco + text[fine:]


def load_records() -> list[dict]:
    return json.loads(DATA.read_text(encoding="utf-8"))


def rows_of(text: str) -> list[re.Match]:
    return list(re.finditer(r"<tr\b[^>]*>.*?</tr>", text, re.S))


def cells_of(row: str) -> list[tuple[str, str]]:
    out = []
    for m in re.finditer(r"(<td[^>]*>)(.*?)(</td>)", row, re.S):
        cls = ""
        cm = re.search(r'class="([^"]+)"', m.group(1))
        if cm:
            cls = cm.group(1)
        out.append((cls, m.group(2)))
    return out


def key_for_cells(rec: dict) -> str:
    c = rec.get("cells") or []
    return "|".join(norm(x) for x in c[:2]) if len(c) >= 2 else norm(c[0] if c else "")


def key_for_row(cells: list[tuple[str, str]]) -> str:
    vals = [norm(v) for _, v in cells]
    return "|".join(vals[:2]) if len(vals) >= 2 else (vals[0] if vals else "")


def sync_page(fname: str, spec: dict, records: list[dict]) -> tuple[str, dict]:
    path = HTML / fname
    text = path.read_text(encoding="utf-8")
    stats = {"fixed_cells": 0, "fixed_rows": 0, "missing": 0, "extra": 0, "checked": 0, "reported": 0}
    if spec.get("solo_note"):
        return text, stats

    if spec.get("cells_schema"):
        recs = [r for r in records if r.get("elenco") in spec["elenchi"]]
        by_key = {key_for_cells(r): r for r in recs}
        out: list[str] = []
        pos = 0
        for m in rows_of(text):
            out.append(text[pos:m.start()])
            row = m.group(0)
            cs = cells_of(row)
            if not cs:
                out.append(row)
                pos = m.end()
                continue
            rec = by_key.get(key_for_row(cs))
            if rec is None:
                stats["extra"] += 1
                out.append(row)
                pos = m.end()
                continue
            expected = [norm(x) for x in (rec.get("cells") or [])]
            if len(expected) != len(cs):
                stats["extra"] += 1
                out.append(row)
                pos = m.end()
                continue
            stats["checked"] += 1
            new_row = row
            changed = False
            for i, (cls, cur) in enumerate(cs):
                raw_cell = str((rec.get("cells") or [])[i])
                if "[agg." in raw_cell:
                    target = render_note(raw_cell, contesto_riga(rec, cs))
                    if target != cur:
                        new_row = new_row.replace(f">{cur}<", f">{target}<", 1)
                        stats["fixed_cells"] += 1
                        changed = True
                    continue
                if norm(cur) == expected[i]:
                    continue
                # scrittura solo per i marker di aggiornamento mancanti: la formattazione
                # redazionale (es. <br>) e il testo dell'HTML restano quelli esistenti
                missing = marker_mancanti(cur, raw_cell)
                if not missing:
                    stats["reported"] += 1
                    continue
                value = str(cur) + " " + " ".join(missing)
                new_row = new_row.replace(f">{cur}<", f">{esc(value)}<", 1)
                stats["fixed_cells"] += 1
                changed = True
            if changed:
                stats["fixed_rows"] += 1
            out.append(new_row)
            pos = m.end()
        out.append(text[pos:])
        text = "".join(out)
    else:
        recs = [r for r in records if r.get("elenco") in spec["elenchi"]]
        by_id = {str(r.get(spec["id"]) or "").strip(): r for r in recs}
        note_map: dict[str, tuple[str, str, dict]] = {}
        for el, (cls, field) in (spec.get("note_only_map") or {}).items():
            for r in records:
                if r.get("elenco") != el:
                    continue
                rid = str(r.get(spec["id"]) or r.get("minsan") or r.get("aic") or "").strip()
                note_map[rid] = (cls, field, r)
        out = []
        pos = 0
        seen: set[str] = set()
        for m in rows_of(text):
            out.append(text[pos:m.start()])
            row = m.group(0)
            cs = cells_of(row)
            pos = m.end()
            if not cs:
                out.append(row)
                continue
            rid = norm(cs[0][1])
            rec = by_id.get(rid)
            if rec is None:
                # nota propagata da un altro elenco (es. metilfenidato dentro la pagina DPC)
                alt = note_map.get(rid)
                if alt is not None:
                    cls, field, alt_rec = alt
                    want = str(alt_rec.get(field) or "")
                    cur = next((v for c, v in cs if c == cls), None)
                    if cur is not None and "[agg." in want:
                        target = render_note(want, contesto_riga(alt_rec, cs))
                        if target == cur:
                            continue
                        if "<" in cur and norm(strip_tags(target)) != norm(cur):
                            stats["reported"] += 1
                        else:
                            row = row.replace(f">{cur}<", f">{target}<", 1)
                            stats["fixed_cells"] += 1
                            stats["fixed_rows"] += 1
                    elif cur is not None and norm(cur) != norm(want):
                        missing = marker_mancanti(cur, want)
                        if not missing:
                            stats["reported"] += 1
                        else:
                            row = row.replace(f">{cur}<", f">{esc(str(cur) + ' ' + ' '.join(missing))}<", 1)
                            stats["fixed_cells"] += 1
                            stats["fixed_rows"] += 1
                else:
                    stats["extra"] += 1
                out.append(row)
                pos = m.end()
                continue
            seen.add(rid)
            stats["checked"] += 1
            new_row = row
            changed = False
            for cls, field in spec["cols"]:
                if field == "@bpc":
                    want = norm(str(rec.get("note") or "")) if "[agg." in (rec.get("note") or "") \
                        else norm(str(rec.get("indicazioni_bpc") or ""))
                else:
                    want = norm(str(rec.get(field) or ""))
                cur = next((v for c, v in cs if c == cls), None)
                if cur is None:
                    continue
                raw = str(rec.get(field) or "") if field != "@bpc" else str(
                    rec.get("note") or "" if "[agg." in (rec.get("note") or "") else rec.get("indicazioni_bpc") or "")
                if "[agg." in raw:
                    target = render_note(raw, contesto_riga(rec, cs))
                    if target == cur:
                        continue
                    cur_plain = re.sub(r'<a class="src".*?</a>', '', cur, flags=re.S)
                    if "<" in cur_plain and norm(strip_tags(target)) != norm(cur):
                        # cella con formattazione propria e testo diverso: non si tocca
                        stats["reported"] += 1
                        continue
                    new_row = new_row.replace(f">{cur}<", f">{target}<", 1)
                    stats["fixed_cells"] += 1
                    changed = True
                    continue
                if norm(cur) == want:
                    continue
                # la cella deve riflettere il JSON (fonte di verita')
                target = esc(raw)
                cur_plain = re.sub(r'<a class="src".*?</a>', '', cur, flags=re.S)
                if "<" in cur_plain:
                    stats["reported"] += 1
                    continue
                new_row = new_row.replace(f">{cur}<", f">{target}<", 1)
                stats["fixed_cells"] += 1
                changed = True
                continue
            if changed:
                stats["fixed_rows"] += 1
            out.append(new_row)
        out.append(text[pos:])
        text = "".join(out)
        stats["missing"] = len([k for k in by_id if k and k not in seen])
        # righe presenti nei dati ma assenti dalla tabella -> inserite in ordine alfabetico
        if stats["missing"]:
            text, aggiunte = insert_missing_rows(text, spec, recs, seen)
            stats["inserted"] = len(aggiunte)
            stats["missing"] = 0
            if aggiunte:
                print(f"[{fname}] righe inserite: {', '.join(aggiunte)}")

    return text, stats


MARKER_RE = re.compile(r"\[agg\.[^\[]+?(?=\[agg\.|$)")
MARKER_TAG_RE = re.compile(r"\[agg\.[^\]]*\]")

LINKS_FILE = Path(__file__).with_name("fonti_links.json")
NOTE_FILE = ROOT / "data" / "note_pagine.json"
PILLOLE_FILE = ROOT / "data" / "pillole_pagine.json"
INDICE_PAGINE_FILE = ROOT / "data" / "pdf_pagine_ocr.json"
NOTE_BEGIN = "    <!-- DPC-NOTE-BEGIN -->\n"
NOTE_END = "    <!-- DPC-NOTE-END -->\n"
PILL_BEGIN = "    <!-- DPC-PILL-BEGIN -->\n"
PILL_END = "    <!-- DPC-PILL-END -->\n"
_INDICE: dict | None = None


def indice_pagine() -> dict:
    """Indice OCR delle pagine dei PDF locali (per il deep linking 'documento.pdf#page=N')."""
    global _INDICE
    if _INDICE is None:
        try:
            _INDICE = json.loads(INDICE_PAGINE_FILE.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            _INDICE = {}
    return _INDICE


def normalizza(s: str) -> str:
    return re.sub(r"[^A-Z0-9]", "", (s or "").upper())


def pagina_documento(file_name: str, contesto: str) -> int | None:
    """Pagina del PDF in cui compare il farmaco indicato (dal nome commerciale)."""
    pagine = indice_pagine().get(file_name)
    if not pagine or not contesto:
        return None
    marchio = str(contesto).split("*")[0]
    marchio = re.split(r"\s+[–—-]\s+", marchio)[0]
    chiave = normalizza(marchio)
    if len(chiave) < 4:
        return None
    migliore = None
    migliore_conteggio = 0
    for pagina, testo in pagine.items():
        n = testo.count(chiave)
        if n > migliore_conteggio:
            migliore_conteggio = n
            migliore = int(pagina)
    return migliore


def load_links() -> list[tuple[str, str]]:
    try:
        data = json.loads(LINKS_FILE.read_text(encoding="utf-8"))
        return [(p, u) for p, u in data.get("link", [])]
    except Exception:
        return []


LINKS = load_links()


def strip_tags(h: str) -> str:
    """Rimuove i tag HTML (per confrontare il testo renderizzato con quello della cella)."""
    return re.sub(r"<[^>]+>", "", h or "")


def link_for(inner: str, contesto: str = "") -> str:
    """URL del provvedimento per un marker '[agg. ...]' (primo pattern che corrisponde).

    Se il marker cita la pagina di un PDF ('pag. N'), si aggiunge il frammento #page=N.
    Se il link e' un PDF locale e la riga indica un farmaco, si aggiunge la pagina del PDF in cui
    il farmaco compare (deep linking: il link apre la pagina esatta, non il documento generico).
    """
    for pattern, url in LINKS:
        if pattern in inner:
            m = re.search(r"pag\.\s*(\d+)", inner)
            if m and url.lower().endswith(".pdf"):
                return f"{url}#page={m.group(1)}"
            if url.lower().endswith(".pdf") and contesto:
                nome = url.split("/")[-1].split("#")[0]
                pagina = pagina_documento(nome, contesto)
                if pagina:
                    return f"{url}#page={pagina}"
            return url
    return ""


def render_note(text: str, contesto: str = "") -> str:
    """Trasforma il testo della nota JSON in HTML, rendendo cliccabile il riferimento al provvedimento."""
    out: list[str] = []
    pos = 0
    for m in MARKER_TAG_RE.finditer(text or ""):
        out.append(esc(text[pos:m.start()]))
        inner = m.group(0)
        url = link_for(inner, contesto)
        label = inner
        if url:
            out.append(
                f'<a class="src" href="{url}" target="_blank" rel="noopener" '
                f'title="Apri il provvedimento: {esc(label, quote=True)}">{esc(label)}</a>'
            )
        else:
            out.append(esc(inner))
        pos = m.end()
    out.append(esc(text[pos:]))
    return "".join(out)


def marker_mancanti(cell_text: str, json_value: str) -> list[str]:
    """Marker presenti nel JSON ma assenti nella cella HTML (da aggiungere, senza toccare il resto)."""
    have = {m.strip() for m in MARKER_RE.findall(cell_text or "")}
    out = []
    for m in MARKER_RE.findall(json_value or ""):
        m = m.strip()
        if m and m not in have:
            out.append(m)
    return out


def contesto_riga(rec: dict, cells: list[tuple[str, str]] | None = None) -> str:
    """Nome commerciale della riga: serve al deep linking (pagina del PDF in cui compare)."""
    d = str(rec.get("descrizione") or "")
    if not d and cells and len(cells) > 1:
        d = norm(cells[1][1])
    return d


def build_row(spec: dict, rec: dict) -> str:
    """Genera una riga <tr> dalle colonne della pagina (per le righe mancanti)."""
    cells = []
    for cls, field in spec["cols"]:
        if field == "@bpc":
            val = str(rec.get("note") or "") if "[agg." in (rec.get("note") or "") else str(rec.get("indicazioni_bpc") or "")
        else:
            val = str(rec.get(field) or "")
        cells.append(f'                <td class="{cls}">{render_note(val, contesto_riga(rec)) if "[agg." in val else esc(val)}</td>')
    return '<tr class="drug">\n' + "\n".join(cells) + "\n            </tr>"


def sort_key(spec: dict, rec: dict) -> str:
    for cls, field in spec["cols"]:
        if cls in ("descr", "med", "farm"):
            return str(rec.get(field) or "").upper()
    return str(rec.get("aic") or rec.get("minsan") or "")


def insert_missing_rows(text: str, spec: dict, records: list[dict], seen: set[str]) -> tuple[str, list[str]]:
    """Inserisce le righe presenti nei dati ma assenti nella tabella, in ordine alfabetico."""
    if "cols" not in spec or spec.get("no_insert"):
        return text, []
    mancanti = []
    for rec in records:
        rid = str(rec.get(spec.get("id") or "aic") or "").strip()
        if rid and rid not in seen:
            mancanti.append(rec)
    if not mancanti:
        return text, []
    for rec in sorted(mancanti, key=lambda r: sort_key(spec, r)):
        row = build_row(spec, rec)
        key = sort_key(spec, rec)
        idx = 0
        for m in re.finditer(r"<tr\b.*?</tr>", text, flags=re.S):
            body = m.group(0)
            cells = cells_of(body)
            if not cells:
                continue
            cur_key = norm(cells[1][1]).upper() if len(cells) > 1 else ""
            if cur_key > key:
                idx = m.start()
                break
            idx = m.end()
        text = text[:idx] + row + "\n" + text[idx:]
    return text, [str(r.get("aic") or r.get("minsan")) for r in mancanti]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    if not args.apply and not args.dry_run:
        ap.error("specificare --dry-run o --apply")

    records = load_records()
    note_pagine = load_note_pagine()
    pillole_pagine = load_pillole_pagine()
    total = 0
    changed_files: list[str] = []
    for fname, spec in PAGES.items():
        path = HTML / fname
        if not path.exists():
            print(f"[skip] {fname} non trovato")
            continue
        new, st = sync_page(fname, spec, records)
        new = apply_note_pagina(new, fname, note_pagine)
        new = apply_pillole_pagina(new, fname, pillole_pagine)
        changed = new != path.read_text(encoding="utf-8")
        total += st["fixed_cells"]
        print(f"[{fname}] righe verificate {st['checked']} | celle allineate {st['fixed_cells']} "
              f"| righe modificate {st['fixed_rows']} | record senza riga {st['missing']} "
              f"| righe senza record {st['extra']} | differenze solo testuali (non scritte) {st['reported']} "
              f"| file cambiato: {changed}")
        if changed and args.apply:
            path.write_text(new, encoding="utf-8")
            changed_files.append(fname)

    if args.apply:
        # snapshot dei dati e nota di sincronizzazione dentro il repo (il sito resta identico)
        import shutil
        import datetime as dt
        snap = HTML / "dati_farmaci.json"
        shutil.copy2(DATA, snap)
        markers = sum((HTML / f).read_text(encoding="utf-8").count("[agg.") for f in PAGES if (HTML / f).exists())
        rows = sum(1 for r in records)
        (HTML / "README_SYNCHRONIZZAZIONE.md").write_text(
            "# Sincronizzazione dati ↔ HTML\n\n"
            f"- **Fonte di verita'**: `data/dati_farmaci.json` "
            f"({rows} record, {sum(len(r.get('variazioni') or []) for r in records)} variazioni)\n"
            f"- **Snapshot versionato qui**: `dati_farmaci.json` (copia generata automaticamente)\n"
            f"- **Marker di aggiornamento negli HTML**: {markers} occorrenze `[agg. <data> – <fonte>]`\n"
            f"- **Rigenerazione**: `python3 scripts/sync_html_da_json.py --apply`\n"
            f"- **Ultima sincronizzazione**: {dt.datetime.now().isoformat(timespec='seconds')}\n\n"
            "Il sito statico non dipende dal JSON: il JSON serve per tracciare la versione dei dati\n"
            "da cui sono state generate le pagine e per rigenerarle in futuro.\n",
            encoding="utf-8",
        )
        changed_files += ["dati_farmaci.json", "README_SYNCHRONIZZAZIONE.md"]
        print(f"[snapshot] dati_farmaci.json + README_SYNCHRONIZZAZIONE.md aggiornati")

    print(f"\n[{'APPLICATO' if args.apply else 'DRY-RUN'}] celle allineate totali: {total}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
