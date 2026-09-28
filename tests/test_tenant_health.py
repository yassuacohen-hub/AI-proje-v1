# -*- coding: utf-8 -*-
"""TEN-01 — Tenant Health Score v1 testleri (PO-BACK-01)."""

from __future__ import annotations

import pytest

from company_master.sunum import tavan_getir
from company_master.tenant.health import (
    TenantHealthScore,
    hesapla,
    esik_dokumani,
    _banti_bul,
    _identity_completeness,
    _source_reliability_score,
    _coverage_score,
    _activity_score,
    HEALTH_GREEN,
    HEALTH_YELLOW,
    WEIGHTS,
)
from company_master.tenant.model import TenantContext


# ---------------------------------------------------------------------------
# Sabitler ve yardımcı veriler
# ---------------------------------------------------------------------------

VARSAYILAN_TENANT = TenantContext("huginn", "Huginn Data", "kurumsal")
TENANT_STANDART = TenantContext("ankara_tech", "Ankara Teknoloji A.Ş.", "standart")
TENANT_TEMEL = TenantContext("istanbul_yazilim", "İstanbul Yazılım Ltd.", "temel")

# D-250/7: tamlik puani 0-10 olceginde uretilir; test verisi de tavandan
# turetilir. Sabit yazilsa agirlik seti v2 olunca testler yalan soylerdi.
TAVAN = tavan_getir()

ORNEK_FIRMALAR_GUCLU = [
    {
        "company_id": "c1",
        "identity_completeness": TAVAN,          # tavana oturmus -> %100
        "nace_code": "6201",
        "adres": "Ankara OSB",
        "son_guncelleme_gun": 5,
    },
    {
        "company_id": "c2",
        "identity_completeness": TAVAN * 0.8,    # -> %80
        "nace_code": "6202",
        "adres": "İstanbul",
        "son_guncelleme_gun": 10,
    },
]

ORNEK_FIRMALAR_ZAYIF = [
    {
        "company_id": "c1",
        "identity_completeness": TAVAN * 0.2,
        "nace_code": None,
        "adres": None,
        "son_guncelleme_gun": None,
    },
    {
        "company_id": "c2",
        "identity_completeness": TAVAN * 0.15,
        "nace_code": "",
        "adres": "",
        "son_guncelleme_gun": None,
    },
]

# ---------------------------------------------------------------------------
# Bant hesaplama testleri
# ---------------------------------------------------------------------------

def test_banti_green():
    assert _banti_bul(85.0) == "green"
    assert _banti_bul(90.0) == "green"
    assert _banti_bul(100.0) == "green"


def test_banti_yellow():
    assert _banti_bul(60.0) == "yellow"
    assert _banti_bul(75.0) == "yellow"
    assert _banti_bul(84.9) == "yellow"


def test_banti_red():
    assert _banti_bul(59.9) == "red"
    assert _banti_bul(0.0) == "red"
    assert _banti_bul(30.0) == "red"


# ---------------------------------------------------------------------------
# Bileşen formül testleri
# ---------------------------------------------------------------------------

def test_tamlik_bos():
    assert _identity_completeness([]) == 0.0


def test_tamlik_tavana_oranlanir():
    """0-10'luk puan yuzdeye cevrilir; yoksa digerleriyle toplanamaz."""
    firms = [
        {"identity_completeness": TAVAN},
        {"identity_completeness": TAVAN / 2},
    ]
    assert _identity_completeness(firms) == 75.0


def test_tamlik_olculmemis_firma_ortalamayi_dusurmez():
    """D-249: None 0 degildir; ortalamaya girmez."""
    firms = [
        {"identity_completeness": TAVAN},
        {"identity_completeness": None},
    ]
    assert _identity_completeness(firms) == 100.0


def test_tamlik_yuz_olcekli_veri_sessizce_kabul_edilmez():
    """Mandal: 0-100'luk veri sizarsa ValueError; sessizce %1500 olmaz."""
    with pytest.raises(ValueError, match="tavani"):
        _identity_completeness([{"identity_completeness": 90}])


