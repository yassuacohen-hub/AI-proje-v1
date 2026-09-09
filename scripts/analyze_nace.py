#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""NACE eksikleri analizi — 1266 sektörsüz firma."""
import sys, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

# ASO data ile NACE eksiklerini analiz et
aso_path = ROOT / "data" / "aso" / "aso_full.jsonl"
if not aso_path.exists():
    print("ASO data bulunamadı")
    sys.exit(1)

records = []
with open(aso_path, "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if line:
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                pass

print(f"Toplam ASO kaydı: {len(records)}")

# NACE kodu olan / olmayan
has_nace = sum(1 for r in records if r.get("naceKod"))
no_nace = sum(1 for r in records if not r.get("naceKod"))
print(f"NACE kodu olan: {has_nace}")
print(f"NACE kodu olmayan: {no_nace}")

# NACE detaylı dağılım
from collections import Counter
nace_dist = Counter(r.get("naceKod", "") for r in records if r.get("naceKod"))
print("\nEn yaygın NACE kodları:")
for kod, sayi in nace_dist.most_common(20):
    print(f"  {kod}: {sayi}")

# Meslek grubu dağılımı
meslek_dist = Counter(r.get("meslekGrubu", "") for r in records if r.get("meslekGrubu"))
print("\nMeslek grupları:")
for grp, sayi in meslek_dist.most_common(15):
    print(f"  {grp}: {sayi}")
