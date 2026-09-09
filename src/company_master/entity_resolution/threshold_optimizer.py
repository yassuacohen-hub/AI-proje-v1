# -*- coding: utf-8 -*-
"""Entity resolution threshold optimizer.
0.70-0.90 aralığında VKN eşleştirme oranını optimize eder."""

import logging
from sqlalchemy import text
from company_master.db.connection import get_engine

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

MIN_THRESHOLD = 0.70
MAX_THRESHOLD = 0.90
DEFAULT_THRESHOLD = 0.80


def optimize_threshold():
    """VKN eşleştirme threshold'unu optimize et."""
    engine = get_engine()

    # Mevcut eşleştirmeleri analiz et
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT 
                CASE 
                    WHEN similarity_score >= 0.90 THEN 'high'
                    WHEN similarity_score >= 0.80 THEN 'medium'
                    ELSE 'low'
                END as quality_bucket,
                COUNT(*) as cnt
            FROM entity_matches
            WHERE match_type = 'fuzzy'
            GROUP BY 1
            ORDER BY 1 DESC
        """)).fetchall()

        # Threshold optimizasyonu için istatistikleri al
        threshold_stats = conn.execute(text("""
            SELECT 
                AVG(similarity_score) as avg_score,
                MIN(similarity_score) as min_score,
                MAX(similarity_score) as max_score,
                COUNT(*) as total
            FROM entity_matches
            WHERE match_type = 'fuzzy'
        """)).fetchone()

    if not threshold_stats:
        logger.warning("Eşleşme verisi yok. Default threshold kullanılıyor.")
        return DEFAULT_THRESHOLD

    # Mevcut threshold ile karşılaştır
    current_threshold = DEFAULT_THRESHOLD
    avg_score = float(threshold_stats.avg_score)
    total = threshold_stats.total

    logger.info(f"\nMevcut İstatistikler:")
    logger.info(f"  Ortalama benzerlik: {avg_score:.3f}")
    logger.info(f"  Min: {threshold_stats.min_score:.3f}, Max: {threshold_stats.max_score:.3f}")
    logger.info(f"  Toplam eşleşme: {total}")
    logger.info(f"  Mevcut threshold: {current_threshold}")

    # Kalite bucket'larını göster
    logger.info(f"\nKalite Dağılımı:")
    for row in result:
        logger.info(f"  {row.quality_bucket}: {row.cnt}")

    # Threshold optimizasyonu: VKN doğrulaması varsa yüksek tut, yoksa düşür
    has_vkn_matches = any(row.quality_bucket == 'high' for row in result)
    new_threshold = DEFAULT_THRESHOLD

    if has_vkn_matches:
        new_threshold = max(MIN_THRESHOLD, avg_score * 0.85)
    else:
        new_threshold = min(MAX_THRESHOLD, avg_score * 1.15)

    new_threshold = max(MIN_THRESHOLD, min(MAX_THRESHOLD, new_threshold))

    logger.info(f"\n✓ Optimizasyon tamamlandı:")
    logger.info(f"  Yeni threshold: {new_threshold:.2f} ({MIN_THRESHOLD}-{MAX_THRESHOLD})")
    logger.info(f"  VKN eşleşmeleri: {'Evet' if has_vkn_matches else 'Hayır'}")

    return new_threshold


if __name__ == "__main__":
    optimize_threshold()