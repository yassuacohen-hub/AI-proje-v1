# -*- coding: utf-8 -*-
import sys, io
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, r"c:\HUGINN~1\HUGINN~1")
sys.path.insert(0, r"c:\HUGINN~1\HUGINN~1\scripts")

import importlib.util
spec = importlib.util.spec_from_file_location(
    "gk", r"c:\HUGINN~1\HUGINN~1\scripts\gorev_kutusu.py")
gk = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gk)

tid = "API-V1-NETWORK-REPORT-01"
print("hedefler:", [str(p) for p in gk._hafiza_hedefleri(tid)])
print("izi     :", [str(p) for p in gk._hafiza_izi(tid)])
print("GECTI" if gk._hafiza_izi(tid) else "KAPALI")

# hub son satirlar
L = io.open(r"c:\Huginn~1\Huginn~1\hubs\PLAN_STRATEGY_HUB.md",
            encoding="utf-8").read().splitlines()
print("hub toplam:", len(L))
for i, s in enumerate(L[-8:], len(L) - 7):
    print(f"  {i}: {s[:90]}")
