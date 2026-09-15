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
    GRUP_SISTEM,
    ROL_ADMIN,
    ROL_ANALYST,
    ROL_ANON,
    ROL_SEVIYE,
    ROL_USER,
    SECTIONS,
    YUZEY_HUGINN,
    YUZEY_MUNINN,
    YUZEYLER,
    TabTanimi,
    erisebilir,
    gorunur_bolumler,
    gruplar,
    musteri_onizleme_bolumleri,
    render_fonksiyonu,
    rol_normalize,
    tab_getir,
    tab_url_getir,
    varsayilan_tab,
)

# Sekme modulleri runtime disinda import edilince Streamlit "missing
# ScriptRunContext" uyarisi basar; test ciktisini kirletmesin.
logging.disable(logging.WARNING)


def test_bolum_sayisi_ve_benzersizlik() -> None:
    """BK5: bolum listesi eksiksiz ve anahtarlar/URL'ler benzersiz."""
    # 11 (temel) + 14 (U-11 dağıtım) + 1 (PO-BACK-08 executive) = 26
    # Temel: ana_kontrol, musteriler, paketler, pazarlama, abrakadabra, sistem, canli_veri, denetim, yonetim, ayarlar, yukleme
    # U-11: kpi, hatalar, kullanicilar, karar_defteri, kalite, arama, export, maliyet, performans, api, webhook, dlq, yenileme, kimlik
    # PO-BACK-08: executive (MRR/ARR + churn + tenant sağlık dağılımı)
    assert len(SECTIONS) == 26

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


# --------------------------------------------------------------------------- #
# U-10: Rol bazli menu gizleme
# --------------------------------------------------------------------------- #


def test_u10_rol_seviyeleri_rbac_ile_ayni() -> None:
    """Kopya sabitler auth.rbac.ROLE_HIERARCHY'den kaymasin."""
    from company_master.auth.rbac import ROLE_HIERARCHY

    assert ROL_SEVIYE == ROLE_HIERARCHY


def test_u10_her_bolumun_min_rolu_gecerli() -> None:
    for tanim in SECTIONS:
        assert tanim.min_rol in ROL_SEVIYE, tanim.anahtar


def test_u10_gecersiz_min_rol_reddedilir() -> None:
    with pytest.raises(ValueError):
        TabTanimi("x", "X", "x", GRUP_SISTEM, "", "x", min_rol="tanri")


@pytest.mark.parametrize(
    "ham,beklenen",
    [(None, ROL_ANON), ("", ROL_ANON), ("ADMIN", ROL_ADMIN), (" analyst ", ROL_ANALYST), ("kral", ROL_ANON)],
)
def test_u10_rol_normalize(ham, beklenen) -> None:
    assert rol_normalize(ham) == beklenen


def test_u10_admin_her_seyi_gorur_anon_daha_azini() -> None:
    admin = gorunur_bolumler(ROL_ADMIN)
    anon = gorunur_bolumler(ROL_ANON)
    assert admin == SECTIONS
    assert len(anon) < len(SECTIONS)
    assert set(anon) <= set(admin)


def test_u10_hiyerarsi_monoton() -> None:
    """Rol yukseldikce gorunen bolum kumesi kuculmez."""
    onceki: set[TabTanimi] = set()
    for rol in (ROL_ANON, ROL_USER, ROL_ANALYST, ROL_ADMIN):
        simdiki = set(gorunur_bolumler(rol))
        assert onceki <= simdiki, rol
        onceki = simdiki


def test_u10_anon_kritik_bolumleri_gormez_yonetimi_gorur() -> None:
    """Denetim/ayarlar/yukleme gizli; yonetim acik (admin giris formu orada)."""
    anon = {t.anahtar for t in gorunur_bolumler(ROL_ANON)}
    assert {"denetim", "ayarlar", "yukleme", "sistem", "canli_veri"}.isdisjoint(anon)
    assert {"ana_kontrol", "yonetim"} <= anon
    assert erisebilir(tab_getir("yonetim"), ROL_ANON)
    assert not erisebilir(tab_getir("denetim"), ROL_ANON)


def test_u10_analyst_sistem_gorur_denetim_gormez() -> None:
    analyst = {t.anahtar for t in gorunur_bolumler(ROL_ANALYST)}
    assert {"sistem", "canli_veri"} <= analyst
    assert "denetim" not in analyst


