# -*- coding: utf-8 -*-
from .scrapers.ostim_scraper import scrape_tum_osb
from .scrapers.aso_scraper import run_full_scrape
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def scrape_all():
    logging.info("ETL Pipeline başladı")

    try:
        logging.info("OSTİM scrape başlatılıyor...")
        ostim_output = Path("data/ostim/firmalar_full.jsonl")
        ostim_output.parent.mkdir(parents=True, exist_ok=True)
        scrape_tum_osb(output_path=ostim_output)
        logging.info("OSTİM scrape tamamlandı.")
    except Exception as e:
        logging.error(f"OSTİM scrape hatası: {e}")

    try:
        logging.info("ASO scrape başlatılıyor...")
        aso_dir = Path("data/aso")
        aso_dir.mkdir(parents=True, exist_ok=True)
        run_full_scrape()
        logging.info("ASO scrape tamamlandı.")
    except Exception as e:
        logging.error(f"ASO scrape hatası: {e}")

    logging.info("ETL Pipeline tamamlandı.")


if __name__ == "__main__":
    scrape_all()