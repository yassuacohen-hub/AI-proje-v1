# -*- coding: utf-8 -*-
"""VDS'te .env dosyalarini bul, YALNIZ anahtar adi + DOLU/BOS yaz (D-380, D-376 salt-okunur). Deger asla yazilmaz."""
import glob
import os
import re

DESEN = re.compile(r"MAIL|SMTP|BREVO|SENDER|ADMIN_EMAIL", re.I)
yollar = []
for kok in (r"C:\Hugin_insights",):
    for d, alt, dosyalar in os.walk(kok):
        alt[:] = [a for a in alt if a not in ("node_modules", ".git", ".next", "__pycache__", ".venv", "venv")]
        for f in dosyalar:
            if f == ".env":
                yollar.append(os.path.join(d, f))
if not yollar:
    print("VDS: .env bulunamadi")
for p in yollar:
    print("DOSYA:", p)
    for ln in open(p, encoding="utf-8-sig", errors="replace"):
        ln = ln.strip()
        if "=" in ln and not ln.startswith("#"):
            k, _, v = ln.partition("=")
            if DESEN.search(k):
                print("  ", k.strip(), "DOLU" if v.strip().strip('"').strip("'") else "BOS")
