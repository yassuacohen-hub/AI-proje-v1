# -*- coding: utf-8 -*-
"""UX-01: Tasarım token'ları (renk, boşluk, tipografi, yarıçap, gölge).

Bu modül bileşen kütüphanesinin **tek doğru kaynağıdır** (SSOT). Bileşenler
hiçbir yerde ham hex kodu yazmaz; hepsi buradaki CSS değişkenlerine bağlanır.

Yüzey/arkaplan renkleri `.streamlit/config.toml` içindeki koyu tema ile
hizalıdır (``backgroundColor #0a0e17``, ``secondaryBackground #131826``,
``textColor #e2e8f0``); marka/accent rengi ise
`docs/UX_ADMIN_PANEL_REVIEW_2026-09-14.md` denetiminde istenen Indigo
paletine (``#6366F1``) güncellenmiştir.

Not: Tam tema yönetimi (dark/light geçişi) UX-03 kapsamındadır; burada
yalnızca token sözlüğü ve `:root` CSS üretimi bulunur.
"""
from __future__ import annotations

from typing import Final

#: Marka ve durum renkleri.
#:
#: Palet, `docs/UX_ADMIN_PANEL_REVIEW_2026-09-14.md` (Copilot UX denetimi)
#: sözleşmesiyle hizalıdır: accent Indigo ``#6366F1``, success ``#22C55E``,
#: warning ``#F59E0B``, danger ``#EF4444``. ``accent*`` anahtarları
#: ``primary*`` ile aynı değeri taşıyan **semantik takma adlardır**; admin
#: paneli token'ları (`admin_tokens.css`) bu adlandırmaya bağlanır.
RENKLER: Final[dict[str, str]] = {
    # Marka (Indigo — premium enterprise referansı)
    "primary": "#6366f1",
    "primary-hover": "#4f46e5",
    "primary-active": "#4338ca",
    "primary-soft": "rgba(99, 102, 241, 0.15)",
    # Semantik takma ad (Copilot raporu: --color-accent)
    "accent": "#6366f1",
    "accent-hover": "#4f46e5",
    "accent-soft": "rgba(99, 102, 241, 0.15)",
    # Yüzeyler
    "bg": "#0a0e17",
    "surface": "#131826",
    "surface-2": "#1b2233",
    # Etkileşim yüzeyi (hover/active) — surface-2'nin bir tık üstü
    "surface-3": "#242c40",
    "border": "#2a3348",
    "border-strong": "#3b465e",
    # ADMIN-UI-11: Etkileşimli bileşen sınırı (girdi, seçim, odak halkası
    # taşıyıcısı). WCAG 1.4.11 "Non-text Contrast" gereği yüzeye karşı >= 3:1
    # olmalı. `border` / `border-strong` yalnız **dekoratif** ayraçlardır ve
    # bilinçli olarak düşük kontrastlıdır; form kontrolü çizerken bunları
    # kullanmayın.
    "border-interactive": "#5a6880",
    # Metin
    "text": "#e2e8f0",
    "text-muted": "#94a3b8",
    "text-inverse": "#0a0e17",
    # Durum (semantik) — DOLGU rengi. Metin olarak kullanmayın; `*-text`
    # türevini kullanın (aşağıya bakın).
    "success": "#22c55e",
    "success-soft": "rgba(34, 197, 94, 0.15)",
    "warning": "#f59e0b",
    "warning-soft": "rgba(245, 158, 11, 0.15)",
    "danger": "#ef4444",
    "danger-soft": "rgba(239, 68, 68, 0.15)",
    "info": "#38bdf8",
    "info-soft": "rgba(56, 189, 248, 0.15)",
    # DASH-UX-01 kategori renkleri (mavi müşteri / turuncu sistem)
    "metric-customer": "#3b82f6",
    "metric-system": "#f97316",
    # --- ADMIN-UI-11: Erişilebilir METİN türevleri ---
    #
    # Marka/durum renkleri **dolgu** için tasarlanmıştır; aynı tonu yüzey
    # üzerinde metin veya ikon olarak kullanmak WCAG AA'yı (4.5:1) düşürür.
    # Ölçüm: `#6366f1` / `#131826` = 3.96:1 (kalır), `#818cf8` = 5.93:1 (geçer).
    #
    # Sahip kuralı "mevcut renkleri yeniden icat etme" korunur: bunlar yeni
    # renk değil, **aynı ailenin** bir tık açık tonlarıdır (500 -> 400) ve
    # yalnız metin/ikon rolünde devreye girer. Aydınlık temada tersine
    # koyulaşır (bkz. RENKLER_AYDINLIK).
    "primary-text": "#818cf8",
    "success-text": "#4ade80",
    "warning-text": "#fbbf24",
    "danger-text": "#f87171",
    "info-text": "#7dd3fc",
    "metric-customer-text": "#60a5fa",
    "metric-system-text": "#fb923c",
    # --- ADMIN-UI-11: Dolgu üzerindeki metin ("on-*") ---
    #
    # Dolgu rengi iki temada da aynı olduğu için bu token'lar da **tema
    # bağımsızdır**; `text-inverse` kullanmak aydınlık temada beyaz-üstü-sarı
    # gibi 2.15:1 kombinasyonlar üretiyordu (gerçek hata, ADIM 11'de bulundu).
    #
    # `primary` (#6366f1) üzerinde beyaz yalnız 4.47:1 verdiği için dolgu
    # tonu bilinçli olarak bir kademe koyu seçildi: `primary-solid`.
    "primary-solid": "#4f46e5",          # dolgu (beyaz metinle 6.29:1)
    "primary-solid-hover": "#4338ca",    # 7.90:1
    "primary-solid-active": "#3730a3",   # 9.93:1
    "on-primary": "#ffffff",
    "on-success": "#0a0e17",             # 8.47:1
    "on-warning": "#0a0e17",             # 8.99:1
    "on-danger": "#0a0e17",              # 5.13:1
    "on-info": "#0a0e17",                # 9.01:1
}

