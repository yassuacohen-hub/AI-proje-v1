# -*- coding: utf-8 -*-
"""UX-01: Badge (rozet) bileşeni.

Durum etiketleri için kullanılır: "aktif", "review", "done", "blocked" gibi
görev panosu durumları ya da kalite skoru seviyeleri.
"""
from __future__ import annotations

from company_master.ui.base import (
    Bilesen,
    BilesenHatasi,
    boyut_dogrula,
    etiket,
    guvenli_metin,
    sinif,
    sinif_listesi,
    varyant_dogrula,
)

#: Görev panosu durumlarının rozet varyant eşlemesi (orkestratör ile hizalı).
DURUM_VARYANT: dict[str, str] = {
    "plan": "secondary",
    "bekliyor": "secondary",
    "aktif": "info",
    "review": "warning",
    "done": "success",
    "blocked": "danger",
}


class Badge(Bilesen):
    """Küçük durum/etiket rozeti.

    Args:
        metin: Rozet metni (zorunlu).
        varyant: primary | secondary | success | warning | danger | info | ghost
        boyut: sm | md | lg
        nokta: True ise metnin soluna renkli durum noktası eklenir.
        yumusak: True ise dolgu yerine soft arka plan kullanılır (varsayılan).
    """

    def __init__(
        self,
        metin: str,
        *,
        varyant: str = "secondary",
        boyut: str = "sm",
        nokta: bool = False,
        yumusak: bool = True,
    ) -> None:
        if not str(metin).strip():
            raise BilesenHatasi("Badge metni boş olamaz")
        self.metin = str(metin)
        self.varyant = varyant_dogrula(varyant)
        self.boyut = boyut_dogrula(boyut)
        self.nokta = bool(nokta)
        self.yumusak = bool(yumusak)

    @classmethod
    def durumdan(cls, durum: str, **kwargs: object) -> "Badge":
        """Görev durumundan uygun renkte rozet üretir.

        Bilinmeyen durum `secondary` varyantına düşer (çökmez).
        """
        varyant = DURUM_VARYANT.get(str(durum).lower(), "secondary")
        return cls(str(durum), varyant=varyant, nokta=True, **kwargs)  # type: ignore[arg-type]

    def html(self) -> str:
        icerik = ""
        if self.nokta:
            icerik += etiket("span", "", **{"class": sinif("badge", "dot")})
        icerik += guvenli_metin(self.metin)
        siniflar = sinif_listesi(
            sinif("badge"),
            sinif("badge", self.varyant),
            sinif("badge", self.boyut),
            sinif("badge", "solid") if not self.yumusak else None,
        )
        return etiket("span", icerik, **{"class": siniflar})
