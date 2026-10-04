# -*- coding: utf-8 -*-
"""VERI-WEB-SITESI-ZENGINLESTIR-01 — D-66 varsayım ölçümü (salt okunur).

Ne olcuyor:
  1. companies.website_domain bos / dolu sayisi
  2. source_records.raw_website dolu sayisi + en sik degerler (sablon sinyali)
  3. Bos alanli firmalarin kacinda ham web adayi var (aday havuzu)
  4. Kanit: yazma YOK (yalnizca SELECT), --kuru default

    python -X utf8 scripts/web_kaynak_olcum.py
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from sqlalchemy import text  # noqa: E402
from company_master.db.connection import get_engine  # noqa: E402
# D-211: sablon listesi KOPYALANMAZ. `SABLON_WEB` tek kaynak; burada yalniz
# SQL regex'e cevrilir. onceki hali listenin tamamini dosyaya yaziyordu
# (D-303 ihlali: kanonik kopya sayisi 23 -> 24).
from company_master.db.yazma_kapisi import SABLON_WEB  # noqa: E402

#: SQL regulari icin kanonik desen. `re.escape` noktalari kaçirir.
SABLON_DESEN = "(^|[^a-z0-9-])(" + "|".join(
    re.escape(d) for d in SABLON_WEB) + ")"

SORULAR = {
    "firma_toplam": "SELECT count(*) FROM companies",
    "web_dolu": "SELECT count(*) FROM companies WHERE website_domain IS NOT NULL AND btrim(website_domain) <> ''",
    "web_bos": "SELECT count(*) FROM companies WHERE website_domain IS NULL OR btrim(website_domain) = ''",
    "raw_web_dolu": "SELECT count(*) FROM source_records WHERE raw_website IS NOT NULL AND btrim(raw_website) <> ''",
}


def main() -> int:
    engine = get_engine()
    out: dict[str, object] = {}
    with engine.connect() as conn:
        for ad, sql in SORULAR.items():
            out[ad] = int(conn.execute(text(sql)).scalar() or 0)

        # En sik ham degerler: tekrar eden deger kaynak sizintisi isaretidir (D-245).
        satirlar = conn.execute(text("""
            SELECT btrim(raw_website) AS w, count(*) AS n
            FROM source_records
            WHERE raw_website IS NOT NULL AND btrim(raw_website) <> ''
            GROUP BY 1 ORDER BY 2 DESC LIMIT 15
        """)).mappings().all()
        out["raw_web_en_sik"] = [{"deger": r["w"], "adet": int(r["n"])} for r in satirlar]

        # Bos alanli firmada ham adayi olanlar (yazilacak aday havuzu).
        havuz = conn.execute(text("""
            SELECT count(DISTINCT c.company_id)
            FROM companies c
            JOIN source_records sr ON sr.source_record_id = c.source_record_id
            WHERE (c.website_domain IS NULL OR btrim(c.website_domain) = '')
              AND sr.raw_website IS NOT NULL AND btrim(sr.raw_website) <> ''
        """)).scalar()
        out["bos_alan_ham_adayli_firma"] = int(havuz or 0)

        # Bos alanli firmalar kaynak kirilimi (hangi OSB uyesi listeden gelmis).
        kirilim = conn.execute(text("""
            SELECT sr.source_id, count(*) AS n
            FROM companies c
            JOIN source_records sr ON sr.source_record_id = c.source_record_id
            WHERE c.website_domain IS NULL OR btrim(c.website_domain) = ''
            GROUP BY 1 ORDER BY 2 DESC LIMIT 10
        """)).mappings().all()
        out["bos_alan_kaynak_kirilimi"] = [
            {"source_id": r["source_id"], "adet": int(r["n"])} for r in kirilim]

        # Ornek: ham adayi olan bos alanli 5 firma (denetim icin gercek unvan).
        ornek = conn.execute(text("""
            SELECT c.company_id, c.legal_name, btrim(sr.raw_website) AS w
            FROM companies c
            JOIN source_records sr ON sr.source_record_id = c.source_record_id
            WHERE (c.website_domain IS NULL OR btrim(c.website_domain) = '')
              AND sr.raw_website IS NOT NULL AND btrim(sr.raw_website) <> ''
            ORDER BY c.company_id LIMIT 5
        """)).mappings().all()
        out["ornek"] = [{"legal_name": r["legal_name"], "raw_website": r["w"]} for r in ornek]

        # Ham degerin kendi alan adi sekli: sema/host ayrimi.
        ana = Counter()
        for r in satirlar:
            d = str(r["w"])
            ana[d.split("/")[0] if "//" in d else d] += 1
        out["raw_web_ana_kok"] = ana.most_common(10)

        # --- backfill_websites.py'nin YAZACAGI adaylarin gercek/sablon ayrimi ---
        # `kabul()` reddedecekleri (sablon) ayri sayilir: script kapiyi cagrirmiyor.
        # D-211: desen SABLON_WEB'ten uretilir (asagida), buraya YAZILMAZ.
        gercek_aday = conn.execute(text("""
            SELECT count(DISTINCT c.company_id)
            FROM companies c
            JOIN source_records sr ON sr.source_record_id = c.source_record_id
            WHERE (c.website_domain IS NULL OR btrim(c.website_domain) = '')
              AND sr.raw_website IS NOT NULL AND btrim(sr.raw_website) <> ''
              AND lower(btrim(sr.raw_website)) !~ :sablon
        """), {"sablon": SABLON_DESEN}).scalar()
        out["bos_alan_sablonsuz_ham_aday"] = int(gercek_aday or 0)

        # Ayni adayin birden fazla firmaya yazilmasi = yanlis pozitif riski.
        cakisma = conn.execute(text("""
            SELECT btrim(sr.raw_website) AS w, count(DISTINCT c.company_id) AS n
            FROM companies c
            JOIN source_records sr ON sr.source_record_id = c.source_record_id
            WHERE (c.website_domain IS NULL OR btrim(c.website_domain) = '')
              AND sr.raw_website IS NOT NULL AND btrim(sr.raw_website) <> ''
            GROUP BY 1 HAVING count(DISTINCT c.company_id) > 1
            ORDER BY 2 DESC LIMIT 10
        """)).mappings().all()
        out["birden_firmaya_yazilacak_ham_aday"] = [
            {"deger": r["w"], "firma": int(r["n"])} for r in cakisma]

    print(json.dumps(out, ensure_ascii=False, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
