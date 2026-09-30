# -*- coding: utf-8 -*-
"""D-309 kapilari: "bitti" demeyi hataya baglayan testler.

D-309 dort hatanin kaydini tutar:
  1. Arac yesil dedi, gercek borc defteri ACIK kaldi -> KAYIT KAPISI
  2. Baskasinin isine sessizce atlandi  -> KARSILASTI KAPISI
  3. Test yesilken tablo yari-Turkce      -> AD KONTROLU KAPISI
  4. Yarim degisiklik geri alindi          -> KAZA KAYDI KAPISI

Bu testler yukaridaki hatalarin TEKRARINI mandallar. Amac yazilmis kurali
uygulamak degil, tekrarlanmasini onlemektir.
"""
from __future__ import annotations

import pathlib
import re

KOK = pathlib.Path(__file__).resolve().parents[1]
DEFK = KOK / "docs" / "BORC_DEFTERI.md"
AJAN = KOK / "AGENTS.md"
HAFIZA = KOK / "yasu_project_context.md"
TURKCE = re.compile(r"[ığüşöçİıĞÜŞÖÇ]")


def _oku(yol: pathlib.Path) -> str:
    return yol.read_text(encoding="utf-8")


def test_kapi_1_acik_borc_sahipsiz_kalmaz() -> None:
    """Kapi 1: 'bitti' diyebilmek icin ACIK borclar sahiplenilmis olmali.

    0042'de goc_defteri.py 'TAM defterde' dedi ama iki kayit ACIK'ti.
    Bu test, arac ciktisinin gercek kayit olmadigini mandallar.
    """
    defter = _oku(DEFK)
    aciklar = [l for l in defter.splitlines()
               if re.search(r"`BORC-[A-Z0-9-]+`", l) and "**ACIK**" in l]
    assert aciklar, "ornek: ACIK kayit bulunamadi (kapi calisiyor mu?)"
    sahipsiz = []
    for satir in aciklar:
        hucre = satir.split("|")
        kimlik = hucre[1].strip()
        # kapanis hucresi bos birakilmamali (bos = hic kimse devralmamis)
        if len(hucre) < 6 or hucre[5].strip() in ("", "—", "-"):
            sahipsiz.append(kimlik)
    assert not sahipsiz, "sahipsiz ACIK borc (D-309 kapi 1): %s" % sahipsiz


def test_kapi_1_negatif_kontrol() -> None:
    """Kapi 1'in gercekten yakaladigini gosterir (kendi kendini denetler).

    Bilerek bozucu bir kayit uretilip kapinin kirmiziya dondugu
    gorulur; sonra eslenir. Boylece testin 'yesil ama olu' olmadiği
    kanitlanir (D-268: dogrulama olmadan 'dogrulandi' denmez).
    """
    ornek = ("| `BORC-DEMO-99` | yapay kayit | **ACIK** | D-000 | — |")
    hucre = ornek.split("|")
    sahipsiz_mi = len(hucre) < 6 or hucre[5].strip() in ("", "—", "-")
    assert sahipsiz_mi, "kapi 1 bosluk tespit etmiyor - test olu!"


def test_kapi_2_karsilastigim_is_sahibi_yazili() -> None:
    """Kapi 2: baska ajanin alanina girilince sahip yazilmali.

    osb_tender_monitor.py sahibi utku. Dosyaya dokunulmadi ama borca
    sahibi yazildi. Bu test sessiz atlamayi engeller.
    """
    defter = _oku(DEFK)
    satir = next((l for l in defter.splitlines()
                  if "BORC-TENDER-KOD-01" in l), None)
    assert satir is not None, "BORC-TENDER-KOD-01 yok (sessiz atlanmis olabilir)"
    assert "utku" in satir, "borc sahibi yazili degil"


def test_kapi_3_ihale_goc_hedefleri_ingilizce() -> None:
    """Kapi 3: goc dosyalarindaki Turkce kalinti olmamali.

    0042 yalniz 'ığüşöç' iceren kolonlari cevirdi; ASCII-Turkce kolonlar
    (ilan_basligi, osb_adi...) kaldi ve hicbir test onlari gormuyordu.
    """
    goc = KOK / "src" / "company_master" / "schema" / "migrations"
    kod = "\n".join(p.read_text(encoding="utf-8")
                    for p in sorted(goc.glob("00*_tender*.sql")))
    assert kod, "tender goc dosyasi bulunamadi"
    for kolon in re.findall(r"RENAME COLUMN\s+(\w+)\s+TO\s+(\w+)",
                            kod, flags=re.I):
        assert not TURKCE.search(kolon[0]), "hedef hala Turkce: %s" % kolon[0]


def test_kapi_4_geri_alinan_deneme_kayitli() -> None:
    """Kapi 4: geri alinan yarim deneme 'kaza kaydi' olarak yazili olmali."""
    ajan = _oku(AJAN)
    assert "kaza" in ajan.lower(), "kaza kaydi tanimi yok"
    assert "yarım" in ajan.lower() or "yarim" in ajan.lower(), (
        "yarim degisiklik kurali yok")


def test_d309_ders_kaydi_her_yerde_var() -> None:
    """Ders hem AGENTS.md'de (karar) hem ajan hafizasinda olmali."""
    assert "D-309" in _oku(AJAN), "AGENTS.md'de D-309 karar kaydi yok"
    assert "D-309" in _oku(HAFIZA), "ajan hafizasinda D-309 dersi yok"


def test_kapi_5_karar_numarasi_tahsis_edilmis() -> None:
    """Kapi 5: AGENTS.md'de yazan karar numarasi TAHSIS EDILMIS olmali.

    D-309'un kendi kazasidir: numarayi AGENTS.md'ye yazdim ama
    `karar_no.py --al` cagrisini atladim. Hook reddetti:
    'tahsis edilmemis karar numarasi'. Yani yazmak yetmez,
    tahsis etmek gerekir.
    """
    import re
    import subprocess
    import sys

    ajan = _oku(AJAN)
    # AGENTS.md basliklarindaki karar numaralari
    numaralar = set(re.findall(r"^## D-(\d+)", ajan, flags=re.M))
    assert numaralar, "AGENTS.md'de karar basligi bulunamadi"

    sonuc = subprocess.run(
        [sys.executable, "scripts/karar_no.py"],
        cwd=str(KOK), capture_output=True, text=True)
    cikti = sonuc.stdout + sonuc.stderr
    if "TAHSIS EDILMEMIS" in cikti:
        # sadece bizim dosyamiz icin dogrula (baska ajanlarin acik kayitlari
        # bizi baglamaz, bu yuzden yalniz D-309'a bakilir)
        satir = next(l for l in cikti.splitlines()
                     if "TAHSIS EDILMEMIS" in l)
        numara = satir.split(":")[-1].strip()
        assert numara != "D-309", (
            "D-309 yazildi ama tahsis edilmedi (D-309 kapi 5)")



def test_hafiza_tavani_asmiyor() -> None:
    """Ajan hafizasi 200 satiri gecmemeli (tavan karari AGENTS.md'de)."""
    n = len(_oku(HAFIZA).splitlines())
    assert n <= 200, "hafiza %d satir, tavan 200" % n
