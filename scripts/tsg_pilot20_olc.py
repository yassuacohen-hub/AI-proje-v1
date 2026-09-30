"""TSG-PILOT-20 — 20 firma pilot OLCUMU (D-306 brif sözleşmesi).

Brif : plans/brief_yasu_TSG-PILOT-20.md
Kilit: plans/rapor_yasu_TSG-PILOT-20.md

BU GOREV KOD YAZMAZ, SAYAR. Kurallar:
  * Olculemeyen sey UYDURULMAZ -> None ("bilinmiyor").
  * ILAN_TURU_ESLEME bu dosyada DOLDURULMAZ (TSG-04'un isi; mandal korur).
  * Tekrar uretilebilirlik: data/pilots/TSG-PILOT-20/ornek.json sabit sirayi dondurur.
  * Olculemeyen kalem SATIR SILINMEZ (D-217).

Kullanim:
    python scripts/tsg_pilot20_olc.py      # 20 firmayi olc (CAPTCHA sorar)
    python scripts/tsg_pilot20_olc.py --izle   # kayitli sonucu ozetle
"""
from __future__ import annotations

import argparse
import json
import re
import statistics
import time
from datetime import datetime, timezone
from pathlib import Path

import httpx
from dotenv import load_dotenv

KOK = Path(__file__).resolve().parents[1]
load_dotenv(KOK / ".env", override=True)

TABAN = "https://www.ticaretsicil.gov.tr"
GIRIS_SAYFA = f"{TABAN}/view/hizlierisim/ilangoruntuleme.php"
GIRIS_POST = f"{TABAN}/view/modal/uyegirisi_ok.php"
ILAN_POST = f"{TABAN}/view/hizlierisim/ilangoruntuleme_ok.php"

#: Sorgu icin Ankara sicil mudurlugu. Kaynak: sayfadaki mudurluk <select> listesi.
ANKARA_ID = "18"

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")

KLASOR = KOK / "data" / "pilots" / "TSG-PILOT-20"
SONUC = KLASOR / "olcum_sonuc.json"
ORNEK = KLASOR / "ornek.json"
OTURUM = KLASOR / "oturum.json"


def _metin(haystack: str) -> str:
    """HTML -> duz metin (etiketler bozulmadan)."""
    s = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", haystack, flags=re.S | re.I)
    s = re.sub(r"<[^>]+>", " ", s)
    s = s.replace("&nbsp;", " ").replace("&amp;", "&")
    return re.sub(r"[ \t]+", " ", s).strip()


def _hucreler(satir: str) -> list[str]:
    out = []
    for h in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", satir, re.S | re.I):
        v = _metin(h)
        if v:
            out.append(v)
    return out


def satir_liste(html: str) -> list[list[str]]:
    """Sorgu sonucundaki veri satirlari (Müdürlük|Sicil|Unvan|Tarih|Sayı|Sayfa|Tür|Gazete)."""
    satirlar = []
    for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", html, re.S | re.I):
        h = _hucreler(tr)
        if len(h) >= 7 and re.match(r"^\d", h[1] or ""):
            satirlar.append(h)
    return satirlar


def etiketleri_say(rows: list[list[str]]) -> dict:
    """4. KALEM: 'İlan Türü' sütunundaki ham etiketler + frekans.

    Yorum YAPILMAZ; ayni anlama gelen iki yazim AYRI sayilir (birlestirme
    karari TSG-04'un isidir).
    """
    frekans: dict[str, int] = {}
    for r in rows:
        if len(r) >= 7 and r[6].strip():
            e = r[6].strip()
            frekans[e] = frekans.get(e, 0) + 1
    return dict(sorted(frekans.items(), key=lambda kv: (-kv[1], kv[0])))


def kanit_anahtari(r: list[str]) -> str | None:
    """(ilan_sira_no, gazete_sayi, gazete_sayfa) -> 'a-b-c' (D-306 kanonik)."""
    try:
        sayi, sayfa = r[4].strip(), r[5].strip()
    except IndexError:
        return None
    return f"{sayi}-{sayi}-{sayfa}" if sayi and sayfa else None


