# -*- coding: utf-8 -*-
"""UX-01: Input bileşeni (metin/sayı/şifre/arama/çok satırlı).

Erişilebilirlik: her alan `label` ile `id` üzerinden bağlanır; hata durumunda
`aria-invalid` ve `aria-describedby` yazılır (ekran okuyucu desteği).
"""
from __future__ import annotations

import re
from typing import Any

from company_master.ui.base import (
    Bilesen,
    BilesenHatasi,
    boyut_dogrula,
    etiket,
    guvenli_metin,
    sinif,
    sinif_listesi,
)

#: Desteklenen alan tipleri.
TIPLER: tuple[str, ...] = ("text", "number", "password", "email", "search", "textarea")

_ID_TEMIZ = re.compile(r"[^a-zA-Z0-9_-]+")


def _id_uret(etiket_metni: str) -> str:
    """Etiketten güvenli bir HTML `id` üretir."""
    taban = _ID_TEMIZ.sub("-", etiket_metni.strip().lower()).strip("-")
    return f"hg-input-{taban or 'alan'}"


class Input(Bilesen):
    """Etiketli form giriş alanı.

    Args:
        etiket_metni: Alanın görünen adı (zorunlu — erişilebilirlik gereği).
        deger: Başlangıç değeri.
        tip: text | number | password | email | search | textarea
        yer_tutucu: Placeholder metni.
        yardim: Alanın altında görünen açıklama.
        hata: Doluysa alan hatalı görünür ve mesaj kırmızı gösterilir.
        zorunlu: True ise etikete `*` eklenir ve `required` yazılır.
        pasif: True ise alan devre dışıdır.
        boyut: sm | md | lg
        alan_id: Elle `id` vermek için (verilmezse etiketten türetilir).
    """

    def __init__(
        self,
        etiket_metni: str,
        *,
        deger: Any = "",
        tip: str = "text",
        yer_tutucu: str = "",
        yardim: str = "",
        hata: str = "",
        zorunlu: bool = False,
        pasif: bool = False,
        boyut: str = "md",
        alan_id: str = "",
    ) -> None:
        if not str(etiket_metni).strip():
            raise BilesenHatasi("Input etiketi zorunludur (erişilebilirlik)")
        if tip not in TIPLER:
            raise BilesenHatasi(
                f"Geçersiz input tipi: {tip!r}. İzinli: {', '.join(TIPLER)}"
            )
        self.etiket_metni = str(etiket_metni)
        self.deger = deger
        self.tip = tip
        self.yer_tutucu = yer_tutucu
        self.yardim = yardim
        self.hata = hata
        self.zorunlu = bool(zorunlu)
        self.pasif = bool(pasif)
        self.boyut = boyut_dogrula(boyut)
        self.alan_id = alan_id or _id_uret(self.etiket_metni)

    @property
    def hatali(self) -> bool:
        """Alanda görüntülenecek bir hata mesajı var mı?"""
        return bool(str(self.hata).strip())

    def _yardim_id(self) -> str:
        return f"{self.alan_id}-yardim"

    def _etiket_html(self) -> str:
        metin = guvenli_metin(self.etiket_metni)
        if self.zorunlu:
            metin += etiket("span", "*", **{"class": sinif("input", "required")})
        return etiket(
            "label",
            metin,
            **{"class": sinif("input", "label"), "for": self.alan_id},
        )

    def _alan_html(self) -> str:
        siniflar = sinif_listesi(
            sinif("input", "field"),
            sinif("input", self.boyut),
            sinif("input", "error") if self.hatali else None,
        )
        ortak: dict[str, Any] = {
            "class": siniflar,
            "id": self.alan_id,
            "name": self.alan_id,
            "placeholder": self.yer_tutucu or None,
            "disabled": self.pasif or None,
            "required": self.zorunlu or None,
            "aria-invalid": "true" if self.hatali else None,
            "aria-describedby": self._yardim_id()
            if (self.hatali or self.yardim)
            else None,
        }
        if self.tip == "textarea":
            return etiket("textarea", guvenli_metin(self.deger), rows="4", **ortak)
        ortak["type"] = self.tip
        ortak["value"] = guvenli_metin(self.deger)
        return etiket("input", "", kapanissiz=True, **ortak)

    def _yardim_html(self) -> str:
        if self.hatali:
            return etiket(
                "div",
                guvenli_metin(self.hata),
                **{
                    "class": sinif("input", "message-error"),
                    "id": self._yardim_id(),
                    "role": "alert",
                },
            )
        if self.yardim:
            return etiket(
                "div",
                guvenli_metin(self.yardim),
                **{"class": sinif("input", "message"), "id": self._yardim_id()},
            )
        return ""

    def html(self) -> str:
        govde = self._etiket_html() + self._alan_html() + self._yardim_html()
        return etiket("div", govde, **{"class": sinif("input", "group")})

    def streamlit(self, container: Any | None = None) -> Any:
        """Gerçek Streamlit girdisi çizer ve kullanıcı değerini döndürür."""
        hedef = container
        if hedef is None:
            import streamlit as st

            hedef = st
        yardim = self.hata or self.yardim or None
        if self.tip == "textarea":
            return hedef.text_area(
                self.etiket_metni,
                value=str(self.deger or ""),
                placeholder=self.yer_tutucu or None,
                help=yardim,
                disabled=self.pasif,
                key=self.alan_id,
            )
        if self.tip == "number":
            return hedef.number_input(
                self.etiket_metni,
                value=float(self.deger or 0),
                help=yardim,
                disabled=self.pasif,
                key=self.alan_id,
            )
        return hedef.text_input(
            self.etiket_metni,
            value=str(self.deger or ""),
            placeholder=self.yer_tutucu or None,
            help=yardim,
            disabled=self.pasif,
            type="password" if self.tip == "password" else "default",
            key=self.alan_id,
        )
