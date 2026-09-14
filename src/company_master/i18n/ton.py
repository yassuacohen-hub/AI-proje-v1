# -*- coding: utf-8 -*-
"""Ton sistemi — marka sesinin duygusal rengi ve ikon eşlemesi.

Ton, bir mesajın **ne hissettirdiğini** tanımlar; katman (`veri` / `cerceve`)
ise mesajın **hangi dille** yazıldığını tanımlar. İkisi diktir:

- `veri` katmanındaki bir hata mesajı da `danger` tonundadır (ama mitolojisiz).
- `cerceve` katmanındaki bir karşılama da `info` tonundadır (ve anlatısaldır).

Bu modül UI bileşenlerine bağımlı değildir; yalnızca `company_master.ui.base`
içindeki semantik varyant kümesiyle **sözleşme** kurar.
"""

from __future__ import annotations

from typing import Final

#: Marka sesinde izin verilen tonlar (MRK planı, Bölüm 2.2).
TONLAR: Final[tuple[str, ...]] = ("info", "success", "warning", "danger", "neutral")

#: Varsayılan ton — şemada `ton` verilmediğinde kullanılır.
VARSAYILAN_TON: Final[str] = "neutral"

#: Ton → UI bileşen varyantı (`company_master.ui.base.VARYANTLAR` alt kümesi).
#: `neutral` tonunun UI karşılığı `secondary`'dir; UI'da "neutral" varyantı yoktur.
TON_VARYANT: Final[dict[str, str]] = {
    "info": "info",
    "success": "success",
    "warning": "warning",
    "danger": "danger",
    "neutral": "secondary",
}

#: Ton → varsayılan Material Symbols ikonu (kayıtta `ikon` yoksa bu kullanılır).
TON_IKON: Final[dict[str, str]] = {
    "info": "info",
    "success": "check_circle",
    "warning": "warning",
    "danger": "error",
    "neutral": "circle",
}

#: Ton → Streamlit bildirim fonksiyonu adı (st.info / st.success / ...).
TON_STREAMLIT: Final[dict[str, str]] = {
    "info": "info",
    "success": "success",
    "warning": "warning",
    "danger": "error",
    "neutral": "info",
}


class TonHatasi(ValueError):
    """Bilinmeyen bir ton kullanıldığında fırlatılır."""


def ton_dogrula(ton: str) -> str:
    """Tonu doğrular; geçersizse açık hata verir.

    Sessizce `neutral`'a düşmez — bozuk ton, bozuk mesaj demektir ve
    bekçi testinde yakalanmalıdır.
    """
    if ton not in TONLAR:
        raise TonHatasi(f"Gecersiz ton: {ton!r}. Izinli: {', '.join(TONLAR)}")
    return ton


def ton_varyant(ton: str) -> str:
    """Tonu UI bileşen varyantına çevirir (`Badge`, `Button`, `Card` için)."""
    return TON_VARYANT[ton_dogrula(ton)]


def ton_ikon(ton: str) -> str:
    """Tonun varsayılan Material Symbols ikon adını verir."""
    return TON_IKON[ton_dogrula(ton)]


def ton_streamlit(ton: str) -> str:
    """Tonu `st.<fn>` bildirim fonksiyonu adına çevirir."""
    return TON_STREAMLIT[ton_dogrula(ton)]
