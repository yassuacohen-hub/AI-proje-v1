#!/usr/bin/env python3
"""quick_task.py uçtan uca validasyon testleri (VALIDATE-01).

ORCH-01 notu: Bu testler gerçek `data/orchestrator/task_board.json`'a
ASLA yazmaz; tüm orchestrator yolları autouse fixture ile tmp_path'e
izole edilir.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pytest

import scripts.quick_task as qt
from scripts.quick_task import brief_olustur, main
from src.company_master.orchestrator import sync as sync_module
from src.company_master.orchestrator import task_board as tb_module


@pytest.fixture(autouse=True)
def _isolated_orchestrator(tmp_path, monkeypatch):
    """Pano/lock/handoff/workspace yollarını tmp_path'e yönlendir."""
    monkeypatch.chdir(tmp_path)
    state_dir = tmp_path / "data" / "orchestrator"
    monkeypatch.setattr(tb_module, "STATE_DIR", state_dir)
    monkeypatch.setattr(tb_module, "TASK_BOARD", state_dir / "task_board.json")
    monkeypatch.setattr(tb_module, "FILE_LOCKS", state_dir / "file_locks.json")
    monkeypatch.setattr(tb_module, "STATE_JSON", state_dir / "state.json")
    monkeypatch.setattr(tb_module, "TASK_MD", state_dir / "gorev_panosu.md")
    if hasattr(tb_module, "HANDOFF_FILE"):
        monkeypatch.setattr(tb_module, "HANDOFF_FILE", state_dir / "handoffs.json")
    monkeypatch.setattr(sync_module, "AGENT_SYNC_PATH", tmp_path / "AGENT_SYNC.md")
    monkeypatch.setattr(qt, "WORKSPACE_ROOT", tmp_path / "workspace" / "external")


def test_brief_olustur_gecerli_brief_uretir():
    brief_path = brief_olustur(
        agent_id="claude_code",
        task_id="VALIDATE-01-TEST",
        title="Test Validation Brief",
        task_type="research",
        from_agent="mimar",
        source="harici",
        run_mode="orchestrator",
        context_files=["docs/test.md"],
        success_criteria=["Test passes", "Output generated"],
    )
    assert brief_path.exists()
    data = json.loads(brief_path.read_text(encoding="utf-8"))
    assert data["agent_id"] == "claude_code"
    assert data["task_id"] == "VALIDATE-01-TEST"
    assert data["title"] == "Test Validation Brief"
    assert data["task_type"] == "research"
    assert data["source"] == "harici"
    assert data["from_agent"] == "mimar"
    assert data["run_mode"] == "orchestrator"
    assert data["context_files"] == ["docs/test.md"]
    assert data["success_criteria"] == ["Test passes", "Output generated"]
    # quick_task varsayılan olarak kısıt setini boş bırakır
    assert data["constraints"] == {}


def test_brief_olustur_varsayilanlar():
    brief_path = brief_olustur(
        agent_id="cursor_grok",
        task_id="DEFAULT-TEST",
        title="Default Test",
    )
    data = json.loads(brief_path.read_text(encoding="utf-8"))
    assert data["task_type"] == "research"
    assert data["source"] == "harici"
    assert data["from_agent"] is None
    assert data["run_mode"] is None
    assert data["context_files"] == []
    assert data["success_criteria"] == []


def test_quick_task_e2e_dispatch_ve_review():
    """Uçtan uca: brief_olustur -> dispatch -> review -> done + handoff + AGENT_SYNC."""
    sync_path = Path(sync_module.AGENT_SYNC_PATH)
    sync_path.write_text(
        "# AGENT Sync\n\n## Tamamlananlar (Senkron Kaydi)\n", encoding="utf-8"
    )
    eski_argv = sys.argv
    sys.argv = [
        "quick_task",
        "--from-agent", "mimar",
        "--agent", "claude_code",
        "--task", "QT-E2E-01",
        "--title", "E2E Validation",
        "--task-type", "research",
        "--run-mode", "orchestrator",
        "--review",
    ]
    try:
        rc = main()
    finally:
        sys.argv = eski_argv
    assert rc == 0

    # 1) Görev panoya kaydedildi ve review PASS ile done oldu
    task = tb_module.gorev_getir("QT-E2E-01")
    assert task is not None, "Görev panoya kaydedilmeli"
    assert task["sahip"] == "claude_code"
    assert task["durum"] == "done", f"Review PASS sonrası done beklenir: {task['durum']}"
    assert task["source"] == "harici"
    assert task.get("from_agent") in ("mimar", None)

    # 2) Brief dosyası üretildi
    brief_file = qt.WORKSPACE_ROOT / "claude_code" / "brief_QT-E2E-01.md"
    assert brief_file.exists(), "Brief dosyası oluşturulmalı"
    data = json.loads(brief_file.read_text(encoding="utf-8"))
    assert data["task_id"] == "QT-E2E-01"
    assert data["agent_id"] == "claude_code"

    # 3) Review PASS handoff kaydı bıraktı
    handoffs_path = tb_module.STATE_DIR / "handoffs.json"
    assert handoffs_path.exists(), "handoffs.json oluşturulmalı"
    handoffs = json.loads(handoffs_path.read_text(encoding="utf-8"))
    assert "QT-E2E-01" in handoffs, "Review PASS handoff kaydı bırakmalı"

    # 4) AGENT_SYNC tamamlanma kaydı eklendi
    sync_text = sync_path.read_text(encoding="utf-8")
    assert "QT-E2E-01" in sync_text, "AGENT_SYNC tamamlanma kaydı eklenmeli"


def test_quick_task_bilinmeyen_ajan_hata_verir():
    sync_path = Path(sync_module.AGENT_SYNC_PATH)
    sync_path.write_text(
        "# AGENT Sync\n\n## Tamamlananlar (Senkron Kaydi)\n", encoding="utf-8"
    )
    eski_argv = sys.argv
    sys.argv = [
        "quick_task",
        "--from-agent", "mimar",
        "--agent", "bilinmeyen_ajan",
        "--task", "QT-BAD-01",
        "--title", "Bad agent",
        "--task-type", "research",
        "--run-mode", "orchestrator",
    ]
    try:
        rc = main()
    finally:
        sys.argv = eski_argv
    assert rc != 0, "Bilinmeyen ajan için sıfır dışı çıkış kodu beklenir"
