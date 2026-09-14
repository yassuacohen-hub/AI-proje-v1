# -*- coding: utf-8 -*-
"""UX-01: Dropdown (seçim) bileşeni.

Seçenekler iki biçimde verilebilir:
  - Düz liste: ``["Ankara", "İstanbul"]``
  - (deger, etiket) çiftleri: ``[("06", "Ankara"), ("34", "İstanbul")]``

Çoklu seçim `coklu=True` ile açılır.
"""
from __future__ import annotations

from typing import Any, Iterable, Sequence

from company_master.ui.base import (
    Bilesen,
    BilesenHatasi,
    boyut_dogrula,
    etiket,
    guvenli_metin,
    sinif,
    sinif_listesi,
)
from company_master.ui.components.input import _id_uret


def secenekleri_normalize(secenekler: Iterable[Any]) -> list[tuple[str, str]]:
    """Karışık seçenek girdisini ``(deger, etiket)`` listesine indirger."""
    normal: list[tuple[str, str]] = []
    for ham in secenekler:
        if isinstance(ham, (tuple, list)):
            if len(ham) != 2:
                raise BilesenHatasi(
                    f"Seçenek çifti (deger, etiket) olmalı, alınan: {ham!r}"
                )
            normal.append((str(ham[0]), str(ham[1])))
        else:
            normal.append((str(ham), str(ham)))
    return normal


class Dropdown(Bilesen):
    """Tekli veya çoklu seçim alanı.

    Args:
        etiket_metni: Alanın görünen adı (zorunlu).
        secenekler: Seçenek listesi (düz veya (deger, etiket) çiftleri).
        secili: Tekli seçimde tek değer, çoklu seçimde değer listesi.
        coklu: True ise çoklu seçim (``multiple``).
        yer_tutucu: Boş seçenek metni (tekli seçimde ilk satır).
        yardim: Alt açıklama.
        pasif: True ise devre dışı.
        boyut: sm | md | lg
        alan_id: Elle id.
    """

    def __init__(
        self,
        etiket_metni: str,
        secenekler: Sequence[Any],
        *,
        secili: Any = None,
        coklu: bool = False,
        yer_tutucu: str = "Seçiniz…",
        yardim: str = "",
        pasif: bool = False,
        boyut: str = "md",
        alan_id: str = "",
    ) -> None:
        if not str(etiket_metni).strip():
            raise BilesenHatasi("Dropdown etiketi zorunludur (erişilebilirlik)")
        self.etiket_metni = str(etiket_metni)
        self.secenekler = secenekleri_normalize(secenekler)
        self.coklu = bool(coklu)
        if secili is None:
            self.secili: list[str] = []
        elif isinstance(secili, (list, tuple, set)):
            self.secili = [str(s) for s in secili]
        else:
            self.secili = [str(secili)]
        if not self.coklu and len(self.secili) > 1:
            raise BilesenHatasi("Tekli seçimde birden fazla seçili değer olamaz")
        gecerli = {d for d, _ in self.secenekler}
        bilinmeyen = [s for s in self.secili if s not in gecerli]
        if bilinmeyen:
            raise BilesenHatasi(
                f"Seçenek listesinde olmayan değer(ler): {', '.join(bilinmeyen)}"
            )
        self.yer_tutucu = yer_tutucu
        self.yardim = yardim
        self.pasif = bool(pasif)
        self.boyut = boyut_dogrula(boyut)
        self.alan_id = alan_id or _id_uret(self.etiket_metni).replace(
            "hg-input-", "hg-select-"
        )

    def _secenek_html(self) -> str:
        parcalar: list[str] = []
        if not self.coklu and self.yer_tutucu:
            parcalar.append(
                etiket(
                    "option",
                    guvenli_metin(self.yer_tutucu),
                    value="",
                    disabled=True,
                    selected=not self.secili,
                )
            )
        for deger, gorunen in self.secenekler:
            parcalar.append(
                etiket(
                    "option",
                    guvenli_metin(gorunen),
                    value=deger,
                    selected=deger in self.secili,
                )
            )
        return "".join(parcalar)

    def html(self) -> str:
        etiket_html = etiket(
            "label",
            guvenli_metin(self.etiket_metni),
            **{"class": sinif("select", "label"), "for": self.alan_id},
        )
        select_html = etiket(
            "select",
            self._secenek_html(),
            **{
                "class": sinif_listesi(
                    sinif("select", "field"), sinif("select", self.boyut)
                ),
                "id": self.alan_id,
                "name": self.alan_id,
                "multiple": self.coklu or None,
                "disabled": self.pasif or None,
            },
        )
        yardim_html = (
            etiket("div", guvenli_metin(self.yardim), **{"class": sinif("select", "message")})
            if self.yardim
            else ""
        )
        return etiket(
            "div",
            etiket_html + select_html + yardim_html,
            **{"class": sinif("select", "group")},
        )

    def streamlit(self, container: Any | None = None) -> Any:
        """Gerçek Streamlit selectbox/multiselect çizer, seçimi döndürür."""
        hedef = container
        if hedef is None:
            import streamlit as st

            hedef = st
        gorunenler = [g for _, g in self.secenekler]
        deger_haritasi = {g: d for d, g in self.secenekler}
        if self.coklu:
            varsayilan = [g for d, g in self.secenekler if d in self.secili]
            secim = hedef.multiselect(
                self.etiket_metni,
                gorunenler,
                default=varsayilan,
                help=self.yardim or None,
                disabled=self.pasif,
                key=self.alan_id,
            )
            return [deger_haritasi[s] for s in secim]
        indeks = 0
        if self.secili:
            for i, (d, _) in enumerate(self.secenekler):
                if d == self.secili[0]:
                    indeks = i
                    break
        secim = hedef.selectbox(
            self.etiket_metni,
            gorunenler,
            index=indeks,
            help=self.yardim or None,
            disabled=self.pasif,
            key=self.alan_id,
        )
        return deger_haritasi.get(secim)
