# -*- coding: utf-8 -*-
"""UX-MENU-03: Sol menü bilgi mimarisi ölçütleri.

E1-E5 birleştirmeleri sonrası menü ağacının sınırlar içinde kaldığını ve
menüden çıkarılan sekmelerin URL'lerinin kırılmadığını doğrular.
"""

from __future__ import annotations

from web_dashboard.tabs import (
    SECTIONS,
    alt_sekmeler,
    tab_getir,
    tab_url_getir,
    ust_sayfalar,
)

# Menüden çıkarılan (ust=None) ama URL'i yaşamaya devam eden sekmeler.
# UX-MENU-04 (2026-09-25): proje_yonetimi 11 alt sekmeden 4'e indi; taşan
# sekmeler seviye 3'e (sayfa gövdesi) veya hesap popover'ına çıktı.
MENUSUZ = (
    "executive",
    "arama",
    "performans",
    "webhook",
    "yenileme",
    "ayarlar",
    "yukleme",
    "ajan_sohbet",
    "rapor_listesi",
    "kvkk_rapor",
    "kontrol_panosu",
    "feature_flags",
    "mfa",
)


def test_ust_sayfa_sayisi() -> None:
    assert len(ust_sayfalar()) <= 6


def test_menudeki_alt_sekme_sayisi() -> None:
    toplam = sum(len(alt_sekmeler(k)) for k in ust_sayfalar())
    assert toplam <= 18, f"menüde {toplam} alt sekme var"


def test_etiket_benzersiz() -> None:
    """UX-MENU-04: aynı ikon+başlık iki kez çizilemez (çift buton kaynağı)."""
    etiketler = [f"{t.ikon} {t.baslik}" for t in SECTIONS]
    cift = {e for e in etiketler if etiketler.count(e) > 1}
    assert not cift, f"çift etiket: {sorted(cift)}"


def test_ikon_benzersiz() -> None:
    """UX-MENU-04: menüde görünen her sekmenin ikonu ayırt edici olmalı."""
    menudeki = [t for t in SECTIONS if t.ust or t.anahtar in ust_sayfalar()]
    ikonlar = [t.ikon for t in menudeki]
    cift = {i for i in ikonlar if ikonlar.count(i) > 1}
    assert not cift, f"çift ikon: {sorted(cift)}"


def test_sira_bosluksuz() -> None:
    """UX-MENU-04: alt sekme sıraları 0..n-1 aralığını boşluksuz doldurur."""
    for anahtar in ust_sayfalar():
        siralar = [t.sira for t in alt_sekmeler(anahtar)]
        assert siralar == list(range(len(siralar))), f"{anahtar}: {siralar}"


def test_ust_basina_alt_sekme_siniri() -> None:
    for anahtar in ust_sayfalar():
        assert len(alt_sekmeler(anahtar)) <= 6, anahtar


def test_derinlik_en_fazla_uc_seviye() -> None:
    """Alt sekmenin altında sekme olamaz (seviye 3 sayfa gövdesinde çözülür)."""
    ustler = set(ust_sayfalar())
    for tanim in SECTIONS:
        if tanim.ust:
            assert tanim.ust in ustler, f"{tanim.anahtar} -> {tanim.ust}"


def test_url_path_benzersiz() -> None:
    yollar = [t.url_path for t in SECTIONS]
    assert len(yollar) == len(set(yollar))


def test_menuden_cikanlarin_adresi_kirilmadi() -> None:
    for anahtar in MENUSUZ:
        tanim = tab_getir(anahtar)
        assert tanim is not None, anahtar
        assert tanim.ust is None, f"{anahtar} hâlâ menüde"
        assert tab_url_getir(tanim.url_path) is not None, anahtar


def test_birlestirilen_sekme_basliklari() -> None:
    assert tab_getir("kpi").baslik == "Özet"
    assert tab_getir("hatalar").baslik == "Olaylar & Hatalar"
    assert tab_getir("hatalar").ust == "sistem"
    assert tab_getir("teknik_altyapi").baslik == "Altyapı"


if __name__ == "__main__":  # elle çalıştırma: python tests/test_tabs_ia.py
    for ad, fn in sorted(globals().items()):
        if ad.startswith("test_") and callable(fn):
            fn()
            print("OK", ad)
