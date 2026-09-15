# -*- coding: utf-8 -*-
"""PO-BACK-10: Kapsama (coverage) analitiği — saf fonksiyonlar, DB yok.

Amaç: "Hedef evrenin yüzde kaçını yakaladık?" sorusunu sektör (NACE grubu)
kırılımıyla cevaplamak. Huginn 'Kapsam' kartı bu modülü besler.

Girdi sözleşmesi
----------------
- ``firmalar``: ``list[dict]``; her firma için NACE grubu şu anahtarlardan
  ilk bulunanla okunur: ``nace_grup``, ``nace_group``, ``sektor``, ``nace_kodu``
  (NACE kodunun ilk 2 hanesi grup sayılır).
- ``nace_gruplari``: ``dict[str, int]`` (grup → hedef firma sayısı) **veya**
  ``list[dict]`` (``{"nace_grup": ..., "hedef": ...}``).

Tüm oranlar 0-100 aralığında, 2 ondalık yuvarlanmış ``float`` döner.
Hedef 0 / boş girdi hata fırlatmaz; oran 0.0 olur.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable

__all__ = [
    "coverage_orani",
    "sektor_bazli_coverage",
    "coverage_ozeti",
    "firma_nace_grubu",
    "nace_hedeflerini_yukle",
    "NACE_HEDEF_DOSYASI",
]

_GRUP_ALANLARI: tuple[str, ...] = ("nace_grup", "nace_group", "sektor", "nace_kodu")
BILINMEYEN_GRUP = "bilinmeyen"

# HEDEF-NACE-01: gerçek hedef tablosu (grup → hedef firma sayısı). Yoksa/bozuksa
# eşit paylaşım fallback'i kullanılır; UI bu durumu ``kaynak`` alanından anlar.
NACE_HEDEF_DOSYASI = Path("data") / "nace_hedefleri.json"


def _esit_paylasim(gruplar: Iterable[str], hedef_evren: int) -> dict[str, int]:
    """Hedef evreni gruplara eşit böler (grup yoksa boş sözlük)."""
    grup_listesi = sorted({str(g) for g in gruplar if g})
    if not grup_listesi:
        return {}
    try:
        evren = max(0, int(hedef_evren))
    except (TypeError, ValueError):
        evren = 0
    pay = evren // len(grup_listesi)
    return {g: pay for g in grup_listesi}


def nace_hedeflerini_yukle(
    dosya: str | Path | None = None,
    gruplar: Iterable[str] = (),
    hedef_evren: int = 0,
) -> tuple[dict[str, int], str]:
    """HEDEF-NACE-01: NACE hedef tablosunu JSON'dan yükler.

    Dosya biçimi: ``{"hedefler": {"62": 1200, "10": 800}}`` **veya** düz
    ``{"62": 1200, ...}`` **veya** ``[{"nace_grup": "62", "hedef": 1200}]``.

    Dönüş: ``(hedefler, kaynak)``; ``kaynak`` ∈ {``"dosya"``, ``"esit_paylasim"``}.
    Dosya yok / bozuk / boşsa ``gruplar`` + ``hedef_evren`` ile eşit paylaşıma
    düşer. Dosyadan gelen tablo ``gruplar`` içinde olmayan grupları da korur;
    dosyada olmayan ama DB'de görülen gruplara 0 hedef verilmez (raporda
    ``hedef=0`` → oran 0.0 olarak görünür, bilinçli tercih).
    """
    yol = Path(dosya) if dosya is not None else NACE_HEDEF_DOSYASI
    try:
        ham = json.loads(yol.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return _esit_paylasim(gruplar, hedef_evren), "esit_paylasim"
    if isinstance(ham, dict) and isinstance(ham.get("hedefler"), (dict, list)):
        ham = ham["hedefler"]
    hedefler = _hedefleri_normalize(ham)
    if not hedefler:
        return _esit_paylasim(gruplar, hedef_evren), "esit_paylasim"
    return hedefler, "dosya"


def _oran(pay: int, payda: int) -> float:
    """0-100 arası oran; payda 0 ise 0.0. Üst sınır 100'e kırpılır."""
    if payda <= 0:
        return 0.0
    return round(min(100.0, max(0.0, pay * 100.0 / payda)), 2)


