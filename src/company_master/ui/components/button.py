# -*- coding: utf-8 -*-
"""UX-01: Button bileşeni.

Kullanım:
    >>> from company_master.ui import Button
    >>> Button("Kaydet", varyant="primary", ikon="💾").html()

Streamlit'te tıklanabilir davranış gerektiğinde `Button.streamlit()`
kullanılır; salt görsel/HTML gerektiğinde `html()` yeterlidir.
"""
from __future__ import annotations

from typing import Any, Callable, Iterable, Sequence

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

__all__ = ["Button", "ButtonGroup", "ROLLER"]

#: ADMIN-UI-02 — semantik buton rolleri.
#:
#: Sahip kuralı: ekranda **tek bir birincil** aksiyon olur. Roller, ekran
#: yazarken "hangi renk?" sorusunu ortadan kaldırmak için vardır; renk seçimi
#: tasarım sisteminin sorumluluğudur, ekranın değil.
ROLLER: dict[str, str] = {
    "birincil": "primary",      # Sayfanın tek ana aksiyonu (Kaydet, Çalıştır)
    "ikincil": "secondary",     # Destekleyici aksiyon (Vazgeç, Geri)
    "tehlikeli": "danger",      # Geri dönüşü olmayan aksiyon (Sil, Sıfırla)
    "sessiz": "ghost",          # Düşük vurgulu aksiyon (Yenile, Detay)
}


def rol_dogrula(rol: str) -> str:
    """Semantik rolü varyanta çevirir; geçersizse Türkçe hata verir."""
    if rol not in ROLLER:
        raise BilesenHatasi(
            f"Geçersiz rol: {rol!r}. İzinli roller: {', '.join(sorted(ROLLER))}"
        )
    return ROLLER[rol]


class Button(Bilesen):
    """Tasarım sistemine uygun buton.

    Args:
        etiket_metni: Buton üzerinde görünen metin.
        rol: birincil | ikincil | tehlikeli | sessiz (verilirse `varyant` ezilir).
            Yeni ekranlarda **rol tercih edilir**; varyant geriye uyum içindir.
        varyant: primary | secondary | success | warning | danger | info | ghost
        boyut: sm | md | lg
        ikon: Metnin soluna yerleşen emoji/ikon (opsiyonel).
        pasif: True ise buton devre dışı görünür ve tıklanamaz.
        tam_genislik: True ise kapsayıcının tamamını kaplar.
        yukleniyor: True ise spinner gösterilir ve buton pasifleşir.
        href: Verilirse `<a>` olarak render edilir (link buton).
        anahtar: Streamlit `key` değeri (streamlit() için).
    """

    def __init__(
        self,
        etiket_metni: str,
        *,
        rol: str = "",
        varyant: str = "primary",
        boyut: str = "md",
        ikon: str = "",
        pasif: bool = False,
        tam_genislik: bool = False,
        yukleniyor: bool = False,
        href: str = "",
        anahtar: str = "",
    ) -> None:
        if not str(etiket_metni).strip() and not ikon:
            raise BilesenHatasi("Buton metni veya ikon zorunludur")
        self.etiket_metni = str(etiket_metni)
        self.rol = rol
        self.varyant = rol_dogrula(rol) if rol else varyant_dogrula(varyant)
        self.boyut = boyut_dogrula(boyut)
        self.ikon = ikon
        self.pasif = bool(pasif) or bool(yukleniyor)
        self.tam_genislik = bool(tam_genislik)
        self.yukleniyor = bool(yukleniyor)
        self.href = href
        self.anahtar = anahtar

    def _siniflar(self) -> str:
        return sinif_listesi(
            sinif("btn"),
            sinif("btn", self.varyant),
            sinif("btn", self.boyut),
            sinif("btn", "block") if self.tam_genislik else None,
            sinif("btn", "loading") if self.yukleniyor else None,
            sinif("btn", "disabled") if self.pasif else None,
        )

    def _icerik(self) -> str:
        parcalar: list[str] = []
        if self.yukleniyor:
            parcalar.append(etiket("span", "", **{"class": sinif("spinner")}))
        elif self.ikon:
            parcalar.append(
                etiket("span", guvenli_metin(self.ikon), **{"class": sinif("btn", "icon")})
            )
        if self.etiket_metni.strip():
            parcalar.append(
                etiket(
                    "span",
                    guvenli_metin(self.etiket_metni),
                    **{"class": sinif("btn", "label")},
                )
            )
        return "".join(parcalar)

    def html(self) -> str:
        nitelikler: dict[str, Any] = {
            "class": self._siniflar(),
            "type": "button",
        }
        if self.pasif:
            nitelikler["disabled"] = True
            nitelikler["aria-disabled"] = "true"
        if self.yukleniyor:
            nitelikler["aria-busy"] = "true"
        if self.href and not self.pasif:
            nitelikler.pop("type", None)
            nitelikler["href"] = self.href
            nitelikler["role"] = "button"
            return etiket("a", self._icerik(), **nitelikler)
        return etiket("button", self._icerik(), **nitelikler)

    def streamlit(
        self,
        container: Any | None = None,
        on_click: Callable[[], None] | None = None,
    ) -> bool:
        """Gerçek tıklanabilir Streamlit butonu çizer, tıklandıysa True döner."""
        hedef = container
        if hedef is None:
            import streamlit as st

            hedef = st
        gorunen = f"{self.ikon} {self.etiket_metni}".strip()
        return bool(
            hedef.button(
                gorunen,
                key=self.anahtar or None,
                disabled=self.pasif,
                width="stretch" if self.tam_genislik else "content",
                type="primary" if self.varyant == "primary" else "secondary",
                on_click=on_click,
            )
        )


