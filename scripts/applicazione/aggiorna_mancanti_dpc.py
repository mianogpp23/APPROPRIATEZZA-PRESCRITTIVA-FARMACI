#!/usr/bin/env python3
"""Inserisce nelle liste i farmaci presenti nel DPC regionale ma assenti dalle liste.

I dati sono stati trascritti leggendo direttamente il PDF del DPC (render a 200 dpi delle righe),
perche' per queste righe l'estrattore geometrico non risolve le colonne (descrizione lunga che
sposta il principio attivo oltre il boundary x fisso).

Uso:  python3 aggiorna_mancanti_dpc.py [--dry-run|--apply] [--pubblica-dpc]
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
JSON_PATH = ROOT / "data" / "dati_farmaci.json"
PDF_DPC = ROOT / "docs" / "dpc" / "Controllo-appropriatezza-prescrittiva.pdf"
DOCS = ROOT / "html_estratto" / "docs"
BACKUP = ROOT / "output" / "backup"
DATA = "10/11/2026"
FONTE = "DPC Regione Siciliana - Controllo appropriatezza prescrittiva (aggiornato)"
LINK_DPC = "docs/dpc-controllo-appropriatezza.pdf"

# (codice, descrizione, principio_attivo, nota, pagina)  - verificati sul PDF renders
FARMACI_DPC = [
    ("044407043", "ARIPIPRAZOLO SAND*28CPR 5MG", "ARIPIPRAZOLO", "", 42),
    ("046284055", "CINACALCET EG*28CPR RIV 60MG", "CINACALCET CLORIDRATO", "PT online", 43),
    ("043152204", "CORBILTA*100CPR125+31,25+200MG", "LEVODOPA/CARBIDOPA/ENTACAPONE", "PT", 44),
    ("027066137", "ENANTONE*IM SC SIR11,25MG/MLRP", "LEUPORELINA ACETATO",
     "|max 1 ogni 80 gg. PT online - Nota 51 - CAP", 45),
    ("027276031", "FRAGMIN*SC 6SIR 2500UI 0,2ML", "DALTEPARINA SODICA", "Chirurgia maggiore", 46),
    ("044905293", "IVABRADINA MY*56CPR RIV 5MG", "IVABRADINA OSSALATO", "max 2 m.- 3 patol", 47),
    ("042241024", "MEMANTINA AURO*28CPR RIV 20MG", "MEMANTINA CLORIDRATO",
     "PT online - Nota 85|max 2 m.", 48),
    ("040261036", "OLANZAPINA ACT*28CPR RIV 2,5MG", "OLANZAPINA", "", 49),
    ("045597402", "PRASUGREL TEVA*28CPR RIV 10MG", "PRASUGREL BROMIDRATO",
     "PT online max 2 conf mese", 51),
    ("040510152", "QUETIAPINA TE*30CPR RIV 25MG", "QUETIAPINA FUMARATO", "", 52),
    ("040036042", "SENEFOR*30CPR 0,7MG", "PRAMIPEXOLO DICLORIDRATO MONOIDRATO", "max 2 m.- 3 patol", 54),
    ("041141021", "TROBALT*84CPR RIV 50MG", "RETIGABINA", "PT", 55),
]

# (codice, descrizione, atc, principio_attivo, nota, pagina)
DISTRIBUZIONE_DIRETTA = [
    ("034525042", "FERRIPROX*FL 50CPR RIV 1000MG", "V03AC02", "DEFERIPRONE", "", 58),
    ("034525028", "FERRIPROX*OS FL 250ML 100MG/ML", "V03AC02", "DEFERIPRONE", "", 58),
    ("029610108", "METADONE CLOR.MOL*OS 5MG/ML10M", "N07BC02", "METADONE CLORIDRATO", "", 59),
    ("029610110", "METADONE CLOR.MOL*OS 5MG/ML20M", "N07BC02", "METADONE CLORIDRATO", "", 59),
    ("032887010", "RILUTEK*56CPR RIV 50MG", "N07XX02", "RILUZOLO", "", 60),
    ("040541070", "RILUZOLO ACT*56CPR RIV 50MG", "N07XX02", "RILUZOLO", "", 60),
    ("035609041", "TRACLEER*56CPR RIV 125MG", "C02KX01", "BOSENTAN MONOIDRATO", "", 61),
    ("035609027", "TRACLEER*56CPR RIV 62,5MG", "C02KX01", "BOSENTAN MONOIDRATO", "", 61),
]


def variazione(pagina: int) -> dict:
    return {
        "data": DATA,
        "fonte": f"{FONTE}, pag. {pagina}",
        "url_o_percorso": LINK_DPC,
        "testo_breve": "Farmaco presente nel DPC regionale ma assente dalle liste",
        "stato": "inserimento",
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    grp = ap.add_mutually_exclusive_group()
    grp.add_argument("--dry-run", action="store_true")
    grp.add_argument("--apply", action="store_true")
    ap.add_argument("--pubblica-dpc", action="store_true",
                    help="copia il PDF del DPC in html_estratto/docs/ per il link cliccabile")
    args = ap.parse_args()
    apply = args.apply and not args.dry_run

    data = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    esistenti = {str(r.get("minsan") or r.get("aic") or "") for r in data}

    nuovi = []
    for codice, desc, pa, nota, pag in FARMACI_DPC:
        if codice in esistenti:
            continue
        nuovi.append({
            "minsan": codice, "descrizione": desc, "principio_attivo": pa,
            "note": nota, "elenco": "farmaci_dpc", "variazioni": [variazione(pag)],
        })
    for codice, desc, atc, pa, nota, pag in DISTRIBUZIONE_DIRETTA:
        if codice in esistenti:
            continue
        nuovi.append({
            "aic": codice, "descrizione": desc, "atc": atc, "principio_attivo": pa,
            "note": nota, "elenco": "distribuzione_diretta", "variazioni": [variazione(pag)],
        })

    print(f"record attuali: {len(data)} | da inserire: {len(nuovi)}")
    for r in nuovi:
        print(f"  + {r.get('minsan') or r.get('aic')} [{r['elenco']}] {r['descrizione'][:44]} "
              f"| PA={r['principio_attivo'][:28]} | nota={r['note'][:34]}")

    if not apply:
        print("\n[DRY-RUN] nessuna scrittura eseguita (usare --apply per applicare)")
        return 0

    BACKUP.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    bak = BACKUP / f"dati_farmaci.json.{ts}.bak"
    shutil.copy2(JSON_PATH, bak)
    print(f"\n[backup] {bak}")

    # inserimento a fine gruppo elenco
    for rec in nuovi:
        idx = max((i for i, r in enumerate(data) if r.get("elenco") == rec["elenco"]), default=len(data) - 1)
        data.insert(idx + 1, rec)

    JSON_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"[scritto] {JSON_PATH} ({len(data)} record)")

    copia = ROOT / "html_estratto" / "dati_farmaci.json"
    shutil.copy2(JSON_PATH, copia)
    print(f"[copia] {copia}")

    if args.pubblica_dpc:
        DOCS.mkdir(parents=True, exist_ok=True)
        dest = DOCS / "dpc-controllo-appropriatezza.pdf"
        shutil.copy2(PDF_DPC, dest)
        print(f"[docs] {dest} ({dest.stat().st_size // 1024} KB)")
    else:
        print(f"[docs] non pubblicato il PDF DPC: il link '{LINK_DPC}' non risolverà "
              f"(usare --pubblica-dpc o cambiare url_o_percorso)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
