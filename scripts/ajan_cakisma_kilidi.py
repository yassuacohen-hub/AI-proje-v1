# -*- coding: utf-8 -*-
"""ALTYAPI-AJAN-CAKISMA-01: es zamanli ajan calismasinda kilit kapisi.

Kok neden (olcum: FAZ0_RAPOR_kok_hijyeni_2026-09-29): 130 dosya tasinirken
dosya kilidi **sorgulanmadi**. Panoda gorev gorunmemesi, dosyanin bosta
oldugu anlamina gelmiyor.

Var olan ne yapiyor: `scripts/kilit_zorla.py` kilidi **commit aninda**
zorlar. Ama zarar commit'ten once, diskte olusur; commit kapisi gec kalidir.
Bu modul o kapinin **onunde** gelen sorguyu verir.

Tek kaynak (D-211): `ajan_kimligi` / `bayat` / `KILIT` `kilit_zorla`dan alinir,
burada kopya yoktur.

    python scripts/ajan_cakisma_kilidi.py --ajan yasu
    python scripts/ajan_cakisma_kilidi.py --kayitli-son 5
    python scripts/ajan_cakisma_kilidi.py --denetle docs/ODIN_DEPLOYMENT_ARCHITECTURE.md
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(KOK / "scripts"))

from kilit_zorla import KILIT, ajan_kimligi, bayat  # noqa: E402  (tek kaynak)

#: Son kac dakikada degisen dosya "aktif" sayilir. Brief'te `IZIN_KILIT_ESIK`
#: adiyla sabitlendi; kodda baska bir deger **yok** (olcum 2026-10-03), bu yuzden
#: varsayilan burada tanimlaniyor ve env ile degistirilebilir.
VARSAYILAN_ESIK_DAKIKA = int(os.environ.get("IZIN_KILIT_ESIK", "5"))

#: Hareket gostergesi olan dizinler: bunlar kaynak kod degil, artik.
HAREKET_DISI = {".git", ".venv", "node_modules", "__pycache__",
                "_ARSIV_tek_kullanimlik", "yedekler", "backups"}


def kilitleri_oku() -> dict:
    """Kilit dosyasini okur; yoksa bos sozluk doner."""
    if not KILIT.is_file():
        return {}
    try:
        return json.loads(KILIT.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def aktif_kilitler(kilitler: dict | None = None) -> dict:
    """Bayatlamamis kilitler (bayat olan sahipsiz sayilir - D-303)."""
    k = kilitleri_oku() if kilitler is None else kilitler
    return {y: v for y, v in k.items() if not bayat(v)}


def ajan_kilitleri(ajan: str, kilitler: dict | None = None) -> dict:
    """Verilen ajanin aktif kilitleri: {yol: {sahip, task_id, kilitlendi}}."""
    return {y: v for y, v in aktif_kilitler(kilitler).items()
            if v.get("sahip") == ajan}


def kacisi_kilitli(yollar, kilitler: dict | None = None) -> list:
    """Verilen yollardan BASKASININ aktif kilidinde olanlar."""
    k = aktif_kilitler(kilitler)
    return [(y, k[y]) for y in yollar if y in k]


def son_degisenler(dakika: int = VARSAYILAN_ESIK_DAKIKA,
                   kok: Path | None = None) -> list:
    """Son `dakika` dakikada degismis dosyalar (kok'e gore yol)."""
    kok = kok or KOK
    esik = time.time() - max(0, dakika) * 60
    bulunan = []
    for p in kok.rglob("*"):
        if not p.is_file() or HAREKET_DISI & set(p.parts):
            continue
        try:
            if p.stat().st_mtime >= esik:
                bulunan.append(p.relative_to(kok).as_posix())
        except OSError:
            continue
    return sorted(bulunan)
def hareket_uyarisi(dakika: int = VARSAYILAN_ESIK_DAKIKA) -> str | None:
    """Son `dakika` dakikada baska ajanin kilidinde dosya hareketi var mi.

    Doner: uyari metni ya da None. Kilit PANODA olmasa bile dosya hareketi
    varsa kapi kapatilir - brief'in kok nedeni budur.
    """
    hareket = set(son_degisenler(dakika))
    if not hareket:
        return None
    cakisma = kacisi_kilitli(hareket)
    if not cakisma:
        return None
    satirlar = ["KILITLI DOSYA HAREKETI (commit kapisi gec kalmis):"]
    for y, v in sorted(cakisma):
        satirlar.append("  %s -> %s (%s)" % (y, v.get("sahip"), v.get("task_id")))
    satirlar.append("  son %d dakikada degisen toplam dosya: %d" % (dakika, len(hareket)))
    return "\n".join(satirlar)


def kapi_gecer(yollar, ajan: str | None = None,
               kilitler: dict | None = None):
    """Faz B kapisi: (gecer mi, mesaj). Kilitli dosyaya dokunma."""
    ben = ajan if ajan is not None else ajan_kimligi()
    cakisma = kacisi_kilitli(yollar, kilitler)
    if ben is not None:
        cakisma = [(y, v) for y, v in cakisma if v.get("sahip") != ben]
    if not cakisma:
        return True, ""
    satirlar = ["KILIT KAPISI: %d dosya baska ajana ait." % len(cakisma)]
    for y, v in sorted(cakisma):
        satirlar.append("  %s -> %s (%s)" % (y, v.get("sahip"), v.get("task_id")))
    return False, "\n".join(satirlar)


def main() -> int:
    import argparse

    ap = argparse.ArgumentParser(
        description="Eszamanli ajan calismasinda kilit sorgusu ve kapisi")
    ap.add_argument("--ajan", help="ajan adi; aktif kilitlerini listeler")
    ap.add_argument("--kayitli-son", type=int, metavar="DAKIKA",
                    help="son DAKIKA dakikada degisen dosyalar")
    ap.add_argument("--denetle", nargs="+", metavar="YOL",
                    help="verilen yollar kilitli mi diye bakar")
    ap.add_argument("--hareket-uyari", action="store_true",
                    help="son dakikalarda kilitli dosya hareketi var mi")
    a = ap.parse_args()

    if a.denetle:
        gecti, mesaj = kapi_gecer(a.denetle)
        print(mesaj if mesaj else "KILIT YOK: yollar serbest.")
        return 0 if gecti else 3

    if a.hareket_uyari:
        uyari = hareket_uyarisi(a.kayitli_son or VARSAYILAN_ESIK_DAKIKA)
        print(uyari if uyari else "Son dakikalarda kilitli dosya hareketi yok.")
        return 1 if uyari else 0

    if a.kayitli_son is not None:
        for y in son_degisenler(a.kayitli_son):
            print(y)
        return 0

    if a.ajan:
        k = ajan_kilitleri(a.ajan)
        if not k:
            print("%s: aktif kilit yok." % a.ajan)
            return 0
        print("%s: %d aktif kilit" % (a.ajan, len(k)))
        for y, v in sorted(k.items()):
            print("  %s  (%s, %s)" % (y, v.get("task_id"), v.get("kilitlendi")))
        return 0

    k = aktif_kilitler()
    print("Aktif kilit: %d" % len(k))
    for y, v in sorted(k.items()):
        print("  %-11s %s  (%s)" % (v.get("sahip"), y, v.get("task_id")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())