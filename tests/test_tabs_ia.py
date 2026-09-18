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
MENUSUZ = (
    "executive",
    "arama",
    "performans",
    "webhook",
    "dlq",
    "yenileme",
    "ayarlar",
    "yukleme",
)


def test_ust_sayfa_sayisi() -> None:
    assert len(ust_sayfalar()) <= 6


def test_menudeki_alt_sekme_sayisi() -> None:
    toplam = sum(len(alt_sekmeler(k)) for k in ust_sayfalar())
    assert toplam <= 16, f"menüde {toplam} alt sekme var"


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
