# -*- coding: utf-8 -*-
"""Mojibake onarici (ENC-ADMIN-PANEL-01).

UTF-8 metnin cp1252 olarak yeniden kodlanmasiyla olusan cift kodlama
bozulmalarini ("\u00c3\u00a7" -> "\u00e7", "\u00e2\u20ac\u201d" -> "\u2014", "\u00e2\u0161\u2122\u00ef\u00b8" -> "\u2699\ufe0f") satir bazinda onarir.

Kullanim:
    python scripts/mojibake_onar.py web_dashboard/tabs/admin_panel.py [--kontrol]
    python scripts/mojibake_onar.py app.py --kalinti-temizle

--kontrol: dosyaya yazmaz, yalnizca bulgu sayisini basar (exit 1 = mojibake var).
--kalinti-temizle: cp1252 cevriminin cozemedigi kirik emoji kalintilarini
    (U+FFFD ve C1 kontrol karakterleri U+0080-U+009F) siler (KPI-EXA-02).
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# Tipik cift-kodlama izleri (UTF-8 cok baytli dizilerin cp1252 gorunumu).
MOJIBAKE_RX = re.compile(r"\u00c3.|\u00c2.|\u00e2\u20ac.|\u00e2\u201e.|\u00e2\u0161.|\u00ef\u00b8|\u00c4.|\u00c5.")

# Cift kodlamada tamamen kaybolan emoji kalintilari (geri kurtarilamaz).
KALINTI_RX = re.compile(r"[\ufffd\u0080-\u009f]")


def _cp1252_bayt(karakter: str) -> bytes:
    """cp1252'de tanimsiz 0x81/0x8D/0x8F/0x90/0x9D noktalarina latin-1 ile duser."""
    try:
        return karakter.encode("cp1252")
    except UnicodeEncodeError:
        return karakter.encode("latin-1")


def satir_onar(satir: str) -> str | None:
    """Satiri cp1252->utf8 ile geri cozer; cozulemiyorsa None."""
    try:
        ham = b"".join(_cp1252_bayt(k) for k in satir)
        return ham.decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return None


def kalinti_temizle(metin: str) -> tuple[str, int]:
    """Kurtarilamayan kirik emoji kalintilarini siler; (yeni metin, silinen)."""
    silinen = len(KALINTI_RX.findall(metin))
    if not silinen:
        return metin, 0
    temiz = KALINTI_RX.sub("", metin)
    # Kalinti silinince olusan cift bosluklari toparla (yalniz yatay bosluklar, satir sonu degil).
    temiz = re.sub(r'(f?")[ \t]{2,}', r"\1", temiz)
    return temiz, silinen


def dosya_onar(yol: Path, kontrol: bool = False, kalinti: bool = False) -> tuple[int, int, int]:
    """Donus: (duzeltilen, atlanan, kalan)."""
    metin = yol.read_text(encoding="utf-8")
    satirlar = metin.split("\n")
    duzeltilen = atlanan = 0
    for i, satir in enumerate(satirlar):
        if not MOJIBAKE_RX.search(satir):
            continue
        yeni = satir_onar(satir)
        if yeni is None or yeni == satir:
            atlanan += 1
            print(f"ATLANDI {yol}:{i + 1}: {satir.strip()[:70]!r}")
            continue
        duzeltilen += 1
        print(f"{yol}:{i + 1}: {satir.strip()[:50]!r} -> {yeni.strip()[:50]!r}")
        satirlar[i] = yeni
    sonuc = "\n".join(satirlar)
    if kalinti:
        sonuc, silinen = kalinti_temizle(sonuc)
        if silinen:
            duzeltilen += silinen
            print(f"{yol}: kalinti silindi={silinen}")
    if not kontrol and duzeltilen:
        yol.write_text(sonuc, encoding="utf-8", newline="")
    kalan = len(MOJIBAKE_RX.findall(sonuc))
    return duzeltilen, atlanan, kalan


def main() -> int:
    # Windows cp1254 konsolunda '→' gibi karakterler UnicodeEncodeError vermesin.
    for akis in (sys.stdout, sys.stderr):
        if hasattr(akis, "reconfigure"):
            akis.reconfigure(encoding="utf-8", errors="replace")

    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("dosyalar", nargs="+", help="Onarilacak UTF-8 dosyalar")
    ap.add_argument("--kontrol", action="store_true", help="Yazma; sadece raporla")
    ap.add_argument("--kalinti-temizle", action="store_true", dest="kalinti",
                    help="Kurtarilamayan kirik emoji kalintilarini sil")
    args = ap.parse_args()

    toplam_kalan = 0
    for d in args.dosyalar:
        yol = Path(d)
        if not yol.is_file():
            print(f"YOK: {yol}")
            return 2
        duz, atl, kal = dosya_onar(yol, kontrol=args.kontrol, kalinti=args.kalinti)
        toplam_kalan += kal
        print(f"{yol}: duzeltilen={duz} atlanan={atl} kalan={kal}")
    return 1 if toplam_kalan else 0


if __name__ == "__main__":
    sys.exit(main())
