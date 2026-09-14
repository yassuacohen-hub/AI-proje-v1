# -*- coding: utf-8 -*-
"""UX-01: Modal (diyalog) bileşeni.

Streamlit'te gerçek modal yoktur; bu bileşen iki kullanım sunar:
  1. `html()`  → `role="dialog"` erişilebilir statik diyalog işaretlemesi
     (onay ekranları, bilgi kutuları, `st.markdown(..., unsafe_allow_html=True)`).
  2. `streamlit()` → `st.dialog` varsa onu, yoksa `st.expander` yedeğini kullanır.

Katmanlama `--hg-z-modal-backdrop` (1200) ve `--hg-z-modal` (1201) token'larına
dayanır; Dropdown (1000) ve Tooltip (1100) üzerinde kalması garanti edilir.
"""
from __future__ import annotations

import re
from typing import Any, Callable, Sequence

from company_master.ui.base import (
    Bilesen,
    BilesenHatasi,
    boyut_dogrula,
    guvenli_metin,
    sinif,
    sinif_listesi,
)

#: Modal genişlik kademeleri.
MODAL_BOYUTLARI: tuple[str, ...] = ("sm", "md", "lg", "full")

_ID_TEMIZ = re.compile(r"[^a-zA-Z0-9_-]+")


def _modal_id(baslik: str) -> str:
    """Başlıktan kararlı bir DOM kimliği üretir."""
    slug = _ID_TEMIZ.sub("-", baslik.strip().lower()).strip("-")
    return f"hg-modal-{slug or 'diyalog'}"


class Modal(Bilesen):
    """Erişilebilir diyalog kutusu.

    Parametreler
    ------------
    baslik:
        Diyalog başlığı (zorunlu — `aria-labelledby` buna bağlanır).
    icerik:
        Gövde metni. `ham_html=True` verilmedikçe kaçışlanır.
    aksiyonlar:
        Alt bara yerleşecek bileşenler (genelde `Button`). `html()` üreten
        her nesne veya hazır HTML string kabul edilir.
    boyut:
        `sm` | `md` | `lg` | `full`.
    kapatilabilir:
        `True` ise sağ üstte ✕ düğmesi çizilir.
    acik:
        `False` ise kök öğeye `hidden` + `hg-modal-kapali` eklenir.
    aciklama:
        Başlık altındaki tek satırlık açıklama (K3 kuralı).
    ham_html:
        İçeriği kaçışlamadan gömer. Yalnızca güvenilir içerik için.
    """

    def __init__(
        self,
        baslik: str,
        icerik: str = "",
        *,
        aksiyonlar: Sequence[Any] | None = None,
        boyut: str = "md",
        kapatilabilir: bool = True,
        acik: bool = True,
        aciklama: str = "",
        ham_html: bool = False,
        modal_id: str = "",
    ) -> None:
        if not baslik or not baslik.strip():
            raise BilesenHatasi("Modal başlığı zorunludur (erişilebilirlik gereği)")
        self.baslik = baslik
        self.icerik = icerik
        self.aksiyonlar = list(aksiyonlar or [])
        self.boyut = boyut_dogrula(boyut, MODAL_BOYUTLARI)
        self.kapatilabilir = kapatilabilir
        self.acik = acik
        self.aciklama = aciklama
        self.ham_html = ham_html
        self.modal_id = modal_id or _modal_id(baslik)

    # ------------------------------------------------------------------ iç
    @property
    def baslik_id(self) -> str:
        return f"{self.modal_id}-baslik"

    @property
    def aciklama_id(self) -> str:
        return f"{self.modal_id}-aciklama"

    def _aksiyon_html(self) -> str:
        parcalar: list[str] = []
        for aksiyon in self.aksiyonlar:
            if hasattr(aksiyon, "html"):
                parcalar.append(aksiyon.html())
            elif isinstance(aksiyon, str):
                parcalar.append(aksiyon)
            else:
                raise BilesenHatasi(
                    "Aksiyon ya html() üreten bir bileşen ya da HTML string olmalı"
                )
        if not parcalar:
            return ""
        return f'<div class="{sinif("modal", "footer")}">{"".join(parcalar)}</div>'

    def _basli_html(self) -> str:
        kapat = ""
        if self.kapatilabilir:
            kapat = (
                f'<button type="button" class="{sinif("modal", "close")}" '
                f'aria-label="Kapat">&times;</button>'
            )
        aciklama = ""
        if self.aciklama:
            aciklama = (
                f'<p class="{sinif("modal", "subtitle")}" id="{self.aciklama_id}">'
                f"{guvenli_metin(self.aciklama)}</p>"
            )
        return (
            f'<header class="{sinif("modal", "header")}">'
            f'<div><h2 class="{sinif("modal", "title")}" id="{self.baslik_id}">'
            f"{guvenli_metin(self.baslik)}</h2>{aciklama}</div>"
            f"{kapat}</header>"
        )

    # ----------------------------------------------------------------- API
    def html(self) -> str:
        govde = self.icerik if self.ham_html else guvenli_metin(self.icerik)
        govde_html = f'<div class="{sinif("modal", "body")}">{govde}</div>'
        siniflar = sinif_listesi(
            sinif("modal"),
            sinif("modal", self.boyut),
            None if self.acik else sinif("modal", "kapali"),
        )
        gizli = "" if self.acik else " hidden"
        aciklama_bag = (
            f' aria-describedby="{self.aciklama_id}"' if self.aciklama else ""
        )
        return (
            f'<div class="{sinif("modal", "backdrop")}" '
            f'id="{self.modal_id}"{gizli}>'
            f'<div class="{siniflar}" role="dialog" aria-modal="true" '
            f'aria-labelledby="{self.baslik_id}"{aciklama_bag}>'
            f"{self._basli_html()}{govde_html}{self._aksiyon_html()}"
            f"</div></div>"
        )

    def streamlit(self, govde_fn: Callable[[], None] | None = None) -> Any:
        """Streamlit'te diyalog açar.

        `st.dialog` (Streamlit >= 1.31) varsa gerçek modal; yoksa `st.expander`
        yedeği kullanılır. `govde_fn` verilmezse `icerik` markdown olarak yazılır.
        """
        import streamlit as st  # yerel import: test ortamı Streamlit istemez

        def _cizim() -> None:
            if self.aciklama:
                st.caption(self.aciklama)
            if govde_fn is not None:
                govde_fn()
            elif self.icerik:
                st.markdown(self.icerik)

        dialog = getattr(st, "dialog", None)
        if callable(dialog):
            @dialog(self.baslik)  # type: ignore[misc]
            def _modal() -> None:
                _cizim()

            return _modal()

        with st.expander(self.baslik, expanded=self.acik):
            _cizim()
        return None
