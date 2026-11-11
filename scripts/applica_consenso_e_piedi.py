#!/usr/bin/env python3
"""Applica alle pagine statiche del sito: guardia di accesso e piede di trasparenza.

- `consent.js`: senza accettazione le pagine interne reindirizzano alla splash (index.html);
  la splash e il disclaimer restano sempre accessibili.
- piede: riferimento al documento di base (Federfarma Messina 2023), all'aggiornamento del database
  con le disposizioni piu' recenti e al disclaimer legale.
Idempotente: se i blocchi sono gia' presenti non viene duplicato nulla.

Uso: python3 applica_consenso_e_piedi.py [--dry-run]
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

HTML = ROOT / "html_estratto"

PAGINE = [
    "index_list.html", "home.html", "farmaci_dpc.html", "distribuzione_diretta.html",
    "nota_99.html", "metilfenidato.html", "farmaci_no_dpc.html", "formalismi.html",
]

CONSENSO = '    <script src="consent.js"></script>\n'
PIEDE = """
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
"""

CSS = """
    .site-foot {
        margin: 26px auto 0; max-width: 1500px; padding: 14px 18px 22px;
        border-top: 1px solid var(--glass-border); color: var(--muted); font-size: 13.5px; line-height: 1.5;
    }
    .site-foot p { margin: 0 0 6px; }
    .site-foot a { color: var(--accent); }
"""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    modificati = 0
    for nome in PAGINE:
        p = HTML / nome
        if not p.exists():
            print(f"  {nome}: non trovata")
            continue
        s = p.read_text(encoding="utf-8")
        orig = s
        # guardia di accesso
        if "consent.js" not in s:
            s = s.replace("</head>", CONSENSO + "</head>", 1)
        # stile del piede
        if ".site-foot {" not in s:
            s = s.replace("</style>", CSS + "</style>", 1)
        # piede di trasparenza
        if 'class="site-foot"' not in s:
            s = s.replace("</body>", PIEDE + "\n</body>", 1)
        if s != orig:
            modificati += 1
            print(f"  {nome}: guardia + piede applicati")
            if not args.dry_run:
                p.write_text(s, encoding="utf-8")
        else:
            print(f"  {nome}: gia' conforme")
    print(f"pagine modificate: {modificati}" + ("  [DRY-RUN]" if args.dry_run else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
