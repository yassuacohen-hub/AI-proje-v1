#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""9Router son durum ozeti."""
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

p = Path("_tmp/9r_sonuc.json")
raw = p.read_text(encoding="utf-8", errors="replace")
start = raw.find("{")
if start < 0:
    print("JSON YOK, ham cikti ilk 2000:")
    print(raw[:2000])
    sys.exit(1)

d = json.loads(raw[start:])
s = d["saglik"]
print("=" * 70)
print("9ROUTER SAGLIK (post-temizlik)")
print("=" * 70)
print(f"  Aktif    : {s['aktif']}")
print(f"  Inaktif  : {s['inaktif']}")
print(f"  Sorunlu  : {s['sorunlu_sayisi']}")

print()
print("EN IYI 8 PROVIDER (skora gore):")
for x in d["skorlar"][:8]:
    print(f"  {x['provider']:<22} skor={x['toplam']:>5.1f}  saglik={x['saglik']:>3}  hiz={x['hiz']:>3}  maliyet={x['maliyet']:>3}")

print()
print(f"ANOMALI SAYISI: {len(d['anomaliler'])}")
for a in d["anomaliler"]:
    print(f"  [{a['oncelik']:<6}] {a['provider']:<20} {', '.join(a['nedenler'])}")

print()
print("COMBO STRATEJISI:", d["combo_istatistik"]["settings"])
print("ORT LATENCY:", d["combo_istatistik"]["requestDetails"]["ortalama_latency_ms"], "ms")
print("STATUS:", d["combo_istatistik"]["requestDetails"]["status_dagilimi"])
