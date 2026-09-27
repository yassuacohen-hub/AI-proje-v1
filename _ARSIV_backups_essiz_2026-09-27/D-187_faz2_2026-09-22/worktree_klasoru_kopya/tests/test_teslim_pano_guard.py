# -*- coding: utf-8 -*-
"""D-172 / ORPHAN-ARASTIRMA-01: panoda kaydı olmayan ID teslim edilemez."""
import pytest

from src.company_master.orchestrator import task_board as tb
from src.company_master.orchestrator import trigger as t


def test_panoda_olmayan_gorev_teslim_edilemez(tmp_path, monkeypatch):
    monkeypatch.setattr(tb, "gorev_getir", lambda _tid: None)
    with pytest.raises(t.TriggerError, match="panoda kayıtlı değil"):
        t.teslim_et("HAYALI-01", "roo", "iş bitti", data_dir=tmp_path)
    # kuyruğa öksüz kayıt yazılmamalı
    assert not (tmp_path / "onay_kuyrugu.json").exists()
