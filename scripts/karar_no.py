# -*- coding: utf-8 -*-
"""Karar numarasi TEK KAPI: sonraki bos D-NNN'i soyler (D-227 + D-283).

D-281'e kadar numara iki dosyadan bagimsiz veriliyordu; D-281 iki ayri karara
birden verildi. Sebep ihlal degil, **gorusuz mandal**: D-227 mandali yalnizca
AGENTS.md'ye bakiyor ve yalnizca `(D-NNN — KAHIN...)` bicimini taniyordu;
`docs/BORC_DEFTERI.md`'nin `## D-NNN — ...` basliklari gorunmezdi.

Urun sahibinin yetkisi kisitlanmaz: karar BASKA dosyaya da yazilabilir.
Kisitlanan tek sey numaranin KAYNAGI -- havuz burada birlesir.

    python scripts/karar_no.py          # sonraki bos numara + catisma raporu
    python scripts/karar_no.py --al     # numarayi ATOMIK kapatir (O_EXCL)

D-285 olcumu: yalnizca "sonraki bos"u SOYLEMEK yetmedi -- ayni numara iki ajana
saniyeler arayla bos gorundu (D-283 ve D-284 iki kez cakisti). Olcum anliktir,
tahsis degildir. `--al` numarayi dosya olusturarak kapatir; ikinci ajan ayni
numarayi alamaz.
"""
from __future__ import annotations

import os
import re
import sys
from datetime import datetime
from pathlib import Path

KOK = Path(__file__).resolve().parents[1]
# Numara havuzunu olusturan dosyalar (yeni dosya eklenirse buraya yazilir)
HAVUZ = (KOK / "AGENTS.md", KOK / "docs" / "BORC_DEFTERI.md")
TAHSIS = KOK / "data" / "karar_tahsis"
# Iki bicim: "## Baslik (D-NNN — KAHIN...)" ve "## D-NNN — ..."
BASLIK = re.compile(r"^#+ (?:.*?\(D-(\d{1,3}) [\u2014-] KAH|D-(\d{1,3})\b)", re.M)


def numaralar(yol: Path) -> dict[int, str]:
    """Dosyadaki karar numaralari -> ilk gorulen baslik satiri."""
    if not yol.is_file():
        return {}
    metin = yol.read_text(encoding="utf-8", errors="replace")
    out: dict[int, str] = {}
    for m in BASLIK.finditer(metin):
        n = int(m.group(1) or m.group(2))
        out.setdefault(n, metin[m.start():metin.find("\n", m.start())].strip())
    return out


def havuz() -> list[dict[int, str]]:
    return [numaralar(y) for y in HAVUZ]


def catismalar() -> list[int]:
    """Birden cok dosyada kanonik baslik tasiyan numaralar."""
    h = havuz()
    return sorted({n for i, a in enumerate(h) for b in h[i + 1:] for n in a if n in b})


def tahsisli() -> set[int]:
    """Kapatilmis ama henuz belgeye yazilmamis numaralar."""
    return {int(p.stem[2:]) for p in TAHSIS.glob("D-*.txt") if p.stem[2:].isdigit()}


def sonraki() -> int:
    return max({max(d) for d in havuz() if d} | tahsisli() | {0}) + 1


def al(ajan: str) -> int:
    """Numarayi ATOMIK kapatir; yarisi kaybeden bir sonrakine gecer."""
    TAHSIS.mkdir(parents=True, exist_ok=True)
    n = sonraki()
    while True:
        try:
            fd = os.open(TAHSIS / f"D-{n}.txt", os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError:
            n += 1
            continue
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(f"{ajan} {datetime.now().isoformat(timespec='seconds')}\n")
        return n


def main() -> int:
    h = havuz()
    for yol, d in zip(HAVUZ, h):
        print(f"{yol.name}: {len(d)} baslik, max=D-{max(d) if d else 0}")
    if c := catismalar():
        print(f"CATISMA: {['D-%d' % n for n in c]}", file=sys.stderr)
    if "--al" in sys.argv:
        # ponytail: ajan adi git'ten; tahsis ancak TUM ajanlar `--al` kullanirsa
        # tam korur. Yukseltme: karar yazan her yol bu kapidan gecirilir.
        ad = os.environ.get("HUGINN_AJAN") or "bilinmeyen"
        print(f"TAHSIS EDILDI = D-{al(ad)}")
    else:
        print(f"sonraki bos numara = D-{sonraki()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
