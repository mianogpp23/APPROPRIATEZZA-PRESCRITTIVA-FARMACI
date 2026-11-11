#!/usr/bin/env python3
"""Genera la pagina 'dpc_convenzionata.html' (scheda 07) dal documento ufficiale.

Fonte primaria: FARMACI-DIATETE-TIPO-2-A-NOTA-AIFA-100.pdf (2 pagine):
  - pag. 1: farmaci diabete tipo 2 a Nota AIFA 100 che RESTANO IN DPC (GLP-1 RA, GIP/GLP-1 RA)
             con le regole operative (PT on-line, Protocollo DMDU0A0000, fuori regione)
  - pag. 2: farmaci passati IN CONVENZIONATA dal 15 ottobre 2025 (tabelle per molecola)
             + nota di eccezione per Dapagliflozin (FORXIGA) ed Empagliflozin (JARDIANCE)
Arricchimento: confezioni AIC e flag "Nota 100 obbligatoria" dall'export AIFA (archivio documentale).
Uso: python3 build_dpc_convenzionata.py
"""
from __future__ import annotations

import datetime as dt
import html as htmllib
import json
import os
import re
from pathlib import Path

import pdfplumber

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "html_estratto"
PDF = ROOT / "docs" / "dpc" / "FARMACI-DIATETE-TIPO-2-A-NOTA-AIFA-100.pdf"
PDF_NEL_SITO = "docs/diabete-tipo2-nota-100.pdf"
DATA = json.loads((ROOT / "data" / "dati_farmaci.json").read_text(encoding="utf-8"))
# export AIFA "Nota 100 obbligatoria": percorso configurabile (fuori dal progetto).
# Se assente il generatore continua con i dati delle liste regionali.
EXPORT = Path(os.environ.get("DPC_EXPORT_NOTA100",
                     str(ROOT / "docs" / "fonti_normative" / "export-nota100-obbligatoria.md")))

AIFA_NOTA100 = "https://www.aifa.gov.it/-/diabete-mellito-tipo2-aggiornamento-nota-aifa-100"
REGIONE = ("https://www.regione.sicilia.it/istituzioni/regione/strutture-regionali/assessorato-salute/"
           "dipartimento-pianificazione-strategica/appropriatezza-d-uso-farmaci")

# testi ripresi dal PDF (verificati a mano sul documento)
REGOLA = ("A far data dal 15 ottobre 2025 per le specialità di seguito indicate non deve essere compilata e "
          "allegata la &ldquo;Scheda di Valutazione e Prescrizione&rdquo; o verificata la presenza del "
          "&ldquo;Protocollo DMDU&rdquo; e l&rsquo;erogazione va operata nel canale della Convenzionata con "
          "obbligo di ricetta a Nota AIFA 100:")
ECCEZIONE = [
    ("DAPAGLIFLOZIN O EMPAGLIFOZIN costituiscono un&rsquo;eccezione, in quanto possono essere prescritti anche "
     "SENZA NOTA AIFA 100 e rimborsati in convenzionata nelle seguenti indicazioni:"),
    ("Dapagliflozin FORXIGA nelle indicazioni &ldquo;per il trattamento negli adulti dell&rsquo;insufficienza "
     "cardiaca cronica sintomatica in classe NYHA II e III con frazione di eiezione ridotta&rdquo; e "
     "&ldquo;malattia renale cronica&rdquo;"),
    ("Empaglifozin JARDIANCE nell&rsquo;indicazione &ldquo;per il trattamento negli adulti dell&rsquo;insufficienza "
     "cardiaca cronica sintomatica con frazione di eiezione ridotta&rdquo;"),
]
REGOLE_DPC = [
    ("Gli Specialisti in Sicilia, a decorrere dal 1&deg; settembre 2025, devono prescrivere detti farmaci come "
     "PT-online. Il Farmacista, all&rsquo;atto dell&rsquo;inserimento della ricetta sulla GopenDPC, riscontra la "
     "presenza del PT &ldquo;Autorizzato&rdquo; e, solo dopo, pu&ograve; procedere con l&rsquo;ordine nonch&eacute; alla "
     "successiva erogazione delle confezioni cos&igrave; autorizzate."),
    ("La Scheda di Valutazione e Prescrizione cartacea compilata dallo Specialista prima del 01/09/2025 &egrave; "
     "valida fino alla naturale scadenza della stessa e il Farmacista allega alla ricetta la Scheda in originale."),
    ("Nel caso di prescrizione proveniente da uno Specialista Fuori Regione, tenuto a compilare la prevista "
     "&ldquo;Scheda di Valutazione e Prescrizione&rdquo; cartacea, questa dovr&agrave; essere trasmessa a "
     "<b>dpc@asppalermo.org</b> per la prevista autorizzazione."),
    ("I Medici di Medicina Generale sono tenuti a compilare la Scheda di Valutazione e Prescrizione on-line su "
     "SistemaTS, che collega automaticamente alla ricetta il Protocollo <b>DMDU0A0000&hellip;</b>: la sua presenza "
     "deve essere riscontrata dal Farmacista a video oppure sulla ricetta, o, in mancanza, occorre allegare la "
     "fotocopia riportante il relativo protocollo DMDU."),
    ("N.B.: il Protocollo DMDU vale anche per le prescrizioni di MMG Fuori Regione su ricetta DEM."),
]


