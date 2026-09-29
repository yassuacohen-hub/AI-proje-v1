from __future__ import annotations

from unittest.mock import MagicMock

import pandas as pd

from web_dashboard.tabs import admin_quality


class _Result:
    def __init__(self, row=None, scores=None, rows=None):
        self._row = row
        self._scores = scores or []
        self._rows = rows or []

    def mappings(self):
        return self

    def first(self):
        return self._row

    def scalars(self):
        return self

    def all(self):
        return self._scores


def test_quality_loaders_return_empty_states_when_source_is_unavailable(monkeypatch):
    class _Spinner:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

    monkeypatch.setattr(admin_quality, "get_engine", MagicMock(side_effect=RuntimeError("database unavailable")))
    monkeypatch.setattr(admin_quality.st, "spinner", lambda *args, **kwargs: _Spinner())
    admin_quality.load_quality_overview.clear()
    admin_quality.load_score_distribution.clear()
    admin_quality.load_missing_field_analysis.clear()
    admin_quality.load_risky_companies.clear()

    assert admin_quality.load_quality_overview.__wrapped__()["toplam_firma"] == 0
    assert admin_quality.load_score_distribution.__wrapped__().empty
    # D-249: olculemeyen kaynak "7 alan, hepsi %0 eksik" diye sunulamaz; bos doner.
    assert admin_quality.load_missing_field_analysis.__wrapped__().empty
    assert admin_quality.load_risky_companies.__wrapped__().empty


def test_quality_overview_calculates_populated_metrics(monkeypatch):
    connection = MagicMock()
    connection.execute.side_effect = [
        _Result(row={"toplam": 4, "ort": 52.5, "min_s": 10, "max_s": 90, "riskli": 1}),
        _Result(scores=[10, 40, 70, 90]),
    ]
    engine = MagicMock()
    engine.connect.return_value.__enter__.return_value = connection
    monkeypatch.setattr(admin_quality, "get_engine", lambda: engine)
    admin_quality.load_quality_overview.clear()

    overview = admin_quality.load_quality_overview.__wrapped__()

    assert overview == {
        "toplam_firma": 4,
        "ortalama_skor": 52.5,
        "medyan_skor": 55.0,
        "min_skor": 10.0,
        "max_skor": 90.0,
        "riskli_sayisi": 1,
        "riskli_orani": 25.0,
    }


def test_quality_suggestions_handle_empty_and_populated_inputs():
    empty = admin_quality.generate_improvement_suggestions(pd.DataFrame(), {"riskli_orani": 0})
    populated = admin_quality.generate_improvement_suggestions(
        pd.DataFrame([{"Alan": "Web Sitesi", "Eksiklik (%)": 60.0}]),
        {"riskli_orani": 12.0},
    )

    assert empty == []
    assert len(populated) == 2
    assert populated[0]["Öncelik"] == "🔴 Yüksek"
    assert populated[1]["Alan"] == "Web Sitesi"
