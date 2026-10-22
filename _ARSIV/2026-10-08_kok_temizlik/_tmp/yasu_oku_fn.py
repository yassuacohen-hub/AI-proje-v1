# -*- coding: utf-8 -*-
"""chat.py kapat/oku/guncelle fonksiyon govdelerini yazdir."""
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
src = Path(r"c:\HUGINN~1\HUGINN~1\src\company_master\chat.py")
L = src.read_text(encoding="utf-8").splitlines()
hedef = ("def kapat", "def oku", "def guncelle")
for i, ln in enumerate(L):
    if any(ln.strip().startswith(h) for h in hedef):
        print(f"\n----- satir {i+1} -----")
        for j in range(i, min(i+45, len(L))):
            print(L[j])
        print("...")