def esc(s: str) -> str:
    return htmllib.escape(str(s or ""), quote=True)


def norm_cella(c: str | None) -> str:
    return re.sub(r"\s+", " ", str(c or "")).strip()


def tabelle_pdf(page) -> list[tuple[str, str, str]]:
    """Elenco (gruppo, molecola, marchio) dalle tabelle del PDF."""
    out: list[tuple[str, str, str]] = []
    gruppo = ""
    for tab in page.find_tables():
        righe = tab.extract()
        # la tabella con la nota di eccezione (SENZA NOTA AIFA 100) non e' un elenco di farmaci
        if "SENZA NOTA AIFA 100" in " ".join(norm_cella(c) for r in righe for c in r):
            continue
        for r in righe:
            celle = [norm_cella(c) for c in r]
            if not any(celle):
                continue
            intest = next((c for c in celle if c.startswith("Molecola")), "")
            if intest:
                gruppo = re.sub(r"^Molecola\s*", "", intest).strip()
                continue
            non_vuote = [c for c in celle if c and c != "Nome Commerciale"]
            if len(non_vuote) < 2:
                continue
            molecola, marchio = non_vuote[0], non_vuote[-1]
            if marchio.upper().startswith("MOL"):
                continue
            out.append((gruppo, molecola, marchio))
    return out


def main() -> None:
    with pdfplumber.open(PDF) as pdf:
        in_dpc = tabelle_pdf(pdf.pages[0])
        in_conv = tabelle_pdf(pdf.pages[1])

    # export AIFA: (AIC, descrizione, Nota100 obbligatoria)
    export: list[tuple[str, str, str]] = []
    if EXPORT.exists():
        txt = EXPORT.read_text(encoding="utf-8")
        for m in re.finditer(r"^(\d{9,10})\s*\|\s*([^|]+?)\s*\|\s*(Si|No)\s*$", txt, re.M):
            export.append((m.group(1), m.group(2).strip(), m.group(3)))

    our: dict[str, dict] = {}
    for r in DATA:
        a = str(r.get("aic") or r.get("minsan") or "").strip()
        if a:
            our[a] = r

    def confezioni(brand: str) -> list[tuple[str, str, str]]:
        """(AIC, descrizione, Nota100 obbligatoria) dell'export AIFA per un marchio."""
        out: list[tuple[str, str, str]] = []
        pat = re.compile(r"^" + re.escape(brand) + r"(\b|\s)", re.I)
        escludi = re.compile(r"^" + re.escape(brand) + r"\s+MET\b", re.I)
        for aic, desc, flag in export:
            if not pat.match(desc):
                continue
            if escludi.match(desc) and " MET" not in brand.upper():
                continue
            out.append((aic, desc, flag))
        return out

    def riga(gruppo: str, molecola: str, marchio: str, convenzionata: bool) -> str:
        eccezione = marchio.strip().endswith("*")
        marchio = marchio.replace("*", " ").strip()
        marchi = [m.strip() for m in re.split(r"\s*[–—-]\s*", marchio) if m.strip()]
        conf: list[tuple[str, str, str]] = []
        for m in marchi:
            for c in confezioni(m):
                if c not in conf:
                    conf.append(c)
        aics = ", ".join(a for a, _, _ in conf[:8])
        if len(conf) > 8:
            aics += f" &hellip; ({len(conf)} confezioni)"
        in_dpc_n = sum(1 for a, _, _ in conf if a in our)
        if convenzionata:
            # regola del documento ufficiale: ricetta a Nota AIFA 100 obbligatoria
            flag = "Si" if conf else "&mdash;"
        else:
            flag = "Si" if any(f == "Si" for _, _, f in conf) else ("No" if conf else "&mdash;")
        eccezz = "Si" if eccezione else "no"
        return (
            f'<tr><td>{esc(gruppo)}</td><td>{esc(molecola)}</td>'
            f'<td>{esc(marchio)}</td><td class="aic">{aics or "&mdash;"}</td>'
            f'<td class="{"si" if in_dpc_n else "no"}">'
            f'{"si (" + str(in_dpc_n) + " conf.)" if in_dpc_n else "no"}</td>'
            f'<td class="{"si" if flag == "Si" else "no"}">{flag}</td>'
            f'<td class="{"si" if eccezione else "no"}">{eccezz}</td></tr>'
        )

    righe_conv = [riga(g, m, b, True) for g, m, b in in_conv]
    righe_dpc = [riga(g, m, b, False) for g, m, b in in_dpc]

    eccezione_html = "\n".join(
        f"    <li>{t}</li>" for t in ECCEZIONE
    )
    regole_html = "\n".join(f"    <li>{t}</li>" for t in REGOLE_DPC)

    page = (PAGE.replace("{GENERATED}", dt.datetime.now().strftime("%d/%m/%Y"))
            .replace("{PDF_NEL_SITO}", PDF_NEL_SITO)
            .replace("{REGIONE}", REGIONE)
            .replace("{AIFA_NOTA100}", AIFA_NOTA100)
            .replace("{REGOLA}", REGOLA)
            .replace("{ECCEZIONE}", eccezione_html)
            .replace("{REGOLE_DPC}", regole_html)
            .replace("{ROWS_CONV}", "\n".join(righe_conv))
            .replace("{ROWS_DPC}", "\n".join(righe_dpc)))
    (HTML / "dpc_convenzionata.html").write_text(page, encoding="utf-8")
    print(f"dpc_convenzionata.html generato: {len(righe_conv)} righe in convenzionata, "
          f"{len(righe_dpc)} righe che restano in DPC")


