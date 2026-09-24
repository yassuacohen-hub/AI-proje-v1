#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test D-87 atama otomasyonu — buyuk/kucuk harf duyarsiz gorev arama.

ALTYAPI-TEST-HERMETIK-01: Bu testler URETIM VERISINE DOKUNMAZ.
Onceki surum betigi subprocess ile cagiriyordu; betik yollarini
`__file__`'dan turettigi icin `cwd=` hicbir izolasyon saglamiyordu ve
her kosu canli `data/orchestrator/task_board.json` + tetik kuyrugunu
yaziyordu. Artik betik surec-icinde yuklenip `root` tmp_path'e baglanir.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

KOK = Path(__file__).resolve().parents[1]


def _betik():
    """scripts/gorev_atama_otomasyonu.py'yi modul olarak yukler (paket degil)."""
    import importlib.util
    import sys
    from pathlib import Path

    KOK = Path(__file__).resolve().parents[1]
    yol = KOK / "scripts" / "gorev_atama_otomasyonu.py"
    
    # Use the exact same module name as the original to ensure they share the same root
    mod_name = "gorev_atama_otomasyonu"
    
    # Check if this module is already loaded
    if mod_name in sys.modules:
        mod = sys.modules[mod_name]
    else:
        spec = importlib.util.spec_from_file_location(mod_name, yol)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        sys.modules[mod_name] = mod
    
    # Set the root attribute on the module to ensure it can be monkeypatched
    # YA-03: mutlak dizin adi varsayma; depo kokunden turet.
    if not hasattr(mod, 'root'):
        mod.root = KOK
    
    return mod


@pytest.fixture
def izole(tmp_path, monkeypatch):
    """Sahte kok: pano + brif tmp_path'te, tetik bellekte toplanir."""
    # Import the original module directly
    import importlib.util
    import sys
    from pathlib import Path

    KOK = Path(__file__).resolve().parents[1]
    yol = KOK / "scripts" / "gorev_atama_otomasyonu.py"
    
    # Use the exact same module name as the original
    mod_name = "gorev_atama_otomasyonu"
    
    # Load the original module directly
    if mod_name in sys.modules:
        mod = sys.modules[mod_name]
    else:
        spec = importlib.util.spec_from_file_location(mod_name, yol)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        sys.modules[mod_name] = mod
    
    # Monkeypatch the root attribute on the original module
    monkeypatch.setattr(mod, "root", tmp_path)

    pano = tmp_path / "data" / "orchestrator"
    pano.mkdir(parents=True)
    (pano / "task_board.json").write_text(
        '[{"task_id": "DASH-UX-02a", "durum": "plan"},'
        ' {"task_id": "DASH-UX-02b", "durum": "plan"}]',
        encoding="utf-8",
    )
    (tmp_path / "plans").mkdir()

    tetikler: list[tuple] = []
    monkeypatch.setattr(
        mod.trigger, "tetik_ekle",
        lambda t, a, m: tetikler.append((t, a, m)),
    )
    return mod, tmp_path, tetikler


def _brif_yaz(kok: Path, ajan: str, task_id: str, baslik: str = "# Test brifi") -> None:
    (kok / "plans" / f"brief_{ajan}_{task_id}.md").write_text(baslik, encoding="utf-8")


def _cagir(mod, monkeypatch, *args: str) -> int:
    monkeypatch.setattr(sys, "argv", ["gorev_atama_otomatis.py", *args])
    return mod.main()


def test_dash_ux_02b_atanabiliyor(izole, monkeypatch, capsys) -> None:
    """Kucuk harf sonekli gorev bulunur ve tetiklenir."""
    mod, kok, tetikler = izole
    _brif_yaz(kok, "roo", "DASH-UX-02b")
    assert _cagir(mod, monkeypatch, "--task-id", "DASH-UX-02b", "--ajan", "roo") == 0
    assert tetikler == [("DASH-UX-02b", "roo", "Test brifi")]


def test_bilinmeyen_gorev_reddedilir(izole, monkeypatch, capsys) -> None:
    mod, _kok, tetikler = izole
    assert _cagir(mod, monkeypatch, "--task-id", "YOK-BOYLE-99", "--ajan", "utku") == 1
    assert "gorev bulunamadi" in capsys.readouterr().out.lower()
    assert tetikler == []


def test_brifsiz_atama_reddedilir(izole, monkeypatch, capsys) -> None:
    """D-66: brif yoksa tetik ATILMAZ."""
    mod, _kok, tetikler = izole
    assert _cagir(mod, monkeypatch, "--task-id", "DASH-UX-02a", "--ajan", "olmayan") == 1
    assert "brif bulunamadi" in capsys.readouterr().out.lower()
    assert tetikler == []


def test_case_insensitive_lookup(izole, monkeypatch, capsys) -> None:
    """Panoda 'DASH-UX-02a' yazan gorev buyuk harfle de bulunur."""
    mod, kok, tetikler = izole
    _brif_yaz(kok, "mimar", "DASH-UX-02a")
    assert _cagir(mod, monkeypatch, "--task-id", "dash-ux-02A", "--ajan", "mimar") == 0
    # Panodaki gercek yazim kullanilir, kullanicinin yazdigi degil.
    assert tetikler[0][0] == "DASH-UX-02a"


def test_uretim_panosuna_dokunulmaz(izole, monkeypatch) -> None:
    """Bariyer: kosu sonrasi canli pano dosyasi bayt-bayt ayni kalir."""
    mod, kok, _tetikler = izole
    canli = KOK / "data" / "orchestrator" / "task_board.json"
    onceki = canli.read_bytes() if canli.exists() else None
    _brif_yaz(kok, "roo", "DASH-UX-02b")
    _cagir(mod, monkeypatch, "--task-id", "DASH-UX-02b", "--ajan", "roo")
    assert (canli.read_bytes() if canli.exists() else None) == onceki
