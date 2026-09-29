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
import hashlib
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

#: D-290 — GUECENLIK DUVARI (KAHIN: "eski database tekrar kirli ve
#: hatali olmasini istemiyorum, her turlu onlemi al").
#:
#: 1) Cikti TAMAMEN IZOLE: gonderiye ayri bir klasor, hicbir mevcut
#:    dosyaya dokunulmaz. Yeni kayit eski verinin UZERINE yazilmaz.
#: 2) Kaynak dosyalar SALT-OKUNUR: asagidaki koruma kilidi, her yazma
#:    denemesinden once SHA-256 dogrular. Biri degistiyse tur DURUR.
#: 3) Tarama hicbir SQLite/DB dosyasina dokunmaz (olculdu: 0 referans).

#: D-290: yalnizca BU dosyalar yazilir.
KAZANIM = DATA / "tamamlama_2026-09-29"
CIKTI = KAZANIM / "firmalar_tamamlanmis.jsonl"
DURUM = KAZANIM / "durum.json"
RAPOR = KAZANIM / "rapor.json"

#: D-290: korunacak kaynak dosyalar (SHA-256 ile kilitlenir).
#:
#: D-297: `firmalar_birlestirilmis.jsonl` KILIT LISTESINDEN CIKARILDI.
#: Sebep: bu bir KAYNAK degil, bir CIKTI dosyasidir; birlestirme
#: calistiginda (D-292 sayi sizintisi duzeltmesi) bilerek degisir.
#: Kilitlenmeye devam ederse tarama kalici olarak "kaynak degismis"
#: diyerek durur — yani asil koruma amacini (kaynak veri degismesin)
#: yanlis yere yonlendirir.
#:
#: KORUNAN = yalnizca OKUNAN kaynak dosyalar. Tarama bunlari hic
#: yazmaz; kilit, "baska biri bozdu mu" sorusunu yanitlar.
KORUNAN = [
    DATA / "firmalar_full.jsonl",        # ana liste (8.313) — salt okunur
    DATA / "firmalar_vkn_ekli.jsonl",    # mevcut detayli (5.040) — salt okunur
]
KILIT = DATA / "kaynak_kilidi.json"


def _sha(yol: pathlib.Path) -> str:
    import hashlib
    return hashlib.sha256(yol.read_bytes()).hexdigest()


def koruma_kontrolu() -> Optional[str]:
    """Korunan dosyalar degistiyse turu DURDURUR.

    D-290: "eski database tekrar kirli olmasin" talebinin TEK GARANTISI
    budur. Kilit dosyasi yoksa OLUSTURULUR (ilk calisma). Varsa
    karşılaştırılır; fark varsa hicbir sey yazilmaz.
    """
    if not KILIT.is_file():
        KILIT.parent.mkdir(parents=True, exist_ok=True)
        KILIT.write_text(json.dumps(
            {p.name: _sha(p) for p in KORUNAN if p.is_file()},
            indent=2), encoding="utf-8")
        return None
    eski = json.loads(KILIT.read_text(encoding="utf-8"))
    bozuk = [p.name for p in KORUNAN
             if p.is_file() and eski.get(p.name) not in (None, _sha(p))]
    if bozuk:
        return ("KAYNAK DOSYALAR DEGISMIS: " + ", ".join(bozuk) +
                ". Tur durduruldu; eski veri korunuyor.")
    return None


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


#: Gercek kullanici adi OLABILECEK ozel adlar: kisa/tek harf olanlar
#: ve altyazi/URL parcasi olanlar hesap DEGILDIR.
_GEcersiz_AD = frozenset({
    "sharer", "share", "home", "tr", "intent", "plugins", "accounts",
    "login", "signup", "about", "privacy", "terms", "help", "search",
    "explore", "p", "reel", "tv", "watch", "pg", "pg2", "settings",
    "ostimosb", "ostim-osb", "ostim_osb",
})


