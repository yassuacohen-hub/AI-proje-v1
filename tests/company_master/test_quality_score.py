import pytest

import sys

from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.company_master.etl.normalize import _data_quality_score


def _row(raw_phone=None, raw_email=None, raw_website=None, website_domain=None,
         raw_tax_number=None, raw_payload=None):
    return {
        "raw_phone": raw_phone,
        "raw_email": raw_email,
        "raw_website": raw_website,
        "website_domain": website_domain,
        "raw_tax_number": raw_tax_number,
        "raw_payload": raw_payload or {},
    }


def test_full_row_scores_100():
    row = _row(
        raw_phone="0312 123 45 67",
        raw_email="info@abc.com",
        raw_website="https://abc.com",
        raw_tax_number="1234567890",
        raw_payload={
            "adres": "Ankara OSB",
            "sektor": "İmalat",
            "vergi_no": "1234567890",
            "osb_parsel": "123/45",
            "nace_code": "71.12",
        },
    )
    assert _data_quality_score(row) == 100.0


def test_empty_row_scores_0():
    row = _row()
    assert _data_quality_score(row) == 0.0


def test_missing_vergi_and_adres_penalties():
    row = _row(
        raw_phone="0312 123 45 67",
        raw_email="info@abc.com",
        raw_website="https://abc.com",
        raw_payload={"sektor": "İmalat"},
    )
    assert _data_quality_score(row) == 15.0


def test_only_vergi_no():
    row = _row(raw_tax_number="1234567890")
    assert _data_quality_score(row) == 5.0


def test_score_clamped_to_100():
    row = _row(
        raw_phone="0312 123 45 67",
        raw_email="info@abc.com",
        raw_website="https://abc.com",
        raw_tax_number="1234567890",
        raw_payload={
            "adres": "Ankara OSB",
            "sektor": "İmalat",
            "vergi_no": "1234567890",
            "osb_parsel": "123/45",
            "nace_code": "71.12",
        },
    )
    assert _data_quality_score(row) <= 100.0


def test_score_clamped_to_0():
    row = _row()
    assert _data_quality_score(row) >= 0.0