PAGE = r"""<!DOCTYPE html>
<html lang="it">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>DPC in Convenzionata — Nota AIFA 100 (diabete tipo 2)</title>
<link rel="stylesheet" href="theme.css">
<style>
    :root {
        --bg1: rgb(var(--t-bg-rgb)); --bg2: rgb(var(--t-bg2-rgb)); --accent: rgb(var(--t-accent-rgb));
        --accent2: rgb(var(--t-accent2-rgb)); --glass: rgba(var(--t-ov-rgb),0.06);
        --glass-border: rgba(var(--t-ov-rgb),0.16); --text: rgb(var(--t-text-rgb));
        --muted: rgb(var(--t-muted-rgb)); --red: rgb(var(--t-red-rgb)); --green: rgb(var(--t-green-rgb));
    }
    * { box-sizing: border-box; }
    body { margin:0; font-family: system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
        background: var(--bg1); color: var(--text); font-size: 17px; line-height: 1.5; }
    .wrap { max-width: 1600px; margin: 0 auto; padding: 28px 18px 60px; }
    h1 { color: var(--red); font-size: 28px; margin: 0 0 6px; text-transform: uppercase; }
    h2 { color: var(--green); font-size: 21px; margin: 26px 0 10px; }
    h3 { color: var(--accent); font-size: 17px; margin: 18px 0 8px; }
    .sub { color: var(--muted); margin-bottom: 16px; }
    .box { background: var(--glass); border: 1px solid var(--glass-border); border-left: 4px solid var(--red);
        border-radius: 12px; padding: 14px 18px; margin-bottom: 18px; }
    .box b { color: var(--green); }
    .box a { color: var(--accent); }
    .filters { display:flex; flex-wrap:wrap; gap:10px; align-items:center; margin-bottom:12px;
        position:sticky; top:0; background:rgba(var(--t-bg-rgb),.95); padding:12px 0; z-index:5;
        border-bottom:1px solid var(--glass-border); }
    input[type=text] { background:rgba(var(--t-ov-rgb),.07); border:1px solid var(--glass-border);
        color:var(--text); padding:9px 12px; border-radius:9px; font-size:15px; min-width:230px; }
    button { background:var(--accent); border:0; color:rgb(var(--t-onaccent-rgb)); font-weight:700; padding:9px 16px;
        border-radius:9px; font-size:15px; cursor:pointer; }
    #count { color:var(--muted); }
    .tablewrap { overflow:auto; max-height: 70vh; border:1px solid var(--glass-border); border-radius:12px; }
    table { border-collapse:collapse; width:100%; font-size:15px; }
    th, td { padding:9px 12px; border-bottom:1px solid rgba(var(--t-ov-rgb),.08); text-align:left; vertical-align:top; }
    th { position:sticky; top:0; background:var(--bg2); color:var(--accent); white-space:nowrap; }
    table.dpc th.sortable { cursor:pointer; user-select:none; position:relative; padding-right:18px; }
    table.dpc th.sortable::after { content: " ⇅"; font-size:11px; color:var(--muted); position:absolute;
        right:4px; top:50%; transform:translateY(-50%); }
    table.dpc th.sortable.asc::after { content: " ▲"; color: var(--accent); }
    table.dpc th.sortable.desc::after { content: " ▼"; color: var(--accent); }
    table.dpc th.sortable:hover { background: rgba(var(--t-accent-rgb),0.22); }
    tr.grp td { background:rgba(var(--t-green-rgb),.12); font-weight:700; color:var(--green); }
    .si { color:var(--green); font-weight:700; }
    .no { color:var(--muted); }
    .aic { font-variant-numeric: tabular-nums; }
    .back { display:inline-block; margin-bottom:14px; padding:9px 16px; border-radius:10px;
        border:1px solid var(--glass-border); background:var(--glass); color:var(--text);
        text-decoration:none; font-weight:600; }
    a { color: var(--accent); }
    ul { margin: 8px 0 0; padding-left: 22px; }
    li { margin-bottom: 7px; }
    .nota-pdf { font-size: 14px; color: var(--muted); margin-top: 18px; }
    .site-foot {
        margin: 26px auto 0; max-width: 1600px; padding: 14px 18px 22px;
        border-top: 1px solid var(--glass-border); color: var(--muted); font-size: 13.5px; line-height: 1.5;
    }
    .site-foot p { margin: 0 0 6px; }
    .site-foot a { color: var(--accent); }
</style>
</head>
<body>
<div class="wrap">
    <a class="back" href="index_list.html">&larr; Torna all'indice</a>
    <h1>Farmaci di diabete tipo 2 a Nota AIFA 100 in Convenzionata</h1>
    <div class="sub">Scheda 07 &mdash; {REGOLA} Documento: <b>FARMACI DIATETE TIPO 2 A NOTA AIFA 100</b>
        (pag. 2 &ldquo;in Convenzionata&rdquo;) &mdash; dati aggiornati al {GENERATED}.</div>

    <div class="box">
        <b>Regola operativa (dal 15 ottobre 2025)</b><br>
        {REGOLA}
        <br><br>
        <b>Eccezioni (dal documento ufficiale)</b>
        <ul>{ECCEZIONE}</ul>
        <br>
        <b>Fonti:</b>
        <a href="{PDF_NEL_SITO}" target="_blank" rel="noopener">documento ufficiale
        &ldquo;FARMACI DIATETE TIPO 2 A NOTA AIFA 100&rdquo; (PDF, 2 pagine)</a> &middot;
        <a href="{AIFA_NOTA100}" target="_blank" rel="noopener">AIFA &mdash; aggiornamento Nota 100</a> &middot;
        <a href="{REGIONE}" target="_blank" rel="noopener">Assessorato Salute &mdash; appropriatezza d&rsquo;uso dei farmaci</a>
        <br>
        <b>Nota:</b> restano fuori dal canale della convenzionata i medicinali a base di agonisti recettoriali
        del GLP-1 e di doppi agonisti GIP/GLP-1 (BYETTA, BYDUREON, LYXUMIA, OZEMPIC, RYBELSUS, TRULICITY,
        VICTOZA, XULTOPHY, SULIQUA, MOUNJARO): per questi la Scheda di Valutazione e Prescrizione resta
        obbligatoria e l&rsquo;erogazione avviene in DPC (vedi la tabella sotto).
    </div>

    <h2>Farmaci di diabete tipo 2 a Nota AIFA 100 in Convenzionata</h2>
    <div class="filters">
        <input type="text" id="q" placeholder="Cerca molecola, specialita', AIC...">
        <button id="reset">Reset</button>
        <span id="count"></span>
    </div>
    <div class="tablewrap">
        <table id="tbl" class="dpc">
            <thead><tr>
                <th class="sortable" data-col="0">Gruppo</th>
                <th class="sortable" data-col="1">Molecola</th>
                <th class="sortable" data-col="2">Nome commerciale</th>
                <th class="sortable" data-col="3">Confezioni (AIC)</th>
                <th class="sortable" data-col="4">Nelle liste DPC</th>
                <th class="sortable" data-col="5">Nota 100 obbligatoria</th>
                <th class="sortable" data-col="6">Eccezione (senza Nota 100)</th>
            </tr></thead>
            <tbody>{ROWS_CONV}</tbody>
        </table>
    </div>
    <div class="nota-pdf">Colonna &ldquo;Confezioni (AIC)&rdquo; e &ldquo;Nelle liste DPC&rdquo;: dati delle liste
        regionali DPC. &ldquo;Eccezione&rdquo;: dal documento ufficiale (Dapagliflozin / Empagliflozin).</div>

    <h2>Restano in DPC (Piano Terapeutico on-line)</h2>
    <div class="tablewrap">
        <table id="tbl2" class="dpc">
            <thead><tr>
                <th class="sortable" data-col="0">Gruppo</th>
                <th class="sortable" data-col="1">Molecola</th>
                <th class="sortable" data-col="2">Nome commerciale</th>
                <th class="sortable" data-col="3">Confezioni (AIC)</th>
                <th class="sortable" data-col="4">Nelle liste DPC</th>
                <th class="sortable" data-col="5">Nota 100 obbligatoria</th>
                <th class="sortable" data-col="6">Eccezione (senza Nota 100)</th>
            </tr></thead>
            <tbody>{ROWS_DPC}</tbody>
        </table>
    </div>
    <div class="box">
        <b>Regole operative per i farmaci che restano in DPC (dal documento ufficiale, pag. 1)</b>
        <ul>{REGOLE_DPC}</ul>
    </div>
</div>
<script>
(function () {
    "use strict";
    var tbl = document.getElementById("tbl");
    var tbl2 = document.getElementById("tbl2");
    var rows = Array.prototype.slice.call(tbl.tBodies[0].rows)
        .concat(Array.prototype.slice.call(tbl2.tBodies[0].rows));
    var idx = rows.map(function (tr) { return tr.textContent.toLowerCase(); });
    function apply() {
        var q = document.getElementById("q").value.trim().toLowerCase();
        var n = 0;
        rows.forEach(function (tr, i) {
            var ok = !q || idx[i].indexOf(q) >= 0;
            tr.style.display = ok ? "" : "none";
            if (ok) n++;
        });
        document.getElementById("count").textContent = n + " / " + rows.length + " righe";
    }
    document.getElementById("q").addEventListener("input", apply);
    document.getElementById("reset").addEventListener("click", function () {
        document.getElementById("q").value = ""; apply();
    });
    apply();
})();
</script>
<script>
(function () {
    "use strict";
    function setup(table) {
        if (!table) return;
        var tbody = table.tBodies[0];
        if (!tbody) return;
        var ths = table.querySelectorAll("thead th.sortable");
        function cellText(row, col) {
            if (!row || !row.cells || !row.cells[col]) return "";
            return (row.cells[col].textContent || "").trim();
        }
        function compare(a, b, col, dir) {
            var va = cellText(a, col);
            var vb = cellText(b, col);
            var na = parseFloat(va.replace(/\s/g, ""));
            var nb = parseFloat(vb.replace(/\s/g, ""));
            var cmp;
            if (!isNaN(na) && !isNaN(nb) && /^\d/.test(va) && /^\d/.test(vb)) {
                cmp = na - nb;
            } else {
                cmp = va.localeCompare(vb, "it", { sensitivity: "base", numeric: true });
            }
            return dir === "asc" ? cmp : -cmp;
        }
        ths.forEach(function (th) {
            th.addEventListener("click", function () {
                var col = parseInt(th.getAttribute("data-col"), 10);
                var dir = th.classList.contains("asc") ? "desc" : "asc";
                ths.forEach(function (t) { t.classList.remove("asc", "desc"); });
                th.classList.add(dir);
                var rs = Array.prototype.slice.call(tbody.rows);
                rs.sort(function (a, b) { return compare(a, b, col, dir); });
                rs.forEach(function (r) { tbody.appendChild(r); });
                apply();
            });
        });
    }
    [tbl, tbl2].forEach(setup);
})();
</script>

    <footer class="site-foot">
        <p><strong>Documento di base:</strong> Documento di Controllo dell'appropriatezza prescrittiva
            (DPC) di <strong>Federfarma Messina</strong> (edizione 2023, D.A. n. 278/2024 &ndash; G.U.R.S.
            n. 15 del 29/03/2024). <strong>Database e regole operative</strong> successivamente aggiornati e
            integrati con le disposizioni piu' recenti (determine AIFA 2025-2026, protocolli regionali,
            circolari di categoria, versioni aggiornate del DPC): ogni variazione e' marcata e ogni marcatura
            e' un link diretto al provvedimento.</p>
        <p><a href="disclaimer.html">Disclaimer legale e avvertenze</a> &middot; strumento informativo,
            uso gratuito &middot; verificare sempre con la propria professionalita' e sui canali ufficiali
            &middot; <a href="index.html">Ingresso</a></p>
    </footer>

<script src="consent.js"></script>
<script src="theme.js" defer></script>
</body>
</html>
"""


if __name__ == "__main__":
    main()
