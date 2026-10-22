# -*- coding: utf-8 -*-
"""MD belgesinin baslik iskeletini + kritik kavram haritasini cikar (salt okuma)."""
import re, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
p = Path("yedekler/Ticari İstihbarat Odaklı Veri Sağlayıcıları yol haritası ve öneriler.md")
t = p.read_text(encoding="utf-8", errors="replace")
sat = t.splitlines()
print("TOPLAM SATIR:", len(sat), "| KARAKTER:", len(t))
out = []
for i, s in enumerate(sat, 1):
    x = s.strip()
    if not x:
        continue
    if (re.match(r"^#{1,6} ", x)
            or re.match(r"^\*\*[^*]{4,}\*\*\s*$", x)
            or re.match(r"^\*\*[^\w\s]", x)
            or re.match(r"^\*\*\d+\.", x)):
        out.append(f"{i:5d} | {x[:120]}")
print("BASLIK SAYISI:", len(out))
print("\n".join(out))
print("\n=== KAVRAM SAYIMLARI ===")
for k in ["kap_rss_monitor", "yfinance", "EVDS", "TÜİK", "PostGIS", "Neo4j", "Redis",
          "Paywall", "Kredi", "SSE", "Shadcn", "ticariradar", "sirketarama",
          "firmaistihbarat", "Celery", "Escrow", "Findeks", "quarantine", "job_signals",
          "Master Context", "Katman 0", "SLA", "19,49", "48,73", "50.000", "200 USD", "150 ₺"]:
    print(f"{k:18s}: {len(re.findall(re.escape(k), t, re.IGNORECASE))}")
