#!/usr/bin/env python3
"""Verifica che tutti i link presenti nelle pagine del sito carichino davvero.

- link esterni: HTTP + dimensione + presenza di contenuto (le pagine JS vuote vengono segnalate)
- link locali (docs/*.pdf): esistenza + validita' del PDF
Uso: python3 verifica_link.py
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

HTML = ROOT / "html_estratto"
MIN_BYTES = 20000      # sotto questa soglia la pagina e' probabilmente una shell JS


def check_url(url: str) -> tuple[str, str]:
    try:
        out = subprocess.run(
            ["curl", "-sS", "-L", "--max-time", "40", "-A",
             "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
             "-o", "/tmp/_lnk.html", "-w", "%{http_code} %{size_download} %{url_effective}", url],
            capture_output=True, text=True, timeout=70)
        parts = out.stdout.split(" ", 2)
        if len(parts) < 3:
            return "000", "0", url
        return parts[0], parts[1], parts[2]
    except Exception:
        return "ERR", "0", url


def document_stamp(url: str, local: Path | None = None) -> str:
    """Descrive il documento raggiunto: per i PDF la prima pagina, per le pagine il <title>."""
    try:
        if local is not None:
            if local.suffix.lower() != ".pdf":
                return ""
            out = subprocess.run(["pdftotext", "-f", "1", "-l", "1", str(local), "-"],
                                 capture_output=True, text=True, timeout=60).stdout
            head = " ".join(out.split())[:110]
            return head
        tmp = Path("/tmp/_lnk_doc")
        subprocess.run(["curl", "-sS", "-L", "--max-time", "40", "-A", "Mozilla/5.0",
                        "-o", str(tmp), url], capture_output=True, timeout=70)
        if tmp.exists() and tmp.read_bytes()[:4] == b"%PDF":
            out = subprocess.run(["pdftotext", "-f", "1", "-l", "1", str(tmp), "-"],
                                 capture_output=True, text=True, timeout=60).stdout
            return " ".join(out.split())[:110]
        raw = tmp.read_text(encoding="utf-8", errors="replace") if tmp.exists() else ""
        m = re.search(r"<title[^>]*>(.*?)</title>", raw, re.S | re.I)
        if m:
            return re.sub(r"\s+", " ", m.group(1)).strip()[:110]
        return ""
    except Exception:
        return ""


def main() -> int:
    urls: dict[str, list[str]] = {}
    for f in sorted(HTML.glob("*.html")):
        t = f.read_text(encoding="utf-8")
        for m in re.finditer(r'href="([^"]+)"', t):
            u = m.group(1)
            if u.startswith("#") or u.startswith("http") is False and u.endswith(".html"):
                continue
            urls.setdefault(u, []).append(f.name)

    problemi = 0
    for u, pages in sorted(urls.items()):
        # il frammento (#page=N) non fa parte del percorso/URL: si valida il bersaglio
        target = u.split("#", 1)[0]
        if u.startswith("http"):
            code, size, final = check_url(target)
            ok = code == "200" and int(size or 0) >= MIN_BYTES
            stato = "OK " if ok else "KO "
            if not ok:
                problemi += 1
            print(f"{stato}{code} {int(size or 0):>8}b  {u[:88]}")
            if ok:
                stamp = document_stamp(target)
                if stamp:
                    print(f"      -> {stamp}")
            else:
                print(f"      usato in: {', '.join(pages)}")
        else:
            p = HTML / target
            if p.exists():
                info = subprocess.run(["pdfinfo", str(p)], capture_output=True, text=True).stdout
                pages_n = re.search(r"Pages:\s+(\d+)", info)
                print(f"OK {u:<70} PDF {pages_n.group(1) if pages_n else '?'} pagine, {p.stat().st_size} byte")
                stamp = document_stamp(target, local=p)
                if stamp:
                    print(f"      -> {stamp}")
            else:
                problemi += 1
                print(f"KO file locale mancante: {u}")
    print(f"\nlink verificati: {len(urls)} | problemi: {problemi}")
    return 1 if problemi else 0


if __name__ == "__main__":
    sys.exit(main())
