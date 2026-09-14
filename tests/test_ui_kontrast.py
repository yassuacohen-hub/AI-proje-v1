# -*- coding: utf-8 -*-
"""ADMIN-UI-11: Erişilebilirlik bekçisi — kontrast + responsive.

Bu dosya iki ayrı sözleşmeyi korur:

1. **Kontrast (WCAG 2.1 AA).** Tasarım token'larındaki metin/zemin
   kombinasyonlarının **her iki temada da** eşiği geçtiğini doğrular.
   Ölçüm doğrudan ``tema_tokenlari()`` üzerinden yapılır; yani biri
   ``tokens.py``'de bir rengi değiştirirse test anında kırılır.

2. **Responsive.** ``styles.py`` içindeki küçük ekran kurallarının
   silinmediğini denetler. CSS'i "temizlerken" media query blokları
   sessizce düşerse admin paneli mobilde okunmaz hâle gelir.

Eşikler (WCAG 2.1):
    * Gövde metni / ikon+metin karışımı ....... 4.5:1  (1.4.3 Contrast Minimum)
    * Etkileşimli bileşen sınırı .............. 3.0:1  (1.4.11 Non-text Contrast)

Neden `border` denetlenmiyor?
    `border` ve `border-strong` bilinçli olarak **dekoratif ayraçlardır**
    (kart kenarı, tablo çizgisi). WCAG bunları kapsam dışı bırakır. Form
    kontrolü veya etkileşimli bileşen çizerken `border-interactive`
    kullanılmalıdır — denetlenen token odur.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

from company_master.ui.styles import bilesen_css
from company_master.ui.tokens import TEMALAR, tema_tokenlari, token_adi

# ---------------------------------------------------------------- WCAG ölçüm

#: WCAG AA gövde metni eşiği.
ESIK_METIN: float = 4.5

#: WCAG AA metin dışı (sınır, ikon) eşiği.
ESIK_NESNE: float = 3.0


def _kanal(deger: float) -> float:
    """Tek bir sRGB kanalını doğrusal ışık uzayına çevirir."""
    return deger / 12.92 if deger <= 0.03928 else ((deger + 0.055) / 1.055) ** 2.4


def luminans(hex_renk: str) -> float:
    """Bir hex rengin WCAG bağıl parlaklığını (relative luminance) verir."""
    ham = hex_renk.strip().lstrip("#")
    if len(ham) == 3:
        ham = "".join(k * 2 for k in ham)
    if len(ham) != 6:
        raise ValueError(f"Hex renk bekleniyordu: {hex_renk!r}")
    r, g, b = (int(ham[i : i + 2], 16) / 255 for i in (0, 2, 4))
    return 0.2126 * _kanal(r) + 0.7152 * _kanal(g) + 0.0722 * _kanal(b)


def oran(on: str, arka: str) -> float:
    """İki renk arasındaki WCAG kontrast oranı (1.0 – 21.0)."""
    a, b = luminans(on), luminans(arka)
    ust, alt = max(a, b), min(a, b)
    return (ust + 0.05) / (alt + 0.05)


def _renk(tema: str, ad: str) -> str:
    """Tema içindeki bir renk token'ının gerçek değerini okur."""
    tokenlar = tema_tokenlari(tema)
    anahtar = token_adi("color", ad)
    if anahtar not in tokenlar:
        raise AssertionError(f"'{ad}' rengi '{tema}' temasında tanımlı değil.")
    return tokenlar[anahtar]


# ------------------------------------------------------------ ölçüm doğruluğu


def test_luminans_uc_degerler() -> None:
    """Siyah/beyaz referansları — formülün doğru kurulduğunu kanıtlar."""
    assert luminans("#000000") == pytest.approx(0.0, abs=1e-9)
    assert luminans("#ffffff") == pytest.approx(1.0, abs=1e-9)


