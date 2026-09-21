#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""D-185: DASH-UX-02a bekleyen tetigini v1 brifine gunceller (pre-split talimat -> v1)."""
import sys
from pathlib import Path

root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root))

from src.company_master.orchestrator import trigger

# Eski bekleyen tetigini al ve cikart
tetikler = trigger._tetikleri_oku("utku")
bulundu = False
yeni_tetikler = []

for t in tetikler:
    if t.get("task_id") == "DASH-UX-02a" and t.get("durum") == "bekliyor":
        bulundu = True
        # Yeni talimatla yenisini ekle (eski silip yenisini yazacak)
        continue
    yeni_tetikler.append(t)

if bulundu:
    trigger._tetikleri_yaz(yeni_tetikler, "utku")
    # Yeni tetigi ekle (v1 talimatı ile)
    talimat_v1 = (
        "DASH-UX-02a.v1: admin_sistem.py yaz, tabs/__init__.py'ye DOKUNMA. "
        "K1 kalibrasyonu burada tanimla (02b'de yeniden kullanilacak). "
        "SECTIONS kaydi v2'de (MENUTREE bitince). Brif: plans/brief_utku_DASH-UX-02a-v1.md"
    )
    trigger.tetik_ekle("DASH-UX-02a", "utku", talimat_v1)
    print("[OK] DASH-UX-02a tetigi v1 brifine guncellendi")
else:
    print("[ATLA] Bekleyen DASH-UX-02a tetigi bulunamadi")
