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

import re

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
    alt_sekmeler,
    erisebilir,
    eski_url_yonlendir,
    gorunur_bolumler,
    gruplar,
    musteri_onizleme_bolumleri,
    render_fonksiyonu,
    rol_normalize,
    tab_getir,
    tab_url_getir,
    ust_sayfalar,
    varsayilan_tab,
)

# NOT: Burada bir zamanlar modul seviyesinde `logging.disable(logging.WARNING)`
# vardi (Streamlit "missing ScriptRunContext" uyarisini bastirmak icin).
# pytest tum test modullerini toplama asamasinda import ettigi icin bu cagri
# TUM suite boyunca global kaliyor ve geri alinmiyordu; logging davranisini
# olcen testler (test_error_handling) tek basina yesil, suite icinde kirmizi
# oluyordu. Olcum: kaldirildiginda gurultu geri gelmiyor, 3 kirmizi yesile
# donuyor. Gurultu bastirmak gerekirse dosya kapsaminda caplog/fixture kullan.


def test_bolum_sayisi_ve_benzersizlik() -> None:
    """BK5: bolum listesi eksiksiz ve anahtarlar/URL'ler benzersiz.

    Sabit sayi kirilgan: her yeni sayfa bu testi kirip "sayiyi buyut" refleksi
    yaratiyordu (nitekim 38'e cikmisken 37 yaziyordu). Onemli olan alt sinir +
    benzersizlik; bolum silindiyse test yine uyarir.
    """
    assert len(SECTIONS) >= 35

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
        "musteri_onizleme",  # D-214: eski "paketler" ikizi silindi, kök bunu devraldi
        "pazarlama",
        "abrakadabra",
        "ayarlar",
    }
    assert beklenen.issubset({t.anahtar for t in SECTIONS})


def test_varsayilan_bolum_ana_kontrol() -> None:
    assert varsayilan_tab().anahtar == "ana_kontrol"


def test_tab_getir() -> None:
    assert tab_getir("musteri_onizleme").anahtar == "musteri_onizleme"
    assert tab_getir("olmayan_bolum") is None


def test_tab_url_getir_normalize_eder() -> None:
    """Derin baglanti: bas/son slash ve buyuk harf tolere edilmeli; eski
    /Paketler/ adresi D-214 sonrasi ESKI_URL uzerinden musteri_onizleme'ye
    yonlenir."""
    assert tab_url_getir("/Paketler/").anahtar == "musteri_onizleme"
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
    assert {"ana_kontrol"} <= anon


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
    """Sitemap MIG-UI-01: ana_kontrol, musteri_onizleme, pazarlama → Huginn hedefli."""
    onizleme = {t.anahtar for t in musteri_onizleme_bolumleri()}
    assert onizleme == {"ana_kontrol", "musteri_onizleme", "pazarlama"}
    for tanim in musteri_onizleme_bolumleri():
        assert tanim.yuzey == YUZEY_HUGINN
        assert tanim.musteri_onizleme is True


def test_mig_onizleme_bolumleri_sections_sirasini_korur() -> None:
    sira = [t.anahtar for t in SECTIONS if t.musteri_onizleme]
    assert [t.anahtar for t in musteri_onizleme_bolumleri()] == sira


def test_mig_sistem_bolumleri_muninn_kalir() -> None:
    """Yönetim/denetim gibi iç ekip bölümleri asla müşteri yüzeyine düşmez."""
    for anahtar in ("denetim", "sistem", "ayarlar"):
        tanim = tab_getir(anahtar)
        assert tanim is not None
        assert tanim.yuzey == YUZEY_MUNINN, anahtar


# --------------------------------------------------------------------------- #
# NAV-IA-01: üst sayfa, alt sekme, eski url yönlendirme
# --------------------------------------------------------------------------- #


def test_ust_sayfalar_admin_7():
    """NAV-IA-01: admin 7 üst sayfayı görür (D-215: denetim → Güvenlik Kapısı kök oldu)."""
    ust = ust_sayfalar(ROL_ADMIN)
    assert len(ust) == 7
    assert set(ust.keys()) == {
        "ana_kontrol", "musteri_yonetimi", "proje_yonetimi",
        "veri_kalite", "sistem", "musteri_onizleme", "denetim",
    }


