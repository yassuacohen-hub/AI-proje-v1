# -*- coding: utf-8 -*-
"""Kademe kurali + chat kapatma mekanizmasi net okuma."""
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
BASE = Path(r"c:\HUGINN~1\HUGINN~1")

# 1) AGENTS.md'den kademe ilgili bolumler
ag = (BASE / "Huginn Data Insights" / "AGENTS.md")
print("=== AGENTS.md kademe bolumleri ===")
if ag.exists():
    L = ag.read_text(encoding="utf-8", errors="replace").splitlines()
    for i, s in enumerate(L):
        if re.search(r"kademe|Kademe|KADEME|kademe-1|kademe-2|yasu.*rol|rol.*yasu", s):
            print(f"  {i+1}: {s.strip()[:160]}")

# 2) chat.py teslim_kontrol_et + _mesaj_kontrol_et + kapat
print("\n=== chat.py kapatma mekanizmasi ===")
ch = (BASE / "src/company_master/chat.py")
if ch.exists():
    L = ch.read_text(encoding="utf-8", errors="replace").splitlines()
    yaz = False
    for i, s in enumerate(L):
        if re.search(r"def (teslim_kontrol_et|_mesaj_kontrol_et|acik_sorulari|kapat)\b", s):
            yaz = True
            print(f"--- {i+1} ---")
        if yaz:
            print(f"{i+1}: {s}")
            if s.strip().startswith("def ") and i > 0 and "---" in L[i-1] if False else False:
                pass
