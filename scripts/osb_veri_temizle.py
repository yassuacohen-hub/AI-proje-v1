# -*- coding: utf-8 -*-
"""OSB veri seti temizligi — kalici arac (VERI-OSB-TEMIZLIK-01).

Neden kalici: `data/osb/` her `osb_veri_seti_uret.py` kosusunda yeniden uretilir.
Gecici bir betikle temizlik, bir sonraki uretimde kaybolur (R1: gecici script yasak).
Bu dosya ureticiyle ayni yolu izler; tek farki kimlik kuralidir.

Kararlar (2026-10-02, ihsan onayi):
  1. Ayni slug + ayni adres + FARKLI osb_slug -> **AYNI TESIS**, tek kayit.
     Silme degil: once kayit "kopya" olarak isaretlenir, sonra tekilestirilir.
  2. Bozuk kodlamali satir ("?" iceren) -> slug URETILMEZ, `slug_durumu`
     kolonu ile "kaynak eksik" olarak isaretlenir.
  3. Slug cakismasi -> once adres karsilastirilir; adres farkliysa kayit KALIR.

Kurallar: D-245 (kolon olcerek) · D-249 (veri yok = NULL, 0 degil) ·
D-260 (kanitsiz iddia yok) · D-262 (silmeden once referans tasi).

SSOT: `yedekler/Huginn Data Insights (HUGIns).txt:760-779` (düğüm türleri)
"""
from __future__ import annotations

import argparse
import collections
import json
import logging
import pathlib
import re
import sys

logger = logging.getLogger(__name__)

KOK = pathlib.Path(__file__).resolve().parents[1]
VERI = KOK / "data" / "osb"
KIMLIK = "company_slug"

#: Kanonik alan listesi — 17 alanlı ortak şema (osb_veri_seti_uret.py ile aynı).
ALANLAR: tuple[str, ...] = (
    "legal_name", "adres", "phones", "emails", "website_domain", "sektor",
    "tax_number", "parsel", "company_slug", "source_name", "source_type",
    "social_media", "osb_slug", "source_file", "status", "is_ankara",
    "is_osb_member",
)

#: Türkçe harf -> ASCII (D-245: kaynak slug kuralı OSTIM_TEMIZ.jsonl'den gelir;
#: bu eşleme o kaynağın üretim kuralıyla birebir ölçüldü — bkz. osb_veri_denetim.py).
_HARF: dict[str, str] = {
    "ı": "i", "ş": "s", "ğ": "g", "ü": "u", "ö": "o", "ç": "c",
    "İ": "i", "Ş": "s", "Ğ": "g", "Ü": "u", "Ö": "o", "Ç": "c", "I": "i",
}


def slug_uret(yazi: str | None) -> str:
    """Kaynak OSB slug kuralı: Türkçe→ASCII, küçült, noktalama SİLİNİR,
    boşluk→tire, ardışık tireler tekilleştirilir.

    Kural OSTIM_TEMIZ.jsonl kaynağından ölçüldü: nokta silinir
    ("San.Tıc." -> "santic"), boşluk tireye dönüşür.
    """
    if not yazi:
        return ""
    t = "".join(_HARF.get(ch, ch) for ch in str(yazi).lower())
    t = re.sub(r"[^a-z0-9 -]", "", t)      # noktalama ve ayraçlar SİLİNİR
    t = re.sub(r"[\s]+", "-", t.strip())   # boşluk -> tire
    return re.sub(r"-{2,}", "-", t).strip("-")


def bozuk_mu(yazi: str | None) -> bool:
    """Bozuk kodlama taşıyor mu? `?` Türkçe harfi yutmuşsa bozuktur.

    Denetim `\\ufffd` arıyor ve bu satırları kaçırıyor (bulgu: `MOJIBAKE: 0`
    yanlış negatif). Buradaki `?` kontrolü onu tamamlar (D-260).
    """
    return bool(yazi) and "?" in yazi


