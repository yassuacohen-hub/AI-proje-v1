#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KONTROL-KVKK-MASKELEME-31 — Admin KVKK Mode E2E Test

Test: strict ↔ lenient mod değiştirirken /api/company/{id} response'ta
PII alanların maskeleme durumunun değiştiğini doğrular.
"""
import sys
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock, call

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from company_master.api.core.normalize import apply_kvkk_mask


class TestAdminKvkkModeE2E:
    """api_admin_kvkk_mode endpoint strict→lenient geçişi E2E test."""

    def test_strict_mode_masks_pii(self):
        """Strict modda phone/email maskeli olmalı."""
        row = {
            "company_id": "test_e2e_001",
            "legal_name": "E2E Test Şti.",
            "primary_phone": "0532 123 45 67",
            "primary_email": "test@example.com",
            "website": "e2etest.com",
            "nace_code": "6202",
        }

        masked = apply_kvkk_mask(row.copy(), admin_mode="strict")

        # website, nace acik (OSINT) oldugu icin gorunur
        assert masked["website"] == "e2etest.com"
        assert masked["nace_code"] == "6202"
        # phone/email kisitli → strict modda maske
        assert masked["primary_phone"] != "0532 123 45 67"
        assert masked["primary_email"] != "test@example.com"

    def test_lenient_mode_reveals_pii(self):
        """Lenient modda phone/email açık olmalı."""
        row = {
            "company_id": "test_e2e_001",
            "legal_name": "E2E Test Şti.",
            "primary_phone": "0532 123 45 67",
            "primary_email": "test@example.com",
            "website": "e2etest.com",
            "nace_code": "6202",
        }

        masked = apply_kvkk_mask(row.copy(), admin_mode="lenient")

        # Kısıtlı alanlar lenient'de açık
        assert masked["primary_phone"] == "0532 123 45 67"
        assert masked["primary_email"] == "test@example.com"
        # website/nace hâlâ açık
        assert masked["website"] == "e2etest.com"
        assert masked["nace_code"] == "6202"

    def test_strict_to_lenient_toggle(self):
        """strict → lenient toggle: aynı row farklı maskeleme."""
        row = {
            "company_id": "test_e2e_001",
            "legal_name": "E2E Test Şti.",
            "primary_phone": "0532 123 45 67",
            "primary_email": "test@example.com",
            "website": "e2etest.com",
            "quarantine_reason": "ç1_telefon",  # Yasak alan — hep maskeli
        }

        masked_strict = apply_kvkk_mask(row.copy(), admin_mode="strict")
        masked_lenient = apply_kvkk_mask(row.copy(), admin_mode="lenient")

        # Phone/email değişir
        assert masked_strict["primary_phone"] != masked_lenient["primary_phone"]
        assert masked_strict["primary_phone"] != "0532 123 45 67"  # strict: maske
        assert masked_lenient["primary_phone"] == "0532 123 45 67"  # lenient: açık
        # Yasak alan hep maske — strict ve lenient'de aynı
        assert masked_strict["quarantine_reason"] == "***"
        assert masked_lenient["quarantine_reason"] == "***"

    def test_admin_kvkk_mode_endpoint_logic(self):
        """api_admin_kvkk_mode endpoint mantığını mock ile test et."""
        # Mock engine ve cache
        mock_engine = MagicMock()
        mock_conn = MagicMock()
        mock_engine.connect.return_value.__enter__ = MagicMock(return_value=mock_conn)
        mock_engine.connect.return_value.__exit__ = MagicMock(return_value=None)
        mock_engine.begin.return_value.__enter__ = MagicMock(return_value=mock_conn)
        mock_engine.begin.return_value.__exit__ = MagicMock(return_value=None)

        mock_mapping_row = MagicMock()
        mock_mapping_row.__getitem__ = MagicMock(side_effect=lambda k: {"mode": "strict"}[k])

        mock_conn.execute.return_value.mappings.return_value.first = MagicMock(return_value=mock_mapping_row)

        with patch("web_app.get_engine", return_value=mock_engine):
            with patch("web_app.cache_set"):
                # Import the endpoint function
                import web_app
                # Test mode validation
                with pytest.raises(Exception):
                    # Invalid mode should raise 400
                    web_app.api_admin_kvkk_mode(
                        {"mode": "invalid", "reason": "test"},
                        _auth="admin"
                    )

    def test_e2e_with_plan_field_visibility(self):
        """Layer 2 plan_field_visibility ile mask testi."""
        row = {
            "company_id": "test_e2e_001",
            "legal_name": "E2E Test Şti.",
            "primary_phone": "0532 123 45 67",
            "primary_email": "test@example.com",
            "address": "Test Mah. Test Cad. No:1",
        }

        # plan_field_visibility: terminal = kisitli
        plan_v = {"iletisim": "kisitli", "lokasyon": "kisitli"}
        masked = apply_kvkk_mask(row.copy(), admin_mode="lenient", plan_field_visibility=plan_v)

        # Lenient'de kısıtlı alanlar açık
        assert masked["primary_phone"] == "0532 123 45 67"
        assert masked["primary_email"] == "test@example.com"
        assert masked["address"] == "Test Mah. Test Cad. No:1"

        # plan_field_visibility: yasağa göre maske
        plan_v_yasak = {"iletisim": "yasak", "lokasyon": "yasak"}
        masked_yasak = apply_kvkk_mask(row.copy(), admin_mode="lenient", plan_field_visibility=plan_v_yasak)

        assert masked_yasak["primary_phone"] == "***"
        assert masked_yasak["primary_email"] == "***"
        assert masked_yasak["address"] == "***"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
