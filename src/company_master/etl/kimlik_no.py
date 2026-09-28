# -*- coding: utf-8 -*-
"""Vergi kimlik numarasi dogrulama (K-6).

Kural (urun sahibi, 2026-09-27):
- **10 hane** -> tuzel kisi VKN (sirket). GIB saglama algoritmasi ile dogrulanir.
- **11 hane** -> gercek kisi / sahis isletmesi; TCKN vergi numarasi yerine gecer.
  TCKN saglama algoritmasi ile dogrulanir.
- Bu ikisi disinda hicbir sey vergi numarasi degildir. Uzunlugu tutan ama
  saglamasi tutmayan deger de vergi numarasi **degildir** (D-245: doluluk != gecerlilik).

Kullanim tek kapidir: kaziyici/ETL kendi regex'i ile vergi no uretmez,
`kimlik_dogrula()` cagirir ve donen turu kaydeder.
"""

from __future__ import annotations

import re

# ponytail: GIB/NVI cevrimici dogrulamasi yok, sadece saglama toplami.
# Numaranin gercekten o firmaya ait oldugunu kanitlamaz; adi eslestirme
# gerektiginde mersis_api.GIBVKNProvider yolu acilir.

__all__ = [
    "kimlik_dogrula",
    "vkn_gecerli",
    "tckn_gecerli",
    "sicil_dogrula",
    "mersis_dogrula",
    "mersis_metinden_bul",
]

# 16 hane, aralarda ayirici (bosluk/tire/nokta) olabilir. Web sitelerinde
# "MERSIS No: 0310-2014-1740-1234" gibi bloklu yazim yaygin.
_MERSIS_ADAY = re.compile(r"(?:\d[\s.\-]?){15}\d")

# Ardisik rakam dizileri; icinde gecen her alt dizi sahte sayilir.
_ARDISIK = ("01234567890123456789", "98765432109876543210")


def _sahte_kalip(v: str) -> bool:
    """Saglamayi gecse bile gerceklikte tahsis edilmeyen kaliplar.

    Kural (urun sahibi, 2026-09-28): ``11111111111`` / ``12345678901`` gibi
    degerler dolgu/test verisidir, gercek kimlik degildir. Saglama toplami
    bunlarin bir kismini eler ama hepsini elemez; kalip sinifi ayrica kapatilir
    (D-245: doluluk != gecerlilik).
    """
    return len(set(v)) == 1 or any(v in d for d in _ARDISIK)


def vkn_gecerli(v: str) -> bool:
    """10 haneli tuzel kisi VKN saglama toplami (GIB algoritmasi)."""
    if len(v) != 10 or not v.isdigit():
        return False
    toplam = 0
    for i in range(9):
        gecici = (int(v[i]) + 9 - i) % 10
        if gecici == 9:
            toplam += gecici
        else:
            toplam += (gecici * 2 ** (9 - i)) % 9
    return (10 - toplam % 10) % 10 == int(v[9])


def tckn_gecerli(v: str) -> bool:
    """11 haneli TC kimlik numarasi saglama toplami (gercek kisi / sahis isletmesi)."""
    if len(v) != 11 or not v.isdigit() or v[0] == "0":
        return False
    d = [int(c) for c in v]
    tekler = d[0] + d[2] + d[4] + d[6] + d[8]
    ciftler = d[1] + d[3] + d[5] + d[7]
    if (tekler * 7 - ciftler) % 10 != d[9]:
        return False
    return sum(d[:10]) % 10 == d[10]


def kimlik_dogrula(deger: str | None) -> tuple[str | None, str]:
    """Ham degeri vergi kimligi olarak dogrular.

    Donus: (normalize_no, tur). `tur` degerleri: ``vkn``, ``tckn``, ``gecersiz``.
    Gecersizde no ``None`` doner - cagiran taraf degeri vergi_no kolonuna **yazmaz**.
    """
    if not deger:
        return None, "gecersiz"
    temiz = "".join(c for c in str(deger) if c.isdigit())
    if _sahte_kalip(temiz):
        return None, "gecersiz"
    if vkn_gecerli(temiz):
        return temiz, "vkn"
    if tckn_gecerli(temiz):
        return temiz, "tckn"
    return None, "gecersiz"


