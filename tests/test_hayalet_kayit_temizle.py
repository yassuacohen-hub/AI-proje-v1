# -*- coding: utf-8 -*-
"""Hayalet kayıt temizleme testleri."""
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from company_master.etl.hayalet_kayit_temizle import (
    CompanyRecord, select_keeper, merge_records, run_cleanup
)


def make_record(company_id: str, legal_name: str, **kwargs) -> CompanyRecord:
    """Test için CompanyRecord oluşturur (varsayılanlar None)."""
    defaults = {
        "trade_name": None, "company_type": None, "tax_number": None,
        "mersis_number": None, "establishment_date": None, "status": None,
        "status_confidence": None, "employee_count": None, "website_domain": None,
        "primary_phone": None, "primary_email": None, "description": None,
        "is_ankara": None, "is_osb_member": None, "osb_id": None,
        "nace_validity": None, "quarantine_reason": None, "data_quality_score": None,
        "entity_confidence": None,
        "osb_parcel": None, "first_seen_at": None, "last_verified_at": None,
        "created_at": None, "updated_at": None,
    }
    defaults.update(kwargs)
    return CompanyRecord(company_id=company_id, legal_name=legal_name, **defaults)


class TestCompanyRecord:
    """CompanyRecord veri sınıfı testleri."""

    def test_filled_field_count(self):
        """Dolu alan sayımı doğru mu?"""
        rec = make_record("1", "TEST FIRMA", trade_name="TEST", tax_number="1234567890", primary_phone="5551234567", website_domain="test.com")
        assert rec.filled_field_count() == 4  # trade_name, tax_number, primary_phone, website_domain

    def test_has_tax_number_tax_number(self):
        """tax_number dolu olduğunda True döner."""
        rec = make_record("1", "TEST", tax_number="123")
        assert rec.has_tax_number() is True

    def test_has_tax_number_bos(self):
        """D-254: tek kaynak tax_number; bos dize False sayilir."""
        rec = make_record("1", "TEST", tax_number="")
        assert rec.has_tax_number() is False


class TestSelectKeeper:
    """Keeper seçim mantığı testleri."""

    def test_tax_number_priority(self):
        """Vergi numarası olan kayıt öncelikli."""
        rec1 = make_record("1", "TEST", tax_number="123")
        rec2 = make_record("2", "TEST", trade_name="A", primary_phone="1")
        keeper = select_keeper([rec1, rec2])
        assert keeper.company_id == "1"

    def test_filled_field_count_priority(self):
        """Vergi numarası yoksa dolu alan sayısı öncelikli."""
        rec1 = make_record("1", "TEST", trade_name="A")
        rec2 = make_record("2", "TEST", trade_name="B", primary_phone="1", website_domain="b.com")
        keeper = select_keeper([rec1, rec2])
        assert keeper.company_id == "2"

    def test_company_id_tiebreaker(self):
        """Alan sayısı eşitse küçük company_id kazanır."""
        rec1 = make_record("1", "TEST", trade_name="A")
        rec2 = make_record("2", "TEST", primary_phone="1")
        keeper = select_keeper([rec1, rec2])
        assert keeper.company_id == "1"


class TestMergeRecords:
    """Kayıt birleştirme testleri."""

    def test_merge_fills_empty_fields(self):
        """Keeper'ın boş alanları duplicate'dan doldurulur."""
        keeper = make_record("1", "TEST", trade_name="K")
        dup = make_record("2", "TEST", primary_phone="555", website_domain="dup.com")

        merged = merge_records(keeper, [dup])

        assert merged.trade_name == "K"  # keeper'ın olduğu korunur
        assert merged.primary_phone == "555"  # duplicate'dan alınır
        assert merged.website_domain == "dup.com"  # duplicate'dan alınır

    def test_keeper_field_not_overwritten(self):
        """Keeper'ın dolu alanı duplicate ile ezilmez."""
        keeper = make_record("1", "TEST", trade_name="KEEPER")
        dup = make_record("2", "TEST", trade_name="DUP")

        merged = merge_records(keeper, [dup])

        assert merged.trade_name == "KEEPER"