def test_u10_filtre_sections_i_degistirmez_ve_sirayi_korur() -> None:
    uzunluk = len(SECTIONS)
    anon = gorunur_bolumler(ROL_ANON)
    assert len(SECTIONS) == uzunluk
    assert gorunur_bolumler(None) is SECTIONS
    sira = [SECTIONS.index(t) for t in anon]
    assert sira == sorted(sira)


def test_u10_gruplar_rol_ile_bos_grup_dusurur() -> None:
    anon_gruplar = gruplar(ROL_ANON)
    for tanimlar in anon_gruplar.values():
        assert tanimlar, "bos grup sidebar'a sizmamali"
    toplam = sum(len(v) for v in anon_gruplar.values())
    assert toplam == len(gorunur_bolumler(ROL_ANON))
    assert sum(len(v) for v in gruplar().values()) == len(SECTIONS)


def test_etiket_ikon_ve_baslik_icerir() -> None:
    for tanim in SECTIONS:
        assert tanim.ikon and tanim.baslik and tanim.aciklama
        assert tanim.etiket == f"{tanim.ikon} {tanim.baslik}"


@pytest.mark.parametrize("tanim", SECTIONS, ids=lambda t: t.anahtar)
def test_ikon_st_page_icin_gecerli_emoji(tanim: TabTanimi) -> None:
    """PANEL-FIX-01: `st.Page(icon=...)` yalnız tek emoji kabul eder.

    "✓" (U+2713) gibi Unicode işaretleri emoji sayılmaz ve `sayfalari_uret`
    tüm paneli açılışta düşürür. Bu test regresyonu import aşamasında yakalar.
    """
    from streamlit.string_util import validate_icon_or_emoji

    validate_icon_or_emoji(tanim.ikon)


# ---------------------------------------------------------------------------
# MIG-UI-01: Ürün yüzeyi + "Müşteri Önizleme" ara adımı
# ---------------------------------------------------------------------------


def test_mig_yuzey_sabitleri() -> None:
    assert YUZEYLER == frozenset({YUZEY_MUNINN, YUZEY_HUGINN})
    assert YUZEY_MUNINN == "muninn" and YUZEY_HUGINN == "huginn"


def test_mig_varsayilan_yuzey_muninn() -> None:
    """Yeni bir bölüm yuzey belirtmezse iç ekip yüzeyinde kalır."""
    tanim = TabTanimi(
        anahtar="x", baslik="X", ikon="•", grup=GRUP_SISTEM,
        aciklama="a", url_path="x",
    )
    assert tanim.yuzey == YUZEY_MUNINN
    assert tanim.musteri_onizleme is False


def test_mig_bilinmeyen_yuzey_reddedilir() -> None:
    with pytest.raises(ValueError, match="yuzey"):
        TabTanimi(
            anahtar="x", baslik="X", ikon="•", grup=GRUP_SISTEM,
            aciklama="a", url_path="x", yuzey="odin",
        )


def test_mig_musteri_ekranlari_huginn_isaretli() -> None:
    """Sitemap MIG-UI-01: ana_kontrol, paketler, pazarlama → Huginn hedefli."""
    onizleme = {t.anahtar for t in musteri_onizleme_bolumleri()}
    assert onizleme == {"ana_kontrol", "paketler", "pazarlama"}
    for tanim in musteri_onizleme_bolumleri():
        assert tanim.yuzey == YUZEY_HUGINN
        assert tanim.musteri_onizleme is True


def test_mig_onizleme_bolumleri_sections_sirasini_korur() -> None:
    sira = [t.anahtar for t in SECTIONS if t.musteri_onizleme]
    assert [t.anahtar for t in musteri_onizleme_bolumleri()] == sira


def test_mig_sistem_bolumleri_muninn_kalir() -> None:
    """Yönetim/denetim gibi iç ekip bölümleri asla müşteri yüzeyine düşmez."""
    for anahtar in ("yonetim", "denetim", "sistem", "ayarlar"):
        tanim = tab_getir(anahtar)
        assert tanim is not None
        assert tanim.yuzey == YUZEY_MUNINN, anahtar
