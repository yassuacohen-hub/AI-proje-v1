# -*- coding: utf-8 -*-
"""CLAUDE'IN GERCEKTE HANGI MODEL ADIYLA ISTEK ATTIGINI OLGER.
Claude Desktop/Code'un yazi kutusundaki model kutusu = gonderecegi model adi.
Bu dosya: (a) requestDetails son istekler (provider/model/status), (b) settings.data
yapisinin anahtar agaci, (c) kv scope sayilari.
GUVENLIK: tum ciktidan once desen bazli maskeleme (nvapi-, sk-, eyJ, ya29., ghu_,
castai_, workos:, aoaAAAA) — onceki aracim 'data' kolonunu ham basti ve anahtar
sizdirdi; bu tur yine olmamali (D-380)."""
import json
import re
import sqlite3
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
DB = Path.home() / "AppData/Roaming/9router/db/data.sqlite"

DESEN = re.compile(
    r"(nvapi-|sk-[A-Za-z0-9\-]{6,}|sk-or-v1-|eyJ[A-Za-z0-9_\-]{6,}|ya29\.[A-Za-z0-9_\-]{6,}"
    r"|ghu_[A-Za-z0-9]{6,}|castai_[A-Za-z0-9]{6,}|workos:[A-Za-z0-9._\-]{6,}"
    r"|aoaAAAA[A-Za-z0-9_\-]{6,}|cfut_[A-Za-z0-9]{6,}|gho_[A-Za-z0-9]{6,})"
    r"[A-Za-z0-9_\-\.]*")


def maskele(s: str) -> str:
    s = DESEN.sub(lambda m: m.group(1)[:9] + "…MASKELI", s)
    return s if len(s) <= 300 else s[:300] + f"…({len(s)}b)"


con = sqlite3.connect(f"file:{DB.as_posix()}?mode=ro", uri=True)
con.row_factory = sqlite3.Row

print("=== (a) SON 30 ISTEK: Claude hangi adla gonderiyor? ===")
for r in con.execute("SELECT timestamp, provider, model, status FROM requestDetails"
                     " ORDER BY id DESC LIMIT 30"):
    print(f"  {str(r['timestamp'])[:19]} {str(r['provider'])[:16]:<17}"
          f"{maskele(str(r['model']))[:58]:<60}{r['status']}")

print("\n=== (b) settings.data anahtar agaci ===")
row = con.execute("SELECT data FROM settings LIMIT 1").fetchone()
if row:
    d = json.loads(row["data"])

    def agac(o, derin=0, yol=""):
        if derin > 2:
            return
        if isinstance(o, dict):
            for k, v in o.items():
                if isinstance(v, (dict, list)):
                    boyut = len(v)
                    print("  " + "  " * derin + f"{k}: ({type(v).__name__} {boyut})")
                    agac(v, derin + 1, yol + "/" + k)
                else:
                    print("  " + "  " * derin + f"{k} = {maskele(str(v))[:70]}")
        elif isinstance(o, list) and o:
            print("  " + "  " * derin + f"[0] ornek: {maskele(str(o[0]))[:90]}")
    agac(d)

print("\n=== (c) kv scope dagilimi ===")
for r in con.execute("SELECT scope, count(*) n FROM kv GROUP BY scope ORDER BY n DESC"):
    print(f"  {str(r['scope'])[:40]:<42}{r['n']}")

print("\n=== (d) Claude ile gelen isteklerde gorulen model adlari (ozet) ===")
for r in con.execute("SELECT provider, model, count(*) n FROM requestDetails"
                     " GROUP BY provider, model ORDER BY n DESC LIMIT 20"):
    print(f"  {str(r['provider'])[:14]:<16}{maskele(str(r['model']))[:62]:<64}x{r['n']}")
