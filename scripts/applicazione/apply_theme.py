#!/usr/bin/env python3
"""Applica il sistema di temi a tutte le pagine del sito DPC.

- sostituisce i colori letterali nelle <style> con rgb(var(--t-*-rgb)) / rgba(var(--t-*-rgb), a)
- inserisce <link rel="stylesheet" href="theme.css"> e lo script che applica il tema salvato
- inserisce <script src="theme.js" defer> prima della chiusura del body
Idempotente: se rilanciato non modifica nulla.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

HTML = ROOT / "html_estratto"
PAGES = ["index.html", "index_list.html", "farmaci_dpc.html", "distribuzione_diretta.html",
         "farmaci_no_dpc.html", "formalismi.html", "metilfenidato.html", "nota_99.html"]

# esadecimale -> variabile tema
HEX = {
    "#0f172a": "--t-bg-rgb", "#1e293b": "--t-bg2-rgb", "#020617": "--t-bgdeep-rgb",
    "#e2e8f0": "--t-text-rgb", "#f1f5f9": "--t-textlt-rgb", "#cbd5e1": "--t-text2-rgb",
    "#94a3b8": "--t-muted-rgb", "#64748b": "--t-muted2-rgb",
    "#38bdf8": "--t-accent-rgb", "#a78bfa": "--t-accent2-rgb",
    "#FF2800": "--t-red-rgb", "#7FFF00": "--t-green-rgb",
    "#34d399": "--t-green2-rgb", "#22c55e": "--t-green3-rgb", "#16a34a": "--t-green4-rgb",
    "#f472b6": "--t-pink-rgb", "#1e3a8a": "--t-deepblue-rgb", "#4c1d95": "--t-deepviolet-rgb",
    "#1d4ed8": "--t-blue2-rgb", "#147cd7": "--t-blue2-rgb",
    "#ffffff": "--t-white-rgb", "#fff": "--t-white-rgb",
}

# rgba(...) -> variabile tema (per canale)
RGBA = [
    (re.compile(r"rgba\(\s*255,\s*255,\s*255,\s*([0-9.]+)\)"), "--t-ov-rgb"),
    (re.compile(r"rgba\(\s*0,\s*0,\s*0,\s*([0-9.]+)\)"), "--t-ink-rgb"),
    (re.compile(r"rgba\(\s*56,\s*189,\s*248,\s*([0-9.]+)\)"), "--t-accent-rgb"),
    (re.compile(r"rgba\(\s*34,\s*197,\s*94,\s*([0-9.]+)\)"), "--t-green3-rgb"),
    (re.compile(r"rgba\(\s*15,\s*23,\s*42,\s*([0-9.]+)\)"), "--t-bg-rgb"),
    (re.compile(r"rgba\(\s*147,\s*197,\s*253,\s*([0-9.]+)\)"), "--t-sky-rgb"),
]


def tokenize(css: str) -> str:
    # colore su gradiente: il testo deve restare leggibile -> --t-onaccent
    css = re.sub(r"(background:\s*linear-gradient\([^;]*\);\s*color:\s*)#0f172a",
                 r"\1var(--t-onaccent)", css, flags=re.S)

    # riflessi/specularita' delle sfere: restano bianchi in ogni tema
    def fix_highlight(m):
        return re.sub(r"rgba\(\s*255,\s*255,\s*255,\s*([0-9.]+)\)",
                      r"rgba(var(--t-white-rgb),\1)", m.group(0))
    css = re.sub(r"radial-gradient\(\s*circle[^;]*?\)", fix_highlight, css, flags=re.S)

    for rx, var in RGBA:
        css = rx.sub(lambda m: f"rgba(var({var}),{m.group(1)})", css)
    for hx, var in HEX.items():
        css = re.sub(re.escape(hx) + r"\b", f"rgb(var({var}))", css, flags=re.I)
    return css


def main() -> int:
    changed = []
    for name in PAGES:
        p = HTML / name
        if not p.exists():
            print(f"[skip] {name} non trovato")
            continue
        t = p.read_text(encoding="utf-8")
        orig = t

        # 1) tokenizza la <style> inline
        def repl_style(m):
            return "<style>" + tokenize(m.group(1)) + "</style>"
        t = re.sub(r"<style>(.*?)</style>", repl_style, t, flags=re.S)

        # 2) link a theme.css subito prima della <style> inline
        if 'href="theme.css"' not in t:
            t = t.replace("<style>", '<link rel="stylesheet" href="theme.css">\n<style>', 1)

        # 3) script nel <head> che applica il tema prima del primo render
        head_script = ('<script>(function(){try{var t=localStorage.getItem("dpc-tema");'
                       'if(t){document.documentElement.setAttribute("data-theme",t);}}catch(e){}})();</script>')
        if 'localStorage.getItem("dpc-tema")' not in t:
            t = t.replace("</head>", head_script + "\n</head>", 1)

        # 4) script del selettore prima di </body>
        if 'src="theme.js"' not in t:
            t = t.replace("</body>", '<script src="theme.js" defer></script>\n</body>', 1)

        if t != orig:
            p.write_text(t, encoding="utf-8")
            changed.append(name)
        print(f"[{name}] {'aggiornato' if t != orig else 'gia' + chr(39) + ' conforme'}")
    print(f"\nPagine modificate: {len(changed)} -> {', '.join(changed) if changed else 'nessuna'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
