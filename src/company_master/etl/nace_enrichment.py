# -*- coding: utf-8 -*-
"""NACE enrichment: 1266 sektörsüz firma için NACE kodu tahmini."""

import logging
import pandas as pd
from difflib import SequenceMatcher
from sqlalchemy import text
from company_master.db.connection import get_engine

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# NACE kodları ve açıklamaları (sektör tanımlayıcı kelimeler)
NACE_PATTERNS = {
    "28": {"name": "Makine ve Ekipman İmalatı", "keywords": ["makine", "torna", "cnc", "imalat", "üretim", "pres", "döküm", "tasarım", "montaj"]},
    "25": {"name": "Metal Ürünleri İmalatı", "keywords": ["metal", "sac", "boru", "profil", "paslanmaz", "çelik", "alüminyum", "demir"]},
    "26": {"name": "Bilgisayar, Elektronik Ürünler", "keywords": ["elektronik", "bilgisayar", "yazılım", "donanım", "PCB", "ar-ge", "otomasyon"]},
    "27": {"name": "Elektrikli Ekipman İmalatı", "keywords": ["elektrik", "kablo", "trafo", "jeneratör", "motor", "panjur", "LED"]},
    "62": {"name": "Yazılım ve Danışmanlık", "keywords": ["yazılım", "bilgi işlem", "danışmanlık", "IT", "sistem"]},
    "45": {"name": "Motorlu Araç Ticareti ve Onarımı", "keywords": ["oto", "araç", "otomotiv", "garaj", "servis", "lastik"]},
    "46": {"name": "Toptan Ticaret", "keywords": ["toptan", "ithalat", "ihracat", "ticaret"]},
    "47": {"name": "Perakende Ticaret", "keywords": ["perakende", "mağaza", "satış"]},
    "33": {"name": "Makine Ekipman Kurulum ve Onarım", "keywords": ["kurulum", "onarım", "bakım", "servis", "montaj"]},
    "71": {"name": "Mimarlık ve Mühendislik", "keywords": ["mühendislik", "mimarlık", "proje", "danışmanlık", "inşaat"]},
}


def calculate_similarity(text1: str, text2: str) -> float:
    """İki metin arasındaki benzerlik oranını hesapla."""
    if not text1 or not text2:
        return 0.0
    return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()


def infer_nace_code(trade_name: str, legal_name: str = "") -> str:
    """Firma isminden NACE kodu tahmin et."""
    combined_text = f"{trade_name} {legal_name}".lower()

    best_score = 0
    best_nace = None

    for nace_code, pattern_data in NACE_PATTERNS.items():
        for keyword in pattern_data["keywords"]:
            score = calculate_similarity(combined_text, keyword)
            if score > best_score:
                best_score = score
                best_nace = nace_code

    # Minimum eşleşme threshold
    if best_score > 0.3:
        return best_nace
    return None


def run_enrichment():
    """NACE enrichment işlemini çalıştır."""
    engine = get_engine()

    # Sektörsüz firmaları al
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT company_id, legal_name, trade_name
            FROM companies
            WHERE is_ankara = TRUE
            AND (nace_code IS NULL OR nace_code = '')
            LIMIT 1266
        """))
        companies = result.fetchall()

    if not companies:
        logger.info("Enrich edilecek firma yok.")
        return 0

    logger.info(f"NACE enrichment başlatılıyor: {len(companies)} firma")

    enriched = 0
    for company_id, legal_name, trade_name in companies:
        nace_code = infer_nace_code(trade_name or "", legal_name or "")
        if nace_code:
            conn.execute(text("""
                UPDATE companies SET nace_code = :nace WHERE company_id = :cid
            """), {"nace": nace_code, "cid": company_id})
            enriched += 1

    logger.info(f"✓ {enriched}/{len(companies)} firma için NACE kodu tahmin edildi.")

    # Özet istatistikler
    with engine.connect() as conn:
        stats = conn.execute(text("""
            SELECT nace_code, COUNT(*) as cnt
            FROM companies
            WHERE is_ankara = TRUE AND nace_code IS NOT NULL AND nace_code != ''
            GROUP BY nace_code
            ORDER BY cnt DESC
            LIMIT 10
        """)).fetchall()

    logger.info("\nEn Yaygın NACE Kodları:")
    for row in stats:
        logger.info(f"  {row.nace_code}: {row.cnt} firma")

    return enriched


if __name__ == "__main__":
    run_enrichment()