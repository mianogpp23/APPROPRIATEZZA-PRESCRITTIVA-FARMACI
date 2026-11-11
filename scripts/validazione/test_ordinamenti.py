#!/usr/bin/env python3
"""Test di regressione degli ordinamenti delle tabelle del sito DPC.

Verifica in un browser reale (chromium headless) che ogni intestazione ordinabile riordini
effettivamente le righe e che il risultato sia ordinato. La pagina di test viene copiata
temporaneamente nella cartella del sito (serve la stessa origine per l'iframe), eseguita e rimossa.

Uso: python3 test_ordinamenti.py [--url http://192.168.1.229:8081]
"""
from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

SITO = ROOT / "html_estratto"
TEST = """<!DOCTYPE html>
<html lang="it"><head><meta charset="UTF-8"><title>test ordinamenti</title></head>
<body><pre id="out">in corso...</pre><iframe id="f" style="width:1400px;height:700px"></iframe>
<script>
(function () {   // il portale richiede l'accettazione: il test la registra per poter leggere le pagine
    try { localStorage.setItem("dpc-consenso", "1"); } catch (e) { /* storage non disponibile */ }
})();
(function () {
    var out = document.getElementById("out"), lines = [];
    function log(s) { lines.push(s); out.textContent = lines.join("\\n"); }
    var PAGINE = ["farmaci_dpc.html", "distribuzione_diretta.html", "nota_99.html",
                  "metilfenidato.html", "dpc_convenzionata.html"];
    var f = document.getElementById("f"), i = 0;
    function seq(tb, col) {
        var a = [];
        for (var k = 0; k < tb.rows.length; k++) {
            if (tb.rows[k].parentNode.tagName === "THEAD") continue;
            if (tb.rows[k].classList.contains("note")) continue;
            var c = tb.rows[k].cells[col];
            if (!c) continue;
            var t = c.textContent.trim();
            if (t) a.push(t);
        }
        return a;
    }
    function isSorted(a) {
        for (var k = 1; k < a.length; k++) {
            if (a[k].localeCompare(a[k - 1], "it", { sensitivity: "base", numeric: true }) < 0) return false;
        }
        return true;
    }
    function provaPagina() {
        if (i >= PAGINE.length) { log("FINE"); return; }
        var pagina = PAGINE[i++];
        f.src = pagina;
        f.addEventListener("load", function () {
            setTimeout(function () {
                try {
                    var d = f.contentDocument, res = [];
                    d.querySelectorAll("table.dpc").forEach(function (tb, ti) {
                        tb.querySelectorAll("thead th.sortable").forEach(function (th) {
                            var col = parseInt(th.getAttribute("data-col"), 10);
                            var prima = seq(tb, col).join("");
                            th.click();
                            var dopo = seq(tb, col);
                            var ok = isSorted(dopo);
                            res.push("tab" + (ti + 1) + " | " + (th.textContent.trim() || "col" + col) + " | " +
                                     (prima === dopo.join("") ? "identico" : "riordinato") + " | " +
                                     (ok ? "ORDINATO" : "NON ORDINATO"));
                            th.click();
                        });
                    });
                    log(pagina);
                    res.forEach(function (r) { log("  " + r); });
                    provaPagina();
                } catch (e) { log(pagina + ": ECCEZIONE " + e.message); provaPagina(); }
            }, 1200);
        }, { once: true });
    }
    provaPagina();
})();
</script></body></html>
"""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default="http://192.168.1.229:8081")
    args = ap.parse_args()

    tmp = SITO / "_test_ordinamenti.html"
    tmp.write_text(TEST, encoding="utf-8")
    try:
        out = subprocess.run(
            ["chromium-browser", "--headless", "--disable-gpu", "--no-sandbox",
             "--virtual-time-budget=60000", "--dump-dom", f"{args.url}/_test_ordinamenti.html"],
            capture_output=True, text=True, timeout=300).stdout
    finally:
        tmp.unlink(missing_ok=True)

    m = re.search(r'<pre id="out">(.*?)</pre>', out, re.S)
    testo = re.sub(r"<[^>]+>", "", m.group(1)) if m else ""
    print(testo)
    ok = testo.count("ORDINATO |") + testo.count("| ORDINATO")
    ko = testo.count("NON ORDINATO")
    print(f"\ncolonne verificate: {ok + ko} | ordinate: {ok} | NON ordinate: {ko}")
    return 0 if ko == 0 and ok > 0 else 1


if __name__ == "__main__":
    sys.exit(main())
