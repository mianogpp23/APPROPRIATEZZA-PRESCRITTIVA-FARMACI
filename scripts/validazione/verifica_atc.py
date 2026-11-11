#!/usr/bin/env python3
"""Verifica dei 3 ATC non standard: il testo è troncato nel PDF o nell'estrazione?"""
from pathlib import Path
import pdfplumber, collections, re

PDF = str(Path(__file__).resolve().parents[2] / "docs" / "dpc" / "Controllo-appropriatezza-prescrittiv1a.pdf")
TARGETS = [(61, 530.5), (62, 274.9), (63, 58.4)]

def hbands(pg):
    ys = sorted({round(e["top"], 1) for e in pg.edges if e["orientation"] == "h"})
    g = []
    for y in ys:
        if g and y - g[-1][-1] <= 1.2: g[-1].append(y)
        else: g.append([y])
    c = [sum(x) / len(x) for x in g]
    return [(c[i], c[i+1]) for i in range(len(c)-1)]

with pdfplumber.open(PDF) as pdf:
    for pno, top in TARGETS:
        pg = pdf.pages[pno-1]
        for b0, b1 in hbands(pg):
            if not (b0 - 0.6 <= top < b1 - 0.6): continue
            ch = [c for c in pg.chars if b0 - 0.6 <= c["top"] < b1 - 0.6]
            print(f"--- p{pno} banda {b0:.1f}-{b1:.1f} ({len(ch)} char)")
            byline = collections.defaultdict(list)
            for c in ch: byline[round(c["top"],1)].append(c)
            for t in sorted(byline):
                parts = []
                for c in sorted(byline[t], key=lambda c: c["x0"]):
                    parts.append(f"{c['text']!r}@{c['x0']:.1f}-{c['x1']:.1f}({c['size']:.1f})")
                print(f"   top={t}: " + " ".join(parts))
            # testo grezzo per colonna
            def txt(lo, hi):
                sel = [c for c in ch if lo <= c["x0"] < hi]
                sel.sort(key=lambda c: (round(c["top"],1), c["x0"]))
                return "".join(c["text"] for c in sel)
            print(f"   ATC bucket [199,236): {txt(199,236)!r}")
            print(f"   PA  bucket [236,526): {txt(236,526)!r}")
            print()
