#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Alternatif kaynaklardan eksik alanlari doldur + kalite raporu."""

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
LOG_DOSYA = LOG_KLASOR / "enrich_alternative_sources.log"

logger = logging.getLogger("enrich_alternative_sources")
logger.setLevel(logging.INFO)
_fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
_fh = logging.FileHandler(LOG_DOSYA, encoding="utf-8")
_fh.setFormatter(_fmt)
_sh = logging.StreamHandler()
_sh.setFormatter(_fmt)
logger.addHandler(_fh)
logger.addHandler(_sh)


ADIM_1_VERGI_NO_SQL = text("""
    UPDATE companies c
    SET tax_number = vkn.vkn,
        vergi_no  = vkn.vkn
    FROM (
        SELECT sr.source_record_id,
               (regexp_matches(
                   sr.raw_payload->>'unvan',
                   '([0-9]{10,11})',
                   'g'
               ))[1] AS vkn
        FROM source_records sr
        WHERE sr.raw_payload->>'unvan' IS NOT NULL
          AND sr.raw_payload->>'unvan' <> ''
    ) vkn
    WHERE c.source_record_id = vkn.source_record_id
      AND vkn.vkn IS NOT NULL
      AND (c.tax_number IS NULL OR c.tax_number = '')
      AND (c.vergi_no  IS NULL OR c.vergi_no  = '')
""")


ADIM_2_PARSEL_SQL = text("""
    UPDATE companies c
    SET osb_parsel = parsel.parsel
    FROM (
        SELECT sr.source_record_id,
               (
                   SELECT trim(line)
                   FROM unnest(string_to_array(sr.raw_payload->>'adres', E'\n')) AS line
                   WHERE line ILIKE '%PARSEL%' OR line ILIKE '%ADA%'
                   LIMIT 1
               ) AS parsel
        FROM source_records sr
        WHERE sr.raw_payload->>'adres' IS NOT NULL
          AND sr.raw_payload->>'adres' <> ''
    ) parsel
    WHERE c.source_record_id = parsel.source_record_id
      AND parsel.parsel IS NOT NULL
      AND (c.osb_parsel IS NULL OR c.osb_parsel = '')
""")


ADIM_3_WEB_TEMIZLE_SQL = text("""
    UPDATE companies c
    SET website_domain = NULL
    FROM source_records sr
    WHERE c.source_record_id = sr.source_record_id
      AND (
            sr.raw_payload->>'web_sitesi' ILIKE '%/Home/OstimMain%'
         OR LOWER(sr.raw_payload->>'web_sitesi') = 'ostimonline.com'
         OR LOWER(sr.raw_payload->>'web_sitesi') = 'www.ostimonline.com'
         OR COALESCE(NULLIF(sr.raw_payload->>'web_sitesi', ''), '') = ''
      )
      AND c.website_domain IS NOT NULL
""")


ADIM_3_WEB_DOLDUR_SQL = text("""
    UPDATE companies c
    SET website_domain = LOWER(TRIM(sr.raw_payload->>'web_sitesi'))
    FROM source_records sr
    WHERE c.source_record_id = sr.source_record_id
      AND (c.website_domain IS NULL OR c.website_domain = '')
      AND sr.raw_payload ? 'web_sitesi'
      AND NULLIF(TRIM(sr.raw_payload->>'web_sitesi'), '') IS NOT NULL
      AND LOWER(sr.raw_payload->>'web_sitesi') NOT LIKE '%/Home/OstimMain%'
      AND LOWER(sr.raw_payload->>'web_sitesi') <> 'ostimonline.com'
      AND LOWER(sr.raw_payload->>'web_sitesi') <> 'www.ostimonline.com'
      AND LOWER(sr.raw_payload->>'web_sitesi') NOT LIKE 'ostim.org.tr%'
""")


ADIM_5_RAPOR_SQL = text("""
    SELECT
        COUNT(*) AS toplam,
        COUNT(*) FILTER (WHERE COALESCE(sr.raw_payload->>'adres', '') <> '') AS adres_dolu,
        COUNT(*) FILTER (WHERE COALESCE(c.website_domain,
                                        sr.raw_payload->>'web_sitesi') <> '') AS web_dolu,
        COUNT(*) FILTER (WHERE COALESCE(c.tax_number, c.vergi_no,
                                        sr.raw_payload->>'vergi_no') <> '') AS vergi_dolu,
        COUNT(*) FILTER (WHERE COALESCE(c.osb_parsel,
                                        sr.raw_payload->>'osb_parsel') <> '') AS parsel_dolu,
        AVG(c.data_quality_score) AS ort_skor
    FROM companies c
    LEFT JOIN source_records sr ON sr.source_record_id = c.source_record_id
""")


