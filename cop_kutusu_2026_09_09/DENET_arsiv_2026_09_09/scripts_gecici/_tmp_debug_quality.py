#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Kalite skoru analizi ve eksik alan raporu."""
from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path
from sqlalchemy import text

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from company_master.db.connection import get_engine  # noqa: E402


def main() -> int:
    engine = get_engine()
    with engine.connect() as conn:
        toplam = conn.execute(text("SELECT COUNT(*) FROM companies WHERE is_ankara = TRUE")).scalar()
        ortalama = conn.execute(text("SELECT AVG(data_quality_score) FROM companies WHERE is_ankara = TRUE")).scalar()

        eksik = {}
        for alan, sql in [
            ("phone", "SELECT COUNT(*) FROM companies WHERE primary_phone IS NULL OR primary_phone = ''"),
            ("email", "SELECT COUNT(*) FROM companies WHERE primary_email IS NULL OR primary_email = ''"),
            ("web_sitesi", "SELECT COUNT(*) FROM companies WHERE website_domain IS NULL OR website_domain = ''"),
            ("vergi_no", "SELECT COUNT(*) FROM companies WHERE vergi_no IS NULL OR vergi_no = ''"),
            ("tax_number", "SELECT COUNT(*) FROM companies WHERE tax_number IS NULL OR tax_number = ''"),
            ("adres", "SELECT COUNT(*) FROM companies WHERE adres IS NULL OR adres = ''"),
            ("osb_parsel", "SELECT COUNT(*) FROM companies WHERE osb_parsel IS NULL OR osb_parsel = ''"),
        ]:
            eksik[alan] = conn.execute(text(sql)).scalar()

        raw_doluluk = {}
        for alan in ["adres", "web_sitesi", "vergi_no", "osb_parsel", "sektor", "nace_code"]:
            raw_doluluk[alan] = conn.execute(text("SELECT COUNT(*) FROM source_records WHERE raw_payload ? :alan AND NULLIF(raw_payload->>:alan, '') IS NOT NULL"), {"alan": alan}).scalar()

        dagilim = {}
        rows = conn.execute(text("SELECT data_quality_score, COUNT(*) FROM companies WHERE is_ankara = TRUE GROUP BY data_quality_score ORDER BY data_quality_score")).fetchall()
        for skor, sayi in rows:
            dagilim[str(int(skor))] = int(sayi)

    sonuc = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "toplam_firma": toplam,
        "ortalama_kalite_skoru": float(ortalama or 0),
        "eksik_alanlar": eksik,
        "raw_payload_doluluk": raw_doluluk,
        "skor_dagilimi": dagilim,
    }
    print(json.dumps(sonuc, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
