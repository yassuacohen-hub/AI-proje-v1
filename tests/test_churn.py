# -*- coding: utf-8 -*-
"""Test API-ADMIN-CHURN-3SINYAL-16 (API-16): risk_etiketi_3sinyal()."""

from __future__ import annotations

import pytest
from datetime import date, timedelta

# Test edilecek modülü import et
from src.company_master.churn import risk_etiketi_3sinyal, risk_etiketi


def test_risk_etiketi_3sinyal_basit():
    """Tek sinyalle geriye dönük uyum testi."""
    bugun = date(2026, 9, 24)

    # Eski risk_etiketi hala çalışmalı
    assert risk_etiketi(bugun, bugun) == "Yok"  # 0 gün
    assert risk_etiketi(bugun - timedelta(days=13), bugun) == "Yok"  # 13 gün
    assert risk_etiketi(bugun - timedelta(days=14), bugun) == "Düşük"  # 14 gün
    assert risk_etiketi(None, bugun) == "Düşük"  # Hiç giriş yok


def test_risk_etiketi_3sinyal_3_sinyal():
    """3 sinyal formülü testi."""
    bugun = date(2026, 9, 24)

    # 3 sinyal hepsi taze (<14 gün) -> 0 sinyal -> "Yok"
    assert risk_etiketi_3sinyal(bugun, bugun, bugun, bugun) == "Yok"

    # 3 sinyal hepsi bayat (>=14 gün) -> 3 sinyal -> "Yüksek"
    eski = bugun - timedelta(days=30)
    assert risk_etiketi_3sinyal(eski, eski, eski, bugun) == "Yüksek"

    # Karışık: 1 taze, 2 bayat -> 2 sinyal -> "Orta"
    assert risk_etiketi_3sinyal(bugun, eski, eski, bugun) == "Orta"

    # None girdisi = bayat sayılmalı (riskli sinyal)
    assert risk_etiketi_3sinyal(None, None, None, bugun) == "Yüksek"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
