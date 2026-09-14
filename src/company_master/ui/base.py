# -*- coding: utf-8 -*-
"""UX-01: Bileşen kütüphanesi ortak altyapısı.

Tüm bileşenler bu modüldeki yardımcıları kullanır:
  - `guvenli_metin()`  : XSS'e karşı HTML kaçışı (KVKK/güvenlik gereği zorunlu)
  - `sinif()`          : `hg-` ön ekli CSS sınıf adı üretimi
  - `varyant_dogrula()`: geçersiz varyant/boyut değerlerini erken yakalar
  - `Bilesen`          : `html()` üreten, Streamlit'ten bağımsız temel sınıf

Tasarım kararı: bileşenler **saf HTML string** üretir; Streamlit çağrısı
`render()` içinde izole edilir. Böylece testler Streamlit çalıştırmadan
sadece HTML çıktısını doğrulayabilir.
"""
from __future__ import annotations

import html as _html
from abc import ABC, abstractmethod
from typing import Any, Iterable, Sequence

from company_master.ui.tokens import ONEK

#: Tüm bileşenlerde ortak semantik varyant kümesi.
VARYANTLAR: tuple[str, ...] = (
    "primary",
    "secondary",
    "success",
    "warning",
    "danger",
    "info",
    "ghost",
)

#: Tüm bileşenlerde ortak boyut kümesi.
BOYUTLAR: tuple[str, ...] = ("sm", "md", "lg")


class BilesenHatasi(ValueError):
    """Bileşene geçersiz parametre verildiğinde fırlatılır."""


def guvenli_metin(deger: Any) -> str:
    """Kullanıcı verisini HTML'e gömmeden önce kaçışlar.

    `None` boş stringe döner. Tırnaklar da kaçışlanır (attribute güvenliği).
    """
    if deger is None:
        return ""
    return _html.escape(str(deger), quote=True)


def sinif(*parcalar: str) -> str:
    """`hg-` ön ekli CSS sınıf adı üretir: ``sinif("button", "primary")``."""
    temiz = [p.strip() for p in parcalar if p and p.strip()]
    if not temiz:
        raise BilesenHatasi("En az bir sınıf parçası gerekli")
    return f"{ONEK}-" + "-".join(temiz)


def sinif_listesi(*siniflar: str | None) -> str:
    """Boş/None değerleri atarak `class` attribute değeri üretir."""
    return " ".join(s for s in siniflar if s)


def varyant_dogrula(varyant: str, izinli: Sequence[str] = VARYANTLAR) -> str:
    """Varyantı doğrular; geçersizse anlaşılır Türkçe hata verir."""
    if varyant not in izinli:
        raise BilesenHatasi(
            f"Geçersiz varyant: {varyant!r}. İzinli değerler: {', '.join(izinli)}"
        )
    return varyant


def boyut_dogrula(boyut: str, izinli: Sequence[str] = BOYUTLAR) -> str:
    """Boyutu doğrular; geçersizse anlaşılır Türkçe hata verir."""
    if boyut not in izinli:
        raise BilesenHatasi(
            f"Geçersiz boyut: {boyut!r}. İzinli değerler: {', '.join(izinli)}"
        )
    return boyut


def nitelik_yaz(nitelikler: dict[str, Any]) -> str:
    """Sözlüğü güvenli HTML attribute dizesine çevirir.

    - `None` ve `False` değerli nitelikler atlanır.
    - `True` değerli nitelikler boolean attribute olarak yazılır (``disabled``).
    """
    parcalar: list[str] = []
    for ad, deger in nitelikler.items():
        if deger is None or deger is False:
            continue
        if deger is True:
            parcalar.append(guvenli_metin(ad))
            continue
        parcalar.append(f'{guvenli_metin(ad)}="{guvenli_metin(deger)}"')
    return " ".join(parcalar)


def etiket(
    ad: str,
    icerik: str = "",
    *,
    kapanissiz: bool = False,
    **nitelikler: Any,
) -> str:
    """Bir HTML etiketi üretir. İçerik **kaçışlanmaz** (bileşen sorumluluğu)."""
    nit = nitelik_yaz(nitelikler)
    acilis = f"<{ad} {nit}>" if nit else f"<{ad}>"
    if kapanissiz:
        return acilis
    return f"{acilis}{icerik}</{ad}>"


class Bilesen(ABC):
    """Tüm UI bileşenlerinin temel sınıfı.

    Alt sınıflar yalnızca `html()` uygular. `render()` Streamlit'e yazar ve
    Streamlit kurulu değilse anlaşılır bir hata verir (test ortamı için).
    """

    @abstractmethod
    def html(self) -> str:
        """Bileşenin HTML çıktısını döndürür (yan etkisiz)."""

    def render(self, container: Any | None = None) -> str:
        """Bileşeni Streamlit'e çizer ve üretilen HTML'i döndürür."""
        cikti = self.html()
        hedef = container
        if hedef is None:
            import streamlit as st  # yerel import: test ortamı Streamlit istemez

            hedef = st
        hedef.markdown(cikti, unsafe_allow_html=True)
        return cikti

    def __str__(self) -> str:  # pragma: no cover - kolaylık
        return self.html()


def birlestir(parcalar: Iterable[str]) -> str:
    """HTML parçalarını boşluksuz birleştirir."""
    return "".join(parcalar)
