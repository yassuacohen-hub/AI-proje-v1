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


#: D-300: telefon uzunlugu olculdu. Turk mobil 11, sabit 10-11 hanedir.
#:   12+ haneli degerler BIRBIRINE BITISIK URLESIYOR: `903123852424`
#:   = "0 312 385 24 24" -> bastaki 0 ve aradaki bosluk kaybolmus.
#:   Cozum: Turk numaralari 5 haneli alan kodu + 7 haneli abone
#:   gecer. 12 hanede bolup ILK 10 haneyi al ve boslugu onune koy.
_TEL_MIN, _TEL_MAX = 10, 11


def telefonlari_temizle(ham: list) -> list[str]:
    """Bitisik URLESIYEN telefon numaralarini duzeltir. D-300.

    Turk sabit: 0312 385 40 00 -> 10 hane
    Turk mobil: 0532 123 45 67 -> 11 hane
    12+ hane   : iki numara birlestmis veya format bozulmus.
    Cift sayi bile varsa AYIRIRIZ, tek sayiyi KIRPARIZ (veri uydurulmaz).
    """
    temiz: list[str] = []
    for t in ham or []:
        s = re.sub(r"\D", "", str(t))
        if _TEL_MIN <= len(s) <= _TEL_MAX:
            temiz.append(s)
            continue
        if len(s) > _TEL_MAX:
            # 12 hane: bolup bak - iki parcaya ayrilabiliyor mu?
            bas, kalan = s[:10], s[10:]
            if kalan and 3 <= len(kalan) <= 4:
                temiz.append(bas)
                continue                     # ikinci parca numara degil
            # 12 haneyi tek numara kabul etme; 90/0 prefiksini dene
            govde = s[2:] if s.startswith("90") else s.lstrip("0")
            if _TEL_MIN <= len(govde) <= _TEL_MAX:
                temiz.append(govde)
                continue
        # AYIRILAMADI -> kirp BIRAKILIR (uydurma numara uretme)
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
_ADRES_BLOGU = re.compile(
    rf"({_SS}\s*{_UU}be|Lojistik\s+adresi|Fabrika|Merkez|Telefon|Tel|"
    rf"E-?Posta|Web\s*Site|Sekt{_UU}r|Faks)\s*:", re.IGNORECASE)
_ADRES_MAX = 120
_ADRES_MIN = 8


def adresi_temizle(ham) -> str | None:
    """Adres alanindaki sayfa blogunu kirpar. D-300."""
    if not ham:
        return None
    s = str(ham).strip()
    if not s:
        return None
    # "Merkez: X Sube: Y" -> X al (ilk blok), "Sube:" ve sonrasi atilir.
    # D-300: `m.start() > 0` sarti YANLIS: ilk etiket metnin BASINDA
    # oldugunda ("Merkez: ...") hicbir sey kesilmezdi. Dogru kural:
    # etiket + iki nokta + BOSLUK geliyorsa o etiketten SONRASI alinir.
    m = _ADRES_BLOGU.search(s)
    if m:
        s = s[m.end():].strip()
        # sonraki bloklari da kes
        m2 = _ADRES_BLOGU.search(s)
        if m2:
            s = s[:m2.start()].strip(" ,;-")
    s = re.sub(r"^\s*(Merkez|Şube|Fabrika)\s*:\s*", "", s, flags=re.I)
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

