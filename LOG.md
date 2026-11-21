# LOG — DPC

## 2026-11-20 — Fase 1 Percorsi (clone di lavoro)

- **Path canonico originale**: `/media/k10/BTRFS 741/progetti-github-farmacia/dpc` (repo Git in `html_estratto/`, `data/dati_farmaci.json` fonte di verità, mount BTRFS).
- **Clone di lavoro/fallback**: `/home/k10/progetti/dpc/APPROPRIATEZZA-PRESCRITTIVA-FARMACI` (`origin/main` 75e9174, nessun push). Usato per le modifiche Fase 1; da propagare al canonico solo dopo conferma utente.
- **Backup**: `dati_farmaci.json.bak-pre-fase1` (632912 bytes, copia root pre-Fase 1).
- **Fase 1 eseguita**: creato `scripts/config.py` (rilevamento layout root/html_estratto, risoluzione JSON `data/dati_farmaci.json` poi fallback `dati_farmaci.json`, helper PDF `PDF_*`, `BACKUP`, `require_json()`, `ensure_backup_dir()`).
- **Refactor**: 30 script sotto `scripts/` aggiornati per usare `scripts.config`; aggiunto bootstrap `sys.path` per esecuzione da root. `rendi_portabili.py` convertito a stub innocuo (obsoleto).
- **Guard --help**: aggiunti guard `--help/-h` (SystemExit 0, nessun side effect) agli script con lavoro top-level/storici: `estrai_2023.py`, `build_dpc_convenzionata.py`, `build_index.py`, `audit_contaminazione.py`, `audit_estratore_vs_json.py`, `audit_geometrico_dpc.py`, `audit_tabelle_dpc.py`, `qa_crosscheck.py`, `test_index.py`, `verifica_link.py`.
- **Fix mirati**: `build_dpc_convenzionata.py`, `audit_associazioni.py`, `audit_contaminazione.py` usano `JSON.read_text()`; `audit_estratore_vs_json.py` usa `JSON`, `PDF_DPC`, lookup `scripts/applicazione/estrai_2023.py` con guard; `verifica_deep_link.py` usa `HTML.glob`; `aggiorna_mancanti_dpc.py` usa `HTML`/config e guarda `PDF_DPC` None.
- **Verifica**: `python3 -m py_compile scripts/config.py scripts/*.py scripts/applicazione/*.py scripts/validazione/*.py` OK; 30/30 script (escluso config.py) passano `--help` o `--dry-run` senza `FileNotFoundError` e con rc=0.
- **Discrepanza nota**: `data/dati_farmaci.json` assente nel clone; `dati_farmaci.json` presente in root (1744 record). `config.py` risolve con fallback; nessun dato inventato/modificato.
- **Script assenti nel clone (non creati)**: `scripts/applicazione/estrai_dpc.py`, `scripts/applicazione/fix_tr_vuoti.py`, `scripts/applicazione/ocr_dpc.py`.
- **Residui noti**: `scripts/validazione/qa_crosscheck.py` contiene path storico `output/pp41-67_verificato.csv` (protetto da --help guard; file non presente nel clone). Script applicativi storici con logica top-level restano eseguibili ma richiedono conferma/contesto dati prima dell'uso reale.
- **HTML revertiti**: ripristinati `farmaci_dpc.html`, `formalismi.html`, `index.html` dopo side effect involontario da esecuzione script durante smoke test; successivamente aggiunti guard --help.
- **Nessun commit/push eseguito**.
## Fase 2 – Validatori (2026-11-20)

### Eseguiti (workdir clone, output /tmp)
| Script | RC | Esito sintetico |
|---|---:|---|
| `scripts/validazione/test_ordinamenti.py` | 1 | 0 colonne verificate; nessun server raggiungibile su `http://127.0.0.1:8081` (test browser richiede sito servito). Corretto default IP LAN hardcoded + messaggio chiaro. |
| `scripts/validazione/verifica_atc.py` | 0 | Strumento diagnostico ad-hoc (dump bande 3 ATC non standard) — non pass/fail. |
| `scripts/validazione/audit_associazioni.py` | 0 | 1 sospetto: `038744189 XARELTO*28CPR RIV 20MG PA=RIVAROXABAN Nota 100 [farmaci_dpc]` — **falso positivo noto, non modificare**. |
| `scripts/validazione/audit_contaminazione.py` | 0 | 579 sospetti (celle lunghe/testo esteso), audit informativo. |
| `scripts/validazione/audit_estratore_vs_json.py` | 0 | 1991 celle diverse, 9 solo JSON, 11 solo PDF; anomalie parser `{principio_attivo_vuoto:341, atc_non_standard:3, banda_senza_minsan:1, rimborso_non_standard:88, minsan_non_valido:2}`. |
| `scripts/validazione/audit_geometrico_dpc.py` | 0 | 2237 incoerenze, audit informativo. |
| `scripts/validazione/audit_tabelle_dpc.py` | 0 | 1527 incoerenze, audit informativo. |
| `scripts/validazione/verifica_deep_link.py` | 0 | 70 deep link verificati, 70 coerenti, 0 da controllare. |
| `scripts/validazione/qa_crosscheck.py` | 1 | Artefatti storici mancanti nel clone (`output/pp41-67_verificato.csv`, `data/dpc.json,diretta.json,nota99.json`). Corretto: fallimento pulito con elenco mancanti (no traceback). |
| `scripts/validazione/verifica_link.py` | 1 | 36 link verificati, 1 problema reale esterno: `https://www.aifa.gov.it/-/diabete-mellito-tipo2-aggiornamento-nota-aifa-100` (000/0b), usato in `distribuzione_diretta.html` (3 occ.). Non modificato. Aggiunto fallimento esplicito se 0 pagine/link trovati (richiesta Fase 2). |
| `scripts/validazione/test_index.py` | 1 | Artefatti mancanti nel clone (`data/dpc.json,diretta.json,nota99.json`); richiede anche Playwright+Chromium. Corretto: fallimento pulito + type-safety fix (`text_content() or ""`). |

