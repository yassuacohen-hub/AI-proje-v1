# -*- coding: utf-8 -*-
"""D-66 brifsiz atama yasağı — gorev_at.py guard testi.

Karar: [[D-66]] Brifsiz Atama Yasak
Kod: scripts/gorev_at.py::cmd_at
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

KOK = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(KOK / "scripts"))

import gorev_at


def test_brifsiz_ve_talimatsiz_atama_reddedilir(tmp_path, monkeypatch, capsys) -> None:
    """Brief dosyası yok + talimat boş → exit kodu 6."""
    monkeypatch.chdir(tmp_path)
    (tmp_path / "plans").mkdir()

    args = argparse.Namespace(
        task_id="TEST-YOK-01",
        baslik="[TEST] Deneme yaz → tests/x.py (1s)",
        baslik_b64=None,
        ajan="utku",
        oncelik="P2",
        dosya=None,
        talimat="",
        mod="code",
        cagiran=None,
    )
    monkeypatch.setattr(gorev_at, "_orkestrator_kapisi", lambda _: None)
    monkeypatch.setattr(gorev_at, "_d57_dogrula", lambda *a: None)

    kod = gorev_at.cmd_at(args)
    assert kod == 6, "brifsiz+talimatsiz atama reddedilmeli"
    assert "D-66" in capsys.readouterr().err


def test_talimat_dolu_ama_brif_yoksa_reddedilir(tmp_path, monkeypatch, capsys) -> None:
    """D-66/D-80 onarımı: talimat tek başına yetmez, brif dosyası da diskte olmalı."""
    monkeypatch.chdir(tmp_path)
    (tmp_path / "plans").mkdir()

    args = argparse.Namespace(
        task_id="TEST-VAR-00",
        baslik="[TEST] Deneme yaz → tests/x.py (1s)",
        baslik_b64=None,
        ajan="utku",
        oncelik="P2",
        dosya=None,
        talimat="Dolu talimat",
        mod="code",
        cagiran=None,
    )
    monkeypatch.setattr(gorev_at, "_orkestrator_kapisi", lambda _: None)
    monkeypatch.setattr(gorev_at, "_d57_dogrula", lambda *a: None)

    assert gorev_at.cmd_at(args) == 6, "brif dosyasi yokken talimat gecirmemeli"
    assert "D-66" in capsys.readouterr().err


def test_brif_ve_talimat_varsa_gecer(tmp_path, monkeypatch) -> None:
    """Brif dosyası + talimat dolu → D-66 kapısı geçilir (sonraki adıma düşer)."""
    # Brif aramasi cwd'ye degil gorev_at.KOK'e goreli; ikisi birden ayarlanmali.
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(gorev_at, "KOK", tmp_path)
    (tmp_path / "plans").mkdir()
    (tmp_path / "plans" / "brief_utku_TEST-VAR-01.md").write_text("brif", encoding="utf-8")

    args = argparse.Namespace(
        task_id="TEST-VAR-01",
        baslik="[TEST] Deneme yaz → tests/x.py (1s)",
        baslik_b64=None,
        ajan="utku",
        oncelik="P2",
        dosya=None,
        talimat="Dolu talimat",
        mod="code",
        cagiran=None,
    )
    monkeypatch.setattr(gorev_at, "_orkestrator_kapisi", lambda _: None)
    monkeypatch.setattr(gorev_at, "_d57_dogrula", lambda *a: None)

    def _patlat(**kwargs):
        raise ValueError("D-66 gecildi")

    monkeypatch.setattr(gorev_at.tb, "gorev_ekle", _patlat)
    kod = gorev_at.cmd_at(args)
    assert kod == 1, "D-66 gecilmeli, gorev_ekle asamasina dusmeli"


if __name__ == "__main__":
    import pytest

    sys.exit(pytest.main([__file__, "-v"]))
