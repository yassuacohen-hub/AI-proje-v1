# -*- coding: utf-8 -*-
"""Defterdeki tum bozuk satirlari listele (test ilk hatada duruyor)."""
import sys
sys.path.insert(0, r"c:\Huginn Data Projesi\Huginn Data Insights\scripts")
import bulgu_defteri as bd
veri = bd._veri_satirlari(bd.DEFLER)
for s in veri:
    a = [x.strip() for x in s.split("|")]
    neden = []
    if len(a) != 6: neden.append(f"alan={len(a)}")
    if len(a) > 2 and a[2] not in bd.ROLLER: neden.append(f"rol={a[2]}")
    if len(a) > 3 and a[3] not in bd.RENKLER.values(): neden.append(f"renk={a[3]}")
    if len(a) > 5 and not a[5]: neden.append("karar bos")
    if neden: print(neden, "||", s[:90])
print("islenmemis:", bd.islenmemis(bd.DEFLER))