def _gercek_hesap_mi(ad: str) -> bool:
    """Bu metin gercek bir sosyal medya hesabi mi?

    D-286: pilot kosuda `{"instagram": "accounts"}` uretildi. Kaynak,
    sayfadaki gecici-login linki (`/accounts/login/?next=`) idi. Yani
    **dogru bir regex bile** sahte hesap uretebilir; sadece platformun
    kendi altyapisina ait segmentleri elemek gerekir.

    Kurallar:
      * ozel listede olan segmentler (login, accounts, share ...)
      * 1 haneden kisa adlar (anlamli bir kullanici adi olamaz)
      * OSTIM'in kendi hesaplari (firma hesabi DEGILDIR, D-285)
    """
    if not ad:
        return False
    a = ad.strip().lower()
    if a in _GEcersiz_AD or len(a) < 2:
        return False
    if a.startswith("ostim") or "ostim_osb" in a:
        return False
    return True


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
            # D-286 PILOT KIRP: `{"instagram": "accounts"}` cikti. Bu hesap
            # DEGIL, gecici-login linkinin (`/accounts/login/?next=`) son
            # parcasi. Duz metin olarak yazilsa bile gercek bir kullanici
            # adi uretmek mumkun degil; boyle degerler UZAKLASTIRILIR.
            if not _gercek_hesap_mi(bulunan):
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


#: P-1/P-2: robots.txt'te yasakli yol kalibrasi (canli olcum: Disallow
#: /admin/, /portal/, /auth/ — /firmalar/ SERBESTTIR).
ROBOTS_YASAK = ("/admin/", "/portal/", "/auth/")

#: Politika ac kapi degil: /firmalar/ yasaksa tur BASLAMAZ.
_ROBOTS_KAPALI = False


def robots_uyumlu_mu(yol: str = "/firmalar/") -> bool:
    """robots.txt uyumunu canli okuyarak dogrular (P-1/P-2).

    D-286: onceki surumde `robots_kontrol` adiyle bir parametre
    bekleniyordu ama HIC tanimli degildi; politika maddesi koda
    hic yansimamisti. Artik:
      * varsayilan AÇIK — uyum degilse tur baslamaz
      * `--robots-kontrol kapat` ile uzerebilir
    """
    global _ROBOTS_KAPALI
    if _ROBOTS_KAPALI:
        return True
    try:
        with httpx.Client(headers={"User-Agent": UA}, timeout=20,
                          follow_redirects=True) as c:
            r = c.get(f"{DIZIN}/robots.txt")
        if r.status_code != 200:
            print("  P-1: robots.txt okunamadi (HTTP "
                  f"{r.status_code}) — tur baslamadi")
            return False
        yasak = [ln.split(":", 1)[1].strip() for ln in r.text.splitlines()
                 if ln.lower().startswith("disallow:")]
    except Exception as e:
        print(f"  P-1: robots.txt hatasi ({type(e).__name__}) — "
              "tur baslamadi")
        return False

    cakisi = [y for y in yasak if yol.startswith(y)]
    if cakisi:
        print(f"  P-1: '{yol}' robots.txt'te YASAK ({cakisi}) — "
              "tur baslamadi")
        return False
    print(f"  P-1: robots.txt uygun ({yol} serbest; "
          f"yasakli: {', '.join(yasak) or '-'})")
    return True


def imza(html: str) -> str:
    """P-8: sayfa 'imzasi'. Ayni icerik iki kez geldiyse tespit icin.

    OSTIM bir hatada hep ayni hata/boş sayfayi dondurebilir. O durumda
    "firma sayisi" degil, ayni sayfa sayilir. Ozellikle liste sonu
    sayfalarinda (28-29) gozlenmistir: her sayfa kendini tekrarliyor.
    """
    t = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", html, flags=re.S | re.I)
    return hashlib.sha256(t.encode("utf-8", "ignore")).hexdigest()[:16]


