
import sys
import json
from pathlib import Path

import pytest

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

# Script .gitignore'da (scripts/validate_*.py) -> CI'da yoksa atla.
validate_vkn_duplicate = pytest.importorskip("validate_vkn_duplicate")


def test_validate_vkn_format():
    assert validate_vkn_duplicate.validate_vkn(None) == (False, "missing")
    assert validate_vkn_duplicate.validate_vkn("") == (False, "missing")
    assert validate_vkn_duplicate.validate_vkn("12345") == (False, "invalid_length")
    assert validate_vkn_duplicate.validate_vkn("0" + "1" * 9) == (False, "invalid_prefix")
    assert validate_vkn_duplicate.validate_vkn("123456789A") == (False, "non_digit_chars")
    # 10-digit valid
    assert validate_vkn_duplicate.validate_vkn("1234567890") == (True, "1234567890")
    # 11-digit invalid checksum
    assert validate_vkn_duplicate.validate_vkn("12345678901") == (False, "invalid_checksum")


def test_vkn_checksum_valid():
    # 11-digit VKN with correct checksum: 12345678901 -> last digit should be 5?
    # Compute checksum for 1234567890? Let's use a known valid example.
    # 10000000001 is not real; we'll compute one.
    # Use the algorithm: d1=1,d2=2,d3=3,d4=4,d5=5,d6=6,d7=7,d8=8,
    # d9=9,d10=0 => sum_odd=1+3+5+7+9=25, sum_even=2+4+6+8+0=20,
    # check=(25*7-20)%10=155%10=5 => d11=5 => 12345678905
    assert validate_vkn_duplicate._vkn_checksum_valid("12345678905") is True
    # Invalid checksum
    assert validate_vkn_duplicate._vkn_checksum_valid("12345678906") is False


def test_compute_record_hash():
    rec = {"legal_name": "Test Inc.", "trade_name": "Test Ltd", "tax_number": "1234567890", "vergi_no": "9876543210"}
    h1 = validate_vkn_duplicate.compute_record_hash(rec)
    h2 = validate_vkn_duplicate.compute_record_hash(rec)
    assert h1 == h2
    # With custom dedup fields
    h3 = validate_vkn_duplicate.compute_record_hash(rec, ["legal_name", "tax_number"])
    assert isinstance(h3, str)


def test_apply_spam_filter():
    records = [
        {"website_domain": "example.com", "nace_code": "1234"},
        {"website_domain": "example.com", "nace_code": "1234"},
        {"website_domain": "example.com", "nace_code": "1234"},
        {"website_domain": "other.com", "nace_code": "5678"},
    ]
    filtered = validate_vkn_duplicate.apply_spam_filter(records, max_records_per_domain=2, max_records_per_nace=2)
    # First two kept, third dropped (domain limit), fourth kept (different domain)
    assert len(filtered) == 3


def test_full_pipeline_min_score(tmp_path):
    test_data = [
        {"legal_name": "A", "trade_name": "A",
         "tax_number": "1234567890", "vergi_no": "1234567890",
         "website_domain": "a.com", "nace_code": "1000",
         "primary_email": "a@a.com"},
        {"legal_name": "B", "trade_name": "B",
         "tax_number": "0987654321", "vergi_no": "0987654321",
         "website_domain": "b.com", "nace_code": "2000"},
        {"legal_name": "C", "trade_name": "C",
         "tax_number": "1111111111", "vergi_no": "1111111111",
         "website_domain": "c.com", "nace_code": "3000"},
    ]
    in_file = tmp_path / "in.jsonl"
    out_file = tmp_path / "out.jsonl"
    with open(in_file, "w", encoding="utf-8") as f:
        for r in test_data:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    validate_vkn_duplicate.main([
        str(in_file),
        str(out_file),
        "--min-score", "100"
    ])
    # Verify output file created
    assert out_file.exists()


if __name__ == "__main__":
    # Allow running via pytest
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))