def test_siyah_beyaz_orani_21() -> None:
    """WCAG'in tanımladığı maksimum oran 21:1'dir."""
    assert oran("#000000", "#ffffff") == pytest.approx(21.0, abs=0.01)


def test_ayni_renk_orani_bir() -> None:
    assert oran("#6366f1", "#6366f1") == pytest.approx(1.0, abs=1e-9)


def test_kisa_hex_desteklenir() -> None:
    assert luminans("#fff") == pytest.approx(luminans("#ffffff"))


# --------------------------------------------------------------- metin çiftleri

#: (ön plan token'ı, arka plan token'ı) — yüzey üzerinde okunacak metinler.
METIN_CIFTLERI: tuple[tuple[str, str], ...] = (
    # Gövde ve yardımcı metin
    ("text", "bg"),
    ("text", "surface"),
    ("text", "surface-2"),
    ("text", "surface-3"),
    ("text-muted", "bg"),
    ("text-muted", "surface"),
    ("text-muted", "surface-2"),
    # Semantik metin türevleri (ADMIN-UI-11'de eklendi)
    ("primary-text", "surface"),
    ("success-text", "surface"),
    ("warning-text", "surface"),
    ("danger-text", "surface"),
    ("info-text", "surface"),
    ("metric-customer-text", "surface"),
    ("metric-system-text", "surface"),
)

#: (ön plan token'ı, dolgu token'ı) — dolgu butonların üstündeki metin.
DOLGU_CIFTLERI: tuple[tuple[str, str], ...] = (
    ("on-primary", "primary-solid"),
    ("on-primary", "primary-solid-hover"),
    ("on-primary", "primary-solid-active"),
    ("on-success", "success"),
    ("on-warning", "warning"),
    ("on-danger", "danger"),
    ("on-info", "info"),
)

#: (sınır token'ı, zemin token'ı) — etkileşimli bileşen sınırı.
SINIR_CIFTLERI: tuple[tuple[str, str], ...] = (
    ("border-interactive", "bg"),
    ("border-interactive", "surface"),
)


def _kimlik(veri: object) -> str:
    if isinstance(veri, tuple):
        return f"{veri[0]}~{veri[1]}"
    return str(veri)


@pytest.mark.parametrize("tema", sorted(TEMALAR))
@pytest.mark.parametrize("cift", METIN_CIFTLERI, ids=_kimlik)
def test_metin_kontrasti_aa(tema: str, cift: tuple[str, str]) -> None:
    """Yüzey üzerindeki metin her iki temada da >= 4.5:1 olmalı."""
    on, arka = cift
    deger = oran(_renk(tema, on), _renk(tema, arka))
    assert deger >= ESIK_METIN, (
        f"[{tema}] {on} / {arka} = {deger:.2f}:1 (gereken >= {ESIK_METIN}). "
        "Dolgu tonunu metin olarak kullanmayin; '*-text' turevini secin."
    )


@pytest.mark.parametrize("tema", sorted(TEMALAR))
@pytest.mark.parametrize("cift", DOLGU_CIFTLERI, ids=_kimlik)
def test_dolgu_uzeri_metin_kontrasti_aa(tema: str, cift: tuple[str, str]) -> None:
    """Dolgu buton/rozet üzerindeki metin >= 4.5:1 olmalı."""
    on, arka = cift
    deger = oran(_renk(tema, on), _renk(tema, arka))
    assert deger >= ESIK_METIN, (
        f"[{tema}] {on} / {arka} = {deger:.2f}:1 (gereken >= {ESIK_METIN}). "
        "Dolgu uzerinde 'text-inverse' degil 'on-*' token'i kullanilmali."
    )


@pytest.mark.parametrize("tema", sorted(TEMALAR))
@pytest.mark.parametrize("cift", SINIR_CIFTLERI, ids=_kimlik)
def test_etkilesimli_sinir_kontrasti(tema: str, cift: tuple[str, str]) -> None:
    """Form kontrolü sınırı >= 3:1 olmalı (WCAG 1.4.11)."""
    on, arka = cift
    deger = oran(_renk(tema, on), _renk(tema, arka))
    assert deger >= ESIK_NESNE, (
        f"[{tema}] {on} / {arka} = {deger:.2f}:1 (gereken >= {ESIK_NESNE})."
    )