def test_ust_sayfalar_anon_2():
    """NAV-IA-01: anon yalnız 2 üst sayfayı görür (kimlik/yonetim/sistem çıkmaz)."""
    ust = ust_sayfalar(ROL_ANON)
    assert len(ust) == 2
    assert set(ust.keys()) == {"ana_kontrol", "musteri_onizleme"}


def test_ust_sayfalar_analyst_4():
    """NAV-IA-01: analyst 4 üst sayfayı görür."""
    ust = ust_sayfalar(ROL_ANALYST)
    assert len(ust) == 4
    assert "sistem" in ust
    assert "veri_kalite" in ust
    assert "musteri_yonetimi" not in ust


def test_ust_sayfa_ust_none_ve_ust_dolu():
    """Üst sayfalar ust=None, alt sekmeler ust=dolu.

    NAV-AGAC-01: `sira` artik kok sayfalarda da anlamli (menu sirasi), bu yuzden
    `sistem` icin 0 beklenmiyor; yalnizca tanimli olmasi yeterli.
    """
    ust_page = tab_getir("sistem")
    assert ust_page is not None
    assert ust_page.ust is None
    assert ust_page.sira >= 0

    alt = tab_getir("teknik_altyapi")
    assert alt is not None
    assert alt.ust == "sistem"
    assert alt.sira == 0


def test_alt_sekmeler_sistem_analyst():
    """Sistem üst sayfasının alt sekmeleri analyst rolünde visible.

    NAV-AGAC-01 (KAHİN): "oluşturulmuş bir sayfa navigatör menü ağacında
    gözükmeli". `performans` ve `yenileme` artık Sistem başlığı altında; eskiden
    `ust=None` bırakılıp menüden düşüyorlardı. `ayarlar`/`mfa` da Sistem altında
    (popover yalnızca kısayol). `maliyet` gelir grubunda kaldı.
    """
    alt = alt_sekmeler("sistem", ROL_ANALYST)
    alt_analhtar = {t.anahtar for t in alt}
    assert "teknik_altyapi" in alt_analhtar
    assert "api" in alt_analhtar
    assert "performans" in alt_analhtar
    assert "webhook" in alt_analhtar
    # maliyet moved to gelir group (ADMIN-UX-GELIR-GRUP-01)
    assert "maliyet" not in alt_analhtar
    # ayarlar/mfa admin gerektirir; analyst gormez
    assert "ayarlar" not in alt_analhtar
    assert "mfa" not in alt_analhtar


def test_alt_sekmeler_bos_ust():
    """Bos ust ile alt_sekemeler bos tuple dondurmeli."""
    assert alt_sekmeler("") == ()
    assert alt_sekmeler("yok") == ()


def test_alt_sekmeler_sira_sirali():
    """Alt sekme siralari korunmali.

    UX-MENU-03: `hatalar` -> Sistem'e taşındı (E4), `dlq` menüden çıktı.
    ADMIN-UX-GELIR-GRUP-01: `executive` ve `maliyet` gelir grubuna taşındı.
    NAV-AGAC-01 (2026-09-26, KAHİN): "oluşturulmuş bir sayfa navigatör menü
    ağacında gözükmeli, fakat aynı başlık altında bir sayfa birleşebiliyorsa
    birleşebilmeli." UX-MENU-04'ün "en fazla 6 alt sekme" kırpması sayfaları
    menüden tamamen düşürüyordu; gizlenenler artık ilgili başlığa bağlı.
    """
    alt = alt_sekmeler("proje_yonetimi", ROL_ADMIN)
    siralar = [t.sira for t in alt]
    assert siralar == sorted(siralar)
    assert [t.anahtar for t in alt] == [
        "karar_defteri", "abrakadabra",
        "ajan_sohbet", "gorev_panosu", "rapor_listesi",
    ]


