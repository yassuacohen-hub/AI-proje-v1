import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'src'))

from data_quality_toolkit.classifier import PIIScanner


def test_validate_tckn_valid():
    """Geçerli TCKN örnekleri."""
    assert PIIScanner.validate_tckn("10000000146") is True


def test_validate_tckn_invalid_first_zero():
    assert PIIScanner.validate_tckn("01234567890") is False


def test_validate_tckn_invalid_length():
    assert PIIScanner.validate_tckn("123") is False


def test_validate_luhn_visa():
    # Visa test numarası: 4111111111111111
    assert PIIScanner.validate_luhn_credit_card("4111111111111111") is True


def test_validate_luhn_invalid():
    assert PIIScanner.validate_luhn_credit_card("4111111111111112") is False


def test_scan_column_email():
    scanner = PIIScanner()
    samples = ["ahmet@kurumsal.com", "mehmet@sirket.com.tr", None]
    result = scanner.scan_column("email", samples)
    assert result.detected_type == "EMAIL"
    assert result.sensitivity_level.value.startswith("INTERNAL")
