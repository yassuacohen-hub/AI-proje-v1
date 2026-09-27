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


def test_bypass_logging_kaydedilir(izole_tetik_dosya, capsys):
    """Bypass event'i logging'e kaydedilir (stdout'a da düşer)."""
    from scripts import tetik_senk

    argv = ["senkron", "--bypass-override", "--bypass-reason", "D-66 — Saat uyuşmazlığı"]
    tetik_senk.main(argv)

    # Stdout kontrol et (logging basicConfig stdout'a yazar)
    cap = capsys.readouterr()
    assert "D-66 BYPASS TETIKLEME" in cap.out
    assert "Saat uyuşmazlığı" in cap.out


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
