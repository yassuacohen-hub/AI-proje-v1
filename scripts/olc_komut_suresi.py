# -*- coding: utf-8 -*-
"""Makine donmasi olcumu: su an calisan ajan surecleri + tipik komutun suresi.

Neden: 'tum ajanlar komut yazinca bilgisayar donuyor' sikayeti. Tahmin yasak (D-260);
once kac python/pwsh/node sureci var ve tek `gorev_kutusu bak` kac saniye suruyor olculur.
Kullanim: python scripts/olc_komut_suresi.py
"""
from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path

KOK = Path(__file__).resolve().parent.parent
IZLENEN = ("python.exe", "pwsh.exe", "powershell.exe", "node.exe", "Code.exe", "docker.exe")


def surecler() -> dict[str, int]:
    """tasklist ile isim bazli sayim (Windows; psutil bagimliligi eklenmez)."""
    cikti = subprocess.run(["tasklist", "/FO", "CSV", "/NH"], capture_output=True, text=True,
                           encoding="cp1254", errors="replace").stdout
    sayim = {ad: 0 for ad in IZLENEN}
    for satir in cikti.splitlines():
        ad = satir.split('","')[0].strip('"')
        if ad in sayim:
            sayim[ad] += 1
    return sayim


def sure(cmd: list[str], env: dict | None = None) -> float:
    t = time.perf_counter()
    subprocess.run(cmd, cwd=KOK, capture_output=True, env=env)
    return round(time.perf_counter() - t, 2)


def main() -> int:
    print("surecler:", surecler())
    ortam = dict(os.environ)
    print("gorev_kutusu bak --ajan utku (notion dahil):", sure([sys.executable, "scripts/gorev_kutusu.py", "bak", "--ajan", "utku"], ortam), "s")
    ortam_sessiz = dict(ortam, HUGINN_NOTION_KAPALI="1")
    print("gorev_kutusu bak --ajan utku (HUGINN_NOTION_KAPALI=1):", sure([sys.executable, "scripts/gorev_kutusu.py", "bak", "--ajan", "utku"], ortam_sessiz), "s")
    print("chat_al.py oku --ajan utku:", sure([sys.executable, "scripts/chat_al.py", "oku", "--ajan", "utku"]), "s")
    print("python -c pass (yorumlayici acilisi):", sure([sys.executable, "-c", "pass"]), "s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
