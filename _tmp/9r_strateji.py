#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Round Robin vs Fallback karsilastirma raporu."""
import json
import sqlite3
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

DB = Path.home() / "AppData/Roaming/9router/db/data.sqlite"
con = sqlite3.connect(f"file:{DB.as_posix()}?mode=ro", uri=True)
con.row_factory = sqlite3.Row

row = con.execute("SELECT data FROM settings LIMIT 1").fetchone()
st = json.loads(row["data"]) if row and row["data"] else {}
cs = st.get("comboStrategies") or {}

print("=" * 70)
print("ROUND ROBIN vs FALLBACK — HANGISI SIZIN IÇIN IYI?")
print("=" * 70)
print()
print(f"Guncel comboStrategy: {st.get('comboStrategy')}")
print(f"Guncel stickyLimit:   {st.get('comboStickyRoundRobinLimit')}")
print()

print("=" * 70)
print("1. FALLBACK (Guncel — Tavsiye)")
print("=" * 70)
print("""
Nasıl çalışır:
  1. cc/claude-sonnet-5-5 (en üstte) denenecek
  2. 429/hata verirse -> sıradaki modele geçilir
  3. Hiçbiri çalışmazsa -> hata döner

Avantaj:
  + cc/claude-sonnet-5-5 HER ZAMAN önce denenecek (senin istediğin)
  + 429 aldığında otomatik sıradakine geçer (Claude Code durmaz)
  + En güçlü model öncelikli

Dezavantaj:
  - Tek model çok istek alabilir (diğerleri bekler)
""")

print("=" * 70)
print("2. ROUND ROBIN")
print("=" * 70)
print("""
Nasıl çalışır:
  1. İstek 1 -> cc/claude-sonnet-5-5
  2. İstek 2 -> sıradaki model
  3. İstek 3 -> sıradaki model
  4. Döngüye döner

Avantaj:
  + Tüm modeller eşit paylaşılır (load balancing)
  - Tek modele baskı yok

Dezavantaj:
  - cc/claude-sonnet-5-5 her istekte üstte kalmaz
  - 429 alan modele de istek gider (zaman kaybı)
  - Senin "en üstte olsun" isteği bozulur
""")

print("=" * 70)
print("3. KARISIK (Fallback + Sticky Round Robin)")
print("=" * 70)
print("""
Guncel ayar: fallback + stickyLimit=2

Anlamı:
  - cc/claude-sonnet-5-5 önce denenecek
  - Aynı model 2 kez üst üste denenecek (sticky)
  - Sonra sıradakine geçilir

Bu, senin durumunda en iyisi çünkü:
  + cc/claude-sonnet-5-5 öncelikli
  + 429'dan sonra 2 kez daha denenir (geçici hata olabilir)
  + Sonra otomatik sıradakine geçer
""")

print("=" * 70)
print("SONUC: Sizin icin FALLBACK daha iyi")
print("=" * 70)
print("""
Neden?
  1. cc/claude-sonnet-5-5 her zaman en üstte (senin talibin)
  2. 429 rate limit aldığında otomatik geçiş var
  3. Claude Code durmadan çalışmaya devam eder

Round Robin seçersen: cc/claude-sonnet-5-5 her istekte üstte kalmaz,
429 alan modele de istek gider, zaman kaybı olur.

Tavsiye: Fallback'i koru, stickyLimit'i 2'den 3'e çıkarabilirsin
(429'dan sonra 3 kez denenir, sonra geçilir).
""")

con.close()
