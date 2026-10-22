# -*- coding: utf-8 -*-
import io, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
R = r"c:\HUGINN~1\HUGINN~1"

for hub in ["hubs/PLAN_STRATEGY_HUB.md", "hubs/ADMIN_DASHBOARD_HUB.md"]:
    print("=" * 30, hub)
    try:
        L = io.open(f"{R}\\{hub}", encoding="utf-8").read().splitlines()
    except Exception as e:
        print("  OKUNAMADI:", e)
        continue
    print("  TOPLAM", len(L), "satir")
    for i, s in enumerate(L, 1):
        if s.startswith("#") or "Kapanan" in s or "API-V1-NETWORK" in s:
            print(f"  {i}: {s[:100]}")
