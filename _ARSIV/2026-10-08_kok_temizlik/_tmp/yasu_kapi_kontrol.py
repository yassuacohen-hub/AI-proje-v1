# -*- coding: utf-8 -*-
"""Teslim oncesi kapi kontrolu: acik chat, bulgu defteri, hub hafiza izi."""
import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, "src")
from pathlib import Path
from company_master import chat

BASE = Path(r"c:\HUGINN~1\HUGINN~1")
tid = "VERI-RAPIDAPI-OSINT-ISTEMCI-01"

# 1) acik chat kaydi
acik = [(i, k.get("durum")) for i, k in enumerate(chat.oku(tid)) if k.get("durum") == "acik"]
print("1) acik chat kayit:", acik if acik else "YOK (OK)")

# 2) bulgu defteri
bd = BASE / "data/orchestrator/bulgu_defteri.md"
bd_metin = bd.read_text(encoding="utf-8", errors="replace") if bd.exists() else ""
print("2) bulgu defteri kaydi:", "VAR" if tid in bd_metin else "YOK (ENGELLER)")

# 3) hub hafiza izi
hub_dir = BASE / "hubs"
hub_metin = ""
if hub_dir.is_dir():
    hub_metin = "".join(h.read_text(encoding="utf-8", errors="replace") for h in sorted(hub_dir.glob("*.md")))
ssot = BASE / "Huginn Data Insights/AGENTS.md"
ssot_metin = ssot.read_text(encoding="utf-8", errors="replace") if ssot.exists() else ""
print("3) hub izi:", "VAR" if tid in hub_metin else "YOK", "| SSOT izi:", "VAR" if tid in ssot_metin else "YOK")

# 4) kilitli dosyalar / cikti
cikti = [
    "docs/RAPIDAPI_OSINT_SOZLESME.md",
    "src/company_master/engine/rapidapi_osint.py",
    "tests/test_rapidapi_osint.py",
    "data/orchestrator/VERI-RAPIDAPI-OSINT-ISTEMCI-01_rapor_2026-10-12_yasu.md",
]
print("4) cikti dosyalari:")
for c in cikti:
    print("   ", "OK" if (BASE / c).exists() else "YOK", c)