class ButtonGroup(Bilesen):
    """ADMIN-UI-02: Aksiyon kümesi — tek birincil buton kuralını zorlar.

    Sahip kuralı: *"aynı ekranda birden fazla birincil buton olmasın."*
    Bu sınıf kuralı kod seviyesinde uygular; ihlal ``ValueError`` fırlatır.

    Args:
        butonlar: `Button` nesneleri.
        hizalama: ``sol`` | ``sag`` | ``arali`` (space-between).

    Raises:
        ValueError: Liste boşsa veya birden fazla birincil buton varsa.

    Örnek:
        >>> ButtonGroup([Button("Kaydet", rol="birincil"),
        ...              Button("Vazgeç", rol="ikincil")]).html()[:16]
        '<div class="hg-a'
    """

    HIZALAMALAR: Sequence[str] = ("sol", "sag", "arali")

    def __init__(
        self,
        butonlar: Iterable[Button],
        *,
        hizalama: str = "sol",
    ) -> None:
        self.butonlar = list(butonlar)
        if not self.butonlar:
            raise ValueError("ButtonGroup en az bir buton gerektirir.")
        if hizalama not in self.HIZALAMALAR:
            raise BilesenHatasi(
                f"Geçersiz hizalama: {hizalama!r}. "
                f"İzinli değerler: {', '.join(self.HIZALAMALAR)}"
            )
        birincil = [b for b in self.butonlar if getattr(b, "varyant", "") == "primary"]
        if len(birincil) > 1:
            adlar = [b.etiket_metni for b in birincil]
            raise ValueError(
                "Aynı ekranda yalnızca bir birincil buton olabilir; "
                f"birden fazla bulundu: {adlar}. "
                "Diğerlerini rol='ikincil' veya rol='sessiz' yapın."
            )
        self.hizalama = hizalama

    def html(self) -> str:
        govde = "".join(b.html() for b in self.butonlar)
        siniflar = sinif_listesi(
            sinif("actions"), sinif("actions", self.hizalama)
        )
        return etiket("div", govde, **{"class": siniflar, "role": "group"})
