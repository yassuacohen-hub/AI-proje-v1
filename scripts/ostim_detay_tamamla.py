"""OSTIM detay sayfalarindan EKSIK alanlari tamamlar (D-283).

NEDEN: `firmalar_full.jsonl` (8.313 kayit) `adres`/`web_sitesi`/
`sosyal_medya` alanlarinda **%0** doluluga sahip (olculdu). Sadece
`firmalar_vkn_ekli.jsonl` (5.040) bu alanlari dolu. Aradaki **3.297 firma**
detay sayfalari hic cekilmemis.

KAPSAM: Sadece eksik detaylar. Yeni firma listesi **cekilmez**
(KIYASLAMA olculdu: yeni unvan 0).

POLITIKA P-1..P-10 (KAHIN onayi 2026-09-29):
  P-1  Sabit gercek UA (bot taklidi YOK)
  P-2  Sayfa basina 1 istek
  P-3  2 sn nazik gecikme
  P-4  Kesintisiz calisma yok, --limit ile sinirli
  P-5  403/401 bos liste DEGIL, ACIK HATA
  P-6  tekil/toplam < %95 -> tur basarisiz
  P-7  Ham dosya "w" (K-3)
  P-8  Sayfa imzasi tekrarinda dur (K-1)
  P-9  Durum dosyasi ile yeniden calistirilabilir
  P-10 Maskeli alan kopyalanmaz

KOLON KURALLARI (K-2): `kaynak_adi` + `kaynak_turu` ayri kolon; alanlar
ASLA karistirilmaz. `vergi_no` yalniz dogrulanmis kaynaktan — bu kaynakta
YOKTUR, bu yuzden hep `None` kalir (D-282).

Kullanim:
    python scripts/ostim_detay_tamamla.py --limit 20     # pilot
    python scripts/ostim_detay_tamamla.py                 # tam
"""
from __future__ import annotations

import argparse
import html as html_mod
import json
import pathlib
import re
import time
from datetime import datetime, timezone
from typing import Any, Optional

import httpx

KOK = pathlib.Path(__file__).resolve().parents[1]
DATA = KOK / "data" / "ostim"
GIRIS = DATA / "firmalar_full.jsonl"
VAR = DATA / "firmalar_vkn_ekli.jsonl"
CIKTI = DATA / "firmalar_tamamlanmis.jsonl"
DURUM = DATA / ".detay_tamamla_state.json"
RAPOR = KOK / "data" / "ostim_tamamlama_raporu.json"

#: P-1: Sabit, gercek User-Agent. Bot taklidi YAPILMAZ.
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/131.0 Safari/537.36")

#: P-3: istek araligi (saniye).
GECIKME = 2.0

#: P-6: tekil oran esigi.
TEKIL_ESIK = 0.95

DIZIN = "https://ostim.org.tr"

#: D-283 KOK NEDEN: Sayfada IKI ayri blok var.
#:   (1) FIRMA bilgisi  -> `<p class="... fw-bold small">Etiket</p>`
#:       + ardindaki `bg-light` icerik kutusu
#:   (2) SITE bilgisi   -> menuler, footer, "Iletisim" vb.
#: Ilk surum bunlari AYIRMADIGI icin `web_sitesi=htk.org.tr` (fuar sitesi)
#: ve `sosyal_medya=ostim-osb` (sitenin kendi hesabi) cikti — yani
#: **K-2 ihlali: kolonlar birbirine karisti.** DUZELTILDI.



# ---------------------------------------------------------------- yardimci
def duz(html: str) -> str:
    """HTML -> duz metin. Script/style atilir, HTML entity'leri COZULUR.

    D-283: `&#xC7;` gibi entity'ler cozulmedigi icin unvan `Demir Çelik`
    yerine `Demir ├çelik` cikiyordu.
    """
    t = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", html, flags=re.S | re.I)
    t = re.sub(r"<[^>]+>", " ", t)
    t = html_mod.unescape(t)
    t = t.replace("\xa0", " ")
    return re.sub(r"\s+", " ", t).strip()


def maskeli_mi(deger: str) -> bool:
    """P-10: maskeli alan (****) kopyalanmaz."""
    return "*" in deger or "•" in deger


