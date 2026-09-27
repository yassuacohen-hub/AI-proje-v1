"""Mandal: test modulleri global logging durumunu kalici olarak bozmasin.

GERCEK OLAY (2026-09-27):
    tests/test_dashboard_nav.py modul seviyesinde `logging.disable(logging.WARNING)`
    cagiriyordu. pytest toplama asamasinda TUM test modullerini import ettigi icin
    bu cagri suite basinda devreye giriyor ve hicbir yerde geri alinmiyordu.
    Sonuc: test_error_handling.py'deki 3 test tek basina yesil, tam suitte kirmizi.
    Tam iki gun "gercek hata mi, sizinti mi" tartisildi.

Bu dosya iki seyi birlikte kilitler:
    1) Kaynak duzeyi: hicbir test modulu modul seviyesinde logging.disable cagirmaz.
    2) Davranis duzeyi: suite calisirken global disable seviyesi kapali kalir.

Gurultu bastirmak gerekiyorsa cozum global degil yerel olmali:
    - caplog fixture'i,
    - ya da fixture icinde disable + finally ile geri alma.
"""

from __future__ import annotations

import ast
import logging
from pathlib import Path

import pytest

TESTS_DIZINI = Path(__file__).resolve().parent

# Global logging durumunu bozan cagrilar. Fonksiyon/fixture GOVDESINDE olmasi
# sorun degil (orada geri alinabilir); yasak olan MODUL seviyesi.
YASAKLI_CAGRILAR = {
    ("logging", "disable"),
    ("logging", "basicConfig"),
    ("logging", "shutdown"),
}


def _test_dosyalari() -> list[Path]:
    return sorted(TESTS_DIZINI.rglob("test_*.py"))


def _modul_seviyesi_ihlaller(yol: Path) -> list[str]:
    """Modul govdesindeki (fonksiyon/sinif disi) yasakli cagrilari dondurur."""
    try:
        agac = ast.parse(yol.read_text(encoding="utf-8"))
    except SyntaxError:  # pragma: no cover - bozuk dosya baska test isi
        return []

    ihlaller: list[str] = []
    # Sadece en ust seviye ifadeler: fonksiyon/sinif govdesine inmiyoruz.
    for dugum in agac.body:
        for alt in ast.walk(dugum):
            if not isinstance(alt, ast.Call):
                continue
            hedef = alt.func
            if not isinstance(hedef, ast.Attribute):
                continue
            if not isinstance(hedef.value, ast.Name):
                continue
            if (hedef.value.id, hedef.attr) in YASAKLI_CAGRILAR:
                ihlaller.append(
                    f"{yol.name}:{alt.lineno} -> {hedef.value.id}.{hedef.attr}()"
                )
    return ihlaller


def test_hicbir_test_modulu_global_logging_kapatmaz() -> None:
    """Modul seviyesinde logging.disable/basicConfig = tum suiteye sizan yan etki."""
    tum_ihlaller: list[str] = []
    for yol in _test_dosyalari():
        if yol.name == Path(__file__).name:  # bu dosya kendini taramasin
            continue
        tum_ihlaller.extend(_modul_seviyesi_ihlaller(yol))

    assert not tum_ihlaller, (
        "Test modulu seviyesinde global logging durumu bozuluyor:\n  "
        + "\n  ".join(tum_ihlaller)
        + "\n\nBu cagri pytest toplama aninda calisir ve TUM suite boyunca kalir."
        "\nCozum: caplog kullan ya da fixture icinde yap ve finally ile geri al."
    )


def test_suite_calisirken_global_disable_kapali() -> None:
    """Davranis mandali: baska bir modul disable birakmissa burada yakalanir."""
    mevcut = logging.root.manager.disable
    assert mevcut == 0, (
        f"Global logging devre disi birakilmis (disable={mevcut}, "
        f"{logging.getLevelName(mevcut)}). Bir test modulu/fixture durumu geri "
        "almamis; logging davranisini olcen testler sahte kirmizi verir."
    )


def test_dashboard_nav_regresyon_bekcisi() -> None:
    """Asil olayin gectigi dosya icin nokta kontrol (regresyon kilidi)."""
    yol = TESTS_DIZINI / "test_dashboard_nav.py"
    if not yol.exists():  # dosya adi degistiyse genel tarama yine korur
        pytest.skip("test_dashboard_nav.py yok")
    assert not _modul_seviyesi_ihlaller(yol), (
        "test_dashboard_nav.py yeniden global logging.disable eklemis: "
        "2026-09-27 sizintisi geri dondu."
    )
