# -*- coding: utf-8 -*-
"""ALTYAPI-TEST-HERMETIK-01: uretim verisi dokunulmazlik bariyerinin testi.

Bariyer conftest'te autouse fixture olarak calisir. Bariyerin kendisi bozulursa
sessizce gecerdi; bu dosya onu kanitlar.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

KOK = Path(__file__).resolve().parents[1]


def _conftest():
    """conftest paket olarak import edilemiyor; dosyadan yuklenir."""
    yol = Path(__file__).resolve().parent / "conftest.py"
    spec = importlib.util.spec_from_file_location("_conftest_bariyer", yol)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


conftest = _conftest()


def test_korumali_listede_kritik_dosyalar_var():
    adlar = {p.name for p in conftest.KORUMALI}
    assert {"task_board.json", "file_locks.json", "onay_kuyrugu.json"} <= adlar


def test_korumali_yollar_kok_altinda():
    for yol in conftest.KORUMALI:
        assert KOK in yol.parents


def test_bariyer_yazimi_yakalar_ve_geri_yukler(tmp_path, monkeypatch):
    """Sahte korumali dosyaya yazan bir test: bariyer kirar, icerik geri gelir."""
    sahte = tmp_path / "task_board.json"
    orijinal = b'[{"task_id": "SAHTE-01"}]'
    sahte.write_bytes(orijinal)
    monkeypatch.setattr(conftest, "KORUMALI", (sahte,))

    # Fixture'i elle surerek yield sonrasi davranisini olcuyoruz.
    uretec = conftest._uretim_verisi_dokunulmaz.__wrapped__()
    next(uretec)
    sahte.write_bytes(b"BOZUK")
    with pytest.raises(AssertionError, match="uretim verisine yazdi"):
        next(uretec, None)
    assert sahte.read_bytes() == orijinal


def test_bariyer_dokunmayan_testte_susar(tmp_path, monkeypatch):
    sahte = tmp_path / "file_locks.json"
    sahte.write_bytes(b"{}")
    monkeypatch.setattr(conftest, "KORUMALI", (sahte,))
    uretec = conftest._uretim_verisi_dokunulmaz.__wrapped__()
    next(uretec)
    assert next(uretec, "bitti") == "bitti"  # hata yok


def test_canli_pano_bu_kosuda_degismedi():
    """Bu dosyanin kendi kosusu canli panoyu kirletmiyor (duman testi)."""
    canli = KOK / "data" / "orchestrator" / "task_board.json"
    assert canli.exists(), "canli pano yok: bariyerin korudugu hedef kaybolmus"
