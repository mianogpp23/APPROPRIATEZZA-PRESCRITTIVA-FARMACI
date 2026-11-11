#!/usr/bin/env python3
"""Costruisce l'indice OCR delle pagine dei PDF locali (docs/), per il deep linking.

I PDF pubblicati nel sito (Note 74, 97, 99, modifica PT Nota 39) sono scansioni senza livello
testo: per linkare la pagina esatta in cui compare un farmaco serve l'OCR. L'indice (una volta
creato) e' riusato dal sync per generare i link 'documento.pdf#page=N'.

Uso: python3 ocr_indice_pagine.py [--forza] [--solo nome.pdf]
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DOCS = ROOT / "html_estratto" / "docs"
INDICE = ROOT / "data" / "pdf_pagine_ocr.json"


def normalizza(s: str) -> str:
    return re.sub(r"[^A-Z0-9]", "", (s or "").upper())


def testo_pdf(pdf: Path) -> dict[int, str]:
    """Testo per pagina: livello testo se presente, altrimenti OCR con tesseract."""
    out: subprocess.CompletedProcess = subprocess.run(
        ["pdftotext", "-layout", str(pdf), "-"], capture_output=True, timeout=300)
    pagine = out.stdout.decode("utf-8", errors="replace").split("\f")
    if sum(len(p.strip()) for p in pagine) > 200:
        return {i + 1: p for i, p in enumerate(pagine) if p.strip()}
    with tempfile.TemporaryDirectory(prefix="ocr_idx_") as td:
        tmp = Path(td)
        subprocess.run(["pdftoppm", "-r", "200", "-png", str(pdf), str(tmp / "pg")],
                       capture_output=True, timeout=900)
        res: dict[int, str] = {}
        for img in sorted(tmp.glob("pg-*.png")):
            n = int(img.stem.split("-")[-1])
            o = subprocess.run(["tesseract", str(img), "stdout", "-l", "ita", "--psm", "6"],
                               capture_output=True, timeout=600)
            res[n] = o.stdout.decode("utf-8", errors="replace")
        return res


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--forza", action="store_true")
    ap.add_argument("--solo", default="")
    args = ap.parse_args()

    indice: dict[str, dict[str, str]] = {}
    if INDICE.exists() and not args.forza:
        indice = json.loads(INDICE.read_text(encoding="utf-8"))
    for pdf in sorted(DOCS.glob("*.pdf")):
        if args.solo and args.solo not in pdf.name:
            continue
        if pdf.name in indice and not args.forza:
            print(f"  {pdf.name}: gia' indicizzato ({len(indice[pdf.name])} pagine)")
            continue
        try:
            pagine = testo_pdf(pdf)
        except Exception as e:
            print(f"  {pdf.name}: ERRORE {e}")
            continue
        indice[pdf.name] = {str(k): normalizza(v) for k, v in pagine.items()}
        print(f"  {pdf.name}: {len(pagine)} pagine indicizzate")
        INDICE.parent.mkdir(parents=True, exist_ok=True)
        INDICE.write_text(json.dumps(indice, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"indice: {INDICE}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
