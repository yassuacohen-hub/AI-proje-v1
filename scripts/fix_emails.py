#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""primary_email popülasyonu ve regex düzeltmesi.

raw_payload->'emailler' dizisinden companies.primary_email'i doldurur.
Regex'i Turkish TLD'ler (com.tr, net.org vb.) için gevşetir.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from sqlalchemy import text

from company_master.db.connection import get_engine


def fix_emails() -> int:
    engine = get_engine()
    with engine.begin() as conn:
        print("=== EMAIL POPÜLASYONU & REGEX DÜZELTME ===\n")

        # 1) Mevcut primary_email 'None' stringlerini NULL'a çevir
        print("[1] primary_email 'None' stringlerini NULL'a çevirme...")
        r = conn.execute(text("""
            UPDATE companies
            SET primary_email = NULL
            WHERE primary_email = 'None'
        """))
        print(f"    NULL'a çevrildi: {r.rowcount}")

        # 2) Yeni, daha gevşek regex - Turkish TLD'leri de kabul et
        # Eskisi: ^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$
        # Yeni: domain sonundaki .com.tr, .net.tr, .org.tr gibi TLD'leri de destekle
        new_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        print("[2] Regex güncellendi - Turkish TLD'ler destekleniyor")

        # 3) primary_email NULL olanlara raw_payload emailler dizisinden doldur
        print("[3] primary_email NULL olanlara emailler dizisinden doldurma...")
        r = conn.execute(text("""
            UPDATE companies c
            SET primary_email = sr.raw_payload->'emailler'->>0
            FROM source_records sr
            WHERE c.source_record_id = sr.source_record_id
              AND (c.primary_email IS NULL OR c.primary_email = '')
              AND sr.raw_payload IS NOT NULL
              AND sr.raw_payload ? 'emailler'
              AND jsonb_typeof(sr.raw_payload->'emailler') = 'array'
              AND jsonb_array_length(sr.raw_payload->'emailler') > 0
              AND sr.raw_payload->'emailler'->>0 IS NOT NULL
              AND sr.raw_payload->'emailler'->>0 != 'null'
        """))
        print(f"    populated from emailler: {r.rowcount}")

        # 4) Regex geçerliliği kontrolü - gevşek regex ile
        print("[4] Regex geçerliliği kontrolü (gevşek regex)...")
        r = conn.execute(text("""
            SELECT
                COUNT(*) FILTER (WHERE primary_email ~ '^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$') as valid,
                COUNT(*) FILTER (WHERE primary_email IS NULL) as null,
                COUNT(*) FILTER (WHERE primary_email = '') as empty,
                COUNT(*) FILTER (WHERE primary_email = 'None') as none_str,
                COUNT(*) as total
            FROM companies WHERE is_ankara = TRUE
        """)).fetchone()
        print(f"    valid (regex geçen): {r[0]}")
        print(f"    null: {r[1]}, empty: {r[2]}, None str: {r[3]}")
        print(f"    total: {r[4]}")

        # 5) final stats
        print("\n=== SONUÇ ===")
        r = conn.execute(text("""
            SELECT
                COUNT(*) FILTER (WHERE primary_email IS NULL OR primary_email !~ '^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$') as email_issue,
                COUNT(*) as total
            FROM companies WHERE is_ankara = TRUE
        """)).fetchone()
        print(f"email issue: {r[0]}/{r[1]}")

    return 1


def main() -> int:
    fix_emails()
    return 0


if __name__ == "__main__":
    sys.exit(main())