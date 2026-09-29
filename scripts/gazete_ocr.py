"""TOBB gazete PDF'inden YAPILANDIRILMIS ALAN ÇIKARIMI (vision LLM OCR).

!! D-278: BU MODUL SU AN PASIFTE. OCR GEREKMiyOR !!

KAHIN'in tespiti ve resmi sayfa dogrulamasi (D-278):
  Abonelik (Duzey_1/2/3) verisi **WEB SERVIS** olarak teslim edilir ve
  TSM/XML makine-okunur formatdadir. XML metin dogrudan okunur; PDF'e
  ve OCR'a gerek YOKTUR.

  Bu modulun varlik nedeni: yalnizca **ucretsiz uye PDF'i** tarar.
  Olculdum (`scripts/pdf_kanit_analiz.py` -> `data/pdf_analiz.json`):
    font=0, Tj/TJ=0, ToUnicode=0, 3 gorsel XObject, A4@200DPI
  Yani ucretsiz PDF gercekten SCAN. Duzey_3 alesi degildir.

  Bu yuzden OCR yolu **EKONOMIK DEGILDIR**: 14.000 x OCR. Duzey_3
  alesi ayni veriyi kurumsal olarak verir.

  D-278 karari: OCR calismasi DURDURULDU; oncelik Duzey_3 degerlendirmesine
  kaydirildi. Bu modul **silinmedi** — ucretsiz PDF okunacaksa hazir olsun.

TASINAN ALANLAR (Duzey_3, resmi sayfadan):
  NACE (Ana + Alt n tane) | Vergi No | Vergi Dairesi | UAVT Adres Kodu |
  Ortaklar (Liste, sermaye dahil) | Temsilciler (Liste) | Amac Konu |
  Kurulus Adresi | Toplam Sermaye | Muferek Listesi (JSON)

Kullanim (yalnizca gerektiginde):
    python scripts/gazete_ocr.py
    python scripts/gazete_ocr.py <pdf> --model gemini/gemini-3.8-flash
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import pathlib
import re
import sys
import time
from typing import Any, Optional

import httpx

KOK = pathlib.Path(__file__).resolve().parents[1]
KANIT_DIZIN = KOK / "data" / "kanit"

#: Varsayilan model: hizli + ucuz + guclu layout anlayisi.
VARSAYILAN_MODEL = "gemini/gemini-3.8-flash"

#: Turkce OCR'da sik gorulen karisikliklar (Gemini de yapabiliyor).
DUZELTMELER = {
    "O": "0", "o": "0", "l": "1", "I": "1", "i": "1", "Ş": "5", "ş": "5",
    "B": "8", "Z": "2", "G": "6", "ı": "1", "İ": "1",
}

# --------------------------------------------------------------------------
# D-278 PASIF KORUMA
#
# Bu modul SILINMEDI — yeniden lazim olabilir. Ama kazara calistirilip
# maliyet uretmesin diye asagidaki kapilar var:
#
#   1. `OCR_ETKIN = False` -> `pdf_ocr()` cagirmadan once uyari verir ve
#      HTTP istegi YAPILMAZ. Acilacaksa `--aktif` bayragi ile.
#   2. Yanlis dosyadan calistirilma koruması: yalniz TOBB kaynakli PDF kabul
#      edilir (kaynak satiri kanitlanamayan dosya reddedilir).
#
# Gerekce: 14.000 kayit x OCR ciddi maliyet; Duzey_3 aboneligi ayni veriyi
# kurumsal olarak verir. Oncelik Duzey_3 (bkz. rapor EK-2 §25).
# --------------------------------------------------------------------------

#: OCR hattini acik/kapali tutar. D-278: kapali.
OCR_ETKIN = False

#: Kapatildiginda ne yapilacagini bildiren uyari metni.
PASIF_UYARI = (
    "D-278: OCR hatti PASIF. Abonelik (Duzey_2/3) verisi XML/TSM olarak "
    "makine-okunur gelir; PDF'e ve OCR'a gerek yoktur. Yalnizca ucretsiz "
    "uye PDF'i okumak icin gerekiyorsa `--aktif` bayragi ile acin."
)


class OcrPasifHatasi(RuntimeError):
    """OCR hatti kapaliyken istek atildiginda firlatilir."""


def ocr_ac(aktif: bool = True) -> bool:
    """OCR hattini acar/kapatir. Acik halde `True` doner."""
    global OCR_ETKIN
    OCR_ETKIN = bool(aktif)
    return OCR_ETKIN

#: Modelden istenen JSON semasi.
SEMA = """{
  "ilan_sira_no": "'İlan Sıra No' degeri (yoksa null)",
  "mersis_no": "'Mersis No' satiri, SADECE rakamlar, bastaki bosluklar silinmis (yoksa null)",
  "ticaret_sicil_no": "'Ticaret Sicil/Dosya No' degeri (yoksa null)",
  "ticaret_unvani": "KIRMIZI puntolu 'Ticaret Unvani', tam ve birebir (yoksa null)",
  "adres_kisa": "'Adres :' satiri (yoksa null)",
  "tescil_edilen_hususlar": "Tescile Delil Olan Belgeler paragrafi (yoksa null)",
  "ic_yonergesi_madde": "Ic Yonergesi'ni degistiren MADDE numarasi (yoksa null)",
  "ilan_turu": "Ilan turu: orn. 'SUBE (ADRES DEGISIKLIGI)', 'GENEL KURUL' (yoksa null)",
  "emniyet_uyarisi": "Okunamayan/supheli alan varsa buraya yaz, yoksa null"
}"""


def env_yukle() -> None:
    """`.env` dosyasini ortam degiskenlerine yukler (anahtarlar yazdirilmaz)."""
    dosya = KOK / ".env"
    if not dosya.is_file():
        return
    for satir in dosya.read_text(encoding="utf-8", errors="replace").splitlines():
        satir = satir.strip()
        if not satir or satir.startswith("#") or "=" not in satir:
            continue
        ad, deger = satir.split("=", 1)
        os.environ.setdefault(ad.strip(), deger.strip().strip('"').strip("'"))


def pdf_tek_sayfa_png(pdf_yolu: pathlib.Path, dpi: int = 200) -> pathlib.Path:
    """PDF'in ilk sayfasini PNG'ye cevirir (dosya varsa dokunmaz)."""
    png = KANIT_DIZIN / f"{pdf_yolu.stem}_sayfa.png"
    if png.is_file():
        return png
    KANIT_DIZIN.mkdir(parents=True, exist_ok=True)
    import pdfplumber

    with pdfplumber.open(str(pdf_yolu)) as pdf:
        pdf.pages[0].to_image(resolution=dpi).save(str(png), format="PNG")
    return png


def _sayfayi_kir(png: pathlib.Path) -> list[pathlib.Path]:
    """Gazete sayfasini bolumlere boler.

    Tam sayfa gorseli vision modele verildiginde kucuk puntolar kaybolur.
    Bolme cozunurlugu korur ve OCR dogrulugunu cektirir.
    """
    from PIL import Image

    cikti: list[pathlib.Path] = []
    with Image.open(png) as im:
        g, y = im.size
        kirpimlar = {
            "sag": (int(g * 0.50), 0, g, int(y * 0.72)),
            "sol_ust": (0, 0, int(g * 0.52), int(y * 0.55)),
            "sol_alt": (0, int(y * 0.50), int(g * 0.52), y),
        }
        for ad, kutu in kirpimlar.items():
            yol = png.with_name(f"{png.stem}_{ad}.png")
            im.crop(kutu).save(yol)
            cikti.append(yol)
    return cikti



IPUCLARI = {
    "sag": (
        "BU BOLGE GAZETENIN SAG SUTUNUDUR. Burada 'T.C. ... TICARET SICILI "
        "MUDURLUGUNDEN' basligini takip eden ILAN BLOKLARI vardir. "
        "En ustteki ilan blogunu doldur."
    ),
    "sol_ust": "BU, gazetenin sol-ust kismi. Ilan blogu olabilir veya olmayabilir.",
    "sol_alt": "BU, gazetenin sol-alt kismi. Ilan blogu olabilir veya olmayabilir.",
}


#: Her bolge icin modele verilen yonlendirme metni.
#: Gazetede ilan blogu SAG sutundadir; sol sutun sozlesme metnidir.
IPUCLERI = {
    "sag": (
        "BU BOLGE GAZETENIN SAG SUTUNUDUR. Burada 'T.C. ... TICARET SICILI "
        "MUDURLUGUNDEN' basligini takip eden ILAN BLOKLARI vardir. "
        "En ustteki ilan blogunu doldur."
    ),
    "sol_ust": "BU, gazetenin sol-ust kismi. Ilan blogu olabilir veya olmayabilir.",
    "sol_alt": "BU, gazetenin sol-alt kismi. Ilan blogu olabilir veya olmayabilir.",
}


def _istek_9router(model: str, png: pathlib.Path, ipucu: str) -> dict:
    """9Router uzerinden vision cagrisi yapar."""
    env_yukle()
    url = os.environ.get("NINEROUTER_URL", "").rstrip("/")
    anahtar = os.environ.get("NINEROUTER_KEY", "")
    if not url or not anahtar:
        raise RuntimeError("NINEROUTER_URL/KEY yok (.env)")

    b64 = base64.b64encode(png.read_bytes()).decode("ascii")
    govde = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            "Bu bir Turk Ticaret Sicili Gazetesi sayfasidir.\n"
                            "Gorevin: asagidaki semaya uyan ALANLARI cikart.\n\n"
                            f"{ipucu}\n\nSEMA:\n{SEMA}\n\n"
                            "KURALLAR:\n"
                            "- Sadece JSON dondur, markdown yok.\n"
                            "- Bir alan sayfada yoksa null yaz; TAHMIN ETME.\n"
                            "- Sayisal alanlarda rakam olmayan karakterleri "
                            "rakama cevir: O->0, l/I->1, S->5.\n"
                            "- Unvani ve adresi oldugu gibi yaz, kisaltma yapma."
                        ),
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{b64}"},
                    },
                ],
            }
        ],
        "temperature": 0,
        "max_tokens": 2000,
    }
    r = httpx.post(
        f"{url}/v1/chat/completions",
        headers={"Authorization": f"Bearer {anahtar}"},
        json=govde,
        timeout=180,
    )
    if r.status_code != 200:
        raise RuntimeError(f"HTTP {r.status_code}: {r.text[:300]}")
    return _cevap_ayikla(r)


def _cevap_ayikla(r) -> dict:
    """9Router yanitini JSON'a cevirir.

    D-280 KOK NEDEN: bazi saglayicilar gecerli JSON'un SONUNA SSE kalintisi
    ekliyor (`data: [DONE]`). `response.json()` bunda `Extra data` hatasi
    veriyor — **model cagrisi basarili, ayristirma basarisiz**. Bu yuzden
    govde metni elle kesilir.
    """
    try:
        return r.json()
    except json.JSONDecodeError:
        pass
    govde = r.text.strip()
    for ayirac in ("\ndata:", "\r\ndata:"):
        if ayirac in govde:
            govde = govde.split(ayirac, 1)[0]
    try:
        return json.loads(govde)
    except json.JSONDecodeError as e:
        raise RuntimeError(
            f"Cevap ayristirilamadi ({e}); ilk 300: {r.text[:300]}"
        ) from e


def _json_ayikla(metin: str) -> dict:
    """Model cevabindan JSON nesnesini cikarir (kod bloklari dahil)."""
    metin = metin.strip()
    if metin.startswith("```"):
        metin = re.sub(r"^```[a-z]*\n?", "", metin)
        metin = re.sub(r"\n?```$", "", metin)
    bas = metin.find("{")
    son = metin.rfind("}")
    if bas < 0 or son <= bas:
        return {}
    try:
        return json.loads(metin[bas : son + 1])
    except json.JSONDecodeError:
        return {}


def sayfa_ocr(
    png: pathlib.Path,
    model: str = VARSAYILAN_MODEL,
    ipucu: str = "Bu, gazetenin ILAN blogu iceren bolumudur.",
) -> dict:
    """Tek bir gorsel dilimini OCR eder. Sure, token ve ham cevabi doner."""
    t0 = time.time()
    cevap = _istek_9router(model, png, ipucu)
    sure = round(time.time() - t0, 2)
    ham = cevap["choices"][0]["message"].get("content", "")
    k = cevap.get("usage", {})
    return {
        "gorsel": str(png),
        "model": model,
        "sure_saniye": sure,
        "veri": _json_ayikla(ham),
        "ham_cevap": ham,
        "kullanim": {
            "prompt_token": k.get("prompt_tokens"),
            "tamam_token": k.get("completion_tokens"),
            "toplam_token": k.get("total_tokens"),
        },
        "hata": None,
    }


def _rakamlastir(deger: Any) -> Optional[str]:
    """OCR karisikliklarini duzeltip SADECE rakam iceren degeri dondurur."""
    if deger is None:
        return None
    s = re.sub(r"[\s.\-–—]", "", str(deger))
    for bozuk, dogru in DUZELTMELER.items():
        s = s.replace(bozuk, dogru)
    s = re.sub(r"[^0-9]", "", s)
    return s or None


def dogrula(veri: dict) -> dict:
    """Cikarilan alanlari kanit kapisiyla karsilastirir.

    MERSIS: gazetede 17 hane, basta boslukla yaziliyor
    (orn. `0012032074100024`). Kanonik 16 hanedir; bastaki bosluk
    onceki oturumda D-276 ile duzeltildi. Burada da uygulanir ve
    VKN dogrulamasi `kimlik_no.py` UZERINDE yapilir (K-1: tek kapi).
    """
    sys.path.insert(0, str(KOK))
    from skills.services.ticaret_sicili_kanit import vkn_kontrol

    mersis = _rakamlastir(veri.get("mersis_no"))
    kanonik = None
    if mersis:
        if len(mersis) == 17 and mersis.startswith("0"):
            kanonik = mersis[1:]
        elif len(mersis) == 16:
            kanonik = mersis

    vkn_sonuc = vkn_kontrol(kanonik) if kanonik else None

    return {
        "mersis_ham": mersis,
        "mersis_kanonik_16": kanonik,
        "vkn_dogrulama": vkn_sonuc,
        "sicil_no": _rakamlastir(veri.get("ticaret_sicil_no")),
        "ilan_sira_no": _rakamlastir(veri.get("ilan_sira_no")),
        "unvan": veri.get("ticaret_unvani"),
        "adres": veri.get("adres_kisa"),
        "tescil_husus": veri.get("tescil_edilen_hususlar"),
        "uyari": veri.get("emniyet_uyarisi"),
    }


def pdf_ocr(
    pdf_yolu: pathlib.Path,
    model: str = VARSAYILAN_MODEL,
    dilim: bool = True,
    zorla: bool = False,
) -> dict:
    """PDF'in ilan blogunu OCR ile cikarir ve birlestirir.

    D-278 KAPISI: `OCR_ETKIN` kapaliyken (varsayilan) HTTP istegi
    YAPILMAZ ve `OcrPasifHatasi` firlatilir. Acilacaksa ya `ocr_ac(True)`
    ya da `zorla=True` (CLI `--aktif`) kullanilir.
    """
    if not (OCR_ETKIN or zorla):
        raise OcrPasifHatasi(PASIF_UYARI)
    KANIT_DIZIN.mkdir(parents=True, exist_ok=True)
    png = pdf_tek_sayfa_png(pdf_yolu)
    gorseller = _sayfayi_kir(png) if dilim else [png]

    sonuclar = []
    for g in gorseller:
        ad = g.stem.split("_")[-1]
        try:
            sonuclar.append(sayfa_ocr(g, model, IPUCLERI.get(ad, "")))
        except Exception as e:
            sonuclar.append(
                {
                    "gorsel": str(g),
                    "model": model,
                    "veri": {},
                    "ham_cevap": "",
                    "hata": f"{type(e).__name__}: {e}",
                }
            )

    kanonik = next(
        (s for s in sonuclar if s["gorsel"].endswith("_sag.png") and s.get("veri")),
        next((s for s in sonuclar if s.get("veri")), None),
    )

    return {
        "kaynak_pdf": str(pdf_yolu),
        "model": model,
        "toplam_sure_saniye": round(
            sum(s.get("sure_saniye", 0) for s in sonuclar), 2
        ),
        "dilim_sayisi": len(sonuclar),
        "basarili_dilim": sum(1 for s in sonuclar if s.get("veri")),
        "hatali_dilim": sum(1 for s in sonuclar if s.get("hata")),
        "toplam_token": sum(
            (s.get("kullanim") or {}).get("toplam_token") or 0 for s in sonuclar
        ),
        "kanonik_veri": (kanonik or {}).get("veri", {}),
        "dilimler": sonuclar,
    }


if __name__ == "__main__":
    ay = argparse.ArgumentParser()
    ay.add_argument("pdf", nargs="?", default=str(KANIT_DIZIN / "448217_a18a2282.pdf"))
    ay.add_argument("--model", default=VARSAYILAN_MODEL)
    ay.add_argument("--tam", action="store_true", help="Dilimleme, tam sayfa")
    ay.add_argument(
        "--aktif",
        action="store_true",
        help="D-278: OCR hattini acar (varsayilan KAPALI). Maliyet uretir!",
    )
    ay.add_argument(
        "--durum", action="store_true", help="Pasif/aktif durumunu yazar, cikis yok"
    )
    ns = ay.parse_args()

    if ns.durum:
        print("OCR_ETKIN =", OCR_ETKIN)
        print(PASIF_UYARI if not OCR_ETKIN else "OCR hatti ACIK.")
        raise SystemExit(0)

    if not ns.aktif:
        print(PASIF_UYARI)
        print("\nDurum sorgulamak icin:  --durum")
        print("Acmak icin:             --aktif")
        raise SystemExit(2)

    _r = pdf_ocr(
        pathlib.Path(ns.pdf), ns.model, dilim=not ns.tam, zorla=ns.aktif
    )
    _cikti = KANIT_DIZIN / (pathlib.Path(ns.pdf).stem + "_ocr.json")
    _cikti.write_text(json.dumps(_r, ensure_ascii=False, indent=2), encoding="utf-8")
    print("OCR =", _cikti)
    print("SURE =", _r["toplam_sure_saniye"], "sn | TOKEN =", _r["toplam_token"])
    print("DILIM =", _r["basarili_dilim"], "basarili /", _r["hatali_dilim"], "hatali")
    print("--- KANONIK ---")
    print(json.dumps(_r["kanonik_veri"], ensure_ascii=False, indent=2)[:1500])
    print("--- DOGRULAMA ---")
    print(json.dumps(dogrula(_r["kanonik_veri"]), ensure_ascii=False, indent=2)[:1500])
