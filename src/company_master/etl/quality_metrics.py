#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Kalite skoruna eklenecek yeni metrikler hesaplayıcıları."""
from __future__ import annotations

import json
import re
from datetime import datetime
from typing import Any
from sqlalchemy import text
from company_master.db.connection import get_engine


def calculate_data_freshness_score(last_verified_at: Any) -> int | None:
    """D-249: hic dogrulanmamissa NULL. 0 = 'dogrulandi ama bir yildan bayat'."""
    if not last_verified_at:
        return None
    if isinstance(last_verified_at, str):
        try:
            last_verified_at = datetime.fromisoformat(last_verified_at.replace("Z", "+00:00"))
        except Exception:
            return 0
    days_ago = (datetime.now(last_verified_at.tzinfo if hasattr(last_verified_at, "tzinfo") and last_verified_at.tzinfo else None) - last_verified_at).days
    if days_ago <= 30:
        return 8
    elif days_ago <= 90:
        return 6
    elif days_ago <= 180:
        return 4
    elif days_ago <= 365:
        return 2
    else:
        return 0


def calculate_phone_format_score(phone: str | None) -> int | None:
    """D-249: telefon yoksa NULL. 0 = 'telefon var ama bicimi taninmadi'."""
    if not phone:
        return None
    digits = re.sub(r"\D", "", phone)
    if re.match(r"^\+?90\d{10}$", phone.replace(" ", "").replace("-", "")):
        return 2
    if re.match(r"^0\d{9,10}$", digits):
        return 2
    if re.match(r"^5\d{9}$", digits):
        return 1
    if len(digits) in (10, 11) and digits.isdigit():
        return 1
    return 0


def calculate_social_media_score(social_media: dict | None) -> int | None:
    """D-249: sosyal medya alani hic yoksa NULL. 0 = 'alan var, gecerli URL yok'."""
    if not social_media or not isinstance(social_media, dict):
        return None
    valid_platforms = 0
    for platform, url in social_media.items():
        if url and isinstance(url, str) and url.startswith(("http://", "https://")):
            valid_platforms += 1
    if valid_platforms == 0:
        return 0
    elif valid_platforms == 1:
        return 2
    elif valid_platforms <= 3:
        return 3
    else:
        return 5


def calculate_source_diversity_score(source_count: int | None) -> int | None:
    """D-249: veri yoksa NULL. 0 degeri 'tek kaynaktan geldi' demektir."""
    if source_count is None or source_count <= 0:
        return None
    if source_count == 1:
        return 0
    elif source_count == 2:
        return 2
    elif source_count <= 4:
        return 4
    else:
        return 5


def calculate_job_postings_score(job_count: int | None) -> int | None:
    """D-249: is ilani verisi yoksa NULL; 0 'aradik, ilan yok' demektir."""
    if job_count is None:
        return None
    if job_count <= 0:
        return 0
    elif job_count <= 2:
        return 2
    elif job_count <= 5:
        return 4
    elif job_count <= 10:
        return 6
    elif job_count <= 20:
        return 7
    else:
        return 8


def calculate_employee_count_score(employee_count: int | None) -> int | None:
    """D-249: calisan sayisi bilinmiyorsa NULL, 0 puan degil."""
    if employee_count is None:
        return None
    if employee_count <= 0:
        return 0
    elif employee_count <= 10:
        return 2
    elif employee_count <= 50:
        return 3
    elif employee_count <= 200:
        return 4
    elif employee_count <= 500:
        return 5
    elif employee_count <= 1000:
        return 6
    else:
        return 7


def calculate_email_validity_score(email: str | None) -> int | None:
    """D-249: e-posta yoksa NULL. 0 = 'e-posta var ama gecersiz'."""
    if not email:
        return None
    if re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email):
        return 2
    return 0


def _sosyal_medya_coz(deger: Any) -> dict:
    if not deger:
        return {}
    if isinstance(deger, dict):
        return deger
    try:
        cozulen = json.loads(deger)
    except Exception:
        return {}
    return cozulen if isinstance(cozulen, dict) else {}


def run_all_metrics_update() -> dict[str, int]:
    """D-249: her skor tek toplu UPDATE ile yazilir.

    Onceki hali firma basina ayri UPDATE atiyordu (9412 x 7 ~ 66 bin tur);
    tek islem icinde saatler suruyordu. Hesap mantigi Python'da kalir,
    yazma executemany ile tek tura duser.
    """
    engine = get_engine()
    # (istatistik adi, kolon, kaynak sorgusu, satirdan puan ureten islev)
    isler: list[tuple[str, str, str, Any]] = [
        ("data_freshness", "data_freshness_score",
         "SELECT company_id, last_verified_at AS v FROM companies",
         calculate_data_freshness_score),
        ("phone_format", "phone_format_score",
         "SELECT company_id, primary_phone AS v FROM companies",
         calculate_phone_format_score),
        ("email_valid", "email_validity_score",
         "SELECT company_id, primary_email AS v FROM companies",
         calculate_email_validity_score),
        ("employee_count", "employee_count_score",
         "SELECT company_id, employee_count AS v FROM companies",
         calculate_employee_count_score),
        ("social_media", "social_media_score",
         "SELECT c.company_id, sr.raw_payload->>'sosyal_medya' AS v"
         " FROM companies c"
         " JOIN source_records sr ON sr.source_record_id = c.source_record_id",
         lambda d: calculate_social_media_score(_sosyal_medya_coz(d))),
        # D-249/2: dogru bag source_records.company_id. Eski sorgu
        # companies.source_record_id uzerinden gidiyordu; o tanim geregi tek
        # kayit dondurur, bu yuzden skor 9412 satirda sabit 0 kaliyordu.
        ("source_diversity", "source_diversity_score",
         "SELECT c.company_id, COUNT(DISTINCT sr.source_id) AS v"
         " FROM companies c"
         " LEFT JOIN source_records sr ON sr.company_id = c.company_id"
         " GROUP BY c.company_id",
         calculate_source_diversity_score),
    ]
    stats: dict[str, int] = {}
    with engine.begin() as conn:
        for ad, kolon, sorgu, hesapla in isler:
            satirlar = conn.execute(text(sorgu)).mappings().all()
            veri = [{"id": r["company_id"], "s": hesapla(r["v"])} for r in satirlar]
            if veri:
                conn.execute(
                    text(f"UPDATE companies SET {kolon} = :s WHERE company_id = :id"),
                    veri,
                )
            stats[ad] = len(veri)
        # D-249/1: bu dongu hic yazilmamisti, kolon DEFAULT 0 ile dolu sanilirdi.
        satirlar = conn.execute(text("""
            SELECT c.company_id, COUNT(j.job_posting_id) AS v
            FROM companies c
            LEFT JOIN job_postings j ON j.company_id = c.company_id
            GROUP BY c.company_id
        """)).mappings().all()
        veri = [{"id": r["company_id"], "n": r["v"] or None,
                 "s": calculate_job_postings_score(r["v"] or None)} for r in satirlar]
        if veri:
            conn.execute(text(
                "UPDATE companies SET job_postings_count = :n, job_postings_score = :s"
                " WHERE company_id = :id"
            ), veri)
        stats["job_postings"] = len(veri)
    return stats


if __name__ == "__main__":
    result = run_all_metrics_update()
    print(json.dumps(result, ensure_ascii=False, indent=2))
