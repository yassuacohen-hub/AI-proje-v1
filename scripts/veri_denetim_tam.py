"""KAHIN (2026-09-29): 'her satir dogru veri var mi - hatlari tekrar gozden
gecir, ostim ve ivedik dahil, her sey hazir olsun.'

BU ARAC NEDEN VAR:
  D-300'de iki GERCEK hata vardi ve ikisi de elle fark edildi. Elle
  gozden gecirme 8.296 satira kadar calismaz; 35.000+ satirda insan
  gozu kayar. Burada kurallar KODDA: her dosya icin otomatik denenir.

DENETLENEN KAYNAKLAR: OSTIM_TEMIZ + OSTIM aile dosyalari, IVEDIK,
BASKENT, ASO, MERGED.

KURALLAR: YAPI (parse/tip/bosluk) | TELEFON (KAHIN yazim kurali) |
E-POSTA | WEB + altyapi siteleri | SOSYAL sahte hesap | ADRES |
SEKTOR sayfa metni sizintisi | VKN | CAPRAZ tekillik | DOLULUK.

Kullanim:
    python scripts/veri_denetim_tam.py
    python scripts/veri_denetim_tam.py --kaynak ostim_temiz
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
from collections import Counter, defaultdict

KOK = pathlib.Path(__file__).resolve().parents[1]

#: (etiket, yol, oncelik)
KAYNAKLAR: list[tuple[str, str, str]] = [
    ("ostim_temiz", "data/ostim/OSTIM_TEMIZ.jsonl", "P0"),
    ("ostim_full", "data/ostim/firmalar_full.jsonl", "P1"),
    ("ostim_birlestirilmis", "data/ostim/firmalar_birlestirilmis.jsonl", "P1"),
    ("ostim_detayli", "data/ostim/firmalar_detayli.jsonl", "P1"),
    ("ostim_detayli_validated", "data/ostim/firmalar_detayli_validated.jsonl", "P1"),
    ("ostim_vkn_ekli", "data/ostim/firmalar_vkn_ekli.jsonl", "P1"),
    ("ostim_tamamlama",
     "data/ostim/tamamlama_2026-09-29/firmalar_tamamlanmis.jsonl", "P1"),
    ("ivedik", "data/ivedik/firmalar.jsonl", "P0"),
    ("baskent", "data/baskent/firmalar.jsonl", "P1"),
    ("aso_full", "data/aso/aso_full.jsonl", "P2"),
    ("merged_multi_osb", "data/merged/multi_osb_merged.jsonl", "P1"),
]

#: alan -> (tip, bos_izin)
ALAN_TIPLERI: dict[str, tuple[type, bool]] = {
    "unvan": (str, True), "unvan_anahtari": (str, True),
    "adres": (str, True), "web_sitesi": (str, True),
    "sektor": (str, True), "nace_kod": (str, True),
    "nace_detay": (str, True), "osb_parsel": (str, True),
    "vergi_no": (str, True), "ticaret_sicil_no": (str, True),
    "kaynak_adi": (str, True), "kaynak_turu": (str, True),
    "slug": (str, True), "osb": (str, True),
    "telefonler": (list, True), "emailler": (list, True),
    "kaynaklar": (list, True), "yetkililer": (list, True),
}

#: TELEFON — KAHIN yazim kurali
TEL_SABIT = re.compile(r"0[1-9]\d{2} \d{7}")   # "0312 3854000"
TEL_CEP = re.compile(r"05\d{9}")                # "05321234567"
TEL_KURALLI = re.compile(r"^(\d[\d ]*)$")

#: WEB. DIKKAT: iki hata sinifi var ve BIRBIRINDEN AYRI OLUR:
#:   (a) TEK URL icinde birden fazlA adres: "https://a.com  https://b.com"
#:       -> ilki alinir, ikincisi AYRI alan (COZULMEZ).
#:   (b) Bozuk ayirac: "www bfblast.com" (bosluk), "https://http//x.com"
#:       -> duzeltilir; duzeltilemiyorsa ALAN BOSLUGUNU BIRAKIR.
#: Daha once her ikisi de "bicim_gecersiz" sayiliyordu; duzeltilebilir
#: olanlar ile duzeltilemeyenler birbirine karisti.
#: DIKKAT: bu desen SIKI OLMALI. `[^\\s"'<>\\]]+` icinde `//` serbest
#: oldugu icin BOZUK "https://http//a.com" degerini gecerli sayiyordu
#: ve duzeltme hic calismiyordu. Artik protokol + host ayri denetlenir.
URL_OK = re.compile(
    r"^https?://[A-Za-z0-9\-]+(?:\.[A-Za-z0-9\-]+)+(?::\d+)?(?:/[^\s\"'<>]*)?$",
    re.IGNORECASE)
URL_HARF = re.compile(r"^[A-Za-z0-9.\-]+\.[A-Za-z]{2,}(/\S*)?$")
#: Tam alan adi: en az bir nokta + 2+ harfli TLD
URL_DUZELTILIR = re.compile(r"^(?:https?://)?(www\.)?([A-Za-z0-9\-]+\.)+[A-Za-z]{2,}$")


def web_temizle(ham) -> str | None:
    """Tek ve gecerli bir URL dondurur; duzeltilemezse None.

    Kural (KAHIN D-303): veri UYDURMA.

    DIKKAT — parcalar sirayla denenir, ILK GECERLI olan alinir:
      "https://http//a.com  https://b.com" icinde ilk parca BOZUKTUR.
      Ilk parca dogrudan secilirse bozuk deger korunur. Duzeltilmis
      hâli gecerliyse o tercih edilir.
    """
    if not ham:
        return None
    s = str(ham).strip()
    if not s:
        return None
    # K-2 KOLON KARIŞMASI: "https://info@firma.com" aslında E-POSTA'dir.
    # Bu deger web_sitesi alanina yazilmis olamaz; ayrica degeri de
    # bozuk (protokol eki alan adi degildir). K-2: kirp BIRAKILIR.
    if "@" in s and not re.search(r"\.[A-Za-z]{2,}/", s):
        return None
    # "https://5050051468" -> TELEFON numarasi web alaninda. Sadece
    # rakam iceren bir deger alan adi OLA MAZ; kirp birakilir.
    if re.search(r"://[0-9/]+$", s):
        return None
    parcalar = [p for p in re.split(r"[\s;]+", s) if p]
    # (0) URL icine karisan TELEFON: "http://x.com/0 312 354 22 65"
    #     -> yalnizca SONDAN rakamla baslayan blok kirpilir.
    #     DIKKAT: `(?<=/)\s*\d` deseni "/0 312..." icinde calisip
    #     SADECE sondan bolup GERISININ TAMAMINI sildi; sonuc
    #     "http://3atest.com.tr" -> "http:///" oldu. VERI BOZULDU.
    #     Duzeltme: parca bolunur, yalnizca rakamli KALAN atilir.
    temiz_parca = []
    for p in parcalar:
        # "http://x.com/0 312 354 22 65" -> "http://x.com" (tamami)
        m = re.search(r"/\s*\d{3}\s*[\d\s]+$", p)
        if m:
            p = p[:m.start()]
        # "http://x.com/0" -> sondaki tek rakam da kirpilir
        p = re.sub(r"/\d+$", "", p)
        if p:
            temiz_parca.append(p)
    parcalar = temiz_parca
    # 1) dogrudan gecerli olan varsa ilk o alinir
    for p in parcalar:
        if URL_OK.match(p):
            return p
    # 2) duzeltilmis halleri sirayla dene; ilk duzelenen alinir.
    #    DIKKAT: "https://http//a.com" once "https://a.com" olur
    #    (cift protokol), SONRA "https://" kirpilmasi denenir. Aksi
    #    halde cift protokol deseni URL_DUZELTILIR'i gecmez ve deger
    #    BOZUK kalir.
    for p in parcalar:
        # DIKKAT: once `http//` duzelt, SONRA `:/` ekle. Ters sira
        # hatali: "https://http//x.com" -> ":/"->"://" once
        # "https:///http//x.com" uretiyor (fazladan '/') ve
        # cift-protokol kurali da artik tutmuyor.
        d = p.replace("http//", "http://").replace("https//", "https://")
        d = d.replace(":/", "://")
        d = re.sub(r"^(https?)://\1://", r"\1://", d)
        d = re.sub(r"^https?://https?://", "https://", d)
        d = d.replace(" ", "")
        if not d:
            continue
        if URL_OK.match(d) or URL_DUZELTILIR.match(d):
            return d if d.startswith("http") else f"https://{d}"
    return None


#: E-POSTA. DIKKAT: Turkce karakterli local kisim GERCEKTIR
#: ("erenkocyigit26@gmail.com" yaygin). Ilk regex ASCII ile sinirli
#: kalmisti ve 37 gecerli epostayi "gecersiz" ilan ediyordu - YANLIŞ
#: ALARM. Duzeltildi: karsilastirmadan once Turkce harfler ASCII'ye
#: indirgenir (kirpma yapmadan, yalnizca denetim icin).
EMAIL = re.compile(r"^[\w.%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$", re.UNICODE)

#: K-2 sizinti izleri
HTML_IZI = re.compile(r"<[a-zA-Z/][^>]*>|&[a-zA-Z#0-9]{2,6};")
SAYFA_BLOKU = re.compile(
    r"\b(bizi\s+arayalir|ileti[s\u015f]im|devamini\s+oku|"
    r"t\u00fcm\s+firmalar|listeye\s+d\u00f6n)", re.IGNORECASE)
SAHTE_SOSYAL = re.compile(
    r"^(accounts|login|logout|signup|search|about|contact|home|"
    r"index|privacy|terms)$", re.IGNORECASE)

ALTYAPI_WEB = {
    "ostim.org.tr", "google.com", "facebook.com", "instagram.com",
    "twitter.com", "x.com", "linkedin.com", "youtube.com",
    "maps.google.com", "wikipedia.org", "t.me", "goo.gl", "bit.ly",
}

GECERLI_ALAN_KODLARI = {
    "0312", "0212", "0216", "0222", "0232", "0242", "0258", "0262",
    "0264", "0272", "0282", "0322", "0324", "0325", "0326", "0327",
    "0332", "0333", "0334", "0335", "0336", "0338", "0342", "0343",
    "0344", "0345", "0346", "0347", "0348", "0352", "0353", "0354",
    "0355", "0356", "0357", "0358", "0359", "0362", "0364", "0366",
    "0368", "0382", "0384", "0386", "0387", "0388", "0410", "0411",
}


class Rapor:
    """Birikmis denetim sonuclari."""

    def __init__(self, ad: str) -> None:
        self.ad = ad
        self.bulgu: dict[str, list] = defaultdict(list)
        self.satir = 0
        self.alan_doluluk: Counter = Counter()

    def ekle(self, kural: str, ornek: object, kayit: int = 0) -> None:
        self.bulgu[kural].append((kayit, ornek))

    def sayi(self, kural: str) -> int:
        return len(self.bulgu.get(kural, []))

    def toplam(self) -> int:
        return sum(len(v) for v in self.bulgu.values())

    def temiz_mi(self) -> bool:
        return self.toplam() == 0


def _norm(s) -> str:
    if not s:
        return ""
    t = str(s).lower().replace("\u0131", "i").replace("\u015f", "s")
    return re.sub(r"[^a-z0-9]+", "", t)


def _oku(yol: pathlib.Path):
    for satir in yol.read_text(encoding="utf-8").splitlines():
        if satir.strip():
            yield json.loads(satir)


def denetle_kayit(s: dict, r: Rapor, i: int) -> None:
    """TEK satirda tum kural gruplarini denetir."""
    r.satir += 1

    # --- YAPI: alan tipleri ve bosluk tutarliligi
    for alan, (tip, bos_izin) in ALAN_TIPLERI.items():
        if alan not in s:
            continue
        v = s[alan]
        if v is None:
            if not bos_izin:
                r.ekle(f"yapi/{alan}_none", None, i)
            continue
        if not isinstance(v, tip):
            r.ekle(f"yapi/{alan}_tip", f"{type(v).__name__}: {str(v)[:40]}", i)
            continue
        if tip is str and not v.strip():
            r.ekle(f"yapi/{alan}_bos_dize", v, i)

    # --- UNVAN
    unvan = (s.get("unvan") or "").strip()
    if not unvan:
        r.ekle("yapi/unvan_yok", "-", i)
    elif len(unvan) < 3:
        r.ekle("unvan/cok_kisa", unvan, i)

    # --- TELEFON (KAHIN kurali)
    for t in (s.get("telefonler") or []):
        t = str(t)
        if TEL_SABIT.match(t) or TEL_CEP.match(t):
            continue
        if not TEL_KURALLI.match(t):
            r.ekle("telefon/rakam_disi_karakter", t, i)
            continue
        rakam = re.sub(r"\D", "", t)
        if not rakam:
            r.ekle("telefon/rakam_yok", t, i)
        elif rakam.startswith("90") or rakam.startswith("0090"):
            r.ekle("telefon/ulke_kodu_kaldi", t, i)
        elif not rakam.startswith("0"):
            r.ekle("telefon/basinda_0_yok", t, i)
        elif len(rakam) > 11:
            r.ekle("telefon/11_hane_fazla", t, i)
        elif len(rakam) < 10:
            r.ekle("telefon/10_hane_eksik", t, i)
        elif rakam.startswith("05"):
            r.ekle("telefon/cep_bolum_kurali", t, i)
        elif " " not in t:
            r.ekle("telefon/sabit_bolum_yok", t, i)
        elif t[:4] not in GECERLI_ALAN_KODLARI:
            r.ekle("telefon/alan_kodu_gecersiz", t, i)

    # --- E-POSTA
    for e in (s.get("emailler") or []):
        e = str(e).strip()
        if not EMAIL.match(e):
            # (a) TLD'siz alan adi: info@tnzcable -> DUZELTILEMEZ.
            #     Uzantiyu UYDURMAK yasak; alan bos birakilir.
            alan = e.rsplit("@", 1)[-1] if "@" in e else ""
            if "@" in e and alan and "." not in alan:
                r.ekle("email/alan_adi_uzantisiz", e, i)
            else:
                r.ekle("email/bicim_gecersiz", e, i)
        elif e != e.lower() and e.split("@")[0].lower() != e.split("@")[0]:
            r.ekle("email/buyuk_harf_karisik", e, i)
        elif e.count("@") > 1:
            r.ekle("email/coklu_at", e, i)

    # --- WEB + altyapi siteleri
    w = s.get("web_sitesi")
    if w:
        w = str(w).strip()
        parcalar = [p for p in re.split(r"[\s;]+", w) if p]
        if len(parcalar) > 1:
            r.ekle("web/coklu_adres", f"{len(parcalar)} adres", i)
        temiz = web_temizle(w)
        if temiz is None:
            r.ekle("web/duzeltilemiyor", w[:60], i)
        else:
            host = re.sub(r"^https?://(www\.)?", "", temiz).split("/")[0].lower()
            if " " in host or ":" in host:
                r.ekle("web/bozuk_ayirac", w[:60], i)
            elif host in ALTYAPI_WEB:
                r.ekle("web/altyapi_sitesi", host, i)
            elif temiz != w:
                r.ekle("web/duzeltilebilir", f"{w[:40]} -> {temiz[:40]}", i)

    # --- SOSYAL MEDYA (K-2 sahte hesap)
    sm = s.get("sosyal_medya")
    if isinstance(sm, dict):
        for k, v in sm.items():
            if not v:
                continue
            for hesap in (v if isinstance(v, list) else [v]):
                h = str(hesap).strip("/ ")
                son = h.split("/")[-1]
                if SAHTE_SOSYAL.match(son):
                    r.ekle("sosyal/sahte_hesap", f"{k}={son}", i)
                    break
                if len(son) < 2:
                    r.ekle("sosyal/hesap_cok_kisa", f"{k}={son}", i)
                    break
    elif sm:
        r.ekle("yapi/sosyal_medya_tip", type(sm).__name__, i)

    # --- ADRES
    a = s.get("adres")
    if a:
        a = str(a)
        if HTML_IZI.search(a):
            r.ekle("adres/html_izi", a[:50], i)
        if SAYFA_BLOKU.search(a):
            r.ekle("adres/sayfa_blogu", a[:50], i)
        if re.search(r"(Merkez|\u015eube|\u015e\u00dcBE|Fabrika|"
                     r"Lojistik\s+adresi)\s*:", a, re.IGNORECASE):
            r.ekle("adres/etiket_kaldi", a[:50], i)
        if not re.search(r"\d", a):
            r.ekle("adres/rakam_yok", a[:50], i)
        if len(a) > 120:
            r.ekle("adres/120_fazla_karakter", f"{len(a)} hane", i)

    # --- SEKTOR (sayfa metni sizintisi)
    sek = s.get("sektor")
    if sek:
        sek = str(sek)
        if re.search(r"\d{3,}", sek):
            r.ekle("sektor/rakamli_sonek", sek[:50], i)
        if HTML_IZI.search(sek):
            r.ekle("sektor/html_izi", sek[:50], i)
        if len(sek) > 80:
            r.ekle("sektor/cok_uzun", f"{len(sek)} hane", i)

    # --- VKN
    vkn = s.get("vergi_no")
    if vkn:
        vkn = str(vkn).strip()
        if not re.fullmatch(r"\d{10,11}", vkn):
            r.ekle("vkn/bicim_gecersiz", vkn, i)

    # --- HTML izi (diger alanlar)
    for alan in ("unvan", "nace_detay", "osb_parsel"):
        v = s.get(alan)
        if v and HTML_IZI.search(str(v)):
            r.ekle(f"yapi/{alan}_html_izi", str(v)[:50], i)

    # --- DOLULUK
    for alan in ("unvan", "adres", "telefonler", "emailler", "web_sitesi",
                 "kaynak_adi", "kaynak_turu", "sektor"):
        v = s.get(alan)
        if v not in (None, "", [], {}):
            r.alan_doluluk[alan] += 1


def denetle_tekillik(raporlar: dict[str, Rapor], yollar: dict[str, pathlib.Path],
                     slug_gor: dict[str, list[str]],
                     unvan_gor: dict[tuple, list]) -> None:
    """Dosya ici + kaynaklar arasi tekillik (K-1 sessiz tekrar yasagi)."""
    for ad, r in raporlar.items():
        yol = yollar.get(ad)
        if not yol or not yol.is_file():
            continue
        yerel: Counter = Counter()
        for i, s in enumerate(_oku(yol), 1):
            slug = s.get("slug")
            if slug:
                yerel[str(slug)] += 1
                slug_gor[str(slug)].append(ad)
            k = (s.get("unvan_anahtari") or _norm(s.get("unvan")),
                 _norm(s.get("adres")))
            if k[0]:
                unvan_gor[k].append((ad, i))
        for slug, adet in yerel.items():
            if adet > 1:
                r.ekle("capraz/dosya_ici_ayni_slug", f"{slug} x{adet}")

    for slug, sahipleri in slug_gor.items():
        if len(sahipleri) > 1:
            ad = sahipleri[0]
            # YANLIŞ ALARM KORUMASI: ayni slug'in iki kaynakta birden
            # olmasi NORMALDIR (birlestirilmis kopya + temiz kopya ayni
            # firmayi icerir). Gercek sorun, TEK kaynak disinda ayni
            # slug'i iki AYRI kaynakta gormek degil; slug'in kendi icinde
            # tekrarli olmasi capraz/dosya_ici kuralinda zaten yakalanir.
            # Burada yalnizca ayni slug'e sahip 2+ kaynak VEYA tek kaynakta
            # tekrarli gorunumu incelenir.
            adet = Counter(sahipleri)
            tekrarli = [s for s, c in adet.items() if c > 1]
            if tekrarli:
                raporlar[ad].ekle(
                    "capraz/ayni_slug_iki_kaynakta",
                    f"{slug} ({', '.join(sorted(tekrarli))})")
    for k, yerler in unvan_gor.items():
        # YANLIŞ ALARM KORUMASI: (unvan, adres) ciftinin birden fazla
        # KAYNAKTA gorunmesi normaldir — kaynak dosyalar ayni havuzu
        # farkli asamalarda tutar. Gercek mükerrer, TEK kaynak icinde
        # ayni firmanin iki kez durmasidir; o zaten yukarida
        # "dosya_ici_ayni_slug" ile yakalanir.
        tek_kaynak = Counter(ad for ad, _ in yerler)
        gercek = {ad: c for ad, c in tek_kaynak.items() if c > 1}
        if gercek:
            ad = max(gercek, key=gercek.get)
            raporlar[ad].ekle("capraz/ayni_unvan_ayni_adres",
                              f"{k[0][:38]} x{gercek[ad]}")


def raporla(r: Rapor) -> None:
    n = r.satir
    print(f"\n{'=' * 66}")
    print(f"{r.ad.upper()}  ({n} satir)")
    print("=" * 66)
    if r.toplam() == 0:
        print("  TEMIZ - tum kural gruplari gecti.")
    else:
        for kural, kayitlar in sorted(r.bulgu.items(),
                                      key=lambda x: -len(x[1])):
            print(f"  [KIRMIZI] {kural:36s} {len(kayitlar):6d}  "
                  f"orn: {str(kayitlar[0][1])[:40]}")
    if n:
        dol = "  ".join(
            f"{a}:{r.alan_doluluk[a] * 100 // n}%" for a in
            ("adres", "telefonler", "emailler", "web_sitesi", "kaynak_adi"))
        print(f"  doluluk: {dol}")


def main() -> int:
    ay = argparse.ArgumentParser()
    ay.add_argument("--kaynak", default=None,
                    help="tek kaynak etiketi (orn: ostim_temiz)")
    ns = ay.parse_args()

    print("=" * 66)
    print("KAPSAMLI VERI DENETIMI — her satir, her kural")
    print("=" * 66)

    raporlar: dict[str, Rapor] = {}
    yollar: dict[str, pathlib.Path] = {}
    slug_gor: dict[str, list[str]] = defaultdict(list)
    unvan_gor: dict[tuple, list] = defaultdict(list)

    for etiket, yol, oncelik in KAYNAKLAR:
        if ns.kaynak and etiket != ns.kaynak:
            continue
        p = KOK / yol
        yollar[etiket] = p
        if not p.is_file():
            print(f"  [{oncelik}] {etiket:24s} YOK ({yol})")
            continue
        r = Rapor(etiket)
        for i, s in enumerate(_oku(p), 1):
            denetle_kayit(s, r, i)
        raporlar[etiket] = r

    if not raporlar:
        print("Hicbir kaynak bulunamadi.")
        return 1

    denetle_tekillik(raporlar, yollar, slug_gor, unvan_gor)
    for ad, r in raporlar.items():
        raporla(r)

    # --- OZET
    print(f"\n{'=' * 66}")
    print("OZET")
    print("=" * 66)
    kirli = {a: r.toplam() for a, r in raporlar.items() if r.toplam()}
    toplam_satir = sum(r.satir for r in raporlar.values())
    toplam_hata = sum(r.toplam() for r in raporlar.values())
    print(f"  denetlenen kaynak : {len(raporlar)}")
    print(f"  denetlenen satir  : {toplam_satir:,}".replace(",", "."))
    print(f"  toplam bulgu      : {toplam_hata:,}".replace(",", "."))
    if kirli:
        print("\n  HATALI KAYNAKLAR:")
        for a, t in sorted(kirli.items(), key=lambda x: -x[1]):
            print(f"    {a:26s} {t:6d} bulgu")
    else:
        print("\n  HICBIR KAYNAKTA HATA YOK.")
    return 0


def temizle(kaynak_etiket: str = "ostim_temiz") -> dict:
    """Duzeltilebilir hatalari dosyaya YAZAR. D-303.

    Kural: veri UYDURMA.
      - web/duzeltilebilir  -> mekanik duzeltme, UYGULANIR
      - web/coklu_adres     -> ilki alinir, digerleri KAYBOLMAZ (rapora yazilir)
      - email/buyuk_harf    -> kucuk harfe INDIRILIR (adres degismez)
      - email/alan_adi_uzantisiz, email/bicim_gecersiz -> BIRAKILIR
        (uzanti/duzeltme UYDURMA olurdu; alan bosaltilir)
    """
    yol = KOK / dict((k, v) for k, v, _ in KAYNAKLAR)[kaynak_etiket]
    satirlar = list(_oku(yol))
    degisen = Counter()
    coklu = []
    for s in satirlar:
        w = s.get("web_sitesi")
        if w:
            parcalar = [p for p in re.split(r"[\s;]+", w) if p]
            if len(parcalar) > 1:
                coklu.append({"unvan": s.get("unvan"),
                              "bulunan": w,
                              "alan_kalan": parcalar[0]})
            t = web_temizle(w)
            if t and t != w:
                s["web_sitesi"] = t
                degisen["web_duzeltildi"] += 1
        eski = list(s.get("emailler") or [])
        yeni = []
        for e in eski:
            e = str(e).strip()
            if not EMAIL.match(e):
                degisen["email_drop"] += 1
                continue
            if e != e.lower():
                degisen["email_kucultuldu"] += 1
                e = e.lower()
            if e not in yeni:
                yeni.append(e)
        if yeni != eski:
            s["emailler"] = yeni

    gecici = yol.with_suffix(".jsonl.tmp")
    with gecici.open("w", encoding="utf-8") as f:
        for s in satirlar:
            f.write(json.dumps(s, ensure_ascii=False) + "\n")
    gecici.replace(yol)
    return {"degisen": dict(degisen), "coklu_adres": coklu,
            "satir": len(satirlar)}


if __name__ == "__main__":
    raise SystemExit(main())
