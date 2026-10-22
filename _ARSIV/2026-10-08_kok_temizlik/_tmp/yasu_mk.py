# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
BASE = r"c:\HUGINN~1\HUGINN~1"

src = open(BASE + r"\scripts\gorev_kutusu.py", encoding="utf-8").read().splitlines()
# def _mesaj_kontrol_et ve cmd_teslim govdelerini yazdir
start = None
for i, s in enumerate(src):
    if "def _mesaj_kontrol_et" in s:
        start = i
        break
if start is not None:
    print("=== _mesaj_kontrol_et ===")
    for j in range(start, min(start + 45, len(src))):
        print(j + 1, src[j])
else:
    print("_mesaj_kontrol_et tanimi bulunamadi")
