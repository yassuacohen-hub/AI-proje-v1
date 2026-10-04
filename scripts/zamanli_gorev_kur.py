# -*- coding: utf-8 -*-
"""Haftalik Continue taramasi icin Windows zamanlanmis gorev kurar/sonlandirir.

Neden Python ile: `schtasks /tr` tirkacisi cmd tarafindan yeniden ayristirilir;
Python'in `subprocess` listesi tek katmanda kalir, tirnak kacisi yoktur
(olcum: bu hatayi iki kez yasadik).

    python scripts/zamanli_gorev_kur.py            # kur (varsa guncelle)
    python scripts/zamanli_gorev_kur.py --kontrol  # sadece durum
    python scripts/zamanli_gorev_kur.py --sil      # kaldir

Anahtar degerleri bu dosyada veya ciktida YOKTUR (D-288).
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

KOK = Path(__file__).resolve().parents[1]
GOREV_ADI = "Huginn_Continue_Haftalik"
HEDEF = KOK / "scripts" / "continue_haftalik_bildir.py"
GUN = "MON"
SAAT = "09:00"


def _python() -> str:
    """Aktif yorumlayici; yoksa sistem python'u."""
    return sys.executable or "python"


def komut(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["schtasks", *args], capture_output=True,
                          text=True, errors="replace")


def kur() -> int:
    if not HEDEF.is_file():
        print("HATA: hedef betik yok: " + str(HEDEF))
        return 2
    # schtasks /tr tek tirnakli komut ister; ic ice tirnak dogru uretilir.
    satir = '"{}" -X utf8 "{}"'.format(_python(), HEDEF)
    cp = komut("/create", "/tn", GOREV_ADI, "/tr", satir,
               "/sc", "weekly", "/d", GUN, "/st", SAAT, "/f")
    print("KURULDU" if cp.returncode == 0 else "HATA")
    print((cp.stdout or cp.stderr).strip()[:400])
    if cp.returncode == 0:
        print(f"hedef: {satir}")
    return cp.returncode


def kontrol() -> int:
    cp = komut("/query", "/tn", GOREV_ADI, "/v", "/fo", "list")
    print((cp.stdout or cp.stderr).strip()[:900])
    return cp.returncode


def sil() -> int:
    cp = komut("/delete", "/tn", GOREV_ADI, "/f")
    print("SILINDI" if cp.returncode == 0 else "HATA")
    print((cp.stdout or cp.stderr).strip()[:300])
    return cp.returncode


def main() -> int:
    p = argparse.ArgumentParser(description="Zamanlanmis gorev yonetimi")
    p.add_argument("--kontrol", action="store_true")
    p.add_argument("--sil", action="store_true")
    a = p.parse_args()
    if a.kontrol:
        return kontrol()
    if a.sil:
        return sil()
    return kur()


if __name__ == "__main__":
    raise SystemExit(main())