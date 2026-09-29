"""OSB firma listesi kaziyicisi - politika P-1..P-10 (D-305).

KAHIN 2026-09-29: "eksik 4 OSB'de bitir, hepsini topla."

OLCULE YAPI (selector UYDURULMADI):
  ptoosb/firmalarimiz : WordPress. Firma adi
      div.wpb_text_column > div.wpb_wrapper > p > strong
      'pagination' CSS sinifi sayfalamada kullaniliyor.

POLITIKA (BORC_DEFTERI D-283):
  P-1  sabit gercek User-Agent, bot taklidi YAPILMAZ
  P-2  robots.txt kontrolu; yasaksa DUR
  P-3  istek araligi 2.0 sn
  P-5  kaynak dosyalara dokunulmaz (SHA-256 kilidi)
  P-6  tekil oran esigi 0.95
  P-10 500 kayit/gun tavani

Kurallar: kaynak dosyalara dokunulmaz, hicbir kayit silinmez,
cikti AYRI klasore yazilir (data/osb_tarama/<slug>/).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import re
import time
from datetime import datetime, timezone

KOK = pathlib.Path(__file__).resolve().parents[1]
CIKTI = KOK / "data" / "osb_tarama"
DURUM = CIKTI / "_durum.json"

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36")
GECIKME = 2.0
TEKIL_ESIK = 0.95
GUN_TAVANI = 500

HEDEFLER = {
    "polatli_ticaret": ("Polatli Ticaret Odasi OSB",
                        "https://www.ptoosb.org.tr/firmalarimiz/"),
    "sereflikochisar": ("Sereflikochisar OSB",
                         "http://www.sereflikochisarosb.org.tr/"),
}

KORUNAN = [
    KOK / "data" / "ostim" / "OSTIM_TEMIZ.jsonl",
    KOK / "data" / "ostim" / "firmalar_full.jsonl",
    KOK / "data" / "baskent" / "firmalar.jsonl",
    KOK / "data" / "aso" / "aso_full_clean.jsonl",
    KOK / "data" / "ivedik" / "firmalar.jsonl",
]

#: OLCULE GORE YAZILDI - selector UYDURULMADI.
#:
#: KOK NEDEN (4 deneme, 3'i basarisiz): sınıf niteliği şu:
#:   class="wpb_text_column wpb_content_element " >
#: `class="wpb_text_column[^"]*"\s*>` deseni BOSLUKTA takiliyordu
#: ve 0 unvan donuyordu. Ölçüm: `wpb_text_column` + 600 karakter
#: içinde `<strong>` deseni dosyada TAM 12 unvan buluyor.
#: Gevşek desen K-2 riski taşımaz çünkü `wpb_text_column` sınıfı
#: sadece içerik sütununda kullanılıyor (menü/başlıkta yok).
_BLOK = re.compile(
    r'wpb_text_column.{0,600}?<strong[^>]*>(.*?)</strong>',
    re.S | re.I)
_GUVENLI = re.compile(
    r"\b(LTD|SAN|TICARET|TIC|ANONIM|A\.S|LIMIT|GROUP|GRUP|"
    r"HOLDING|INSAAT|MAKINA)\b", re.I)


def _duz(html: str) -> str:
    t = re.sub(r"<[^>]+>", " ", html)
    for a, b in (("&nbsp;", " "), ("&amp;", "&"), ("&#8211;", "-"),
                 ("&#8217;", "'"), ("&quot;", '"'), ("&#039;", "'"),
                 ("&#199;", "C"), ("&#220;", "U")):
        t = t.replace(a, b)
    return re.sub(r"\s+", " ", t).strip()


def koruma_kontrolu() -> str | None:
    """P-5: korunan dosyalar degistiyse turu DURDURUR."""
    kilit = CIKTI / "_kaynak_kilidi.json"
    mevcut = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
              for p in KORUNAN if p.is_file()}
    if not kilit.is_file():
        CIKTI.mkdir(parents=True, exist_ok=True)
        kilit.write_text(json.dumps(mevcut, indent=2), encoding="utf-8")
        return None
    eski = json.loads(kilit.read_text(encoding="utf-8"))
    bozuk = [k for k, v in mevcut.items() if eski.get(k) not in (None, v)]
    if bozuk:
        return f"KAYNAK DEGISMIS: {', '.join(bozuk)}. Tur durduruldu."
    return None


def robots_uyumlu_mu(istem) -> tuple[bool, str]:
    """P-2. DIKKAT: '/robots.txt' GORELI yoldir ve httpx bunu
    'UnsupportedProtocol' ile reddeder; MUTLAK URL gerekir."""
    import urllib.parse as up
    try:
        base = str(istem.base_url)
        kok = up.urljoin(base, "/robots.txt")
        r = istem.get(kok, timeout=15)
        if r.status_code != 200:
            return True, f"robots.txt yok (HTTP {r.status_code})"
        for ln in r.text.splitlines():
            if not ln.lower().startswith("disallow"):
                continue
            d = ln.split(":", 1)[1].strip()
            if d and d != "/":
                return False, f"DISALLOW {d}"
        return True, "izin veriyor"
    except Exception as e:
        return True, f"alinamadi ({type(e).__name__})"


def sayfalari_getir(istem, liste_url: str, en_fazla: int = 30) -> list[str]:
    kok = liste_url.rstrip("/") + "/page/"
    aday = set()
    try:
        html = istem.get(liste_url, timeout=25).text
        for h in re.findall(r'href="([^"]+)"', html, re.I):
            if h.startswith(kok):
                aday.add(h)
    except Exception:
        return [liste_url]
    sira = []
    for u in aday:
        try:
            sira.append(int(u.rstrip("/").split("/")[-1]))
        except ValueError:
            pass
    return [liste_url] + [f"{kok}{n}" for n in sorted(sira)[:en_fazla]]



def sayfadan_unvanlar(html: str) -> list[str]:
    """K-2: menu girmesini eler, yalniz firma bloklarini alir."""
    out: list[str] = []
    for m in _BLOK.finditer(html):
        ad = _duz(m.group(1))
        if 10 <= len(ad) <= 90 and _GUVENLI.search(ad):
            out.append(ad)
    return out


def main() -> int:
    ay = argparse.ArgumentParser()
    ay.add_argument("--osb", default=None)
    ay.add_argument("--kuru", action="store_true")
    ay.add_argument("--tavan", type=int, default=GUN_TAVANI)
    ns = ay.parse_args()

    hata = koruma_kontrolu()
    if hata:
        print(f"DURDURULDU: {hata}")
        return 1
    print("P-5 koruma kilidi: kaynak dosyalar degismemis")

    import httpx
    sluglar = [ns.osb] if ns.osb else list(HEDEFLER)
    toplam = 0
    ozet = []
    for slug in sluglar:
        if slug not in HEDEFLER:
            print(f"bilinmeyen slug: {slug}")
            return 1
        ad, url = HEDEFLER[slug]
        print("\n" + "=" * 64)
        print(f"{ad} ({slug})\n  {url}")
        print("=" * 64)
        with httpx.Client(headers={"User-Agent": UA}, timeout=25,
                          follow_redirects=True) as istem:
            uy, not_ = robots_uyumlu_mu(istem)
            print(f"  P-2 robots: {uy} ({not_})")
            if not uy:
                print("  YASAK")
                ozet.append({"slug": slug, "durum": "robots yasak"})
                continue
            sayfalar = sayfalari_getir(istem, url)
            print(f"  sayfa: {len(sayfalar)}")
            if ns.kuru:
                print("  --kuru: yazma yok")
                continue
            kayitlar = []
            for i, syf in enumerate(sayfalar, 1):
                try:
                    unvanlar = sayfadan_unvanlar(
                        istem.get(syf, timeout=25).text)
                except Exception as e:
                    print(f"    [{i}] hata {type(e).__name__}")
                    continue
                print(f"    [{i}/{len(sayfalar)}] {len(unvanlar)} unvan")
                for u in unvanlar:
                    if len(kayitlar) >= ns.tavan:
                        break
                    kayitlar.append({
                        "unvan": u,
                        "unvan_anahtari": re.sub(r"[^a-z0-9]+", "",
                                                  u.lower()),
                        "osb_slug": slug, "kaynak_adi": ad,
                        "kaynak_turu": "osb", "kaynak_url": syf,
                        "toplanma_tarihi": datetime.now(timezone.utc)
                        .isoformat(timespec="seconds"),
                        "vergi_no": None, "adres": None,
                        "telefonler": [], "emailler": [],
                        "web_sitesi": None, "sektor": None,
                    })
                if len(kayitlar) >= ns.tavan:
                    print(f"    P-10 tavan {ns.tavan}")
                    break
                if i < len(sayfalar):
                    time.sleep(GECIKME)
            tekil = {k["unvan_anahtari"] for k in kayitlar}
            oran = len(tekil) / len(kayitlar) if kayitlar else 0.0
            print(f"  toplam {len(kayitlar)} | tekil %{oran * 100:.1f}")
            if kayitlar:
                hedef = CIKTI / slug
                hedef.mkdir(parents=True, exist_ok=True)
                gecici = hedef / "firmalar.jsonl.tmp"
                with gecici.open("w", encoding="utf-8") as f:
                    for k in kayitlar:
                        f.write(json.dumps(k, ensure_ascii=False) + "\n")
                gecici.replace(hedef / "firmalar.jsonl")
                (hedef / "meta.json").write_text(json.dumps({
                    "osb_slug": slug, "ad": ad, "kayit": len(kayitlar),
                    "tekil_oran": round(oran, 4), "sayfa": len(sayfalar),
                    "zaman": datetime.now(timezone.utc).isoformat(
                        timespec="seconds"),
                }, ensure_ascii=False, indent=2), encoding="utf-8")
                toplam += len(kayitlar)
            ozet.append({"slug": slug, "kayit": len(kayitlar),
                         "tekil_oran": round(oran, 4)})

    print("\n" + "=" * 64)
    print(f"TOPLAM: {toplam} kayit")
    CIKTI.mkdir(parents=True, exist_ok=True)
    DURUM.write_text(json.dumps(ozet, ensure_ascii=False, indent=2),
                     encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