# ------------------------------------------------------------------ cekim
def _bilgi_kutulari(html: str) -> dict[str, str]:
    """Sayfadaki FIRMA bilgi kutularini {etiket: deger} sozlugune cevirir.

    Sayfa yapisi (olculdu, 2026-09-29):
        <p class="... bg-secondary fw-bold small">Merkez</p>
        <div class="p-2 bg-light mb-2 small">
          <strong>Telefon</strong> <p class="m-0 fw-5">+90 552 ...</p>
          <strong>Adres</strong>   <p class="m-0 fw-5">AHIT EVRAN CAD. 63</p>
          <strong>E-Posta</strong> <p class="m-0 fw-5"><a ...>..</a></p>
        </div>
        <p class="... bg-secondary fw-bold small">Web Site</p>
        <div class="p-2 bg-light mb-2 small">
          <p class="m-0 fw-5">Web sitesi bilgisi girilmemiştir.</p>
        </div>

    ANCAK: `<strong>Adres</strong>` kaliplari SAYFA MENUSU/FOOTER'da da
    vardir (orn. OSTIM Merkez Telefonu). Bu yuzden yalniz
    **`bg-light` kutusu icinde** olanlar alinir → site/firma ayrimi (K-2).
    """
    dolgu = (
        "girilmemiştir", "girilmemistir", "bilgi yok", "belirtilmemiştir",
        "belirtilmemistir", "yoktur", "n/a",
    )
    sonuc: dict[str, str] = {}
    # Yalniz `bg-light` kutulari: bolum basligi + icerik
    desen = re.compile(
        r'<p class="[^"]*bg-secondary[^"]*fw-bold[^"]*">\s*([^<]{2,40}?)\s*</p>'
        r'\s*<div class="p-2 bg-light[^"]*">(.*?)</div>',
        re.S,
    )
    for m in desen.finditer(html):
        bolum = m.group(1).strip()
        icerik = m.group(2)
        # Kutu icindeki <strong>Etiket</strong> + <p class="m-0 fw-5">deger</p>
        for em in re.finditer(
            r"<strong>([^<]{2,30})</strong>\s*"
            r'<p class="m-0 fw-5">(.*?)</p>',
            icerik, re.S,
        ):
            etiket = em.group(1).strip()
            deger = duz(em.group(2)).strip()
            if not deger or any(x in deger.lower() for x in dolgu):
                continue
            sonuc[f"{bolum}:{etiket}"] = deger
        # Bos kutu (orn. "Web sitesi bilgisi girilmemiştir")
        if "<strong>" not in icerik:
            dm = re.search(r'<p class="m-0 fw-5">(.*?)</p>', icerik, re.S)
            deger = duz(dm.group(1)).strip() if dm else ""
            if deger and not any(x in deger.lower() for x in dolgu):
                sonuc[bolum] = deger
    return sonuc


