# -*- coding: utf-8 -*-
"""D-198: arsivde duran bir task_id ikinci kez panoya giremez."""
import json
import sys
from pathlib import Path

import pytest

KOK = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(KOK))

from src.company_master.orchestrator import task_board as tb  # noqa: E402


def test_arsivdeki_task_id_tekrar_eklenemez(tmp_path, monkeypatch):
    pano = tmp_path / "task_board.json"
    pano.write_text("[]", encoding="utf-8")
    arsiv = tmp_path / "task_board_arsiv_2026-Q3.json"
    arsiv.write_text(
        json.dumps([{"task_id": "ALTYAPI-D66-BYPASS-TETIKLEME-01", "durum": "done"}]),
        encoding="utf-8",
    )
    monkeypatch.setattr(tb, "TASK_BOARD", pano)
    monkeypatch.setattr(tb, "STATE_DIR", tmp_path)

    with pytest.raises(ValueError) as hata:
        tb.gorev_ekle("ALTYAPI-D66-BYPASS-TETIKLEME-01", "Ayni is ikinci kez", "utku")

    # Hata metni HANGI arsiv dosyasi oldugunu soylemeli.
    assert "task_board_arsiv_2026-Q3.json" in str(hata.value)
