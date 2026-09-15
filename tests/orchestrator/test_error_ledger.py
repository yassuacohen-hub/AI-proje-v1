"""Tests for orchestrator error ledger."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pytest

from src.company_master.orchestrator.error_ledger import ErrorLedger
from src.company_master.orchestrator.models import ErrorLedgerEntry


def test_error_ledger_add_and_list(tmp_path):
    ledger = ErrorLedger(tmp_path / "ledger.json")
    entry = ErrorLedgerEntry(task_id="TSK-001", agent_id="cursor_grok", error_type="timeout")
    ledger.add(entry)
    entries = ledger.all()
    assert len(entries) == 1
    assert entries[0]["task_id"] == "TSK-001"


def test_error_ledger_by_task(tmp_path):
    ledger = ErrorLedger(tmp_path / "ledger.json")
    ledger.add_dict({"task_id": "TSK-001", "agent_id": "cursor_grok", "error_type": "timeout"})
    ledger.add_dict({"task_id": "TSK-002", "agent_id": "copilot", "error_type": "crash"})
    assert len(ledger.by_task("TSK-001")) == 1
    assert len(ledger.by_task("TSK-002")) == 1
    assert len(ledger.by_agent("cursor_grok")) == 1


def test_error_ledger_persistence(tmp_path):
    path = tmp_path / "ledger.json"
    ledger1 = ErrorLedger(path)
    ledger1.add(ErrorLedgerEntry(task_id="TSK-1", agent_id="a", error_type="t"))
    ledger2 = ErrorLedger(path)
    assert len(ledger2.all()) == 1


def test_error_ledger_clear(tmp_path):
    ledger = ErrorLedger(tmp_path / "ledger.json")
    ledger.add(ErrorLedgerEntry(task_id="TSK-1", agent_id="a", error_type="t"))
    ledger.clear()
    assert len(ledger.all()) == 0


# --- FIX-LEDGER-01: Windows gecici kilit (WinError 5) retry ---------------


def _replace_sahte(basarisiz_sayisi: int, sayac: dict[str, int]):
    """Ilk N cagrida PermissionError firlatan, sonra gercek os.replace'i yapan sahte."""
    import os as _os

    gercek = _os.replace

    def _sahte(kaynak, hedef):
        sayac["n"] = sayac.get("n", 0) + 1
        if sayac["n"] <= basarisiz_sayisi:
            raise PermissionError(5, "Erisim engellendi (sahte WinError 5)")
        return gercek(kaynak, hedef)

    return _sahte


def test_fix_ledger_01_gecici_kilit_retry_ile_gecilir(tmp_path, monkeypatch):
    """Ilk 2 replace denemesi PermissionError verse bile 3. deneme yazar."""
    import src.company_master.orchestrator.error_ledger as mod

    monkeypatch.setattr(mod, "REPLACE_BEKLEME_SN", 0.0)
    sayac: dict[str, int] = {}
    monkeypatch.setattr(mod.os, "replace", _replace_sahte(2, sayac))

    ledger = ErrorLedger(tmp_path / "ledger.json")
    ledger.add(ErrorLedgerEntry(task_id="TSK-R", agent_id="a", error_type="t"))

    assert sayac["n"] == 3
    assert (tmp_path / "ledger.json").exists()
    assert len(ErrorLedger(tmp_path / "ledger.json").all()) == 1


def test_fix_ledger_01_kalici_kilit_hatayi_yukari_atar(tmp_path, monkeypatch):
    """Tum denemeler basarisizsa PermissionError yutulmaz."""
    import src.company_master.orchestrator.error_ledger as mod

    monkeypatch.setattr(mod, "REPLACE_BEKLEME_SN", 0.0)
    sayac: dict[str, int] = {}
    monkeypatch.setattr(mod.os, "replace", _replace_sahte(99, sayac))

    ledger = ErrorLedger(tmp_path / "ledger.json")
    with pytest.raises(PermissionError):
        ledger.add(ErrorLedgerEntry(task_id="TSK-R", agent_id="a", error_type="t"))
    assert sayac["n"] == mod.REPLACE_DENEME