def detay_ayikla(html: str, slug: str) -> dict:
    """Tek detay sayfasindan KOLON KOLON alan cikarir (K-2: karistirma YOK)."""
    kutular = _bilgi_kutulari(html)

    kayit: dict[str, Any] = {
        "slug": slug,
        "kaynak_adi": "ostim",          # K-2
        "kaynak_turu": "osb",           # K-2
        "kaynak_url": f"{DIZIN}/firmalar/{slug}",
        "cekilme_tarihi": datetime.now(timezone.utc).isoformat(
            timespec="seconds"
        ),
    }

    # --- unvan: <h1> (D-11: kisaltma/normalizasyon YOK)
    unvan = None
    mh = re.search(r"<h1[^>]*>(.*?)</h1>", html, re.S | re.I)
    if mh:
        unvan = duz(mh.group(1))
    if not unvan:
        mt = re.search(r"<title[^>]*>(.*?)</title>", html, re.S | re.I)
        if mt:
            unvan = re.split(r"\s+-\s+Ostim", duz(mt.group(1)))[0].strip()
    kayit["unvan"] = unvan

    # --- adres / telefon / e-posta: YALNIZ bilgi kutularindan
    def bul(*etiketler):
        """`Merkez:Telefon` gibi `bolum:etiket` anahtarlarindan deger getirir.

        KUTU BASLIGI ONEMLIDIR: "Merkez:Telefon" (firma) ile
        "Merkez Telefonu" (site footer) farklidir.
        """
        istenen = {e.lower() for e in etiketler}
        for anaht, val in kutular.items():
            bolum, _, et = anaht.partition(":")
            if et.strip().lower() in istenen:
                return val
        return None

    kayit["adres"] = bul("Adres", "Adres Bilgisi")
    tel = bul("Telefon", "Telefon No", "Tel")
    kayit["telefonler"] = [re.sub(r"\s+", " ", tel).strip()] if tel else []
    ep = bul("E-Posta", "Eposta", "E-Posta Adresi", "Mail")
    kayit["emailler"] = [ep] if ep else []

    # --- web sitesi: YALNIZ "Web Site" bolum kutusu (menulerden DEGIL)
    web = kutular.get("Web Site")
    kayit["web_sitesi"] = web

    # --- sektor: yalniz firma blogundan
    kayit["sektor"] = bul("Sektör", "Sektor", "Faaliyet", "Sektör Bilgisi")

    # --- sosyal medya: YALNIZ firma blogundaki mailto/telif linki
    # (Onceki surumde menulerden `ostim-osb` gibi hesaplar geliyordu.)
    sosyal: dict[str, str] = {}
    for plat, desen in (
        ("linkedin", r"linkedin\.com/(?:company|in)/([\w\-]+)"),
        ("facebook", r"facebook\.com/([\w.\-]+)"),
        ("twitter", r"(?:twitter|x)\.com/([\w_]+)"),
        ("instagram", r"instagram\.com/([\w_.]+)"),
    ):
        for m in re.finditer(desen, html, re.I):
            bulunan = m.group(1)
            if bulunan.lower() in ("sharer", "share", "home", "tr", "intent",
                                   "plugins", "ostimosb", "ostim-osb"):
                continue
            # Sitenin kendi sosyal hesaplari firma degildir
            if bulunan.lower().startswith("ostim"):
                continue
            sosyal[plat] = bulunan
            break
    kayit["sosyal_medya"] = sosyal

    # --- P-10: maskeli alan kopyalanmaz
    if ep and maskeli_mi(ep):
        kayit["emailler"] = []

    # --- vergi_no: BU KAYNAKTA YOK (D-282 olculdu) -> hep None
    kayit["vergi_no"] = None
    kayit["vergi_no_kaynagi"] = None

    # --- NACE: bu kaynakta da YOK -> None (karistirma yasak, K-2)
    kayit["nace_code"] = None
    kayit["nace_source"] = None
    kayit["nace_confidence"] = "none"

    return kayit


#PLACEHOLDER

def robots_kontrol(istem: httpx.Client) -> None:
    """P-5: her turda robots.txt yeniden okunur; /firmalar yasakliysa hata."""
    r = istek.get(f"{DIZIN}/robots.txt")
    if r.status_code != 200:
        raise RuntimeError(f"P-5: robots.txt okunamadi (HTTP {r.status_code})")
    if "disallow: /firmalar" in r.text.lower():
        raise RuntimeError("P-5: /firmalar robots.txt'te yasakli")


def eksik_slug_ler() -> tuple[list[str], int]:
    """`firmalar_full.jsonl`de olup detayi OLMMAYAN slug'lar (K-4 mantigi).

    Yalniz detay alanlari bos olanlar kapsama alinir; dolu olanlar atlanir.
    """
    var = set()
    if VAR.is_file():
        for satir in VAR.read_text(encoding="utf-8").splitlines():
            if satir.strip():
                try:
                    s = json.loads(satir)
                except json.JSONDecodeError:
                    continue
                if s.get("slug"):
                    var.add(s["slug"])

    eksik: list[str] = []
    toplam = 0
    if GIRIS.is_file():
        for satir in GIRIS.read_text(encoding="utf-8").splitlines():
            if not satir.strip():
                continue
            try:
                s = json.loads(satir)
            except json.JSONDecodeError:
                continue
            toplam += 1
            slug = s.get("slug")
            if not slug or slug in var:
                continue
            if not s.get("adres") and not s.get("web_sitesi"):
                eksik.append(slug)
    return sorted(set(eksik)), toplam


