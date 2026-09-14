# -*- coding: utf-8 -*-
"""UX-01: Table (tablo) bileşeni.

Sözlük listesi veya pandas DataFrame kabul eder. Boş veri durumunda
"empty state" mesajı gösterir (K-kuralı: kullanıcı boş ekranda kalmaz).
"""
from __future__ import annotations

from typing import Any, Callable, Iterable, Sequence

from company_master.ui.base import (
    Bilesen,
    BilesenHatasi,
    etiket,
    guvenli_metin,
    sinif,
    sinif_listesi,
)

#: Sütun hizalama seçenekleri.
HIZALAMALAR: tuple[str, ...] = ("left", "center", "right")


class Table(Bilesen):
    """Veri tablosu.

    Args:
        satirlar: Sözlük listesi (her sözlük bir satır).
        sutunlar: Gösterilecek sütun anahtarları; None ise ilk satırdan türetilir.
        basliklar: ``{anahtar: görünen_başlık}`` eşlemesi (opsiyonel).
        hizalama: ``{anahtar: left|center|right}`` eşlemesi (opsiyonel).
        bicimleyiciler: ``{anahtar: fonksiyon}`` — hücre değerini metne çevirir.
        bos_mesaj: Veri yoksa gösterilecek metin.
        zebra: True ise satırlar dönüşümlü arka planla çizilir.
        yogun: True ise satır yüksekliği azaltılır (compact).
        max_satir: Gösterilecek en fazla satır; aşılırsa altta uyarı çıkar.
    """

    def __init__(
        self,
        satirlar: Iterable[dict[str, Any]] | Any,
        *,
        sutunlar: Sequence[str] | None = None,
        basliklar: dict[str, str] | None = None,
        hizalama: dict[str, str] | None = None,
        bicimleyiciler: dict[str, Callable[[Any], str]] | None = None,
        bos_mesaj: str = "Veri gelince burada görünecek.",
        zebra: bool = True,
        yogun: bool = False,
        max_satir: int = 100,
    ) -> None:
        self.satirlar = self._satirlari_coz(satirlar)
        if sutunlar is not None:
            self.sutunlar = list(sutunlar)
        elif self.satirlar:
            self.sutunlar = list(self.satirlar[0].keys())
        else:
            self.sutunlar = []
        self.basliklar = basliklar or {}
        self.hizalama = hizalama or {}
        for anahtar, deger in self.hizalama.items():
            if deger not in HIZALAMALAR:
                raise BilesenHatasi(
                    f"Geçersiz hizalama {deger!r} (sütun: {anahtar}). "
                    f"İzinli: {', '.join(HIZALAMALAR)}"
                )
        self.bicimleyiciler = bicimleyiciler or {}
        self.bos_mesaj = bos_mesaj
        self.zebra = bool(zebra)
        self.yogun = bool(yogun)
        if max_satir < 1:
            raise BilesenHatasi("max_satir en az 1 olmalı")
        self.max_satir = max_satir

    @staticmethod
    def _satirlari_coz(veri: Any) -> list[dict[str, Any]]:
        """DataFrame / sözlük listesi girdisini sözlük listesine çevirir."""
        if veri is None:
            return []
        if hasattr(veri, "to_dict"):  # pandas.DataFrame
            return list(veri.to_dict(orient="records"))
        cozulmus = list(veri)
        for satir in cozulmus:
            if not isinstance(satir, dict):
                raise BilesenHatasi(
                    f"Tablo satırları sözlük olmalı, alınan: {type(satir).__name__}"
                )
        return cozulmus

    @property
    def bos(self) -> bool:
        """Gösterilecek satır var mı?"""
        return not self.satirlar

    def _hucre_metni(self, anahtar: str, deger: Any) -> str:
        bicimleyici = self.bicimleyiciler.get(anahtar)
        if bicimleyici is not None:
            return guvenli_metin(bicimleyici(deger))
        if deger is None:
            return "—"
        if isinstance(deger, bool):
            return "Evet" if deger else "Hayır"
        if isinstance(deger, int):
            return f"{deger:,}".replace(",", ".")
        return guvenli_metin(deger)

    def _baslik_html(self) -> str:
        hucreler = [
            etiket(
                "th",
                guvenli_metin(self.basliklar.get(s, s)),
                **{
                    "class": sinif("table", "th"),
                    "style": f"text-align:{self.hizalama.get(s, 'left')}",
                    "scope": "col",
                },
            )
            for s in self.sutunlar
        ]
        return etiket("thead", etiket("tr", "".join(hucreler)))

    def _govde_html(self) -> str:
        satir_html: list[str] = []
        for satir in self.satirlar[: self.max_satir]:
            hucreler = [
                etiket(
                    "td",
                    self._hucre_metni(s, satir.get(s)),
                    **{
                        "class": sinif("table", "td"),
                        "style": f"text-align:{self.hizalama.get(s, 'left')}",
                    },
                )
                for s in self.sutunlar
            ]
            satir_html.append(etiket("tr", "".join(hucreler)))
        return etiket("tbody", "".join(satir_html))

    def _bos_html(self) -> str:
        return etiket(
            "div",
            guvenli_metin(self.bos_mesaj),
            **{"class": sinif("table", "empty")},
        )

    def html(self) -> str:
        if self.bos:
            return self._bos_html()
        siniflar = sinif_listesi(
            sinif("table"),
            sinif("table", "zebra") if self.zebra else None,
            sinif("table", "dense") if self.yogun else None,
        )
        tablo = etiket(
            "table", self._baslik_html() + self._govde_html(), **{"class": siniflar}
        )
        parcalar = [tablo]
        gizli = len(self.satirlar) - self.max_satir
        if gizli > 0:
            parcalar.append(
                etiket(
                    "div",
                    f"{gizli} satır daha var — filtre uygulayın veya dışa aktarın.",
                    **{"class": sinif("table", "more")},
                )
            )
        return etiket(
            "div", "".join(parcalar), **{"class": sinif("table", "wrapper")}
        )