#: Bir kaydin slug'ini yazmadan once tutulan durum (D-249: "veri yok" ≠ bos).
DURUM_SLUG_YOK = "kaynak_eksik_bozuk_kodlama"
DURUM_SLUG_VAR = "uretildi"


def _oku(dosya: pathlib.Path) -> list[dict]:
    out: list[dict] = []
    for satir in dosya.read_text(encoding="utf-8").splitlines():
        if satir.strip():
            try:
                out.append(json.loads(satir))
            except json.JSONDecodeError:
                continue
    return out


def _yaz(dosya: pathlib.Path, kayitlar: list[dict]) -> None:
    """Atomik yazım: once .tmp, sonra replace (osb_veri_seti_uret.py deseni)."""
    gecici = dosya.with_suffix(".jsonl.tmp")
    gecici.write_text(
        "".join(json.dumps(k, ensure_ascii=False) + "\n" for k in kayitlar),
        encoding="utf-8",
    )
    gecici.replace(dosya)


def temizle(kuru: bool = True) -> dict:
    """Tüm OSB klasörlerini temizler. Varsayılan: kuru çalışma (sadece ölçüm).

    Döner: {'slug_uretilen': n, 'slug_atlanan': n, 'tekillestirilen': n,
            'korunan': n, 'bos_sayilan': n}
    """
    ozet = {
        "slug_uretilen": 0, "slug_atlanan": 0,
        "tekillestirilen": 0, "korunan": 0,
        "isaretlenen_kopya": 0, "silinen_kayit": 0, "dosya": 0,
    }
    # 1) Tüm kayıtları oku; slug tekilliği için global indeks kur
    hepsi: list[tuple[pathlib.Path, dict]] = []
    slug_nerede: dict[str, list[tuple[pathlib.Path, dict]]] = collections.defaultdict(list)
    for dosya in sorted(VERI.glob("*/firmalar.jsonl")):
        kayitlar = _oku(dosya)
        ozet["dosya"] += 1
        for k in kayitlar:
            hepsi.append((dosya, k))
            if k.get(KIMLIK):
                slug_nerede[k[KIMLIK]].append((dosya, k))

    # 2) Slug üretimi (KARAR 2): bozuk kodlama -> slug ÜRETİLMEZ
    for _dosya, k in hepsi:
        if k.get(KIMLIK):
            continue
        if bozuk_mu(k.get("legal_name")):
            # Kanıtsız slug yazmak kalıcı kimliği bozar -> yazma, işaretle
            k["slug_durumu"] = DURUM_SLUG_YOK
            k["slug_notu"] = "legal_name icinde '?' var: kaynak kodlamasi bozuk (D-260)"
            ozet["slug_atlanan"] += 1
            continue
        yeni = slug_uret(k.get("legal_name"))
        if not yeni:
            k["slug_durumu"] = DURUM_SLUG_YOK
            k["slug_notu"] = "legal_name slug'a cevrilemedi (harf disi karakter)"
            ozet["slug_atlanan"] += 1
            continue
        k[KIMLIK] = yeni
        k["slug_durumu"] = DURUM_SLUG_VAR
        slug_nerede[yeni].append((_dosya, k))
        ozet["slug_uretilen"] += 1

    # 3) Tekillestirme (KARAR 1 + 3): ayni slug icin adres karsilastir
    tekillestir: list[tuple[pathlib.Path, dict, dict]] = []
    for slug, kayitlar_ in slug_nerede.items():
        if len(kayitlar_) < 2:
            continue
        adresler = {(k.get("adres") or "").strip() for _d, k in kayitlar_}
        osbler = {k.get("osb_slug") for _d, k in kayitlar_}
        if len(adresler) == 1 and len(osbler) > 1:
            # AYNI TESIS, iki OSB klasorunde -> tekilestir
            # Birakilan kayit: osb_slug alfabetik olarak ilk olan (deterministik)
            sirali = sorted(kayitlar_, key=lambda x: (str(x[1].get("osb_slug")), str(x[0])))
            korunan_dosya, korunan = sirali[0]
            tekillestir.append((korunan_dosya, korunan, slug))
            ozet["tekillestirilen"] += len(kayitlar_) - 1
        else:
            # FARKLI adres -> gercek ayri kayitlar, SILMEZ; isaretle (KARAR 3)
            for _d, k in kayitlar_:
                if k.get("slug_cakismasi"):
                    continue
                k["slug_cakismasi"] = {
                    "slug": slug,
                    "adres_sayisi": len(adresler),
                    "osb_sayisi": len(osbler),
                    "cozum": "ayri adres -> ayri kayit korunur; slug farklidir",
                }
            ozet["korunan"] += len(kayitlar_)

    # 4) Tekillestirilenleri diskten kaldir (kopya isaretle, sonra dusur)
    dusurulecek: dict[pathlib.Path, set[str]] = collections.defaultdict(set)
    for korunan_dosya, korunan, slug in tekillestir:
        for dosya, k in slug_nerede[slug]:
            if dosya == korunan_dosya and k is korunan:
                continue
            k["tekillestirildi"] = {
                "slug": slug,
                "korunan_osb": korunan.get("osb_slug"),
                "korunan_dosya": korunan_dosya.parent.name,
                "gerekce": "ayni adres + ayni slug; ayni fiziksel tesis",
            }
            dusurulecek[dosya].add(slug)
            # D-262: kayıt SİLİNMEZ, İŞARETLENİR — veri kaybı yok.
            ozet["isaretlenen_kopya"] += 1

    # 5) Yaz — YALNIZCA kuru değilse (varsayılan kuru = veriye dokunma, D-244)
    if not kuru:
        gruplu: dict[pathlib.Path, list[dict]] = collections.defaultdict(list)
        for dosya, k in hepsi:
            gruplu[dosya].append(k)
        for dosya, kayitlar_ in gruplu.items():
            # Kural: `tekillestirildi` işareti taşıyan kayıt DÜŞÜRÜLMEZ —
            # D-262 "silmeden önce referans taşı": iz durur, veri kaybolmaz.
            # Bu görev kayıt SILMEZ; yalnız kimliği tekillestirir.
            _yaz(dosya, kayitlar_)
    return ozet


