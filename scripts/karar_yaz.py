#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Genel karar kaydedici — decision_log.jsonl'ye idempotent ekler.

Kullanim:
  python scripts/karar_yaz.py --dosya plans/yeni_karar.json

JSON dosyasi tek karar ya da karar listesi olabilir. 'id' alani zorunlu.
Ayni id varsa dokunmaz. [[D-86]] cmd.exe kurali geregi: cok satirli -c yok.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOG = ROOT / "data" / "orchestrator" / "decision_log.jsonl"


def mevcut_idler() -> set[str]:
    if not LOG.exists():
        return set()
    idler = set()
    for satir in LOG.read_text(encoding="utf-8").splitlines():
        if not satir.strip():
            continue
        try:
            kayit = json.loads(satir)
        except json.JSONDecodeError:
            continue
        if isinstance(kayit, dict) and kayit.get("id"):
            idler.add(kayit["id"])
    return idler


def ekle(kararlar: list[dict]) -> tuple[int, int]:
    """Yeni kararlari ekler. (eklenen, atlanan) doner."""
    var_olan = mevcut_idler()
    yeni = [k for k in kararlar if k.get("id") and k["id"] not in var_olan]
    atlanan = len(kararlar) - len(yeni)

    if yeni:
        mevcut = LOG.read_text(encoding="utf-8") if LOG.exists() else ""
        if mevcut and not mevcut.endswith("\n"):
            mevcut += "\n"
        mevcut += "".join(json.dumps(k, ensure_ascii=False) + "\n" for k in yeni)
        LOG.write_text(mevcut, encoding="utf-8")

    return len(yeni), atlanan


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--dosya", required=True, help="Karar JSON dosyasi (tek obje ya da liste)")
    args = ap.parse_args()

    yol = ROOT / args.dosya if not Path(args.dosya).is_absolute() else Path(args.dosya)
    if not yol.exists():
        print(f"[ERROR] Dosya yok: {yol}")
        return 1

    veri = json.loads(yol.read_text(encoding="utf-8"))
    kararlar = veri if isinstance(veri, list) else [veri]

    eksik = [i for i, k in enumerate(kararlar) if not k.get("id")]
    if eksik:
        print(f"[ERROR] 'id' alani eksik, sira: {eksik}")
        return 1

    eklenen, atlanan = ekle(kararlar)
    print(f"[OK] Eklenen: {eklenen}, atlanan (zaten var): {atlanan}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