@pytest.mark.parametrize("tema", sorted(TEMALAR))
def test_dolgu_renkleri_tema_bagimsiz(tema: str) -> None:
    """`on-*` token'ları tema bağımsızdır — dolgu rengi de öyle olduğu için.

    Biri aydınlık temada dolgu rengini override ederse `on-*` eşleşmesi
    bozulur ve buton okunmaz hâle gelir; bu test o kaymayı yakalar.
    """
    karanlik = tema_tokenlari("karanlik")
    hedef = tema_tokenlari(tema)
    for ad in ("primary-solid", "success", "warning", "danger", "info"):
        anahtar = token_adi("color", ad)
        assert hedef[anahtar] == karanlik[anahtar], (
            f"'{ad}' dolgu rengi '{tema}' temasinda degistirilmis. "
            "Dolguyu degistirirseniz ilgili 'on-*' token'ini da yeniden olcun."
        )


def test_text_inverse_dolgu_butonlarda_kullanilmaz() -> None:
    """Regresyon bekçisi: dolgu buton kuralları `text-inverse`'e dönmemeli."""
    css = bilesen_css()
    for kural in re.findall(r"\.hg-btn-(?:primary|success|warning|danger|info)\{[^}]*\}", css):
        assert "text-inverse" not in kural, (
            f"Dolgu butonda 'text-inverse' geri gelmis: {kural}"
        )


# ------------------------------------------------------------------ responsive

KAYNAK = Path(__file__).resolve().parents[1] / "src" / "company_master" / "ui" / "styles.py"

#: Küçük ekranda mutlaka uyarlanması gereken bileşenler.
RESPONSIVE_SECICILER: tuple[str, ...] = (
    ".hg-actions",
    ".hg-page-head",
    ".hg-page-title",
    ".hg-page-actions",
    ".hg-nav-vertical",
    ".hg-topbar",
    ".hg-chat-panel",
)


def _media_bloklari() -> list[str]:
    """`styles.py` içindeki tüm `@media` blok gövdelerini çıkarır."""
    css = bilesen_css()
    bloklar: list[str] = []
    for eslesme in re.finditer(r"@media[^{]*\{", css):
        bas = eslesme.end()
        derinlik = 1
        imlec = bas
        while imlec < len(css) and derinlik:
            if css[imlec] == "{":
                derinlik += 1
            elif css[imlec] == "}":
                derinlik -= 1
            imlec += 1
        bloklar.append(css[bas : imlec - 1])
    return bloklar


def test_media_blogu_var() -> None:
    """Responsive katman tamamen silinmiş olmamalı."""
    assert _media_bloklari(), "styles.py icinde hic @media blogu yok."


@pytest.mark.parametrize("secici", RESPONSIVE_SECICILER)
def test_kucuk_ekran_kurali_var(secici: str) -> None:
    """Her kritik bileşenin en az bir media query karşılığı olmalı."""
    govde = "\n".join(_media_bloklari())
    assert secici in govde, (
        f"'{secici}' icin kucuk ekran kurali yok; mobilde tasma/okunmazlik riski."
    )


def test_reduced_motion_destegi() -> None:
    """Hareket hassasiyeti olan kullanıcılar için geçişler kapatılmalı."""
    css = bilesen_css()
    assert "prefers-reduced-motion" in css
    assert "transition:none" in css


def test_media_query_kaynakta_korunuyor() -> None:
    """Dosya düzeyinde de doğrula (blok bir daldan düşerse yakalanır)."""
    metin = KAYNAK.read_text(encoding="utf-8")
    assert metin.count("@media") >= 5, (
        "styles.py'deki media query sayisi beklenenden az; responsive kurallar silinmis olabilir."
    )
