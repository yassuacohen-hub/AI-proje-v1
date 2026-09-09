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


def calculate_data_freshness_score(last_verified_at: Any) -> int:
    if not last_verified_at:
        return 0
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


def calculate_phone_format_score(phone: str | None) -> int:
    if not phone:
        return 0
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


def calculate_social_media_score(social_media: dict | None) -> int:
    if not social_media or not isinstance(social_media, dict):
        return 0
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


def calculate_source_diversity_score(source_count: int) -> int:
    if source_count <= 1:
        return 0
    elif source_count == 2:
        return 2
    elif source_count <= 4:
        return 4
    else:
        return 5


def calculate_job_postings_score(job_count: int) -> int:
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


def calculate_employee_count_score(employee_count: int | None) -> int:
    if not employee_count or employee_count <= 0:
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


def calculate_email_validity_score(email: str | None) -> int:
    if not email:
        return 0
    if re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email):
        return 2
    return 0


def run_all_metrics_update() -> dict[str, int]:
    engine = get_engine()
    stats = {"data_freshness": 0, "phone_format": 0, "social_media": 0,
             "source_diversity": 0, "job_postings": 0, "employee_count": 0, "email_valid": 0}
    with engine.begin() as conn:
        rows = conn.execute(text("SELECT company_id, last_verified_at FROM companies")).mappings().all()
        for row in rows:
            score = calculate_data_freshness_score(row["last_verified_at"])
            conn.execute(text("UPDATE companies SET data_freshness_score = :s WHERE company_id = :id"), {"s": score, "id": row["company_id"]})
            stats["data_freshness"] += 1
        rows = conn.execute(text("SELECT company_id, primary_phone FROM companies")).mappings().all()
        for row in rows:
            score = calculate_phone_format_score(row["primary_phone"])
            conn.execute(text("UPDATE companies SET phone_format_score = :s WHERE company_id = :id"), {"s": score, "id": row["company_id"]})
            stats["phone_format"] += 1
        rows = conn.execute(text("""
            SELECT c.company_id, sr.raw_payload->>"sosyal_medya" as social_media
            FROM companies c
            JOIN source_records sr ON sr.source_record_id = c.source_record_id
        """)).mappings().all()
        for row in rows:
            social_media = row["social_media"]
            if social_media:
                try:
                    sm_dict = json.loads(social_media) if isinstance(social_media, str) else social_media
                except Exception:
                    sm_dict = {}
            else:
                sm_dict = {}
            score = calculate_social_media_score(sm_dict)
            conn.execute(text("UPDATE companies SET social_media_score = :s WHERE company_id = :id"), {"s": score, "id": row["company_id"]})
            stats["social_media"] += 1
        rows = conn.execute(text("""
            SELECT c.company_id, COUNT(DISTINCT s.source_id) as src_count
            FROM companies c
            JOIN source_records sr ON sr.source_record_id = c.source_record_id
            JOIN sources s ON s.source_id = sr.source_id
            GROUP BY c.company_id
        """)).mappings().all()
        for row in rows:
            score = calculate_source_diversity_score(row["src_count"])
            conn.execute(text("UPDATE companies SET source_diversity_score = :s WHERE company_id = :id"), {"s": score, "id": row["company_id"]})
            stats["source_diversity"] += 1
        rows = conn.execute(text("SELECT company_id, employee_count FROM companies")).mappings().all()
        for row in rows:
            score = calculate_employee_count_score(row["employee_count"])
            conn.execute(text("UPDATE companies SET employee_count_score = :s WHERE company_id = :id"), {"s": score, "id": row["company_id"]})
            stats["employee_count"] += 1
        rows = conn.execute(text("SELECT company_id, primary_email FROM companies")).mappings().all()
        for row in rows:
            score = calculate_email_validity_score(row["primary_email"])
            conn.execute(text("UPDATE companies SET email_validity_score = :s WHERE company_id = :id"), {"s": score, "id": row["company_id"]})
            stats["email_valid"] += 1
    return stats


if __name__ == "__main__":
    result = run_all_metrics_update()
    print(json.dumps(result, ensure_ascii=False, indent=2))
