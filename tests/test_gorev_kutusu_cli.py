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

def _bulgu_kapisi_ac(monkeypatch):
    """D-318 bulgu kapisini gecer. Bu testler kapinin kendisini degil
    teslim davranisini olcer; bulgu yazmadan teslim reddedilir.
    Kapinin gercekten calistigini test_cmd_teslim_bulgu_kapisi_reddeder
    dogrular."""
    monkeypatch.setattr(gk.bulgu, "task_var_mi", lambda task_id: True)


def test_cmd_teslim_basarili(tmp_path, monkeypatch):
    _bulgu_kapisi_ac(monkeypatch)
    _gorev()
    trigger.tetik_ekle("T-01", "kilo", data_dir=tmp_path)
    trigger.tetik_al("kilo", "T-01", data_dir=tmp_path)
    args = argparse.Namespace(ajan="kilo", task_id="T-01", ozet="test", cikti=None)
    rc = gk.cmd_teslim(args)
    assert rc == 0


def test_cmd_teslim_bulgu_kapisi_reddeder(tmp_path):
    """Kapinin kendisi: bulgu yoksa teslim reddedilir (D-318)."""
    _gorev()
    trigger.tetik_ekle("T-01", "kilo", data_dir=tmp_path)
    trigger.tetik_al("kilo", "T-01", data_dir=tmp_path)
    args = argparse.Namespace(ajan="kilo", task_id="T-01", ozet="test", cikti=None)
    rc = gk.cmd_teslim(args)
    assert rc == 1, "bulgu kapisi devre disi kalmis"


def test_cmd_teslim_hata(tmp_path, monkeypatch):
    _bulgu_kapisi_ac(monkeypatch)
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


# ---- _tetik_dengele: D-DENGE-TARIH-BAGIMLILIK-01 (2026-10-04) ----

def test_tetik_dengele_gelecek_ve_bagimlilik_ertelenir_hazir_tetiklenir(tmp_path):
    # bagimlilik bitmemis -> DENGE-DEP ertelenir (ts asamasinda elenir)
    tb.gorev_ekle("BEKLE-DEP", "bekle", "salih", "P1")
    tb.gorev_ekle("DENGE-DEP", "denge dep", "salih", "P1")
    tb.gorev_guncelle("DENGE-DEP", dependencies=["BEKLE-DEP"])
    # gelecek tarihli -> ertelenir
    tb.gorev_ekle("DENGE-GELECEK", "denge gelecek", "ihsan", "P1", baslangic="2099-01-01")
    # hazir (gecmis tarih, bagimliliksiz) -> tetiklenir
    tb.gorev_ekle("DENGE-HAZIR", "denge hazir", "utku", "P1", baslangic="2020-01-01")

    secilen_idler = {g["task_id"] for g in gk._tetik_dengele(kuru=True)}

    assert "DENGE-DEP" not in secilen_idler
    assert "DENGE-GELECEK" not in secilen_idler
    assert "DENGE-HAZIR" in secilen_idler
    assert "BEKLE-DEP" in secilen_idler
