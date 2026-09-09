#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Veri Kalitesi KPI Dashboard - Markdown raporu uretir.

Kullanim:
    python scripts/generate_kpi_report.py
"""
import sys
from pathlib import Path
from sqlalchemy import text
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from company_master.db.connection import get_engine

def main():
    engine = get_engine()
    with engine.connect() as conn:
        # Ana metrikler
        r = conn.execute(text("""
            SELECT COUNT(*) as total,
                COUNT(*) FILTER(WHERE COALESCE(c.tax_number, c.vergi_no) IS NOT NULL AND COALESCE(c.tax_number, c.vergi_no) != '') as vergi,
                COUNT(*) FILTER(WHERE c.website_domain IS NOT NULL AND c.website_domain != '') as web,
                COUNT(*) FILTER(WHERE c.osb_parsel IS NOT NULL AND c.osb_parsel != '') as parsel,
                COUNT(*) FILTER(WHERE c.primary_phone IS NOT NULL AND c.primary_phone != '') as telefon,
                COUNT(*) FILTER(WHERE c.primary_email IS NOT NULL AND c.primary_email != '') as email,
                COUNT(*) FILTER(WHERE c.nace_code IS NOT NULL AND c.nace_code != '') as nace,
                COUNT(*) FILTER(WHERE sr.raw_payload ? 'adres'
                                  AND NULLIF(sr.raw_payload->>'adres', '') IS NOT NULL) as adres,
                AVG(c.data_quality_score) as ort_skor
            FROM companies c
            LEFT JOIN source_records sr ON sr.source_record_id = c.source_record_id
            WHERE c.is_ankara=TRUE AND c.is_osb_member=TRUE
        """)).mappings().first()
        
        total = r["total"] or 0
        def p(n): return f"{n} ({n/total*100:.1f}%)" if total else "0 (0.0%)"
        def s(v): return f"{v:.2f}" if v else "0.00"
        
        report = f"""# Veri Kalitesi KPI Dashboard

Tarih: 2026-09-03
Toplam Firma: {total}

## Alan Doluluk Oranlari

| Alan | Dolu | Oran |
|------|------|------|
| Telefon | {p(r['telefon'])} | bar |
| E-posta | {p(r['email'])} | bar |
| Web Sitesi | {p(r['web'])} | bar |
| Vergi No | {p(r['vergi'])} | bar |
| NACE Kodu | {p(r['nace'])} | bar |
| Adres | {p(r['adres'])} | bar |
| OSB Parsel | {p(r['parsel'])} | bar |

## Kalite Skorlari

- Ortalama Kalite Skoru: {s(r['ort_skor'])}/100
- Hedef: 50+/100 (MVP kabul edilebilir)

## Durum

"""
        if r["ort_skor"] and r["ort_skor"] >= 50:
            report += "VERI KALITESI: YETERLI - MVP icin uygun\n"
        elif r["ort_skor"] and r["ort_skor"] >= 30:
            report += "VERI KALITESI: ORTA - Detay scrape ile yukseltilebilir\n"
        else:
            report += "VERI KALITESI: DUSUK - Detay scrape oncelikli\n"
        
        print(report)
        # Markdown dosyaya kaydet
        rapor_dosya = ROOT / "data" / "kpi_raporu.md"
        rapor_dosya.write_text(report, encoding="utf-8")
        print(f"\nRapor kaydedildi: {rapor_dosya}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
