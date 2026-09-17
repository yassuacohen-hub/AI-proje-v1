# -*- coding: utf-8 -*-
"""Test fixtures for MCP + webhook test suites.

Isolates tests from the real persistent spend log
(data/orchestrator/mcp_spend_log.jsonl) which already contains
today-spend entries and would otherwise exhaust the default
daily_spend_limit (5.0) and break unpatched tests.
"""

from __future__ import annotations

import importlib
import os
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(autouse=True)
def isolated_spend_log(tmp_path, monkeypatch):
    """Point every test at a fresh, empty spend log."""
    log_file = tmp_path / "mcp_spend_log.jsonl"
    monkeypatch.setattr(
        "company_master.mcp.policy_engine.SPEND_LOG", log_file
    )
    # Also cover any module that captured the path at import time.
    monkeypatch.setenv("MCP_SPEND_LOG", str(log_file))
    yield log_file


@pytest.fixture(autouse=True)
def _pano_dosyalari_yalitim(tmp_path, monkeypatch):
    """TEST-SYNC-01 / TEST-ISO-02: testler gercek pano dosyalarini ezemesin.

    Turetilmis (salt-okunur kabul edilen) uc dosya korunur:
      * ``AGENT_SYNC.md``        (kok senkron ozeti)
      * ``data/orchestrator/gorev_panosu.md``  (Obsidian gorunumu)
      * ``AGENT_SYNC_kopya.md``  (orchestrator kopyasi)

    Neden gerekli:
      * ``AUTO_SYNC=False`` yalnizca otomatik senkronu kapatir; panoya yazan
        bir test (or. ``tests/test_isbirligi.py``, ``tests/test_gorev_kutusu_cli.py``)
        gercek dosyalari yine uretir.
      * ``TASK_MD`` / ``AGENT_SYNC_MD`` modul import aninda ``STATE_DIR``'den
        turetilir; testte yalnizca ``STATE_DIR`` yamamak bu sabitleri
        degistirmez ve yazim gercek yola gider.
      * Testler iki farkli modul kimligi kullanabiliyor:
        ``company_master.orchestrator.task_board`` (``src/`` sys.path'te) ve
        ``src.company_master.orchestrator.task_board`` (kok sys.path'te).
        Ikisi ayri sabit nesneleridir; yalnizca biri yamalanirsa digeri
        gercek dosyayi yazmaya devam eder. Bu yuzden ikisi de yamalanir.
    """
    moduller = []
    for ad in (
        "company_master.orchestrator.task_board",
        "src.company_master.orchestrator.task_board",
    ):
        try:
            modul = importlib.import_module(ad)
        except Exception:  # noqa: BLE001 - modul yoksa koruma gerekmez
            continue
        if not any(modul is m for m in moduller):
            moduller.append(modul)
    if not moduller:  # pragma: no cover - src import edilemiyorsa atlanir
        yield
        return

    yollar = {
        "AUTO_SYNC": False,
        "AGENT_SYNC_MD": tmp_path / "AGENT_SYNC.md",
        "AGENT_SYNC_MD_KOPYA": tmp_path / "orchestrator" / "AGENT_SYNC.md",
        "TASK_MD": tmp_path / "gorev_panosu.md",
    }
    for modul in moduller:
        for ad, deger in yollar.items():
            monkeypatch.setattr(modul, ad, deger, raising=False)
    yield


@pytest.fixture(autouse=True)
def _no_real_env_secrets(monkeypatch):
    """Ensure tests never accidentally read production env secrets."""
    for key in ("APIFY_API_TOKEN", "APIFY_API_KEY", "TELEGRAM_BOT_TOKEN"):
        monkeypatch.delenv(key, raising=False)

