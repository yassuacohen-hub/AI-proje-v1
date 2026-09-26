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
    """D-215 ratchet: 7 kök (Gelir Kapısı + Güvenlik Kapısı eklendi).

    Tavan 6'dan 7'ye yükseldi — KAHİN onayıyla (D-214 prensibi: tavan
    sabit kalırsa yeni dağınıklık test kırar, düşürülürse dosya elle
    güncellenir)."""
    assert len(ust_sayfalar()) <= 7
    # Nav agaci sirasi (D-215):
    # 0 Ana Kontrol | 1 Gelir Kapısı | 2 Müşteriler | 3 Metrikler
    # 4 Proje | 5 Güvenlik Kapısı | 6 Sistem
    assert len(ust_sayfalar()) == 7


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
    """D-214 ratchet: sınır gizlemeyle değil BİRLEŞTİRMEYLE korunur (KAHİN:
    "ilgili ve alakalı olanları birleştirelim"). Sabit sayı yerine mevcut
    fiilî maksimum tavan olarak alınır — bir kök bu tavanı geçerse test
    kırılır (yeni dağınıklık); tavan düşürülürse test dosyası güncellenir.
    """
    TAVAN = 11  # D-214 itibarıyla en kalabalık kök (`sistem`) 11 çocuğa sahip.
    for anahtar in ust_sayfalar():
        assert len(alt_sekmeler(anahtar)) <= TAVAN, anahtar


def test_d214_kok_cocuk_ayni_renderer_yasak() -> None:
    """D-214: bir kök ile kendi çocuklarından biri aynı (modul, fonksiyon)
    ikilisini render edemez — ikiz sekme (D-211) kökler için de geçerli."""
    kokler = {t.anahtar: t for t in SECTIONS if t.ust is None}
    for tanim in SECTIONS:
        if tanim.ust and tanim.ust in kokler:
            kok = kokler[tanim.ust]
            ikiz = (kok.modul, kok.fonksiyon) == (tanim.modul, tanim.fonksiyon)
            assert not ikiz, f"{tanim.ust} == {tanim.anahtar} (aynı renderer)"


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
    assert tab_getir("hatalar").baslik == "Olaylar & Hatalar"
    assert tab_getir("hatalar").ust == "sistem"
    assert tab_getir("teknik_altyapi").baslik == "Altyapı"


if __name__ == "__main__":  # elle çalıştırma: python tests/test_tabs_ia.py
    for ad, fn in sorted(globals().items()):
        if ad.startswith("test_") and callable(fn):
            fn()
            print("OK", ad)
