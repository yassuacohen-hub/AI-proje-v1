# -*- coding: utf-8 -*-
"""Mimir sohbet ucu: uc parca prompt + BAGLAM + KATALOG + IC arac dongusu.

Prompt KODDA KOPYALANMAZ (D-230): prompts/mimir_sistem_promptu.md okunur.
Rol: dis=musteri (varsayilan) / ic=admin (ARA/GETIR ekli). Varsayilan kisitli
olan dis (D-311). Bos BAGLAMda model cagrilmaz.
"""
from __future__ import annotations

import json
import logging
import os
import time
from pathlib import Path
from typing import Callable

logger = logging.getLogger(__name__)

KOK = Path(__file__).resolve().parents[3]
PROMPT_DOSYASI = KOK / "prompts" / "mimir_sistem_promptu.md"
# prompt madde 2d, AYNEN bu cumle:
BOS_BAGLAM_YANITI = "Bu bilgi veri tabanımızda yok."
NL = chr(10)


def _blok_ayir(metin: str) -> list[str]:
    """Markdown ```text``` bloklarini sirasiyla dondurur (regex'siz, D-230 safe)."""
    parcalar = metin.split("```text")
    return [p.split("```", 1)[0].strip() for p in parcalar[1:]]


def prompt_yukle(rol: str = "dis", dosya: Path | None = None) -> str:
    """Prompt dosyasindan rol metnini dondur.

    rol: 'dis' (DISS blogu) / 'ic' (DISS + IC blogu, cunku IC kendisini
    'DISS'tan farki' ile anlatir). Tanimsiz rol -> ValueError (D-311).
    """
    if rol not in ("dis", "ic"):
        raise ValueError(f"gecersiz rol {rol!r}; beklenen dis veya ic")
    yol = dosya or PROMPT_DOSYASI
    bloklar = _blok_ayir(yol.read_text(encoding="utf-8"))
    if len(bloklar) < 2:
        raise ValueError("DISS/IC blogu bulunamadi")
    if rol == "dis":
        return bloklar[0]
    return bloklar[0] + NL + NL + bloklar[1]


def baglam_uret(soru: str, servis, n: int | None = None) -> str:
    """Soruya en yakin N chunk'i <BAGLAM> blogune cevir; bos ise ''."""
    if n is None:
        n = int(os.environ.get("MIMIR_KOMSU_CHUNK", "5"))
    try:
        isabetler = servis.find_similar(soru, top_k=n)
    except Exception as exc:  # noqa: BLE001
        logger.warning("baglam_uret find_similar hatasi: %s", exc)
        return ""
    if not isabetler:
        return ""
    satirlar: list[str] = []
    for i, h in enumerate(isabetler, 1):
        m = h.metadata
        kunye = " | ".join(
            str(x) for x in (h.id, m.get("nace_code") or "nace?",
                             m.get("last_updated") or "?") if x
        )
        metin = str(m.get("text", "")).replace("<BAGLAM>", "").replace(
            "</BAGLAM>", "")
        satirlar.append(f"[{i}] {metin}" + NL + f"    kaynak: {kunye}")
    return "<BAGLAM>" + NL + NL.join(satirlar) + NL + "</BAGLAM>"


def katalog_uret(dosya: str | None = None) -> str:
    """Katalog blogunu §3b biciminde kur; kaynak yoksa '' dondurur (D-230).

    Sabit fiyat/modul KODA GOMULMEZ; kaynak MIMIR_KATALOG_DOSYASI (JSON).
    """
    yol = dosya or os.environ.get("MIMIR_KATALOG_DOSYASI", "")
    if not yol or not Path(yol).exists():
        logger.warning("KATALOG kaynagi yok; blog bos gidiyor.")
        return ""
    try:
        k = json.loads(Path(yol).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        logger.warning("KATALOG okunamadi: %s", exc)
        return ""
    satirlar = [
        "plan: " + str(k.get("plan", "?")),
        "acik_moduller: " + ", ".join(k.get("acik_moduller", [])),
        "kilitli_moduller:",
    ]
    for m in k.get("kilitli_moduller", []):
        satirlar.append(
            "  - ad: " + str(m.get("ad"))
            + NL + "    ne_yapar: " + str(m.get("ne_yapar", ""))
            + NL + "    fiyat: " + str(m.get("fiyat", ""))
        )
    cs = k.get("carpma_sayaci", {})
    if cs:
        satirlar.append(
            "carpma_sayaci: " + ", ".join(f"{a}={s}" for a, s in cs.items())
        )
    return "<KATALOG>" + NL + NL.join(satirlar) + NL + "</KATALOG>"


def mimir_sohbet(
    soru: str,
    cevapla,
    rol: str = "dis",
    servis=None,
    istemci=None,
    katalog: str = "",
) -> str:
    """Sohbet ucu. cevapla(prompt)->str adaptor (injeksiyon testiyle ayni).

    Bos BAGLAM (servis verildi ama chunk yok) -> model CAGRILMAZ (brif 4).
    rol='ic' + istemci verilirse ARA/GETIR dongusu calisir.
    """
    zaman = time.perf_counter()
    sistem = prompt_yukle(rol)
    baglam = baglam_uret(soru, servis) if servis is not None else ""
    if servis is not None and not baglam.strip():
        logger.info("BOS_BAGLAM: model cagrilmadi")
        return BOS_BAGLAM_YANITI
    bloklar = [sistem]
    if baglam:
        bloklar.append(baglam)
    if katalog:
        bloklar.append(katalog)
    prompt = NL + NL.join(bloklar) + NL + NL + "Kullanici: " + soru
    yanit = str(cevapla(prompt) or "")
    if rol == "ic" and istemci is not None and yanit:
        from .arac_dongusu import arac_dongusu
        yanit = arac_dongusu(cevapla, prompt, yanit, istemci).yanit
    sure_ms = round((time.perf_counter() - zaman) * 1000)
    logger.info("mimir_sohbet rol=%s sure_ms=%d karakter=%d", rol, sure_ms,
                len(yanit))
    return yanit
