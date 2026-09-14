# -*- coding: utf-8 -*-
"""ADMIN-UI-03: Üst şerit (topbar) ve AI sohbet balonu.

Sahip talimatındaki üç yeni unsurdan ikisi burada tanımlanır:

* **Gece/gündüz tema düğmesi** (sağ üst) — :class:`ThemeToggle`
* **AI Abrakadabra sohbet balonu** (sağ alt) — :class:`ChatBubble`

Üçüncü unsur olan arama alanı, gerçek metin girişi gerektirdiği için
Streamlit'in kendi ``st.text_input`` bileşeniyle çizilir; bu modül ona
yerleşim sağlayan :class:`TopBar` kabuğunu üretir.

Neden link (``<a href="?...">``) tabanlı?
    Streamlit ``unsafe_allow_html`` ile enjekte edilen HTML içinde JavaScript
    **çalışmaz**. Bu yüzden tıklanabilir kontroller, sorgu parametresi
    değiştiren normal bağlantılar olarak kurulur: tıklama sayfayı yeniden
    yükler, ``app.py`` parametreyi okur ve durumu uygular. Böylece hiçbir
    ek bileşen/JS bağımlılığı olmadan gerçek etkileşim elde edilir.
"""
from __future__ import annotations

from typing import Any, Iterable

from company_master.ui.base import (
    Bilesen,
    BilesenHatasi,
    etiket,
    guvenli_metin,
    sinif,
    sinif_listesi,
)

#: Tema anahtarı → (ikon, düğme metni, erişilebilirlik açıklaması).
#:
#: Değerler **mevcut görsel dili korur**: yeni renk/ikon icat edilmez,
#: yalnızca ay/güneş sembolleri kullanılır.
TEMA_SUNUMU: dict[str, tuple[str, str, str]] = {
    "karanlik": ("🌙", "Gece", "Gündüz moduna geç"),
    "aydinlik": ("☀️", "Gündüz", "Gece moduna geç"),
}

#: Sohbet mesajı rolleri → CSS son eki.
SOHBET_ROLLERI: dict[str, str] = {
    "ai": "ai",
    "kullanici": "kullanici",
}


def tema_dogrula(tema: str) -> str:
    """Tema anahtarını doğrular; geçersizse Türkçe hata verir."""
    if tema not in TEMA_SUNUMU:
        raise BilesenHatasi(
            f"Geçersiz tema: {tema!r}. İzinli temalar: {', '.join(sorted(TEMA_SUNUMU))}"
        )
    return tema


def tema_karsiti(tema: str) -> str:
    """Verilen temanın karşıtını döndürür (düğmenin hedefi)."""
    return "aydinlik" if tema_dogrula(tema) == "karanlik" else "karanlik"


class ThemeToggle(Bilesen):
    """Sağ üst gece/gündüz geçiş düğmesi.

    Args:
        tema: **Şu anda aktif** tema (``"karanlik"`` / ``"aydinlik"``).
        hedef_url: Tıklanınca gidilecek adres. Varsayılan, yalnız tema
            parametresini değiştiren göreli bağlantıdır.

    Görünen etiket her zaman *aktif* temayı anlatır; ``aria-label`` ise
    tıklamanın **ne yapacağını** söyler. Ekran okuyucu kullanıcısı düğmenin
    bir durum göstergesi mi yoksa eylem mi olduğunu böylece ayırt eder.
    """

    def __init__(self, tema: str = "karanlik", hedef_url: str | None = None) -> None:
        self.tema = tema_dogrula(tema)
        self.hedef = tema_karsiti(self.tema)
        self.hedef_url = hedef_url if hedef_url is not None else f"?tema={self.hedef}"

    def html(self) -> str:
        ikon, metin, aciklama = TEMA_SUNUMU[self.tema]
        govde = etiket("span", ikon, **{"class": sinif("theme-toggle", "ikon"), "aria-hidden": "true"})
        govde += etiket("span", metin, **{"class": sinif("theme-toggle", "metin")})
        return etiket(
            "a",
            govde,
            **{
                "class": sinif("theme-toggle"),
                "href": self.hedef_url,
                "role": "button",
                "title": aciklama,
                "aria-label": aciklama,
                "data-tema": self.tema,
            },
        )


class TopBar(Bilesen):
    """Sayfa üstü şerit: sol tarafta kimlik, sağ tarafta kontroller.

    Args:
        baslik: Şeritte görünen kısa başlık (sayfa H1'inin yerini **almaz**;
            H1 :class:`PageHeader` tarafından çizilir).
        ust_etiket: Başlığın üzerindeki küçük bağlam metni (örn. grup adı).
        sag: Sağ bölüme yerleşecek hazır HTML parçaları (tema düğmesi vb.).

    Şerit bilinçli olarak "boş kabuk"tur: hangi kontrolün sağa gireceğine
    çağıran karar verir. Böylece arama alanı ileride Streamlit widget'ından
    saf HTML'e (veya tersine) taşınırken bu sınıf değişmez.
    """

    def __init__(
        self,
        baslik: str,
        ust_etiket: str = "",
        sag: Iterable[Any] | None = None,
    ) -> None:
        if not str(baslik).strip():
            raise ValueError("TopBar başlığı boş olamaz")
        self.baslik = baslik
        self.ust_etiket = ust_etiket
        self.sag = [self._parca(p) for p in (sag or [])]

    @staticmethod
    def _parca(deger: Any) -> str:
        """Bileşen nesnesini veya hazır HTML metnini tek biçime indirger."""
        return deger.html() if isinstance(deger, Bilesen) else str(deger)

    def _sol_html(self) -> str:
        ic = ""
        if self.ust_etiket:
            ic += etiket(
                "span",
                guvenli_metin(self.ust_etiket),
                **{"class": sinif("topbar", "etiket")},
            )
        ic += etiket(
            "span",
            guvenli_metin(self.baslik),
            **{"class": sinif("topbar", "baslik")},
        )
        return etiket("div", ic, **{"class": sinif("topbar", "sol")})

    def _sag_html(self) -> str:
        return etiket("div", "".join(self.sag), **{"class": sinif("topbar", "sag")})

    def html(self) -> str:
        return etiket(
            "header",
            self._sol_html() + self._sag_html(),
            **{"class": sinif("topbar")},
        )