def main() -> int:
    logger.info("==== enrich_alternative_sources basladi ====")
    engine = get_engine()

    with engine.begin() as conn:
        logger.info("Adim 1: unvan icinden VKN regex fallback")
        vkn_onceki = conn.execute(text(
            "SELECT COUNT(*) FROM companies WHERE tax_number IS NULL OR tax_number = ''"
        )).scalar() or 0
        vkn_upd = conn.execute(ADIM_1_VERGI_NO_SQL).rowcount
        vkn_sonra = conn.execute(text(
            "SELECT COUNT(*) FROM companies WHERE tax_number IS NULL OR tax_number = ''"
        )).scalar() or 0
        logger.info("Vergi_no: onceki bos=%d, guncellenen=%d, sonra bos=%d",
                    vkn_onceki, vkn_upd, vkn_sonra)

        logger.info("Adim 2: adres icinden PARSEL/ADA fallback")
        parsel_onceki = conn.execute(text(
            "SELECT COUNT(*) FROM companies WHERE osb_parsel IS NULL OR osb_parsel = ''"
        )).scalar() or 0
        parsel_upd = conn.execute(ADIM_2_PARSEL_SQL).rowcount
        parsel_sonra = conn.execute(text(
            "SELECT COUNT(*) FROM companies WHERE osb_parsel IS NULL OR osb_parsel = ''"
        )).scalar() or 0
        logger.info("OSB parsel: onceki bos=%d, guncellenen=%d, sonra bos=%d",
                    parsel_onceki, parsel_upd, parsel_sonra)

        logger.info("Adim 3a: jenerik web_sitesi NULL isaretleniyor")
        web_temiz_upd = conn.execute(ADIM_3_WEB_TEMIZLE_SQL).rowcount
        logger.info("Web temizleme (NULL yapilan): %d", web_temiz_upd)

        logger.info("Adim 3b: firma-ozgu web_sitesi website_domain'e yaziliyor")
        web_onceki = conn.execute(text(
            "SELECT COUNT(*) FROM companies WHERE website_domain IS NULL OR website_domain = ''"
        )).scalar() or 0
        web_upd = conn.execute(ADIM_3_WEB_DOLDUR_SQL).rowcount
        web_sonra = conn.execute(text(
            "SELECT COUNT(*) FROM companies WHERE website_domain IS NULL OR website_domain = ''"
        )).scalar() or 0
        logger.info("Website_domain: onceki bos=%d, guncellenen=%d, sonra bos=%d",
                    web_onceki, web_upd, web_sonra)

    logger.info("Adim 4: scripts/recalculate_quality_scores.py calistiriliyor")
    kalite_cikti = ""
    try:
        sonuc = subprocess.run(
            [sys.executable, str(PROJE_KOK / "scripts" / "recalculate_quality_scores.py")],
            capture_output=True, text=True, check=False, env=os.environ.copy(),
        )
        kalite_cikti = (sonuc.stdout or "") + (sonuc.stderr or "")
        logger.info(kalite_cikti.strip())
        if sonuc.returncode != 0:
            logger.error("recalculate_quality_scores.py basarisiz oldu")
            return sonuc.returncode or 1
    except Exception as exc:
        logger.exception("recalculate_quality_scores.py calistirilamadi: %s", exc)
        return 1

    logger.info("Adim 5: Son durum raporu")
    with engine.connect() as conn:
        row = conn.execute(ADIM_5_RAPOR_SQL).mappings().first()
        toplam = row["toplam"] or 0

        def pct(n):
            return (n / toplam * 100.0) if toplam else 0.0

        print()
        print("=" * 72)
        print("  ALTERNATIF KAYNAK ENRICH RAPORU - " +
              datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"))
        print("=" * 72)
        print(f"Toplam firma           : {toplam}")
        print(f"Adres dolu orani       : {row['adres_dolu']:>5}  ({pct(row['adres_dolu']):.1f}%)")
        print(f"Web sitesi dolu orani  : {row['web_dolu']:>5}  ({pct(row['web_dolu']):.1f}%)")
        print(f"Vergi_no dolu orani    : {row['vergi_dolu']:>5}  ({pct(row['vergi_dolu']):.1f}%)")
        print(f"OSB parsel dolu orani  : {row['parsel_dolu']:>5}  ({pct(row['parsel_dolu']):.1f}%)")
        print(f"Ortalama kalite skoru  : {row['ort_skor']:.2f}")
        print("-" * 72)
        print("Fallback guncellemeleri:")
        print(f"  vergi_no    : {vkn_upd:>5} kayit (kalan bos: {vkn_sonra})")
        print(f"  osb_parsel  : {parsel_upd:>5} kayit (kalan bos: {parsel_sonra})")
        print(f"  website_dom : {web_upd:>5} doldurulan, {web_temiz_upd:>5} NULL yapilan (kalan bos: {web_sonra})")
        print("-" * 72)
        print("recalculate_quality_scores.py son cikti:")
        for satir in kalite_cikti.strip().splitlines()[-2:]:
            print(f"  {satir}")
        print("-" * 72)
        print("Sonraki adim onerisi:")
        if vkn_sonra > toplam * 0.5:
            print("  -> vergi_no >50% bos: detay scrape gerekli (ingest_ostim_detail.py).")
        if parsel_sonra > toplam * 0.9:
            print("  -> osb_parsel >90% bos: detay sayfada parsel alani yok; ek kaynak (OSB kroki / belediye) entegre edilmeli.")
        if row["ort_skor"] is None or row["ort_skor"] < 50:
            print("  -> Ortalama kalite <50: onceliklendirme icin ingest_ostim_detail.py sonrasi bu script tekrar calistirilmali.")
        print("=" * 72)

    logger.info("==== enrich_alternative_sources tamamlandi ====")
    return 0


if __name__ == "__main__":
    sys.exit(main())
