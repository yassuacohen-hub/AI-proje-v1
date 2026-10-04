# -*- coding: utf-8 -*-
"""Git hook kurulumu — hook'u repo disindan repo icine tasir.

NEDEN GEREKLI (D-333): `.git/hooks/` git'e OZELDIR, versiyonlanmaz.
Bu yuzden D-332'de yazilan TOCTOU korumasi ve hook exit duzeltmesi
baska ajanlara ve yeni klonlara GITMEZDI; her makinede ayrica elle
kurulmasi gerekirdi.

KAYNAK (SSOT): scripts/hooks/pre-commit.sh  ->  .git/hooks/pre-commit
Kaynak dosya degistiginde yeniden calistir: python scripts/hook_kur.py

Kullanim:
    python scripts/hook_kur.py           # kur (veya guncelle)
    python scripts/hook_kur.py --kontrol # kurulu mu, ayni mi? (yazmaz)
"""
from __future__ import annotations

import argparse
import hashlib
import pathlib
import sys

KOK = pathlib.Path(__file__).resolve().parents[1]
KAYNAK = KOK / "scripts" / "hooks" / "pre-commit.sh"
HEDEF = KOK / ".git" / "hooks" / "pre-commit"


def _izi(p: pathlib.Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()[:16] if p.is_file() else "(yok)"


def kur(uret: bool = True) -> int:
    if not KAYNAK.is_file():
        print(f"HATA: kaynak yok -> {KAYNAK}")
        return 1
    if not uret:
        a, b = _izi(KAYNAK), _izi(HEDEF)
        print(f"kaynak : {a}")
        print(f"hedef  : {b}")
        if a == b:
            print("DURUM: kurulu ve guncel")
            return 0
        print("DURUM: FARKLI - kurmak icin: python scripts/hook_kur.py")
        return 1

    HEDEF.parent.mkdir(parents=True, exist_ok=True)
    HEDEF.write_bytes(KAYNAK.read_bytes())
    if sys.platform != "win32":
        HEDEF.chmod(0o755)
    print(f"KURULDU: {HEDEF}")
    print(f"  kaynak -> hedef  ({_izi(KAYNAK)})")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--kontrol", action="store_true",
                    help="Sadece kontrol et, yazma")
    a = ap.parse_args()
    return kur(uret=not a.kontrol)


if __name__ == "__main__":
    sys.exit(main())
