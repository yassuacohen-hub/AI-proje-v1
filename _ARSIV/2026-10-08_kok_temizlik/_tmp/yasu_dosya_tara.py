# -*- coding: utf-8 -*-
import pathlib, subprocess, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
KOK = pathlib.Path(r"c:\HUGINN~1\HUGINN~1")

def var(rel):
    return (KOK / rel).exists()

# NETWORK: kilitli dosyalar + test + frontend
print("=== API-V1-NETWORK-REPORT-01 dosyalari ===")
for f in ["src/company_master/api/routers/v1_network.py",
          "src/company_master/api/routers/v1/v1_network.py",
          "tests/test_api_v1_network.py",
          "web_app.py"]:
    print(f"  {var(f)}  {f}")

print("\n=== UI-SSR-NEXT-KUNYE-01 dosyalari ===")
for f in ["frontend/package.json", "frontend/next.config.mjs",
          "frontend/app/layout.tsx", "frontend/app/firma/[vkn]/page.tsx",
          "frontend/app/firma/firma.test.tsx"]:
    print(f"  {var(f)}  {f}")

print("\n=== ORCH-KODLAMA-TEMIZLIK-01 brief var mi ===")
print("  brief:", var("plans/brief_yasu_ORCH-KODLAMA-TEMIZLIK-01.md"))

print("\n=== ALTYAPI-REPO-TEMIZLIK-01 brief + _ARSIV ===")
print("  brief:", var("plans/brief_yasu_ALTYAPI-REPO-TEMIZLIK-01.md"))
print("  _ARSIV dir:", var("_ARSIV"))