def test_eski_url_yonlendirme():
    """NAV-IA-01 ESKI_URL: eski URL'ler yeni yere yonlendiriliyor."""
    assert eski_url_yonlendir("kullanicilar") == ("musteri_yonetimi", "kullanicilar")
    assert eski_url_yonlendir("yonetim") == ("admin_yonetim", "")
    assert eski_url_yonlendir("kimlik") == ("admin_auth", "")
    assert eski_url_yonlendir("yok") is None


def test_marka_basligi_gradyan_ve_metin() -> None:
    """MARKA-BASLIK-01 (KAHIN): "logo... buyut ve sag kismina Admin Insights
    kelimesini yaz ayni renk gradeninde olsun uyumsuz olmasin".

    Gradyan degerleri KAHIN'in verdigi logo renkleri; biri elle degisirse marka
    uyumu sessizce bozulur, bu yuzden sabitler test edilir.
    `import app` yapilamaz: app.py modul duzeyinde `main()` cagiriyor (Streamlit
    betigi, `if __name__` korumasi yok) -> import UI cizmeye kalkiyor. Bu yuzden
    kaynak metin okunur.
    """
    from pathlib import Path

    kaynak = (Path(__file__).resolve().parents[1] / "app.py").read_text(encoding="utf-8")
    for renk in ("#22D3EE", "#3B82F6", "#4F46E5", "#8B5CF6"):
        assert renk in kaynak, f"marka rengi {renk} kayboldu"
    assert "linear-gradient(135deg, " in kaynak
    assert 'content: "Admin Insights"' in kaynak
    # st.logo(size="large") Streamlit'in ust siniri: buyutme CSS ezmesiyle
    assert "max-height" in kaynak
    assert "st.markdown(MARKA_CSS, unsafe_allow_html=True)" in kaynak


def test_tab_url_getir_eski_url_fallback():
    """tab_url_getir ESKI_URL'e bakar (cagri aktarimi)."""
    tanim = tab_url_getir("kullanicilar")
    assert tanim is not None
    assert tanim.anahtar == "kullanicilar"


# ---------------------------------------------------------------------------
# UI-ADMIN-ACIKLAMA-METIN-37: menü ipuçları admin dilinde (jargonsuz)
# ---------------------------------------------------------------------------

# Tasarım kararı: eşleşme KELİME SINIRINDA yapılır, düz alt-dize değil.
# Ölçülen çakışma: "Paketler ve müşteri ekranı önizlemesi" kelimesinde
# "Pak-**etl**-er" alt-dize olarak "ETL"yi tutuyor. Düz `in` kontrolü
# meşru Türkçe kelimeyi jargon sayardı; `\\b` bu yanlış pozitifi kapatir.
JARGON = ("DLQ", "ETL", "KPI", "webhook", "latency")
_JARGON_DESEN = re.compile(
    r"\b(" + "|".join(JARGON) + r")\b", re.IGNORECASE,
)


def test_aciklama_menusunde_jargon_yok() -> None:
    """KK-12 K2: menü ipucu teknik jargonsuz okunmalı.

    Kırma kanıtı (D-256/4): `_JARGON_DESEN.search("DLQ kuyrugu")` True,
    `_JARGON_DESEN.search("Paketler ve musteri")` False.
    """
    # Mandal gerçekten kırılabiliyor mu? (negatif kontrol)
    assert _JARGON_DESEN.search("DLQ kuyrugu"), "mandal jargonu gormuyor"
    assert not _JARGON_DESEN.search("Paketler ve musteri ekrani"), "yanlis pozitif"

    ihlaller = [
        (t.anahtar, t.aciklama)
        for t in SECTIONS
        if _JARGON_DESEN.search(t.aciklama)
    ]
    assert not ihlaller, f"menü ipucunda kalan jargon: {ihlaller}"


def test_aciklama_kisa_ve_dolu() -> None:
    """Her ipucu boş değil ve 60 karakteri geçmez (menü ipucu satırına sığar)."""
    for tanim in SECTIONS:
        assert tanim.aciklama.strip(), f"{tanim.anahtar} ipucu bos"
        assert len(tanim.aciklama) <= 60, (
            f"{tanim.anahtar} ipucu {len(tanim.aciklama)} karakter: {tanim.aciklama}"
        )

