# Report aggiornamenti — DPC / Second Brain

**Generato:** 2026-11-10 14:20  
**Progetto:** `/media/k10/BTRFS 741/dpc`  
**Repository:** https://github.com/mianogpp23/APPROPRIATEZZA-PRESCRITTIVA-FARMACI (branch `main`)

---

## 1. Second Brain — verifica e sincronizzazione dell'archivio email

- **Pacchetti indicizzati:** 532 (pagine wiki gemelle: 532, abbinamento 1:1)
- **Per formato:** pdf: 211, html-email: 191, docx: 84, doc: 42, xlsx: 3, zip: 1
- **File reali nella cartella sorgente** `/media/k10/PASSWORDLIST/backup-farmacia`: 513 (.pdf 193, .html 191, .docx 84, .doc 42, .xlsx 3) → **tutti indicizzati, 0 mancanti**
- **PDF dentro archivi ZIP:** 18 (TURNI II SEMESTRE 2024.zip) + 1 pacchetto per il contenitore ZIP
- **Riparazione qualità testo:** 7 pacchetti con font PDF a codifica personalizzata (testo illeggibile) → testo rigenerato con OCR tesseract (qualità 0,02 → 0,80)
- **Annotazione:** 28 email 'varie' senza corpo testuale (contenuto solo in allegati) → annotate
- **Indice:** registry ricostruito, QMD reindicizzato (lexical, model-free)

## 2. Verifica multi-colonna delle righe farmaci

Ricerca eseguita su **tutte** le colonne di ogni riga contemporaneamente: Minsan/AIC, Descrizione, Principio attivo, campo PT/SM/Nota AIFA.
- Record analizzati: **1725** (6 elenchi: farmaci_dpc 1178, distribuzione_diretta 329, nota_99 158, farmaci_no_dpc 41, formalismi 10, metilfenidato 9)
- Incrocio con la Second Brain (532 documenti) su 4 livelli di colonna, con filtro sui documenti che contengono provvedimenti concreti (revoca, determinazione, nuova immissione, carenza, prezzo/classe, nota/PT).
- Verifica online: indice delle determine AIFA 2023-2026 (G.U.) + testi vigenti AIFA e Regione Siciliana (prot. 35765 del 09/07/2026).

## 3. Normative rilevate e variazioni applicate

