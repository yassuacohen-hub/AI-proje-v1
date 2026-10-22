# -*- coding: utf-8 -*-
import pathlib, re, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
KOK = pathlib.Path(r"c:\HUGINN~1\HUGINN~1")

wa = (KOK / "web_app.py").read_text(encoding="utf-8", errors="replace").splitlines()
print("=== web_app.py: v1_network include / prefix ===")
for i, s in enumerate(wa, 1):
    if "v1_network" in s or ("include_router" in s and "v1" in s):
        print(f"  {i}: {s.strip()}")

print("\n=== _fetch_company_by_vkn gövdesi (84-108) ===")
net = (KOK / "src/company_master/api/routers/v1/v1_network.py").read_text(encoding="utf-8", errors="replace").splitlines()
for i in range(83, 108):
    if i < len(net):
        print(f"  {i+1}: {net[i]}")

print("\n=== require_api_key / _charge_module_credit imzasi ===")
for i, s in enumerate(wa, 1):
    if "def require_api_key" in s or "def _charge_module_credit" in s or "def get_engine" in s:
        print(f"  {i}: {s.strip()}")

print("\n=== mevcut v1 include_router blogu (prefix) ===")
for i, s in enumerate(wa, 1):
    if "include_router" in s and ("prefix" in s or "/api/v1" in s or "network" in s or "compan" in s):
        print(f"  {i}: {s.strip()}")
