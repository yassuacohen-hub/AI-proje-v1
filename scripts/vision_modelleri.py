"""9Router'da OCR/vision yetenekli modelleri listeler.

Kullanim: python scripts/vision_modelleri.py
"""
from __future__ import annotations

import os
import pathlib
import sys

import httpx

KOK = pathlib.Path(__file__).resolve().parents[1]
ANAHTARLAR = ("NINEROUTER_URL", "NINEROUTER_KEY")

#: OCR isine yarayabilecek model isaretleri.
ISARETLER = (
    "vision", "gemini", "gpt-4o", "gpt-4.1", "gpt-5", "claude",
    "pixtral", "llava", "qwen-vl", "ocr", "minicpm", "internvl",
)


def env_yukle() -> None:
    """`.env` dosyasını ortam degiskenlerine yukler (anahtarlar yazdirilmaz)."""
    dosya = KOK / ".env"
    if not dosya.is_file():
        return
    for satir in dosya.read_text(encoding="utf-8", errors="replace").splitlines():
        satir = satir.strip()
        if not satir or satir.startswith("#") or "=" not in satir:
            continue
        ad, deger = satir.split("=", 1)
        os.environ.setdefault(ad.strip(), deger.strip().strip('"').strip("'"))


def modelleri_getir() -> dict:
    env_yukle()
    url = os.environ.get("NINEROUTER_URL", "").rstrip("/")
    anahtar = os.environ.get("NINEROUTER_KEY", "")
    if not url or not anahtar:
        return {"hata": "NINEROUTER_URL/KEY yok"}
    try:
        r = httpx.get(
            f"{url}/v1/models",
            headers={"Authorization": f"Bearer {anahtar}"},
            timeout=30,
        )
    except Exception as e:
        return {"hata": f"{type(e).__name__}: {e}"}
    if r.status_code != 200:
        return {"hata": f"HTTP {r.status_code}", "govde": r.text[:200]}
    return {"toplam": len(r.json().get("data", [])),
            "modeller": [m["id"] for m in r.json().get("data", [])]}


if __name__ == "__main__":
    sonuc = modelleri_getir()
    if "hata" in sonuc:
        print("HATA:", sonuc["hata"], sonuc.get("govde", ""))
    else:
        print("TOPLAM MODEL:", sonuc["toplam"])
        print("--- OCR/VISION OLASI OLANLAR ---")
        for m in sonuc["modeller"]:
            if any(x in m.lower() for x in ISARETLER):
                print("  ", m)
