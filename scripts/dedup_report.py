# -*- coding: utf-8 -*-
"""P4-5: Duplicate analizi (salt okunur rapor).

Tespit stratejileri:
  1. VKN bazli: ayni tax_number/vergi_no'ya sahip birden fazla firma
  2. Unvan bazli: normalize edilmis legal_name ayni olan firmalar
  3. Web bazli: ayni website_domain'e sahip firmalar
  4. source_record bazli: ayni kaynaktan ayni orijinal kayit id
"""
from __future__ import annotations

import re
import sys
from collections import Counter, defaultdict

from sqlalchemy import text

ROOT = __import__('pathlib').Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from company_master.db.connection import get_engine


def norm_name(s: str) -> str:
    """Unvani karsilastirma icin normalize et: buyuk harf, tr->ascii, noktalama temizle."""
    if not s:
        return ""
    s = s.upper().strip()
    tr = str.maketrans({'İ': 'I', 'I': 'I', 'Ş': 'S', 'Ğ': 'G', 'Ü': 'U', 'Ö': 'O', 'Ç': 'C', 'ı': 'I'})
    s = s.translate(tr)
    s = re.sub(r'[^A-Z0-9 ]', ' ', s)
    s = re.sub(r'\s+', ' ', s).strip()
    # Sirket turu eklerini at
    for suffix in (' ANONIM SIRKETI', ' ANONIM SIRKETI ', ' LIMITED SIRKETI', ' LTD STI', ' A S', ' AS'):
        if s.endswith(suffix.strip()):
            s = s[: -len(suffix.strip())].strip()
    return s


def main() -> None:
    engine = get_engine()
    with engine.connect() as conn:
        rows = conn.execute(text("""
            SELECT company_id, legal_name, trade_name, tax_number, vergi_no,
                   website_domain, primary_email, primary_phone,
                   data_quality_score, is_ankara, is_osb_member
            FROM companies
        """)).mappings().all()

    print(f"Toplam firma: {len(rows)}")

    # 1) VKN bazli duplicate
    vkn_map: dict[str, list] = defaultdict(list)
    for r in rows:
        v = (r.get('tax_number') or r.get('vergi_no') or '').strip()
        if v and v not in ('0', '0000000000'):
            vkn_map[v].append(r)
    vkn_dups = {v: rs for v, rs in vkn_map.items() if len(rs) > 1}
    print(f"\n[1] VKN DUPLICATE: {len(vkn_dups)} VKN degeri coklu firmada")
    for v, rs in list(vkn_dups.items())[:10]:
        names = [f"{r['legal_name'][:40]} ({str(r['company_id'])[:8]})" for r in rs]
        print(f"    VKN {v}: {len(rs)} firma -> {names}")

    # 2) Unvan bazli duplicate (normalize edilmis)
    name_map: dict[str, list] = defaultdict(list)
    for r in rows:
        n = norm_name(r.get('legal_name') or '')
        if n:
            name_map[n].append(r)
    name_dups = {n: rs for n, rs in name_map.items() if len(rs) > 1}
    print(f"\n[2] UNVAN DUPLICATE (normalize): {len(name_dups)} unvan coklu firmada")
    total_dup_rows = sum(len(rs) for rs in name_dups.values())
    print(f"    Etkilenen toplam satir: {total_dup_rows} (silinebilecek: {total_dup_rows - len(name_dups)})")
    for n, rs in list(name_dups.items())[:10]:
        ids = [f"{str(r['company_id'])[:8]}(skor={r['data_quality_score']})" for r in rs]
        print(f"    '{n[:45]}': {len(rs)} -> {ids}")

    # 3) Web bazli
    web_map: dict[str, list] = defaultdict(list)
    for r in rows:
        w = (r.get('website_domain') or '').strip().lower().rstrip('/')
        if w and w not in ('', 'http://', 'https://'):
            web_map[w].append(r)
    web_dups = {w: rs for w, rs in web_map.items() if len(rs) > 1}
    print(f"\n[3] WEB DUPLICATE: {len(web_dups)} domain coklu firmada")
    for w, rs in list(web_dups.items())[:5]:
        print(f"    {w}: {len(rs)} firma")

    # 4) source_records bazli (ayni kaynak+orijinal id)
    with engine.connect() as conn:
        sr_dups = conn.execute(text("""
            SELECT s.source_name, sr.source_record_id, COUNT(DISTINCT c.company_id) AS cnt
            FROM source_records sr
            JOIN sources s ON sr.source_id = s.source_id
            JOIN companies c ON c.source_record_id = sr.source_record_id
            GROUP BY 1, 2
            HAVING COUNT(DISTINCT c.company_id) > 1
            LIMIT 10
        """)).fetchall()
    print(f"\n[4] KAYNAK KAYIDI COKLU FIRMA: {len(sr_dups)} ornek")
    for sname, srid, cnt in sr_dups:
        print(f"    {sname}/{str(srid)[:30]}: {cnt} firma")

    # Ozet
    print("\n=== OZET ===")
    print(f"  VKN duplicate grubu: {len(vkn_dups)}")
    print(f"  Unvan duplicate grubu: {len(name_dups)}")
    print(f"  Web duplicate grubu: {len(web_dups)}")
    print(f"  Unvan dup. nedeniyle silinebilecek satir: {max(0, total_dup_rows - len(name_dups))}")


if __name__ == "__main__":
    main()
