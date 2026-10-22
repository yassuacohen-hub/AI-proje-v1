# -*- coding: utf-8 -*-
"""Utku'nun 5 aktif görevini yasu ve salih'e dagitmak icin gorev_at.py komutlarini hazirla."""
import json
import sys
import os
from pathlib import Path

TB = "Huginn Data Insights/data/orchestrator/task_board.json"

with open(TB, "r", encoding="utf-8") as f:
    data = json.load(f)

# Utku'nun aktif gorevleri
utku_gorevleri = [g for g in data if g.get("sahip") == "utku" and g.get("durum") not in ("done", "archive", "tamamlandi", "iptal")]

print(f"Utku'nun devredilecek AKTIF gorev sayisi: {len(utku_gorevleri)}")
print()

# Dagilma: %60 yasu, %40 salih
yasu_sayisi = int(len(utku_gorevleri) * 0.6)
salih_sayisi = len(utku_gorevleri) - yasu_sayisi

print(f"Dagilma: Yasu = {yasu_sayisi} (%60), Salih = {salih_sayisi} (%40)")
print()

# Her bir gorev icin gorev_at.py komutunu hazirla
for i, gorev in enumerate(utku_gorevleri):
    task_id = gorev.get("task_id")
    baslik = gorev.get("baslik", "")
    
    # Hedef sahibi belirle
    hedef_sahip = "yasu" if i < yasu_sayisi else "salih"
    
    # Komut hazirla
    komut = f"python3 scripts/gorev_at.py at --task-id {task_id} --baslik '{baslik}' --sahip {hedef_sahip} --talimat 'Utku'nun {len(utku_gorevleri)} aktif gorevini {hedef_sahip} adina devrediyor.'"
    
    print(f"Gorev {i+1}: {task_id}")
    print(f"  Baslik: {baslik[:60]}...")
    print(f"  Hedef Sahip: {hedef_sahip}")
    print(f"  Komut: {komut}")
    print()