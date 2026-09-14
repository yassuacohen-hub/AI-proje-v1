# -*- coding: utf-8 -*-
"""P7-44: Dashboard navigasyon kayit defteri regresyon testleri.

Amac (K-01'in tekrar olusmasini engellemek):
`web_dashboard/tabs/` altina yazilan bir sekme kodu, `app.py` sidebar'ina
baglanmadigi icin kullaniciya gorunmuyordu. Artik sidebar + yonlendirme
tek kaynaktan (`SECTIONS`) uretiliyor. Bu test, kayit defterindeki her
hazir bolumun gercekten cagirilabilir bir render fonksiyonuna
cozumlendigini dogrular. Bir sekme koparsa test kirilir.

Not: `web_dashboard.tabs.__init__` Streamlit import etmez; bu yuzden test
Streamlit runtime olmadan calisir.
"""
from __future__ import annotations

import logging

import pytest

from web_dashboard.tabs import (
    SECTIONS,
    TabTanimi,
    gruplar,
    render_fonksiyonu,
    tab_getir,
    tab_url_getir,
    varsayilan_tab,
)

# Sekme modulleri runtime disinda import edilince Streamlit "missing
# ScriptRunContext" uyarisi basar; test ciktisini kirletmesin.
logging.disable(logging.WARNING)


def test_bolum_sayisi_ve_benzersizlik() -> None:
    """BK5: bolum listesi eksiksiz ve anahtarlar/URL'ler benzersiz."""
    # 9 temel bolum + Denetim (DASH-08) + Yukleme Durumlari (P7-42) = 11
    assert len(SECTIONS) == 11

    anahtarlar = [t.anahtar for t in SECTIONS]
    urller = [t.url_path for t in SECTIONS]
    assert len(set(anahtarlar)) == len(anahtarlar), "anahtar tekrari var"
    assert len(set(urller)) == len(urller), "url_path tekrari var"


def test_bk5_zorunlu_bolumler_mevcut() -> None:
    """BK5'te sozu gecen 7 bolum + Canli Veri + Ayarlar kayit defterinde olmali."""
    beklenen = {
        "ana_kontrol",
        "musteriler",
        "sistem",
        "paketler",
        "pazarlama",
        "abrakadabra",
        "yonetim",
        "ayarlar",
    }
    assert beklenen.issubset({t.anahtar for t in SECTIONS})


def test_varsayilan_bolum_ana_kontrol() -> None:
    assert varsayilan_tab().anahtar == "ana_kontrol"


def test_tab_getir() -> None:
    assert tab_getir("paketler").anahtar == "paketler"
    assert tab_getir("olmayan_bolum") is None


def test_tab_url_getir_normalize_eder() -> None:
    """Derin baglanti: bas/son slash ve buyuk harf tolere edilmeli."""
    assert tab_url_getir("/Paketler/").anahtar == "paketler"
    assert tab_url_getir("canli-veri").anahtar == "canli_veri"
    assert tab_url_getir("") is None
    assert tab_url_getir("olmayan") is None


def test_gruplar_tum_bolumleri_kapsar() -> None:
    """Sidebar gruplamasi hicbir bolumu dusurmemeli (gorunmez sekme olmasin)."""
    gruplama = gruplar()
    toplam = sum(len(v) for v in gruplama.values())
    assert toplam == len(SECTIONS)
    # Huginn + Muninn en az iki grup; yeni gruplar eklenebilir (kırılgan == yerine >=).
    assert len(gruplama) >= 2


@pytest.mark.parametrize("tanim", [t for t in SECTIONS if t.hazir], ids=lambda t: t.anahtar)
def test_hazir_bolum_render_fonksiyonuna_cozumlenir(tanim: TabTanimi) -> None:
    """K-01 regresyonu: hazir isaretli her bolum gercekten cagirilabilir olmali."""
    fn = render_fonksiyonu(tanim)
    assert callable(fn), (
        f"{tanim.anahtar} bolumu ekrana baglanamadi: "
        f"beklenen {tanim.modul}.{tanim.fonksiyon}"
    )


@pytest.mark.parametrize("tanim", [t for t in SECTIONS if not t.hazir], ids=lambda t: t.anahtar)
def test_hazir_olmayan_bolum_bekleyen_gorev_bildirir(tanim: TabTanimi) -> None:
    """Placeholder bolum sessiz olu link olmamali; bekleyen gorev ID'si tasimali."""
    assert render_fonksiyonu(tanim) is None
    assert tanim.bekleyen_gorev, f"{tanim.anahtar} icin bekleyen_gorev bos"


def test_etiket_ikon_ve_baslik_icerir() -> None:
    for tanim in SECTIONS:
        assert tanim.ikon and tanim.baslik and tanim.aciklama
        assert tanim.etiket == f"{tanim.ikon} {tanim.baslik}"
