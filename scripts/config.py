#!/usr/bin/env python3
"""Configurazione centralizzata dei percorsi del progetto DPC.

Calcola i path dal layout reale del repository, supportando sia il layout
"working dir" originale (html_estratto/, data/, docs/dpc/...) sia il layout
del clone pubblicato (HTML a root, docs/ piatto, dati_farmaci.json a root).

Uso dagli script:
    import sys
    from pathlib import Path
    _ROOT = Path(__file__).resolve().parents[1]  # scripts/ -> root; .parents[2] per sottocartelle
    if str(_ROOT) not in sys.path:
        sys.path.insert(0, str(_ROOT))
    from scripts.config import ROOT, HTML, JSON, DOCS, BACKUP
"""

from __future__ import annotations

from pathlib import Path

# Root del progetto = parent della cartella scripts/
ROOT = Path(__file__).resolve().parents[1]

# HTML: layout originale usa html_estratto/, il clone pubblicato tiene gli HTML a root.
_HTML_DIR = ROOT / "html_estratto"
HTML = _HTML_DIR if _HTML_DIR.is_dir() else ROOT

# JSON: fonte di verità dati. Preferisce data/dati_farmaci.json, poi root.
_JSON_DATA = ROOT / "data" / "dati_farmaci.json"
_JSON_ROOT = ROOT / "dati_farmaci.json"
if _JSON_DATA.is_file():
    JSON = _JSON_DATA
elif _JSON_ROOT.is_file():
    JSON = _JSON_ROOT
else:
    # default canonico per messaggi di errore chiari; non inventa dati
    JSON = _JSON_DATA

# Directory dati (parent del JSON canonico)
DATA_DIR = JSON.parent

# Documenti (PDF/fonti)
DOCS = ROOT / "docs"

# Backup
BACKUP = ROOT / "output" / "backup"

# PDF noti (risolti se presenti; None se assenti)
def _find_pdf(*candidates: str) -> Path | None:
    for c in candidates:
        p = ROOT / c
        if p.is_file():
            return p
    return None

PDF_DPC = _find_pdf(
    "docs/dpc-controllo-appropriatezza.pdf",
    "docs/dpc/Controllo-appropriatezza-prescrittiva.pdf",
    "docs/dpc/Controllo-appropriatezza-prescrittiv1a.pdf",
)
PDF_NOTA100 = _find_pdf(
    "docs/diabete-tipo2-nota-100.pdf",
    "docs/dpc/FARMACI-DIATETE-TIPO-2-A-NOTA-AIFA-100.pdf",
)
PDF_NOTA74 = _find_pdf("docs/nota-74.pdf", "docs/nota74-22-maggio-2024.pdf")
PDF_NOTA97 = _find_pdf("docs/nota-97.pdf", "docs/nota97-11-novembre-2025.pdf")
PDF_NOTA99 = _find_pdf("docs/nota-99.pdf", "docs/nota99-27-novembre-2025.pdf")
PDF_NOTA39 = _find_pdf("docs/modifica-pt-nota-39.pdf", "docs/modifica-piano-terapeutico-nota-39.pdf")


def ensure_backup_dir() -> Path:
    BACKUP.mkdir(parents=True, exist_ok=True)
    return BACKUP


def require_json() -> Path:
    if not JSON.is_file():
        raise FileNotFoundError(
            f"dati_farmaci.json non trovato. Cercato: {_JSON_DATA} e {_JSON_ROOT}. "
            "Nessun dato inventato: ripristinare il file dalla fonte di verità."
        )
    return JSON
