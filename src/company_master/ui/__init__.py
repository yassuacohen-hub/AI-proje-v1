# -*- coding: utf-8 -*-
"""UX-01: Huginn UI bileşen kütüphanesi.

Tek giriş noktası. Örnek:

    from company_master.ui import Button, MetricCard, stil_enjekte

    stil_enjekte()                       # sayfa başında bir kez
    MetricCard("Toplam Firma", 8313,
               kategori="customer",
               aciklama="Veritabanındaki doğrulanmış firma sayısı",
               soru="Bu hafta kaç yeni firma eklendi?").render()

Tasarım ilkeleri:
  - Bileşenler **saf HTML string** üretir (`html()`); Streamlit bağımlılığı
    yalnızca `render()`/`streamlit()` içinde, yerel import ile.
  - Tüm kullanıcı verisi `guvenli_metin()` ile kaçışlanır (XSS koruması).
  - Hiçbir bileşende sabit renk yoktur; her şey `tokens.py` üzerinden.
  - CSS ön eki `hg-` — Streamlit ve mevcut `web_dashboard/css` ile çakışmaz.
"""
from __future__ import annotations

from company_master.ui.base import (
    BOYUTLAR,
    VARYANTLAR,
    Bilesen,
    BilesenHatasi,
    birlestir,
    boyut_dogrula,
    guvenli_metin,
    sinif,
    sinif_listesi,
    varyant_dogrula,
)
from company_master.ui.components import (
    DURUM_VARYANT,
    HIZALAMALAR,
    KATEGORILER,
    KONUMLAR,
    MODAL_BOYUTLARI,
    ROLLER,
    SOHBET_ROLLERI,
    TEMA_SUNUMU,
    TIPLER,
    Badge,
    Button,
    ButtonGroup,
    Card,
    ChatBubble,
    Dropdown,
    Input,
    MetricCard,
    Modal,
    PageHeader,
    Section,
    SectionNav,
    Table,
    ThemeToggle,
    Tooltip,
    TopBar,
    api_cagir,
    bos_durum,
    hata_kutusu,
    kimlik_uret,
    rol_dogrula,
    secenekleri_normalize,
    tema_dogrula,
    tema_karsiti,
    yukleniyor,
)
from company_master.ui.styles import (
    bilesen_css,
    stil_enjekte,
    stil_etiketi,
    tum_css,
)
from company_master.ui.tokens import (
    BOSLUKLAR,
    GECISLER,
    GOLGELER,
    GOLGELER_AYDINLIK,
    KATMANLAR,
    ONEK,
    RENKLER,
    RENKLER_AYDINLIK,
    TEMALAR,
    TIPOGRAFI,
    YARICAPLAR,
    kok_css,
    tema_tokenlari,
    token,
    token_adi,
    tum_tokenlar,
)

__all__ = [
    # Bileşenler
    "Badge",
    "Button",
    "ButtonGroup",
    "Card",
    "ChatBubble",
    "Dropdown",
    "Input",
    "MetricCard",
    "Modal",
    "PageHeader",
    "Section",
    "SectionNav",
    "Table",
    "ThemeToggle",
    "Tooltip",
    "TopBar",
    # Durum bileşenleri (ADMIN-ROO-01)
    "api_cagir",
    "bos_durum",
    "hata_kutusu",
    "yukleniyor",
    # Temel altyapı
    "Bilesen",
    "BilesenHatasi",
    "birlestir",
    "boyut_dogrula",
    "guvenli_metin",
    "sinif",
    "sinif_listesi",
    "varyant_dogrula",
    # Stil
    "bilesen_css",
    "stil_enjekte",
    "stil_etiketi",
    "tum_css",
    # Token
    "kok_css",
    "tema_tokenlari",
    "token",
    "token_adi",
    "tum_tokenlar",
    # Sabitler
    "BOSLUKLAR",
    "BOYUTLAR",
    "DURUM_VARYANT",
    "GECISLER",
    "GOLGELER",
    "GOLGELER_AYDINLIK",
    "HIZALAMALAR",
    "KATEGORILER",
    "KATMANLAR",
    "KONUMLAR",
    "MODAL_BOYUTLARI",
    "ONEK",
    "RENKLER",
    "RENKLER_AYDINLIK",
    "ROLLER",
    "SOHBET_ROLLERI",
    "TEMA_SUNUMU",
    "TEMALAR",
    "TIPLER",
    "TIPOGRAFI",
    "VARYANTLAR",
    "YARICAPLAR",
    "kimlik_uret",
    "rol_dogrula",
    "secenekleri_normalize",
    "tema_dogrula",
    "tema_karsiti",
]