class TestRunCleanup:
    """run_cleanup entegrasyon testleri (mock ile)."""

    @patch("company_master.etl.hayalet_kayit_temizle.get_engine")
    def test_no_duplicates(self, mock_get_engine):
        """Tekrarlayan kayıt yoksa 0 silinir."""
        mock_engine = MagicMock()
        mock_conn = MagicMock()
        mock_result = MagicMock()
        # Row objects with named attributes
        row1 = MagicMock()
        row1.company_id = "1"
        row1.legal_name = "FIRMA A"
        row1.trade_name = None
        row1.company_type = None
        row1.tax_number = None
        row1.mersis_number = None
        row1.establishment_date = None
        row1.status = None
        row1.status_confidence = None
        row1.employee_count = None
        row1.website_domain = None
        row1.primary_phone = None
        row1.primary_email = None
        row1.description = None
        row1.is_ankara = None
        row1.is_osb_member = None
        row1.osb_id = None
        row1.nace_validity = None
        row1.quarantine_reason = None
        row1.data_quality_score = None
        row1.entity_confidence = None
        row1.osb_parcel = None
        row1.first_seen_at = None
        row1.last_verified_at = None
        row1.created_at = None
        row1.updated_at = None

        row2 = MagicMock()
        row2.company_id = "2"
        row2.legal_name = "FIRMA B"
        for attr in ["trade_name", "company_type", "tax_number", "mersis_number",
                     "establishment_date", "status", "status_confidence", "employee_count",
                     "website_domain", "primary_phone", "primary_email", "description",
                     "is_ankara", "is_osb_member", "osb_id", "nace_validity",
                     "quarantine_reason", "data_quality_score", "entity_confidence",
                     "osb_parcel", "first_seen_at",
                     "last_verified_at", "created_at", "updated_at"]:
            setattr(row2, attr, None)

        mock_result.fetchall.return_value = [row1, row2]
        mock_conn.execute.return_value = mock_result
        mock_engine.connect.return_value.__enter__.return_value = mock_conn
        mock_get_engine.return_value = mock_engine

        result = run_cleanup(dry_run=True)

        assert result["deleted"] == 0
        assert result["merged"] == 0

    @patch("company_master.etl.hayalet_kayit_temizle.get_engine")
    def test_with_duplicates_dry_run(self, mock_get_engine):
        """Tekrarlayan kayıt varsa dry-run doğru raporlar."""
        mock_engine = MagicMock()
        mock_conn = MagicMock()
        mock_result = MagicMock()

        def make_row(cid, lname, **kwargs):
            row = MagicMock()
            row.company_id = cid
            row.legal_name = lname
            defaults = {
                "trade_name": None, "company_type": None, "tax_number": None,
                "mersis_number": None, "establishment_date": None, "status": None,
                "status_confidence": None, "employee_count": None, "website_domain": None,
                "primary_phone": None, "primary_email": None, "description": None,
                "is_ankara": None, "is_osb_member": None, "osb_id": None,
                "nace_validity": None, "quarantine_reason": None, "data_quality_score": None,
                "entity_confidence": None,
                "osb_parcel": None, "first_seen_at": None, "last_verified_at": None,
                "created_at": None, "updated_at": None,
            }
            defaults.update(kwargs)
            for k, v in defaults.items():
                setattr(row, k, v)
            return row

        mock_result.fetchall.return_value = [
            make_row("1", "FIRMA A", trade_name="T1", tax_number="123"),
            make_row("2", "FIRMA A", trade_name="T2"),
            make_row("3", "FIRMA B", trade_name="T3"),
            make_row("4", "FIRMA B", tax_number="456"),
            make_row("5", "FIRMA B"),
        ]
        mock_conn.execute.return_value = mock_result
        mock_engine.connect.return_value.__enter__.return_value = mock_conn
        mock_get_engine.return_value = mock_engine

        # get_related_records için de mock
        with patch("company_master.etl.hayalet_kayit_temizle.get_related_records", return_value={}):
            result = run_cleanup(dry_run=True)

        # FIRMA A: 2 kayıt -> 1 silinecek, FIRMA B: 3 kayıt -> 2 silinecek = toplam 3
        assert result["deleted"] == 3
        assert result["merged"] == 2
        assert result["dry_run"] is True
        # dry-run DİSKE YAZMAZ: yedek yolu dönmez, üretim dizini kirlenmez
        assert result["backup_path"] is None
        assert not list(Path("data/backup").glob("hayalet_*.jsonl"))


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