def firma_nace_grubu(firma: dict[str, Any]) -> str:
    """Firmadan NACE grubunu çıkarır; yoksa ``bilinmeyen``."""
    if not isinstance(firma, dict):
        return BILINMEYEN_GRUP
    for alan in _GRUP_ALANLARI:
        deger = firma.get(alan)
        if deger is None:
            continue
        metin = str(deger).strip()
        if not metin:
            continue
        if alan == "nace_kodu":
            # "62.01" / "6201" → "62"
            rakamlar = "".join(ch for ch in metin if ch.isdigit())
            return rakamlar[:2] if len(rakamlar) >= 2 else metin
        return metin
    return BILINMEYEN_GRUP


def _hedefleri_normalize(nace_gruplari: Any) -> dict[str, int]:
    """dict veya list[dict] hedef tanımını ``{grup: hedef}`` sözlüğüne çevirir."""
    sonuc: dict[str, int] = {}
    if not nace_gruplari:
        return sonuc
    if isinstance(nace_gruplari, dict):
        kaynak: Iterable[tuple[Any, Any]] = nace_gruplari.items()
    else:
        kaynak = (
            (k.get("nace_grup") or k.get("nace_group") or k.get("sektor"), k.get("hedef", 0))
            for k in nace_gruplari
            if isinstance(k, dict)
        )
    for grup, hedef in kaynak:
        if grup is None:
            continue
        try:
            sayi = int(hedef or 0)
        except (TypeError, ValueError):
            sayi = 0
        sonuc[str(grup).strip()] = max(0, sayi)
    return sonuc


def coverage_orani(firmalar: list[dict[str, Any]], hedef_evren: int) -> float:
    """Toplam kapsama oranı (0-100).

    - Boş liste → 0.0
    - ``hedef_evren`` ≤ 0 → 0.0 (bölme hatası yok)
    - Yakalanan > hedef → 100.0 (kırpılır)
    """
    yakalanan = len(firmalar or [])
    try:
        hedef = int(hedef_evren or 0)
    except (TypeError, ValueError):
        hedef = 0
    return _oran(yakalanan, hedef)


def sektor_bazli_coverage(
    firmalar: list[dict[str, Any]],
    nace_gruplari: dict[str, int] | list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Sektör (NACE grubu) bazlı kapsama listesi.

    Dönüş: ``[{"nace_grup", "yakalanan", "hedef", "oran"}, ...]``
    Sıralama: oran artan (en düşük önce) → aynı oranda hedef azalan → ad.
    Hedef tanımında olmayan ama firmalarda geçen gruplar ``hedef=0, oran=0.0``
    ile listeye eklenir (görünmez kalmasın).
    """
    hedefler = _hedefleri_normalize(nace_gruplari)
    sayim: dict[str, int] = {}
    for firma in firmalar or []:
        grup = firma_nace_grubu(firma)
        sayim[grup] = sayim.get(grup, 0) + 1

    gruplar = set(hedefler) | set(sayim)
    satirlar: list[dict[str, Any]] = []
    for grup in gruplar:
        hedef = hedefler.get(grup, 0)
        yakalanan = sayim.get(grup, 0)
        satirlar.append(
            {
                "nace_grup": grup,
                "yakalanan": yakalanan,
                "hedef": hedef,
                "oran": _oran(yakalanan, hedef),
            }
        )
    satirlar.sort(key=lambda s: (s["oran"], -s["hedef"], s["nace_grup"]))
    return satirlar


def coverage_ozeti(
    firmalar: list[dict[str, Any]],
    hedef_evren: int,
    nace_gruplari: dict[str, int] | list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Kapsam kartı için tek sözlük.

    Dönüş anahtarları:
      - ``toplam``: yakalanan firma sayısı
      - ``hedef``: hedef evren
      - ``oran``: toplam kapsama (0-100)
      - ``sektorler``: :func:`sektor_bazli_coverage` çıktısı
      - ``en_dusuk_3_sektor``: hedefi > 0 olan en düşük oranlı 3 sektör
      - ``veri_var``: firma listesi boş değilse ``True``
    """
    firmalar = firmalar or []
    sektorler = sektor_bazli_coverage(firmalar, nace_gruplari or {})
    en_dusuk = [s for s in sektorler if s["hedef"] > 0][:3]
    return {
        "toplam": len(firmalar),
        "hedef": max(0, int(hedef_evren or 0)) if isinstance(hedef_evren, (int, float)) else 0,
        "oran": coverage_orani(firmalar, hedef_evren),
        "sektorler": sektorler,
        "en_dusuk_3_sektor": en_dusuk,
        "veri_var": bool(firmalar),
    }
