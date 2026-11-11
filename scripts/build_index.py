#!/usr/bin/env python3
"""Genera index.html (Step 2) a partire da un template statico + dati JSON.

Il template non incorpora i dati: li carica con fetch() dai JSON in data/.
"""
import json, os

BASE = str(ROOT)

HTML = r"""<!DOCTYPE html>
<html lang="it">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="icon" href="data:,">
<title>Particolarismi dispensazione farmaci</title>
<style>
  :root {
    --bg: #f4f6f9;
    --panel: #ffffff;
    --ink: #1d2733;
    --muted: #5b6b7c;
    --line: #d8e0e8;
    --accent: #0b5d8f;
    --accent-soft: #e7f1f8;
    --warn: #8a5a00;
    --warn-soft: #fdf3d8;
    --ok: #1d6b3f;
    --ok-soft: #e4f4ea;
    --radius: 10px;
  }
  * { box-sizing: border-box; }
  html, body { margin: 0; padding: 0; }
  body {
    font-family: "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    background: var(--bg);
    color: var(--ink);
    line-height: 1.45;
  }
  header {
    background: linear-gradient(180deg, #0b5d8f 0%, #084a72 100%);
    color: #fff;
    padding: 2.2rem 1rem 2.6rem;
    text-align: center;
  }
  header h1 {
    margin: 0;
    font-size: clamp(1.6rem, 4vw, 2.8rem);
    font-weight: 700;
    letter-spacing: .2px;
  }
  header p { margin: .5rem 0 0; opacity: .9; font-size: .95rem; }
  main { max-width: 1400px; margin: 0 auto; padding: 1.5rem 1rem 3rem; }
  .cards {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 1rem;
    margin-bottom: 1.5rem;
  }
  .card {
    background: var(--panel);
    border: 1px solid var(--line);
    border-left: 5px solid var(--accent);
    border-radius: var(--radius);
    padding: 1.1rem 1.2rem;
    cursor: pointer;
    transition: transform .12s ease, box-shadow .12s ease, border-color .12s ease;
    text-align: left;
    font: inherit;
    color: inherit;
    display: block;
    width: 100%;
  }
  .card:hover { transform: translateY(-2px); box-shadow: 0 6px 18px rgba(16,40,64,.10); }
  .card[aria-selected="true"] {
    border-color: var(--accent);
    border-left-color: var(--accent);
    background: var(--accent-soft);
    box-shadow: 0 6px 18px rgba(11,93,143,.16);
  }
  .card h2 { margin: 0 0 .35rem; font-size: 1.1rem; }
  .card .conteggio { font-size: 1.9rem; font-weight: 700; color: var(--accent); line-height: 1.1; }
  .card .pagine { margin: .35rem 0 0; color: var(--muted); font-size: .85rem; }
  .card .stato { margin: .45rem 0 0; font-size: .8rem; color: var(--muted); }
  .toolbar {
    display: flex;
    flex-wrap: wrap;
    gap: .6rem;
    align-items: center;
    margin: 0 0 .9rem;
  }
  .toolbar input[type="search"] {
    flex: 1 1 260px;
    padding: .5rem .7rem;
    border: 1px solid var(--line);
    border-radius: 8px;
    font: inherit;
    background: var(--panel);
  }
  .toolbar .info { color: var(--muted); font-size: .88rem; }
  .panel {
    background: var(--panel);
    border: 1px solid var(--line);
    border-radius: var(--radius);
    overflow: auto;
    max-height: 72vh;
  }
  table { border-collapse: collapse; width: 100%; font-size: .9rem; }
  thead th {
    position: sticky;
    top: 0;
    z-index: 2;
    background: #eef3f7;
    border-bottom: 2px solid var(--line);
    padding: .55rem .6rem;
    text-align: left;
    cursor: pointer;
    white-space: nowrap;
    user-select: none;
  }
  thead th .arrow { color: var(--accent); font-size: .78rem; margin-left: .25rem; }
  thead th.nosort { cursor: default; }
  tbody td { padding: .45rem .6rem; border-bottom: 1px solid #edf1f5; vertical-align: top; }
  tbody tr:nth-child(even) { background: #fafcfd; }
  tbody tr:hover { background: var(--accent-soft); }
  td.minsan { white-space: nowrap; font-variant-numeric: tabular-nums; }
  td.desc { min-width: 260px; }
  td.pa { min-width: 220px; }
  td.note { min-width: 170px; }
  td.atc { white-space: nowrap; }
  .badge {
    display: inline-block;
    margin-left: .35rem;
    padding: .05rem .4rem;
    border-radius: 999px;
    font-size: .72rem;
    font-weight: 600;
    white-space: nowrap;
    cursor: help;
  }
  .badge.agg { background: var(--ok-soft); color: var(--ok); border: 1px solid #b9dfc9; }
  .badge.dv  { background: var(--warn-soft); color: var(--warn); border: 1px solid #ecd9a4; }
  .empty { padding: 2rem; text-align: center; color: var(--muted); }
  .errore {
    background: #fdecec;
    border: 1px solid #eab7b7;
    color: #8a1f1f;
    border-radius: var(--radius);
    padding: 1rem 1.2rem;
    margin-bottom: 1rem;
  }
  .errore code {
    display: block;
    margin-top: .5rem;
    padding: .5rem .7rem;
    background: #fff;
    border-radius: 6px;
    font-family: "SFMono-Regular", Consolas, monospace;
    white-space: pre-wrap;
  }
  footer {
    text-align: center;
    color: var(--muted);
    font-size: .85rem;
    padding: 1.5rem 1rem 2.5rem;
  }
  @media (max-width: 720px) {
    .panel { max-height: none; }
    td.desc, td.pa, td.note { min-width: 160px; }
  }
</style>
</head>
<body>
<header>
  <h1>Particolarismi dispensazione farmaci</h1>
  <p>Elenco DPC &middot; Distribuzione diretta ASP &middot; Nota 99 BPCO</p>
</header>

<main>
  <div id="errore" class="errore" hidden></div>

  <div class="cards" id="cards"></div>

  <div class="toolbar">
    <input type="search" id="filtro" placeholder="Filtra per minsan, descrizione, principio attivo o nota&hellip;" aria-label="Filtra righe">
    <span class="info" id="info"></span>
  </div>

  <div class="panel" id="panel"></div>
</main>

<footer>
  Dati tratti da Federfarma Messina, agg. 17/07/2023, con aggiornamenti verificati; fa fede la fonte ufficiale.
</footer>

<script>
"use strict";

const ELENCHI = [
  { id: "dpc",    titolo: "DPC",                    file: "data/dpc.json",    pagine: "pp. 44-58" },
  { id: "diretta",titolo: "Distribuzione diretta ASP", file: "data/diretta.json",pagine: "pp. 59-63" },
  { id: "nota99", titolo: "Nota 99 BPCO",            file: "data/nota99.json", pagine: "pp. 66-67" }
];

const stato = {
  elenco: null,       // id elenco attivo
  dati: {},           // id -> array righe
  ordine: { campo: null, dir: 1 },
  filtro: ""
};

const $ = (sel) => document.querySelector(sel);

function fmtData(d) {
  if (!d) return "";
  const [y, m, g] = d.split("-");
  if (!y || !m) return d;
  return `${g}/${m}/${y.slice(2)}`;
}

function badgeAggiornato(r) {
  if (!r.aggiornato) return "";
  const a = r.aggiornato;
  const tip = `Variazione: ${a.nota_breve || ""}\nData variazione: ${a.data || "n.d."}\nFonte: ${a.fonte || "n.d."}`;
  return `<span class="badge agg" title="${escapeHtml(tip)}">agg. ${escapeHtml(fmtData(a.data))}</span>`;
}

function badgeDaVerificare(r) {
  if (!r.da_verificare) return "";
  const motivo = typeof r.da_verificare === "string" ? r.da_verificare : "da verificare";
  return `<span class="badge dv" title="${escapeHtml(motivo)}">da verificare</span>`;
}

const ESC_MAP = {
  "&": String.fromCharCode(38),
  "<": String.fromCharCode(60),
  ">": String.fromCharCode(62),
  "\"": String.fromCharCode(34),
  "'": String.fromCharCode(39)
};
function escapeHtml(s) {
  return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) { return ESC_MAP[c]; });
}

function confronta(a, b) {
  return String(a == null ? "" : a).localeCompare(String(b == null ? "" : b), "it", { numeric: true });
}

function righeFiltrate() {
  const righe = stato.dati[stato.elenco] || [];
  const f = stato.filtro.trim().toLowerCase();
  if (!f) return righe;
  return righe.filter(r => [r.minsan, r.descrizione, r.principio_attivo, r.note, r.atc]
    .filter(Boolean).join(" ").toLowerCase().includes(f));
}

function ordinaRighe(righe) {
  const { campo, dir } = stato.ordine;
  if (!campo) return righe;
  const copia = righe.slice();
  copia.sort((x, y) => confronta(x[campo], y[campo]) * dir);
  return copia;
}

function intestazioni(elenco) {
  const cols = [
    { k: "minsan", t: "Minsan" },
    { k: "descrizione", t: "Descrizione" },
    { k: "principio_attivo", t: "Principio Attivo" }
  ];
  if (elenco === "diretta") cols.splice(3, 0, { k: "atc", t: "ATC" });
  cols.push({ k: "note", t: "Note" });
  return cols;
}

function renderTabelle() {
  const panel = $("#panel");
  const elenco = stato.elenco;
  if (!elenco) { panel.innerHTML = '<div class="empty">Seleziona una card per caricare la tabella.</div>'; return; }
  const righe = ordinaRighe(righeFiltrate());
  const cols = intestazioni(elenco);
  const thead = cols.map(c => {
    const attiva = stato.ordine.campo === c.k;
    const arrow = attiva ? `<span class="arrow">${stato.ordine.dir === 1 ? "▲" : "▼"}</span>` : "";
    return `<th data-campo="${c.k}" title="Clic per ordinare">${c.t}${arrow}</th>`;
  }).join("");

  const body = righe.map(r => {
    const tds = cols.map(c => {
      let v = escapeHtml(r[c.k] || "");
      if (c.k === "note") v += badgeAggiornato(r) + badgeDaVerificare(r);
      return `<td class="${c.k === "principio_attivo" ? "pa" : c.k === "descrizione" ? "desc" : c.k}">${v}</td>`;
    }).join("");
    return `<tr>${tds}</tr>`;
  }).join("");

  panel.innerHTML = `<table><thead><tr>${thead}</tr></thead><tbody>${body}</tbody></table>`;

  panel.querySelectorAll("thead th").forEach(th => {
    th.addEventListener("click", () => {
      const campo = th.dataset.campo;
      if (stato.ordine.campo === campo) {
        stato.ordine.dir = -stato.ordine.dir;
      } else {
        stato.ordine.campo = campo;
        stato.ordine.dir = 1;
      }
      renderTabelle();
    });
  });

  const tot = (stato.dati[elenco] || []).length;
  $("#info").textContent = `${righe.length} righe mostrate su ${tot}` +
    (stato.filtro ? ` (filtro: "${stato.filtro}")` : "") +
    (stato.ordine.campo ? ` · ordinato per ${stato.ordine.campo} ${stato.ordine.dir === 1 ? "asc" : "desc"}` : "");
}

function renderCard() {
  const wrap = $("#cards");
  wrap.innerHTML = "";
  ELENCHI.forEach(e => {
    const righe = stato.dati[e.id];
    const n = righe ? righe.length : null;
    const b = document.createElement("button");
    b.className = "card";
    b.type = "button";
    b.setAttribute("aria-selected", String(stato.elenco === e.id));
    b.innerHTML = `<h2>${escapeHtml(e.titolo)}</h2>
      <div class="conteggio">${n === null ? "—" : n.toLocaleString("it-IT")}</div>
      <div class="pagine">${escapeHtml(e.pagine)}</div>
      <div class="stato">${righe ? "caricato" : "non caricato"}</div>`;
    b.addEventListener("click", () => {
      stato.elenco = e.id;
      stato.ordine = { campo: null, dir: 1 };
      renderCard();
      renderTabelle();
    });
    wrap.appendChild(b);
  });
}

function mostraErrore(msg, extra) {
  const box = $("#errore");
  box.hidden = false;
  box.innerHTML = `<strong>${escapeHtml(msg)}</strong>${extra || ""}`;
}

async function carica(id) {
  const e = ELENCHI.find(x => x.id === id);
  try {
    const risp = await fetch(e.file, { cache: "no-store" });
    if (!risp.ok) throw new Error(`HTTP ${risp.status}`);
    const dati = await risp.json();
    if (!Array.isArray(dati)) throw new Error("il JSON non è un array");
    stato.dati[id] = dati;
    return true;
  } catch (err) {
    const cartella = e.file.split("/").slice(0, -1).join("/");
    mostraErrore(
      `Impossibile caricare ${e.file}: ${err.message}.`,
      "<code>cd " + cartella + " && ./serve.sh\n# oppure: python3 -m http.server 8080</code>"
    );
    return false;
  }
}

async function init() {
  const risultati = await Promise.all(ELENCHI.map(e => carica(e.id)));
  if (!risultati.every(Boolean)) {
    $("#panel").innerHTML = '<div class="empty">Dati non caricati: consulta il messaggio qui sopra.</div>';
  }
  renderCard();
  if (risultati.every(Boolean)) {
    stato.elenco = "dpc";
    renderCard();
    renderTabelle();
  } else {
    renderTabelle();
  }
  $("#filtro").addEventListener("input", (ev) => {
    stato.filtro = ev.target.value;
    renderTabelle();
  });
}

document.addEventListener("DOMContentLoaded", init);
</script>
</body>
</html>
"""

SERVE = r"""#!/usr/bin/env bash
# Avvia un server HTTP locale per index.html (fetch su file:// e' bloccato dai browser).
set -euo pipefail
cd "$(dirname "$0")"
PORT="${1:-8080}"
echo "Particolarismi dispensazione farmaci"
echo "Apri: http://localhost:${PORT}/index.html"
echo "Ctrl+C per arrestare."
exec python3 -m http.server "${PORT}" --bind 127.0.0.1
"""

def main():
    with open(os.path.join(BASE, "index.html"), "w", encoding="utf-8") as f:
        f.write(HTML)
    p = os.path.join(BASE, "serve.sh")
    with open(p, "w", encoding="utf-8") as f:
        f.write(SERVE)
    os.chmod(p, 0o755)
    print("scritti index.html e serve.sh")

if __name__ == "__main__":
    main()
