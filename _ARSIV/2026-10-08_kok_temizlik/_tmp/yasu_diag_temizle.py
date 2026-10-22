# -*- coding: utf-8 -*-
import os, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
F = r"C:\Huginn Data Projesi\Huginn Data Insights\frontend"
dosyalar = [
    r"app\firma\diag.test.tsx",
    r"app\firma\diag2.test.tsx",
    r"app\firma\diag3.test.tsx",
    r"app\firma\diag4.test.tsx",
    r"diag_link.mjs",
    r"diag_link.cjs",
]
for rel in dosyalar:
    p = os.path.join(F, rel)
    if os.path.exists(p):
        os.remove(p)
        print("SILINDI:", rel)
    else:
        print("zaten yok:", rel)
