# -*- coding: utf-8 -*-
"""Kalite skoru recalculation scripti.

Tum firmalar icin kalite skorunu yeniden hesaplar ve DB'ye yazar.
SQLite/PostgreSQL uyumlu.
"""
from __future__ import annotations

from sqlalchemy import text
from company_master.db.connection import get_engine


def kalite_puani(row: dict) -> float:
    """Toplam kalite puani (0-100) — TEK KAPI (D-250).

    Alan agirliklari: VKN 15, adres 15, telefon 15, e-posta 15, NACE 15,
    web 10, OSB parsel 10, unvan 5.

    Alt skorlar (tazelik, telefon bicimi, sosyal medya, kaynak cesitliligi,
    calisan sayisi, is ilani) BU PUANA GIRMEZ — D-250/2. Sebep:
    employee_count %100, job_postings %99.9 bos; puana katmak "veri yok"u
    "kotu firma" diye yansitir (D-249 ihlali).
    """
    score = 0.0
    # VKN (dogrulanmis; D-254: kaynak kimlik defteri) - 15 puan
    vkn = row.get("tax_number") or ""
    if vkn and vkn.strip():
        score += 15
    # Adres - 15 puan
    adres = row.get("address") or ""
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
    web = row.get("website_domain") or ""
    if web and web.strip():
        score += 10
    # NACE kodu - 15 puan
    nace = row.get("nace_code") or ""
    if nace and nace.strip():
        score += 15
    # OSB parsel - 10 puan
    parsel = row.get("osb_parcel") or ""
    if parsel and parsel.strip():
        score += 10
    # Ticaret unvani - 5 puan
    trade = row.get("trade_name") or ""
    if trade and trade.strip():
        score += 5
    return round(min(score, 100.0), 1)


_score = kalite_puani  # geriye donuk ad


def recalc_quality_scores() -> int:
    """Tum firmalar icin kalite puanini yeniden hesapla ve DB'ye yaz.

    D-249/2: satir basina UPDATE yasak — tek toplu yazma.
    D-250/3: is_ankara filtresi kaldirildi; bayat puan Ankara disinda da olusur.
    """
    engine = get_engine()
    with engine.connect() as conn:
        rows = conn.execute(text("""
            SELECT company_id, legal_name, trade_name, tax_number,
                   address, primary_phone, primary_email, website_domain,
                   nace_code, osb_parcel
            FROM companies
        """)).mappings().all()

        print(f"Toplam firma: {len(rows)}")
        if not rows:
            return 0

        veri = [{"cid": r["company_id"], "s": kalite_puani(dict(r))} for r in rows]
        conn.execute(text(
            "UPDATE companies SET data_quality_score = :s WHERE company_id = :cid"
        ), veri)
        conn.commit()
        updated = len(veri)

        # Ozet
        avg = conn.execute(text(
            "SELECT AVG(data_quality_score) FROM companies"
        )).fetchone()[0]
        print(f"Guncellenen: {updated}")
        print(f"Ortalama kalite puani: {avg:.2f}")

        # Dagilim
        dist = conn.execute(text("""
            SELECT CASE
                WHEN data_quality_score >= 80 THEN '80-100'
                WHEN data_quality_score >= 60 THEN '60-79'
                WHEN data_quality_score >= 40 THEN '40-59'
                WHEN data_quality_score >= 20 THEN '20-39'
                ELSE '0-19'
            END as bucket, COUNT(*) as cnt
            FROM companies
            GROUP BY 1 ORDER BY 1 DESC
        """)).fetchall()
        print("\nSkor Dagilimi:")
        for bucket, cnt in dist:
            print(f"  {bucket}: {cnt} firma")

        return updated


if __name__ == "__main__":
    recalc_quality_scores()
