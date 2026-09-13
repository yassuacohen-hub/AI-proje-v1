# -*- coding: utf-8 -*-
"""Exa API ile arama/sayfa cekme yardimcisi.

Kullanim:
    python scripts/exa_arastir.py ara "sorgu metni" --sayi 8 --cikti data/out.json
    python scripts/exa_arastir.py getir https://ornek.com --cikti data/page.json

API anahtari .env icindeki EXA_API_KEY'den okunur.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

KOK = Path(__file__).resolve().parents[1]
EXA_SEARCH = "https://api.exa.ai/search"
EXA_CONTENTS = "https://api.exa.ai/contents"


def api_key_oku() -> str:
    key = os.environ.get("EXA_API_KEY", "").strip()
    if key:
        return key
    env_yolu = KOK / ".env"
    if env_yolu.exists():
        for satir in env_yolu.read_text(encoding="utf-8", errors="replace").splitlines():
            satir = satir.strip()
            if satir.startswith("EXA_API_KEY="):
                return satir.split("=", 1)[1].strip().strip('"').strip("'")
    raise RuntimeError("EXA_API_KEY bulunamadi (.env veya ortam degiskeni)")


def istek(url: str, govde: dict[str, Any], key: str, zaman_asimi: int = 45) -> dict[str, Any]:
    req = urllib.request.Request(
        url,
        data=json.dumps(govde).encode("utf-8"),
        method="POST",
    )
    req.add_header("Content-Type", "application/json")
    req.add_header("x-api-key", key)
    try:
        with urllib.request.urlopen(req, timeout=zaman_asimi) as resp:
            ham = resp.read().decode("utf-8", errors="replace")
            return {"ok": True, "status": resp.status, "data": json.loads(ham)}
    except urllib.error.HTTPError as e:
        return {
            "ok": False,
            "status": e.code,
            "hata": e.read().decode("utf-8", errors="replace")[:2000],
        }
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "status": None, "hata": f"{type(e).__name__}: {e}"}


def cmd_ara(args: argparse.Namespace) -> int:
    key = api_key_oku()
    govde: dict[str, Any] = {
        "query": args.sorgu,
        "numResults": args.sayi,
        "contents": {"text": {"maxCharacters": args.karakter}},
    }
    if args.tur:
        govde["type"] = args.tur
    sonuc = istek(EXA_SEARCH, govde, key)
    return _yaz(sonuc, args.cikti)


def cmd_getir(args: argparse.Namespace) -> int:
    key = api_key_oku()
    govde = {
        "urls": args.urls,
        "text": {"maxCharacters": args.karakter},
    }
    sonuc = istek(EXA_CONTENTS, govde, key)
    return _yaz(sonuc, args.cikti)


def _yaz(sonuc: dict[str, Any], cikti: str | None) -> int:
    metin = json.dumps(sonuc, ensure_ascii=False, indent=2)
    if cikti:
        yol = Path(cikti)
        yol.parent.mkdir(parents=True, exist_ok=True)
        yol.write_text(metin, encoding="utf-8")
        print(f"YAZILDI: {yol} (ok={sonuc.get('ok')} status={sonuc.get('status')})")
    else:
        print(metin)
    return 0 if sonuc.get("ok") else 1


def main() -> int:
    p = argparse.ArgumentParser(description="Exa API arastirma araci")
    alt = p.add_subparsers(dest="komut", required=True)

    a = alt.add_parser("ara", help="Exa arama")
    a.add_argument("sorgu")
    a.add_argument("--sayi", type=int, default=8)
    a.add_argument("--karakter", type=int, default=2000)
    a.add_argument("--tur", default="", help="auto|neural|keyword")
    a.add_argument("--cikti", default="")
    a.set_defaults(func=cmd_ara)

    g = alt.add_parser("getir", help="URL icerigi cek")
    g.add_argument("urls", nargs="+")
    g.add_argument("--karakter", type=int, default=4000)
    g.add_argument("--cikti", default="")
    g.set_defaults(func=cmd_getir)

    args = p.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
