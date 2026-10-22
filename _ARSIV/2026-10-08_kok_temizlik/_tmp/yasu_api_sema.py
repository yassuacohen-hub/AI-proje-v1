# -*- coding: utf-8 -*-
import io, sys, re
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
R = r"C:\Huginn Data Projesi\Huginn Data Insights"

for f in ["src/company_master/api/routers/v1/companies.py",
          "src/company_master/api/routers/v1/fraud.py"]:
    print("=" * 25, f)
    L = io.open(f"{R}\\{f}", encoding="utf-8", errors="replace").read().splitlines()
    for i, s in enumerate(L, 1):
        if re.search(r"@(router|app)\.(get|post)", s) or "response_model" in s:
            print(f"  {i}: {s.strip()[:140]}")

print("=" * 25, "web_app include_router")
L = io.open(f"{R}\\web_app.py", encoding="utf-8", errors="replace").read().splitlines()
for i, s in enumerate(L, 1):
    if "include_router" in s:
        print(f"  {i}: {s.strip()[:140]}")
