# -*- coding: utf-8 -*-
"""PANEL-DURUSTLUK-01 TEK KAPI: panelde/raporda gosterilen metin buradan gecer.

Neden tek kapi: D-256'da puan YAZAN 17 yol bulundu, hepsi tek kapiya baglandi.
Puan/sektor GOSTEREN yollar da cogul (14+ ekran). Ekran basina metin yazilirsa
bir ekran duzeltilirken ikincisi eski yalani gostermeye devam eder.

Sozlesme:
  - D-249: "veri yok" 0 gibi gosterilmez; bos gosterilir.
  - D-250/7: puan tek basina degil, ULASILABILIR TAVAN ile birlikte sunulur.
  - D-252/2: kanit kaynagi olmayan NACE "tahmini sektor" etiketi olmadan sunulamaz.
  - D-252/5: tek kaynaktan kopyalanmis kod kutlesi sektor sayacina girmez.
"""
from __future__ import annotations

import math
from functools import lru_cache

from .etl.quality_recalc import (
    AZAMI,
    KILIT_GEREKCESI,
    NACE_KANIT_KAYNAKLARI,
    SURUM,
    bayat_mi,
    tavan_raporu,
)

__all__ = [
    "BOS",
    "TAHMIN_ETIKETI",
    "BANT_SAYISI",
    "puan_metni",
    "bos_veya",
    "nace_tahmin_mi",
    "nace_etiketi",
    "nace_metni",
    "sektor_sayaci",
    "kilit_satirlari",
    "tavan_metni",
    "bantlar",
    "bant_dagilimi",
    "risk_esigi",
    "tavan_getir",
    "tavan_ozeti",
]

# D-249: panelde "veri yok" bu isaretle gosterilir — asla 0 ile.
BOS = "—"

TAHMIN_ETIKETI = "tahmini sektör"


def _yok_mu(deger) -> bool:
    """"Olculmedi" testi. NaN de yokluktur.

    pandas SQL NULL'unu None DEGIL NaN yapar; sadece ``is None`` bakan kod
    olculmemis puani sayiya cevirir (NaN > hicbir sey degildir, karsilastirma
    hep False doner, puan en ust banda dusuverir). D-249'un tam tersi.
    """
    if deger is None:
        return True
    if isinstance(deger, str):
        return not deger.strip()
    try:
        return math.isnan(float(deger))
    except (TypeError, ValueError):
        return False


def bos_veya(deger, bicim: str = "{}") -> str:
    """D-249: None/NaN/bos dize 0'a cevrilmez, BOS gosterilir."""
    if _yok_mu(deger):
        return BOS
    return bicim.format(deger)


def puan_metni(deger, tavan: float, surum: str | None = SURUM) -> str:
    """D-250/7: puan daima tavanla birlikte. Olcek azami degil TAVAN'dir.

    >>> puan_metni(3.71, 6.5)
    '3.71 / 6.50 ulaşılabilir'
    >>> puan_metni(None, 6.5)
    '—'
    >>> puan_metni(float('nan'), 6.5)
    '—'
    >>> puan_metni(3.71, 6.5, 'v0')
    '3.71 / 6.50 ulaşılabilir (bayat: v0)'
    """
    if _yok_mu(deger):
        return BOS
    metin = f"{float(deger):.2f} / {float(tavan):.2f} ulaşılabilir"
    if bayat_mi(surum):
        metin += f" (bayat: {surum or BOS})"
    return metin


def tavan_metni(tavan: float) -> str:
    """Tavanin azamiye oranini aciklayan tek satir (D-250/7)."""
    kayip = round(AZAMI - float(tavan), 1)
    return (
        f"Ulaşılabilir tavan {float(tavan):.2f} / {AZAMI:.2f}. "
        f"{kayip:.1f} puan kaynağı olmayan alanlarda kilitli."
    )


def kilit_satirlari(kilitli: dict[str, float]) -> list[dict]:
    """Kilitli alanlari gerekcesiyle listeler (D-257)."""
    return [
        {
            "alan": alan,
            "kayip_puan": agirlik,
            "gerekce": KILIT_GEREKCESI.get(alan, "kaynak bağlı değil"),
        }
        for alan, agirlik in sorted(kilitli.items(), key=lambda kv: -kv[1])
    ]


def nace_tahmin_mi(nace_source: str | None) -> bool:
    """D-245: kanit listesinde olmayan her kaynak tahmindir."""
    return nace_source not in NACE_KANIT_KAYNAKLARI


