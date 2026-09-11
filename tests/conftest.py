# -*- coding: utf-8 -*-
"""Test fixtures for MCP + webhook test suites.

Isolates tests from the real persistent spend log
(data/orchestrator/mcp_spend_log.jsonl) which already contains
today-spend entries and would otherwise exhaust the default
daily_spend_limit (5.0) and break unpatched tests.
"""

from __future__ import annotations

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
def _no_real_env_secrets(monkeypatch):
    """Ensure tests never accidentally read production env secrets."""
    for key in ("APIFY_API_TOKEN", "APIFY_API_KEY", "TELEGRAM_BOT_TOKEN"):
        monkeypatch.delenv(key, raising=False)
