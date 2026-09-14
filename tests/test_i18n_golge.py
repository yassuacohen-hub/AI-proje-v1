# -*- coding: utf-8 -*-
"""BEKÇİ-T: i18n ``t()`` fonksiyonunu gölgeleyen yerel ``t`` adlarını yakalar.

Gerekçe (FIX-AUDIT-T): ``from company_master.i18n import t`` yapan bir modülde
fonksiyon gövdesinin herhangi bir yerinde ``t`` adına atama olursa (döngü
değişkeni, comprehension, parametre, ``with ... as t`` vb.) Python o fonksiyonda
``t``'yi yerel sayar ve daha önceki ``t("anahtar")`` çağrısı ``UnboundLocalError``
verir. Bu test, sorun üretime sızmadan önce statik (AST) taramayla durdurur.
"""
from __future__ import annotations

import ast
from pathlib import Path

import pytest

KOK = Path(__file__).resolve().parents[1]
TARANAN_KOKLER: tuple[Path, ...] = (
    KOK / "app.py",
    KOK / "web_dashboard",
    KOK / "src" / "company_master",
)
YASAK_AD = "t"


def _dosyalar() -> list[Path]:
    sonuc: list[Path] = []
    for kok in TARANAN_KOKLER:
        if kok.is_file():
            sonuc.append(kok)
        elif kok.is_dir():
            sonuc.extend(sorted(kok.rglob("*.py")))
    return sonuc


def _t_ice_aktariyor(agac: ast.Module) -> bool:
    for dugum in ast.walk(agac):
        if isinstance(dugum, ast.ImportFrom) and dugum.module and dugum.module.startswith(
            "company_master.i18n"
        ):
            for isim in dugum.names:
                if (isim.asname or isim.name) == YASAK_AD:
                    return True
    return False


def _atanan_adlar(hedef: ast.AST) -> set[str]:
    """Bir atama hedefinden (Name/Tuple/List/Starred) düz ad kümesi çıkarır."""
    adlar: set[str] = set()
    for alt in ast.walk(hedef):
        if isinstance(alt, ast.Name) and isinstance(alt.ctx, ast.Store):
            adlar.add(alt.id)
    return adlar


def _golgeleyen_satirlar(agac: ast.Module) -> list[int]:
    satirlar: list[int] = []
    for dugum in ast.walk(agac):
        hedefler: list[ast.AST] = []
        if isinstance(dugum, (ast.For, ast.AsyncFor, ast.comprehension)):
            hedefler.append(dugum.target)
        elif isinstance(dugum, ast.Assign):
            hedefler.extend(dugum.targets)
        elif isinstance(dugum, (ast.AugAssign, ast.AnnAssign, ast.NamedExpr)):
            hedefler.append(dugum.target)
        elif isinstance(dugum, (ast.withitem,)) and dugum.optional_vars is not None:
            hedefler.append(dugum.optional_vars)
        elif isinstance(dugum, ast.arg):
            if dugum.arg == YASAK_AD:
                satirlar.append(dugum.lineno)
            continue
        elif isinstance(dugum, ast.ExceptHandler) and dugum.name == YASAK_AD:
            satirlar.append(dugum.lineno)
            continue
        for hedef in hedefler:
            if YASAK_AD in _atanan_adlar(hedef):
                satirlar.append(getattr(hedef, "lineno", getattr(dugum, "lineno", 0)))
    return sorted(set(satirlar))


def _t_kullanan_moduller() -> list[Path]:
    secilen: list[Path] = []
    for yol in _dosyalar():
        try:
            agac = ast.parse(yol.read_text(encoding="utf-8"), filename=str(yol))
        except (SyntaxError, UnicodeDecodeError):
            continue
        if _t_ice_aktariyor(agac):
            secilen.append(yol)
    return secilen


MODULLER = _t_kullanan_moduller()


def test_tarama_en_az_bir_modul_buldu() -> None:
    """Bekçi boşa çalışmasın: t() kullanan en az bir modül olmalı."""
    assert MODULLER, "i18n t() ice aktaran modul bulunamadi; tarama kokleri yanlis olabilir"


@pytest.mark.parametrize("yol", MODULLER, ids=lambda p: str(p.relative_to(KOK)))
def test_t_adi_yerel_olarak_golgelenmiyor(yol: Path) -> None:
    agac = ast.parse(yol.read_text(encoding="utf-8"), filename=str(yol))
    satirlar = _golgeleyen_satirlar(agac)
    assert not satirlar, (
        f"{yol.relative_to(KOK)}: `t` adi su satirlarda yeniden atanmis {satirlar} — "
        "i18n t() golgelenir (UnboundLocalError). Degiskeni yeniden adlandir "
        "(orn. etiket/gorev/tetik/satir)."
    )
