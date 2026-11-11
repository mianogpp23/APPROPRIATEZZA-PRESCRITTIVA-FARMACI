# Particolarismi dispensazione farmaci — DPC Regione Siciliana

Portale statico di supporto alla consultazione prescrittiva per i farmacisti: farmaci in
**Distribuzione Per Conto (DPC)**, **distribuzione diretta ASP**, **Note AIFA** e formalismi, con le
regole operative in primo piano e il link puntuale al provvedimento di riferimento.

## Punto di ingresso

`index.html` è la **splash**: introduce il portale, riassume il disclaimer legale e richiede
l'accettazione delle condizioni (memorizzata nel `localStorage` del browser, `dpc-consenso`).
- **ACCETTO** → entra nel portale (`index_list.html`, l'elenco delle schede)
- **NON ACCETTO** → bloccano l'accesso, con avviso e link al disclaimer

Senza consenso le pagine interne reindirizzano automaticamente alla splash (`consent.js`).

## Pagine

| Pagina | Contenuto |
|---|---|
| `index.html` | splash di ingresso e disclaimer sintetico |
| `index_list.html` | elenco delle 7 schede (portale) |
| `home.html` | vista a sferette delle schede |
| `metilfenidato.html` | metilfenidato in DPC (pag. 41 del DPC) |
| `farmaci_dpc.html` | farmaci in distribuzione per conto (pp. 42-56) |
| `distribuzione_diretta.html` | farmaci in distribuzione diretta ASP (pp. 57-62) |
| `formalismi.html` | riepilogo dei formalismi vigenti (p. 64) |
| `farmaci_no_dpc.html` | farmaci fuori DPC con le loro eccezioni (p. 65) |
| `nota_99.html` | confezioni per uso inalatorio in Nota 99 (pp. 66-67) |
| `dpc_convenzionata.html` | diabete tipo 2 a Nota AIFA 100 passati in convenzionata |
| `disclaimer.html` | disclaimer legale e avvertenze complete |

## Dati e documenti

- `dati_farmaci.json` — **fonte di verità** (1746 record: descrizione, principio attivo, ATC, note, variazioni)
- `data/note_pagine.json` — note di pagina (blocchi DPC-NOTE) delle schede
- `data/pillole_pagine.json` — pillole operative (blocchi DPC-PILL) delle schede
- `data/pdf_pagine_ocr.json` — indice OCR delle pagine dei PDF (deep linking `#page=N`)
- `docs/` — PDF pubblicati: DPC regionale (71 pp.), Note 74/97/99, modifica PT Nota 39, diabete tipo 2
- `theme.css` / `theme.js` — switch dei 5 temi (notte, chiaro, ghiaccio, grafite, caldo)

## Regole editoriali

- **Non si altera la fonte**: in caso di incongruenze fra sezioni del DPC si mantiene il testo ufficiale e si
  aggiunge una nota chiarificatrice con il link alla pagina esatta.
- **Ogni marker `[agg. …]` è un link** al provvedimento (PDF diretto, con `#page=N` quando serve).
- **Le pillole operative** riassumono cosa controllare al banco; il link resta il supporto di verifica.
- **Nessun dato personale** nel sito: i recapiti presenti nei PDF sono istituzionali.

## Fonti

Documento di base: **Documento di Controllo dell'appropriatezza prescrittiva** di **Federfarma Messina**
(edizione 2023, D.A. n. 278/2024 – G.U.R.S. n. 15 del 29/03/2024). Database e regole operative
**successivamente aggiornati e integrati** con le disposizioni più recenti (determine AIFA 2025-2026,
protocolli regionali, circolari di categoria, versioni aggiornate del DPC).

## Strumenti

`scripts/` contiene il workflow e i validatori (sincronizzazione dati → HTML, verifica dei link e dei deep
link, test degli ordinamenti, audit delle associazioni). Sono pensati per la cartella di lavoro del
progetto, in cui la radice contiene `data/`, `docs/`, `html_estratto/` e `scripts/`.

## Verifica

```bash
python3 scripts/validazione/verifica_link.py       # ogni link raggiunge il documento
python3 scripts/validazione/verifica_deep_link.py  # ogni #page=N cade sulla pagina giusta
python3 scripts/validazione/test_ordinamenti.py    # gli ordinamenti riordinano davvero
python3 scripts/validazione/audit_associazioni.py  # PA / canale / Note coerenti
```