def sicil_dogrula(deger: str | None) -> tuple[str | None, str | None]:
    """Ticaret sicil numarasini dogrular ve sicil dairesini ayirir.

    Vergi numarasindan **bagimsiz** bir kimliktir; VKN'nin yedegi degildir.
    Ikisi ayni anda dolu olabilir (D-246 / K-3: bir kolon bir anlam).

    Olculen bicim (620 ham kayit, aso.org.tr 592 + ostim.org.tr 28):
      - tiresiz: 4-6 haneli rakam    (595 kayit)  -> ("211168", None)
      - tireli:  3-4 hane + "-" + ilce sicil dairesi (25 kayit) -> ("623", "KAZAN")
    Bu yuzden kabul araligi 3-6 hane. 10/11 hane KABUL EDILMEZ: vergi
    numarasinin sicil kolonuna sizmasini engeller (K-3: bir kolon bir anlam).

    Donus: (sicil_no, sicil_dairesi). Gecersizde (None, None).

    ponytail: sicil dairesi ham metin olarak saklanir; "BEYP." ile "BEYPAZARI"
    ayri deger kalir (1 kayit). Daire bazli gruplama istenirse ilce sozlugu ekle.
    """
    if not deger:
        return None, None
    ham = str(deger).strip()
    no, _, daire = ham.partition("-")
    no = no.strip()
    daire = daire.strip().rstrip(".").upper() or None
    if not (no.isdigit() and 3 <= len(no) <= 6):
        return None, None
    return no, daire


def mersis_dogrula(deger: str | None) -> tuple[str | None, str | None]:
    """MERSIS numarasini dogrular ve icindeki VKN'yi cikarir.

    Kural (urun sahibi, 2026-09-28): tuzel kisilerde 16 haneli MERSIS
    numarasinin **ilk 10 hanesi VKN'dir**. Yani VKN ikinci bir kaynak
    sorgusuyla toplanmaz, aritmetikle turetilir:

        0123456789 01234
        |-- VKN --|

    Bu ayni zamanda karsilikli denetimdir: ilk 10 hane VKN saglamasini
    tutmuyorsa MERSIS numarasi yanlis okunmus demektir. Bu yuzden gecersiz
    VKN iceren 16 hane KABUL EDILMEZ (D-245: doluluk != gecerlilik).

    Donus: (mersis_no, vkn). Gecersizde (None, None).

    UYARI - yalnizca tuzel kisi. Sahis isletmelerinde kimlik TCKN'dir (11 hane)
    ve MERSIS'in ilk 10 hanesinden turetilemez. Cagiran taraf donen vkn'yi
    yalnizca tuzel_tip == "tuzel" oldugunda yazar.
    """
    if not deger:
        return None, None
    temiz = "".join(c for c in str(deger) if c.isdigit())
    if len(temiz) != 16:
        return None, None
    if not vkn_gecerli(temiz[:10]):
        return None, None
    return temiz, temiz[:10]


def mersis_metinden_bul(metin: str | None) -> str | None:
    """Web sitesi / kunye metninden MERSIS numarasi hasat eder.

    Urun sahibi gozlemi (2026-09-28): sirketlerin cogu MERSIS numarasini
    kendi web sitesinde (kunye, iletisim, sozlesme sayfalari) yayinlar.
    Elimizde 5449 web sitesi var; MERSIS portalina gitmeden once burasi bakilir.

    Yanlis pozitif korumasi: 16 haneli her sayi MERSIS degildir (IBAN parcasi,
    tarih+telefon birlesmesi, siparis no...). Aday yalnizca ilk 10 hanesi
    **gecerli VKN** ise kabul edilir - saglama, hasadin filtresidir.

    Donus: normalize 16 haneli MERSIS no, yoksa None.

    ponytail: ilk gecerli adayi doner, coklu aday ayiklamaz. Bir sayfada birden
    cok MERSIS cikarsa (ornegin grup sirketleri kunyesi) hepsini isteyen cagiran
    _MERSIS_ADAY.finditer dongusunu kendi yazar.
    """
    if not metin:
        return None
    for eslesme in _MERSIS_ADAY.finditer(str(metin)):
        no, _ = mersis_dogrula(eslesme.group())
        if no:
            return no
    return None