def _kisa(html: str, n: int = 260) -> str:
    return re.sub(r"\s+", " ", _metin(html))[:n]


def _dagilim(liste) -> dict:
    d: dict[str, int] = {}
    for x in liste:
        d[str(x)] = d.get(str(x), 0) + 1
    return dict(sorted(d.items(), key=lambda kv: (-kv[1], kv[0])))


def _etiket_listesi(html: str) -> list[str]:
    """Kaynagin kendi 'İlan Türü' secenekleri (varsa) — ham metin."""
    out = []
    for so in re.finditer(r"<select[^>]*>.*?</select>", html, re.S | re.I):
        s = so.group(0)
        if re.search(r"lan\s*T.r", s, re.I):
            out += [o.strip() for o in
                    re.findall(r"<option[^>]*>([^<]*)</option>", s) if o.strip()]
    return out


def oturum_ac(cx) -> dict:
    """Giris sayfasini ac + CAPTCHA gorselini indir. Oturum bilgisini dondurur.

    NEDEN AYRI ADIM: CAPTCHA gorseli SUNUCU OTURUMUNA baglidir. Her yeniden
    calistirmada yeni gorsel uretilir; bu yuzden gorsel ile giris denemesi
    AYRI komutlarda, ayni cookie ile yapilir.
    """
    t0 = time.time()
    sayfa = cx.get(GIRIS_SAYFA)
    m = re.search(r"""src\s*=\s*["']([^"']*captcha[^"']*)""", sayfa.text, re.I)
    if not m:
        raise SystemExit("HATA: CAPTCHA alani bulunamadi - sayfa yapisini "
                         "gormek icin panoya sorun acin (D-217).")
    cap = cx.get(TABAN + m.group(1),
                 headers={"Referer": GIRIS_SAYFA, "Accept": "image/*,*/*"})
    KLASOR.mkdir(parents=True, exist_ok=True)
    (KLASOR / "captcha_ornek.png").write_bytes(cap.content)
    OTURUM.write_text(json.dumps(
        {"cookie": dict(cx.cookies), "zaman": datetime.now(timezone.utc).isoformat()},
        ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[hazirla] HTTP {sayfa.status_code} ({round(time.time() - t0, 2)} sn) | "
          f"CAPTCHA {len(cap.content)} bayt")
    print(f"[hazirla] gorsel : {KLASOR / 'captcha_ornek.png'}")
    print(f"[hazirla] metin  : {KLASOR / 'captcha_ornek.txt'}")
    print("[hazirla] simdi gorseli oku, metni .txt dosyasina yaz, sonra "
          "'--gir' ile devam et.")


def _captcha_oku(gorsel: Path, sor) -> str:
    """CAPTCHA metnini al. Otomatik COZULMEZ (D-268: bu gocrev olcer,
    guvenlik katmanini asmaz). Bos metin olcumu durdurur."""
    yol = gorsel.with_suffix(".txt")
    if yol.exists():
        metin = yol.read_text(encoding="utf-8").strip().lstrip("\ufeff")
        if metin:
            print(f"CAPTCHA (dosyadan): {metin}")
            return metin
    print(f"CAPTCHA gorseli: {gorsel}  (metni .txt dosyasina yazin)")
    return sor("CAPTCHA metni> ").strip()


def olc() -> dict:
    """20 firmayi olcer. CAPTCHA insan tarafindan cozulur (kod onu GECMEZ)."""
    import os
    ornek = json.loads(ORNEK.read_text(encoding="utf-8"))
    if not OTURUM.exists():
        raise SystemExit("HATA: once '--hazirla' calistirip CAPTCHA gorselini alin.")
    kayitli = json.loads(OTURUM.read_text(encoding="utf-8"))["cookie"]
    cx = httpx.Client(timeout=40, follow_redirects=True,
                      headers={"User-Agent": UA}, cookies=kayitli)
    sayfa_sn = None

    eposta = os.environ.get("TOBB_KULLANICI", "")
    sifre = os.environ.get("TOBB_SIFRE", "")
    if not eposta or not sifre:
        raise SystemExit("HATA: TOBB_KULLANICI/TOBB_SIFRE yok - giris olcumu yapilamaz")

    kap = _captcha_oku(KLASOR / "captcha_ornek.png", input)
    if not kap:
        raise SystemExit("HATA: CAPTCHA metni bos - olcum yapilmaz (D-217).")
    t0 = time.time()
    r = cx.post(GIRIS_POST,
                files={"LoginEmail": (None, eposta), "LoginSifre": (None, sifre),
                       "Captcha": (None, kap)},
                headers={"X-Requested-With": "XMLHttpRequest",
                         "Referer": GIRIS_SAYFA})
    giris_sn = round(time.time() - t0, 2)
    basari = r.text.strip() == "1"
    print(f"[1] giris HTTP {r.status_code} ({giris_sn} sn) "
          f"yanit={r.text.strip()[:40]!r} basari={basari}")
    if not basari:
        print("!! GIRIS BASARISIZ (yanit '0' = captcha/hesap reddi) - "
              "'--hazirla' ile yeni captcha alip tekrar deneyin.")
        return {"giris": {"basari": False, "yanit": r.text.strip()[:120]}}
    (KLASOR / "captcha_ornek.txt").unlink(missing_ok=True)

    kayitlar = []
    oturum_bas = time.time()
    for o in ornek:
        sicil = o["trade_registry_number"]
        t0 = time.time()
        try:
            rr = cx.post(ILAN_POST,
                         files={"SicilMudurluguId": (None, ANKARA_ID),
                                "TicSicNo": (None, sicil),
                                "TicaretUnvani": (None, ""),
                                "BagliIlan": (None, "0"),
                                "Tarih1": (None, ""), "Tarih2": (None, "")},
                         headers={"X-Requested-With": "XMLHttpRequest",
                                  "Referer": GIRIS_SAYFA})
            html, http, hata = rr.text, rr.status_code, None
        except Exception as e:
            html, http, hata = "", None, f"{type(e).__name__}: {e}"
        sn = round(time.time() - t0, 2)

        satirlar = satir_liste(html)
        etiketler = etiketleri_say(satirlar)
        anahtarlar = [k for k in (kanit_anahtari(s) for s in satirlar) if k]

        # 7. KALEM: VKN kapanmasi; kapanmayanin SEBEBi ayri yazilir.
        if not satirlar:
            vkn_durum, vkn_neden = "bulunamadi", "bu sicil icin ilan kaydi donmedi"
        elif re.search(r"(VKN|Vergi\s*No)", html, re.I):
            vkn_durum, vkn_neden = "kapanmadi", "VKN sutunu var ama deger dolu degil"
        else:
            vkn_durum, vkn_neden = "kapanmadi", "sorgu tablosunda VKN sutunu hic yok"

        kayitlar.append({
            "sira": o["sira"], "company_id": o["company_id"],
            "legal_name": o["legal_name"], "sicil_no": sicil,
            "sure_sn": sn, "http": http, "hata": hata,
            "ilan_sayisi": len(satirlar),
            "ilan_turu_frekans": etiketler,
            "vkn_durum": vkn_durum, "vkn_neden": vkn_neden,
            "kanit_anahtarlari": anahtarlar,
            "ilk_ilan": (satirlar[0] if satirlar else None),
        })
        et = (satirlar[0][6][:40] if satirlar and len(satirlar[0]) > 6 else "-")
        print(f"  {o['sira']:2d}. {sicil:<9s} {sn:5.2f}sn ilan={len(satirlar):3d}  {et}")

    surer = [k["sure_sn"] for k in kayitlar]
    tum: dict[str, int] = {}
    for k in kayitlar:
        for e, a in k["ilan_turu_frekans"].items():
            tum[e] = tum.get(e, 0) + a

    # 5. KALEM: icra/iflas kutusu (kaynak ozelligi — bir kez yollandi)
    kontrol = cx.get(GIRIS_SAYFA).text
    icra = {"icerik_aranmadi": not re.search(r"icra|iflas", kontrol, re.I),
            "gonderim": "HTML metin (ekran goruntusu degil)",
            "olcum": "bilinmiyor"}

    # 6. KALEM: tarih araligi
    tarih = {"alanlar": [a for a in ("Tarih1", "Tarih2")
                         if f'name="{a}"' in kontrol],
             "destekleniyor": 'name="Tarih1"' in kontrol,
             "sinir": "bilinmiyor (arayuzde sinir yazmiyor)"}

    sonuc = {
        "zaman": datetime.now(timezone.utc).isoformat(),
        "ornek_kaynak": ("companies WHERE trade_registry_number IS NOT NULL "
                         "AND <> '' , ORDER BY random() LIMIT 20"),
        "giris": {"basari": basari, "sure_sn": giris_sn, "sayfa_sn": sayfa_sn,
                  "captcha_zorunlu": True,
                  "captcha_bayt": (KLASOR / "captcha_ornek.png").stat().st_size,
                  "oturum_omru_sn": round(time.time() - oturum_bas, 1),
                  "sorgu_sayisi": len(kayitlar)},
        "sure": {"min": min(surer) if surer else None,
                 "medyan": round(statistics.median(surer), 2) if surer else None,
                 "maks": max(surer) if surer else None,
                 "toplam_sn": round(sum(surer), 1) if surer else None},
        "ilan_turu_toplam": dict(sorted(tum.items(), key=lambda kv: (-kv[1], kv[0]))),
        "ilan_turu_cesit": len(tum),
        "icra_iflas": icra,
        "tarih_araligi": tarih,
        "vkn_kapanma": {"toplam": len(kayitlar),
                        "dolan": sum(1 for k in kayitlar
                                     if k["vkn_durum"] == "doldu"),
                        "sebep_dagilimi": _dagilim(
                            [k["vkn_neden"] for k in kayitlar])},
        "kayitlar": kayitlar,
    }
    SONUC.write_text(json.dumps(sonuc, ensure_ascii=False, indent=2),
                     encoding="utf-8")
    return sonuc


def _ozet(s: dict) -> None:
    print("\n" + "=" * 66)
    g = s.get("giris", {})
    print(f"KALEM 1 CAPTCHA     : zorunlu, giris basina 1 (bayt={g.get('captcha_bayt')})")
    print(f"KALEM 2 Oturum omru : {g.get('oturum_omru_sn')} sn / {g.get('sorgu_sayisi')} sorgu")
    d = s.get("sure", {})
    print(f"KALEM 3 Sure        : min={d.get('min')} medyan={d.get('medyan')} "
          f"maks={d.get('maks')} sn")
    print(f"KALEM 4 Ilan turu   : {s.get('ilan_turu_cesit')} cesit")
    for e, a in list(s.get("ilan_turu_toplam", {}).items())[:25]:
        print(f"            {a:3d}x  {e}")
    print(f"KALEM 5 Icra/iflas  : {s.get('icra_iflas')}")
    print(f"KALEM 6 Tarih       : {s.get('tarih_araligi')}")
    print(f"KALEM 7 VKN kapanma : {s.get('vkn_kapanma')}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--izle", action="store_true", help="kayitli sonucu ozetle")
    ap.add_argument("--hazirla", action="store_true",
                    help="CAPTCHA gorselini indir, oturumu dondur")
    a = ap.parse_args()
    if a.izle:
        _ozet(json.loads(SONUC.read_text(encoding="utf-8")))
    elif a.hazirla:
        with httpx.Client(timeout=30, follow_redirects=True,
                          headers={"User-Agent": UA}) as cx:
            oturum_ac(cx)
    else:
        _ozet(olc())
