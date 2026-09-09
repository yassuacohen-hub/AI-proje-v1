#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""P1-5: NACE enrichment Phase 3 — 1266 firma icin fallback strategy."""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import psycopg

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from company_master.db.connection import get_database_url  # noqa: E402
from company_master.etl.nace_mapper import nace_bul  # noqa: E402


def get_conn():
    url = get_database_url()
    if url.startswith("postgresql+psycopg://"):
        url = url.replace("postgresql+psycopg://", "postgresql://", 1)
    return psycopg.connect(url, prepare_threshold=None, autocommit=True)


GENIS_KELIMELER = [
    (r"(sanayi|fabrik|uretim|imalat)", "25.11"),
    (r"(ticaret|market|dokan|dükhan)", "46.90"),
    (r"(insaat|yapi|yapı|construction|build)", "41.20"),
    (r"(nakliye|taksi|kargo|lojistik|delivery)", "52.29"),
    (r"(bilgisayar|web|software|app|teknoloji)", "62.01"),
    (r"(restoran|kahve|otel|motel|konaklama)", "56.10"),
    (r"(muhasebe|vergi|finans|danismanlik|consult)", "69.20"),
    (r"(okul|egitim|kurs|dokume|egit)", "85.59"),
    (r"(hastane|klinik|eczane|sağlik|saglik)", "86.90"),
    (r"(tarim|farm|bahçe|çift|hayvancilik)", "01.49"),
    (r"(giyim|tekstil|moda|tekstil)", "14.11"),
    (r"(mobilya|dekor|interior|dekorasyon)", "31.02"),
    (r"(enerji|petrol|gas|enerji)", "09.10"),
]

FALLBACK_NACE = "99.00"


def main():
    parser = argparse.ArgumentParser(prog="nace-phase3")
    parser.add_argument("--dry-once", action="store_true",
                        help="Sadece count yaz, DB'ye yans")
    parser.add_argument("--calistir", action="store_true",
                        help="DB'yi NACE kodlariyla guncelle")
    args = parser.parse_args()

    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute(
            "SELECT company_id, trade_name FROM companies "
            "WHERE (nace_code IS NULL OR nace_code = '') "
            "AND trade_name IS NOT NULL AND trade_name <> ''"
        )
        rows = cur.fetchall()
        print(f"NACE'suz firma (trade_name varken): {len(rows)}")

        eslesen = 0
        fallback = 0

        for company_id, trade_name in rows:
            matches = nace_bul(trade_name or "", None, None)
            if matches:
                code = matches[0].code
                eslesen += 1
            else:
                code = None
                for pattern, nace_code in GENIS_KELIMELER:
                    if re.search(pattern, (trade_name or "").lower()):
                        code = nace_code
                        eslesen += 1
                        break
                if not code:
                    code = FALLBACK_NACE
                    fallback += 1

            if not args.dry_once:
                cur.execute(
                    "UPDATE companies SET nace_code = %s WHERE company_id = %s",
                    (code, company_id),
                )

        print(f"NACE kodlandi: {eslesen} | Fallback 99.00: {fallback}")
        if args.dry_once:
            print("(dry-once: DB'ye yazilmedi)")

    conn.close()
    print("P1-5 NACE enrichment tamam!")


if __name__ == "__main__":
    main()