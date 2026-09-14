# -*- coding: utf-8 -*-
"""Oksuz sekme korumasi (K-01 regresyonu).

Neden bu dosya var?
-------------------
`tests/test_dashboard_nav.py` yalnizca *SECTIONS'ta kayitli olanin* calistigini
dogrular. Ama asil yasadigimiz hata bunun tersiydi: P7-46'da
`render_ayarlar_tab` yazildi, 78 testi gecti, gorev "done" damgasi yedi --
fakat `SECTIONS`'a eklenmedigi icin kullanici o ekrani hicbir zaman goremedi.
Yesil test + onayli gorev, "kullanici goruyor" anlamina gelmiyordu.

Bu dosya o bosluğu kapatir: `web_dashboard/tabs/` altinda tanimli her
`render_*_tab` fonksiyonu ya dogrudan `SECTIONS`'ta kayitli olmali, ya da
navigasyondan erisilebilen bir modul tarafindan cagrilmali. Ikisi de degilse
fonksiyon "oksuz"dur -- yazilmistir ama ekranda yoktur -- ve test kirilir.

Yontem: calisma zamani yerine statik analiz (AST). Streamlit modullerini
import etmeden, sadece kaynak kodu okuyarak cagri grafigi cikarilir.
"""
from __future__ import annotations

import ast
import sys
from pathlib import Path

import pytest

KOK = Path(__file__).resolve().parents[1]
if str(KOK) not in sys.path:
    sys.path.insert(0, str(KOK))

from web_dashboard.tabs import SECTIONS  # noqa: E402

TABS_DIR = KOK / "web_dashboard" / "tabs"
APP_PY = KOK / "app.py"
PAKET = "web_dashboard.tabs"


# ---------------------------------------------------------------- muafiyetler
# Buraya bir sey eklemek "bu fonksiyon bilerek navigasyon disinda" demektir.
# Gerekce zorunlu: ileride okuyan kisi neden muaf oldugunu bilmeli.
MUAF: dict[str, str] = {
    # Sekme degil, hata durumunda cagrilan yardimci ekran.
    "render_error_page": "Sekme degil; hata durumunda cagrilan yardimci gorunum.",
}


# ------------------------------------------------------------- bilinen aciklar
# MUAF ile farki: bunlar "sorun degil" demek DEGIL, "sorun var ama henuz
# karara baglanmadi" demek. `xfail(strict=True)` ile isaretlenirler:
#   - Bugun oksuz olduklari icin test YESIL kalir (CI'i bloklamaz),
#   - Biri navigasyona baglaninca XPASS verip bu listeden silinmesini zorlar,
#   - Liste dosyada durdugu icin bulgu unutulmaz / gomulmez.
# Bir kaydi buradan silmeden once ya SECTIONS'a bagla ya MUAF'a tasi.
BILINEN_ACIK: dict[str, str] = {
}


# ------------------------------------------------------------------ yardimcilar
def _agac(yol: Path) -> ast.Module:
    """Dosyayi AST'e cevirir (UTF-8 + BOM toleransli)."""
    return ast.parse(yol.read_text(encoding="utf-8-sig"), filename=str(yol))


def _modul_dosyasi(modul: str) -> Path | None:
    """`web_dashboard.tabs.x` -> dosya yolu. Paket disiysa None."""
    if not modul.startswith(PAKET):
        return None
    parca = modul.split(".")[-1]
    yol = TABS_DIR / f"{parca}.py"
    return yol if yol.exists() else None


def _ice_aktarilan_moduller(agac: ast.Module) -> set[str]:
    """Dosyanin (fonksiyon govdeleri dahil) ice aktardigi tabs modulleri."""
    bulunan: set[str] = set()
    for dugum in ast.walk(agac):
        if isinstance(dugum, ast.ImportFrom) and dugum.module:
            if dugum.module.startswith(PAKET):
                bulunan.add(dugum.module)
        elif isinstance(dugum, ast.Import):
            for ad in dugum.names:
                if ad.name.startswith(PAKET):
                    bulunan.add(ad.name)
    return bulunan


