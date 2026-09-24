# -*- coding: utf-8 -*-
"""Kalite skoru recalculation scripti.

Tum firmalar icin kalite skorunu yeniden hesaplar ve DB'ye yazar.
SQLite/PostgreSQL uyumlu.
"""
from __future__ import annotations

from sqlalchemy import text
from company_master.db.connection import get_engine


def _score(row: dict) -> float:
    """Kalite skoru formulu (0-100)."""
    score = 0.0
    # VKN (tax_number veya vergi_no) - 15 puan
    vkn = row.get("tax_number") or row.get("vergi_no") or ""
    if vkn and vkn.strip():
        score += 15
    # Adres - 15 puan
    adres = row.get("adres") or ""
    if adres and adres.strip():
        score += 15
    # Telefon - 15 puan
    phone = row.get("primary_phone") or ""
    if phone and phone.strip():
        score += 15
    # E-posta - 15 puan
    email = row.get("primary_email") or ""
    if email and email.strip():
        score += 15
    # Web sitesi - 10 puan
    web = row.get("website_domain") or row.get("web_sitesi") or ""
    if web and web.strip():
        score += 10
    # NACE kodu - 15 puan
    nace = row.get("nace_code") or ""
    if nace and nace.strip():
        score += 15
    # OSB parsel - 10 puan
    parsel = row.get("osb_parsel") or ""
    if parsel and parsel.strip():
        score += 10
    # Ticaret unvani - 5 puan
    trade = row.get("trade_name") or ""
    if trade and trade.strip():
        score += 5
    return round(min(score, 100.0), 1)


def recalc_quality_scores() -> int:
    """Tum firmalar icin kalite skorunu yeniden hesapla ve DB'ye yaz."""
    engine = get_engine()
    with engine.connect() as conn:
        rows = conn.execute(text("""
            SELECT company_id, legal_name, trade_name, tax_number, vergi_no,
                   adres, primary_phone, primary_email, website_domain, web_sitesi,
                   nace_code, osb_parsel
            FROM companies
            WHERE is_ankara = TRUE
        """)).mappings().all()

        print(f"Toplam firma: {len(rows)}")
        if not rows:
            return 0

        updated = 0
        for r in rows:
            row = dict(r)
            score = _score(row)
            conn.execute(text(
                "UPDATE companies SET data_quality_score = :s WHERE company_id = :cid"
            ), {"s": score, "cid": row["company_id"]})
            updated += 1

        conn.commit()

        # Ozet
        avg = conn.execute(text(
            "SELECT AVG(data_quality_score) FROM companies WHERE is_ankara = TRUE"
        )).fetchone()[0]
        print(f"Guncellenen: {updated}")
        print(f"Ortalama kalite skoru: {avg:.2f}")

        # Dagilim
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
        print("\nSkor Dagilimi:")
        for bucket, cnt in dist:
            print(f"  {bucket}: {cnt} firma")

        return updated


if __name__ == "__main__":
    recalc_quality_scores()
