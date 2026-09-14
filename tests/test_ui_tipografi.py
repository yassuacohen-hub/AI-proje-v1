# -*- coding: utf-8 -*-
"""ADMIN-UI-12 — Tipografi ölçeği ve buton sistemi sözleşmesi.

Bu dosya iki sahip kuralını kod seviyesinde kilitler:

1. **Tipografi hiyerarşisi tutarlı olmalı.** Sayfa iskeleti (H1 → giriş →
   H2 → H3 → gövde) yalnızca punto farkıyla okunuyorsa, bu farkların
   monoton azalması zorunludur. Biri diğerine eşitlenirse hiyerarşi
   görsel olarak çöker ama hiçbir test uyarmaz — bu testler o boşluğu
   kapatır.

2. **Tek buton sistemi.** Ekran yazarı ham `varyant` seçmek zorunda
   kalmamalı; semantik `rol` kullanmalı. `ROLLER` sözlüğü kapalı bir
   kümedir ve her rol gerçek bir CSS varyantına çözülmelidir. Ayrıca
   "aynı ekranda tek birincil buton" kuralı `ButtonGroup` tarafından
   zorlanır; burada regresyona karşı korunur.

Not: Renk/kontrast sözleşmesi `tests/test_ui_kontrast.py` içindedir.
"""

from __future__ import annotations

import re

import pytest

from company_master.ui.base import VARYANTLAR
from company_master.ui.components.button import Button, ButtonGroup, ROLLER, rol_dogrula
from company_master.ui.styles import bilesen_css
from company_master.ui.tokens import TIPOGRAFI, token_adi

# ---------------------------------------------------------------------------
# Yardımcılar
# ---------------------------------------------------------------------------


def px(anahtar: str) -> int:
    """`TIPOGRAFI` içindeki px değerini tam sayıya çevirir."""
    ham = TIPOGRAFI[anahtar]
    eslesme = re.fullmatch(r"(\d+)px", ham.strip())
    if not eslesme:
        raise AssertionError(f"{anahtar!r} px cinsinden olmalı, bulunan: {ham!r}")
    return int(eslesme.group(1))


#: Sayfa iskeletinin görsel hiyerarşisi — büyükten küçüğe **kesin azalan**.
HIYERARSI: tuple[str, ...] = (
    "size-h1",
    "size-h2",
    "size-h3",
    "size-lead",
    "size-body",
    "size-label",
)

#: Ham ölçek de kendi içinde kesin artan olmalı.
OLCEK: tuple[str, ...] = (
    "size-xs",
    "size-sm",
    "size-md",
    "size-lg",
    "size-xl",
    "size-2xl",
    "size-3xl",
)

#: Semantik rollerin dayandığı ham ölçek basamakları.
AGIRLIKLAR: tuple[str, ...] = (
    "weight-normal",
    "weight-medium",
    "weight-semibold",
    "weight-bold",
)


# ---------------------------------------------------------------------------
# 1) Tipografi ölçeği
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "buyuk,kucuk",
    list(zip(HIYERARSI, HIYERARSI[1:])),
    ids=[f"{a}>{b}" for a, b in zip(HIYERARSI, HIYERARSI[1:])],
)
def test_hiyerarsi_kesin_azalir(buyuk: str, kucuk: str) -> None:
    """H1 > H2 > H3 > lead > body > label — eşitlik bile kabul edilmez."""
    assert px(buyuk) > px(kucuk), (
        f"{buyuk} ({px(buyuk)}px) <= {kucuk} ({px(kucuk)}px): "
        "başlık hiyerarşisi görsel olarak ayırt edilemez hale gelir."
    )


@pytest.mark.parametrize(
    "kucuk,buyuk",
    list(zip(OLCEK, OLCEK[1:])),
    ids=[f"{a}<{b}" for a, b in zip(OLCEK, OLCEK[1:])],
)
def test_ham_olcek_kesin_artar(kucuk: str, buyuk: str) -> None:
    """Ham ölçek basamakları (xs → 3xl) kesin artan olmalı."""
    assert px(kucuk) < px(buyuk), f"{kucuk} ({px(kucuk)}px) >= {buyuk} ({px(buyuk)}px)."


@pytest.mark.parametrize("anahtar", sorted(HIYERARSI + OLCEK))
def test_punto_okunabilir_alt_sinirda(anahtar: str) -> None:
    """Hiçbir punto 11px altına inmez (küçük ekranda okunabilirlik)."""
    assert px(anahtar) >= 11, f"{anahtar} = {px(anahtar)}px, alt sınır 11px."


def test_govde_punto_14px() -> None:
    """Gövde metni sözleşmesi: 14px. Değişirse bilinçli karar olmalı."""
    assert px("size-body") == 14


def test_h1_tek_ve_en_buyuk() -> None:
    """H1, tüm semantik roller arasında tek başına en büyük punto."""
    digerleri = [px(a) for a in HIYERARSI if a != "size-h1"]
    assert px("size-h1") > max(digerleri)


@pytest.mark.parametrize(
    "hafif,agir",
    list(zip(AGIRLIKLAR, AGIRLIKLAR[1:])),
    ids=[f"{a}<{b}" for a, b in zip(AGIRLIKLAR, AGIRLIKLAR[1:])],
)
def test_agirlik_olcegi_artar(hafif: str, agir: str) -> None:
    """Font ağırlıkları 400 → 700 yönünde kesin artmalı."""
    assert int(TIPOGRAFI[hafif]) < int(TIPOGRAFI[agir])


