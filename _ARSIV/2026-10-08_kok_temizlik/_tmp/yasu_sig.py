# -*- coding: utf-8 -*-
import sys, pathlib, re
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = pathlib.Path(r"c:\HUGINN~1\HUGINN~1")

print("=== A) web_app.py network router KAYDI ===")
wa = (ROOT / "web_app.py").read_text(encoding="utf-8", errors="replace")
for i, ln in enumerate(wa.splitlines(), 1):
    if "network_router" in ln:
        print(f"  {i}: {ln.strip()[:100]}")
# prefix + api_v1 dagitimi
print("  --- include_router(network ---")
for i, ln in enumerate(wa.splitlines(), 1):
    if "include_router" in ln and "network" in ln.lower():
        print(f"  {i}: {ln.strip()}")

print("\n=== B) test_v1_companies.py TAM (kalip) ===")
print((ROOT / "tests/test_v1_companies.py").read_text(encoding="utf-8", errors="replace"))

print("=== C) v1_network route + model + dep imzalari ===")
vf = (ROOT / "src/company_master/api/routers/v1/v1_network.py").read_text(encoding="utf-8", errors="replace")
for i, ln in enumerate(vf.splitlines(), 1):
    s = ln.strip()
    if s.startswith("@router") or s.startswith("class ") or s.startswith("router") or "Depends(" in s or s.startswith("async def ") or s.startswith("def ") or s.startswith("APIRouter"):
        print(f"  {i}: {s[:100]}")
