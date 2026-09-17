# -*- coding: utf-8 -*-
"""TEST-CI-01: Pano artefaktı izolasyon guard'ı.

Test koşusundan önce ``data/orchestrator/*.json`` dosyalarının md5 anlık
görüntüsünü alır; koşudan sonra karşılaştırır. Fark varsa testlerin gerçek
panoya sızdığı (TEST-ISO-02) anlaşılır ve süreç 1 ile çıkar.

Kullanım::

    python scripts/pano_guard.py snapshot --out /tmp/pano.json
    python -m pytest ...
    python scripts/pano_guard.py check --in /tmp/pano.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

VARSAYILAN_DIZIN = Path("data/orchestrator")


def md5_hesapla(yol: Path) -> str:
    """Dosyanın md5 özetini döndürür (bellek dostu, parça parça)."""
    h = hashlib.md5()  # noqa: S324 - bütünlük karşılaştırması, güvenlik değil
    with open(yol, "rb") as f:
        for parca in iter(lambda: f.read(65536), b""):
            h.update(parca)
    return h.hexdigest()


def anlik_goruntu(dizin: Path = VARSAYILAN_DIZIN) -> dict[str, str]:
    """``dizin`` altındaki (yalnız üst seviye) ``*.json`` dosyaları → ``{ad: md5}``."""
    if not dizin.is_dir():
        return {}
    return {
        p.name: md5_hesapla(p)
        for p in sorted(dizin.glob("*.json"))
        if p.is_file()
    }


def farklar(once: dict[str, str], sonra: dict[str, str]) -> list[str]:
    """İki anlık görüntü arasındaki farkları insan okunur satırlar olarak döndürür."""
    satirlar: list[str] = []
    for ad in sorted(set(once) | set(sonra)):
        if ad not in once:
            satirlar.append(f"YENI     {ad}")
        elif ad not in sonra:
            satirlar.append(f"SILINDI  {ad}")
        elif once[ad] != sonra[ad]:
            satirlar.append(f"DEGISTI  {ad}")
    return satirlar


def cmd_snapshot(args: argparse.Namespace) -> int:
    goruntu = anlik_goruntu(Path(args.dizin))
    Path(args.out).write_text(json.dumps(goruntu, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[pano_guard] {len(goruntu)} dosya kaydedildi -> {args.out}")
    return 0


def cmd_check(args: argparse.Namespace) -> int:
    once = json.loads(Path(args.inp).read_text(encoding="utf-8"))
    sonra = anlik_goruntu(Path(args.dizin))
    fark = farklar(once, sonra)
    if not fark:
        print("[pano_guard] OK — pano artefaktlari degismedi")
        return 0
    print("::error::Testler data/orchestrator/*.json dosyalarini degistirdi (TEST-ISO-02 sizintisi)")
    for satir in fark:
        print(f"  {satir}")
    return 1


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dizin", default=str(VARSAYILAN_DIZIN), help="izlenecek dizin (varsayılan: data/orchestrator)")
    alt = ap.add_subparsers(dest="komut", required=True)
    s = alt.add_parser("snapshot", help="md5 anlık görüntüsünü yaz")
    s.add_argument("--out", required=True)
    s.set_defaults(fn=cmd_snapshot)
    c = alt.add_parser("check", help="anlık görüntü ile karşılaştır; fark varsa 1")
    c.add_argument("--in", dest="inp", required=True)
    c.set_defaults(fn=cmd_check)
    args = ap.parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
