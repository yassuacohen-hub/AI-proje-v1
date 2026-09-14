# -*- coding: utf-8 -*-
"""Huginn servis nöbetçilerini tek komutla yönetir (penceresiz).

Kullanım:
    python scripts/servisleri_baslat.py baslat          # web + admin nöbetçisi
    python scripts/servisleri_baslat.py baslat --servis admin
    python scripts/servisleri_baslat.py durum
    python scripts/servisleri_baslat.py durdur

Tasarım notu:
    Nöbetçiler ``pythonw.exe`` ile başlatılır ve ``CREATE_NO_WINDOW`` bayrağı
    kullanılır; bu sayede ekranda konsol penceresi açılıp kapanmaz.
    Her servisin kendi PID kilidi olduğu için ikinci kopya sessizce reddedilir.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOG_DIR = ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)

WATCHDOG = ROOT / "scripts" / "server_watchdog.py"
VENV_PYTHONW = ROOT / ".venv" / "Scripts" / "pythonw.exe"
VENV_PYTHON = ROOT / ".venv" / "Scripts" / "python.exe"

SERVISLER: tuple[str, ...] = ("web", "admin")


def _pythonw() -> str:
    """Penceresiz yorumlayıcı; yoksa normal python'a düşer."""
    if VENV_PYTHONW.exists():
        return str(VENV_PYTHONW)
    if VENV_PYTHON.exists():
        return str(VENV_PYTHON)
    return sys.executable


def _python() -> str:
    return str(VENV_PYTHON) if VENV_PYTHON.exists() else sys.executable


def _pid_dosyasi(servis: str) -> Path:
    ek = "" if servis == "web" else f"_{servis}"
    return LOG_DIR / f"server_watchdog{ek}.pid"


def _bayraklar() -> int:
    if sys.platform != "win32":
        return 0
    return getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)


def baslat(servisler: list[str]) -> int:
    for servis in servisler:
        subprocess.Popen(
            [_pythonw(), str(WATCHDOG), "--servis", servis],
            cwd=str(ROOT),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL,
            creationflags=_bayraklar(),
        )
        print(f"[{servis}] nobetci baslatildi (penceresiz).")
    print("Not: Ayni servis icin ikinci kopya PID kilidiyle otomatik reddedilir.")
    return 0


def durum(servisler: list[str]) -> int:
    for servis in servisler:
        print(f"--- {servis} ---")
        subprocess.run(
            [_python(), str(WATCHDOG), "--servis", servis, "--status"],
            cwd=str(ROOT),
            check=False,
        )
    return 0


def durdur(servisler: list[str]) -> int:
    for servis in servisler:
        pid_yolu = _pid_dosyasi(servis)
        if not pid_yolu.exists():
            print(f"[{servis}] calisan nobetci yok.")
            continue
        try:
            pid = int(pid_yolu.read_text(encoding="utf-8").strip() or "0")
        except (ValueError, OSError):
            pid = 0
        if pid:
            subprocess.run(
                ["taskkill", "/PID", str(pid), "/F"] if sys.platform == "win32" else ["kill", "-9", str(pid)],
                check=False,
                capture_output=True,
            )
            print(f"[{servis}] nobetci durduruldu (PID {pid}).")
        pid_yolu.unlink(missing_ok=True)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Huginn servis nobetcisi yoneticisi")
    parser.add_argument("komut", choices=["baslat", "durum", "durdur"])
    parser.add_argument(
        "--servis",
        choices=[*SERVISLER, "hepsi"],
        default="hepsi",
        help="web (8000) | admin (8501) | hepsi",
    )
    args = parser.parse_args()

    secili = list(SERVISLER) if args.servis == "hepsi" else [args.servis]

    if args.komut == "baslat":
        return baslat(secili)
    if args.komut == "durum":
        return durum(secili)
    return durdur(secili)


if __name__ == "__main__":
    raise SystemExit(main())
