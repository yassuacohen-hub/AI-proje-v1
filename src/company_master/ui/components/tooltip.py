# -*- coding: utf-8 -*-
"""UX-01: Tooltip (ipucu) bileşeni.

Saf CSS ile çalışır — JavaScript gerektirmez. Sarmalanan içeriğin üzerine
gelindiğinde veya klavyeyle odaklanıldığında ipucu görünür.

Erişilebilirlik:
  - İpucu metni `role="tooltip"` ve kendi `id`'siyle yazılır.
  - Tetikleyici `aria-describedby` ile bu id'ye bağlanır.
  - `tabindex="0"` sayesinde klavye kullanıcıları da ipucunu görebilir.
"""
from __future__ import annotations

import itertools
from typing import Any

from company_master.ui.base import (
    Bilesen,
    BilesenHatasi,
    guvenli_metin,
    sinif,
    sinif_listesi,
)

#: İpucunun tetikleyiciye göre konumu.
KONUMLAR: tuple[str, ...] = ("top", "bottom", "left", "right")

_sayac = itertools.count(1)


class Tooltip(Bilesen):
    """Bir içeriği ipucu ile sarmalar.

    Parametreler
    ------------
    icerik:
        Tetikleyici içerik (metin ya da `html()` üreten bir bileşen).
    metin:
        İpucu metni (zorunlu).
    konum:
        `top` | `bottom` | `left` | `right`.
    ham_html:
        `icerik` string ise kaçışlamadan gömer.
    genis:
        Uzun açıklamalar için daha geniş kutu.
    tooltip_id:
        DOM kimliği; verilmezse otomatik üretilir.
    """

    def __init__(
        self,
        icerik: Any,
        metin: str,
        *,
        konum: str = "top",
        ham_html: bool = False,
        genis: bool = False,
        tooltip_id: str = "",
    ) -> None:
        if not metin or not metin.strip():
            raise BilesenHatasi("Tooltip metni boş olamaz")
        if konum not in KONUMLAR:
            raise BilesenHatasi(
                f"Geçersiz konum: {konum!r}. İzinli değerler: {', '.join(KONUMLAR)}"
            )
        self.icerik = icerik
        self.metin = metin
        self.konum = konum
        self.ham_html = ham_html
        self.genis = genis
        self.tooltip_id = tooltip_id or f"hg-tip-{next(_sayac)}"

    # ------------------------------------------------------------------ iç
    def _tetikleyici_html(self) -> str:
        if hasattr(self.icerik, "html"):
            return self.icerik.html()
        if self.ham_html:
            return str(self.icerik)
        return guvenli_metin(self.icerik)

    # ----------------------------------------------------------------- API
    def html(self) -> str:
        siniflar = sinif_listesi(
            sinif("tooltip"),
            sinif("tooltip", self.konum),
            sinif("tooltip", "wide") if self.genis else None,
        )
        return (
            f'<span class="{siniflar}" tabindex="0" '
            f'aria-describedby="{self.tooltip_id}">'
            f'<span class="{sinif("tooltip", "trigger")}">'
            f"{self._tetikleyici_html()}</span>"
            f'<span class="{sinif("tooltip", "bubble")}" id="{self.tooltip_id}" '
            f'role="tooltip">{guvenli_metin(self.metin)}</span>'
            f"</span>"
        )

    @classmethod
    def ikon(cls, metin: str, *, konum: str = "top", isaret: str = "ⓘ") -> "Tooltip":
        """Metrik başlıklarının yanına konan küçük bilgi ikonu ipucu."""
        return cls(isaret, metin, konum=konum)
