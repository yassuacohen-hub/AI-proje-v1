# -*- coding: utf-8 -*-
"""Streamlit (8501) sunucusunu güvenli biçimde yeniden başlatır.

Neden gerekli: `.streamlit/config.toml` içinde `fileWatcherType = "none"` olduğu için
kod değişiklikleri otomatik yüklenmez; sunucu kapatılıp açılmalıdır. Bu script
portu dinleyen süreci bulur, öldürür, repo kökünden yeniden başlatır ve sağlık
ucunu doğrular. Ajanlar (roo/kilo/cline) bunu kullanır; Ürün Sahibi yalnız F5 çeker.

Kullanım:
    python scripts/streamlit_restart.py            # 8501'i yeniden başlat
    python scripts/streamlit_restart.py --port 8501 --durum   # sadece durum
    python scripts/streamlit_restart.py --durdur   # sadece kapat
"""
from __future__ import annotations

import argparse
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOG_DIR = ROOT / "logs"
VENV_PY = ROOT / ".venv" / "Scripts" / "python.exe"


def _dinleyen_pidler(port: int) -> list[int]:
    """netstat ile portu LISTENING durumunda tutan PID'leri döner."""
    try:
        cikti = subprocess.run(
            ["netstat", "-ano"], capture_output=True, text=True, check=False
        ).stdout
    except OSError:
        return []
    pidler: set[int] = set()
    for satir in cikti.splitlines():
        parcalar = satir.split()
        if len(parcalar) >= 5 and parcalar[0].upper() == "TCP" and "LISTENING" in satir:
            if parcalar[1].endswith(f":{port}"):
                try:
                    pidler.add(int(parcalar[-1]))
                except ValueError:
                    continue
    return sorted(pidler)


def _saglik(port: int, deneme: int = 20, bekleme: float = 0.75) -> bool:
    url = f"http://127.0.0.1:{port}/_stcore/health"
    for _ in range(deneme):
        try:
            with urllib.request.urlopen(url, timeout=2) as yanit:  # noqa: S310
                if yanit.read().decode("utf-8", "ignore").strip() == "ok":
                    return True
        except Exception:  # noqa: BLE001
            pass
        time.sleep(bekleme)
    return False


def durdur(port: int) -> list[int]:
    pidler = _dinleyen_pidler(port)
    for pid in pidler:
        subprocess.run(["taskkill", "/PID", str(pid), "/F"], capture_output=True, check=False)
    if pidler:
        time.sleep(1.5)
    return pidler


def baslat(port: int) -> int:
    LOG_DIR.mkdir(exist_ok=True)
    python = str(VENV_PY) if VENV_PY.exists() else sys.executable
    log = LOG_DIR / f"streamlit_{port}.log"
    komut = [
        python, "-m", "streamlit", "run", str(ROOT / "app.py"),
        f"--server.port={port}", "--server.address=127.0.0.1",
        "--server.headless=true", "--browser.gatherUsageStats=false",
    ]
    # DETACHED + yeni süreç grubu: bu script bitse de sunucu yaşar.
    flags = getattr(subprocess, "DETACHED_PROCESS", 0) | getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
    with open(log, "ab") as fh:
        proc = subprocess.Popen(  # noqa: S603
            komut, cwd=str(ROOT), stdout=fh, stderr=subprocess.STDOUT,
            stdin=subprocess.DEVNULL, creationflags=flags,
        )
    return proc.pid


def main() -> int:
    ap = argparse.ArgumentParser(description="Streamlit sunucusunu yeniden başlat")
    ap.add_argument("--port", type=int, default=8501)
    ap.add_argument("--durum", action="store_true", help="sadece durum göster")
    ap.add_argument("--durdur", action="store_true", help="sadece kapat")
    args = ap.parse_args()

    if args.durum:
        pidler = _dinleyen_pidler(args.port)
        print(f"PORT {args.port}: {'dinleyen PID ' + str(pidler) if pidler else 'kapalı'}")
        print("SAGLIK:", "ok" if _saglik(args.port, deneme=1) else "yanit yok")
        return 0

    eski = durdur(args.port)
    print(f"DURDURULDU: {eski if eski else 'çalışan süreç yoktu'}")
    if args.durdur:
        return 0

    pid = baslat(args.port)
    if _saglik(args.port):
        print(f"BASLADI: PID {pid} -> http://127.0.0.1:{args.port} (saglik ok)")
        print("Tarayıcıda F5 yeterli.")
        return 0
    print(f"HATA: sunucu {args.port} portunda saglik vermedi; log: logs/streamlit_{args.port}.log")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