#: 4px tabanlı boşluk ölçeği.
BOSLUKLAR: Final[dict[str, str]] = {
    "0": "0",
    "1": "4px",
    "2": "8px",
    "3": "12px",
    "4": "16px",
    "5": "24px",
    "6": "32px",
    "7": "48px",
}

#: Köşe yarıçapları.
#:
#: Copilot UX denetimi bandı: buton 8-10px, kart 12-16px, modal/drawer 16-20px.
#: ``button``/``card``/``modal`` anahtarları bileşenlerin bağlandığı
#: **semantik** yarıçaplardır; ölçek anahtarları (sm/md/lg/xl) ham değerdir.
YARICAPLAR: Final[dict[str, str]] = {
    "sm": "4px",
    "md": "8px",
    "lg": "12px",
    "xl": "16px",
    "full": "9999px",
    # Semantik
    "button": "8px",
    "card": "12px",
    "modal": "16px",
}

#: Tipografi ölçeği.
#:
#: İki katman vardır:
#:
#: * **Ölçek anahtarları** (``size-xs`` … ``size-2xl``) — ham değerler.
#:   Mevcut bileşenler bunlara bağlıdır, geriye dönük uyum için korunur.
#: * **Semantik roller** (``size-h1``, ``size-body``, ``size-label`` …) —
#:   sayfa hiyerarşisinin tek kaynağı. Yeni ekranlar **yalnız** bunları
#:   kullanır; böylece "her sayfada farklı punto" sorunu tekrar doğmaz.
#:
#: Rol → ölçek eşlemesi bilinçlidir: ``size-body`` ile ``size-md`` aynı
#: değeri taşır; rol adı değişmeden ölçek ayarlanabilsin diye ayrı yazılır.
TIPOGRAFI: Final[dict[str, str]] = {
    "font-family": (
        "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', "
        "Roboto, 'Helvetica Neue', Arial, sans-serif"
    ),
    "font-mono": "'JetBrains Mono', 'SF Mono', Consolas, monospace",
    # --- Ölçek (ham) ---
    "size-xs": "11px",
    "size-sm": "13px",
    "size-md": "14px",
    "size-lg": "16px",
    "size-xl": "20px",
    "size-2xl": "26px",
    "size-3xl": "32px",
    # --- Semantik roller (sayfa hiyerarşisi) ---
    "size-h1": "32px",      # sayfa başlığı — ekranda yalnız bir tane
    "size-h2": "22px",      # ana bölüm
    "size-h3": "17px",      # alt bölüm
    "size-body": "14px",    # gövde metni
    "size-lead": "16px",    # H1 altındaki giriş paragrafı
    "size-label": "12px",   # form etiketi / üst etiket
    "size-help": "12px",    # yardımcı metin, dipnot
    # --- Ağırlık (ince ↔ kalın kontrastı) ---
    "weight-normal": "400",
    "weight-medium": "500",
    "weight-semibold": "600",
    "weight-bold": "700",
    # --- Satır yüksekliği ---
    "line-tight": "1.25",   # başlıklar
    "line-normal": "1.5",   # gövde
    "line-relaxed": "1.7",  # uzun paragraf
    # --- Harf aralığı (büyük puntoda sıkı, küçük büyük harfte geniş) ---
    "tracking-tight": "-0.02em",
    "tracking-wide": "0.06em",
}

