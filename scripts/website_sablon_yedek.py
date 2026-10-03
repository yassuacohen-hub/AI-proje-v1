# -*- coding: utf-8 -*-
"""Goc 0052 oncesi yedek (D-244): sablon website_domain tasiyan satirlari diske yaz.

    python scripts/website_sablon_yedek.py            # prova: sayar, yazmaz (D-243)
    python scripts/website_sablon_yedek.py --yaz      # yedekler/companies_website_sablon_<ts>.jsonl

Desen yazma_kapisi.SABLON_WEB_DESEN'den ithal edilir (D-211: kopya yok; goc 0052 ile ayni).
Yedek satir sayisi DB sayisiyla uyusmazsa RuntimeError (D-243 mandali).

Ilgili Nodlar: [[Huginn Data Insights/hubs/VERI_KALITESI_HUB]] ·
[[Huginn Data Insights/docs/BORC_DEFTERI]] (BORC-SITE-COP-01) ·
[[Huginn Data Insights/src/company_master/schema/migrations/0052_website_sablon_kisiti.sql]] ·
[[Huginn Data Insights/tests/test_website_sablon_kisiti.py]]
"""
from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path

KOK = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(KOK / "src"))

from sqlalchemy import text  # noqa: E402

from company_master.db.connection import get_engine  # noqa: E402
from company_master.db.yazma_kapisi import SABLON_WEB_DESEN  # noqa: E402

YEDEK_DIZIN = KOK / "yedekler"


def main(yaz: bool, yedek_dizin: Path = YEDEK_DIZIN) -> int:
    desen = SABLON_WEB_DESEN
    sql = text(
        "SELECT company_id::text AS company_id, website_domain, source_record_id::text AS source_record_id "
        "FROM companies WHERE website_domain IS NOT NULL AND lower(website_domain) ~ :d"
    )
    with get_engine().connect() as c:
        satirlar = [dict(r) for r in c.execute(sql, {"d": desen}).mappings()]
    n = len(satirlar)
    print(f"sablon website_domain: {n} satir")
    if not yaz:
        print("prova — yazilmadi. Yazmak icin --yaz")
        return 0
    yedek_dizin.mkdir(exist_ok=True)
    yol = yedek_dizin / f"companies_website_sablon_{datetime.now():%Y%m%d_%H%M}.jsonl"
    with yol.open("w", encoding="utf-8") as f:
        for s in satirlar:
            f.write(json.dumps(s, ensure_ascii=False) + "\n")
    yazilan = sum(1 for _ in yol.open(encoding="utf-8"))
    if yazilan != n:
        raise RuntimeError(f"yedek eksik: {yazilan}/{n} — goc UYGULANMAZ")
    print(f"yedek: {yol} ({yazilan} satir)")
    return 0


if __name__ == "__main__":
    sys.exit(main("--yaz" in sys.argv))
