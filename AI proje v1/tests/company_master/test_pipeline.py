import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))\

from src.company_master.etl.pipeline import scrape_all


def test_scrape_all_runs_successfully():
    with patch("src.company_master.etl.pipeline.scrape_tum_osb") as mock_ostim, \
         patch("src.company_master.etl.pipeline.run_full_scrape") as mock_aso:
        scrape_all()
        mock_ostim.assert_called_once()
        mock_aso.assert_called_once()


def test_scrape_all_handles_ostim_error():
    with patch("src.company_master.etl.pipeline.scrape_tum_osb", side_effect=Exception("OSTİM error")), \
         patch("src.company_master.etl.pipeline.run_full_scrape") as mock_aso:
        scrape_all()
        mock_aso.assert_called_once()


def test_scrape_all_handles_aso_error():
    with patch("src.company_master.etl.pipeline.scrape_tum_osb") as mock_ostim, \
         patch("src.company_master.etl.pipeline.run_full_scrape", side_effect=Exception("ASO error")):
        scrape_all()
        mock_ostim.assert_called_once()