class ChatBubble(Bilesen):
    """Sağ alt köşedeki "AI Abrakadabra" sohbet balonu.

    Kapalıyken yalnız yüzen bir düğme (FAB), açıkken küçük bir panel çizer.

    Args:
        acik: Panelin açık olup olmadığı.
        mesajlar: ``(rol, metin)`` ikilileri veya ``{"rol": ..., "metin": ...}``
            sözlükleri. Rol ``"ai"`` veya ``"kullanici"`` olmalıdır.
        ac_url / kapat_url: FAB ve kapatma düğmesinin bağlantıları.
        not_metni: Panel altındaki durum notu.

    Not (bilinçli kapsam sınırı):
        Bu sınıf **yalnızca kabuğu** üretir. Gerçek dil modeli bağlantısı
        ayrı bir görevdir; sahip talimatı: "iş yükü çoksa not alırsın sonra
        yaparız". Mesaj listesi dışarıdan verildiği için motor bağlandığında
        bu dosyada değişiklik gerekmez.
    """

    VARSAYILAN_NOT = "Sohbet motoru henüz bağlı değil — arayüz hazır."

    def __init__(
        self,
        acik: bool = False,
        mesajlar: Iterable[Any] | None = None,
        ac_url: str = "?sohbet=acik",
        kapat_url: str = "?sohbet=kapali",
        baslik: str = "AI Abrakadabra",
        not_metni: str | None = None,
    ) -> None:
        self.acik = bool(acik)
        self.mesajlar = self._normalize(mesajlar or [])
        self.ac_url = ac_url
        self.kapat_url = kapat_url
        self.baslik = baslik
        self.not_metni = self.VARSAYILAN_NOT if not_metni is None else not_metni

    @staticmethod
    def _normalize(mesajlar: Iterable[Any]) -> list[tuple[str, str]]:
        """Farklı girdi biçimlerini ``(rol, metin)`` listesine indirger."""
        sonuc: list[tuple[str, str]] = []
        for ham in mesajlar:
            if isinstance(ham, dict):
                rol = str(ham.get("rol", "ai"))
                metin = str(ham.get("metin", ""))
            else:
                rol, metin = str(ham[0]), str(ham[1])
            if rol not in SOHBET_ROLLERI:
                raise BilesenHatasi(
                    f"Geçersiz sohbet rolü: {rol!r}. "
                    f"İzinli roller: {', '.join(sorted(SOHBET_ROLLERI))}"
                )
            sonuc.append((rol, metin))
        return sonuc

    def _fab_html(self) -> str:
        ic = etiket("span", "✨", **{"class": sinif("chat", "fab", "ikon"), "aria-hidden": "true"})
        return etiket(
            "a",
            ic,
            **{
                "class": sinif("chat", "fab"),
                "href": self.ac_url,
                "role": "button",
                "title": f"{self.baslik} — sohbeti aç",
                "aria-label": f"{self.baslik} sohbetini aç",
            },
        )

    def _bas_html(self) -> str:
        baslik = etiket(
            "span",
            f"✨ {guvenli_metin(self.baslik)}",
            **{"class": sinif("chat", "baslik")},
        )
        kapat = etiket(
            "a",
            "✕",
            **{
                "class": sinif("chat", "kapat"),
                "href": self.kapat_url,
                "role": "button",
                "title": "Sohbeti kapat",
                "aria-label": "Sohbeti kapat",
            },
        )
        return etiket("div", baslik + kapat, **{"class": sinif("chat", "bas")})

    def _govde_html(self) -> str:
        if not self.mesajlar:
            ic = etiket(
                "p",
                "Henüz mesaj yok. Panelle ilgili bir soru sorarak başlayın.",
                **{"class": sinif("chat", "bos")},
            )
        else:
            ic = "".join(
                etiket(
                    "div",
                    guvenli_metin(metin),
                    **{
                        "class": sinif_listesi(
                            sinif("chat", "mesaj"),
                            sinif("chat", "mesaj", SOHBET_ROLLERI[rol]),
                        )
                    },
                )
                for rol, metin in self.mesajlar
            )
        return etiket("div", ic, **{"class": sinif("chat", "govde")})

    def _not_html(self) -> str:
        if not self.not_metni:
            return ""
        return etiket(
            "p",
            guvenli_metin(self.not_metni),
            **{"class": sinif("chat", "not")},
        )

    def html(self) -> str:
        if not self.acik:
            return self._fab_html()
        govde = self._bas_html() + self._govde_html() + self._not_html()
        return etiket(
            "section",
            govde,
            **{
                "class": sinif("chat", "panel"),
                "role": "dialog",
                "aria-label": guvenli_metin(self.baslik),
            },
        )
