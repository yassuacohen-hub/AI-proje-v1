# -*- coding: utf-8 -*-
"""Unvan tokenlarinin siralamasini olcer -> "genel" (ayirt edici DEGIL) listesi.

Neden (D-224/D-245): `icerik_dogrula` "unvandan >=2 ayirt edici kelime
icerikte gecsin" kuralini kullanir. `makina`, `sanayi`, `ticaret`,
`cicekcilik` gibi **sektor kelimeleri** her firmanin sayfasinda gecer; onlar
sayilirsa kural anlamini yitirir. 2026-10-04 pilotu bunu kanitladi:
`AKIN MAKINA ...` -> `ostimbul.com` (Ostim bulteni) ve
`OZLEM CIECEKILIK` -> `cicekrehberi.net` (cicek dizini) "gecti".

Bu betik listeyi UYDURMAZ: canli `companies.legal_name` tokenlarinin
frekansini olcer. Frekansi esik uzerindeki token = genel kelime.

Tek kullanim, salt okunur. Idempotent (hicbir sey yazmaz).
"""
from __future__ import annotations

import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except AttributeError:
    pass

#: Esik: bu oranin ustundeki token ayirt edici DEGIL sayilir.
ORAN_USTU = 0.004          # unvanlarin %0.4'inden fazla
TOKEN_DESENI = re.compile(r"[a-z0-9]+")


def _duz(metin: str) -> str:
    """Turkce katlama + ASCII'ye indirme (modulle ayni kural, tek kopya yok:
    burada yalniz olcum icin; kaynak `yazma_kapisi.temizle` degil)."""
    m = metin.replace("İ", "i").replace("I", "i")
    m = m.replace("ı", "i").replace("Ş", "s").replace("ş", "s")
    m = m.replace("Ğ", "g").replace("ğ", "g").replace("Ç", "c").replace("ç", "c")
    m = m.replace("Ö", "o").replace("ö", "o").replace("Ü", "u").replace("ü", "u")
    return m.lower()


def olcum(engine, oran_ustu: float = ORAN_USTU) -> dict:
    from sqlalchemy import text

    with engine.connect() as conn:
        unvanlar = [r[0] for r in conn.execute(
            text("SELECT legal_name FROM companies WHERE legal_name IS NOT NULL"))]
    sayac: Counter[str] = Counter()
    for unvan in unvanlar:
        sayac.update(set(TOKEN_DESENI.findall(_duz(unvan))))
    n = len(unvanlar) or 1
    sirali = sorted(sayac.items(), key=lambda kv: (-kv[1], kv[0]))
    genel = [(k, v) for k, v in sirali if v / n > oran_ustu]
    return {"unvan": n, "token": len(sayac), "oran_ustu": oran_ustu,
            "genel_sayi": len(genel), "genel": genel}


def main() -> int:
    from company_master.db.connection import get_engine
    sonuc = olcum(get_engine())
    print(f"unvan={sonuc['unvan']}  token={sonuc['token']}  "
          f"esik=%{sonuc['oran_ustu'] * 100:.2f}  genel={sonuc['genel_sayi']}")
    print(f"unvanin %0.4'unden fazla gecen -> AYIRT EDICI DEGIL:")
    satir = []
    for kelime, adet in sonuc["genel"]:
        satir.append(f"{kelime}:{adet}")
        if len(satir) == 8:
            print("  " + "  ".join(satir))
            satir = []
    if satir:
        print("  " + "  ".join(satir))

    if "--kod" in sys.argv:
        # Kod bicimi: moduldeki `GENEL_KELIMELER` ile karsilastirilabilir
        # literal uretir (asagida `_drift`).
        kelimeler = sorted(k for k, _ in sonuc["genel"] if len(k) >= 4)
        print("\n--- kod ---")
        print("GENEL_KELIMELER = frozenset({")
        for i in range(0, len(kelimeler), 6):
            print("    " + " ".join(f'"{k}",' for k in kelimeler[i:i + 6]))
        print("})")
        return 0

    if "--drift" in sys.argv:
        return _drift(sonuc)
    return 0


def _drift(sonuc: dict) -> int:
    """Olculen liste ile moduldeki `GENEL_KELIMELER` ayni mi?

    Betigin tuketici kodu budur: liste elle degil buradan uretilir. Eskiyse
    koda yeni olcum islenir (D-245: doluluk degil, olcum).
    """
    from company_master.etl.web_sitesi_zenginlestir import GENEL_KELIMELER

    olculen = {k for k, _ in sonuc["genel"] if len(k) >= 4}
    kodda = set(GENEL_KELIMELER)
    eksik = sorted(olculen - kodda)
    fazla = sorted(kodda - olculen)
    if not eksik and not fazla:
        print(f"[OK] kod ve olcum ayni ({len(kodda)} kelime)")
        return 0
    if eksik:
        print(f"[UYARI] olcumde var, kodda YOK ({len(eksik)}): "
              + " ".join(eksik))
    if fazla:
        print(f"[UYARI] kodda var, olcumde eski ({len(fazla)}): "
              + " ".join(fazla))
    print("-> once degeri isle (asagidaki --kod ciktisini kullan), sonra "
          "tekrar calistir")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
