# -*- coding: utf-8 -*-
"""P4-4/P4-1: Set-based kalite skoru yeniden hesaplama (tek sorgu).

Eski recalc (quality_recalc.py) satir satir UPDATE yapiyordu ve
9.227 kayitta statement timeout'a dusuyordu. Bu script formulu
tek bir UPDATE ile uygular (SQLite/PostgreSQL uyumlu).

Formul (quality_recalc._score ile ayni):
  VKN 15 + adres 15 + tel 15 + e-posta 15 + web 10 + NACE 15 + parsel 10 + ticaret adi 5
"""
from __future__ import annotations

import sys
from pathlib import Path

from sqlalchemy import text

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from company_master.db.connection import get_engine

SCORE_SQL = text("""
    UPDATE companies
    SET data_quality_score = LEAST(
        (CASE WHEN COALESCE(tax_number, vergi_no, '') <> '' THEN 15 ELSE 0 END)
      + (CASE WHEN COALESCE(adres, '') <> '' THEN 15 ELSE 0 END)
      + (CASE WHEN COALESCE(primary_phone, '') <> '' THEN 15 ELSE 0 END)
      + (CASE WHEN COALESCE(primary_email, '') <> '' THEN 15 ELSE 0 END)
      + (CASE WHEN COALESCE(website_domain, web_sitesi, '') <> '' THEN 10 ELSE 0 END)
      + (CASE WHEN COALESCE(nace_code, '') <> '' THEN 15 ELSE 0 END)
      + (CASE WHEN COALESCE(osb_parsel, '') <> '' THEN 10 ELSE 0 END)
      + (CASE WHEN COALESCE(trade_name, '') <> '' THEN 5 ELSE 0 END)
    , 100.0)
""")


def main() -> None:
    engine = get_engine()
    with engine.connect() as conn:
        # Satir-satir timeout'u asmak icin oturum timeout'unu yukselt
        try:
            conn.execute(text("SET statement_timeout = 300000"))  # 5 dk
        except Exception:
            pass  # SQLite desteklemez

        res = conn.execute(SCORE_SQL)
        conn.commit()
        print(f"Guncellenen satir: {res.rowcount}")

        avg = conn.execute(text(
            "SELECT AVG(data_quality_score) FROM companies WHERE is_ankara = TRUE"
        )).scalar()
        print(f"Ortalama kalite skoru: {avg:.2f}")

        dist = conn.execute(text("""
            SELECT CASE
                WHEN data_quality_score >= 80 THEN '80-100'
                WHEN data_quality_score >= 60 THEN '60-79'
                WHEN data_quality_score >= 40 THEN '40-59'
                WHEN data_quality_score >= 20 THEN '20-39'
                ELSE '0-19'
            END as bucket, COUNT(*) as cnt
            FROM companies WHERE is_ankara = TRUE
            GROUP BY 1 ORDER BY 1 DESC
        """)).fetchall()
        print("Skor Dagilimi:")
        for bucket, cnt in dist:
            print(f"  {bucket}: {cnt} firma")


if __name__ == "__main__":
    main()
