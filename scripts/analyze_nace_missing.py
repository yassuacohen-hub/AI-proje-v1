#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""NACE'siz kayitlarin analizi: hangi unvanlar eslesmedi?"""
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "ostim" / "firmalar_full.jsonl"

records = []
with open(DATA, encoding="utf-8") as f:
    for line in f:
        if line.strip():
            records.append(json.loads(line))

bos = [r for r in records if not r.get('nace_code')]
dolu = [r for r in records if r.get('nace_code')]
print(f"Toplam: {len(records)} | NACE dolu: {len(dolu)} | NACE yok: {len(bos)}")

# NACE'siz kayitlarin sektor dagilimi
sektor_dag = Counter((r.get('sektor') or 'SEKTORSUZ') for r in bos)
print("\nNACE'siz kayitlarin sektor dagilimi (ilk 10):")
for s, n in sektor_dag.most_common(10):
    print(f"  {s}: {n}")

# NACE'siz kayitlarda unvan durumu
bos_unvansiz = sum(1 for r in bos if not (r.get('unvan') or '').strip())
print(f"\nNACE'siz ve unvansiz kayit: {bos_unvansiz}")

# Ornek unvanlar (bos olmayanlardan)
ornek = [(r.get('unvan') or '')[:70] for r in bos if (r.get('unvan') or '').strip()][:12]
print("\nNACE'siz ornek unvanlar:")
for u in ornek:
    print(f"  - {u}")

# NACE'siz kayitlarin slug/adres durumuna bak (tekrar scrape icin)
slug_var = sum(1 for r in bos if r.get('slug'))
print(f"\nNACE'siz ve slug'i olan kayit: {slug_var}/{len(bos)}")