# -*- coding: utf-8 -*-
"""change_notify mandallari (D-249 / D-250-7).

Eski hali 0-100 olceginden kalma `threshold=10.0` varsayilani tasiyordu;
0-10'luk kimlik dosyasi tamliginda bu esigin asilmasi imkansizdi, yani
bildirim hic ateslenmiyordu. Ayrica olculmemis puani 0 sayiyordu.
"""
import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


def _mod():
    spec = importlib.util.spec_from_file_location(
        "change_notify", ROOT / "scripts" / "change_notify.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


cn = _mod()


def test_esik_zorunlu():
    """Varsayilan esik yok: cagiran tavandan turetmek zorunda."""
    with pytest.raises(TypeError):
        cn.diff_snapshots({}, {})


def test_kucuk_degisim_yakalanir():
    """0-10 olceginde 0.65'lik degisim bildirilir (eski 10.0 esigi yutuyordu)."""
    old = {"a": {"name": "A", "score": 3.0}}
    new = {"a": {"name": "A", "score": 3.7}}
    d = cn.diff_snapshots(old, new, threshold=0.65)
    assert len(d["changed"]) == 1
    assert d["changed"][0]["delta"] == 0.7


def test_olculmemis_puan_degisim_sayilmaz():
    """D-249: None -> 3.71 "sifirdan yukseldi" degil, olculdu. Bildirilmez."""
    old = {"a": {"name": "A", "score": None}}
    new = {"a": {"name": "A", "score": 3.71}}
    assert cn.diff_snapshots(old, new, threshold=0.65)["changed"] == []


def test_yeni_ve_silinen_ayri_durur():
    d = cn.diff_snapshots({"x": {"score": 1.0}}, {"y": {"score": 1.0}}, threshold=0.65)
    assert (d["added"], d["removed"]) == (["y"], ["x"])
