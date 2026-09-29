"""TOBB gazete PDF'ini KATMANLARINA AYIRIR.

Neden var: `pdfplumber.extract_text()` bos dondu ama kullanici PDF'i
acikca METIN OKUNABILIR sekilde goruyor. Demek ki "metin katmani yok"
diyis HATALI bir cikarimdi. Iki olasilik var:
  (a) PDF gercekten taranmis gorsel (scan)
  (b) PDF'te metin KATMANI VAR ama kodlama/ToUnicode bozuk
      -> cikarim bos/bozuk gelir, gorsel dogru ama sonuc yanlis

Bu arac (b) ve (a) ayirt EDER. Sonuc karari degistirir:
  (b) ise OCR'a GEREK YOK.
"""

from __future__ import annotations

import json
import sys
import zlib
from pathlib import Path

KOK = Path(__file__).resolve().parents[1]
VARSAYILAN = KOK / "data" / "kanit" / "448217_a18a2282.pdf"


def _ham_nesneler(veri: bytes) -> dict:
    """PDF icindeki nesne turlerini kabaca sayar."""
    return {
        "toplam_bayt": len(veri),
        "gorsel_xobject": veri.count(b"/Subtype /Image")
        + veri.count(b"/Subtype/Image"),
        "font": veri.count(b"/Type /Font") + veri.count(b"/Type/Font"),
        "tounicode_cmap": veri.count(b"/ToUnicode"),
        "metin_Tj": veri.count(b"Tj"),
        "metin_TJ": veri.count(b"TJ"),
        "flate_stream": veri.count(b"/FlateDecode"),
        "sayfa_nesnesi": veri.count(b"/Type /Page") + veri.count(b"/Type/Page"),
    }


def _streamleri_coz(veri: bytes) -> list[bytes]:
    """Tum FlateDecode stream'leri cozer."""
    cikti: list[bytes] = []
    i = 0
    while True:
        j = veri.find(b"stream", i)
        if j < 0:
            break
        k = j + 6
        if veri[k : k + 2] == b"\r\n":
            k += 2
        elif veri[k : k + 1] in (b"\n", b"\r"):
            k += 1
        son = veri.find(b"endstream", k)
        if son < 0:
            break
        try:
            cozulmus = zlib.decompress(veri[k:son])
        except zlib.error:
            try:
                cozulmus = zlib.decompressobj().decompress(veri[k:son])
            except Exception:
                cozulmus = b""
        if cozulmus:
            cikti.append(cozulmus)
        i = son + 9
    return cikti


def _icerik_akisi_kanit(veri: bytes) -> dict:
    """Cozulmus icerik akislarinda GERCEK metin cizgisi var mi?

    Ayirt edici: sayfa icerik akisinda `(text) Tj` ya da `[(a)-1(b)] TJ`
    operatorlari gorunur. Gorsel-XObject iceren akislarda piksel vardir
    ama metin operatoru YOKTUR.
    """
    akislar = _streamleri_coz(veri)
    metin_akisi = 0
    gorsel_akisi = 0
    ornekler: list[str] = []
    for akis in akislar:
        if b"Tj" in akis or b"TJ" in akis:
            metin_akisi += 1
            if len(ornekler) < 3:
                ornekler.append(akis[:400].decode("latin-1", "replace"))
        elif b"/Image" in akis or b"/DCTDecode" in akis:
            gorsel_akisi += 1
    return {
        "cozulmus_stream": len(akislar),
        "metin_operatoru_olan_stream": metin_akisi,
        "gorseli_olan_stream": gorsel_akisi,
        "icerik_akis_ornekleri": ornekler,
    }


def _kutuphane_dene(yol: Path) -> dict:
    """Mevcut PDF kutuphanelerini tek tek dener."""
    sonuc: dict = {}

    try:
        import pdfplumber

        with pdfplumber.open(str(yol)) as pdf:
            sayfalar = []
            for pg in pdf.pages:
                sayfalar.append(
                    {
                        "genislik": round(pg.width, 1),
                        "yukseklik": round(pg.height, 1),
                        "karakter_sayisi": len(pg.chars),
                        "gorsel_sayisi": len(pg.images),
                        "metin_ornegi": (pg.extract_text() or "")[:300],
                    }
                )
            sonuc["pdfplumber"] = {"ok": True, "sayfalar": sayfalar}
    except Exception as e:
        sonuc["pdfplumber"] = {"ok": False, "hata": f"{type(e).__name__}: {e}"}

    try:
        from pypdf import PdfReader

        r = PdfReader(str(yol))
        sayfalar = []
        for pg in r.pages:
            try:
                metin = pg.extract_text() or ""
            except Exception as e:
                metin = f"<HATA: {e}>"
            sayfalar.append(
                {"karakter_sayisi": len(metin), "metin_ornegi": metin[:300]}
            )
        sonuc["pypdf"] = {
            "ok": True,
            "sifreli": r.is_encrypted,
            "sayfa_sayisi": len(r.pages),
            "sayfalar": sayfalar,
        }
    except Exception as e:
        sonuc["pypdf"] = {"ok": False, "hata": f"{type(e).__name__}: {e}"}

    try:
        from pdfminer.high_level import extract_text

        metin = extract_text(str(yol)) or ""
        sonuc["pdfminer"] = {
            "ok": True,
            "karakter_sayisi": len(metin),
            "metin_ornegi": metin[:300],
        }
    except Exception as e:
        sonuc["pdfminer"] = {"ok": False, "hata": f"{type(e).__name__}: {e}"}

    return sonuc



def analiz_et(yol: Path | None = None) -> dict:
    """PDF'in gercek yapisini raporlar ve KARAR verir."""
    yol = Path(yol) if yol else VARSAYILAN
    veri = yol.read_bytes()
    rapor = {
        "dosya": str(yol),
        "ham": _ham_nesneler(veri),
        "icerik_akisi": _icerik_akisi_kanit(veri),
        "kutuphaneler": _kutuphane_dene(yol),
    }

    akis = rapor["icerik_akisi"]
    ham = rapor["ham"]
    metin_akisi = akis["metin_operatoru_olan_stream"]
    gorsel = ham["gorsel_xobject"]

    if metin_akisi > 0:
        karar = "METIN_KATMANI_VAR"
        gerekce = (
            f"{metin_akisi} icerik akisinda metin gosterim operatoru (Tj/TJ) "
            "bulundu. OCR GEREKMEZ; once kodlama/ToUnicode duzeltmesi denenmeli."
        )
    elif gorsel > 0:
        karar = "TARANMIS_GORSEL"
        gerekce = (
            f"{gorsel} gorsel XObject, 0 metin operatoru. PDF gercekten scan; "
            "OCR gerekli."
        )
    else:
        karar = "BELIRSIZ"
        gerekce = "Ne metin operatoru ne gorsel bulundu; dosya bozuk olabilir."

    rapor["karar"] = karar
    rapor["gerekce"] = gerekce
    return rapor


if __name__ == "__main__":
    _yol = Path(sys.argv[1]) if len(sys.argv) > 1 else VARSAYILAN
    _rapor = analiz_et(_yol)
    _cikti = KOK / "data" / "pdf_analiz.json"
    _cikti.write_text(
        json.dumps(_rapor, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(_rapor["karar"], "|", _cikti)

