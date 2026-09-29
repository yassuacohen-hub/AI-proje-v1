"""OCR maliyet/erisim OLCUMU (D-280).

KAHIN (2026-09-29): "Duzey_3 OCR ile taramak daha ucuz... simdi verilerimizi
duzeltmek icin pek ise yaramaz, abonelik sonraki surecte yapilabilir."

Bu arac "daha ucuz" iddiasini TAHMIN etmez, OLÇER:
  - Hangi vision modeli gercekten erisilebilir (503/401 ayrimi)
  - Sayfa basina token ve sure
  - 930.000 ilan icin projeksiyon

Kullanim: python scripts/ocr_maliyet_olcer.py
"""
from __future__ import annotations

import json
import pathlib
import sys
import time

KOK = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(KOK / "scripts"))

import gazete_ocr as g  # noqa: E402

#: Denenecek modeller (ucuzdan pahaliya). Suffix = erisim saglayicisi.
DENENECEKLER = [
    "ag/gemini-3.5-flash-low",
    "ag/gemini-3.6-flash-low",
    "gemini/gemini-3.5-flash-lite",
    "gc/gemini-2.5-flash-lite",
    "bzl/gemini-3.1-pro-preview",
    "openai/gpt-4o-mini",
    "cl/openai/gpt-4o",
]

#: Duzey_3 birim maliyet (sayfadan): 1,535 TL/ilan.
TL_PER_ILAN = 1.535


def dene(model: str, png: pathlib.Path) -> dict:
    """Tek modeli dener; sure/token/hata doner (exception YUTULMAZ)."""
    t0 = time.time()
    try:
        r = g.sayfa_ocr(png, model, g.IPUCLARI["sag"])
        return {
            "model": model,
            "erisim": "TAMAM",
            "sure_saniye": round(time.time() - t0, 2),
            "token": (r.get("kullanim") or {}).get("toplam_token"),
            "alan_sayisi": len(r.get("veri") or {}),
            "ornek": str(r.get("veri") or {})[:160],
            "hata": None,
        }
    except Exception as e:
        return {
            "model": model,
            "erisim": "HATA",
            "sure_saniye": round(time.time() - t0, 2),
            "token": None,
            "alan_sayisi": 0,
            "ornek": "",
            "hata": str(e)[:180],
        }


def main() -> dict:
    pdf = KOK / "data" / "kanit" / "448217_a18a2282.pdf"
    png = g.pdf_tek_sayfa_png(pdf)
    # Yalniz sag sutun (ilan blogu) yeterli.
    bolum = g._sayfayi_kir(png)
    sag = next(b for b in bolum if b.stem.endswith("_sag"))

    sonuclar = []
    for m in DENENECEKLER:
        sonuclar.append(dene(m, sag))
        print(f"{m:38s} {sonuclar[-1]['erisim']:8s}", flush=True)

    calisan = [s for s in sonuclar if s["erisim"] == "TAMAM"]
    ozet = {
        "denenen": len(sonuclar),
        "calisan": len(calisan),
        "en_ucuz_calisan": min(
            (s for s in calisan if s.get("token")),
            key=lambda s: s["token"],
            default=None,
        ),
        "sonuclar": sonuclar,
    }
    cikti = KOK / "data" / "ocr_maliyet_olcum.json"
    cikti.write_text(json.dumps(ozet, ensure_ascii=False, indent=2), encoding="utf-8")
    return ozet


if __name__ == "__main__":
    o = main()
    print("\nCALISAN =", o["calisan"], "/", o["denenen"])
    print(cikti if False else KOK / "data" / "ocr_maliyet_olcum.json")
