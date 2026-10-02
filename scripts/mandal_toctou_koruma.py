# -*- coding: utf-8 -*-
"""MANDAL-TOCTOU-01 (D-332): paylasilan index yarisi korumasi.

OLCU (2026-10-02): iki kez oldu.
  - 6d86d56: ihsan'in commit'i AGENTS.md + gorev_kutusu.py'imi (D-331 kodu) aldi
  - 8c84522: utku'nun commit'i AGENTS.md'deki D-331 kararimi aldi
Sebep: ajan `git add` ile `git commit` arasinda ~8 saniye geciyor; bu
pencerede baska ajan index'i guncelliyor. Mandal `--name-only` ile TEK
kontrol noktasi kullandigi icin sizmayi gormedi.

COZUM: index parmak izi (blob'larin SHA-1 listesi) mandal ONCESI ve
SONRASI karsilastirilir. Degisirse kanit gecersizdir -> commit durur.

Kullanim:
    python scripts/mandal_toctou_koruma.py oncesi   # parmak izini yaz
    python scripts/mandal_toctou_koruma.py sonrasi   # ayni mi diye bak
"""
from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path

KOK = Path(__file__).resolve().parent.parent
IZ_DOSYA = KOK / "data" / "_mandal_index_izi.tmp"


def index_izi() -> str:
    """Index'in icerik parmak izi (sirali blob SHA-1 listesi)."""
    out = subprocess.run(
        ["git", "diff", "--cached", "--name-only"],
        cwd=KOK, capture_output=True, text=True, encoding="utf-8",
        errors="replace",
    ).stdout
    sat = sorted(x.strip() for x in out.splitlines() if x.strip())
    # yalnizca AD degil, ICERIK de: ayni ad, farkli icerik de yaris sayilir
    detay = []
    for ad in sat:
        sha = subprocess.run(
            ["git", "rev-parse", f":{ad}"],
            cwd=KOK, capture_output=True, text=True, encoding="utf-8",
            errors="replace",
        ).stdout.strip()
        detay.append(f"{ad}={sha}")
    return hashlib.sha256("\n".join(detay).encode("utf-8")).hexdigest()


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    faz = sys.argv[1]
    izi = index_izi()

    if faz == "oncesi":
        IZ_DOSYA.write_text(izi, encoding="utf-8")
        print(f"[toctou] index izi kaydedildi: {izi[:16]}")
        return 0

    if faz == "sonrasi":
        if not IZ_DOSYA.exists():
            print("[toctou] oncesi kaydi yok - atlandi")
            return 0
        eski = IZ_DOSYA.read_text(encoding="utf-8").strip()
        try:
            IZ_DOSYA.unlink()
        except OSError:
            pass
        if eski == izi:
            print(f"[toctou] index degismedi ({izi[:16]}) - kanit gecerli")
            return 0
        print("")
        print("[toctou] INDEX MANDAL CALISIRKEN DEGISTI.")
        print("[toctou] Kanit gecersiz: dogrulama commit'teki icerikle ayni nesneyi gostermiyor.")
        print("[toctou] Baska bir ajan ayni index'i kullaniyor. Tekrar dene.")
        print("")
        return 1

    print(f"[toctou] bilinmeyen faz: {faz}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
