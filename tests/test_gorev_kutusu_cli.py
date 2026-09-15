# -*- coding: utf-8 -*-
"""COP-04: gorev_kutusu.py CLI komut testleri.

bak, al, teslim, onayla, reddet komutlarini mock et.
Gerçek dosyalara dokunmaz: izole pano (tmp_path).
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from unittest.mock import patch

import pytest

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from scripts import gorev_kutusu as gk
from src.company_master.orchestrator import task_board as tb
from src.company_master.orchestrator import trigger


@pytest.fixture(autouse=True)
def izole(tmp_path, monkeypatch):
    monkeypatch.setattr(tb, "AUTO_SYNC", False)
    monkeypatch.setattr(tb, "STATE_DIR", tmp_path)
    monkeypatch.setattr(tb, "TASK_BOARD", tmp_path / "task_board.json")
    monkeypatch.setattr(tb, "FILE_LOCKS", tmp_path / "file_locks.json")
    return tmp_path


def _gorev(task_id: str = "T-01", ajan: str = "kilo", talimat: str = "test brifi"):
    tb.gorev_ekle(task_id, f"{task_id} test", ajan, "P1")
    if talimat:
        tb.gorev_guncelle(task_id, talimat=talimat)


# ---- bak ----

def test_cmd_bak_bos(tmp_path):
    args = argparse.Namespace(ajan="kilo")
    rc = gk.cmd_bak(args)
    assert rc == 0


def test_cmd_bak_bekleyen_var(tmp_path):
    _gorev()
    trigger.tetik_ekle("T-01", "kilo", data_dir=tmp_path)
    args = argparse.Namespace(ajan="kilo")
    rc = gk.cmd_bak(args)
    assert rc == 0


# ---- al ----

def test_cmd_al_basarili(tmp_path):
    _gorev()
    trigger.tetik_ekle("T-01", "kilo", data_dir=tmp_path)
    args = argparse.Namespace(ajan="kilo", task_id="T-01")
    rc = gk.cmd_al(args)
    assert rc == 0


def test_cmd_al_talimatsiz_reddedilir(tmp_path, capsys):
    """Brif görünürlüğü: ne tetikte ne panoda talimat yoksa `al` reddedilir."""
    _gorev(talimat="")
    trigger.tetik_ekle("T-01", "kilo", data_dir=tmp_path)
    args = argparse.Namespace(ajan="kilo", task_id="T-01")
    assert gk.cmd_al(args) == 1
    assert "talimat" in capsys.readouterr().out.lower()
    assert tb.gorev_getir("T-01")["durum"] != "aktif"


def test_cmd_al_talimatsiz_zorla_alinir(tmp_path):
    _gorev(talimat="")
    trigger.tetik_ekle("T-01", "kilo", data_dir=tmp_path)
    args = argparse.Namespace(ajan="kilo", task_id="T-01", zorla=True)
    assert gk.cmd_al(args) == 0
    assert tb.gorev_getir("T-01")["durum"] == "aktif"


def test_cmd_al_tetik_talimati_yeterli(tmp_path):
    _gorev(talimat="")
    trigger.tetik_ekle("T-01", "kilo", talimat="tetik brifi", data_dir=tmp_path)
    args = argparse.Namespace(ajan="kilo", task_id="T-01")
    assert gk.cmd_al(args) == 0


def test_cmd_bak_pano_talimatini_basar(tmp_path, capsys):
    """Tetikte talimat yoksa panodaki brif gösterilir."""
    _gorev(talimat="pano brifi")
    trigger.tetik_ekle("T-01", "kilo", data_dir=tmp_path)
    gk.cmd_bak(argparse.Namespace(ajan="kilo"))
    assert "pano brifi" in capsys.readouterr().out


def test_cmd_bak_talimat_yok_uyarisi(tmp_path, capsys):
    _gorev(talimat="")
    trigger.tetik_ekle("T-01", "kilo", data_dir=tmp_path)
    gk.cmd_bak(argparse.Namespace(ajan="kilo"))
    assert "TALIMAT YOK" in capsys.readouterr().out


def test_cmd_al_hata(tmp_path):
    _gorev()
    trigger.tetik_ekle("T-01", "kilo", data_dir=tmp_path)
    trigger.tetik_al("kilo", "T-01", data_dir=tmp_path)
    args = argparse.Namespace(ajan="kilo", task_id="T-01")
    rc = gk.cmd_al(args)
    assert rc == 1


# ---- teslim ----

def test_cmd_teslim_basarili(tmp_path):
    _gorev()
    trigger.tetik_ekle("T-01", "kilo", data_dir=tmp_path)
    trigger.tetik_al("kilo", "T-01", data_dir=tmp_path)
    args = argparse.Namespace(ajan="kilo", task_id="T-01", ozet="test", cikti=None)
    rc = gk.cmd_teslim(args)
    assert rc == 0


def test_cmd_teslim_hata(tmp_path):
    _gorev()
    trigger.tetik_ekle("T-01", "kilo", data_dir=tmp_path)
    trigger.tetik_al("kilo", "T-01", data_dir=tmp_path)
    trigger.teslim_et("T-01", "kilo", "ilk", data_dir=tmp_path)
    args = argparse.Namespace(ajan="kilo", task_id="T-01", ozet="ikinci", cikti=None)
    rc = gk.cmd_teslim(args)
    assert rc == 1


# ---- onayla ----

def test_cmd_onayla_basarili(tmp_path):
    _gorev()
    trigger.tetik_ekle("T-01", "kilo", data_dir=tmp_path)
    trigger.tetik_al("kilo", "T-01", data_dir=tmp_path)
    trigger.teslim_et("T-01", "kilo", "test", data_dir=tmp_path)
    args = argparse.Namespace(task_id="T-01", ben="orkestrator")
    rc = gk.cmd_onayla(args)
    assert rc == 0


def test_cmd_onayla_hata(tmp_path):
    _gorev()
    args = argparse.Namespace(task_id="T-01", ben="orkestrator")
    rc = gk.cmd_onayla(args)
    assert rc == 1


# ---- reddet ----

def test_cmd_reddet_basarili(tmp_path):
    _gorev()
    trigger.tetik_ekle("T-01", "kilo", data_dir=tmp_path)
    trigger.tetik_al("kilo", "T-01", data_dir=tmp_path)
    trigger.teslim_et("T-01", "kilo", "test", data_dir=tmp_path)
    args = argparse.Namespace(task_id="T-01", ben="orkestrator", neden="test reddet")
    rc = gk.cmd_reddet(args)
    assert rc == 0


def test_cmd_reddet_hata(tmp_path):
    _gorev()
    trigger.tetik_ekle("T-01", "kilo", data_dir=tmp_path)
    trigger.tetik_al("kilo", "T-01", data_dir=tmp_path)
    trigger.teslim_et("T-01", "kilo", "test", data_dir=tmp_path)
    trigger.reddet("T-01", "orkestrator", "test", data_dir=tmp_path)
    args = argparse.Namespace(task_id="T-01", ben="orkestrator", neden="tekrar")
    rc = gk.cmd_reddet(args)
    assert rc == 1


# ---- onay-bekleyen ----

def test_cmd_onay_bekleyen_bos(tmp_path):
    args = argparse.Namespace()
    rc = gk.cmd_onay_bekleyen(args)
    assert rc == 0


def test_cmd_onay_bekleyen_var(tmp_path):
    _gorev()
    trigger.tetik_ekle("T-01", "kilo", data_dir=tmp_path)
    trigger.tetik_al("kilo", "T-01", data_dir=tmp_path)
    trigger.teslim_et("T-01", "kilo", "test", data_dir=tmp_path)
    args = argparse.Namespace()
    rc = gk.cmd_onay_bekleyen(args)
    assert rc == 0
