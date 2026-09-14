# -*- coding: utf-8 -*-
"""UX-01: Card ve MetricCard bileşenleri.

`Card`       : başlık + gövde + altbilgi içeren genel kapsayıcı.
`MetricCard` : DASH-UX-01 mavi (müşteri) / turuncu (sistem) metrik kartı.
"""
from __future__ import annotations

from typing import Any

from company_master.i18n import sayi as _sayi_bicimle
from company_master.ui.base import (
    Bilesen,
    BilesenHatasi,
    etiket,
    guvenli_metin,
    sinif,
    sinif_listesi,
)

#: DASH-UX-01 metrik kategorileri (mavi müşteri / turuncu sistem).
KATEGORILER: tuple[str, ...] = ("customer", "system", "neutral")


class Card(Bilesen):
    """Genel amaçlı kart kapsayıcısı.

    Args:
        baslik: Kart başlığı (opsiyonel).
        icerik: Gövde metni. `ham_html=True` değilse kaçışlanır.
        altbilgi: Alt bilgi satırı.
        ikon: Başlığın soluna eklenen emoji.
        vurgulu: True ise kenarlık marka rengiyle vurgulanır.
        ham_html: İçeriği kaçışlamadan gömer (yalnız güvenilir kaynak için).
    """

    def __init__(
        self,
        *,
        baslik: str = "",
        icerik: str = "",
        altbilgi: str = "",
        ikon: str = "",
        vurgulu: bool = False,
        ham_html: bool = False,
    ) -> None:
        if not any([baslik, icerik, altbilgi]):
            raise BilesenHatasi("Kart tamamen boş olamaz (başlık/içerik/altbilgi)")
        self.baslik = baslik
        self.icerik = icerik
        self.altbilgi = altbilgi
        self.ikon = ikon
        self.vurgulu = bool(vurgulu)
        self.ham_html = bool(ham_html)

    def _baslik_html(self) -> str:
        if not self.baslik:
            return ""
        metin = guvenli_metin(self.baslik)
        if self.ikon:
            metin = (
                etiket("span", guvenli_metin(self.ikon), **{"class": sinif("card", "icon")})
                + metin
            )
        return etiket("div", metin, **{"class": sinif("card", "header")})

    def _govde_html(self) -> str:
        if not self.icerik:
            return ""
        govde = self.icerik if self.ham_html else guvenli_metin(self.icerik)
        return etiket("div", govde, **{"class": sinif("card", "body")})

    def _alt_html(self) -> str:
        if not self.altbilgi:
            return ""
        return etiket(
            "div", guvenli_metin(self.altbilgi), **{"class": sinif("card", "footer")}
        )

    def html(self) -> str:
        siniflar = sinif_listesi(
            sinif("card"), sinif("card", "accent") if self.vurgulu else None
        )
        govde = self._baslik_html() + self._govde_html() + self._alt_html()
        return etiket("div", govde, **{"class": siniflar})


class MetricCard(Bilesen):
    """KPI metrik kartı (DASH-UX-01 renk kodlaması ile).

    Args:
        etiket_metni: Metrik adı ("Toplam Firma").
        deger: Gösterilecek değer (sayı veya metin).
        kategori: customer (mavi) | system (turuncu) | neutral
        delta: Değişim metni ("+12 bu hafta"); None ise gösterilmez.
        delta_yonu: "yukari" | "asagi" | "notr" — renk için.
        aciklama: "Neyi gösterir" satırı (K3 kuralı).
        soru: Operasyonel soru satırı (K3 kuralı).
    """

    def __init__(
        self,
        etiket_metni: str,
        deger: Any,
        *,
        kategori: str = "neutral",
        delta: str | None = None,
        delta_yonu: str = "notr",
        aciklama: str = "",
        soru: str = "",
    ) -> None:
        if not str(etiket_metni).strip():
            raise BilesenHatasi("Metrik etiketi zorunludur")
        if kategori not in KATEGORILER:
            raise BilesenHatasi(
                f"Geçersiz kategori: {kategori!r}. İzinli: {', '.join(KATEGORILER)}"
            )
        if delta_yonu not in ("yukari", "asagi", "notr"):
            raise BilesenHatasi(
                f"Geçersiz delta yönü: {delta_yonu!r}. İzinli: yukari, asagi, notr"
            )
        self.etiket_metni = str(etiket_metni)
        self.deger = deger
        self.kategori = kategori
        self.delta = delta
        self.delta_yonu = delta_yonu
        self.aciklama = aciklama
        self.soru = soru

    def _deger_metni(self) -> str:
        """Sayıları binlik ayraçlı Türkçe biçimde gösterir."""
        return _sayi_bicimle(self.deger)

    def html(self) -> str:
        parcalar = [
            etiket(
                "div",
                guvenli_metin(self.etiket_metni),
                **{"class": sinif("metric", "label")},
            ),
            etiket(
                "div",
                guvenli_metin(self._deger_metni()),
                **{"class": sinif("metric", "value")},
            ),
        ]
        if self.delta is not None:
            ok = {"yukari": "▲", "asagi": "▼", "notr": "•"}[self.delta_yonu]
            parcalar.append(
                etiket(
                    "div",
                    f"{ok} {guvenli_metin(self.delta)}",
                    **{
                        "class": sinif_listesi(
                            sinif("metric", "delta"),
                            sinif("metric", "delta", self.delta_yonu),
                        )
                    },
                )
            )
        if self.aciklama:
            parcalar.append(
                etiket(
                    "div",
                    guvenli_metin(self.aciklama),
                    **{"class": sinif("metric", "hint")},
                )
            )
        if self.soru:
            parcalar.append(
                etiket(
                    "div",
                    guvenli_metin(self.soru),
                    **{"class": sinif("metric", "question")},
                )
            )
        siniflar = sinif_listesi(sinif("metric"), sinif("metric", self.kategori))
        return etiket("div", "".join(parcalar), **{"class": siniflar})
