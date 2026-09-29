"""D-299: MUKERRER tekillestirme + FILTRELI kaliteli dataset uretimi.

KAHIN 2026-09-29: "m.ukerrer i$ini hallet - filtreli bir data seti olsun,
duzgun kaliteli gercekci".

GIRIS : data/ostim/tamamlama_2026-09-29/firmalar_tamamlanmis.jsonl (3.338)
        + data/ostim/firmalar_vkn_ekli.jsonl (mevcut 5.040)
CIKTI : data/ostim/OSTIM_TEMIZ.jsonl
        data/ostim/OSTIM_TEMIZ_RAHATLARI.json

KURALLAR:
  1. TEKILLESTIRME yalnizca OLCULMUS gruplara uygulanir: ayni normalize
     unvan + ayni telefon + ayni adres. Adresi farkli olanlar AYRI
     ISLETME sayilir ve KORUNUR.
  2. FILTRE: kirp degerler (D-285/D-292) ve dolgu metni temizlenir.
  3. KAYNAK KORUNUR: hicbir kaynak dosyaya dokunulmaz.
  4. VKN bu kaynakta YOKTUR (D-282) - uydurulmaz.
  5. NACE resmi degil; `nace_confidence=medium` isaretli kalir (K-2).

Kullanim:
    python scripts/ostim_mukerrer_coz.py --kuru     # sadece rapor
    python scripts/ostim_mukerrer_coz.py           # dosya uret
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
from collections import Counter
from datetime import datetime

KOK = pathlib.Path(__file__).resolve().parents[1]
DATA = KOK / "data" / "ostim"
TARAMA = DATA / "tamamlama_2026-09-29" / "firmalar_tamamlanmis.jsonl"
VAR = DATA / "firmalar_vkn_ekli.jsonl"
LISTE = DATA / "firmalar_full.jsonl"
CIKTI = DATA / "OSTIM_TEMIZ.jsonl"
RAPOR = DATA / "OSTIM_TEMIZ_RAHATLARI.json"

#: D-285/D-292: kurumun kendi altyapisi, firma verisi DEGILDIR.
_ALT_YAPI_WEB = {
    "isim.org.tr", "www.isim.org.tr", "ostimistihdam.com",
    "www.ostimistihdam.com", "htk.org.tr", "www.htk.org.tr",
    "ostim.org.tr", "www.ostim.org.tr",
}
#: D-285: OSTIM'in kendi sosyal hesaplari firma hesabi DEGILDIR.
_KIRLI_SOSYAL = ("ostimosb", "ostim-osb", "ostim_osb", "ostimosb_org")
#: D-292: sektor adinin sonuna yapisan sira numarasi.
_SAYI_SIZINTISI = re.compile(r"\d+\s*$")
#: D-285: "bilgi yok" anlamina gelen dolgu metinleri.
_DOLGU = ("girilmemis", "bilgi yok", "belirtilmemis", "bilgisi yok", "yoktur")
_METIN_ALAN = ("adres", "unvan", "sektor", "nace_name_tr")



def norm_unvan(u: str) -> str:
    return re.sub(r"[^A-Z0-9]", "", (u or "").upper())


def norm_telefon(t: str) -> str:
    return re.sub(r"\D", "", str(t or ""))[-9:]


def norm_adres(a: str) -> str:
    return re.sub(r"[^A-Z0-9]", "", (a or "").upper())


def _guvenli(alan: str, deger) -> bool:
    """D-285/D-292 kirp filtresi. Bos deger -> False."""
    if deger in (None, "", [], {}):
        return False
    if alan == "sosyal_medya":
        return not any(any(x in str(v).lower() for x in _KIRLI_SOSYAL)
                       for v in (deger or {}).values())
    s = str(deger).strip()
    low = s.lower()
    if alan in _METIN_ALAN:
        if low in {"-", "n/a", "na", "yok", "bilinmiyor", "?"}:
            return False
        if any(x in low for x in _DOLGU):
            return False
    if alan == "web_sitesi":
        t = re.sub(r"^https?://", "", low).rstrip("/")
        if t in _ALT_YAPI_WEB or t.removeprefix("www.") in _ALT_YAPI_WEB:
            return False
    if alan == "sektor" and _SAYI_SIZINTISI.search(s):
        return False
    if alan in ("osb_parsel", "nace_name_tr") and len(s) > 60:
        return False
    return True


#: D-300 + KAHIN kurali (2026-09-29) — Turk telefonu YAZIM KURALLARI:
#:
#:   1) ULKE KODU YOK. Bastaki `90` / `0090` SILINIR. `+90 312...` yazimi
#:      goruldugunde hicbir ulke kodu saklanmaz.
#:   2) 0 BASLANGIC ZORUNLU. Alan kodu `312` degil `0312` olur; `0`
#:      yoksa EKLENIR. Cep `532` degil `0532` olur.
#:   3) SABIT HAT: `0` + 3 haneli alan kodu + 7 haneli abone = 10 hane.
#:      0312 ile baslar (Ankara). Alan kodu ile abone arasinda BOSLUK.
#:   4) CEP: `05` ile baslar. Alan kodu YOKTUR; 05 + 9 haneli numara
#:      = 11 hane. Arada bolum yok.
#:   5) AYIRILAMAZSA BIRAKILIR. Kirpmak bastaki `0`'yi dusurup gecersiz
#:      numara uretir — uretmek, birakmaktan kotudur.
#:
#: D-300 hatasi: `903123852424` sessizce `3123852424` olurdu; bastaki 0
#: kAYBOLURDU. Artik boyle bir deger uretilmez.
_ALAN_KODU_UZ = 3          # 312 / 212 / 555
_ABONE_UZ = 7              # sabit hat abone no


def _tel_bicimlendir(rakamlar: str) -> str | None:
    """Normalize edilmis rakam dizisini Turk yazim kuralina gore bicimlendirir.

    Girdi: yalniz rakam. Cikti: "0312 3854000" (sabit) veya
    "05321234567" (cep), ya da None (ayrilamadi -> BIRAKILIR).
    """
    s = rakamlar
    if not s:
        return None
    # 1) ulke kodunu soy
    if s.startswith("0090"):
        s = s[4:]
    elif s.startswith("90"):
        s = s[2:]

    # 2) basinda 0 yoksa ekle
    if not s.startswith("0"):
        s = "0" + s

    # 3) CEP: 05 ile baslar, alan kodu yok, 05 + 9 hane = 11
    if s.startswith("05"):
        govde = s[2:]                    # 9 hane beklenir
        if len(govde) == _ABONE_UZ + 2:  # 05 + 7 = 9 -> 11 hane
            return "05" + govde
        return None

    # 4) SABIT: 0 + 3 alan kodu + 7 abone = 10 hane
    if len(s) == 1 + _ALAN_KODU_UZ + _ABONE_UZ:      # 10
        return s[:1 + _ALAN_KODU_UZ] + " " + s[1 + _ALAN_KODU_UZ:]

    return None


def telefonlari_temizle(ham: list) -> list[str]:
    """Bitisik URLESIYEN telefon numaralarini duzeltir. D-300 + KAHIN kurali.

    Turk sabit: 0312 385 40 00  -> "0312 3854000"   (alan kodu sonrasi bosluk)
    Turk mobil: 0532 123 45 67  -> "05321234567"    (alan kodu YOK)
    12+ hane    : ayrilamazsa BIRAKILIR (kirpma gecersiz numara uretir).
    """
    temiz: list[str] = []
    for t in ham or []:
        s = re.sub(r"\D", "", str(t))
        bicim = _tel_bicimlendir(s)
        if bicim:
            temiz.append(bicim)
    return sorted(set(temiz))


#: D-300: adres alanina sayfa blogu sizmis olabilir
#: ("Merkez: X Sube: Y", "Fabrika: X Lojistik adresi: Y", "Tel: X").
#: Bunlar TEK adres DEGILDIR; ama ikisi de GERCEK adres oldugu icin
#: ilki alinir ve kirp BIRAKILMAZ (bilgi kaybi olmaz).
#:
#: DIKKAT (D-300 duzeltme): Turkce "Ş" = U+015E, "ş" = U+015F, "Ü" =
#: U+00DC, "ü" = U+00FC. Duz "Şube" yazmak terminal/editor kodlamasina
#: gore BOZULUR ve desen HIC eslesmez. Bu yuzden karakter sinifi
#: kullanilir: S, s, Ş, ş, ŞU, şu, ŞÜ, şÜ hepsi eslesir.
_SS = "[Ss\u015e\u015f\u0158]"        # S / s / Ş / ş / Ş
_UU = "[uU\u00fc\u0131\u0130\u00d6\u00f6]"   # u / U / ü / Ü / ı / İ / ö / Ö
#: IKI ETIKET SINIFI AYRI OLMALI (D-300 duzeltme):
#:
#:  - ADRES_BASLATICI (Merkez/Fabrika/Sube/Lojistik adresi): metnin
#:    BASINDA gelirse arkadaki deger ADRESTIR -> etiket atilir, deger alinir.
#:  - GECIS_ETIKETI (Tel/Telefon/Faks/E-Posta/Web Site/Sektör): bunlar
#:    ilk bloktan SONRA gelir ve o blogun devami degildir -> kirpilir.
#:
#: Once tek desen kullanildi; `Tel:` gecis etiketi de "adres basindadir"
#: sanildigi icin metnin basinda kalinca telefon numarasi adres sanildi.
#: Ayri desen olmadan bu AYIRT EDILEMEZ.
#: DIKKAT: bu desen ANCHOR'SIZ olmali. `^` ile derlenirse `search()`
#: icteki ikinci etiketi ("Merkez: Fabrika: X Sube: Y") bulamaz ve
#: kirpma calismaz. Basinda kontrol `match()` ile AYRI yapilir.
_ADRES_BASLATICI = re.compile(
    rf"(?:{_SS}\s*{_UU}be|Lojistik\s+adresi|Fabrika|Merkez)\s*:",
    re.IGNORECASE)
_GECIS_ETIKETI = re.compile(
    r"(Telefon|Tel|Faks|E-?Posta|Web\s*Site|Sekt\u00f6?r)\s*:",
    re.IGNORECASE)
_ADRES_BLOGU = re.compile(
    rf"({_SS}\s*{_UU}be|Lojistik\s+adresi|Fabrika|Merkez|Telefon|Tel|"
    rf"E-?Posta|Web\s*Site|Sekt{_UU}r|Faks)\s*:", re.IGNORECASE)
_ADRES_MAX = 120
_ADRES_MIN = 8


def adresi_temizle(ham) -> str | None:
    """Adres alanindaki sayfa blogunu kirpar. D-300.

    Kurallar:
      1) Basinda ADRES_BASLATICI varsa (`Merkez: X`) X alinir.
      2) Sonraki GECIS_ETIKETI'nden (`Sube: Y`, `Tel: Z`) itibaren kesilir.
      3) Etiketsiz metin aynen korunur.
    """
    if not ham:
        return None
    s = str(ham).strip()
    if not s:
        return None

    # 1) basta adres baslatici varsa degeri al. ARKA ARKAYA etiketler
    #    ("Merkez: Fabrika: X") olabilir; ilki bosluk birakmasin diye
    #    etiket basinda oldugu surece dongu.
    while True:
        m = _ADRES_BASLATICI.match(s)
        if not m:
            break
        s = s[m.end():].strip(" :;-")
        if not s:
            return None

    # 2) sonraki GECIS etiketinden itibaren kes (ilk olana kadar)
    g = _ADRES_BASLATICI.search(s) or _GECIS_ETIKETI.search(s)
    if g:
        s = s[:g.start()].strip(" ,;-")

    s = s.strip(" :;-")
    # cok uzunsa: ilk adres benzeri blok
    if len(s) > _ADRES_MAX:
        parca = re.split(r"(?<=\d)\s*[/,;]\s+(?=[A-ZÇĞİÖŞÜa-zçğıöşü])", s)
        if parca and len(parca[0]) <= _ADRES_MAX:
            s = parca[0]
    s = re.sub(r"\s+", " ", s).strip(" ,;-")
    # adres icinde RAKAM olmali ve makul uzunlukta olmali
    if len(s) < _ADRES_MIN or not re.search(r"\d", s):
        return None
    return s




def _yukle(yol: pathlib.Path) -> list[dict]:
    if not yol.is_file():
        return []
    out = []
    for satir in yol.read_text(encoding="utf-8").splitlines():
        if satir.strip():
            try:
                out.append(json.loads(satir))
            except json.JSONDecodeError:
                continue
    return out


def temizle(kayit: dict) -> tuple[dict, list[str]]:
    """Kirp alanlari temizler. (kayit, temizlenen_alanlar)."""
    kirp = []
    for alan in ("adres", "web_sitesi", "sektor", "osb_parsel",
                 "nace_name_tr", "sosyal_medya", "telefonler", "emailler"):
        if not _guvenli(alan, kayit.get(alan)):
            if kayit.get(alan) not in (None, "", [], {}):
                kirp.append(alan)
            kayit[alan] = {} if alan == "sosyal_medya" else (
                [] if alan in ("telefonler", "emailler") else None)
    kayit["vergi_no"] = None              # D-282: bu kaynakta yok
    kayit["vergi_no_kaynagi"] = None
    # D-300: telefon/adres alanlarinda sayfa blogu ve bitisik urlesme var
    temiz_tel = telefonlari_temizle(kayit.get("telefonler"))
    if temiz_tel != (kayit.get("telefonler") or []):
        kirp.append("telefonler")
        kayit["telefonler"] = temiz_tel
    temiz_adres = adresi_temizle(kayit.get("adres"))
    if temiz_adres != kayit.get("adres"):
        kirp.append("adres")
        kayit["adres"] = temiz_adres
    # K-2: kaynak kolonlari AYRI ve BOS BIRAKILMAZ. Eski detayli dosyada
    # bu kolonlar 4.969 kayitta YOK; birlestirme sirasinda eklendi.
    kayit.setdefault("kaynak_adi", "ostim")
    kayit.setdefault("kaynak_turu", "osb")
    if not kayit.get("kaynak_adi"):
        kayit["kaynak_adi"] = "ostim"
    if not kayit.get("kaynak_turu"):
        kayit["kaynak_turu"] = "osb"
    # NACE resmi DEGILDIR (D-282): sektorden turetilir, guven isaretli
    # kalir. Sektor kolonu temizlendiginde NACE de duser (turetilmis
    # oldugu icin tutulamaz) — bu K-2 dogru davranistir.
    if not kayit.get("sektor"):
        kayit["nace_code"] = None
        kayit["nace_name_tr"] = None
        kayit["nace_source"] = None
        kayit["nace_confidence"] = "none"
    return kayit, kirp



def main() -> int:
    ay = argparse.ArgumentParser()
    ay.add_argument("--kuru", action="store_true",
                    help="dosya yazma, sadece rapor")
    ns = ay.parse_args()

    tarama, var, liste = _yukle(TARAMA), _yukle(VAR), _yukle(LISTE)
    print(f"GIRIS: tarama={len(tarama)} mevcut={len(var)} liste={len(liste)}")

    # 1) tam havuz (slug tekilli); yeni tarama verisi eskiyi ezer
    havuz: dict[str, dict] = {}
    for k in var + tarama:
        if k.get("slug"):
            havuz[k["slug"]] = k
    print(f"HAVUZ: {len(havuz)}")

    # 2) m.ukerrer gruplarini OLC (unvan bazli)
    gruplar: dict[str, list[dict]] = {}
    for k in havuz.values():
        gruplar.setdefault(norm_unvan(k.get("unvan")), []).append(k)

    birlestirilebilir, ayri_korunacak = [], []
    for anahtar, grup in gruplar.items():
        if not anahtar or len(grup) < 2:
            continue
        # AYNI adres + AYNI telefon -> kesin ayni kayit (slug farki
        # siteden gelir, ayni firma iki kez listelenmis olabilir).
        # FARKLI adres -> ayri isletme, KORUNUR.
        tel_set = set()
        for g in grup:
            tel_set |= {norm_telefon(t) for t in (g.get("telefonler") or [])}
        adr_set = {norm_adres(g.get("adres")) for g in grup if g.get("adres")}
        if len(adr_set) <= 1 and len(tel_set) <= 1:
            birlestirilebilir.append(grup)
        else:
            ayri_korunacak.append(grup)

    # 3) tekillestir: en dolu kayit kalir, digerleri dusurulur
    def doluluk(g: dict) -> int:
        return sum(1 for a in ("adres", "telefonler", "emailler",
                               "web_sitesi", "sektor", "sosyal_medya")
                   if g.get(a) not in (None, "", [], {}))

    drop = set()
    for grup in birlestirilebilir:
        en_iyi = max(grup, key=doluluk)["slug"]
        drop |= {g["slug"] for g in grup if g["slug"] != en_iyi}

    # 4) filtrele
    cikti, kirp_sayi, kirp_kayit = [], Counter(), 0
    for slug, k in havuz.items():
        if slug in drop:
            continue
        k, kirp = temizle(dict(k))
        if kirp:
            kirp_kayit += 1
            for a in kirp:
                kirp_sayi[a] += 1
        cikti.append(k)

    # 5) kalite olcumu
    unvanlar = [norm_unvan(k.get("unvan")) for k in cikti]
    sluglar = [k.get("slug") for k in cikti]
    doluluk = {}
    for alan in ("adres", "telefonler", "emailler", "web_sitesi",
                 "sektor", "sosyal_medya"):
        d = sum(1 for k in cikti if k.get(alan) not in (None, "", [], {}))
        doluluk[alan] = {"dolu": d,
                         "oran_yuzde": round(100 * d / len(cikti), 1)}

    sekt_rakam = sum(1 for k in cikti if k.get("sektor")
                     and _SAYI_SIZINTISI.search(str(k["sektor"])))
    sosyal_kirli = sum(1 for k in cikti
                       for v in (k.get("sosyal_medya") or {}).values()
                       if any(x in str(v).lower() for x in _KIRLI_SOSYAL))
    web_kirli = sum(
        1 for k in cikti if k.get("web_sitesi")
        and re.sub(r"^https?://", "", str(k["web_sitesi"]).lower())
        .rstrip("/").removeprefix("www.") in _ALT_YAPI_WEB)

    rapor = {
        "uretim_zamani": datetime.now().isoformat(timespec="seconds"),
        "girdi": {"tarama": len(tarama), "mevcut_detayli": len(var),
                  "liste": len(liste), "havuz_tekilli": len(havuz)},
        "cikti": {"kayit": len(cikti),
                  "dusen_mukerrer": len(drop),
                  "birlestirilen_grup": len(birlestirilebilir),
                  "ayri_korunan_grup": len(ayri_korunacak)},
        "tekillestirme": {
            "mukerrer_slug_kaldi": len(sluglar) - len(set(sluglar)),
            "mukerrer_unvan_kaldi": len(unvanlar) - len(set(unvanlar)),
        },
        "filtre": {"temizlenen_kayit": kirp_kayit,
                   "alan_bazinda": dict(kirp_sayi)},
        "kalan_kirlilik": {"rakamli_sektor": sekt_rakam,
                           "kirli_sosyal_hesap": sosyal_kirli,
                           "alt_yapi_web": web_kirli},
        "doluluk": doluluk,
        "kaynak_disi": {
            "vergi_no_dolu": sum(1 for k in cikti if k.get("vergi_no")),
            "aciklama": "OSTIM VKN yayimlamaz (D-282); uydurulmadi",
        },
        "kaynak_isaretleme": {
            "kaynak_adi_dolu": sum(1 for k in cikti if k.get("kaynak_adi")),
            "kaynak_turu_dolu": sum(1 for k in cikti if k.get("kaynak_turu")),
            "kaynak_adi_degerleri": dict(Counter(
                str(k.get("kaynak_adi")) for k in cikti).most_common()),
            "nace_confidence": dict(Counter(
                str(k.get("nace_confidence")) for k in cikti).most_common()),
        },
    }
    RAPOR.write_text(json.dumps(rapor, ensure_ascii=False, indent=2),
                     encoding="utf-8")

    if not ns.kuru:
        with CIKTI.open("w", encoding="utf-8") as f:
            for k in cikti:
                f.write(json.dumps(k, ensure_ascii=False) + "\n")

    print("\n=== CIKTI ===")
    print(f"kayit               : {len(cikti)}")
    print(f"dusen m.ukerrer     : {len(drop)} "
          f"({len(birlestirilebilir)} grup)")
    print(f"ayri korunan grup   : {len(ayri_korunacak)}")
    print(f"mukerrer slug KALDI : "
          f"{rapor['tekillestirme']['mukerrer_slug_kaldi']}")
    print(f"mukerrer unvan KALDI: "
          f"{rapor['tekillestirme']['mukerrer_unvan_kaldi']}")
    print(f"temizlenen kayit    : {kirp_kayit} {dict(kirp_sayi)}")
    print(f"KALAN KIRLILIK      : {rapor['kalan_kirlilik']}")
    print("\n=== DOLULUK ===")
    for a, v in doluluk.items():
        print(f"  {a:14s} {v['dolu']:5d}  %{v['oran_yuzde']}")
    print(f"\n{'KURU (--kuru)' if ns.kuru else CIKTI}")
    print(RAPOR)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