### sync_html_da_json.py --dry-run (nessuna modifica applicata)
- `metilfenidato.html`: 9 verificate, 3 righe senza record (benigne note), file cambiato False.
- `farmaci_dpc.html`: 1190 verificate, 0 celle allineate, 0 modificate, 0 record senza riga, 102 righe senza record, **1199 differenze solo testuali (non scritte), file cambiato: True**.
- `distribuzione_diretta.html`: 337 verificate, tutto allineato.
- `nota_99.html`: 159 verificate, tutto allineato.
- `farmaci_no_dpc.html`: 39 verificate, 1 differenza solo testuale (non scritta).
- `formalismi.html`: 7 verificate, 3 righe senza record (benigne note).
- `dpc_convenzionata.html`: 0 righe verificate, file cambiato: True.
- Totale celle allineate: 0. **Nessun file scritto**.

### Fix applicati (Fase 2)
- `scripts/validazione/verifica_link.py`: check `if not urls: ERRORE+return 1` (richiesta piano); signature `check_url -> tuple[str,str,str]`.
- `scripts/validazione/test_ordinamenti.py`: default `--url` da `192.168.1.229:8081` a `127.0.0.1:8081`; messaggio esplicito se 0 colonne verificate.
- `scripts/validazione/qa_crosscheck.py`: pre-check artefatti mancanti con messaggio chiaro; context manager CSV.
- `scripts/validazione/test_index.py`: pre-check artefatti mancanti con messaggio chiaro; context manager JSON; fix `text_content() or ""`.

### Verifiche
- `python3 -m py_compile` sui 4 file modificati: OK.
- `qa_crosscheck.py` rieseguito: RC=1 con messaggio pulito (no traceback).
- `test_index.py` rieseguito: RC=1 con messaggio pulito (no traceback).

### Note / non azioni
- Nessun dato/HTML/PDF modificato; nessun commit/push.
- Audit con molte incoerenze (estratore/geo/tabelle/contaminazione) sono report informativi: non corretti ciecamente; richiedono valutazione in Fase 4/contesto dati.
- Link AIFA nota 100 rotto è esterno; va valutato in Fase 3/5/6 secondo policy (non alterare contenuto normativo senza conferma).
- `test_ordinamenti.py` e `test_index.py` richiedono ambiente browser/server; nel clone non eseguibili end-to-end senza prerequisiti.
## Fase 3 – Documentazione e navigazione (2026-11-20)

### Modifiche
- `README.md`: record JSON corretto 1746→1744; chiarito percorso canonico clone/root e risoluzione via `scripts/config.py`; tabella pagine aggiornata includendo `eparinoidi.html`, `insuline.html`, `stupefacenti.html`; sezione Strumenti aggiornata al layout reale (no assunzione fissa `html_estratto/`).
- `README_SYNCHRONIZZAZIONE.md`: allineato a JSON canonico root attuale (`dati_farmaci.json`), risoluzione percorso via `scripts/config.py`, rigenerazione consigliata prima `--dry-run`.
- `index_list.html`: aggiunta voce sidebar `stupefacenti.html` (stesso stile, meta "Normativa DPR 309/90 · slide 49-82") dopo Metilfenidato.

### Verifiche/fatti
- `dati_farmaci.json` root: 1744 record; per elenco: farmaci_dpc 1190, distribuzione_diretta 337, nota_99 159, farmaci_no_dpc 39, formalismi 10, metilfenidato 9; 406 variazioni in 325 record.
- `docs/`: 7 PDF presenti. `stupefacenti.html` presente in root.

### Note
- Nessuna modifica a dati, HTML di contenuto normativo, PDF in `docs/`. Nessun commit/push.

## Fase 4 – Dati (report, nessuna correzione) (2026-11-20)

### Ambito
- Solo analisi/report su `dati_farmaci.json` (clone). **Nessuna modifica ai dati/JSON/HTML/PDF**, nessun commit/push.

### 1) Record senza descrizione (49)
- Conteggio: **49** record con `descrizione` mancante/vuota/null.
- Per elenco: `farmaci_no_dpc` **39**, `formalismi` **10**.
- Struttura osservata (tutti e 49): `{"minsan": None, "descrizione": None, "principio_attivo": None, "atc": None, "note": None, "elenco": "..."}`.
- Interpretazione: sembrano placeholder/righe vuote o righe di testo libero non strutturato importate; **non è chiaro se siano voluti**.
- **Decisione richiesta**: confermare se vanno mantenuti così, rimossi, o convertiti in rappresentazione esplicita (solo dopo conferma; nessuna azione autonoma).

### 2) ATC incompleti/da confermare (PROTROMPLEX, UMANCOMPLEX, STELARA)
- `PROTROMPLEX TIM3*F 600UI+20ML` — `aic: 023288032`, `minsan: null`, `principio_attivo: COMPLESSO PROTROMBINICO UMANO`, `atc: B02BD`, `note: PT`, `elenco: distribuzione_diretta`.
  - Osservazione: `B02BD` è livello 4 (fattori della coagulazione del sangue). Per complesso protrombinico umano (fattori II, VII, IX, X in combinazione) il codice WHO ATC/DDD completo è **B02BD01**.
  - Fonti: WHO ATC/DDD index B02BD01 https://www.whocc.no/atc_ddd_index/?code=B02BD01 ; EMA Core SPC Human Plasma Prothrombin Complex Products (ATC B02BD01) https://www.ema.europa.eu/en/documents/scientific-guideline/core-spc-human-plasma-derived-prothrombin-complex-medicinal-products_en.pdf ; Wikipedia Prothrombin complex concentrate (B02BD01) https://en.wikipedia.org/wiki/Prothrombin_complex_concentrate .
  - **Proposta (da confermare)**: `B02BD` → `B02BD01`.
