#!/usr/bin/env python3
"""Stub storico: la portabilità dei path è gestita da scripts/config.py.

Questo script esisteva per riscrivere path assoluti hardcoded. Dopo il refactor
Fase 1 (config.py) non è più necessario. Mantenuto come stub innocuo per
compatibilità con riferimenti/documentazione storica.

Uso: python3 scripts/rendi_portabili.py [--dry-run|--help]
"""
from __future__ import annotations

import sys


def main() -> int:
    if any(a in ("--help", "-h") for a in sys.argv[1:]):
        print("Uso: python3 scripts/rendi_portabili.py [--dry-run]")
        print("Stub: la portabilità è gestita da scripts/config.py")
        return 0
    dry = "--dry-run" in sys.argv[1:]
    print("rendi_portabili.py: stub Fase 1 - nessuna azione necessaria.")
    print("I path sono centralizzati in scripts/config.py.")
    if dry:
        print("[DRY-RUN] nessuna modifica.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
