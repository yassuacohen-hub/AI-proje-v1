# -*- coding: utf-8 -*-
"""Sosyal adres doluluğu — kaç firmanın LinkedIn/Instagram/Facebook/Twitter adresi var?

Kaynak: source_records.raw_payload->>'sosyal_medya' (OSTİM detay sayfası, K-2: ayrı kolon).
Ölçüm 2026-10-03: 5016 kayıt dolu görünür ama HEPSİ OSTİM'in kendi hesapları
(sayfa altbilgisi kazınmış) → gerçek firma adresi 0. ``gercek_*`` sütunları ostim'i eler.
Kullanım: python scripts/sosyal_adres_olc.py
"""
from __future__ import annotations

import io
import sys

sys.path.insert(0, "src")
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

from sqlalchemy import text
from company_master.db.connection import get_engine

AGLAR = ("linkedin", "instagram", "facebook", "twitter")

SQL = """
SELECT
  COUNT(*)                                                           AS firma,
  COUNT(sr.raw_payload->'sosyal_medya')                              AS payload_var,
  COUNT(*) FILTER (WHERE sr.raw_payload->'sosyal_medya' <> '{}'::jsonb) AS en_az_bir,
  %s
FROM companies c
LEFT JOIN source_records sr ON sr.source_record_id = c.source_record_id
""" % ",\n  ".join(
    f"COUNT(sr.raw_payload->'sosyal_medya'->>'{a}') AS {a},\n  "
    f"COUNT(*) FILTER (WHERE COALESCE(sr.raw_payload->'sosyal_medya'->>'{a}','') <> ''"
    f" AND sr.raw_payload->'sosyal_medya'->>'{a}' NOT ILIKE '%%ostim%%') AS gercek_{a}"
    for a in AGLAR
)


def main() -> int:
    with get_engine().connect() as conn:
        r = conn.execute(text(SQL)).mappings().one()
    toplam = r["firma"] or 1
    print(f"{'alan':<18}{'adet':>8}{'%':>8}")
    for k in ("firma", "payload_var", "en_az_bir", *AGLAR, *(f"gercek_{a}" for a in AGLAR)):
        print(f"{k:<18}{r[k]:>8}{100 * r[k] / toplam:>7.1f}%")
    return 0


if __name__ == "__main__":
    sys.exit(main())