- `UMANCOMPLEX D.I.*FL 500UI+F20M` — `aic: 023309103`, `minsan: null`, `principio_attivo: COMPLESSO PROTROMBINICO UMANO`, `atc: B02BD`, `note: PT`, `elenco: distribuzione_diretta`.
  - Osservazione/proposta identica a PROTROMPLEX (stesso PA/categoria).
  - **Proposta (da confermare)**: `B02BD` → `B02BD01`.
- `STELARA*SC 1SIR 1ML 90MG` — `aic: 038936047`, `minsan: null`, `principio_attivo: USTEKINUMAB`, `atc: L04C05`, `note: ''`, `elenco: distribuzione_diretta`.
  - Osservazione: `L04C05` non è il codice ATC completo WHO per ustekinumab; il codice WHO ATC/DDD completo è **L04AC05** (ustekinumab, interleukin inhibitors).
  - Fonti: WHO ATC/DDD index L04AC05 https://www.whocc.no/atc_ddd_index/?code=L04AC05 ; evidenza di uso/regolatorio ustekinumab (Stelara, anti-IL-12/23) coerente con classe L04AC — FDA/EMA label/product info (es. Stelara/ustekinumab biosimilars labeling). 
  - **Proposta (da confermare)**: `L04C05` → `L04AC05`.

### 3) `distribuzione_diretta`: AIC/minsan e coerenza schema
- `distribuzione_diretta` totale: **337** record.
- Chiavi osservate nel campione/tutti i record DD: `['aic', 'descrizione', 'atc', 'principio_attivo', 'note', 'elenco', 'variazioni']`.
- Record con `aic` presente: **337/337**. Record senza chiave `minsan`: **337/337** (nessun `minsan: null` esplicito, chiave assente).
- I 3 target sopra (PROTROMPLEX, UMANCOMPLEX, STELARA) sono in `distribuzione_diretta` e seguono lo stesso schema `aic`-based, con `minsan` assente.
- **Valutazione schema**: per `distribuzione_diretta` l'identificativo usato è `aic`, non `minsan`; non è di per sé un dato mancante, ma è una **divergenza di schema** rispetto agli elenchi `minsan`-based. Va confermato se lo schema DD "solo AIC" è intenzionale/canonico o se va normalizzato/dual-key.

### Decisioni richieste / esito
1. **49 record senza descrizione** (39 `farmaci_no_dpc`, 10 `formalismi`, tutti campi null tranne elenco): **nessuna modifica**. Assunzione conservativa in attesa di conferma esplicita (mantenere/rimuovere/rappresentare diversamente).
2. **ATC confermati dall'utente ("Procedi con fix") e applicati** su backup `dati_farmaci.json.bak-pre-fase4-fix`:
   - `023288032 PROTROMPLEX TIM3*F 600UI+20ML`: `B02BD` → `B02BD01`
   - `023309103 UMANCOMPLEX D.I.*FL 500UI+F20M`: `B02BD` → `B02BD01`
   - `038936047 STELARA*SC 1SIR 1ML 90MG`: `L04C05` → `L04AC05`
   Verifica: `python3 -m json.tool` implicito via load/dump OK; 1744 record; 49 no_desc invariati; `git diff --unified=0 -- dati_farmaci.json` mostra solo 3 linee ATC + newline finale.
3. **Schema `distribuzione_diretta` aic-only** (337/337 con `aic`, nessuna chiave `minsan`): **nessuna modifica**. Assunzione conservativa: schema lasciato com'è in attesa conferma policy canonica.

## Fase 5 – File orfani (report, nessuna modifica) (2026-11-20)

### Ambito
- Solo verifica riferimenti e report. **Nessun file cancellato/spostato/rinominato**.

### Risultati

| File | Presente | Tracciato git | Riferimenti nel repo | Valutazione | Proposta |
|---|---|---|---|---|---|
| `ang_prodotti.xls` (root, 313K) | sì | sì | Nessun riferimento da `git grep "ang_prodotti"` nel codice tracciato; è input sorgente storico (gara/PT/Piano Web, citato in contesto 41af3fa) | Non orfano funzionale runtime, ma non usato dagli script correnti | **Tenere**; opzionale spostarlo in `data/sorgenti/` o `docs/sorgenti/` in un cleanup dedicato, solo dopo conferma e aggiornamento eventuali riferimenti/documentazione |
| `data/turni_acate.json` | sì | sì | `index_list.html:403` costruisce dinamicamente `data/turni_${citta}.json` (include acate) | **Usato** | **Tenere** |
| `data/turni_comiso.json` | sì | sì | `index_list.html:403` | **Usato** | **Tenere** |
| `data/turni_pedalino.json` | sì | sì | `index_list.html:403` | **Usato** | **Tenere** |
| `data/turni_scoglitti.json` | sì | sì | `index_list.html:403` | **Usato** | **Tenere** |
| `data/turni_vittoria.json` | sì | sì | `index_list.html:403` (caso esplicito `vittoria`) | **Usato** | **Tenere** |

### Decisioni utente (2026-11-21)
1. `ang_prodotti.xls`: **tenere** in root. Nessuna azione.
2. `data/turni_*.json`: **tenere** in `data/`. Nessuna azione.
3. Fase 4 punto 1 (49 record no-desc): **tenere**. Nessuna azione.
4. Fase 4 punto 3 (schema DD AIC-only): **canonico**. Nessuna azione.

