#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""VDS 9Router DB'sindeki kombo uyelerini cek (py.exe ile, ssh uzerinden)."""
import json
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
OUT = Path("_tmp/vds_kombolar.json")

SCRIPT = r'''
import json, sqlite3, sys, glob, os
sys.stdout.reconfigure(encoding="utf-8")
adaylar = [
    os.path.expanduser("~/AppData/Roaming/9router/db/data.sqlite"),
    r"C:\Users\Administrator\AppData\Roaming\9router\db\data.sqlite",
    r"C:\ProgramData\9router\db\data.sqlite",
    r"C:\Hugin_insights\Apps\hugin-infra\9router\db\data.sqlite",
    r"C:\Hugin_insights\apps\9router\db\data.sqlite",
]
# 9router profilini bul: %AppData%/9router
aday = []
for b in ["C:\\Users", "C:\\ProgramData", "C:\\Hugin_insights"]:
    for p in glob.glob(b + "**\\9router\\db\\data.sqlite", recursive=True):
        aday.append(p)
for p in adaylar + aday:
    try:
        if os.path.exists(p):
            con = sqlite3.connect("file:" + p + "?mode=ro", uri=True)
            con.row_factory = sqlite3.Row
            rows = con.execute("SELECT name, kind, models FROM combos ORDER BY name").fetchall()
            con.close()
            sonuc = {}
            for r in rows:
                try:
                    modeller = json.loads(r["models"] or "[]")
                except Exception:
                    modeller = []
                if isinstance(modeller, list):
                    adlar = []
                    for m in modeller:
                        if isinstance(m, str):
                            adlar.append(m)
                        elif isinstance(m, dict):
                            adlar.append(m.get("model") or m.get("id") or m.get("name") or "?")
                    sonuc[r["name"]] = {"kind": r["kind"], "uyeler": adlar}
            if sonuc:
                print(json.dumps({"PATH": p, "combos": sonuc}, ensure_ascii=False))
                break
    except Exception as e:
        print("ERR:", p, e, file=sys.stderr)
'''

# ssh ile py.exe uzerinden calistir
try:
    r = subprocess.run(
        ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=15", "huginn-vds",
         "py.exe -3 -X utf8 -c", SCRIPT],
        capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=60,
    )
    print("RC:", r.returncode)
    print("STDERR:", r.stderr[:800])
    out = r.stdout.strip()
    if out:
        # tek satirlik JSON dondur
        OUT.write_text(out, encoding="utf-8")
        d = json.loads(out)
        print("VDS DB:", d.get("PATH"))
        for ad, v in sorted(d.get("combos", {}).items()):
            print(f"  {ad:24s} kind={str(v.get('kind')):12s} uye={len(v.get('uyeler', []))}")
    else:
        print("STDOUT BOS")
        print("RAW STDERR:", r.stderr[:500])
except Exception as e:
    print("HATA:", type(e).__name__, str(e)[:300])
