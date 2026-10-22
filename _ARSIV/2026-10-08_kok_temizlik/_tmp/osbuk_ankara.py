# -*- coding: utf-8 -*-
"""OSBÜK liste sayfasından Ankara OSB satırlarını çeker (stdlib, tek seferlik ölçüm)."""
import re
import sys
import urllib.request

URL = "https://osbuk.org/view/osb/osbliste.php"
html = urllib.request.urlopen(urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0"}), timeout=30).read().decode("utf-8", "replace")
tag = re.compile(r"<[^>]+>")
rows = re.findall(r"<tr[^>]*>([\s\S]*?)</tr>", html)
out = []
for r in rows:
    cells = [re.sub(r"\s+", " ", tag.sub(" ", c).replace("&nbsp;", " ")).strip() for c in re.findall(r"<td[^>]*>([\s\S]*?)</td>", r)]
    if len(cells) >= 7 and cells[1] == "Ankara":
        out.append(cells)
sys.stdout.reconfigure(encoding="utf-8")
print(f"toplam satir: {len(rows)} | Ankara: {len(out)}")
for c in out:
    print(f"{c[0]:>3} | {c[2]:<45} | {c[4]:<25} | {c[6]}")