## Fase 6 – Aggiornamento normativo (report, nessuna applicazione) (2026-11-21)

### Ambito
- Solo elenco/report. **Nessuna modifica applicata** a dati, HTML, PDF, script; nessun commit/push. Gli script indicati sono stati letti come input, **non eseguiti**.

### Evidenza locale (marker `[agg. …]` negli HTML)
- File con marker `[agg.]`: `disclaimer.html`, `distribuzione_diretta.html`, `farmaci_no_dpc.html`, `metilfenidato.html`, `nota_99.html`.
- Marker osservati (grep): includono `27/11/2025 – circ. Fed. 420/2025` (6 occ.), ma anche marker successivi già presenti nel repo (`09/12/2025`, `09/07/2026 Det. AIFA 819/821/822/2026`, `06/07/2026`, `10/11/2026 DPC Regione Siciliana pag. 58-61/67` ecc.). 
- **Nota**: il piano utente indicava 27/11/2025 come ultimo marker; la scansione mostra marker più recenti già presenti in alcuni HTML. Il cutoff per questo report è comunque **post-27/11/2025** come richiesto, con segnalazione esplicita di ciò che è già presente/mappato.

### Script input già presenti (NON eseguiti)
| Script | Ambito mappato | Stato |
|---|---|---|
| `scripts/applicazione/aggiorna_norme_2026.py` | Det. AIFA 819/2026 (Nota 39), 820/2026 (Nota 74), 822/2026 citata in NOTA99_SCHEDA; circ. Fed. 420/2025 Nota 100; revoche AIC SANIFOLIN 02/01/2026, ZOMACTON 09/12/2025 | Input, non eseguito |
| `scripts/applicazione/aggiorna_nota_97.py` | Det. AIFA 821/2026 (Nota 97, GU 144 24/06/2026, vigore 09/07/2026); abrogazioni Nota 8 (Det 11/11/2025 GU 267 17/11/2025) e Nota 92 (Det 30/09/2025 GU 230 03/10/2025) | Input, non eseguito |
| `scripts/applicazione/aggiorna_note_2025_2026.py` | Nota 84 abrogata (Det 422/2026, GU 84 11/04/2026, 12/04/2026); Nota 11 abrogata (Det 421/2026); Nota 85 aggiornata (Det 142/2026, GU 38 16/02/2026); Nota 98 aggiornata (Det 1533/2025, GU 271 21/11/2025); Nota 51 aggiornata (DET PRES 624/2025, GU 111 15/05/2025); Nota 79 aggiornata (DET PRES 1127/2025, GU 213 13/09/2025; anche Det 225/2025) | Input, non eseguito |
| `scripts/applicazione/correggi_associazioni.py` | Correzioni associazioni/colonne (spillover PA/nota, JARDIANCE AIC 043443047, XARELTO incongruenze Nota 97/98/100 rispetto riepilogo DPC pag.15) | Input, non eseguito; **XARELTO già noto come punto sensibile** |
| `scripts/applicazione/ricostruisci_nota99.py` | Ricostruzione righe Nota 99 da tabella DPC pp.66-67; marker Det. AIFA 822/2026 | Input, non eseguito |

### Aggiornamenti post-27/11/2025 rilevanti (da verificare prima di applicare)

