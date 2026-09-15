# -*- coding: utf-8 -*-
"""Decision Log mekanizmasinin testleri."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.decision_log import (
    DECISION_LOG,
    read_decisions,
    log_decision,
    search_decisions,
)


@pytest.fixture
def temp_decision_log(tmp_path, monkeypatch):
    """Testler icin gecici decision_log dosyasi."""
    log_file = tmp_path / "decision_log.jsonl"
    log_file.write_text("", encoding="utf-8")
    monkeypatch.setattr("scripts.decision_log.DECISION_LOG", log_file)
    return log_file


def test_read_empty_when_missing(temp_decision_log):
    """Mevcut olmayan dosya icin [] dondugunu kontrol eder."""
    temp_decision_log.unlink()
    assert read_decisions() == []


def test_log_and_read(temp_decision_log):
    """log_decision sonra read_decisions ile okunur; son girin title aynidir."""
    entry = log_decision(
        title="Test Karari",
        decision="accepted",
        decider="test",
        reason="unit test",
        tags=["test", "unit"],
    )
    entries = read_decisions()
    assert len(entries) == 1
    assert entries[-1]["title"] == "Test Karari"
    assert entry["title"] == "Test Karari"
    assert entry["decision"] == "accepted"
    assert entry["decider"] == "test"
    assert entry["tags"] == ["test", "unit"]


def test_log_decision_uses_empty_tags_by_default(temp_decision_log):
    """tags verilmezse kayit bos liste ve UTC timestamp icermelidir."""
    entry = log_decision(
        title="Varsayilan etiket testi",
        decision="deferred",
        decider="copilot",
        reason="Daha fazla veri gerekiyor",
    )

    assert entry["tags"] == []
    assert entry["ts"].endswith("+00:00")
    assert entry["title"] == "Varsayilan etiket testi"
    assert entry["decision"] == "deferred"
    assert entry["decider"] == "copilot"
    assert entry["reason"] == "Daha fazla veri gerekiyor"
    assert read_decisions() == [entry]


def test_search(temp_decision_log):
    """Keyword ile arama yapip girin dondugunu kontrol eder."""
    log_decision(
        title="VKN stratejisi",
        decision="accepted",
        decider="mimar",
        reason="schema uyumu",
        tags=["schema"],
    )
    log_decision(
        title="Baska karar",
        decision="rejected",
        decider="user",
        reason="MVP disinda",
        tags=["mvp"],
    )
    vkn_results = search_decisions("VKN")
    assert len(vkn_results) == 1
    assert vkn_results[0]["title"] == "VKN stratejisi"

    mvp_results = search_decisions("mvp")
    assert len(mvp_results) == 1
    assert mvp_results[0]["title"] == "Baska karar"


def test_import():
    """Fonksiyonlar import edilebildigini kontrol eder."""
    from scripts.decision_log import read_decisions, log_decision, search_decisions
    assert callable(read_decisions)
    assert callable(log_decision)
    assert callable(search_decisions)