if __name__ == "__main__":
    # Mandal: gercek olcum verisinden ornekler (2026-09-27, companies tablosu).
    assert kimlik_dogrula("3102014174") == ("3102014174", "vkn")
    assert kimlik_dogrula("11113191042") == ("11113191042", "tckn")
    assert kimlik_dogrula("51692509524") == ("51692509524", "tckn")

    # Kaziyici regex'inin urettigi cop: 11 hane ama hicbir saglamayi tutmuyor.
    assert kimlik_dogrula("71788429969") == (None, "gecersiz")
    assert kimlik_dogrula("13102014174") == (None, "gecersiz")  # basta fazla rakam

    # Uzunluk sinirlari ve bicim
    assert kimlik_dogrula("") == (None, "gecersiz")
    assert kimlik_dogrula(None) == (None, "gecersiz")
    assert kimlik_dogrula("123") == (None, "gecersiz")
    assert kimlik_dogrula("01234567890") == (None, "gecersiz")  # TCKN 0 ile baslamaz

    # Sahte kalip: saglamayi gecse bile gercek kimlik degil (urun sahibi, 2026-09-28).
    # Bu ikisi companies tablosunda gercekten duruyordu.
    assert kimlik_dogrula("12345678901") == (None, "gecersiz")  # ardisik
    assert kimlik_dogrula("99999999999") == (None, "gecersiz")  # tek rakam
    assert kimlik_dogrula("1111111111") == (None, "gecersiz")  # 10 hane tek rakam
    assert kimlik_dogrula("9876543210") == (None, "gecersiz")  # ters ardisik
    assert kimlik_dogrula("3102014174 ")[1] == "vkn"  # bosluk/ayirici tolere edilir
    assert kimlik_dogrula("310-201-4174")[1] == "vkn"

    # --- sicil: gercek ham veriden (source_records.raw_payload.ticaretSicilNo) ---
    assert sicil_dogrula("211168") == ("211168", None)
    assert sicil_dogrula("623-KAZAN") == ("623", "KAZAN")      # daire ayrilir
    assert sicil_dogrula("1105-BEYP.") == ("1105", "BEYP")     # sondaki nokta atilir
    assert sicil_dogrula("501-NALLIHAN") == ("501", "NALLIHAN")
    assert sicil_dogrula("9999") == ("9999", None)
    assert sicil_dogrula("623") == ("623", None)               # 3 hane alt sinir
    # Vergi numarasi sicil kolonuna sizmaz (asil koruma):
    assert sicil_dogrula("3102014174") == (None, None)         # 10 hane VKN
    assert sicil_dogrula("11113191042") == (None, None)        # 11 hane TCKN
    assert sicil_dogrula("12") == (None, None)                 # 2 hane: alt sinir alti
    assert sicil_dogrula("1234567") == (None, None)            # 7 hane: ust sinir ustu
    assert sicil_dogrula("") == (None, None)
    assert sicil_dogrula(None) == (None, None)
    # Sicil de vergi kolonuna sizmaz (ters yon):
    assert kimlik_dogrula("211168") == (None, "gecersiz")

    # --- mersis: ilk 10 hane = VKN (urun sahibi kurali, 2026-09-28) ---
    # 3102014174 gercek veriden gelen gecerli VKN; sonuna 6 hane eklenmis.
    assert mersis_dogrula("3102014174012345") == ("3102014174012345", "3102014174")
    assert mersis_dogrula("1111111110012345") == (None, None)   # ilk 10 gecersiz VKN
    assert mersis_dogrula("310201417401234") == (None, None)    # 15 hane
    assert mersis_dogrula("31020141740123456") == (None, None)  # 17 hane
    assert mersis_dogrula("3102014174") == (None, None)         # VKN tek basina MERSIS degil
    assert mersis_dogrula("") == (None, None)
    assert mersis_dogrula(None) == (None, None)
    # Ayirici tolere edilir (web sitelerinde "0310-2014-1740-1234" gibi yazilir):
    assert mersis_dogrula("3102-0141-7401-2345")[1] == "3102014174"

    # --- mersis_metinden_bul: web sitesi metninden hasat ---
    assert mersis_metinden_bul("MERSIS No: 3102014174012345") == "3102014174012345"
    assert mersis_metinden_bul("Mersis: 3102-0141-7401-2345") == "3102014174012345"
    assert mersis_metinden_bul("Tel: 03123456789 Faks: 03123456780") is None
    assert mersis_metinden_bul("") is None
    # Gecersiz VKN iceren 16 hane hasat edilmez (telefon/IBAN parcasi olabilir):
    assert mersis_metinden_bul("1111111110012345") is None

    print("kimlik_no: tum mandallar gecti")
