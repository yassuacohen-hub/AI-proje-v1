# -*- coding: utf-8 -*-
"""Sayfa iskeleti bileşenleri (ADMIN-UI-01).

Streamlit Playground dokümantasyon mantığını kod sözleşmesine çevirir:

    H1 (sayfa başlığı)
      └─ giriş paragrafı (lead) — "bu ekran ne işe yarar"
          └─ H2 bölüm ─ isteğe bağlı H3 alt bölüm
              └─ içerik + aksiyon öğeleri

Neden ayrı bir bileşen?
    Önceden her sekme kendi `st.markdown("## ...")` / `st.subheader` karışımını
    yazıyordu; punto ve boşluk her ekranda farklıydı. Buradaki sınıflar tek
    tipografi ölçeğine (``--hg-font-size-h1`` vb.) bağlıdır, dolayısıyla
    hiyerarşi ekrandan ekrana kaymaz.

Kullanım (Streamlit):
    from company_master.ui import PageHeader, Section, SectionNav

    PageHeader("Ana Kontrol", "Panelin genel sağlık özeti.").render()
    SectionNav([("veri-sagligi", "Veri Sağlığı"), ("sistem", "Sistem")]).render()
    Section("Veri Sağlığı", kimlik="veri-sagligi").render()
"""
from __future__ import annotations

import re
import unicodedata
from typing import Any, Iterable, Sequence

from company_master.ui.base import (
    Bilesen,
    etiket,
    guvenli_metin,
    nitelik_yaz,
    sinif_listesi,
)

__all__ = ["PageHeader", "Section", "SectionNav", "kimlik_uret"]

_TR_HARITA = str.maketrans(
    {
        "ç": "c", "Ç": "c",
        "ğ": "g", "Ğ": "g",
        "ı": "i", "İ": "i",
        "ö": "o", "Ö": "o",
        "ş": "s", "Ş": "s",
        "ü": "u", "Ü": "u",
    }
)
_SLUG_TEMIZ = re.compile(r"[^a-z0-9]+")


def kimlik_uret(metin: str) -> str:
    """Başlıktan anchor kimliği üretir (Türkçe karakter güvenli).

    ``"Veri Sağlığı Özeti"`` → ``"veri-sagligi-ozeti"``

    Not: ``unicodedata.normalize`` tek başına Türkçe ``ı``/``İ`` için doğru
    sonuç vermez; bu yüzden önce açık harita uygulanır.
    """
    duz = metin.translate(_TR_HARITA)
    duz = unicodedata.normalize("NFKD", duz).encode("ascii", "ignore").decode("ascii")
    duz = _SLUG_TEMIZ.sub("-", duz.lower()).strip("-")
    return duz or "bolum"


class PageHeader(Bilesen):
    """Sayfa başlığı bloğu: üst etiket + H1 + giriş paragrafı + aksiyonlar.

    Args:
        baslik: H1 metni. Bir ekranda **yalnız bir** ``PageHeader`` olmalı.
        giris: H1 altındaki kısa açıklama ("bu ekran ne işe yarar").
        ust_etiket: Başlığın üstündeki küçük bağlam etiketi (örn. grup adı).
        ikon: Başlığın solundaki emoji/ikon.
        aksiyonlar: Sağ üstte duracak `Button` benzeri bileşenler.
            **Kural:** en fazla bir tanesi ``varyant="primary"`` olmalıdır.
        kimlik: Anchor kimliği; verilmezse başlıktan üretilir.

    Raises:
        ValueError: Birden fazla birincil aksiyon verilirse.
    """

    def __init__(
        self,
        baslik: str,
        giris: str = "",
        *,
        ust_etiket: str = "",
        ikon: str = "",
        aksiyonlar: Sequence[Any] = (),
        kimlik: str = "",
    ) -> None:
        self.baslik = baslik
        self.giris = giris
        self.ust_etiket = ust_etiket
        self.ikon = ikon
        self.aksiyonlar = list(aksiyonlar)
        self.kimlik = kimlik or kimlik_uret(baslik)
        self._birincil_dogrula()

    def _birincil_dogrula(self) -> None:
        birincil = [a for a in self.aksiyonlar if getattr(a, "varyant", None) == "primary"]
        if len(birincil) > 1:
            raise ValueError(
                "Bir ekranda tek birincil aksiyon olmalı; "
                f"{len(birincil)} adet 'primary' buton verildi. "
                "Fazlasını varyant='secondary' yapın."
            )

    def _ust_etiket_html(self) -> str:
        if not self.ust_etiket:
            return ""
        return etiket("p", guvenli_metin(self.ust_etiket), **{"class": "hg-page-eyebrow"})

    def _baslik_html(self) -> str:
        ikon_html = (
            etiket(
                "span",
                guvenli_metin(self.ikon),
                **{"class": "hg-page-icon", "aria-hidden": "true"},
            )
            if self.ikon
            else ""
        )
        return etiket(
            "h1",
            ikon_html + guvenli_metin(self.baslik),
            **{"class": "hg-page-title", "id": self.kimlik or None},
        )

    def _giris_html(self) -> str:
        if not self.giris:
            return ""
        return etiket("p", guvenli_metin(self.giris), **{"class": "hg-page-lead"})

    def _aksiyon_html(self) -> str:
        if not self.aksiyonlar:
            return ""
        govde = "".join(str(a) for a in self.aksiyonlar)
        return etiket("div", govde, **{"class": "hg-page-actions"})

    def html(self) -> str:
        sol = self._ust_etiket_html() + self._baslik_html() + self._giris_html()
        govde = etiket("div", sol, **{"class": "hg-page-head-main"}) + self._aksiyon_html()
        return etiket("header", govde, **{"class": "hg-page-head"})


