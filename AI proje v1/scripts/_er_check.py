# -*- coding: utf-8 -*-
"""entity_resolution tablosu yapisini ve dedup etkisini inceler."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from sqlalchemy import inspect, text
from company_master.db.connection import get_engine

engine = get_engine()
insp = inspect(engine)

print("=== entity_resolution kolonlari ===")
for c in insp.get_columns("entity_resolution"):
    print(f"  {c['name']}: {c['type']}")

print("\n=== Ornek satirlar ===")
with engine.connect() as conn:
    rows = conn.execute(text("SELECT * FROM entity_resolution LIMIT 5")).mappings().all()
    for r in rows:
        print(" ", dict(r))

print("\n=== Dedup etkisi: kazanan/kaybeden firmalarin entity_resolution durumu ===")
# Unvan bazli duplicate gruplarini yeniden hesapla (dedup_report ile ayni mantik)
import re

def norm_name(s: str) -> str:
    if not s:
        return ""
    s = s.upper().strip()
    tr = str.maketrans({'İ': 'I', 'I': 'I', 'Ş': 'S', 'Ğ': 'G', 'Ü': 'U', 'Ö': 'O', 'Ç': 'C', 'ı': 'I'})
    s = s.translate(tr)
    s = re.sub(r'[^A-Z0-9 ]', ' ', s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s

with engine.connect() as conn:
    rows = conn.execute(text("""
        SELECT company_id, legal_name, tax_number, vergi_no, data_quality_score
        FROM companies
    """)).mappings().all()

from collections import defaultdict
name_map = defaultdict(list)
for r in rows:
    n = norm_name(r.get('legal_name') or '')
    if n:
        name_map[n].append(dict(r))

groups = [rs for rs in name_map.values() if len(rs) > 1]
losers = []
for rs in groups:
    winner = max(rs, key=lambda r: (r['data_quality_score'] or 0))
    losers.extend(r for r in rs if r is not winner)

print(f"Duplicate grup: {len(groups)}, kaybeden firma: {len(losers)}")

if losers:
    lids = [str(r['company_id']) for r in losers]
    with engine.connect() as conn:
        cnt = conn.execute(text(
            "SELECT COUNT(*) FROM entity_resolution WHERE company_id = ANY(:ids)"
        ), {"ids": lids}).scalar()
        print(f"Kaybeden firmalara bagli entity_resolution satiri: {cnt}")

    # VKN bazli tasfiye kayitlari da var mi?
    tasfiye = [r for r in rows if 'TASF' in (r.get('legal_name') or '').upper()]
    print(f"Tasfiye kaydi iceren firma: {len(tasfiye)}")