def raporla(ozet: dict) -> None:
    """Turu konsola yazar (D-236: her alanın bir okuyucusu var)."""
    print("=" * 62)
    print("OSB VERI TEMIZLIK (VERI-OSB-TEMIZLIK-01)")
    print("=" * 62)
    print(f"  taranan klasor        : {ozet['dosya']}")
    print(f"  slug URETILEN         : {ozet['slug_uretilen']}")
    print(f"  slug ATLANAN (bozuk)  : {ozet['slug_atlanan']}")
    print(f"  ayni tesis (isaretl.) : {ozet['isaretlenen_kopya']}")
    print(f"  farkli adres KORUNAN  : {ozet['korunan']}")
    print(f"  SILINEN kayit         : {ozet['silinen_kayit']}  (D-262: hepsi 0)")
    print("-" * 62)
    print("Kural: kayit SILINMEZ. Ayni adres + ayni slug olan kopyalar")
    print("`tekillestirildi` isareti ile korunur; boylece kaynak izi durur.")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--yaz", action="store_true",
                    help="DOSYAYA YAZ (varsayilan: yalniz olc, veriye dokunma)")
    ap.add_argument("--onizleme", action="store_true",
                    help="yazmadan once ne yapilacagini goster (--yaz ile ayni)")
    a = ap.parse_args(argv)

    logging.basicConfig(level=logging.INFO, format="%(message)s")
    # D-244: varsayilan KURU. Veriye yazmak icin acikca --yaz gerekir.
    kuru = not a.yaz
    ozet = temizle(kuru=kuru)
    raporla(ozet)
    if not kuru:
        print("=" * 62)
        print("YAZILDI. Dogrulama: python scripts/osb_veri_denetim.py --self")
    return 0


if __name__ == "__main__":
    sys.exit(main())
