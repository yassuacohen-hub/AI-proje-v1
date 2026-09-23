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
import re
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


# ---- ALTYAPI-MARKA-HUGGINN-01: anti-susturma kilidi ----

#: 'marka-muaf' sentinel'i YALNIZCA bu dosyalarda ve bu sayida kullanilabilir.
#: Brief kurali: "Muafiyet listesine ekleyerek susturmak YASAK". Izin verilen
#: tek kullanim: marka adi DEGIL, dis sozlesme olan eski env adlarinin gecis
#: donemi (bkz. web_app.py _ESKI_CACHE_ENV).
SENTINEL_BEYAZ_LISTE = {
    "web_app.py": 2,
    "tests/test_admin_ui_cache_opt.py": 2,
}

#: Sentinel'in yaninda gerekce bulunmasi zorunlu (susturma dugmesi degil).
GEREKCE = re.compile(r"sozlesme|sözleşme|deprecated|eski env adi", re.IGNORECASE)


def _sentinel_tarama() -> dict[str, list[tuple[int, str]]]:
    """Tarama kapsamindaki tum 'marka-muaf' sentinel satirlarini toplar."""
    bulunan: dict[str, list[tuple[int, str]]] = {}
    for path in md.tarama_kapsami():
        try:
            icerik = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, PermissionError):
            continue
        satirlar = icerik.splitlines()
        for no, satir in enumerate(satirlar, start=1):
            if md.MUAF_SENTINEL not in satir:
                continue
            anahtar = path.relative_to(md.KOK).as_posix()
            bulunan.setdefault(anahtar, []).append((no, satir.strip()))
    return bulunan


def test_muafiyet_susturmaya_donusmez() -> None:
    """Anti-susturma kilidi: sentinel beyaz listeden tasamaz, gerekcesiz olamaz."""
    bulunan = _sentinel_tarama()
    assert set(bulunan) == set(SENTINEL_BEYAZ_LISTE), (
        f"marka-muaf beyaz liste disinda: {sorted(set(bulunan) - set(SENTINEL_BEYAZ_LISTE))}"
    )
    for dosya, satirlar in bulunan.items():
        assert len(satirlar) <= SENTINEL_BEYAZ_LISTE[dosya], (
            f"{dosya}: sentinel sayisi {len(satirlar)} > izinli "
            f"{SENTINEL_BEYAZ_LISTE[dosya]} — yeni muafiyet gerekceyle eklenmeli"
        )
    # Her sentinel satirinin yakininda gerekce metni bulunmali.
    for dosya, satirlar in bulunan.items():
        icerik = (md.KOK / dosya).read_text(encoding="utf-8").splitlines()
        for no, satir in satirlar:
            pencere = "\n".join(icerik[max(0, no - 3):no])
            assert GEREKCE.search(pencere), (
                f"{dosya}:{no} sentinel gerekcesiz (susturma riski): {satir}"
            )