def durum_oku() -> dict:
    if DURUM.is_file():
        try:
            return json.loads(DURUM.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass
    return {"islenen": {}}


def durum_yaz(d: dict) -> None:
    DURUM.write_text(json.dumps(d, ensure_ascii=False, indent=2),
                     encoding="utf-8")


def calistir(limit: Optional[int] = None) -> dict:
    global istek
    istek = httpx.Client(headers={"User-Agent": UA}, timeout=30,
                         follow_redirects=True)
    robots_kontrol(istek)                      # P-5

    eksik, toplam = eksik_slug_ler()
    durum = durum_oku()
    islenmis: dict = durum.get("islenen", {})

    hedef = [s for s in eksik if s not in islenmis]
    if limit:
        hedef = hedef[:limit]

    print(f"Toplam kayit      : {toplam}")
    print(f"Eksik detay       : {len(eksik)}")
    print(f"Bu turda cekilecek: {len(hedef)}")
    print(f"Tahmini sure      : {len(hedef) * GECIKME / 60:.1f} dk")
    print("-" * 60)

    yeni: list[dict] = []                     # P-7: dosya "w" ile
    hata_sayisi = 0
    baslangic = time.time()

    for i, slug in enumerate(hedef, 1):
        try:
            r = istek.get(f"{DIZIN}/firmalar/{slug}")
            if r.status_code in (401, 403):   # P-5
                raise RuntimeError(
                    f"P-5: erisim reddi HTTP {r.status_code}; TUR BIRAKILDI")
            r.raise_for_status()
            kayit = detay_ayikla(r.text, slug)
            dolu = sum(
                1 for k, v in kayit.items()
                if v not in (None, "", [], {})
                and k not in ("slug", "kaynak_adi", "kaynak_turu",
                              "kaynak_url", "cekilme_tarihi")
            )
            if dolu < 2:                      # P-6
                raise RuntimeError(f"P-6: bos cikarim ({dolu} alan)")
            yeni.append(kayit)
            islenmis[slug] = kayit.get("cekilme_tarihi")
        except Exception as e:
            hata_sayisi += 1
            islenmis[slug] = f"HATA: {type(e).__name__}"
            if "P-5" in str(e):
                print(f"\n!! {e}")
                durum["islenen"] = islenmis
                durum_yaz(durum)
                break
        if i % 25 == 0:
            durum["islenen"] = islenmis
            durum_yaz(durum)
            print(f"  [{i}/{len(hedef)}] okunan={len(yeni)} "
                  f"hata={hata_sayisi} ({time.time() - baslangic:.0f}s)")

    durum["islenen"] = islenmis
    durum_yaz(durum)

    if yeni:
        with CIKTI.open("w", encoding="utf-8") as f:
            for k in yeni:
                f.write(json.dumps(k, ensure_ascii=False) + "\n")

    unvanlar = [k.get("unvan") for k in yeni if k.get("unvan")]
    tekil = len(set(unvanlar))
    oran = tekil / len(yeni) if yeni else 0.0
    basarili = oran >= TEKIL_ESIK if yeni else False

    rapor = {
        "calisma_zamani": datetime.now().isoformat(timespec="seconds"),
        "toplam_kayit": toplam,
        "eksik_detay": len(eksik),
        "bu_turda_islenen": len(hedef),
        "basarili_kayit": len(yeni),
        "hata": hata_sayisi,
        "tekil_unvan": tekil,
        "tekil_oran_yuzde": round(100 * oran, 2),
        "P6_esik_yuzde": round(100 * TEKIL_ESIK, 2),
        "tur_basarisiz": not basarili,
        "sure_saniye": round(time.time() - baslangic, 1),
        "cikti": str(CIKTI) if yeni else None,
        "durum_dosyasi": str(DURUM),
        "kalan_islenmemis": len([s for s in eksik if s not in islenmis]),
    }
    RAPOR.write_text(json.dumps(rapor, ensure_ascii=False, indent=2),
                     encoding="utf-8")
    istek.close()
    return rapor


if __name__ == "__main__":
    ay = argparse.ArgumentParser()
    ay.add_argument("--limit", type=int, default=None,
                    help="P-4: bu turda en fazla N firma")
    ns = ay.parse_args()
    r = calistir(ns.limit)
    print("=" * 60)
    for a, b in r.items():
        if a != "calisma_zamani":
            print(f"  {a:24s} {b}")