#: Gölgeler ve katman sırası.
GOLGELER: Final[dict[str, str]] = {
    "sm": "0 1px 2px rgba(0, 0, 0, 0.35)",
    "md": "0 4px 12px rgba(0, 0, 0, 0.35)",
    "lg": "0 12px 32px rgba(0, 0, 0, 0.45)",
    "focus": "0 0 0 3px rgba(99, 102, 241, 0.45)",
}

#: z-index katmanları (modal/tooltip çakışmasını önler).
KATMANLAR: Final[dict[str, str]] = {
    "base": "1",
    "dropdown": "1000",
    "tooltip": "1100",
    "modal-backdrop": "1200",
    "modal": "1201",
}

#: Geçiş süreleri.
GECISLER: Final[dict[str, str]] = {
    "fast": "120ms ease",
    "normal": "200ms ease",
}

#: Aydınlık tema **farkları** (UX-03 / gece-gündüz düğmesi).
#:
#: Yalnız yüzey ve metin token'ları değişir. Marka ve durum renkleri
#: (``primary``, ``success``, ``warning``, ``danger``, ``info``) iki temada
#: da **aynıdır** — sahip talimatı: "mevcut renkleri yeniden icat etme".
#: Burada olmayan her anahtar `RENKLER`'den miras alınır.
RENKLER_AYDINLIK: Final[dict[str, str]] = {
    # Yüzeyler
    "bg": "#f6f7fb",
    "surface": "#ffffff",
    "surface-2": "#f1f3f9",
    "surface-3": "#e6eaf3",
    "border": "#e2e6f0",
    "border-strong": "#c7cdda",
    # ADMIN-UI-11: etkileşimli sınır — WCAG 1.4.11 (>= 3:1).
    # Ölçüt saf beyaz değil, sayfa zemini `bg` (#f6f7fb): #8b93a7 orada 2.87:1
    # kalıyordu. #7e869b ile bg'ye karşı 3.40:1, kart yüzeyine karşı 3.64:1.
    "border-interactive": "#7e869b",
    # Metin — WCAG AA hedefi (#1e293b / #f6f7fb ≈ 13.4:1)
    "text": "#1e293b",
    "text-muted": "#5b6478",
    "text-inverse": "#ffffff",
    # --- ADMIN-UI-11: Erişilebilir metin türevleri (aydınlıkta koyulaşır) ---
    #
    # Karanlıkta 400 tonu okunur, aydınlıkta okunmaz: `#4ade80` beyaz üstünde
    # yalnız 1.7:1'dir. Bu yüzden aynı ailenin 700 tonuna inilir; dolgu
    # renkleri (`success`, `warning` …) değişmeden kalır.
    "primary-text": "#4338ca",           # 7.90:1
    "success-text": "#15803d",           # 5.02:1
    "warning-text": "#b45309",           # 5.02:1
    "danger-text": "#b91c1c",            # 6.47:1
    "info-text": "#0369a1",              # 5.93:1
    "metric-customer-text": "#1d4ed8",   # 6.70:1
    "metric-system-text": "#c2410c",     # 5.18:1
    # Gölgeler aydınlıkta daha yumuşak olmalı (aşağıda GOLGELER_AYDINLIK)
}