class Section(Bilesen):
    """Mantıksal içerik bölümü: H2 (veya H3) + açıklama + ayraç.

    Args:
        baslik: Bölüm başlığı.
        aciklama: Başlığın altındaki tek satırlık açıklama.
        seviye: ``2`` → H2 (ana bölüm), ``3`` → H3 (alt bölüm).
        kimlik: Anchor kimliği; verilmezse başlıktan üretilir.
        ikon: Başlık solundaki ikon.
        ayrac: Bölüm üstüne ince ayraç çizgisi koyar (yalnız H2 için anlamlı).

    Raises:
        ValueError: ``seviye`` 2 veya 3 dışında verilirse.
    """

    def __init__(
        self,
        baslik: str,
        aciklama: str = "",
        *,
        seviye: int = 2,
        kimlik: str = "",
        ikon: str = "",
        ayrac: bool = True,
    ) -> None:
        if seviye not in (2, 3):
            raise ValueError(
                f"Bölüm seviyesi 2 (H2) veya 3 (H3) olmalı; {seviye!r} verildi. "
                "Sayfa başlığı için PageHeader kullanın."
            )
        self.baslik = baslik
        self.aciklama = aciklama
        self.seviye = seviye
        self.kimlik = kimlik or kimlik_uret(baslik)
        self.ikon = ikon
        self.ayrac = ayrac and seviye == 2

    def html(self) -> str:
        ikon_html = (
            etiket(
                "span",
                guvenli_metin(self.ikon),
                **{"class": "hg-section-icon", "aria-hidden": "true"},
            )
            if self.ikon
            else ""
        )
        baslik_html = etiket(
            f"h{self.seviye}",
            ikon_html + guvenli_metin(self.baslik),
            **{
                "class": f"hg-section-title hg-section-h{self.seviye}",
                "id": self.kimlik or None,
            },
        )
        aciklama_html = (
            etiket("p", guvenli_metin(self.aciklama), **{"class": "hg-section-desc"})
            if self.aciklama
            else ""
        )
        siniflar = sinif_listesi("hg-section", "hg-section-ruled" if self.ayrac else None)
        return etiket("section", baslik_html + aciklama_html, **{"class": siniflar})


class SectionNav(Bilesen):
    """Sayfa içi gezinme — "Bu sayfada" anchor listesi.

    Uzun ekranlarda düz listeyi taranabilir bölümlere çevirir.

    Args:
        bolumler: ``(kimlik, etiket)`` çiftleri **veya** doğrudan `Section`
            nesneleri. `Section` verilirse kimlik/başlık ondan okunur.
        baslik: Liste başlığı.
        yatay: ``True`` ise sekme şeridi gibi yatay dizilir (dar ekran dostu).

    Raises:
        ValueError: Bölüm listesi boşsa veya kimlikler benzersiz değilse.
    """

    def __init__(
        self,
        bolumler: Iterable[Any],
        *,
        baslik: str = "Bu sayfada",
        yatay: bool = False,
    ) -> None:
        self.ogeler = self._normalize(bolumler)
        if not self.ogeler:
            raise ValueError("SectionNav en az bir bölüm gerektirir.")
        kimlikler = [k for k, _, _ in self.ogeler]
        if len(kimlikler) != len(set(kimlikler)):
            yinelenen = sorted({k for k in kimlikler if kimlikler.count(k) > 1})
            raise ValueError(
                f"Anchor kimlikleri benzersiz olmalı; yinelenen: {yinelenen}. "
                "Aynı başlığı iki kez kullanıyorsanız `kimlik=` ile ayırın."
            )
        self.baslik = baslik
        self.yatay = yatay

    @staticmethod
    def _normalize(bolumler: Iterable[Any]) -> list[tuple[str, str, int]]:
        """``(kimlik, etiket, seviye)`` üçlülerine indirger."""
        sonuc: list[tuple[str, str, int]] = []
        for oge in bolumler:
            if isinstance(oge, Section):
                sonuc.append((oge.kimlik, oge.baslik, oge.seviye))
            elif isinstance(oge, (tuple, list)) and len(oge) >= 2:
                seviye = int(oge[2]) if len(oge) > 2 else 2
                sonuc.append((str(oge[0]), str(oge[1]), seviye))
            else:
                metin = str(oge)
                sonuc.append((kimlik_uret(metin), metin, 2))
        return sonuc

    def html(self) -> str:
        baglantilar = "".join(
            etiket(
                "a",
                guvenli_metin(ad),
                **{
                    "class": sinif_listesi("hg-nav-link", f"hg-nav-l{seviye}"),
                    "href": f"#{kimlik}",
                },
            )
            for kimlik, ad, seviye in self.ogeler
        )
        baslik_html = etiket("p", guvenli_metin(self.baslik), **{"class": "hg-nav-title"})
        siniflar = sinif_listesi(
            "hg-nav", "hg-nav-horizontal" if self.yatay else "hg-nav-vertical"
        )
        nitelikler = nitelik_yaz({"class": siniflar, "aria-label": self.baslik})
        return f"<nav {nitelikler}>{baslik_html}{baglantilar}</nav>"