def test_source_reliability_bos():
    assert _source_reliability_score([]) == 100.0


def test_source_reliability_aktif_yok():
    camps = [{"durum": "tamamlandi"}]
    assert _source_reliability_score(camps) == 100.0


def test_source_reliability_tam_ve_eksik():
    camps = [
        {"durum": "aktif", "tedarikci": "A", "bitis_tarihi": "2026-12-31"},
        {"durum": "aktif", "tedarikci": None, "bitis_tarihi": None},
    ]
    assert _source_reliability_score(camps) == 50.0


def test_source_reliability_hepsi_tam():
    camps = [
        {"durum": "aktif", "tedarikci": "A", "bitis_tarihi": "2026-12-31"},
        {"durum": "aktif", "tedarikci": "B", "bitis_tarihi": "2026-11-30"},
    ]
    assert _source_reliability_score(camps) == 100.0


def test_coverage_score_bos():
    assert _coverage_score([]) == 0.0


def test_coverage_score_tum_uygun():
    firms = [
        {"identity_completeness": TAVAN, "nace_code": "6201", "adres": "Ankara"},
        {"identity_completeness": TAVAN * 0.7, "nace_code": "6202", "adres": "İstanbul"},
    ]
    assert _coverage_score(firms) == 100.0


def test_coverage_score_hicbir_uygun_degil():
    firms = [
        {"identity_completeness": TAVAN * 0.2, "nace_code": None, "adres": None},
        {"identity_completeness": TAVAN * 0.3, "nace_code": "", "adres": ""},
    ]
    assert _coverage_score(firms) == 0.0


def test_coverage_score_kismi():
    firms = [
        {"identity_completeness": TAVAN, "nace_code": "6201", "adres": "Ankara"},
        {"identity_completeness": TAVAN * 0.2, "nace_code": None, "adres": None},
    ]
    assert _coverage_score(firms) == 50.0


def test_coverage_esigi_tavandan_turetilir():
    """Esik sabit 50 yazilsa 0-10 olcekte hicbir firma uygun sayilmaz,
    skor sessizce daima 0 donerdi."""
    tam_firma = [{
        "identity_completeness": TAVAN,
        "nace_code": "6201",
        "adres": "Ankara",
    }]
    assert _coverage_score(tam_firma) == 100.0, "esik hala 0-100 olceginde"


def test_activity_score_bos():
    assert _activity_score([]) == 50.0


def test_activity_score_guncel():
    firms = [
        {"son_guncelleme_gun": 5},
        {"son_guncelleme_gun": 10},
    ]
    assert _activity_score(firms) == 100.0


def test_activity_score_hic_guncel_degil():
    firms = [
        {"son_guncelleme_gun": None},
        {"son_guncelleme_gun": None},
    ]
    assert _activity_score(firms) == 0.0


def test_activity_score_kismi():
    firms = [
        {"son_guncelleme_gun": 5},
        {"son_guncelleme_gun": None},
    ]
    assert _activity_score(firms) == 50.0
ORNEK_KAMPANYALAR = [
    {"kampanya_id": "CMP-001", "durum": "aktif", "tedarikci": "Meta", "bitis_tarihi": "2026-12-31"},
    {"kampanya_id": "CMP-002", "durum": "aktif", "tedarikci": "Google", "bitis_tarihi": "2026-11-30"},
    {"kampanya_id": "CMP-003", "durum": "aktif", "tedarikci": None, "bitis_tarihi": None},
    {"kampanya_id": "CMP-004", "durum": "tamamlandi", "tedarikci": "Meta", "bitis_tarihi": "2026-08-31"},
]

ORNEK_KAMPANYALAR_TUM_EKSIK = [
    {"kampanya_id": "CMP-005", "durum": "aktif", "tedarikci": None, "bitis_tarihi": None},
]


# ---------------------------------------------------------------------------
# Ana hesaplama testi
# ---------------------------------------------------------------------------

