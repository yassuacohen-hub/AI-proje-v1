# -*- coding: utf-8 -*-
"""11 haneli vergi_no degerlerinin kokeni: ham kayitta izi var mi?"""
import sys
sys.path.insert(0, "src")
from sqlalchemy import text
from company_master.db.connection import get_engine

SATIR = []
MOTOR = get_engine()


def y(s):
    SATIR.append(str(s))


def sor(baslik, sql, bicim=None):
    y(f"\n== {baslik}")
    try:
        with MOTOR.connect() as c:
            bos = True
            for r in c.execute(text(sql)):
                bos = False
                y("   " + (bicim(r) if bicim else str(tuple(r))))
            if bos:
                y("   (bos)")
    except Exception as e:
        y(f"   HATA: {type(e).__name__}: {str(e)[:220]}")


sor("vergi_no hane x ham kayitta iz", """
    SELECT length(regexp_replace(c.vergi_no,'\\D','','g')) AS hane,
           count(*) AS adet,
           count(*) FILTER (WHERE sr.raw_tax_number = c.vergi_no) AS ham_ayni,
           count(*) FILTER (WHERE sr.raw_payload::text LIKE '%'||c.vergi_no||'%') AS payload_icinde
    FROM companies c LEFT JOIN source_records sr ON sr.source_record_id = c.source_record_id
    WHERE c.vergi_no IS NOT NULL AND c.vergi_no <> ''
    GROUP BY 1 ORDER BY 2 DESC
""", lambda r: f"{r[0]:>3} hane  adet={r[1]:>4}  ham_ayni={r[2]:>4}  payload_icinde={r[3]:>4}")

sor("11 hane kaynak kurumu", """
    SELECT s.source_name, count(*)
    FROM companies c
    JOIN source_records sr ON sr.source_record_id = c.source_record_id
    JOIN sources s ON s.source_id = sr.source_id
    WHERE c.vergi_no IS NOT NULL AND length(regexp_replace(c.vergi_no,'\\D','','g'))=11
    GROUP BY 1 ORDER BY 2 DESC
""", lambda r: f"{r[1]:>5}  {r[0]}")

sor("3-6 hane kaynak kurumu", """
    SELECT s.source_name, count(*)
    FROM companies c
    JOIN source_records sr ON sr.source_record_id = c.source_record_id
    JOIN sources s ON s.source_id = sr.source_id
    WHERE c.vergi_no IS NOT NULL AND length(regexp_replace(c.vergi_no,'\\D','','g')) BETWEEN 3 AND 6
    GROUP BY 1 ORDER BY 2 DESC
""", lambda r: f"{r[1]:>5}  {r[0]}")

sor("raw_payload'da vergi/tax anahtarlari (ornek 3 kayit)", """
    SELECT DISTINCT jsonb_object_keys(sr.raw_payload)
    FROM companies c JOIN source_records sr ON sr.source_record_id = c.source_record_id
    WHERE c.vergi_no IS NOT NULL AND length(regexp_replace(c.vergi_no,'\\D','','g'))=11
    LIMIT 40
""", lambda r: r[0])

sor("tax_number hane x ham iz", """
    SELECT length(regexp_replace(c.tax_number,'\\D','','g')) AS hane, count(*),
           count(*) FILTER (WHERE sr.raw_tax_number = c.tax_number) AS ham_ayni
    FROM companies c LEFT JOIN source_records sr ON sr.source_record_id = c.source_record_id
    WHERE c.tax_number IS NOT NULL AND c.tax_number <> ''
    GROUP BY 1 ORDER BY 2 DESC
""", lambda r: f"{r[0]:>3} hane  adet={r[1]:>4}  ham_ayni={r[2]:>4}")

metin = "\n".join(SATIR)
with open("_olcum_koken.txt", "w", encoding="utf-8") as f:
    f.write(metin)
print(metin.encode("ascii", "replace").decode("ascii"))
