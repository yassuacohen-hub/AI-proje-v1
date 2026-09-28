"""Huginn Data Insights — KPI kontrol scripti."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from sqlalchemy import text
from company_master.db.connection import get_engine
from company_master import sunum

engine = get_engine()
with engine.connect() as conn:
    r = conn.execute(text('''
        SELECT COUNT(*) as total,
            COUNT(*) FILTER(WHERE c.tax_number IS NOT NULL AND c.tax_number != '') as vergi,
            COUNT(*) FILTER(WHERE c.website_domain IS NOT NULL AND c.website_domain != '') as web,
            COUNT(*) FILTER(WHERE c.osb_parsel IS NOT NULL AND c.osb_parsel != '') as parsel,
            COUNT(*) FILTER(WHERE c.primary_phone IS NOT NULL AND c.primary_phone != '') as telefon,
            COUNT(*) FILTER(WHERE c.primary_email IS NOT NULL AND c.primary_email != '') as email,
            COUNT(*) FILTER(WHERE c.nace_code IS NOT NULL AND c.nace_code != '') as nace,
            COUNT(*) FILTER(WHERE sr.raw_payload ? 'adres'
                              AND NULLIF(sr.raw_payload->>'adres', '') IS NOT NULL) as adres,
            AVG(c.identity_completeness) as ort_skor
        FROM companies c
        LEFT JOIN source_records sr ON sr.source_record_id = c.source_record_id
        WHERE c.is_ankara=TRUE AND c.is_osb_member=TRUE
    ''')).mappings().first()

    total = r["total"] or 0

    def p(n):
        return f"{n} ({n/total*100:.1f}%)" if total else "0 (0.0%)"

    print(f"Toplam: {total}")
    print(f"Telefon: {p(r['telefon'])}")
    print(f"Email: {p(r['email'])}")
    print(f"Web: {p(r['web'])}")
    print(f"Vergi: {p(r['vergi'])}")
    print(f"NACE: {p(r['nace'])}")
    print(f"Adres: {p(r['adres'])}")
    print(f"Parsel: {p(r['parsel'])}")
    # D-250/7 + D-249: puan tavanla birlikte, olculmemis ise bos.
    # Eski hali terk edilmis 0-100'luk kolonu "/100" diye yaziyordu.
    tavan = sunum.tavan_getir()
    print(f"Ortalama Kimlik Dosyasi Tamligi: {sunum.puan_metni(r['ort_skor'], tavan)}")
    print(sunum.tavan_metni(tavan))
