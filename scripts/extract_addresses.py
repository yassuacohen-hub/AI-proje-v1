#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""raw_payload'dan adres bilgilerini companies.adres kolonuna yaz (optimize)."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from sqlalchemy import text
from company_master.db.connection import get_engine


def main() -> int:
    engine = get_engine()
    with engine.begin() as conn:
        result = conn.execute(text("""
            UPDATE companies c
            SET adres = LEFT(NULLIF(sr.raw_payload->>'adres', ''), 500),
                updated_at = NOW()
            FROM source_records sr
            WHERE c.source_record_id = sr.source_record_id
              AND sr.raw_payload ? 'adres'
              AND NULLIF(sr.raw_payload->>'adres', '') IS NOT NULL
              AND (c.adres IS NULL OR c.adres = '')
        """))
        updated = result.rowcount
    print(f"Tamamlandi: {updated} firma adres guncellendi")
    return 0


if __name__ == "__main__":
    sys.exit(main())