def test_satir_yuksekligi_siralamasi() -> None:
    """Başlık sıkı, gövde normal, uzun paragraf gevşek."""
    tight = float(TIPOGRAFI["line-tight"])
    normal = float(TIPOGRAFI["line-normal"])
    relaxed = float(TIPOGRAFI["line-relaxed"])
    assert tight < normal < relaxed


def test_tek_font_ailesi_kullanilir() -> None:
    """Sahip kuralı: font seçimlerini yeniden icat etme — Inter tek gövde ailesi."""
    assert "Inter" in TIPOGRAFI["font-family"]
    assert "sans-serif" in TIPOGRAFI["font-family"]


@pytest.mark.parametrize("anahtar", sorted(HIYERARSI))
def test_semantik_punto_css_de_kullanilir(anahtar: str) -> None:
    """Tanımlanan her semantik punto CSS'te gerçekten tüketilmeli (ölü token yok)."""
    css = bilesen_css()
    assert token_adi("font", anahtar) in css, (
        f"{anahtar} tanımlı ama hiçbir bileşen kullanmıyor — ölü token."
    )


def test_bilesen_css_hardcoded_punto_icermez() -> None:
    """Bileşen CSS'i ham `font-size: 13px` yazmamalı; token kullanmalı."""
    css = bilesen_css()
    kacaklar = re.findall(r"font-size:\s*(\d+)px", css)
    assert not kacaklar, (
        f"Bileşen CSS'inde token'sız punto bulundu: {sorted(set(kacaklar))}px. "
        "var(--hg-font-size-*) kullanın."
    )


# ---------------------------------------------------------------------------
# 2) Buton sistemi sözleşmesi
# ---------------------------------------------------------------------------


def test_rol_kumesi_kapali() -> None:
    """Roller kapalı küme: birincil/ikincil/tehlikeli/sessiz."""
    assert set(ROLLER) == {"birincil", "ikincil", "tehlikeli", "sessiz"}


@pytest.mark.parametrize("rol,varyant", sorted(ROLLER.items()))
def test_her_rol_gecerli_varyanta_cozulur(rol: str, varyant: str) -> None:
    """Her semantik rol, gerçek bir CSS varyantına karşılık gelmeli."""
    assert varyant in VARYANTLAR
    assert rol_dogrula(rol) == varyant


@pytest.mark.parametrize("rol,varyant", sorted(ROLLER.items()))
def test_rol_css_sinifi_uretilir(rol: str, varyant: str) -> None:
    """Rolün ürettiği sınıfın CSS karşılığı olmalı."""
    html = Button("Dene", rol=rol).html()
    assert f"hg-btn-{varyant}" in html
    assert f".hg-btn-{varyant}" in bilesen_css()


def test_gecersiz_rol_reddedilir() -> None:
    """Bilinmeyen rol sessizce varsayılana düşmemeli; hata vermeli."""
    with pytest.raises(Exception) as hata:
        Button("Dene", rol="ana")
    assert "ana" in str(hata.value)


def test_rol_varyanti_ezer() -> None:
    """Rol verildiğinde `varyant` argümanı yok sayılır (tek kaynak)."""
    buton = Button("Sil", rol="tehlikeli", varyant="success")
    assert buton.varyant == "danger"


def test_grup_tek_birincil_kurali() -> None:
    """Sahip kuralı: aynı ekranda tek birincil buton."""
    with pytest.raises(ValueError) as hata:
        ButtonGroup(
            [
                Button("Kaydet", rol="birincil"),
                Button("Çalıştır", rol="birincil"),
            ]
        )
    assert "birincil" in str(hata.value)


def test_grup_gecerli_kombinasyon() -> None:
    """Bir birincil + çok sayıda destek butonu serbest."""
    html = ButtonGroup(
        [
            Button("Kaydet", rol="birincil"),
            Button("Vazgeç", rol="ikincil"),
            Button("Sil", rol="tehlikeli"),
            Button("Yenile", rol="sessiz"),
        ]
    ).html()
    assert html.count("hg-btn-primary") == 1
    assert 'role="group"' in html


def test_grup_bos_liste_reddedilir() -> None:
    """Boş aksiyon kümesi anlamsız; sessizce boş div üretmemeli."""
    with pytest.raises(ValueError):
        ButtonGroup([])


def test_grup_sifir_birincil_serbest() -> None:
    """Bazı bölümlerde ana aksiyon olmayabilir; bu kural ihlali değildir."""
    html = ButtonGroup([Button("Yenile", rol="sessiz")]).html()
    assert "hg-btn-primary" not in html


@pytest.mark.parametrize("hizalama", sorted(ButtonGroup.HIZALAMALAR))
def test_grup_hizalama_sinifi(hizalama: str) -> None:
    """Her hizalama değerinin CSS karşılığı olmalı."""
    html = ButtonGroup([Button("Tamam", rol="ikincil")], hizalama=hizalama).html()
    assert f"hg-actions-{hizalama}" in html
    assert f".hg-actions-{hizalama}" in bilesen_css()


def test_yukleniyor_pasiflestirir() -> None:
    """Yükleme durumu çift tıklamayı engellemeli (loading = disabled)."""
    buton = Button("Çalıştır", rol="birincil", yukleniyor=True)
    assert buton.pasif is True
    assert "disabled" in buton.html()


def test_buton_odak_stili_tanimli() -> None:
    """Klavye erişimi: `:focus-visible` kuralı CSS'te bulunmalı."""
    css = bilesen_css()
    assert ".hg-btn:focus-visible" in css or ".hg-btn:focus" in css


def test_buton_pasif_stili_tanimli() -> None:
    """Pasif durumun görsel karşılığı olmalı."""
    assert ".hg-btn:disabled" in bilesen_css() or ".hg-btn[disabled]" in bilesen_css()
