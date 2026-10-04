# -*- coding: utf-8 -*-
"""D-335: `gorev_kutusu.py nobet` — is gelene kadar bekler, gelince cikis 0 verir."""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path

_KOK = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("gorev_kutusu", _KOK / "scripts" / "gorev_kutusu.py")
gk = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(gk)


def _bos(monkeypatch, tmp_path):
    monkeypatch.setattr(gk.trigger, "bekleyen_tetikler", lambda a, data_dir=None: [])
    monkeypatch.setattr(gk.trigger, "zincir_kalan", lambda a, data_dir=None: [])
    monkeypatch.setattr(gk.chat, "ajan_acik_sorulari", lambda a, data_dir=None: [])
    monkeypatch.setattr(gk.tb, "STATE_DIR", tmp_path)
    monkeypatch.setattr(gk.time, "sleep", lambda s: None) if hasattr(gk, "time") else None


def test_bos_nobet_azami_sure_dolunca_3_doner(monkeypatch, tmp_path):
    _bos(monkeypatch, tmp_path)
    args = argparse.Namespace(ajan="salih", bekle=1, azami_dk=0)
    assert gk.cmd_nobet(args) == 3


def test_yeni_chat_mesaji_is_sayilir(monkeypatch, tmp_path):
    _bos(monkeypatch, tmp_path)
    (tmp_path / "chat").mkdir()
    yol = tmp_path / "chat" / "messages.jsonl"
    yol.write_text(json.dumps({
        "tarih": "2999-01-01T00:00:00", "kimden": "ihsan", "kime": "hepsi",
        "type": "soru", "task_id": "X-1", "mesaj": "cevap?", "yanit_alindi": False,
    }) + "\n", encoding="utf-8")
    isler = gk.nobet_turu("salih", "2026-01-01T00:00:00")
    assert len(isler) == 1 and isler[0].startswith("CHAT")
    assert gk.cmd_nobet(argparse.Namespace(ajan="salih", bekle=1, azami_dk=0)) == 0


def test_kendi_mesaji_ve_cevaplanmis_is_degil(monkeypatch, tmp_path):
    _bos(monkeypatch, tmp_path)
    (tmp_path / "chat").mkdir()
    yol = tmp_path / "chat" / "messages.jsonl"
    satirlar = [
        {"tarih": "2999-01-01T00:00:00", "kimden": "salih", "kime": "hepsi", "mesaj": "ben", "yanit_alindi": False},
        {"tarih": "2999-01-01T00:00:00", "kimden": "ihsan", "kime": "salih", "mesaj": "eski", "yanit_alindi": True},
        {"tarih": "2000-01-01T00:00:00", "kimden": "ihsan", "kime": "salih", "mesaj": "cok eski", "yanit_alindi": False},
    ]
    yol.write_text("".join(json.dumps(s) + "\n" for s in satirlar), encoding="utf-8")
    assert gk.nobet_turu("salih", "2026-01-01T00:00:00") == []
