# -*- coding: utf-8 -*-
"""ALTYAPI-GOREV-AT-KAPI-01: gorev_at.py KILIT on-kapisi.

Fark (ayri dosya): `test_gorev_at_kapi.py` D-66/D-80 BRIF kapisini olcer.
Buradaki kapı KILIT kapısıdır.

Neden gerekli: `tb.gorev_ekle` -> `_lock_alan` (task_board.py:587) BAYAT
kilidi (D-303, >24 saat) kontrolu YAPMIYOR. `kapi_gecer()` oncesi bayat
kilit eler, TAZE kilit reddeder. `_lock_alan`a dokunulmadi.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

KOK = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(KOK / "scripts"))

_spec = importlib.util.spec_from_file_location(
    "gorev_at_kilit", KOK / "scripts" / "gorev_at.py")
ga = importlib.util.module_from_spec(_spec)
sys.modules["gorev_at_kilit"] = ga
_spec.loader.exec_module(ga)

from ajan_cakisma_kilidi import kapi_gecer  # noqa: E402
from brief_denetim import sablon_kopyala  # noqa: E402


class _Args:
    def __init__(self, **kw):
        self.__dict__.update(kw)


def _args(**kw):
    taban = dict(task_id="TEST-KILIT-01",
                 baslik="[TEST] denetle kilit kapisi -> s.py (1s)",
                 ajan="yasu", oncelik="P2", dosya="", talimat="dolu",
                 mod="code", baslik_b64=None, cagiran="ihsan")
    taban.update(kw)
    return _Args(**taban)


@pytest.fixture
def temiz(monkeypatch, tmp_path):
    """Pano/tetik yazimi kes; yalniz KAPI davranisi olculur."""
    yazilan: dict = {}
    monkeypatch.setattr(ga, "_orkestrator_kapisi", lambda c: None)
    monkeypatch.setattr(ga.tb, "gorev_ekle",
                        lambda **kw: yazilan.update(kw) or dict(kw))
    monkeypatch.setattr(ga.trigger, "tetik_ekle",
                        lambda *a: yazilan.setdefault("tetik", a))
    monkeypatch.setattr(ga, "KOK", tmp_path)
    (tmp_path / "plans").mkdir()
    sablon_kopyala(tmp_path / "plans" / "brief_yasu_TEST-KILIT-01.md")
    return yazilan


def _kilit(sahip, zaman):
    return {"s.py": {"sahip": sahip, "task_id": "T-1", "kilitlendi": zaman}}


TAZE = _kilit("utku", "2099-01-01T00:00:00")      # D-303: gecerli
BAYAT = _kilit("utku", "2000-01-01T00:00:00")     # D-303: elenir


def test_taze_baska_ajan_kilidi_atamayi_reddeder():
    """KRITIK: baskasinin TAZE kilitli dosyasina atama yapilmaz."""
    gecti, mesaj = kapi_gecer(["s.py"], ajan="yasu", kilitler=TAZE)
    assert not gecti
    assert "utku" in mesaj


def test_bayat_kilit_kapiyi_gecer():
    """D-303: 24 saatten eski kilit on-kapida elenir."""
    gecti, _ = kapi_gecer(["s.py"], ajan="yasu", kilitler=BAYAT)
    assert gecti


def test_kendi_kilidine_gecer():
    gecti, _ = kapi_gecer(["s.py"], ajan="utku", kilitler=TAZE)
    assert gecti


def test_bosta_dosya_gecer():
    assert kapi_gecer(["bos.py"], ajan="yasu", kilitler=TAZE)[0]


def test_cmd_at_taze_kilitte_exit8(temiz, monkeypatch, capsys):
    """cmd_at -> kapi_gecer reddi -> return 8, panoya YAZILMAZ."""
    monkeypatch.setattr(ga, "kapi_gecer", lambda y, ajan=None, kilitler=None:
                        (False, "KILIT KAPISI: 1 dosya baska ajana ait."))
    assert ga.cmd_at(_args(dosya="s.py")) == 8
    assert not temiz, "reddedilen atama panoya yazilmamali"
    assert "kilit kapisi" in capsys.readouterr().err


def test_cmd_at_kilit_yoksa_gecer(temiz, monkeypatch):
    monkeypatch.setattr(ga, "kapi_gecer", lambda y, ajan=None, kilitler=None: (True, ""))
    monkeypatch.setattr(ga, "hareket_uyarisi", lambda *a, **k: None)
    assert ga.cmd_at(_args(dosya="s.py")) == 0
    assert temiz["dosyalar"] == ["s.py"]


def test_cmd_at_dosya_bosken_kapi_cagrilmaz(temiz, monkeypatch):
    """--dosya verilmediyse kapı hiç çalışmaz."""
    cagri: list = []
    monkeypatch.setattr(ga, "kapi_gecer",
                        lambda y, ajan=None, kilitler=None: cagri.append(1) or (True, ""))
    monkeypatch.setattr(ga, "hareket_uyarisi", lambda *a, **k: None)
    assert ga.cmd_at(_args()) == 0
    assert cagri == []


def test_hareket_uyarisi_atamayi_durdurmaz(temiz, monkeypatch, capsys):
    """UYARI yazılır ama atama YİNE olur (kilit değilse engellemez)."""
    monkeypatch.setattr(ga, "kapi_gecer", lambda y, ajan=None, kilitler=None: (True, ""))
    monkeypatch.setattr(ga, "hareket_uyarisi", lambda *a, **k: "KILITLI HAREKET var")
    assert ga.cmd_at(_args(dosya="s.py")) == 0
    assert "UYARI" in capsys.readouterr().out
    assert temiz, "uyari atamayi engellememeli"


def test_exit8_kod_serbest():
    """8 hicbir yerde kullanilmiyor olmali (4 = D-58, 2 = PermissionError)."""
    kaynak = (KOK / "scripts" / "gorev_at.py").read_text(encoding="utf-8")
    assert kaynak.count("return 8") == 1


def test_kapi_gorev_ekleden_once_calisir(temiz, monkeypatch):
    """Kapı, gorev_ekle CAGRILMADAN once reddetmeli."""
    sira: list = []
    monkeypatch.setattr(ga, "kapi_gecer", lambda y, ajan=None, kilitler=None:
                        (sira.append("kapi") or False, "x"))
    monkeypatch.setattr(ga.tb, "gorev_ekle",
                        lambda **kw: sira.append("ekle") or dict(kw))
    assert ga.cmd_at(_args(dosya="s.py")) == 8
    assert sira == ["kapi"], "gorev_ekle cagrilmamaliydi"