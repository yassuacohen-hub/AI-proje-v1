# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
L = open(r"c:\HUGINN~1\HUGINN~1\scripts\gorev_kutusu.py",
         encoding="utf-8", errors="replace").read().splitlines()
print("TOTAL", len(L))
for i, l in enumerate(L, 1):
    ll = l.lower()
    if "d-210" in ll or "acik sorular" in ll or "_mesaj_kontrol" in ll \
       or "def _soru" in ll or "kapanmamis" in ll or "kapanmamış" in ll \
       or "yanit_alindi" in ll or "sorulari" in ll or "acik_sorular" in ll:
        print(f"{i}: {l.strip()[:150]}")
