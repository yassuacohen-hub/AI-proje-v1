# -*- coding: utf-8 -*-
"""CLAUDE DESKTOP'un yazi kutusundaki model listesi NEREDEN GELIYOR?
Gozlem (PO ekrani): listede TEK kayit var -> 'claude-claudecombo'.
Ama gateway /v1/models 1042 kayit donuyor. DEMEK KI bir FILTRE/varlik kaydi var.
Aranacak yerler (9Router veritabani):
  settings / kv           -> 'model', 'claude', 'desktop', 'inference' anahtarlari
  providerConnections     -> Claude icin tanimli model listesi
  proxyPools              -> kanal havuzlari
  requestDetails          -> Claude Desktop'in GERCEKTE hangi uca istek attigi
Anahtar degerleri yazilmaz (D-380)."""
import json
import sqlite3
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
DB = Path.home() / "AppData/Roaming/9router/db/data.sqlite"
con = sqlite3.connect(f"file:{DB.as_posix()}?mode=ro", uri=True)
con.row_factory = sqlite3.Row

ANAHTAR_KELIME = ("model", "claude", "desktop", "inference", "allowed", "expose")


def tara(tablo: str, alanlar: list[str]) -> None:
    print(f"\n=== {tablo} ===")
    try:
        kolonlar = [r[1] for r in con.execute(f"PRAGMA table_info({tablo})")]
    except Exception as e:  # noqa: BLE001
        print("  okunamadi:", str(e)[:50])
        return
    print("  kolonlar:", kolonlar)
    n = 0
    for r in con.execute(f"SELECT * FROM {tablo}"):
        d = dict(r)
        damar = " ".join(str(v) for v in d.values()).lower()
        if any(k in damar for k in ANAHTAR_KELIME):
            n += 1
            ozet = []
            for k, v in d.items():
                s = str(v)
                if any(x in k.lower() for x in ("key", "token", "secret")):
                    s = "***" + s[-4:]
                elif len(s) > 90:
                    s = s[:90] + f"...({len(s)}b)"
                ozet.append(f"{k}={s}")
            print("  " + " | ".join(ozet)[:420])
            if n >= 12:
                print("  ... (ilk 12)")
                break
    if n == 0:
        print("  (ilgili kayit yok)")


for t, alans in [("settings", []), ("kv", []), ("providerConnections", [])]:
    tara(t, alans)

print("\n=== requestDetails: Claude Desktop'in cokttugu uclar (son 400) ===")
try:
    kolonlar = [r[1] for r in con.execute("PRAGMA table_info(requestDetails)")]
    print("  kolonlar:", kolonlar)
    yazi = [k for k in kolonlar if k.lower() in ("path", "endpoint", "url", "route")]
    if yazi:
        alan = yazi[0]
        for r in con.execute(
                f"SELECT {alan}, count(*) adet, max(rowid) son "
                f"FROM requestDetails GROUP BY {alan} ORDER BY son DESC LIMIT 25"):
            print(f"  {str(r[alan])[:70]:<72}x{r['adet']}")
except Exception as e:  # noqa: BLE001
    print("  okunamadi:", str(e)[:60])

print("\n=== proxyPools ===")
tara("proxyPools", [])
