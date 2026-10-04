# -*- coding: utf-8 -*-
"""Zombi terminal sayimi ve temizligi (Windows).

Neden: 2026-10-03 olcum -> 83 powershell.exe acik; her ajan komutu yeni terminal aciyor,
kapanmiyor; makine donuyor. Bu betik once SAYAR (--kuru), onay verilirse bos bekleyen
(CPU 0, komut satiri yalnizca kabuk) powershell/pwsh/cmd sureclerini kapatir.

Kullanim:
    python scripts/zombi_kabuk_temizle.py --kuru     # yalnizca say
    python scripts/zombi_kabuk_temizle.py            # 2 dakikadan eski bos kabuklari kapat
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timedelta

KABUKLAR = ("powershell.exe", "pwsh.exe", "cmd.exe")
_PS = ("Get-CimInstance Win32_Process | Where-Object { $_.Name -in @('powershell.exe','pwsh.exe','cmd.exe') } "
       "| Select-Object ProcessId,Name,CreationDate,CommandLine,WorkingSetSize,ParentProcessId | ConvertTo-Json -Compress")


def listele() -> list[dict]:
    """Sureclerin listesi (ebeveyn, yas, bellek). Bagimlilik yok: tek PowerShell sorgusu."""
    cikti = subprocess.run(["powershell", "-NoProfile", "-Command", _PS], capture_output=True,
                           text=True, encoding="utf-8", errors="replace").stdout.strip()
    if not cikti:
        return []
    veri = json.loads(cikti)
    return veri if isinstance(veri, list) else [veri]


def _tarih(cim: str) -> datetime:
    # CIM: /Date(1759516800000)/  veya  20261003204625.123456+180
    if cim.startswith("/Date("):
        return datetime.fromtimestamp(int(cim[6:-2]) / 1000)
    return datetime.strptime(cim[:14], "%Y%m%d%H%M%S")


def zombi_mi(p: dict, en_az_dk: int, benim_pid: int) -> bool:
    cmd = (p.get("CommandLine") or "").lower()
    yas = datetime.now() - _tarih(str(p.get("CreationDate")))
    if p["ProcessId"] == benim_pid or yas < timedelta(minutes=en_az_dk):
        return False
    # Komut satirinda is yoksa (yalnizca kabuk ya da VS Code entegre terminal baslatici) zombidir.
    return ("-command" not in cmd and "-file" not in cmd and " /c " not in cmd) or "shellintegration" in cmd


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--kuru", action="store_true", help="yalnizca say, kapatma")
    ap.add_argument("--en-az-dk", type=int, default=2, help="bu kadar dakikadan genc olanlara dokunma")
    a = ap.parse_args()
    import os
    benim = os.getppid()
    hepsi = listele()
    toplam_mb = sum(int(p.get("WorkingSetSize") or 0) for p in hepsi) // (1024 * 1024)
    zombiler = [p for p in hepsi if zombi_mi(p, a.en_az_dk, benim)]
    print(f"kabuk sureci: {len(hepsi)}  bellek: {toplam_mb} MB  zombi adayi: {len(zombiler)}")
    if a.kuru:
        for p in zombiler[:10]:
            print(f"  pid={p['ProcessId']} {p['Name']} ebeveyn={p.get('ParentProcessId')} "
                  f"{(p.get('CommandLine') or '')[:90]}")
        return 0
    kapatilan = 0
    for p in zombiler:
        r = subprocess.run(["taskkill", "/PID", str(p["ProcessId"]), "/T", "/F"], capture_output=True)
        kapatilan += r.returncode == 0
    print(f"kapatilan: {kapatilan}/{len(zombiler)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
