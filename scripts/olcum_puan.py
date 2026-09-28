"""KALITE-PUAN-01 olcumu.

Toplam kalite puaninin (companies.data_quality_score) saglamligini olcer:
  1. Kac farkli formul yaziyor, birbiriyle tutarli mi?
  2. 7 alt skor toplam puana giriyor mu?
  3. Kaynak kaydi (source_records) bagi saglam mi?

Calistirma: python scripts/olcum_puan.py
"""
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from sqlalchemy import text  # noqa: E402

from company_master.db.connection import get_engine  # noqa: E402
from company_master.etl.quality_recalc import _score  # noqa: E402

ALT_SKORLAR = [
    "data_freshness_score", "phone_format_score", "email_validity_score",
    "employee_count_score", "social_media_score", "source_diversity_score",
    "job_postings_score",
]


def main() -> int:
    with get_engine().connect() as c:
        toplam = c.execute(text("SELECT count(*) FROM companies")).scalar()
        print(f"-- firma: {toplam} --")

        print("\n[1] quality_recalc._score() yeniden hesap vs DB'deki deger")
        satirlar = c.execute(text(
            "SELECT company_id, trade_name, tax_number, vergi_no, adres,"
            " primary_phone, primary_email, website_domain, web_sitesi,"
            " nace_code, osb_parsel, data_quality_score FROM companies"
        )).mappings().all()
        durum, fark = Counter(), Counter()
        for r in satirlar:
            d = dict(r)
            db = d["data_quality_score"]
            if db is None:
                durum["DB bos"] += 1
                continue
            db, yeni = float(db), _score(d)
            if abs(yeni - db) < 0.05:
                durum["tutarli"] += 1
            else:
                durum["TUTARSIZ"] += 1
                fark[round(db - yeni, 1)] += 1
        for k, v in durum.most_common():
            print(f"    {k:10} {v}")
        if fark:
            print(f"    fark miktarlari: {dict(fark.most_common(5))}")

        print("\n[2] 7 alt skorun toplam puana katkisi")
        kolonlar = ", ".join(f"count({a}) AS {a}" for a in ALT_SKORLAR)
        dolu = c.execute(text(f"SELECT {kolonlar} FROM companies")).mappings().one()
        for a in ALT_SKORLAR:
            print(f"    {a:26} dolu={dolu[a]}")
        print("    NOT: mevcut formul alt skorlari kullanmiyor -> katki 0")

        print("\n[3] kaynak kaydi bagi")
        kopuk = c.execute(text(
            "SELECT count(*) FROM companies c WHERE NOT EXISTS"
            " (SELECT 1 FROM source_records s WHERE s.company_id = c.company_id)"
        )).scalar()
        yetim = c.execute(text(
            "SELECT count(*) FROM source_records WHERE company_id IS NULL"
        )).scalar()
        print(f"    kaynak kaydi olmayan firma:      {kopuk}")
        print(f"    firmaya baglanmamis kaynak kaydi: {yetim}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
