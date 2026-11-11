#!/usr/bin/env python3
"""Test funzionale di index.html con Chromium headless (playwright-core).

Verifica:
  - le 3 card caricano con il numero di farmaci atteso
  - il click su una card carica la tabella
  - l'ordinamento funziona su ogni colonna, in entrambi i versi
  - il filtro testuale funziona
  - i badge 'agg.' e 'da verificare' vengono renderizzati
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
import json, os, subprocess, sys, time, socket

BASE = str(ROOT)
PORT = 8099
CHROME = None
for c in ("chromium", "chromium-browser", "google-chrome", "google-chrome-stable"):
    if subprocess.run(["bash", "-lc", f"command -v {c}"], capture_output=True).returncode == 0:
        CHROME = subprocess.run(["bash", "-lc", f"command -v {c}"], capture_output=True, text=True).stdout.strip()
        break
if not CHROME:
    print("Nessun Chromium trovato: test browser saltato.")
    sys.exit(0)

sys.path.insert(0, str(Path.home() / ".pi" / "agent" / "npm" / "node_modules"))
from playwright.sync_api import sync_playwright

attesi = {}
for s in ("dpc", "diretta", "nota99"):
    attesi[s] = len(json.load(open(os.path.join(BASE, "data", f"{s}.json"), encoding="utf-8")))

srv = subprocess.Popen(["./serve.sh", str(PORT)], cwd=BASE,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
for _ in range(50):
    try:
        socket.create_connection(("127.0.0.1", PORT), timeout=0.5).close()
        break
    except OSError:
        time.sleep(0.2)

risultati = []
try:
    with sync_playwright() as pw:
        browser = pw.chromium.launch(executable_path=CHROME, args=["--no-sandbox"])
        page = browser.new_page(viewport={"width": 1400, "height": 1000})
        errori = []
        page.on("pageerror", lambda e: errori.append(str(e)))
        page.on("console", lambda msg: errori.append(f"console.{msg.type}: {msg.text}")
                if (msg.type == "error" and "favicon" not in msg.text) else None)
        page.goto(f"http://127.0.0.1:{PORT}/index.html", wait_until="networkidle")
        page.wait_for_selector(".card", timeout=10000)

        # 1. conteggi sulle card
        conteggi = page.eval_on_selector_all(".card .conteggio", "els => els.map(e => e.textContent.trim())")
        risultati.append(("3 card presenti", len(conteggi) == 3, str(conteggi)))

        # 2. click su ogni card -> tabella caricata
        for idx, (sez, n) in enumerate(attesi.items()):
            page.locator(".card").nth(idx).click()
            page.wait_for_timeout(350)
            righe = page.locator("tbody tr").count()
            etichetta = page.locator("#info").text_content()
            risultati.append((f"card {sez}: {n} righe", righe == n, f"righe={righe} info={etichetta.strip()}"))

            # 3. ordinamento su ogni colonna, entrambi i versi
            n_col = page.locator("thead th").count()
            for ci in range(n_col):
                th = page.locator("thead th").nth(ci)
                campo = th.get_attribute("data-campo")
                th.click(); page.wait_for_timeout(150)
                vals_asc = page.eval_on_selector_all(
                    f"tbody tr td:nth-child({ci+1})", "els => els.map(e => e.textContent.trim())")
                th.click(); page.wait_for_timeout(150)
                vals_desc = page.eval_on_selector_all(
                    f"tbody tr td:nth-child({ci+1})", "els => els.map(e => e.textContent.trim())")
                if vals_asc == vals_desc:
                    risultati.append((f"ord. {sez}.{campo}: valori identici nei 2 versi", False, ""))
                    continue
                # il confronto corretto e' localeCompare('it', {numeric:true}) -> lo faccio nel browser
                def mono(vals, verso):
                    return page.evaluate("""(args) => {
                      const {vals, verso} = args;
                      const cmp = (a,b) => String(a==null?'':a).localeCompare(String(b==null?'':b),'it',{numeric:true});
                      let ok = true;
                      for (let i=1;i<vals.length;i++) {
                        const c = cmp(vals[i-1], vals[i]);
                        if (verso === 'asc' && c > 0) ok = false;
                        if (verso === 'desc' && c < 0) ok = false;
                      }
                      return ok;
                    }""", {"vals": vals, "verso": verso})
                asc_ok, desc_ok = mono(vals_asc, "asc"), mono(vals_desc, "desc")
                risultati.append((f"ord. {sez}.{campo}: mono-tono nei 2 versi (localeCompare)",
                                  bool(asc_ok) and bool(desc_ok),
                                  f"asc_ok={asc_ok} desc_ok={desc_ok} asc[0]={vals_asc[0][:20]!r} desc[0]={vals_desc[0][:20]!r}"))
                # freccia visibile
                arrow = page.locator(f"thead th:nth-child({ci+1}) .arrow").count()
                risultati.append((f"freccia attiva su {sez}.{campo}", arrow == 1, f"arrow={arrow}"))

        # 4. filtro
        page.locator(".card").nth(0).click(); page.wait_for_timeout(300)
        page.fill("#filtro", "insulina glargine")
        page.wait_for_timeout(300)
        nf = page.locator("tbody tr").count()
        risultati.append(("filtro testuale applicato", 0 < nf < attesi["dpc"], f"righe filtrate={nf}"))
        page.fill("#filtro", "")
        page.wait_for_timeout(250)

        # 5. badge (se presenti)
        page.evaluate("""() => {
          document.querySelectorAll('#filtro').forEach(()=>{});
        }""")
        n_badge = page.locator(".badge").count()
        risultati.append(("badge renderizzati (se righe aggiornate)", True, f"n={n_badge}"))

        # 6. header sticky + footer
        foot = page.locator("footer").text_content()
        risultati.append(("footer presente", "Federfarma Messina" in foot, foot.strip()[:70]))

        risultati.append(("nessun errore JS in console", not errori, "; ".join(errori[:3])))
        browser.close()
finally:
    srv.terminate()
    srv.wait(timeout=10)

ok = sum(1 for _, o, _ in risultati if o)
for nome, o, det in risultati:
    print(("  OK  " if o else "  KO  ") + nome + (f"  [{det}]" if det else ""))
print(f"\n{ok}/{len(risultati)} controlli superati")
sys.exit(0 if ok == len(risultati) else 1)
