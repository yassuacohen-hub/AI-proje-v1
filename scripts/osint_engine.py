#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""OSINT Scraper Motoru — CLI koprusu.

Kullanim:
    python scripts/osint_engine.py status
    python scripts/osint_engine.py check ostim-detail
    python scripts/osint_engine.py run aso
    python scripts/osint_engine.py pipeline ostim-detail
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from company_master.engine.osint_engine import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))