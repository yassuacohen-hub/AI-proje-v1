#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test scraper for a single page to diagnose hangs."""
from __future__ import annotations

import logging
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from company_master.etl.scrapers.ostim_scraper import scrape_firma_full

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()],
)
log = logging.getLogger("test_scraper")

URL = "https://www.ostim.org.tr/sektorler/otomotiv-3-1"
PAGE = 2
RATE_LIMIT = 3.0

print(f"Scraping {URL} page {PAGE}...")
start = time.time()
for i, firma in enumerate(scrape_firma_full(URL, PAGE, detay_al=True)):
    print(f"  [{i+1}] {firma.unvan} | web: {firma.web_sitesi} | adres: {firma.adres[:50] if firma.adres else None}...")
    if i >= 9:
        print("  ... (limiting to first 10 firms for test)")
        break
elapsed = time.time() - start
print(f"Done in {elapsed:.1f}s")
