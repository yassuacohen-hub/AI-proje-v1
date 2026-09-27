"""D-217/D-218 brif şablon denetimi — TEK KAYNAK.

Kural gövdesi burada yaşar. İki tüketici vardır:
  1. tests/test_brief_sablon_denetim.py — geriye dönük mandal (baseline büyümez)
  2. scripts/gorev_at.py `ata` — ileriye dönük kapı (uyumsuz brifle görev atanmaz)

Neden ayrı dosya (D-211): kural testin içinde yaşarken `ata` komutu onu
çağıramıyordu. `ata` içine ikinci bir kopya yazmak ikiz mantık üretirdi —
biri güncellenip diğeri çürürdü. Tek gövde, iki çağıran.

Ölçüm (2026-09-27): 9 brif şablonsuz yazılmış, 108 eksik bölüm vardı.
Test bunları yakaladı ama ATAMA anında değil, commit sonrası. Bu dosya
kapıyı atama anına taşır.

Elle çalıştırma:
    python scripts/brief_denetim.py plans/brief_utku_VERI-02.md
"""

from __future__ import annotations

import sys
from pathlib import Path

KOK = Path(__file__).resolve().parent.parent
SABLON = KOK / "plans" / "_brief_sablon.md"

# D-217 zorunlu bölümler. "## Adımlar" yerine "## Faz A" da kabul (toplu iş).
ZORUNLU = [
    "**Başlık:**",
    "**Öncelik:**",
    "**Hub:**",
    "## Neden",
    "## Doğrulanacak varsayım",
    "## Kabul kriteri",
    "## Ajan chat zorunlu",
    "## Teslim",
    "## Ilgili Nodlar",  # D-218 Obsidyen grafiği — linksiz doküman = grep maliyeti
]

# D-218: en az bu kadar wikilink. Linksiz doküman grafikten kopuk kalır,
# ajan onu bulmak için tüm repoyu tarar (token + süre maliyeti).
MIN_WIKILINK = 2


def eksikler(brif: Path) -> list[str]:
    """Brifin taşımadığı zorunlu bölümleri döner. Boş liste = uyumlu."""
    metin = brif.read_text(encoding="utf-8")
    eksik = [b for b in ZORUNLU if b not in metin]
    if "## Adımlar" not in metin and "## Faz A" not in metin:
        eksik.append("## Adımlar|## Faz A")
    if "ajan_chat.py" not in metin:
        eksik.append("ajan_chat.py komut referansı")
    if metin.count("[[") < MIN_WIKILINK:
        eksik.append(f"en az {MIN_WIKILINK} Obsidyen wikilink [[...]] (D-218)")
    return eksik


def sablon_kopyala(hedef: Path) -> Path:
    """Kanonik şablonu `hedef`e yazar; sonuç garantili uyumludur.

    İki kullanım: (a) yeni brif iskeleti, (b) testlerde uyumlu brif üretmek.
    Testler kendi elle yazdıkları içerikle uyumlu brif taklidi yapmasın —
    şablon değişince testler sessizce çürür.
    """
    hedef.parent.mkdir(parents=True, exist_ok=True)
    hedef.write_text(SABLON.read_text(encoding="utf-8"), encoding="utf-8")
    return hedef


def main(argv: list[str] | None = None) -> int:
    yollar = argv if argv is not None else sys.argv[1:]
    if not yollar:
        print("kullanim: python scripts/brief_denetim.py <brif.md> [...]", file=sys.stderr)
        return 2
    kirli = 0
    for s in yollar:
        p = Path(s)
        if not p.is_file():
            print(f"YOK     : {s}", file=sys.stderr)
            kirli += 1
            continue
        eks = eksikler(p)
        if eks:
            kirli += 1
            print(f"UYUMSUZ : {p.name} — eksik: {eks}", file=sys.stderr)
        else:
            print(f"UYUMLU  : {p.name}")
    return 1 if kirli else 0


if __name__ == "__main__":
    raise SystemExit(main())