def nace_etiketi(nace_source: str | None) -> str:
    """Tahmin ise etiket, kanit ise bos dize."""
    return TAHMIN_ETIKETI if nace_tahmin_mi(nace_source) else ""


def nace_metni(nace_code: str | None, nace_source: str | None) -> str:
    """D-252/2: etiketsiz NACE sunulamaz.

    >>> nace_metni('29.10', 'sector_default')
    '29.10 (tahmini sektör)'
    >>> nace_metni('29.10', 'mersis')
    '29.10'
    >>> nace_metni(None, 'mersis')
    '—'
    """
    if not nace_code or not str(nace_code).strip():
        return BOS
    etiket = nace_etiketi(nace_source)
    return f"{nace_code} ({etiket})" if etiket else str(nace_code)


def sektor_sayaci(satirlar) -> dict:
    """D-252/5: tahmin kaynakli kod kutlesi sektor sayacina girmez.

    satirlar: (nace_code, nace_source) ureten yinelenebilir.
    Doner: {"kanitli": {kod: adet}, "tahmin_haric": adet, "kanitli_toplam": adet}

    >>> s = sektor_sayaci([('29.10', 'sector_default')] * 3 + [('62.01', 'mersis')])
    >>> s['kanitli'], s['tahmin_haric'], s['kanitli_toplam']
    ({'62.01': 1}, 3, 1)
    """
    kanitli: dict[str, int] = {}
    haric = 0
    for kod, kaynak in satirlar:
        if not kod or not str(kod).strip():
            continue
        if nace_tahmin_mi(kaynak):
            haric += 1
            continue
        kanitli[str(kod)] = kanitli.get(str(kod), 0) + 1
    return {
        "kanitli": kanitli,
        "tahmin_haric": haric,
        "kanitli_toplam": sum(kanitli.values()),
    }


BANT_SAYISI = 5


def bantlar(tavan: float, adet: int = BANT_SAYISI) -> list[tuple[str, float, float]]:
    """Bantlar TAVANDAN turetilir; 0-100 gibi sabit esik yazilmaz.

    Tavan degisince bant sinirlari da degisir — aksi halde "80-100 bandinda
    firma yok" gibi ulasilamaz bir hedef panelde durur.

    >>> [e for e, _a, _u in bantlar(6.5)]
    ['0.00-1.30', '1.30-2.60', '2.60-3.90', '3.90-5.20', '5.20-6.50']
    """
    t = float(tavan)
    dilim = t / adet
    out = []
    for i in range(adet):
        alt = round(i * dilim, 2)
        ust = round((i + 1) * dilim, 2) if i < adet - 1 else t
        out.append((f"{alt:.2f}-{ust:.2f}", alt, ust))
    return out


def bant_dagilimi(puanlar, tavan: float) -> dict[str, int]:
    """D-249: None/NaN puan hicbir banda girmez, "olculmedi" olarak ayri durur.

    >>> bant_dagilimi([float('nan')], 6.5)['olculmedi']
    1
    """
    bnt = bantlar(tavan)
    sayac = {e: 0 for e, _a, _u in bnt}
    sayac["olculmedi"] = 0
    for p in puanlar:
        if _yok_mu(p):
            sayac["olculmedi"] += 1
            continue
        v = float(p)
        for etiket, _alt, ust in bnt:
            if v <= ust:
                sayac[etiket] += 1
                break
        else:
            sayac[bnt[-1][0]] += 1
    return sayac


def risk_esigi(tavan: float, oran: float = 0.3) -> float:
    """Risk esigi de tavanin orani; 0-100 olcegindeki 30 sabiti yalandir.

    >>> risk_esigi(6.5)
    1.95
    """
    return round(float(tavan) * oran, 2)


@lru_cache(maxsize=1)
def tavan_getir() -> float:
    """Canli veriden tavan (D-238). Ekran basina DB turu atilmasin diye onbellekli.

    Hata yutulmaz: DB yoksa panel patlar. Sessizce AZAMI'ye dusmek, tam bu
    gorevde kaldirdigimiz yalanin aynisi olur.
    """
    return float(tavan_raporu()["tavan"])


def tavan_ozeti() -> dict:
    """Panelde tek blok: olcek metni + kilitli alanlar + gerekceleri."""
    rapor = tavan_raporu()
    return {
        **rapor,
        "metin": tavan_metni(rapor["tavan"]),
        "kilit_satirlari": kilit_satirlari(rapor["kilitli"]),
    }
