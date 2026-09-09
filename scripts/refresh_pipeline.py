#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Zamanlanmış scrape workflow - günlük refresh.

Kullanım:
    # Linux/macOS (cron)
    0 3 * * * /usr/bin/python3 /path/to/refresh_pipeline.py >> /var/log/huginn_scrape.log 2>&1

    # Windows Task Scheduler
    # schtasks /create /tn "Huginn Daily Scrape" /tr "python C:\Projeler\Huginn Data Insights\scripts\refresh_pipeline.py" /sc daily /st 03:00

    # Docker
    # docker run --restart unless-stopped -v $(pwd):/app crontab -e
    # 0 3 * * * python /app/scripts/refresh_pipeline.py
"""

import os
import sys
import logging
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

# Proje kökünü Python path'e ekle
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(ROOT / "logs" / "scrape_refresh.log"),
        logging.StreamHandler(),
    ]
)
logger = logging.getLogger(__name__)


def log_start():
    logger.info("=" * 60)
    logger.info(f"Zamanlanmış Scrape Başladı: {datetime.now():%Y-%m-%d %H:%M:%S}")
    logger.info("=" * 60)


def log_end(success: bool, duration: float):
    status = "BAŞARILI" if success else "HATALARLA TAMAMLANDI"
    logger.info(f"\nZamanlanmış Scrape {status}: {duration:.1f} saniye")


def step_scrape() -> bool:
    """1. Adım: Tüm OSB'leri scrape et."""
    logger.info("[1/4] OSB scrape başlatılıyor...")
    try:
        from src.company_master.etl.pipeline import scrape_all
        scrape_all()
        logger.info("[1/4] ✓ OSB scrape tamamlandı")
        return True
    except Exception as e:
        logger.error(f"[1/4] ✗ OSB scrape hatası: {e}")
        return False


def step_detail_scrape() -> bool:
    """2. Adım: OSTİM detay sayfalarını scrape et."""
    logger.info("[2/4] OSTİM detay scrape başlatılıyor...")
    try:
        from src.company_master.etl.ostim_detail_scraper import run_scraper
        run_scraper()
        logger.info("[2/4] ✓ OSTİM detay scrape tamamlandı")
        return True
    except Exception as e:
        logger.error(f"[2/4] ✗ OSTİM detay scrape hatası: {e}")
        return False


def step_ingest() -> bool:
    """3. Adım: Verileri PostgreSQL'e ingest et."""
    logger.info("[3/4] Veri ingest başlatılıyor...")
    try:
        from src.company_master.etl.ingest_aso import ingest_aso_data
        ingest_aso_data()
        logger.info("[3/4] ✓ Veri ingest tamamlandı")
        return True
    except Exception as e:
        logger.error(f"[3/4] ✗ Veri ingest hatası: {e}")
        return False


def step_quality_recalc() -> bool:
    """4. Adım: Kalite skorlarını recalc et."""
    logger.info("[4/4] Kalite skoru recalc başlatılıyor...")
    try:
        from src.company_master.etl.quality_recalc import recalc_quality_scores
        recalc_quality_scores()
        logger.info("[4/4] ✓ Kalite skoru recalc tamamlandı")
        return True
    except Exception as e:
        logger.error(f"[4/4] ✗ Kalite skoru recalc hatası: {e}")
        return False


def update_task_board(status: str, details: str):
    """Task board JSON'unu güncelle."""
    board_path = ROOT / "data" / "orchestrator" / "task_board.json"
    if not board_path.exists():
        return
    
    import json
    with open(board_path, "r", encoding="utf-8") as f:
        board = json.load(f)
    
    # daily_scrape görevini güncelle
    for task in board:
        if task.get("task_id") == "daily_scrape":
            task["durum"] = status
            task["bitis"] = datetime.now().isoformat()
            task["not"] = details
    
    with open(board_path, "w", encoding="utf-8") as f:
        json.dump(board, f, ensure_ascii=False, indent=2)


def main():
    """Ana çalıştırma."""
    start_time = datetime.now()
    log_start()
    
    results = []
    results.append(("Scrape", step_scrape()))
    results.append(("Detay Scrape", step_detail_scrape()))
    results.append(("Ingest", step_ingest()))
    results.append(("Quality Recalc", step_quality_recalc()))
    
    duration = (datetime.now() - start_time).total_seconds()
    success = all(r[1] for r in results)
    
    # Detaylı sonuç logla
    logger.info("\n--- Adım Sonuçları ---")
    for name, ok in results:
        logger.info(f"  {name}: {'✓' if ok else '✗'}")
    
    # Task board güncelle
    details = "; ".join(f"{n}: {'OK' if ok else 'FAIL'}" for n, ok in results)
    update_task_board("done" if success else "partial", details)
    
    log_end(success, duration)
    
    # Başarısız ise exit code > 0
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()