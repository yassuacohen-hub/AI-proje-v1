# -*- coding: utf-8 -*-
import sys, io, re
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
R = r"C:\Huginn Data Projesi\Huginn Data Insights"

def read(path):
    try:
        with io.open(path, encoding="utf-8", errors="replace") as f:
            return f.read()
    except Exception as e:
        return f"<Error reading {path}: {e}>"

hub_md = read(f"{R}\\hubs\\PLAN_STRATEGY_HUB.md")
# Faz B tanımlarını bul (satır başında 'Faz B' olarak)
print("--- PLAN_STRATEGY_HUB md'den kısa snippet ---")
for line in hub_md.splitlines():
    if re.search(r"Faz\s*B", line, re.I):
        print(line.strip())
        # birkaç sonraki satırları yazdır
        pass
print("\n--- Faz B'nin orijinal değeri (belki metin şeması) ---")
print(hub_md[:1500])