| Data | Provvedimento | Righe |
|---|---|---|
| 21/11/2025 | Det. AIFA 1533/2025 – G.U. n. 271 del 21/11/2025 | 1 |
| 18/11/2025 | Det. AIFA 11/11/2025, G.U. n. 267 del 17/11/2025 | 1 |
| 12/04/2026 | Det. AIFA 421/2026 del 01/04/2026 – G.U. n. 84 del 11/04/202 | 1 |
| 10/10/2025 | Det. AIFA 1322/2025 del 10/10/2025 – G.U. n. 241 del 16/10/2 | 1 |
| 09/07/2026 | Det. AIFA 821/2026 (G.U. n. 144 del 24/06/2026) – prot. Regi | 1 |
| 17/11/2025 | Federfarma Ragusa (circolare 102/2025) | 2 |
| 09/07/2026 | AIFA | 3 |
| 19/10/2023 | AIFA/RITA | 5 |
| 09/07/2026 | Det. AIFA 821/2026, G.U. n. 144 del 24/06/2026 | 9 |
| 13/09/2025 | DET PRES 1127/2025 – G.U. n. 213 del 13/09/2025 | 11 |
| 12/04/2026 | Det. AIFA 422/2026 del 01/04/2026 – G.U. n. 84 del 11/04/202 | 12 |
| 15/05/2025 | DET PRES 624/2025 – G.U. n. 111 del 15/05/2025 | 23 |
| 06/07/2026 | Det. AIFA 914/2026 del 06/07/2026 – G.U. n. 157 del 09/07/20 | 24 |
| 09/07/2026 | Det. AIFA 820/2026 (G.U. n. 144 del 24/06/2026) – prot. Regi | 37 |
| 05/08/2025 | Det. AIFA 1037/2025 del 31/07/2025 – G.U. n. 180 del 05/08/2 | 49 |
| 16/02/2026 | Det. AIFA 142/2026 – G.U. n. 38 del 16/02/2026 (DET PRES 142 | 127 |

**Totale variazioni applicate: 344** su **307 record** con marker.

### Note AIFA presenti nelle liste e stato

| Nota | Righe | Stato |
|---|---|---|
| 8 | 2 | abrogata 18/11/2025 (Det. 1519/2025) — applicata |
| 11 | 2 | abrogata 12/04/2026 (Det. 421/2026) — applicata |
| 15 | 1 | nessun provvedimento 2024-2026 rilevato |
| 36 | 4 | nessun provvedimento 2024-2026 rilevato |
| 39 | 24 | aggiornata 17/06/2026 (Det. 819/2026) + allegato sostituito 06/07/2026 — applicata |
| 40 | 34 | nessun provvedimento 2024-2026 |
| 51 | 46 | aggiornata 07/11/2024 e 15/05/2025 — applicata |
| 65 | 23 | nessun provvedimento 2024-2026 |
| 74 | 37 | aggiornata 17/06/2026 (Det. 820/2026, età 45→46) — applicata |
| 75 | 2 | nessun provvedimento 2024-2026 rilevato |
| 79 | 22 | aggiornata 22/02/2025 e 13/09/2025 (denosumab senza PT) — applicata |
| 84 | 24 | abrogata 12/04/2026 (Det. 422/2026) — applicata |
| 85 | 254 | aggiornata 16/02/2026 (Det. 142/2026) — applicata |
| 92 | 2 | abrogata 04/10/2025 (Det. 1224/2025) + rettifica 10/10/2025 — applicata |
| 95 | 11 | nessun provvedimento 2024-2026 |
| 96 | 1 | nessun provvedimento 2024-2026 |
| 97 | 10 | aggiornata 17/06/2026 (Det. 821/2026) — applicata |
| 98 | 2 | aggiornata 08/10/2024, 19/06/2025, 21/11/2025 — applicata |
| 100 | 109 | aggiornata 05/08/2025 (Det. 1037/2025) — applicata |

## 4. Stato delle modifiche alle pagine HTML

| Pagina | Marker di aggiornamento |
|---|---|
| distribuzione_diretta.html | 59 |
| farmaci_dpc.html | 266 |
| farmaci_no_dpc.html | 13 |
| formalismi.html | 0 |
| index.html | 0 |
| index_list.html | 0 |
| metilfenidato.html | 4 |
| nota_99.html | 2 |

Totale marker negli HTML: **344** · sincronizzazione idempotente (0 differenze residue) · `<td>` bilanciati.

## 5. Segnalazioni aperte (non applicate)

1. **XARELTO 42cpr 15MG (038744138) e 28cpr 20MG (038744189)**: il DPC assegna *Nota 98* / *Nota 100*, il riepilogo a p.15 colloca tutte le cpr di XARELTO sotto *Nota 97* (Nota 98/100 sono note di diabete/anti-VEGF). Correzione non applicata: serve conferma dell'Assessorato.
2. **SANIFOLIN 027683046**: nel DPC (p.54) la riga ha descrizione *SANIFOLIN* ma PA *CALCIO FOLINATO* e *Nota 11* → colonne disallineate nel documento regionale. Annotato nella riga; inoltre l'AIC è stato revocato il 02/01/2026.
3. **TEV / TVP-EP domiciliare dei DOAC**: verificare con l'ASP se sopravvive il PT regionale (Nota 101 abrogata il 18/11/2025, DPC D.A. 278/2024 antecedente).
4. **Nuove confezioni da valutare**: RYBELSUS 1,5/4/9 mg, DABIGATRAN ETEXILATO MEDICAL VALLEY 110/150 mg (in DPC regionale aggiornato?).
5. **DPC di riferimento** (D.A. 278/2024, testo agg. 10/10/2024) antecedente alle determine 2025-2026: le liste sono aggiornate riga per riga, il documento sorgente no.

## 6. Strumenti (riutilizzabili)

- `scripts/sync_html_da_json.py` — riconcilia tutte le pagine HTML con il JSON (idempotente)
- `scripts/aggiorna_note_2025_2026.py` — applica gli aggiornamenti delle Note AIFA 2024-2026
- `scripts/aggiorna_note_97.py` — aggiornamenti Nota 97 / 8 / 92
- `/home/k10/scripts/dpc_audit_html_vs_json.py` — audit di coerenza HTML ↔ JSON
- `/home/k10/scripts/dpc_fase2_match_multi_colonna.py`, `dpc_fase2_evidenze.py`, `dpc_fase2_evidenze_documento.py` — matching multi-colonna con la Second Brain
- `/home/k10/scripts/sb_audit_qualita_testo.py` — audit di leggibilità dei pacchetti (OCR dei PDF corrotti)
- `/home/k10/scripts/ingest_backup_farmacia.py` — ingestione dell'archivio email nella Second Brain

## 7. Temi del sito (switch)

Il sito espone **5 temi** selezionabili con il pulsante in basso a destra (perso tra una visita e l'altra):

| Tema | Fondo | Accento | Titoli |
|---|---|---|---|
| **notte** (predefinito, palette riveduta) | blu notte profondo #0b1220 | azzurro/viola addolciti | rosso Corsa profondo #e10600 / giada #6ee7b7 |
| **chiaro** | grigio chiaro #f8fafc | blu/viola | bordeaux / verde bosco |
| **ghiaccio** | azzurro chiaro #eaf4fb | blu profondo | arancio bruciato / verde petrolio |
| **grafite** | grigio scuro #1c1c1f | bianco/argento | rosa / verde lime |
| **caldo** | crema #fff8ed | arancio/ambra | rosso mattone / verde oliva |

Implementazione: `theme.css` (5 temi come terne RGB) + `theme.js` (selettore, persistenza in localStorage `dpc-tema`, propagazione agli iframe). Nelle 8 pagine **tutti** i colori letterali sono passati a variabili di tema (`rgb(var(--t-*-rgb))`): 0 residui. Script di applicazione: `scripts/apply_theme.py`.

## 8. Link alle determine e pagina "DPC in Convenzionata"

**Link cliccabili**: ogni marker `[agg. data - fonte]` nelle liste DPC e' un link al provvedimento
ufficiale (G.U. via ELI, pagina AIFA della nota, circolare regionale). Mappa in
`scripts/fonti_links.json` (21 provvedimenti, tutti con URL verificato HTTP 200).
Totale: **760 marker, 760 cliccabili, 0 senza link**.

**Nuova pagina `dpc_convenzionata.html`**: farmaci per il diabete mellito di tipo 2 a **Nota AIFA 100**
passati dal canale DPC al canale della **Convenzionata** dal **15 ottobre 2025** (circolare Federfarma
Sicilia n. 90 del 15/10/2025, prot. PRES. TS n. 218; Determine AIFA del 02/07/2025, G.U. n. 153 del
04/07/2025; nota prot. Assessorato 34212 del 18/07/2025; D.A. 367/2025). Regola: niente Scheda di
Valutazione e Prescrizione, niente Protocollo DMDU, erogazione in Convenzionata con ricetta a Nota 100.
Tabella: 35 righe (molecola, nome commerciale, confezioni AIC, presenza nelle liste DPC, Nota 100
obbligatoria) + ricerca. Nelle liste DPC risultano **31 record** (28 confezioni distinte) gia' marcati.

## 9. Link verificati e colonne Nota 99 ricostruite

**Link**: i link alla Gazzetta Ufficiale non mostravano il testo (pagina JavaScript di 11 KB; i pattern di
download diretto restituiscono 404/400). Nel sito sono ora pubblicati i documenti originali in `docs/`:
`nota-74.pdf`, `nota-97.pdf`, `nota-99.pdf`, `modifica-pt-nota-39.pdf`, `prot-35765-note-74-97-99.pdf`.
Le altre fonti restano su AIFA / OMCeO / Regione Siciliana. `scripts/verifica_link.py` controlla ogni link:
**18 verificati, 0 problemi**.

**Colonne Nota 99**: la tabella del DPC (pp. 66-67) è stata ri-estratta con pdfplumber (5 colonne reali:
AIC | Medicinale | Principio attivo | BPCO/regola | SSN non soggette a Nota 99). L'estrazione precedente aveva
unito frammenti di colonne diverse (es. `A-PT-Nota` dentro il Principio attivo). Ora ogni dato sta nella sua
colonna e il **sync ricostruisce le celle dal JSON** e **inserisce le righe mancanti** (recuperata
OXIS TURBOHALER 4,5, AIC 033312012: 159 righe in pagina).

## 10. Audit geometrico delle 5 tabelle DPC e 20 farmaci inseriti

**Verifica**: le altre 5 tabelle del DPC (oltre alla Nota 99 gia' ricostruita) sono state verificate con
lo stesso estrattore geometrico (`pdfplumber`, assegnazione per coordinate x) e con riscontro sui render a
200 dpi. Esito: **0 contaminazioni di colonna** in tutte e 5; `farmaci_no_dpc` (41 record), `formalismi`
(10 record + note di chiusura) e `metilfenidato` (9 farmaci + 3 note) risultano completi e coerenti.

**Ritrovamento**: **20 farmaci presenti nel DPC regionale erano assenti dalle liste**, per un troncamento
sistematico dell'estrazione originaria (ultima riga di ogni pagina del DPC pp. 42-55; ultime due righe di
ogni pagina di Distribuzione diretta pp. 58-61).

- *Farmaci in DPC* (12): ARIPIPRAZOLO SAND 5MG (044407043), CINACALCET EG 60MG (046284055),
  CORBILTA (043152204), ENANTONE (027066137), FRAGMIN 6SIR 2500UI (027276031), IVABRADINA MY 5MG
  (044905293), MEMANTINA AURO 20MG (042241024), OLANZAPINA ACT 2,5MG (040261036), PRASUGREL TEVA 10MG
  (045597402), QUETIAPINA TE 25MG (040510152), SENEFOR 0,7MG (040036042), TROBALT 50MG (041141021).
- *Distribuzione diretta* (8): FERRIPROX FL/OS (034525042, 034525028), METADONE CLOR. MOL 10M/20M
  (029610108, 029610110), RILUTEK (032887010), RILUZOLO ACT (040541070), TRACLEER 125MG/62,5MG
  (035609041, 035609027).

**Applicato**: `data/dati_farmaci.json` 1726 -> **1746 record**; ogni riga nuova riporta il marker
`[agg. 10/11/2026 – DPC Regione Siciliana, pag. N]` cliccabile verso il DPC pubblicato in
`docs/dpc-controllo-appropriatezza.pdf` (72 pp.). Pagine aggiornate: `farmaci_dpc.html` 1182 -> **1194**
righe, `distribuzione_diretta.html` 329 -> **337** righe. Ripulite anche le entita' HTML residue in 4
record. `scripts/verifica_link.py`: **19 link verificati, 0 problemi**.

## 11. Regole di erogazione dei farmaci a PT e Nota 99 (DPC pag. 67)

Le tre note in fondo alla pagina 67 del DPC (Nota 99) **non erano presenti** sul sito e sono state inserite
nella pagina `nota_99.html`, subito sotto la tabella:

1. **Scheda web based**: per i farmaci a PT e Nota 99 la Scheda web based compilata attraverso il sistema
   Tessera Sanitaria (TS) e' adottata in via esclusiva dal 1° settembre 2022; la prescrizione e' consentita
   solo agli Specialisti.
2. **Numero di protocollo**: il Farmacista eroga la ricetta Rossa o DEM con Nota 99 riscontrando la presenza
   del numero di protocollo `BPCO0A0000......` sulla ricetta oppure a video (come per i FANV con Nota 97);
   in mancanza del Protocollo allega fotocopia della Scheda con Protocollo.
3. **TRIMBOW**: dal 4 aprile 2023 la specialita' TRIMBOW e' erogabile anche esclusivamente nel trattamento
   dell'asma con Piano Terapeutico AIFA specifico cartaceo in originale, prescritto da UU.OO. di
   pneumologia, geriatria, medicina interna ed allergologia (strutture ospedaliere, territoriali o
   convenzionate con il SSN) - **senza l'indicazione della Nota AIFA 99** (riferimento `*` nella riga
   TRIMBOW, colonna "PT Aifa Asma *").

Le note sono conservate in `data/note_pagine.json` e re-inserite dal sync tra i marcatori
`<!-- DPC-NOTE-BEGIN -->` / `<!-- DPC-NOTE-END -->`, cosi' non si perdono alle successive sincronizzazioni.
Ogni nota riporta il marker `[agg. 10/11/2026 – DPC Regione Siciliana, pag. 67]` cliccabile verso
`docs/dpc-controllo-appropriatezza.pdf`. Link verificati: **19, 0 problemi**.
