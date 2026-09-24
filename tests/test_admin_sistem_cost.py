from __future__ import annotations

import json
from pathlib import Path

from web_dashboard.tabs import admin_cost


def _write_optimizer_payload(tmp_path: Path, payload: object) -> None:
    output = tmp_path / "data" / "router" / "optimizer_latest.json"
    output.parent.mkdir(parents=True)
    output.write_text(json.dumps(payload), encoding="utf-8")


def test_cost_loader_returns_empty_summary_when_source_is_missing(monkeypatch, tmp_path: Path):
    monkeypatch.chdir(tmp_path)
    admin_cost.load_cost_summary.clear()

    summary = admin_cost.load_cost_summary()

    assert summary.total_daily_cost_usd == 0.0
    assert summary.providers == []
    assert admin_cost.chart_provider_breakdown(summary) is None


def test_cost_loader_parses_provider_usage_and_anomalies(monkeypatch, tmp_path: Path):
    monkeypatch.chdir(tmp_path)
    _write_optimizer_payload(
        tmp_path,
        {
            "timestamp": "2026-09-13T12:00:00",
            "saglik": {
                "providerlar": [
                    {"provider": "alpha", "name": "Alpha", "durum": {"backoffLevel": 0, "modelLockSayisi": 0}},
                    {"provider": "beta", "durum": {"backoffLevel": 6, "modelLockSayisi": 0}},
                ]
            },
            "combo_istatistik": {
                "usageHistory": {
                    "toplam_maliyet_usd": 12.0,
                    "provider_maliyet_toplam": {"alpha": 10.0, "beta": 2.0},
                    "provider_cagri_sayisi": {"alpha": 10, "beta": 2},
                    "provider_maliyet_ort": {"alpha": 1.0, "beta": 1.0},
                },
                "requestDetails": {
                    "provider_latency_ort": {"alpha": 100, "beta": 6000},
                    "provider_status": {"alpha": {"success": 9, "error": 1}, "beta": {"success": 1, "error": 1}},
                },
            },
            "anomaliler": [{"provider": "beta", "oncelik": "YUKSEK", "nedenler": ["backoff"]}],
        },
    )
    admin_cost.load_cost_summary.clear()

    summary = admin_cost.load_cost_summary()

    assert summary.total_daily_cost_usd == 12.0
    assert summary.total_daily_calls == 12
    assert {provider.provider for provider in summary.providers} == {"alpha", "beta"}
    beta = next(provider for provider in summary.providers if provider.provider == "beta")
    assert beta.health_status == "ERROR"
    assert any(anomaly.provider == "beta" for anomaly in summary.anomalies)
    assert admin_cost.chart_provider_breakdown(summary) is not None


def test_cost_loader_returns_empty_summary_for_broken_json(monkeypatch, tmp_path: Path):
    monkeypatch.chdir(tmp_path)
    output = tmp_path / "data" / "router" / "optimizer_latest.json"
    output.parent.mkdir(parents=True)
    output.write_text("{broken json", encoding="utf-8")
    admin_cost.load_cost_summary.clear()

    summary = admin_cost.load_cost_summary()

    assert summary.total_daily_cost_usd == 0.0
    assert summary.providers == []


def test_robust_zscore_anomaly_flags_outlier():
    """UI-ADMIN-MALIYET-ANOMALI-11 (SSOT §9 K5): z = 0.6745*(deger-medyan)/MAD, |z|>3.5 alarm."""
    seri = [10.0, 11.0, 9.0, 10.0, 10.5, 9.5, 10.0]
    z = admin_cost.robust_zscore_anomaly(100.0, seri)
    assert z is not None
    assert abs(z) > 3.5


def test_robust_zscore_anomaly_mad_sifir_bolme_hatasi_vermez():
    """MAD=0 (tekdüze seri) durumunda ZeroDivisionError yerine None (anomali yok)."""
    seri = [5.0, 5.0, 5.0, 5.0]
    assert admin_cost.robust_zscore_anomaly(5.0, seri) is None
    assert admin_cost.robust_zscore_anomaly(999.0, seri) is None


def test_robust_zscore_anomaly_bos_seri_none_doner():
    assert admin_cost.robust_zscore_anomaly(10.0, []) is None
