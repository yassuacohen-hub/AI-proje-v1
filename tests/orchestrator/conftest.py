"""Orchestrator testleri icin ortak izolasyon.

ORCH-03: AUTO_SYNC=False ile gorev_ekle/gorev_guncelle/lock_birak/
handoff_yaz cagrilarinin gercek AGENT_SYNC.md'ye dokunmasi engellenir.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.company_master.orchestrator import task_board as tb_module


@pytest.fixture(autouse=True)
def _disable_auto_sync(monkeypatch, tmp_path):
    """Tum orchestrator testlerinde otomatik AGENT_SYNC senkronu kapali."""
    monkeypatch.setattr(tb_module, "AUTO_SYNC", False)
    # Neredeyse hicbir test bunlara dokunmaz; yine de tmp_path'e yonlendir.
    monkeypatch.setattr(tb_module, "AGENT_SYNC_MD", tmp_path / "AGENT_SYNC.md")
    monkeypatch.setattr(
        tb_module, "AGENT_SYNC_MD_KOPYA", tmp_path / "AGENT_SYNC_kopya.md"
    )
    yield