| Ambito | Provvedimento / aggiornamento | Data/efficacia | Fonte ufficiale | Note |
|---|---|---|---|---|
| AIFA Nota 97 | Det. AIFA 821/2026, aggiornamento Nota 97 (DOAC/AVK, abolizione PT AIFA/scheda valutazione per FANV) | GU n.144 24/06/2026, vigore 09/07/2026 | [AIFA Elenco Note](https://www.aifa.gov.it/elenco-note-aifa), [GU/AIFA determine RIFday](https://www.rifday.it/2026/06/25/aifa-in-gazzetta-ufficiale-le-determine-di-aggiornamento-delle-note-39-74-97-e-99) | Mappato in `aggiorna_nota_97.py`; marker 2026 già presenti in alcuni HTML. Da verificare testo vigente e impatto locale prima di applicare. |
| AIFA Nota 39 | Det. AIFA 819/2026, aggiornamento Nota 39 (somatropina/somatrogon) | GU n.144 24/06/2026, vigore 09/07/2026 | [AIFA Elenco Note](https://www.aifa.gov.it/elenco-note-aifa), [RIFday](https://www.rifday.it/2026/06/25/aifa-in-gazzetta-ufficiale-le-determine-di-aggiornamento-delle-note-39-74-97-e-99) | Mappato in `aggiorna_norme_2026.py`. |
| AIFA Nota 74 | Det. AIFA 820/2026, aggiornamento Nota 74 (infertilità, limite età donna 45→46) | GU n.144 24/06/2026, vigore 09/07/2026 | [AIFA Elenco Note](https://www.aifa.gov.it/elenco-note-aifa), [RIFday](https://www.rifday.it/2026/06/25/aifa-in-gazzetta-ufficiale-le-determine-di-aggiornamento-delle-note-39-74-97-e-99) | Mappato in `aggiorna_norme_2026.py`. |
| AIFA Nota 99 | Det. AIFA 822/2026, aggiornamento Nota 99 BPCO (abrogata SVP; riclassificazione RR; triplici LAMA+LABA+ICS) | GU n.144 24/06/2026, vigore 09/07/2026 | [AIFA Elenco Note](https://www.aifa.gov.it/elenco-note-aifa), [RIFday](https://www.rifday.it/2026/06/25/aifa-in-gazzetta-ufficiale-le-determine-di-aggiornamento-delle-note-39-74-97-e-99) | Mappato in `aggiorna_norme_2026.py` e `ricostruisci_nota99.py`. |
| AIFA Nota 84 | Det. AIFA 422/2026, abrogazione Nota 84 (aciclovir/valaciclovir/famciclovir/brivudina) | GU n.84 11/04/2026, vigore 12/04/2026 | [AIFA Elenco Note](https://www.aifa.gov.it/elenco-note-aifa) (Nota 84 abolita 09/04/2026 in pagina elenco) | Mappato in `aggiorna_note_2025_2026.py`; verificare coerenza data pagina vs GU. |
| AIFA Nota 11 | Det. AIFA 421/2026, abrogazione Nota 11 (calcio folinato non più rimborsato SSN) | GU n.84 11/04/2026, vigore 12/04/2026 | [AIFA Elenco Note](https://www.aifa.gov.it/elenco-note-aifa) | Mappato in `aggiorna_note_2025_2026.py`; impatto forte (rimborsabilità). Richiede revisione accurata. |
| AIFA Nota 85 | Det. AIFA 142/2026, aggiornamento Nota 85 (Alzheimer; donepezil/memantina classe A) | GU n.38 16/02/2026, vigore 17/02/2026 | [AIFA Elenco Note](https://www.aifa.gov.it/elenco-note-aifa) | Mappato in `aggiorna_note_2025_2026.py`. |
| AIFA Nota 8 | Abrogazione Nota 8 (carnitina) | Det. AIFA 11/11/2025, GU n.267 17/11/2025, vigore 18/11/2025 (pre-cutoff stretto ma vicino) | [AIFA Elenco Note](https://www.aifa.gov.it/elenco-note-aifa) | Mappato in `aggiorna_nota_97.py`; verificare se già applicato. |
| AIFA Nota 92 | Abrogazione Nota 92 (benzilpenicillina benzatinica) | Det. AIFA 30/09/2025, GU n.230 03/10/2025 | [AIFA Elenco Note](https://www.aifa.gov.it/elenco-note-aifa) | Pre-27/11/2025 ma mappato; verificare stato applicazione. |
| Revoche AIC | SANIFOLIN (AIC 027683046, 027683010) revoca; ZOMACTON (027743032 e 10 mg) revoca | SANIFOLIN 02/01/2026; ZOMACTON 09/12/2025 | Circolari Federfarma 4/2026 e 429/2025 come da script; verificare determine AIFA/GU | Mappate in `aggiorna_norme_2026.py`. |
| Nota 100 precisazioni | Eccezioni Nota 100 (FORXIGA 5/10 mg, JARDIANCE 10 mg; attenzione JARDIANCE 25 mg) | 27/11/2025 circ. Federfarma 420/2025 | `raw/sources/SRC-2026-11-10-269` citato nello script; verificare fonte primaria | Marker 27/11/2025 già presente; mappato in `aggiorna_norme_2026.py`. |
| Regione Siciliana DPC/appropriatezza | Aggiornamenti documenti/Note su portale regionale | variabile | [Regione Siciliana - Appropriatezza d'uso dei farmaci](https://www.regione.sicilia.it/istituzioni/regione/strutture-regionali/assessorato-salute/dipartimento-pianificazione-strategica/appropriatezza-d-uso-farmaci) | Pagina ufficiale elenca nota 74/97/99, modifica PT Nota 39, guida GLP-1 2026, brochure antidiabetici. Verificare date/adozione regionale rispetto a determine AIFA nazionali. |

### Raccomandazioni (nessuna applicazione)
1. **Non eseguire** `aggiorna_norme_2026.py`, `aggiorna_nota_97.py`, `aggiorna_note_2025_2026.py`, `correggi_associazioni.py`, `ricostruisci_nota99.py` senza revisione umana e conferma esplicita.
2. Verificare su fonti primarie (GU/AIFA/Regione Sicilia) testo vigente, data efficacia e perimetro prima di ogni patch.
3. Per ogni applicazione: backup, dry-run/diff, controllo impatto su `dati_farmaci.json`, HTML, deep-link `[agg.]`, poi revisione.
4. `correggi_associazioni.py` contiene correzione XARELTO già identificata come sensibile: trattare separatamente con conferma.
5. La presenza di marker 2026 già negli HTML richiede audit di coerenza prima di nuove applicazioni (evitare duplicazioni marker).

## Fase 6b – Piano di revisione per TUTTI i provvedimenti (nessuna applicazione) (2026-11-21)

Richiesta utente: "Fallo su tutte". Questo è un piano di revisione/dry-run, **non un'autorizzazione ad applicare**. Ogni blocco richiede conferma esplicita prima di qualsiasi modifica a dati/HTML.

### Prerequisiti globali (prima di qualsiasi blocco)
- [ ] Backup fresco di `dati_farmaci.json` (nome con data/ora) e, se si tocca HTML, backup/copia di lavoro dei file HTML interessati.
- [ ] Conferma che il working tree è pulito o che le modifiche in corso sono intenzionali.
- [ ] Audit marker esistenti: `grep -rn "\[agg\." *.html` e verifica duplicati/marker futuri già presenti.
- [ ] Verifica fonte primaria per ogni provvedimento (GU/AIFA/Regione Sicilia) e salvataggio riferimento in `LOG.md`.
- [ ] Nessun `--apply` senza conferma esplicita utente nel turno; nessun commit/push.

### Blocco A – Pacchetto AIFA 819-822/2026 (Note 39,74,97,99)
| Campo | Dettaglio |
|---|---|
| Script input | `aggiorna_norme_2026.py` (39/74/99/Nota100/revoche), `aggiorna_nota_97.py` (97), `ricostruisci_nota99.py` (Nota 99 tabella DPC) |
| Fonti primarie da verificare | [AIFA Elenco Note](https://www.aifa.gov.it/elenco-note-aifa); GU Serie Generale n.144 24/06/2026; determine AIFA 819/820/821/822/2026; [Regione Sicilia Appropriatezza](https://www.regione.sicilia.it/istituzioni/regione/strutture-regionali/assessorato-salute/dipartimento-pianificazione-strategica/appropriatezza-d-uso-farmaci) per recepimento/indicazioni locali |
| Record/aree impattate | Nota 39: record con `Nota 39` in `note`; Nota 74: `Nota 74`; Nota 97: DOAC MINSAN in script + AVK in `farmaci_no_dpc` cells; Nota 99: elenco `nota_99`, ricostruzione colonne da PDF DPC pp.66-67 |
| Dry-run atteso | Eseguire **solo** con `--dry-run`/modalità lettura; catturare elenco record toccati, diff JSON/HTML, conteggi. Verificare che non riscriva marker già presenti. |
| Rischi | Marker 09/07/2026 già presenti negli HTML; doppia applicazione. Nota 97: distinzione FANV vs TEV/TVP-EP e PT regionale ASP va verificata con fonte primaria. Nota 99: ricostruzione da tabella PDF può alterare colonne/note; verificare contro PDF DPC. |
| Criterio OK | Fonte primaria confermata; diff minimo e coerente; nessun dato inventato; deep-link/marker corretti; nessuna regressione su record non target. |

### Blocco B – Abrogazioni Note 84 e 11 (Det. 421-422/2026)
| Campo | Dettaglio |
|---|---|
| Script input | `aggiorna_note_2025_2026.py` |
| Fonti primarie da verificare | GU n.84 11/04/2026; Det. AIFA 421/2026 e 422/2026; [AIFA Elenco Note](https://www.aifa.gov.it/elenco-note-aifa) |
| Record/aree impattate | `Nota 84`: aciclovir/valaciclovir/famciclovir/brivudina; `Nota 11`: calcio folinato. Lo script segnala già "riga DPC con colonne disallineate" per Nota 11. |
| Dry-run atteso | `--dry-run`; verificare match multi-colonna, evitare falsi positivi su testo "Nota 11/84" in descrizioni non target. |
| Rischi | **Alto**: Nota 11 comporta non rimborsabilità SSN per calcio folinato; richiede verifica puntuale riga per riga. Nota 84 ha clausola salvaguardia spesa: testo marker deve restare fedele. |
| Criterio OK | Ogni riga toccata tracciata con AIC/MINSAN/descrizione; testo conforme a determina/GU; nessuna riga non pertinente. |

### Blocco C – Nota 85 Alzheimer (Det. 142/2026)
| Campo | Dettaglio |
|---|---|
| Script input | `aggiorna_note_2025_2026.py` |
| Fonti primarie da verificare | GU n.38 16/02/2026; Det. AIFA 142/2026; pagina AIFA Nota 85 |
| Record/aree impattate | record con `Nota 85`; associazione donepezil/memantina classe A dal 17/02/2026 |
| Dry-run atteso | `--dry-run`; controllare che i record donepezil/memantina siano identificati correttamente e che il marker non si duplichi. |
| Rischi | Possibile disallineamento tra testo script e testo GU definitivo; verificare classificazione/classe A. |
| Criterio OK | Fonte primaria confermata; solo record Nota 85/donepezil-memantina toccati. |

### Blocco D – Note 98, 51, 79 (aggiornamenti 2025, mappati nello script)
| Campo | Dettaglio |
|---|---|
| Script input | `aggiorna_note_2025_2026.py` |
| Fonti primarie da verificare | Det. AIFA 1533/2025 (Nota 98, GU 271 21/11/2025); DET PRES 624/2025 (Nota 51, GU 111 15/05/2025); DET PRES 1127/2025 (Nota 79, GU 213 13/09/2025) + Det 225/2025; AIFA pagine nota |
| Record/aree impattate | Note 98/51/79 nei campi note/cells. Nota 79 include DENOSUMAB/PT web-based/MMG: verificare impatto campo PT. |
| Dry-run atteso | `--dry-run`; separare report per nota. |
| Rischi | Alcune date pre-cutoff 27/11/2025 (51,79) ma già mappate: verificare se già applicate per evitare marker duplicati. Nota 98 vicina al cutoff (21/11/2025). |
| Criterio OK | Nessuna duplicazione marker; testo coerente con determina; impatto PT/Nota 79 confermato. |

### Blocco E – Abrogazioni Note 8 e 92 (pre-cutoff ma mappate)
| Campo | Dettaglio |
|---|---|
| Script input | `aggiorna_nota_97.py` |
| Fonti primarie da verificare | Det. AIFA 11/11/2025 GU 267 17/11/2025 (Nota 8); Det. AIFA 30/09/2025 GU 230 03/10/2025 (Nota 92); circolari Fed. 403/2025, 333/2025 |
| Record/aree impattate | Nota 8: carnitina MINSAN `018610079`; Nota 92: `SIGMACILLINA*...` in DD. |
| Dry-run atteso | `--dry-run`; confermare che i record target esistono ancora con quei valori. |
| Rischi | Basso volume, ma impatto normativo specifico; verificare già applicato. |
| Criterio OK | 0 duplicati; record target esatti. |

### Blocco F – Revoche AIC e Nota 100 eccezioni
| Campo | Dettaglio |
|---|---|
| Script input | `aggiorna_norme_2026.py` |
| Fonti primarie da verificare | Determine AIFA revoca SANIFOLIN 02/01/2026 e ZOMACTON 09/12/2025; GU; circolari Fed. 4/2026, 429/2025. Circ. Fed. 420/2025 Nota 100 (allegato 1) + fonte primaria AIFA/Regione. |
| Record/aree impattate | SANIFOLIN AIC `027683046`; ZOMACTON `027743032`; SGLT2 eccezioni `042494029,042494070,043443136` e attenzione `043443047`. |
| Dry-run atteso | `--dry-run`; verificare che `043443047` (JARDIANCE 25 mg) non venga marcato come eccezione OK. |
| Rischi | Revoche AIC: il marker deve essere chiaro ("scorte esauribili entro 180 gg dalla GU" solo se confermato dalla fonte). Nota 100: confusione tra eccezioni e non-eccezioni. |
| Criterio OK | Fonte primaria confermata; nessuna eccezione Nota 100 errata; revoche tracciate con data/fonte corretta. |

### Blocco G – Correzioni associazioni (XARELTO/JARDIANCE/spillover)
| Campo | Dettaglio |
|---|---|
| Script input | `correggi_associazioni.py` |
| Fonti primarie da verificare | DPC Regione Siciliana PDF (`docs/dpc-controllo-appropriatezza.pdf`) pag. 15,55-56,59; tabella riepilogo FANV/Nota 97. |
| Record/aree impattate | Spillover PA→nota (10 record attesi dallo script); JARDIANCE DD AIC `043443047` PA errato; XARELTO DPC `038744138`/`038744189`. |
| Dry-run atteso | `--dry-run`; elenco completo AIC toccati. |
| Rischi | **Molto alto per XARELTO**: lo script modifica il testo nota ma **non** imposta la Nota 97 come sostituzione semplice; aggiunge precisazione con link pag.15. Richiede revisione umana della formulazione finale. JARDIANCE: confermare ATC A10BD11 e PA EMPAGLIFLOZIN dal DPC. |
| Criterio OK | Revisione manuale AIC per AIC; XARELTO approvato esplicitamente; nessuna alterazione del testo normativo fonte, solo annotazione/precisazione tracciata. |

### Blocco H – Ricostruzione Nota 99 da PDF DPC
| Campo | Dettaglio |
|---|---|
| Script input | `ricostruisci_nota99.py` |
| Fonti primarie da verificare | `docs/dpc-controllo-appropriatezza.pdf` pp.66-67; Det. AIFA 822/2026 per marker triplici. |
| Record/aree impattate | tutti i record `elenco == nota_99`; possibili righe PDF da aggiungere. |
| Dry-run atteso | `--dry-run`; confrontare record aggiornati, mancanti, da aggiungere. |
| Rischi | Sovrascrive celle/colonne Nota 99: può perdere note/variazioni non previste. Richiede diff riga-per-riga prima di apply. Lo script ha `--apply/--dry-run` obbligatorio. |
| Criterio OK | Diff completo rivisto; nessuna perdita variazioni; righe aggiunte verificate nel PDF. |

### Blocco I – Regione Siciliana / DPC locale
| Campo | Dettaglio |
|---|---|
| Script input | Nessuno specifico; usare `aggiorna_norme_2026.py`/altri solo se contengono recepimento regionale già mappato. |
| Fonti primarie da verificare | [Regione Siciliana – Appropriatezza d'uso dei farmaci](https://www.regione.sicilia.it/istituzioni/regione/strutture-regionali/assessorato-salute/dipartimento-pianificazione-strategica/appropriatezza-d-uso-farmaci); circolari/provvedimenti ASP/Dipartimento Pianificazione Strategica. |
| Record/aree impattate | PT regionali, DPC Regione Siciliana, canali distributivi, modulistica. |
| Dry-run atteso | Nessuna esecuzione script; prima ricognizione documentale e mappa impatti. |
| Rischi | Sovrapposizione tra norma AIFA nazionale e recepimento/indicazione regionale. |
| Criterio OK | Per ogni modifica regionale: fonte regionale primaria, data, ambito Sicilia, impatto separato dal nazionale. |

### Ordine di esecuzione consigliato (dopo conferma)
1. Prerequisiti globali + audit marker.
2. Blocco G (correzioni associazioni) solo su casi non-XARELTO, poi XARELTO separato.
3. Blocco H (Nota 99 ricostruzione) in dry-run, revisione manuale.
4. Blocco A (819-822/2026) a pacchetti piccoli per nota.
5. Blocchi B-F per gruppi di note, con dry-run e diff.
6. Blocco I regionale solo con fonte primaria regionale.

**Nessuna applicazione eseguita. Per procedere serve conferma esplicita per blocco (es. "esegui dry-run Blocco A") o per uno specifico script/provvedimento.**

### Esito dry-run "tutto" (2026-11-21, nessuna scrittura)
Eseguiti in `--dry-run` nel clone; nessun file scritto.

| Script | RC | Esito riportato | Note |
|---|---:|---|---|
| `aggiorna_norme_2026.py --dry-run` | 0 | `[JSON] record aggiornati: 0` | Nessuna modifica JSON rilevata dallo script. |
| `aggiorna_nota_97.py --dry-run` | 0 | `[JSON] modifiche su dati_farmaci.json: 0` | Nessuna modifica. |
| `aggiorna_note_2025_2026.py --dry-run` | 0 | 4 record aggiornati: `nota100_aggiornata:1, nota98_aggiornata:1, nota51_aggiornata:1, nota85_aggiornata:1` | Output senza dettaglio AIC/record; identificare record prima di eventuale apply. |
| `correggi_associazioni.py --dry-run` | 0 | `correzioni: 2 campi su 2 record` (XARELTO `038744189`, `038744138`, campo `note`) | Diff stampato troncato a 70 char; prima/dopo identici nel prefisso visibile. **XARELTO sensibile**: richiede ispezione manuale completa prima di qualsiasi apply. |
| `ricostruisci_nota99.py --dry-run` | 0 | `righe estratte PDF 159, record attuali 159, aggiornati 159, AIC non trovati 0, righe PDF non nelle liste 0` | "Aggiornati 159" indica match/aggiornamento in memoria per tutti i record; non equivale a 159 differenze semantiche. Richiede diff reale riga-per-riga prima di apply. |

**Blocchi senza script eseguibile**: G (spillover/JARDIANCE dentro `correggi_associazioni.py` ma output osservato solo XARELTO; verificare esecuzione completa/codice), I (Regione Sicilia: solo ricognizione documentale, nessun dry-run script).

**Nessuna modifica applicata.** Attesa conferma esplicita per eventuale `APPLICA` mirato (per blocco/script/record), dopo revisione umana.

### Apply eseguito: `aggiorna_note_2025_2026.py --apply` (2026-11-21)
- Conferma utente: "APPLICA aggiorna_note_2025_2026".
- Backup script: `output/backup-note-2025-2026-20261121-191102/`. Backup manuale pre-apply: `dati_farmaci.json.bak-pre-apply-note2025-20261121-191102`.
- Esito script: 4 record aggiornati (`nota100_aggiornata:1, nota98_aggiornata:1, nota51_aggiornata:1, nota85_aggiornata:1`).
- Diff reale (`dati_farmaci.json`, 4 record):
  - `038744189 XARELTO*28CPR RIV 20MG` (idx 1689, farmaci_dpc): aggiunta variazione Det. AIFA 1037/2025 (05/08/2025, Nota 100) + append marker/testo Nota 100 in coda a `note`.
  - `038744138 XARELTO*42CPR RIV 15MG` (idx 1691, farmaci_dpc): aggiunta variazione Det. AIFA 1533/2025 (21/11/2025, Nota 98) + append marker/testo Nota 98 in coda a `note`.
  - `027066137 ENANTONE*IM SC SIR11,25MG/MLRP` (idx 1734, farmaci_dpc): aggiunta variazione DET PRES 624/2025 (15/05/2025, Nota 51) + append marker/testo.
  - `042241024 MEMANTINA AURO*28CPR RIV 20MG` (idx 1737, farmaci_dpc): aggiunta variazione Det. AIFA 142/2026 (16/02/2026, Nota 85) + append marker/testo.
- **Attenzione qualità**: i due XARELTO contengono già nel testo una precisazione "Nota 100/98 ... incongruente, ... Vale il riepilogo: FANV = Nota 97". L'apply ha comunque appeso il marker di aggiornamento Nota 100/98 in coda. Effetto potenzialmente fuorviante; **richiede revisione**. Rollback selettivo possibile dai backup.
- Nessun HTML/PDF modificato; nessun commit/push. In attesa OK/revisione.

### Apply eseguito: `correggi_associazioni.py --apply` (intero) (2026-11-21)
- Conferma utente: "1 poi 2 poi 3 esegui una alla volta" (step 1).
- Backup manuale pre-apply: `dati_farmaci.json.bak-pre-apply-correggi-20261121-191431`.
- Esito script: `correzioni: 2 campi su 2 record` (XARELTO `038744189`, `038744138`, campo `note`). **Crash post-write**: `shutil.SameFileError` perché `COPIA_SITO == JSON_PATH` nel layout clone; il JSON era già stato scritto e risulta valido (`python3 -m json.tool` OK).
- Diff reale (2 record):
  - `038744189 XARELTO*28CPR RIV 20MG`: nota riscritta da `testo_dpc + MARKER + precisazione`; aggiunta variazione `stato=correzione` (DPC pag.15, 11/11/2026).
  - `038744138 XARELTO*42CPR RIV 15MG`: idem.
- **Effetto importante**: la riscrittura nota ha rimosso la coda `[agg. 05/08/2025... Nota 100 aggiornata...]` / `[agg. 21/11/2025... Nota 98 aggiornata...]` appena aggiunta da `aggiorna_note_2025_2026.py`. Le variazioni aggiunte da quello script restano presenti. Questo confligge parzialmente con "OK mantieni" precedente; serve decisione utente.
- Nessun commit/push. Stop in attesa OK prima dello step 2.

### Step 2 – SOLO JARDIANCE (dry-run mirato) (2026-11-21)
- Blocco 2 di `correggi_associazioni.py` isolato: AIC `043443047` DD, PA `AEMIFAPAGLIFLOZIN`→`EMPAGLIFLOZIN`.
- Dry-run mirato: **0 modifiche**. Stato attuale: `043443047 JARDIANCE*28CPR RIV 25MG` DD già `PA=EMPAGLIFLOZIN`, `ATC=A10BD11`.

### Step 3 – `ricostruisci_nota99.py --apply` (2026-11-21)
- Conferma utente: "ok" (procedi step 3).
- Backup script: `output/backup-nota99-colonne-20261121-195539/`. Backup manuale: `dati_farmaci.json.bak-pre-apply-nota99-20261121-195539`.
- Esito script: `159 estratte, 159 JSON, aggiornati 159, non trovati 0, extra 0, 0 righe aggiunte`.
- **Diff reale JSON: 0 record modificati** (nessuna differenza semantica). "Aggiornati 159" = record matchati/processati, non cambiati.

### Sequenza 1-2-3 completata (nessun commit/push)
- Step 1: applicato `correggi_associazioni` intero (2 XARELTO scritti, crash post-write SameFileError benigno, coda nota XARELTO sovrascritta).
- Step 2: SOLO JARDIANCE dry-run mirato, 0 modifiche.
- Step 3: ricostruisci_nota99 applicato, 0 diff reale.
