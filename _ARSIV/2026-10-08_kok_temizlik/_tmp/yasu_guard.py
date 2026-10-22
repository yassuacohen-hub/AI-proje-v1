# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# SECTIONS kaydi: musteri_odeme/musteri_kredi zaten eklenmis mi?
init = open(r"c:\HUGINN~1\HUGINN~1\web_dashboard\tabs\__init__.py", encoding="utf-8").read()
L = init.splitlines()
for i, l in enumerate(L, 1):
    if "musteri_odeme" in l or "musteri_kredi" in l or "render_odemeler" in l or "render_krediler" in l or "render_ayarlar" in l:
        print(f"{i}: {l.strip()[:110]}")

print("=== MODUL IMPORT KONTROLU ===")
import re
for f in ["web_dashboard/tabs/musteri_odeme.py", "web_dashboard/tabs/musteri_kredi.py"]:
    t = open(r"c:\HUGINN~1\HUGINN~1" + "/" + f, encoding="utf-8").read()
    L2 = t.splitlines()
    # key onekleri + requests + st.info (bos DB)
    keys = [l.strip() for l in L2 if re.search(r"key=|st\.info|requests|get_engine|Section|PageSection|kpi_karti", l)]
    print(f"\n--- {f} ({len(L2)} satir) ---")
    for k in keys[:25]:
        print("  ", k[:100])