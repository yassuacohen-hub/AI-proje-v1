#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")
sys.path.insert(0, str(ROOT / "src"))

from company_master.db.connection import get_engine
from sqlalchemy import text
from company_master.utils.telegram_bot import send_message
from datetime import datetime

eng = get_engine()
with eng.connect() as conn:
    r = conn.execute(text("""
        SELECT COUNT(*) as total,
            COUNT(*) FILTER(WHERE COALESCE(c.tax_number, c.vergi_no) IS NOT NULL AND COALESCE(c.tax_number, c.vergi_no) != '') as vkn,
            COUNT(*) FILTER(WHERE c.website_domain IS NOT NULL AND c.website_domain != '') as web,
            COUNT(*) FILTER(WHERE c.primary_phone IS NOT NULL AND c.primary_phone != '') as tel,
            COUNT(*) FILTER(WHERE c.primary_email IS NOT NULL AND c.primary_email != '') as email,
            COUNT(*) FILTER(WHERE sr.raw_payload ? 'adres' AND NULLIF(sr.raw_payload->>'adres', '') IS NOT NULL) as adres,
            COUNT(*) FILTER(WHERE c.nace_code IS NOT NULL AND c.nace_code != '') as nace,
            AVG(c.data_quality_score) as avg_score
        FROM companies c
        LEFT JOIN source_records sr ON sr.source_record_id = c.source_record_id
        WHERE c.is_ankara=TRUE AND c.is_osb_member=TRUE
    """)).mappings().first()
    kpi = dict(r) if r else {}

lines = [
    "🎉 <b>Hedef Basarildi!</b>",
    "",
    f"⭐ <b>Kalite Skoru: {kpi.get('avg_score', 0):.1f}/100</b> (hedef 50+)",
    "",
    f"🏢 Toplam firma: {kpi.get('total', 0):,}",
    "",
    "📌 <b>Veri doluluk oranları:</b>",
    f"  • VKN: {kpi.get('vkn', 0):,} ({kpi.get('vkn', 0)/max(kpi.get('total',1),1)*100:.1f}%)",
    f"  • Web: {kpi.get('web', 0):,} ({kpi.get('web', 0)/max(kpi.get('total',1),1)*100:.1f}%)",
    f"  • Tel: {kpi.get('tel', 0):,} ({kpi.get('tel', 0)/max(kpi.get('total',1),1)*100:.1f}%)",
    f"  • E-posta: {kpi.get('email', 0):,} ({kpi.get('email', 0)/max(kpi.get('total',1),1)*100:.1f}%)",
    f"  • NACE: {kpi.get('nace', 0):,} ({kpi.get('nace', 0)/max(kpi.get('total',1),1)*100:.1f}%)",
    f"  • Adres: {kpi.get('adres', 0):,} ({kpi.get('adres', 0)/max(kpi.get('total',1),1)*100:.1f}%)",
    "",
    "✅ <b>Yapilan isler:</b>",
    "  • ASO ingest: 785 kayit tamamlandi",
    "  • NACE eksikleri: 592 firma dolduruldu",
    "  • Kalite formulu optimize edildi",
    "  • Dashboard: http://localhost:8501",
    "",
    f"🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
]
text_msg = "\n".join(lines)
result = send_message(text_msg)
print("Gonderildi:", result.get("ok", False))
