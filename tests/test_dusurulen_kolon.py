# -*- coding: utf-8 -*-
"""D-268 mandali: goc 0036'da dusurulen kolonlar uretim koduna geri sizmasin.

NICIN SAYI DEGIL METIN CIVILIYOR: bu iki kolon artik semada YOK. Deger
civilayacak bir sayi kalmadi; civilanacak sey "hicbir uretim yolu bu adi
yazmiyor/okumuyor" iddiasi. Kolon DB'den dustugu icin adi geri gelirse kod
UndefinedColumn ile patlar -- mandal o patlamayi commit aninda one ceker.

Olculen gerekce (goc 0036 basligindan):
  nace_codes.is_manufacturing : 3319/3319 'false' (D-249 sifir bilgi),
                                uretimde okuyan yok.
  companies.nace_name         : 52/9412 dolu, uretim cagirani 2/8289 gorur,
                                degerin 47'si raw_payload->>'sektor'ta durur.

D-259 dersi: mandal yalniz *.py tararsa panel yalani *.js'ten gecer. Bu yuzden
kullaniciya ekran basan her uzanti taranir.

nace_name_tr HEDEF DEGIL: entity_resolution'daki dataclass alanidir, DB kolonu
degil. Bu yuzden kelime siniri (\\b) ile aranir, duz alt dize ile degil.
"""
import re
from pathlib import Path

KOK = Path(__file__).resolve().parents[1]

_DUSENLER = ("is_manufacturing", "nace_name")
_KOKLER = ("src", "scripts", "templates", "web_dashboard", "web_app.py")
_UZANTILAR = ("*.py", "*.js", "*.html", "*.sql")

# Goc dosyalari kolonun tarihini anlatir; onlar arsivdir, ihlal degil.
_MUAF = ("schema/migrations/", "schema\\migrations\\")


def _uretim_dosyalari():
    for kok in _KOKLER:
        p = KOK / kok
        if p.is_file():
            yield p
        elif p.is_dir():
            for desen in _UZANTILAR:
                yield from p.rglob(desen)


def test_dusurulen_kolonlar_uretim_kodunda_yok():
    desen = re.compile(r"\b(" + "|".join(_DUSENLER) + r")\b")
    suclular = []
    for p in _uretim_dosyalari():
        yol = str(p.relative_to(KOK))
        if any(m in yol for m in _MUAF):
            continue
        metin = p.read_text("utf-8", errors="replace")
        for no, satir in enumerate(metin.splitlines(), 1):
            if satir.lstrip().startswith(("#", "--", "//")):
                continue  # D-268 aciklama yorumu ihlal degil
            if desen.search(satir):
                suclular.append(f"{yol}:{no}")
    assert not suclular, (
        "Goc 0036'da dusurulen kolon uretim koduna geri sizdi "
        "(DB'de yok -> calisma aninda UndefinedColumn): " + ", ".join(suclular)
    )
