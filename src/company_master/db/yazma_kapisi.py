# -*- coding: utf-8 -*-
"""Veri yazma kapisi: sabloni DB'ye girmeden reddeder (D-303).

Olcum (D-303): `companies` icinde 2666 kayitta website_domain sablon
(`isim.org.tr` vb.). Hepsi **tek kaynaktan** geldi: `ostim.org.tr` / web_scrape.
Kok sebep filtre eksikligi degil, **kanonik liste yoklugu**: ayni sablon listesi
23 dosyada 5 ayri isimle (GENERIC, PLACEHOLDER_DOMAINS, skip_domains,
WEB_BLOCKLIST, _ALT_YAPI_WEB) kopyalanmisti; kopyalar birbirinden sapti.

Burasi tek liste ve tek kapidir. Yeni sablon buraya yazilir, hicbir yere kopyalanmaz.

    from company_master.db.yazma_kapisi import sablon_mu, temizle, kabul

ponytail: kapi cagrilan yazma yollarini korur; D-303 olcumunde 58 bagimsiz
baglanti / 79 dosya SQL yaziyor. Yukseltme yolu: en cok yalan ureten yoldan
baslayarak her yazma yolu bu kapidan gecirilir (sira BORC_DEFTERI'nde).
"""
from __future__ import annotations

import re

# Kanonik sablon degerler. Alan adi SINIRINDA aranir: solunda harf/rakam/tire
# olamaz (protokol/www/slash farketmez). Duz alt dizgi `wixsite.com`,
# `epsiloncomposite.com` gibi gercek alanlari yakaliyordu (olcum 2026-10-04: 4 satir).
SABLON_WEB = (
    "isim.org.tr",
    "osp.com.tr",
    "ostimonline.com",
    "ostimistihdam.com",
    "example.com",
    "site.com",
    "domain.com",
)
SABLON_EPOSTA = (
    "isim@", "ornek@", "example@", "test@", "info@isim", "mail@mail",
)
def desen(liste: tuple[str, ...] = SABLON_WEB) -> str:
    """POSIX ERE + Python `re` ortak desen; goc 0052 trigger'i AYNI dizgiyi kullanir
    (mandal: tests/test_website_sablon_kisiti.py)."""
    return "(^|[^a-z0-9-])(" + "|".join(x.replace(".", r"\.") for x in liste) + ")"


SABLON_WEB_DESEN = desen()

# Yokluk 0 degildir, bostur (D-249): bu degerler "bilgi" sayilmaz.
BOS_SAYILAN = ("", "-", "--", "yok", "bilinmiyor", "n/a", "na", "null", "none", "0")


def temizle(deger: str | None) -> str | None:
    """Bosluk kirp; bos sayilan degerleri None'a cevir (D-249)."""
    if deger is None:
        return None
    s = str(deger).strip()
    return None if s.lower() in BOS_SAYILAN else s


def sablon_mu(deger: str | None, liste: tuple[str, ...] = SABLON_WEB) -> bool:
    """Deger kanonik sablonlardan birini alan adi sinirinda iceriyor mu."""
    s = temizle(deger)
    return bool(s) and re.search(desen(liste), s.lower()) is not None


def kabul(kayit: dict) -> tuple[dict, list[str]]:
    """Yazilacak kaydi kapidan gecirir: (temiz_kayit, ret_sebepleri).

    - Sablon web/eposta **yazilmaz**: alan None'a dusurulur, sebep raporlanir.
    - Bos sayilan degerler None olur (yokluk 0 degil, bos).
    - Koken zorunlu: `source_record_id` yoksa ret sebebi yazilir (D-287:
      dogrulanmamis veri dogrulanmis gibi puanlanmaz).
    Veri SILINMEZ, yalnizca yazilmaz/isaretlenir — silme urun sahibindedir.
    """
    temiz, sebep = dict(kayit), []
    for alan, liste in (("website_domain", SABLON_WEB),
                        ("primary_email", SABLON_EPOSTA)):
        if alan in temiz:
            if sablon_mu(temiz[alan], liste):
                sebep.append(f"{alan}: sablon deger reddedildi ({temiz[alan]})")
                temiz[alan] = None
            else:
                temiz[alan] = temizle(temiz[alan])
    for alan in temiz:
        if isinstance(temiz[alan], str):
            temiz[alan] = temizle(temiz[alan])
    if not temiz.get("source_record_id"):
        sebep.append("koken yok: source_record_id bos (D-287)")
    return temiz, sebep


if __name__ == "__main__":  # kirarak dogrulama (D-288)
    t, s = kabul({"website_domain": "http://www.isim.org.tr",
                  "primary_email": " ", "address": "yok",
                  "source_record_id": None})
    assert t["website_domain"] is None, t
    assert t["primary_email"] is None, t
    assert t["address"] is None, t
    assert len(s) == 2, s
    t2, s2 = kabul({"website_domain": "https://gercekfirma.com.tr",
                    "source_record_id": "x"})
    assert t2["website_domain"] == "https://gercekfirma.com.tr", t2
    assert s2 == [], s2
    assert not sablon_mu("https://enerjilastik.wixsite.com"), "sinir: wixsite gercek"
    assert sablon_mu("x.osp.com.tr") and sablon_mu("HTTP://WWW.ISIM.ORG.TR")
    print("yazma_kapisi: kapi calisiyor")
