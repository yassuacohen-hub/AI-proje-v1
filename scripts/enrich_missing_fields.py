#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""DB'den alternatif alanlardan eksik veriyi doldur + kalite raporu.

Adimlar:
  1. source_records.raw_payload icindeki alanlarin doluluk orani
  2. companies tablosunda NULL olan website_domain / tax_number / vergi_no
     alanlarini source_records.raw_payload (web_sitesi, vergi_no) ile doldur.
     - web_sitesi icin "ostimonline.com" filtresi uygulanir.
  3. scripts/recalculate_quality_scores.py dosyasini calistir.
  4. Son durumu raporla.

Kullanimi:
    python scripts/enrich_missing_fields.py
"""

from __future__ import annotations

import logging
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from sqlalchemy import text

PROJE_KOK = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJE_KOK / "src"))

from company_master.db.connection import get_engine  # noqa: E402

LOG_KLASOR = PROJE_KOK / "logs"
LOG_KLASOR.mkdir(parents=True, exist_ok=True)
LOG_DOSYA = LOG_KLASOR / "enrich_missing_fields.log"

logger = logging.getLogger("enrich_missing_fields")
logger.setLevel(logging.INFO)
_formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
_fh = logging.FileHandler(LOG_DOSYA, encoding="utf-8")
_fh.setFormatter(_formatter)
_sh = logging.StreamHandler()
_sh.setFormatter(_formatter)
logger.addHandler(_fh)
logger.addHandler(_sh)


def adim_1_payload_doluluk(conn) -> dict:
    """source_records.raw_payload icindeki alanlarin dolu sayisi."""
    logger.info("Adim 1: source_records.raw_payload doluluk analizi")
    sql = text("""
        SELECT
            COUNT(*) AS toplam,
            COUNT(*) FILTER (WHERE raw_payload ? 'adres'
                              AND NULLIF(raw_payload->>'adres', '') IS NOT NULL) AS adres,
            COUNT(*) FILTER (WHERE raw_payload ? 'web_sitesi'
                              AND NULLIF(raw_payload->>'web_sitesi', '') IS NOT NULL) AS web_sitesi,
            COUNT(*) FILTER (WHERE raw_payload ? 'vergi_no'
                              AND NULLIF(raw_payload->>'vergi_no', '') IS NOT NULL) AS vergi_no,
            COUNT(*) FILTER (WHERE raw_payload ? 'osb_parsel'
                              AND NULLIF(raw_payload->>'osb_parsel', '') IS NOT NULL) AS osb_parsel,
            COUNT(*) FILTER (WHERE raw_payload ? 'sektor'
                              AND NULLIF(raw_payload->>'sektor', '') IS NOT NULL) AS sektor,
            COUNT(*) FILTER (WHERE raw_payload ? 'nace_code'
                              AND NULLIF(raw_payload->>'nace_code', '') IS NOT NULL) AS nace_code
        FROM source_records
    """)
    row = conn.execute(sql).mappings().first()
    return dict(row)


def adim_2_companies_doldur(conn) -> dict:
    """companies tablosunda NULL olan alanlari source_records'tan doldur."""
    logger.info("Adim 2: companies tablosunda eksik alanlar dolduruluyor")

    onceki_web = conn.execute(text(
        "SELECT COUNT(*) FROM companies WHERE website_domain IS NULL OR website_domain = ''"
    )).scalar()
    onceki_tax = conn.execute(text(
        "SELECT COUNT(*) FROM companies WHERE tax_number IS NULL OR tax_number = ''"
    )).scalar()
    onceki_vn = conn.execute(text(
        "SELECT COUNT(*) FROM companies WHERE vergi_no IS NULL OR vergi_no = ''"
    )).scalar()

    web_sql = text("""
        UPDATE companies c
        SET website_domain = NULLIF(LOWER(TRIM(sr.raw_payload->>'web_sitesi')), '')
        FROM source_records sr
        WHERE c.source_record_id = sr.source_record_id
          AND (c.website_domain IS NULL OR c.website_domain = '')
          AND sr.raw_payload ? 'web_sitesi'
          AND NULLIF(sr.raw_payload->>'web_sitesi', '') IS NOT NULL
          AND LOWER(sr.raw_payload->>'web_sitesi') <> 'ostimonline.com'
    """)
    tax_sql = text("""
        UPDATE companies c
        SET tax_number = NULLIF(TRIM(sr.raw_payload->>'vergi_no'), '')
        FROM source_records sr
        WHERE c.source_record_id = sr.source_record_id
          AND (c.tax_number IS NULL OR c.tax_number = '')
          AND sr.raw_payload ? 'vergi_no'
          AND NULLIF(sr.raw_payload->>'vergi_no', '') IS NOT NULL
    """)
    vn_sql = text("""
        UPDATE companies c
        SET vergi_no = NULLIF(TRIM(sr.raw_payload->>'vergi_no'), '')
        FROM source_records sr
        WHERE c.source_record_id = sr.source_record_id
          AND (c.vergi_no IS NULL OR c.vergi_no = '')
          AND sr.raw_payload ? 'vergi_no'
          AND NULLIF(sr.raw_payload->>'vergi_no', '') IS NOT NULL
    """)

    web_upd = conn.execute(web_sql).rowcount
    tax_upd = conn.execute(tax_sql).rowcount
    vn_upd = conn.execute(vn_sql).rowcount

    sonra_web = conn.execute(text(
        "SELECT COUNT(*) FROM companies WHERE website_domain IS NULL OR website_domain = ''"
    )).scalar()
    sonra_tax = conn.execute(text(
        "SELECT COUNT(*) FROM companies WHERE tax_number IS NULL OR tax_number = ''"
    )).scalar()
    sonra_vn = conn.execute(text(
        "SELECT COUNT(*) FROM companies WHERE vergi_no IS NULL OR vergi_no = ''"
    )).scalar()

    return {
        "onceki": {"website_domain": onceki_web, "tax_number": onceki_tax, "vergi_no": onceki_vn},
        "guncellenen": {"website_domain": web_upd, "tax_number": tax_upd, "vergi_no": vn_upd},
        "sonra": {"website_domain": sonra_web, "tax_number": sonra_tax, "vergi_no": sonra_vn},
    }


