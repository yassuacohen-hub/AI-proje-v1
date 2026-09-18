# -*- coding: utf-8 -*-
"""MARKA-REVIZE-01-BULGU: marka_denetim muafiyet mekanizmasi testleri (B-1/B-2).

Kapsam:
    - gercek ihlal hala yakalaniyor (false negative yok)
    - MUAF_SENTINEL satiri atlanir
    - YASAK_BEYAN satiri (kural tanimi) atlanir
    - ATLANAN_DIZINLER / MUAF_YOLLAR taranmaz
    - kok denetim 0 ihlal verir
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

KOK = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location(
    "marka_denetim", KOK / "scripts" / "marka_denetim.py"
)
assert _spec and _spec.loader
md = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(md)


def _yaz(path: Path, metin: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(metin, encoding="utf-8")
    return path


def test_gercek_ihlal_yakalanir(tmp_path: Path) -> None:
    dosya = _yaz(tmp_path / "a.md", "Hugin platformu iyi calisiyor.\n")
    sonuc = md.tarama(dosya)
    assert len(sonuc["yasal_yazim"]) == 1


def test_sentinel_satiri_atlanir(tmp_path: Path) -> None:
    dosya = _yaz(tmp_path / "b.md", "Hugin ornegi  <!-- marka-muaf -->\n")
    assert md.tarama(dosya)["yasal_yazim"] == []


def test_yasak_beyan_satiri_atlanir(tmp_path: Path) -> None:
    dosya = _yaz(tmp_path / "c.md", "Yasak yazimlar: Huggin, Hugin, Munin\n")
    assert md.tarama(dosya)["yasal_yazim"] == []


def test_kok_dizin_ihlali_yakalanir(tmp_path: Path) -> None:
    dosya = _yaz(tmp_path / "d.md", "Dosya kok dizindeki klasorde duruyor.\n")
    assert len(md.tarama(dosya)["kok_dizin"]) == 1


def test_atlanan_dizin_taranmaz() -> None:
    assert not md.taranabilir(KOK / "_trash" / "x.md")
    assert not md.taranabilir(KOK / "AI proje v1" / "y.md")


def test_muaf_yol_taranmaz() -> None:
    assert md.muaf_dosya(KOK / "scripts" / "marka_denetim.py")
    assert md.muaf_dosya(KOK / "AGENT_SYNC.md")
    assert md.muaf_dosya(KOK / "docs" / "plans" / "herhangi_brief.md")
    assert not md.muaf_dosya(KOK / "AGENTS.md")


def test_kok_denetimi_temiz() -> None:
    """Regresyon kalkani: repo genelinde 0 ihlal (140 -> 0)."""
    sonuc = md.tarama()
    assert sonuc["yasal_yazim"] == [], sonuc["yasal_yazim"][:5]
    assert sonuc["kok_dizin"] == [], sonuc["kok_dizin"][:5]
