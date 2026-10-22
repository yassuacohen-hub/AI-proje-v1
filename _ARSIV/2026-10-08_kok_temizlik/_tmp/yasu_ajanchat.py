# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

print("=== ajan_chat.py subcommand + kapatma API ===")
L = open(r"c:\HUGINN~1\HUGINN~1\scripts\ajan_chat.py",
         encoding="utf-8", errors="replace").read().splitlines()
print("TOTAL", len(L))
for i, l in enumerate(L, 1):
    ll = l.lower()
    if "def " in l or "add_parser" in l or "guncelle" in ll \
       or "acik_sorulari" in ll or "yanit_alindi" in ll or "teslim_kontrol" in ll \
       or "cozum" in ll or "kapat" in ll:
        print(f"{i}: {l.strip()[:140]}")