def _kullanilan_isimler(agac: ast.Module) -> set[str]:
    """Dosyada cagrilan / referans verilen tum isimler.

    Hem `render_x()` dogrudan cagrisini hem `modul.render_x` erisimini hem de
    `RENDER_OVERRIDES = {"x": render_x}` gibi referans gecirmelerini yakalar.
    """
    isimler: set[str] = set()
    for dugum in ast.walk(agac):
        if isinstance(dugum, ast.Name):
            isimler.add(dugum.id)
        elif isinstance(dugum, ast.Attribute):
            isimler.add(dugum.attr)
        elif isinstance(dugum, ast.Constant) and isinstance(dugum.value, str):
            # SECTIONS kaydi fonksiyon adini duz metin olarak tutuyor.
            isimler.add(dugum.value)
    return isimler


def _tanimli_render_fonksiyonlari() -> dict[str, str]:
    """tabs/ altindaki tum `render_*` tanimlari -> {fonksiyon: modul dosyasi}."""
    tanimlar: dict[str, str] = {}
    for yol in sorted(TABS_DIR.glob("*.py")):
        if yol.name == "__init__.py":
            continue
        for dugum in _agac(yol).body:
            if isinstance(dugum, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if dugum.name.startswith("render_"):
                    tanimlar[dugum.name] = yol.name
    return tanimlar


def _erisilebilir_kapsam() -> set[str]:
    """Navigasyondan ulasilabilen tum isimlerin birlesimi.

    Baslangic noktalari: `app.py` + `SECTIONS`'taki hazir modul kayitlari.
    Oradan `from web_dashboard.tabs.x import ...` baglantilari gecisli
    (transitive) izlenir; boylece `admin_sistem` gibi toplayici sekmelerin
    icindeki alt panel cagrilari da kapsama girer.
    """
    kuyruk: list[Path] = [APP_PY]
    for tanim in SECTIONS:
        if tanim.hazir and tanim.modul:
            dosya = _modul_dosyasi(tanim.modul)
            if dosya is not None:
                kuyruk.append(dosya)

    gezildi: set[Path] = set()
    isimler: set[str] = set()

    while kuyruk:
        yol = kuyruk.pop()
        if yol in gezildi or not yol.exists():
            continue
        gezildi.add(yol)

        agac = _agac(yol)
        isimler |= _kullanilan_isimler(agac)
        for modul in _ice_aktarilan_moduller(agac):
            dosya = _modul_dosyasi(modul)
            if dosya is not None and dosya not in gezildi:
                kuyruk.append(dosya)

    return isimler


# Modul seviyesinde bir kez hesapla; her parametrede yeniden tarama yapma.
_TANIMLAR = _tanimli_render_fonksiyonlari()
_KAPSAM = _erisilebilir_kapsam()
_SECTIONS_FONKSIYONLARI = {t.fonksiyon for t in SECTIONS if t.fonksiyon}


# ------------------------------------------------------------------- testler
def test_tanimli_render_fonksiyonu_bulundu() -> None:
    """Tarama gercekten calisti mi? (bos kume yanlis yesil verir)"""
    assert len(_TANIMLAR) >= 15, f"AST taramasi beklenenden az sonuc verdi: {_TANIMLAR}"


def test_kapsam_taramasi_calisti() -> None:
    """Gecisli (transitive) erisilebilirlik grafigi gercekten yuruyor mu?

    `render_webhook_monitor_tab` bilincli secildi: SECTIONS'ta dogrudan kaydi
    YOK, yalnizca `admin_sistem.render_sistem_tab()` icinden cagriliyor. Yani
    bu isim kapsamda gorunuyorsa, tarama "SECTIONS -> modul -> alt modul"
    zincirini en az bir adim izleyebilmis demektir.

    (Onceki surumde burada `render_ana_kontrol_tab` vardi; o isim SECTIONS'ta
    yalnizca duz metin olarak duruyor ve hicbir yerden cagrilmiyor -- yani
    kapsamda olmamasi dogruydu, hatali olan kontrolun kendisiydi.)
    """
    assert "render_webhook_monitor_tab" in _KAPSAM, (
        "Gecisli tarama calismiyor: admin_sistem icindeki alt panel cagrilari "
        "gorulemedi. _erisilebilir_kapsam() bozulmus olabilir."
    )


@pytest.mark.parametrize("fonksiyon", sorted(_TANIMLAR))
def test_render_fonksiyonu_oksuz_degil(fonksiyon: str, request) -> None:
    """Yazilmis her render fonksiyonu kullaniciya ulasabilir olmali.

    Kirilirsa yapilacak is: fonksiyonu `SECTIONS`'a bir `TabTanimi` olarak ekle,
    ya da mevcut bir toplayici sekmeden cagir. Bilerek disarida birakiyorsan
    `MUAF` sozlugune gerekcesiyle yaz. Karar henuz verilmediyse `BILINEN_ACIK`
    listesine gerekcesiyle ekle (test yesil kalir ama bulgu kayitli durur).
    """
    if fonksiyon in MUAF:
        pytest.skip(f"muaf: {MUAF[fonksiyon]}")

    if fonksiyon in BILINEN_ACIK:
        # strict=True: bu fonksiyon navigasyona baglandigi an test XPASS verir
        # ve bizi BILINEN_ACIK kaydini silmeye zorlar. Boylece liste sessiz bir
        # "gormezden gelme" mekanizmasina donusmez.
        request.node.add_marker(
            pytest.mark.xfail(
                strict=True,
                reason=f"BILINEN ACIK: {BILINEN_ACIK[fonksiyon]}",
            )
        )

    dosya = _TANIMLAR[fonksiyon]
    baglayici = fonksiyon in _SECTIONS_FONKSIYONLARI
    cagrilan = fonksiyon in _KAPSAM

    assert baglayici or cagrilan, (
        f"OKSUZ SEKME: `{fonksiyon}` ({dosya}) yazilmis ama kullaniciya ulasmiyor.\n"
        f"  - SECTIONS kaydi yok\n"
        f"  - navigasyondan erisilebilen hicbir modul onu cagirmiyor\n"
        f"Cozum: web_dashboard/tabs/__init__.py icindeki SECTIONS'a TabTanimi ekle, "
        f"ya da bir toplayici sekmeden cagir. Bilerek disarida ise tests/"
        f"test_sekme_kapsama.py icindeki MUAF sozlugune gerekcesiyle ekle."
    )


@pytest.mark.parametrize(
    "tanim", [t for t in SECTIONS if t.hazir], ids=lambda t: t.anahtar
)
def test_sections_kaydi_gercek_dosyaya_isaret_eder(tanim) -> None:
    """SECTIONS'taki modul/fonksiyon ikilisi diskte gercekten var mi?

    `test_dashboard_nav` bunu import ederek dogruluyor; burada ek olarak
    kaynak dosyada `def <fonksiyon>` tanimi oldugunu statik kontrol ediyoruz
    (yanlis modul adi yazilmasi gibi sessiz hatalari yakalar).
    """
    assert tanim.modul, f"{tanim.anahtar}: hazir ama modul bos"
    assert tanim.fonksiyon, f"{tanim.anahtar}: hazir ama fonksiyon bos"

    dosya = _modul_dosyasi(tanim.modul)
    assert dosya is not None, f"{tanim.anahtar}: modul dosyasi bulunamadi ({tanim.modul})"
    assert _TANIMLAR.get(tanim.fonksiyon) == dosya.name, (
        f"{tanim.anahtar}: `{tanim.fonksiyon}` fonksiyonu {dosya.name} icinde "
        f"tanimli degil (bulundugu yer: {_TANIMLAR.get(tanim.fonksiyon)})"
    )


def test_muaf_listesi_gerekcesiz_kayit_icermez() -> None:
    """Muafiyet sessizce buyumesin: her kaydin gerekcesi olmali."""
    for ad, gerekce in MUAF.items():
        assert gerekce.strip(), f"{ad}: muafiyet gerekcesi bos"
        assert ad in _TANIMLAR, (
            f"{ad}: MUAF listesinde ama artik boyle bir fonksiyon yok -- "
            f"olu muafiyet kaydini sil."
        )
