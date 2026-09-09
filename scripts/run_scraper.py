#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""OSTIM scraper runner with resume support."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from company_master.etl.scrapers.ostim_scraper import scrape_tum_osb


def main() -> int:
    output = ROOT / "data/ostim/firmalar_detayli.jsonl"
    output.parent.mkdir(parents=True, exist_ok=True)
    for _ in scrape_tum_osb(output, detay_al=True):
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