def adim_4_rapor(conn, payload_doluluk: dict, enrich: dict, kalite) -> None:
    """Toplam firma ve oranlari raporla."""
    logger.info("Adim 4: Son durum raporu")
    sql = text("""
        SELECT
            COUNT(*) AS toplam,
            COUNT(*) FILTER (WHERE sr.raw_payload->>'adres' IS NOT NULL
                              AND sr.raw_payload->>'adres' <> '') AS adres_dolu,
            COUNT(*) FILTER (WHERE COALESCE(c.website_domain, sr.raw_website,
                                            sr.raw_payload->>'web_sitesi') IS NOT NULL
                              AND COALESCE(c.website_domain, sr.raw_website,
                                           sr.raw_payload->>'web_sitesi') <> '') AS web_dolu,
            COUNT(*) FILTER (WHERE COALESCE(c.tax_number, c.vergi_no,
                                            sr.raw_tax_number,
                                            sr.raw_payload->>'vergi_no') IS NOT NULL
                              AND COALESCE(c.tax_number, c.vergi_no,
                                           sr.raw_tax_number,
                                           sr.raw_payload->>'vergi_no') <> '') AS vergi_dolu,
            COUNT(*) FILTER (WHERE COALESCE(c.osb_parsel,
                                            sr.raw_payload->>'osb_parsel') IS NOT NULL
                              AND COALESCE(c.osb_parsel,
                                           sr.raw_payload->>'osb_parsel') <> '') AS parsel_dolu,
            AVG(c.data_quality_score) AS ort_skor
        FROM companies c
        LEFT JOIN source_records sr ON sr.source_record_id = c.source_record_id
    """)
    row = conn.execute(sql).mappings().first()
    toplam = row["toplam"] or 0

    def pct(n):
        return (n / toplam * 100.0) if toplam else 0.0

    print()
    print("=" * 70)
    print("  VERI KALITE RAPORU  -  " + datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"))
    print("=" * 70)
    print(f"Toplam firma           : {toplam}")
    print(f"Adres dolu orani       : {row['adres_dolu']:>5}  ({pct(row['adres_dolu']):.1f}%)")
    print(f"Web sitesi dolu orani  : {row['web_dolu']:>5}  ({pct(row['web_dolu']):.1f}%)")
    print(f"Vergi no dolu orani    : {row['vergi_dolu']:>5}  ({pct(row['vergi_dolu']):.1f}%)")
    print(f"OSB parsel dolu orani  : {row['parsel_dolu']:>5}  ({pct(row['parsel_dolu']):.1f}%)")
    print(f"Ortalama kalite skoru  : {row['ort_skor']:.2f}")
    print("-" * 70)
    print("source_records.raw_payload alan doluluk sayilari:")
    for k in ("adres", "web_sitesi", "vergi_no", "osb_parsel", "sektor", "nace_code"):
        print(f"  {k:<12}: {payload_doluluk[k]}")
    print("-" * 70)
    print("companies eksik -> doldurma sonucu:")
    for alan in ("website_domain", "tax_number", "vergi_no"):
        o = enrich["onceki"][alan]
        g = enrich["guncellenen"][alan]
        s = enrich["sonra"][alan]
        print(f"  {alan:<14}: onceki bos={o}, guncellenen={g}, sonra bos={s}")
    print("-" * 70)
    print("recalculate_quality_scores.py son satirlar:")
    for satir in kalite:
        print(f"  {satir}")
    print("=" * 70)


def main() -> int:
    logger.info("==== enrich_missing_fields basladi ====")
    engine = get_engine()
    # prepared statement hatasini onlemek icin connection bazinda cache kapat
    conn = engine.connect().execution_options(compiled_cache=None)
    try:
        with conn.begin():
            payload_doluluk = adim_1_payload_doluluk(conn)
            enrich = adim_2_companies_doldur(conn)
    finally:
        conn.close()

    logger.info("Adim 3: scripts/recalculate_quality_scores.py calistiriliyor")
    try:
        sonuc = subprocess.run(
            [sys.executable, str(PROJE_KOK / "scripts" / "recalculate_quality_scores.py")],
            capture_output=True, text=True, check=False, env=os.environ.copy(),
        )
        kalite_cikti = (sonuc.stdout or "") + (sonuc.stderr or "")
        logger.info(kalite_cikti)
        if sonuc.returncode != 0:
            logger.error("recalculate_quality_scores.py basarisiz oldu")
            return sonuc.returncode or 1
    except Exception as e:
        logger.exception("recalculate_quality_scores.py calistirilamadi: %s", e)
        return 1

    conn = engine.connect().execution_options(compiled_cache=None)
    try:
        adim_4_rapor(conn, payload_doluluk, enrich, kalite_cikti.strip().splitlines()[-2:])
    finally:
        conn.close()

    logger.info("==== enrich_missing_fields tamamlandi ====")
    return 0


if __name__ == "__main__":
    sys.exit(main())