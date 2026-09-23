# -*- coding: utf-8 -*-
"""ORKESTRA-GOREV-KAPI-01 — `gorev_at.py at` D-66/D-80 kapisi.

Eski kosul `not brief.exists() and not talimat` idi: talimat verilince brif
atlanabiliyordu, panoya bos `brief` alanli gorev dusuyordu (Utku vakasi).
Simdi iki sart AYRI AYRI zorunlu.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

KOK = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("gorev_at", KOK / "scripts" / "gorev_at.py")
ga = importlib.util.module_from_spec(_spec)
sys.modules["gorev_at"] = ga
_spec.loader.exec_module(ga)


class _Args:
    def __init__(self, **kw):
        self.__dict__.update(kw)


@pytest.fixture
def temiz(monkeypatch, tmp_path):
    """Pano/tetik yazimini kes; sadece kapi davranisi olculur."""
    monkeypatch.setattr(ga, "_orkestrator_kapisi", lambda c: None)
    yazilan: dict = {}
    monkeypatch.setattr(ga.tb, "gorev_ekle", lambda **kw: yazilan.update(kw) or dict(
        kw, dosyalar=kw.get("dosyalar") or []))
    monkeypatch.setattr(ga.trigger, "tetik_ekle", lambda *a: yazilan.setdefault("tetik", a))
    monkeypatch.setattr(ga, "KOK", tmp_path)
    (tmp_path / "plans").mkdir()
    return yazilan


def _args(**kw):
    tabanl = dict(task_id="TEST-KAPI-01", baslik="[TEST] denetle kapi → x.py (1s)",
                  ajan="yasu", oncelik="P2", dosya="", talimat="dolu", mod="code",
                  baslik_b64=None, cagiran="ihsan")
    tabanl.update(kw)
    return _Args(**tabanl)


def test_brif_yoksa_talimat_dolu_olsa_bile_reddeder(temiz, capsys):
    """Kacak yolu kapali: --talimat brif eksikligini ortmez."""
    assert ga.cmd_at(_args()) == 6
    assert "D-66" in capsys.readouterr().err
    assert not temiz, "reddedilen gorev panoya yazilmamali"


def test_brif_varsa_bos_talimat_reddeder(temiz, tmp_path, capsys):
    (tmp_path / "plans" / "brief_yasu_TEST-KAPI-01.md").write_text("x", encoding="utf-8")
    assert ga.cmd_at(_args(talimat="   ")) == 6
    assert "D-80" in capsys.readouterr().err
    assert not temiz


def test_ikisi_de_varsa_gecer_ve_brief_alani_dolar(temiz, tmp_path):
    (tmp_path / "plans" / "brief_yasu_TEST-KAPI-01.md").write_text("x", encoding="utf-8")
    assert ga.cmd_at(_args()) == 0
    # D-66: pano 'brief' alani bos kalmamali; yol KOK'e goreli ve POSIX.
    assert temiz["brief"] == "plans/brief_yasu_TEST-KAPI-01.md"
    # D-80 sart 3: tetik talimati pano talimatiyla ayni metin.
    assert temiz["tetik"][2] == temiz["talimat"] == "dolu"


def test_eski_brif_konumu_da_kabul(temiz, tmp_path):
    """data/orchestrator/<TASK>_brif_*.md mirasi hala gecerli."""
    eski = tmp_path / "data" / "orchestrator"
    eski.mkdir(parents=True)
    (eski / "TEST-KAPI-01_brif_2026-09-23_yasu.md").write_text("x", encoding="utf-8")
    assert ga.cmd_at(_args()) == 0
    assert temiz["brief"].startswith("data/orchestrator/TEST-KAPI-01_brif_")


def test_gorev_ekle_brief_talimat_kabul_eder():
    """Mock kaymasi tuzagi: gercek imza brief/talimat almazsa uretimde TypeError.

    Ustteki testler gorev_ekle'yi monkeypatch ettigi icin imza degisikligini
    goremez; bu kontrol gercek fonksiyona bakar.
    """
    import inspect
    parametreler = inspect.signature(ga.tb.gorev_ekle).parameters
    assert {"brief", "talimat"} <= set(parametreler)