def calistir(limit: Optional[int] = None) -> dict:
    """Eksik detaylari tamamlar.

    D-286: `robots_kontrol` parametresi KULLANICI TARAINDAN verilemiyordu
    (cagri imzasi ile uyusmuyordu). Politika P-1..P-10 `robots.txt` uyumunu
    sart koşuyor; bu yuzden kontrol `robots_uyumlu_mu()` ile **zorunlu adim**
    olarak eklendi ve `--robots-kontrol` bayragi ile kapatilabilir hâle
    getirildi (varsayilan: ACIK, yani kapalıysa tur baslamaz).
    """
    # D-290: en basta koruma kilidi. Kaynak dosyalardan biri degistiyse
    # hicbir is yapilmaz.
    ihlal = koruma_kontrolu()
    if ihlal:
        raise RuntimeError(f"D-290: {ihlal}")

    if not robots_uyumlu_mu():
        raise RuntimeError(
            "P-1/P-2: robots.txt uyumsuz. "
            "Tur baslatilmadi. (uzerinde gecmek icin --robots-kontrol kapat)")

    KAZANIM.mkdir(parents=True, exist_ok=True)   # D-290: izole cikti

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
    imzalar: dict[str, str] = {}              # P-8: slug -> sayfa imzasi
    tekrar_imza = 0                           # P-8 sayaci

    for i, slug in enumerate(hedef, 1):
        # P-3: istekler arasi GERCEK 2 sn bekleme. D-286'da tespit edildi:
        # `time.sleep` HIC CAGRILMAMISTI (beyaz satir) -> sunucuya kesintisiz
        # istek gidiyordu. Politika vaadi ile davranis uyusmuyordu.
        if i > 1:
            time.sleep(GECIKME)
        try:
            r = istek.get(f"{DIZIN}/firmalar/{slug}")

            if r.status_code in (401, 403):   # P-5
                raise RuntimeError(
                    f"P-5: erisim reddi HTTP {r.status_code}; TUR BIRAKILDI")
            r.raise_for_status()

            # P-8: sayfa imzasi tekrarinda DUR. Icerik birebir ayni ise
            # bu gercek bir firma detayi degil; sunucu ayni sayfayi
            # donduruyor demektir. K-1: sessizce tekrarlamak yasak.
            im = imza(r.text)
            if im in imzalar.values():
                tekrar_imza += 1
                islenmis[slug] = f"P8: imza tekrari ({im})"
                if tekrar_imza <= 3:
                    print(f"  P-8: ayni sayfa imzasi ({im}) -> atlandi")
                continue
            imzalar[slug] = im

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
            # D-291: surec ortada kesilirse yuzlerce kayit KAYBOLMASIN.
            # Kumulatif cikti burada da yazilir (atomik).
            _cikti_yaz(yeni)
            print(f"  [{i}/{len(hedef)}] okunan={len(yeni)} "
                  f"hata={hata_sayisi} ({time.time() - baslangic:.0f}s)")

    durum["islenen"] = islenmis
    durum_yaz(durum)

    cikti_ozet = None
    if yeni:
        m, e, t = _cikti_yaz(yeni)
        cikti_ozet = f"{m} mevcut + {e} yeni = {t}"
        print(f"  Cikti: {cikti_ozet}")

def _cikti_yaz(yeni: list[dict]) -> tuple[int, int, int]:
    """Kumulatif ciktiyi guvenli yazar. D-290 + D-291.

    D-290: dosya "w" ile YENIDEN yaziliyordu; `--limit` ile parcalanan
    bir turda onceki parcalar SILINIYORDU. Duzeltme: mevcut kayitlar
    okunur, slug ile birlestirilir, sonra tek seferde yazilir.

    D-291: yazma yalnizca TUR SONUNDA olurdu. Surec ortada kesilirse
    (asili, reboot, hata) o ana kadar toplanan yuzlerce kayit KAYBOLURDU.
    Artik her N kayitta kismi yazim yapilir (`KISIM_YAZIM`).
    """
    mevcut: list[dict] = []
    if CIKTI.is_file():
        for satir in CIKTI.read_text(encoding="utf-8").splitlines():
            if satir.strip():
                try:
                    mevcut.append(json.loads(satir))
                except json.JSONDecodeError:
                    continue
    birlesik = {m.get("slug"): m for m in mevcut if m.get("slug")}
    eklenen = 0
    for k in yeni:
        s = k.get("slug")
        if s and s not in birlesik:
            birlesik[s] = k
            eklenen += 1
    tumu = list(birlesik.values())
    gecici = CIKTI.with_suffix(".jsonl.tmp")     # K-3: atomik yazim
    with gecici.open("w", encoding="utf-8") as f:
        for k in tumu:
            f.write(json.dumps(k, ensure_ascii=False) + "\n")
    gecici.replace(CIKTI)                        # atomik degisim
    return len(mevcut), eklenen, len(tumu)

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
        "P8_tekrar_imza": tekrar_imza,          # D-286
        "P3_gecikme_saniye": GECIKME,
        "P3_uygulandi": True,                   # D-286: daha once hic cagrilmisti
        "D290_izole_klasor": str(KAZANIM),
        "D290_korunan_sha": {
            p.name: _sha(p) for p in KORUNAN if p.is_file()
        },
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
    ay.add_argument("--robots-kontrol", choices=["acik", "kapat"],
                    default="acik",
                    help="P-1/P-2 robots.txt kontrolu (varsayilan: acik)")
    ns = ay.parse_args()
    # D-286: politika varsayilan olarak ACIK; kapali ise tur baslamaz.
    globals()["_ROBOTS_KAPALI"] = (ns.robots_kontrol == "kapat")
    r = calistir(ns.limit)
    print("=" * 60)
    for a, b in r.items():
        if a != "calisma_zamani":
            print(f"  {a:24s} {b}")

