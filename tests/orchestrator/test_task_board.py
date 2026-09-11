#!/usr/bin/env python3
"""Tests for orchestrator task board.

ORCH-01: Bu testler gerçek `data/orchestrator/task_board.json`'a YAZMAZ;
tüm orchestrator yolları autouse fixture ile tmp_path'e izole edilir.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pytest

from src.company_master.orchestrator import task_board as tb_module
from src.company_master.orchestrator.task_board import (
    gorev_ekle,
    gorev_guncelle,
    gorev_getir,
    gorev_listesi,
    _ensure,
    TASK_BOARD,
    FILE_LOCKS,
    STATE_JSON,
)


@pytest.fixture(autouse=True)
def _isolated_board(tmp_path, monkeypatch):
    """Pano/lock/state yollarını tmp_path'e yönlendir.

    Import edilmiş TASK_BOARD bağlantısı fixture içinde modül
    attribute'undan tazelenir; böylece eski bağlantı gerçek panoya yazmaz.
    """
    monkeypatch.chdir(tmp_path)
    state_dir = tmp_path / "data" / "orchestrator"
    monkeypatch.setattr(tb_module, "STATE_DIR", state_dir)
    monkeypatch.setattr(tb_module, "TASK_BOARD", state_dir / "task_board.json")
    monkeypatch.setattr(tb_module, "FILE_LOCKS", state_dir / "file_locks.json")
    monkeypatch.setattr(tb_module, "STATE_JSON", state_dir / "state.json")
    monkeypatch.setattr(tb_module, "TASK_MD", state_dir / "gorev_panosu.md")
    if hasattr(tb_module, "HANDOFF_FILE"):
        monkeypatch.setattr(tb_module, "HANDOFF_FILE", state_dir / "handoffs.json")
    # Eski import bağlantılarını tazele (fonksiyonlar zaten modül
    # global'lerini çağrı anında okur; yalnızca doğrudan Path kullanımı
    # için rebind gerekir).
    globals()["TASK_BOARD"] = tb_module.TASK_BOARD
    globals()["FILE_LOCKS"] = tb_module.FILE_LOCKS
    globals()["STATE_JSON"] = tb_module.STATE_JSON
    yield


def test_gorev_guncelle_not_keyword_argument():
    """Test that gorev_guncelle correctly handles 'not' as a keyword argument.
    
    This addresses the issue where 'not' was being passed as a positional 
    argument incorrectly, causing a syntax error.
    """
    _ensure()
    
    # Clear the board for clean test
    TASK_BOARD.write_text("[]", encoding="utf-8")
    
    # Add a test task
    task = gorev_ekle(
        task_id="TEST-NOT-KEYWORD",
        baslik="Test not keyword argument handling",
        sahip="mimar",
        oncelik="P1"
    )
    
    assert task is not None
    assert task["task_id"] == "TEST-NOT-KEYWORD"
    
    # Test 1: Update with 'not' as a keyword argument (should work)
    result = gorev_guncelle(
        task_id="TEST-NOT-KEYWORD",
        durum="aktif",
        not_test_value="this should work as a keyword argument"
    )
    
    assert result is not None
    assert result["durum"] == "aktif"
    assert result.get("not_test_value") == "this should work as a keyword argument"
    
    # Verify the task was actually updated in the board
    updated_task = gorev_getir("TEST-NOT-KEYWORD")
    assert updated_task is not None
    assert updated_task["durum"] == "aktif"
    assert updated_task.get("not_test_value") == "this should work as a keyword argument"
    
    # Test 2: Update with multiple keyword arguments including one that looks like a built-in
    result2 = gorev_guncelle(
        task_id="TEST-NOT-KEYWORD",
        durum="review",
        **{"not": "this is allowed as a keyword argument"},
        another_field="test value"
    )
    
    assert result2 is not None
    assert result2["durum"] == "review"
    assert result2.get("not") == "this is allowed as a keyword argument"
    assert result2.get("another_field") == "test value"
    
    # Final verification
    final_task = gorev_getir("TEST-NOT-KEYWORD")
    assert final_task is not None
    assert final_task["durum"] == "review"
    assert final_task.get("not") == "this is allowed as a keyword argument"
    assert final_task.get("another_field") == "test value"
    assert final_task.get("not_test_value") == "this should work as a keyword argument"


def test_gorev_guncelle_invalid_duration():
    """Test that gorev_guncelle rejects invalid duration values."""
    _ensure()
    
    # Clear the board for clean test
    TASK_BOARD.write_text("[]", encoding="utf-8")
    
    # Add a test task
    task = gorev_ekle(
        task_id="TEST-INVALID-DURUM",
        baslik="Test invalid duration handling",
        sahip="mimar",
        oncelik="P1"
    )
    
    assert task is not None
    
    # Test with invalid duration - should raise ValueError
    with pytest.raises(ValueError, match="Gecersiz durum"):
        gorev_guncelle(
            task_id="TEST-INVALID-DURUM",
            durum="invalid_duration",
            some_field="test"
        )


def test_gorev_ekle_duplicate_prevention():
    """Test that gorev_ekle prevents duplicate task IDs."""
    _ensure()
    
    # Clear the board for clean test
    TASK_BOARD.write_text("[]", encoding="utf-8")
    
    # Add first task
    task1 = gorev_ekle(
        task_id="DUPLICATE-TEST",
        baslik="First task",
        sahip="mimar",
        oncelik="P1"
    )
    
    assert task1 is not None
    assert task1["task_id"] == "DUPLICATE-TEST"
    
    # Try to add duplicate - should raise ValueError
    with pytest.raises(ValueError, match="Gorev zaten var"):
        gorev_ekle(
            task_id="DUPLICATE-TEST",
            baslik="Second task with same ID",
            sahip="gelistirici",
            oncelik="P2"
        )
    
    # Verify only one task exists
    tasks = gorev_listesi()
    assert len(tasks) == 1
    assert tasks[0]["task_id"] == "DUPLICATE-TEST"
    assert tasks[0]["baslik"] == "First task"


def test_atomic_yazma_tmp_artigi_birakmaz():
    """ORCH-01 devami: JSON/markdown yazmalar atomik; yarisma aninda tmp artigi kalmaz."""
    _ensure()
    gorev_ekle("ATOMIC-01", "Atomik yazma testi", "mimar")
    gorev_guncelle("ATOMIC-01", durum="done", **{"not": "atomik"})
    state_dir = tb_module.STATE_DIR
    kalan_tmp = sorted(p.name for p in state_dir.glob("*.tmp"))
    assert kalan_tmp == [], f"tmp artigi kaldi: {kalan_tmp}"
    board = json.loads(tb_module.TASK_BOARD.read_text(encoding="utf-8-sig"))
    assert any(
        t["task_id"] == "ATOMIC-01" and t["durum"] == "done" for t in board
    ), "guncelleme panoya atomik yazilmali"
    assert (state_dir / "gorev_panosu.md").exists(), "_md_yaz ciktisi uretilmeli"


def test_atomic_write_text_dosya_icerigi():
    """atomic_write_text dogru icerik + UTF-8 + tekrarli yazim."""
    from src.company_master.orchestrator.task_board import atomic_write_text

    hedef = tb_module.STATE_DIR / "deneme.md"
    atomic_write_text(hedef, "merhaba — üğşiçöĞÜ")
    assert hedef.read_text(encoding="utf-8") == "merhaba — üğşiçöĞÜ"
    atomic_write_text(hedef, "ikinci yazim")
    assert hedef.read_text(encoding="utf-8") == "ikinci yazim"
    assert sorted(p.name for p in tb_module.STATE_DIR.glob("*.tmp")) == []


if __name__ == "__main__":
    # ORCH-01: Doğrudan çağrı izolasyon fixture'ını atlar ve gerçek
    # data/orchestrator/task_board.json'a yazabilir -> devre dışı.
    print("Bu test dosyası pytest ile çalıştırılmalıdır:")
    print("  python -m pytest tests/orchestrator/ -q")
    raise SystemExit(0)
    test_gorev_guncelle_not_keyword_argument()  # ulaşılmaz (korumalı)