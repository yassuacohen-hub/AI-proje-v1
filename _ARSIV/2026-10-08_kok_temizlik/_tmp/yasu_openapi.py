# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# 1) web_app.py'de network router kaydi (prefix)
import re, pathlib
web = pathlib.Path(r"c:\HUGINN~1\HUGINN~1\web_app.py").read_text(encoding="utf-8", errors="replace")
print("=== web_app.py network include_router ===")
for i, l in enumerate(web.splitlines(), 1):
    if "network_router" in l or "v1_network" in l or ("include_router" in l and "network" in l.lower()):
        print(f"{i}: {l.strip()}")

print("\n=== web_app.py 40-60 satir (router mount) ===")
WL = web.splitlines()
for i in range(40, min(60, len(WL))):
    print(f"{i+1}: {WL[i]}")

print("\n=== web_app.py 470-495 satir (wrapper?) ===")
for i in range(470, min(495, len(WL))):
    print(f"{i+1}: {WL[i]}")
print("\n=== OpenAPI network paths ===")
try:
    from fastapi.testclient import TestClient
    import web_app
    c = TestClient(web_app.app)
    for p in sorted(c.app.openapi().get("paths", {})):
        if "network" in p.lower() or "full" in p.lower() or "report" in p.lower():
            print(p)
    print("\n--- ornek vkn path kaliplari (companies/*) ---")
    for p in sorted(c.app.openapi().get("paths", {})):
        if p.startswith("/companies"):
            print(p)
except Exception as e:
    print("OPENAPI HATA:", repr(e))
