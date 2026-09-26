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

# NAV-AGAC-01 (D-213, KAHİN 2026-09-26): *"oluşturulmuş bir sayfa navigatör menü
# ağacında gözükmeli"* + *"her sayfa menüde gözüksün, sonra ilgili ve alakalı
# olanları birleştirelim"*. Bu, UX-MENU-04'ün "taşan sekmeyi menüden çıkar"
# kuralını geçersiz kıldı: artık MENÜSÜZ sayfa yok. Eski `MENUSUZ` demeti
# silindi — gizlenecek sayfa listesi tutmak D-211 ikiz yasağının UI hâli
# (üyeliği tek alan belirler: `TabTanimi.ust`).


def test_ust_sayfa_sayisi() -> None:
    assert len(ust_sayfalar()) <= 6


def test_her_sayfa_menu_agacinda() -> None:
    """NAV-AGAC-01: kök değilse mutlaka bir kökün altında olmalı — öksüz sayfa yok."""
    kokler = set(ust_sayfalar())
    oksuz = [t.anahtar for t in SECTIONS if t.ust is None and t.anahtar not in kokler]
    assert not oksuz, f"menü ağacında görünmeyen sayfa: {sorted(oksuz)}"


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
    """NAV-AGAC-01: sınır gizlemeyle değil BİRLEŞTİRMEYLE korunur (KAHİN: "ilgili
    ve alakalı olanları birleştirelim"). Birleştirme yapılana kadar üst sınır
    fiilî duruma göre 12; daha yükseğe çıkması yeni dağınıklıktır.
    """
    for anahtar in ust_sayfalar():
        assert len(alt_sekmeler(anahtar)) <= 12, anahtar


def test_derinlik_en_fazla_uc_seviye() -> None:
    """Alt sekmenin altında sekme olamaz (seviye 3 sayfa gövdesinde çözülür)."""
    ustler = set(ust_sayfalar())
    for tanim in SECTIONS:
        if tanim.ust:
            assert tanim.ust in ustler, f"{tanim.anahtar} -> {tanim.ust}"


def test_url_path_benzersiz() -> None:
    yollar = [t.url_path for t in SECTIONS]
    assert len(yollar) == len(set(yollar))


def test_her_sayfanin_adresi_cozulur() -> None:
    """NAV-AGAC-01: menüye alınan sayfaların URL'i de çalışmaya devam etmeli."""
    for tanim in SECTIONS:
        assert tab_getir(tanim.anahtar) is not None, tanim.anahtar
        assert tab_url_getir(tanim.url_path) is not None, tanim.url_path


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
