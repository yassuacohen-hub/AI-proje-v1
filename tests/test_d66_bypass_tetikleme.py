#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""D-66 bypass tetikleme testi."""
import json
import sys
from pathlib import Path
from datetime import datetime

import pytest

# Import düzeltme
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.company_master.orchestrator import task_board as tb


@pytest.fixture(autouse=True)
def izole_tetik_dosya(tmp_path, monkeypatch):
    """Tetik ve pano dosyasını izole et."""
    state_dir = tmp_path / "orchestrator" / "triggers"
    state_dir.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(tb, "STATE_DIR", tmp_path / "orchestrator")
    
    # Pano dosyası oluştur
    pano_dosya = tmp_path / "orchestrator" / "task_board.json"
    pano_dosya.parent.mkdir(parents=True, exist_ok=True)
    pano_dosya.write_text(
        json.dumps([
            {
                "task_id": "TEST-001",
                "durum": "aktif",
                "sahip": "ihsan",
                "baslik": "Test görev"
            }
        ]),
        encoding="utf-8"
    )
    monkeypatch.setattr(tb, "TASK_BOARD", pano_dosya)
    
    # Tetik dosyası oluştur
    tetik_dosya = state_dir / "ihsan.jsonl"
    tetik_dosya.write_text(
        json.dumps({"task_id": "TEST-001", "durum": "bekliyor", "ajan": "ihsan"}) + "\n",
        encoding="utf-8"
    )
    return tmp_path


def test_bypass_flag_ekli(izole_tetik_dosya, capsys):
    """--bypass-override flag'i kabul edilir."""
    from scripts import tetik_senk
    
    argv = ["senkron", "--bypass-override", "--bypass-reason", "D-66 — Test bypass"]
    kod = tetik_senk.main(argv)
    
    cap = capsys.readouterr()
    assert "D-66 BYPASS TETIKLEME" in cap.out
    assert "Test bypass" in cap.out
    # Senkron başarılı olmalı (bypass olsa da)
    assert kod in (0, 2, 3)  # 0=temiz, 2=sapma var, 3=dosya yok


def test_bypass_reason_varsayilan(izole_tetik_dosya, capsys):
    """--bypass-reason verilmezse varsayılan message kullanılır."""
    from scripts import tetik_senk
    
    argv = ["senkron", "--bypass-override"]
    kod = tetik_senk.main(argv)
    
    cap = capsys.readouterr()
    assert "D-66 BYPASS" in cap.out
    assert kod in (0, 2, 3)


def test_bypass_logging_kaydedilir(izole_tetik_dosya, tmp_path):
    """Bypass event'i logging'e kaydedilir."""
    from scripts import tetik_senk
    import logging
    
    # Logger ayarla
    log_dosya = tmp_path / "tetik_senk.log"
    handler = logging.FileHandler(log_dosya, encoding="utf-8")
    logger = logging.getLogger("tetik_senk")
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    
    argv = ["senkron", "--bypass-override", "--bypass-reason", "D-66 — Saat uyuşmazlığı"]
    tetik_senk.main(argv)
    
    # Log dosyası kontrol et
    if log_dosya.exists():
        log_icerik = log_dosya.read_text(encoding="utf-8")
        assert "D-66 bypass tetikleme" in log_icerik or "Saat uyuşmazlığı" in log_icerik


def test_bypass_olmadan_normal_calisir(izole_tetik_dosya, capsys):
    """--bypass-override olmadan normal senkron çalışır."""
    from scripts import tetik_senk
    
    argv = ["senkron"]
    kod = tetik_senk.main(argv)
    
    cap = capsys.readouterr()
    assert "D-66 BYPASS" not in cap.out
    # Normal mesaj görülmeli
    assert "TETIK-PANO" in cap.out
    assert kod in (0, 2, 3)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