def test_hesapla_guclu_tenant():
    """Güçlü veri kalitesinde tenant — GREEN beklenir."""
    result = hesapla(VARSAYILAN_TENANT, ORNEK_FIRMALAR_GUCLU, ORNEK_KAMPANYALAR)

    assert isinstance(result, TenantHealthScore)
    assert result.tenant_id == "huginn"
    # DQ=90 (tavanin %90'i), SR=66.67, CV=100, AC=100
    # 0.35*90 + 0.25*66.67 + 0.25*100 + 0.15*100 = 88.17 -> GREEN
    assert result.components["data_quality"] == 90.0
    assert result.overall >= HEALTH_GREEN
    assert result.band == "green"
    assert "data_quality" in result.components
    assert "source_reliability" in result.components
    assert "coverage" in result.components
    assert "activity" in result.components


def test_hesapla_zayif_tenant():
    """Zayıf veri kalitesinde tenant — RED beklenir."""
    result = hesapla(VARSAYILAN_TENANT, ORNEK_FIRMALAR_ZAYIF, ORNEK_KAMPANYALAR)

    assert result.overall < HEALTH_YELLOW
    assert result.band == "red"


def test_hesapla_orta_tenant():
    """Orta seviye tenant — YELLOW beklenir."""
    orta_firmalar = [
        {"identity_completeness": TAVAN * 0.7, "nace_code": "6201",
         "adres": "Ankara", "son_guncelleme_gun": 5},
        {"identity_completeness": TAVAN * 0.6, "nace_code": "6202",
         "adres": "", "son_guncelleme_gun": 10},
    ]
    camps = [
        {"durum": "aktif", "tedarikci": "A", "bitis_tarihi": "2026-12-31"},
        {"durum": "aktif", "tedarikci": "B", "bitis_tarihi": "2026-11-30"},
    ]
    result = hesapla(TENANT_STANDART, orta_firmalar, camps)

    assert HEALTH_YELLOW <= result.overall < HEALTH_GREEN
    assert result.band == "yellow"


def test_hesapla_kampanaysiz():
    """Kampanya verilisi olmadan hesaplama."""
    result = hesapla(TENANT_TEMEL, ORNEK_FIRMALAR_GUCLU, None)

    assert result.overall > 0
    assert result.details["kampanya_sayisi"] == 0
    # SR = 100 (bos), DQ = 90, CV = 100, AC = 100. Beklenen deger agirlik
    # setinden turetilir; sabit yazilsa agirlik degisince test yalan soylerdi.
    beklenen = round(
        WEIGHTS["data_quality"] * 90.0
        + WEIGHTS["source_reliability"] * 100.0
        + WEIGHTS["coverage"] * 100.0
        + WEIGHTS["activity"] * 100.0,
        2,
    )
    assert result.overall == beklenen


# ---------------------------------------------------------------------------
# TenantHealthScore veri yapısı testleri
# ---------------------------------------------------------------------------

def test_tenant_health_score_to_dict():
    score = TenantHealthScore(
        tenant_id="test",
        overall=75.5,
        band="yellow",
        components={"data_quality": 70.0},
        details={"firma_sayisi": 10},
    )
    d = score.to_dict()
    assert d["tenant_id"] == "test"
    assert d["overall_score"] == 75.5
    assert d["band"] == "yellow"
    assert d["components"]["data_quality"] == 70.0
    assert d["details"]["firma_sayisi"] == 10


def test_tenant_health_score_bant_otomatik():
    """__post_init__ ile bant otomatik atanmalı."""
    score_green = TenantHealthScore("t1", 90.0, "red")  # band yanlış verilmiş
    assert score_green.band == "green"  # otomatik düzeltmeli

    score_yellow = TenantHealthScore("t2", 70.0, "green")
    assert score_yellow.band == "yellow"

    score_red = TenantHealthScore("t3", 40.0, "yellow")
    assert score_red.band == "red"


# ---------------------------------------------------------------------------
# Eşik dokümanı testi
# ---------------------------------------------------------------------------