#: Aydınlık temada gölge farkları — koyu gölge beyaz zeminde kirli görünür.
GOLGELER_AYDINLIK: Final[dict[str, str]] = {
    "sm": "0 1px 2px rgba(15, 23, 42, 0.06)",
    "md": "0 4px 12px rgba(15, 23, 42, 0.08)",
    "lg": "0 12px 32px rgba(15, 23, 42, 0.12)",
}

#: Geçerli tema adları.
TEMALAR: Final[tuple[str, ...]] = ("karanlik", "aydinlik")

#: CSS değişken ön eki — proje dışı stillerle çakışmayı önler.
ONEK: Final[str] = "hg"

_GRUPLAR: Final[tuple[tuple[str, dict[str, str]], ...]] = (
    ("color", RENKLER),
    ("space", BOSLUKLAR),
    ("radius", YARICAPLAR),
    ("font", TIPOGRAFI),
    ("shadow", GOLGELER),
    ("z", KATMANLAR),
    ("transition", GECISLER),
)


def token_adi(grup: str, anahtar: str) -> str:
    """Bir token için CSS değişken adını döndürür (``--hg-color-primary``)."""
    return f"--{ONEK}-{grup}-{anahtar}"


def token(grup: str, anahtar: str) -> str:
    """Bir token'ın ``var(...)`` referansını döndürür.

    Bileşenler ham renk yerine bunu kullanır; böylece tema değişince
    (UX-03) tüm kütüphane tek noktadan güncellenir.
    """
    return f"var({token_adi(grup, anahtar)})"


def tum_tokenlar() -> dict[str, str]:
    """Tüm token'ları ``{css_degisken_adi: deger}`` olarak düz sözlüğe indirger."""
    duz: dict[str, str] = {}
    for grup, sozluk in _GRUPLAR:
        for anahtar, deger in sozluk.items():
            duz[token_adi(grup, anahtar)] = deger
    return duz


def tema_tokenlari(tema: str = "karanlik") -> dict[str, str]:
    """Bir temanın **tam** token setini döndürür.

    Aydınlık tema, karanlık setin üzerine yalnız yüzey/metin/gölge
    farklarını bindirir; marka ve durum renkleri ortak kalır.

    Args:
        tema: ``"karanlik"`` veya ``"aydinlik"``.

    Raises:
        ValueError: Bilinmeyen tema adı verilirse.
    """
    if tema not in TEMALAR:
        raise ValueError(f"Bilinmeyen tema: {tema!r}. Geçerli: {TEMALAR}")
    duz = tum_tokenlar()
    if tema == "aydinlik":
        for anahtar, deger in RENKLER_AYDINLIK.items():
            duz[token_adi("color", anahtar)] = deger
        for anahtar, deger in GOLGELER_AYDINLIK.items():
            duz[token_adi("shadow", anahtar)] = deger
    return duz


def kok_css(secici: str = ":root", tema: str = "karanlik") -> str:
    """Token'ları CSS özel değişkenleri olarak yazar.

    Args:
        secici: Değişkenlerin tanımlanacağı seçici (varsayılan ``:root``).
        tema: Yazılacak tema (``"karanlik"`` / ``"aydinlik"``).
    """
    satirlar = [f"  {ad}: {deger};" for ad, deger in tema_tokenlari(tema).items()]
    return secici + " {\n" + "\n".join(satirlar) + "\n}"
