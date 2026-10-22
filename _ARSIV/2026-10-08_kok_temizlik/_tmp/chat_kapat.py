# -*- coding: utf-8 -*-
"""VERI-TOBB-HAVUZ-SEMA-01'in ilerleme-notu kayitlarini kapatir (soru degil)."""
import sys
sys.path.insert(0, "src")
from company_master import chat

TASK = "VERI-TOBB-HAVUZ-SEMA-01"
KARAR = "Ilerleme notuydu, soru degil - teslim icin kapatildi (ihsan)"

for i in range(8):
    r = chat.kapat(TASK, i, KARAR)
    print(i, "OK" if r else "FAIL")

satirlar = chat.oku(task_id=TASK)
print("kalan acik:", sum(1 for s in satirlar if s.get("durum") == "acik"))
