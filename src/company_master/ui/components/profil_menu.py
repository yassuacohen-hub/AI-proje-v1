# -*- coding: utf-8 -*-
"""ADMIN-UX-PROFILMENU-01: Sağ-alt admin profil popover (ProfileMenu).

İçerik: kullanıcı adı, rol, "Ayarlar" deep-link, "Çıkış" butonu.
Çıkış butonu `web_dashboard.tabs.admin_auth.admin_cikis()` çağırır.
İkon monokrom (renk yok, tek ton). Mevcut `styles.py` sınıflarını kullan.
"""
from __future__ import annotations

from typing import Any

from company_master.ui.base import (
    Bilesen,
    BilesenHatasi,
    etiket,
    guvenli_metin,
    sinif,
    sinif_listesi,
)

from web_dashboard.tabs.admin_auth import admin_cikis


class ProfileMenu(Bilesen):
    """Sağ-alt admin profil popover bileşeni.

    Args:
        kullanici_adi: Görünen kullanıcı adı.
        rol: Kullanıcı rolü (örn. "admin", "editor").
        acik: Popover açık mı?
        ayarlar_url: "Ayarlar" linkinin hedefi (deep-link).
        cikis_url: Çıkış butonunun hedefi (admin_cikis tetikler).
    """

    def __init__(
        self,
        kullanici_adi: str,
        rol: str = "admin",
        *,
        acik: bool = False,
        ayarlar_url: str = "?sayfa=ayarlar",
        cikis_url: str = "?cikis=1",
    ) -> None:
        if not str(kullanici_adi).strip():
            raise BilesenHatasi("Kullanıcı adı boş olamaz")
        self.kullanici_adi = str(kullanici_adi)
        self.rol = str(rol)
        self.acik = bool(acik)
        self.ayarlar_url = ayarlar_url
        self.cikis_url = cikis_url

    def _avatar_html(self) -> str:
        """Monokrom avatar (baş harf)."""
        harf = self.kullanici_adi.strip()[0].upper()
        return etiket(
            "div",
            guvenli_metin(harf),
            **{"class": sinif_listesi(sinif("profil", "avatar"), sinif("profil", "avatar-monokrom"))},
        )

    def _bilgi_html(self) -> str:
        """Kullanıcı adı + rol."""
        return (
            etiket(
                "div",
                guvenli_metin(self.kullanici_adi),
                **{"class": sinif("profil", "ad")},
            )
            + etiket(
                "div",
                guvenli_metin(self.rol),
                **{"class": sinif("profil", "rol")},
            )
        )

    def _ayarlari_html(self) -> str:
        """Ayarlar deep-link butonu."""
        return etiket(
            "a",
            "⚙️ Ayarlar",
            **{
                "class": sinif_listesi(
                    sinif("profil", "link"),
                    sinif("btn", "ghost"),
                    sinif("btn", "sm"),
                ),
                "href": self.ayarlar_url,
                "role": "button",
                "title": "Kullanıcı ayarlarını aç",
            },
        )

    def _cikis_html(self) -> str:
        """Çıkış butonu (admin_cikis tetikler)."""
        return etiket(
            "a",
            "🚪 Çıkış",
            **{
                "class": sinif_listesi(
                    sinif("profil", "link"),
                    sinif("btn", "danger"),
                    sinif("btn", "sm"),
                ),
                "href": self.cikis_url,
                "role": "button",
                "title": "Oturumu kapat",
            },
        )

    def html(self) -> str:
        """Popover HTML'i üretir."""
        if not self.acik:
            return ""

        govde = (
            etiket(
                "div",
                self._avatar_html() + self._bilgi_html(),
                **{"class": sinif("profil", "ust")},
            )
            + etiket(
                "div",
                self._ayarlari_html() + self._cikis_html(),
                **{"class": sinif("profil", "aksiyonlar")},
            )
        )

        return etiket(
            "div",
            govde,
            **{
                "class": sinif_listesi(
                    sinif("profil", "popover"),
                    sinif("card"),
                ),
                "role": "menu",
                "aria-label": f"{self.kullanici_adi} profil menüsü",
            },
        )

    def streamlit(self, container: Any | None = None) -> None:
        """Streamlit'ta popover çizer (HTML tabanlı)."""
        if not self.acik:
            return
        hedef = container
        if hedef is None:
            import streamlit as st
            hedef = st
        hedef.markdown(self.html(), unsafe_allow_html=True)


def render_profil_menu(
    kullanici_adi: str,
    rol: str = "admin",
    *,
    acik: bool = False,
    ayarlar_url: str = "?sayfa=ayarlar",
    cikis_url: str = "?cikis=1",
) -> ProfileMenu:
    """Kullanım kolaylığı için yardımcı fonksiyon.

    ProfilMenu bileşeni oluşturur ve döndürür. Çağıran `.streamlit()` veya `.html()` çağırır.
    """
    return ProfileMenu(
        kullanici_adi=kullanici_adi,
        rol=rol,
        acik=acik,
        ayarlar_url=ayarlar_url,
        cikis_url=cikis_url,
    )
