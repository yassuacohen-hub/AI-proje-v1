# -*- coding: utf-8 -*-
"""PANO-ARSIV: `gorev_kutusu.py arsivle` bolme + idempotans testi."""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

KOK = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(KOK))

_spec = importlib.util.spec_from_file_location("gk_arsiv", KOK / "scripts" / "gorev_kutusu.py")
gk = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(gk)

PANO = [
    {"task_id": "A-1", "durum": "done", "bitis": "2026-09-21T10:00:00"},
    {"task_id": "A-2", "durum": "iptal", "bitis": "2026-02-03T10:00:00"},
    {"task_id": "A-3", "durum": "archive", "bitis": None},
    {"task_id": "B-1", "durum": "bekliyor", "bitis": ""},
    {"task_id": "B-2", "durum": "plan", "bitis": ""},
]


def test_terminal_tasinir_aktif_kalir():
    aktif, kovalar = gk.arsiv_bol(PANO, "2026-09-24T00:00:00")
    assert [g["task_id"] for g in aktif] == ["B-1", "B-2"]
    assert kovalar["2026-Q3"] and [g["task_id"] for g in kovalar["2026-Q3"]] == ["A-1", "A-3"]
    assert [g["task_id"] for g in kovalar["2026-Q1"]] == ["A-2"]  # tarihten ceyrek
    assert sum(len(v) for v in kovalar.values()) + len(aktif) == len(PANO)


def test_ikinci_calistirma_kayit_cogaltmaz(tmp_path, monkeypatch):
    pano_yol = tmp_path / "task_board.json"
    pano_yol.write_text(json.dumps(PANO, ensure_ascii=False), encoding="utf-8")
    monkeypatch.setattr(gk.tb, "TASK_BOARD", pano_yol)
    monkeypatch.setattr(gk.tb, "STATE_DIR", tmp_path)

    args = argparse.Namespace(kuru=False)
    assert gk.cmd_arsivle(args) == 0
    arsiv = tmp_path / "task_board_arsiv_2026-Q3.json"
    assert len(json.loads(arsiv.read_text(encoding="utf-8"))) == 2
    assert len(json.loads(pano_yol.read_text(encoding="utf-8"))) == 2

    assert gk.cmd_arsivle(args) == 0  # aktif pano bos terminal kayit icerir -> degisim yok
    assert len(json.loads(arsiv.read_text(encoding="utf-8"))) == 2

    # Ayni terminal kayitlari panoya geri koy: arsive ikinci kez yazilmamali.
    pano_yol.write_text(json.dumps(PANO, ensure_ascii=False), encoding="utf-8")
    assert gk.cmd_arsivle(args) == 0
    assert len(json.loads(arsiv.read_text(encoding="utf-8"))) == 2
