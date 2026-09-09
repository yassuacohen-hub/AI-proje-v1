#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

import sys
import os
import json
import logging
from pathlib import Path

# add project src to sys.path
project_root = Path(__file__).resolve().parents[2]
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

# import scoring function
from company_master.intelligence.job_intelligence.pipeline.scorer import score_all_companies

# configure logging
log_file = project_root / "logs" / "recalc_intelligence_scores.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[logging.FileHandler(log_file, encoding="utf-8"), logging.StreamHandler()],
)

def main() -> int:
    try:
        logging.info("Starting company intelligence scoring")
        result = score_all_companies()
        count = len(result) if hasattr(result, "__len__") else "unknown"
        logging.info(f"Scoring completed, processed {count} companies")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except Exception as e:
        logging.exception("Error during scoring")
        return 1

if __name__ == "__main__":
    sys.exit(main())
