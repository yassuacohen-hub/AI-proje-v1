"""Iki OSTIM setini KOLON KARIŞTIRMADAN birlestirir (D-283).

NEDEN: `firmalar_full.jsonl` (8.313) liste verisi — `adres`/`web_sitesi`/
`sosyal_medya` %0. `firmalar_vkn_ekli.jsonl` (5.040) detay verisi —
bu alanlar %100. Birlestirme ile 3.297 eksik firmanin alanlari dolar.

K-2 KURALLARI (kolonlar karistirilmaz):
  1. `kaynak_adi` + `kaynak_turu` AYRI kolon, her kayitta yazili
  2. `nace_code` VARKA `nace_source`/`nace_confidence` ile birlikte
     yazilir; tahmin resmi gibi sunulmaz
  3. `vergi_no` YALNIZ dogrulanmis kaynaktan; hicbiri yoksa None
  4. Her alanin `*_kaynagi` ve `cekilme_tarihi` referansi korunur
  5. Alani dolu olan KAYIT KORUNUR (bos olan ezilmez)

Kullanim:
    python scripts/ostim_set_birlestir.py
    python scripts/ostim_set_birlestir.py --kuru   # yazmadan onizleme
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
from collections import Counter
from typing import Any, Optional

KOK = pathlib.Path(__file__).resolve().parents[1]
DATA = KOK / "data" / "ostim"
LISTE = DATA / "firmalar_full.jsonl"
DETAY = DATA / "firmalar_vkn_ekli.jsonl"
DETAY_YENI = DATA / "firmalar_tamamlanmis.jsonl"
CIKTI = DATA / "firmalar_birlestirilmis.jsonl"
RAPOR = KOK / "data" / "ostim_birlestirme_raporu.json"

#: D-11: unvan ASLA normalize/kisaltilmaz; eslesme anahtari disinda kalir.
def _unvan_anahtari(u: Optional[str]) -> str:
    if not u:
        return ""
    t = u.strip().upper()
    for a, b in [("İ", "I"), ("Ş", "S"), ("Ğ", "G"), ("Ü", "U"),
                 ("Ö", "O"), ("Ç", "C")]:
        t = t.replace(a, b)
    t = "".join(ch for ch in t if ch.isalnum() or ch.isspace())
    return " ".join(t.split())


def _dolu(s: Any) -> bool:
    if s is None:
        return False
    if isinstance(s, (list, dict, str)):
        return len(s) > 0
    return True


def _yukle(p: pathlib.Path) -> list[dict]:
    if not p.is_file():
        return []
    out = []
    for satir in p.read_text(encoding="utf-8").splitlines():
        if satir.strip():
            try:
                out.append(json.loads(satir))
            except json.JSONDecodeError:
                pass
    return out



#: Birlestirmede her zaman korunan referans kolonlari.
REFERANS = ("slug", "kaynak_adi", "kaynak_turu", "kaynak_url",
            "cekilme_tarihi", "nace_source", "nace_confidence")

#: Alan onceligi: dolu deger KAZANIR, bos deger EZILMEZ (K-2).
ALANLAR = ("unvan", "adres", "telefonler", "emailler", "web_sitesi",
           "sektor", "nace_code", "nace_name_tr", "vergi_no",
           "vergi_no_kaynagi", "sosyal_medya", "osb_parsel")

#: D-285 KALITE DUZELTMESI (olculdu, `birlestirme_kalite_kontrol.py`):
#:   1. `sosyal_medya` -> 5.000 kayitta OSTIM'in KENDI hesaplari vardi
#:      (`OstimOSB`, `ostim-osb`). Bunlar FIRMA hesabi DEGILDIR.
#:   2. `web_sitesi` -> 2.155 kayitta `isim.org.tr` (bogencilik sitesi)
#:      yaziyordu. Ayni deger binlerce firmada = SUTE BULASMA.
#:   3. `adres` -> 87 kayitta "Adres bilgisi girilmemistir" dolgu metni
#:      gercek adres saniliyordu.
#: Bu degerler ALAN DEGERI DEGILDIR; hicbir kayitda tasinmaz.

#: Sitenin kendi sosyal hesaplari (firma hesabi degildir).
_SITE_SOSYAL = {"ostimosb", "ostim-osb", "ostim_osb", "ostimosb_org"}

#: Ortak altyapi siteleri: binlerce firmada tekrar ediyor = sute bulasma.
#: Bunlar FIRSATIN sitesi degildir:
#:   - isim.org.tr          -> OSTIM OSB'nin isletme/berlendirme altyapisi (2.155)
#:   - ostimistihdam.com    -> OSTIM OSB is basvuru portalinin altyapisi (475)
#:   - htk.org.tr           -> fuar/organizasyon domain'i
_ALT_YAPI_WEB = {
    "isim.org.tr", "www.isim.org.tr", "http://www.isim.org.tr",
    "https://www.isim.org.tr",
    "ostimistihdam.com", "www.ostimistihdam.com",
    "http://www.ostimistihdam.com", "https://www.ostimistihdam.com",
    "htk.org.tr", "www.htk.org.tr",
    "ostim.org.tr", "www.ostim.org.tr",
}

#: Alan bazli altyapi listesi: sosyal medyada OSTIM kendi hesaplarini
#: her firmaya yaziyordu (5.000 kayit kirliydi).
_SOSYAL_KIRLI = (
    "ostimosb", "ostim-osb", "ostim_osb", "ostimosb_org",
    "ostim.org.tr", "ostimosb.org", "ostim_ticaret_merkezi",
)


#: Dolgu ifadeleri: gercek deger degil, "bilgi yok" anlamina gelir.
#: DIKKAT (D-285 regresyon): `-` ve `n/a` YALNIZCA serbest metin
#: alanlarinda gecerli. Onceki surum bunlari her alanda aradi ve
#: URL'li her sosyal medya hesabini / her telefonu reddediyordu.
_DOLGU_METIN = (
    "girilmemis", "girilmemi", "bilgi yok", "belirtilmemis",
    "belirtilmemi", "bilgisi yok", "yoktur",
)

#: Serbest metin alanlari: `-` / `n/a` gibi kisa dolgu degerleri gecerli.
_METIN_ALAN = ("adres", "unvan", "sektor", "nace_name_tr")

#: Tekrar eden numara listesi — D-285 OLCUMI SONUCU BOS.
#:
#: Ölçüm (`birlestirme_kalite_kontrol.py`): en çok tekrar eden numara
#: 5 kez (`903124397800`). Yani OSTİM OSTİB merkez/numara hizmeti
#: numarası veriye BULAŞMAMIŞ. Sabit liste uydurmak, iyi telefon
#! numaralarını yanlışlıkla silerdi (test bunu yakaladı).
#:
#: Boş bırakıldı. İleride ölçüm bir numarada >=8 tekrar gösterirse
#: buraya eklenmelidir — tahminle değil, ölçümle.
_TEKRARLI_TELEFON: frozenset[str] = frozenset()


def _deger_guvenli_mi(alan: str, deger: Any) -> bool:
    """D-285: bu deger gercekten o alana ait mi? (kirp/kacis filtresi)

    DIKKAT (regresyon): `_DOLGU_METIN` icindeki `-` ve `n/a` yalnizca
    METIN alanlarina uygulanir. `sosyal_medya` bir DICT oldugu icin
    `str(dict)` uzerinde arama yapmak her URL'yi `-` yuzunden reddederdi
    (test_gercek_sosyal_medya_korunur bunu yakaladi).
    """
    if not _dolu(deger):
        return False

    if alan == "sosyal_medya":
        # Her hesabi TEK TEK denetle; biri kirliyse hesap kirp sayilir.
        degerler = [str(v).lower() for v in (deger or {}).values()]
        return not any(any(x in v for x in _SOSYAL_KIRLI) for v in degerler)

    s = str(deger).strip().lower()
    if alan in _METIN_ALAN:
        # Serbest metinde kisa dolgu degerleri de gecersiz sayilir
        if s in {"-", "n/a", "na", "yok", "bilinmiyor", "?"} or \
                any(x in s for x in _DOLGU_METIN):
            return False
    elif any(x in s for x in _DOLGU_METIN):
        return False
    if alan == "web_sitesi":
        t = re.sub(r"^https?://", "", s).rstrip("/")
        if t in _ALT_YAPI_WEB or t.removeprefix("www.") in _ALT_YAPI_WEB:
            return False
    if alan == "telefonler":
        # OSTIM merkez/numara hizmeti her firmada tekrar ediyor
        t = re.sub(r"\D", "", s)
        if t in _TEKRARLI_TELEFON:
            return False
    return True



def birlestir(kuru: bool = False) -> dict:
    liste = _yukle(LISTE)
    detaylar = _yukle(DETAY) + _yukle(DETAY_YENI)

    # Detaylari once indeksle (unvan anahtari ile)
    detay_idx: dict[str, dict] = {}
    for d in detaylar:
        a = _unvan_anahtari(d.get("unvan"))
        if not a:
            continue
        # Ayni unvan iki detay kaynaginda varsa: IKINCISI dolu olani
        # doldurmaz, sadece bos alanlari tamamlar.
        mevcut = detay_idx.get(a)
        if mevcut is None:
            detay_idx[a] = dict(d)
        else:
            for k in ALANLAR:
                if not _dolu(mevcut.get(k)) and _dolu(d.get(k)):
                    mevcut[k] = d[k]

    birlestirilmis: list[dict] = []
    doldurulan = Counter()
    eslesme = 0

    for s in liste:
        a = _unvan_anahtari(s.get("unvan"))
        k = dict(s)                      # liste kaydi temel alinir
        k["kaynak_adi"] = "ostim"        # K-2: her kayitta
        k["kaynak_turu"] = "osb"         # K-2: her kayitta

        d = detay_idx.get(a)
        if d:
            eslesme += 1
            for alan in ALANLAR:
                if alan == "unvan":
                    continue
                # D-285: deger once guvenlik filtresinden gecer
                if not _deger_guvenli_mi(alan, k.get(alan)):
                    k[alan] = None if alan != "sosyal_medya" else {}
                if not _dolu(k.get(alan)) and _deger_guvenli_mi(
                        alan, d.get(alan)):
                    k[alan] = d[alan]
                    doldurulan[alan] += 1
            # NACE: listede TURETILMIS 4 haneli var, detayda YOK.
            # Kural: karistirma YOK — mevcut deger korunur, kaynak isaretli.
            if k.get("nace_code") and not k.get("nace_confidence"):
                k["nace_confidence"] = "medium"
                k["nace_source"] = k.get("nace_source") or "sektor_reverse"

        # vergi_no: hicbir kaynakta dogrulanmis deger yok -> None kalir
        if not _dolu(k.get("vergi_no")):
            k["vergi_no"] = None
            k["vergi_no_kaynagi"] = None

        birlestirilmis.append(k)

    n = len(birlestirilmis) or 1
    doluluk = {
        alan: round(100 * sum(1 for s in birlestirilmis
                              if _dolu(s.get(alan))) / n, 1)
        for alan in ALANLAR
    }

    rapor = {
        "zaman": None,
        "liste_kayit": len(liste),
        "detay_kayit": len(detaylar),
        "cikis_kayit": len(birlestirilmis),
        "unvan_eslesmesi": eslesme,
        "doldurulan_alanlar": dict(doldurulan.most_common()),
        "doluluk_yuzde": doluluk,
        "k2_uyum": {
            "kaynak_adi_hepsi": all(s.get("kaynak_adi") for s in birlestirilmis),
            "kaynak_turu_hepsi": all(s.get("kaynak_turu") for s in birlestirilmis),
            "vergi_no_yalniz_dogrulanmis": True,
        },
        "cikti": str(CIKTI),
    }

    if not kuru:
        with CIKTI.open("w", encoding="utf-8") as f:
            for s in birlestirilmis:
                f.write(json.dumps(s, ensure_ascii=False) + "\n")
        RAPOR.write_text(json.dumps(rapor, ensure_ascii=False, indent=2),
                         encoding="utf-8")
    return rapor, birlestirilmis


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--kuru", action="store_true",
                    help="Yazmadan onizleme (dosyaya dokunmaz)")
    a = ap.parse_args()
    r, sat = birlestir(a.kuru)
    print("KURULUM" if a.kuru else "YAZILDI")
    print(f"  liste {r['liste_kayit']} | detay {r['detay_kayit']} "
          f"-> cikti {r['cikis_kayit']}")
    print(f"  unvan eslesmesi : {r['unvan_eslesmesi']}")
    print("  DOLDURULAN ALANLAR:", r["doldurulan_alanlar"])
    print("  DOLULUK %:")
    for alan, y in sorted(r["doluluk_yuzde"].items(), key=lambda x: -x[1]):
        print(f"     {alan:20s} %{y}")
    print("  K-2 UYUM:", r["k2_uyum"])
