#!/usr/bin/env python3
"""Test del parsing dei link locali con query string e frammento."""
import importlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def target_without_fragment(value: str) -> str:
    """Chiama la funzione reale del validatore senza import statico."""
    module = importlib.import_module("scripts.validazione.verifica_link")
    return module.target_without_fragment(value)


def test_link_locale_con_query_string():
    """Il validatore deve cercare il file, non un nome con '?citta='."""
    assert target_without_fragment("locandina_turni.html?citta=vittoria") == "locandina_turni.html"


def test_link_locale_con_query_e_frammento():
    """Query e frammento non devono finire nel percorso del file locale."""
    assert (
        target_without_fragment("locandina_turni.html?citta=acate#stampa")
        == "locandina_turni.html"
    )


def test_link_pdf_locale_con_frammento_pagina():
    """Il frammento #page=N resta separato dal PDF locale."""
    assert target_without_fragment("docs/nota-99.pdf#page=7") == "docs/nota-99.pdf"


def test_link_esterno_mantiene_la_query():
    """La query di un URL esterno è parte della richiesta e non va rimossa."""
    assert (
        target_without_fragment("https://example.org/doc.pdf?token=a%3Db#page=2")
        == "https://example.org/doc.pdf?token=a%3Db"
    )