def test_esik_dokumani_icerir():
    doc = esik_dokumani()
    assert "Tenant Health Score v1" in doc
    assert str(int(HEALTH_GREEN)) in doc
    assert str(int(HEALTH_YELLOW)) in doc
    assert "Kimlik Dosyası Tamlığı" in doc
    assert "/100" not in doc, "D-250: puan 100'luk olcekte sunulamaz"
    assert "Source Reliability" in doc
    assert "Coverage" in doc
    assert "Activity" in doc
    assert "PO-BACK-01" in doc


# ---------------------------------------------------------------------------
# Ağırlık toplamı testi
# ---------------------------------------------------------------------------

def test_agirliklar_toplami_bir():
    total = sum(WEIGHTS.values())
    assert abs(total - 1.0) < 0.001

# ---------------------------------------------------------------------------
# AST / Monkeypatch testleri (TEN-02 kabul kriterleri)
# ---------------------------------------------------------------------------

import ast
import sys
from pathlib import Path


def test_admin_kpi_contains_tenant_health_call():
    """AST: admin_kpi.py içinde tenant_health_dashboard çağrısı olmalı."""
    admin_kpi_path = Path("web_dashboard/tabs/admin_kpi.py")
    assert admin_kpi_path.exists(), "admin_kpi.py bulunamadi"
    source = admin_kpi_path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    found = False
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Name) and func.id in {
                "tenant_health_dashboard",
                "_tenant_health_dashboard",
            }:
                found = True
            elif isinstance(func, ast.Attribute) and func.attr == "tenant_health_dashboard":
                found = True
    assert found, "admin_kpi.py tenant_health_dashboard çağrısı içermiyor"


def test_tenant_health_dashboard_with_mocked_streamlit(monkeypatch):
    """Monkeypatch: st.* mock'lanarak dashboard çalışmalı."""
    import streamlit as st

    # Mock all streamlit calls
    mock_markdown = lambda *a, **kw: None
    mock_metric = lambda *a, **kw: None
    mock_columns = lambda *a, **kw: [type("Col", (), {"metric": lambda *a2, **kw2: None, "__enter__": lambda s: s, "__exit__": lambda *a: None})() for _ in range(4)]
    mock_expander = lambda *a, **kw: type("Exp", (), {"text": lambda *a2, **kw2: None, "__enter__": lambda s: s, "__exit__": lambda *a: None})()
    mock_subheader = lambda *a, **kw: None
    mock_divider = lambda: None
    mock_spinner = lambda *a, **kw: type("Spin", (), {"__enter__": lambda s: s, "__exit__": lambda *a: None})()
    mock_empty = lambda: type("E", (), {"metric": lambda *a, **kw: None})()
    mock_button = lambda *a, **kw: False
    mock_cache_data = lambda *a, **kw: (lambda f: f)
    mock_rerun = lambda: None
    mock_info = lambda *a, **kw: None
    mock_warning = lambda *a, **kw: None
    mock_caption = lambda *a, **kw: None
    mock_text = lambda *a, **kw: None

    monkeypatch.setattr(st, "markdown", mock_markdown)
    monkeypatch.setattr(st, "metric", mock_metric)
    monkeypatch.setattr(st, "columns", mock_columns)
    monkeypatch.setattr(st, "expander", mock_expander)
    monkeypatch.setattr(st, "subheader", mock_subheader)
    monkeypatch.setattr(st, "divider", mock_divider)
    monkeypatch.setattr(st, "spinner", mock_spinner)
    monkeypatch.setattr(st, "empty", mock_empty)
    monkeypatch.setattr(st, "button", mock_button)
    monkeypatch.setattr(st, "cache_data", mock_cache_data)
    monkeypatch.setattr(st, "rerun", mock_rerun)
    monkeypatch.setattr(st, "info", mock_info)
    monkeypatch.setattr(st, "warning", mock_warning)
    monkeypatch.setattr(st, "caption", mock_caption)
    monkeypatch.setattr(st, "text", mock_text)

    from web_dashboard.tabs.tenant_health_dashboard import tenant_health_dashboard
    from company_master.tenant.model import TenantContext

    ctx = TenantContext("huginn", "Huginn Data", "kurumsal")
    # Should not raise with mocked streamlit
    tenant_health_dashboard(ctx, [])


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
