#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Servis nöbetçisi — Huginn sunucularını izler, çöküşleri loglar ve yeniden başlatır.

Servisler:
  * ``web``   → FastAPI ``web_app.py``            (http://127.0.0.1:8000)
  * ``admin`` → Streamlit ``app.py`` (Süper Admin) (http://127.0.0.1:8501)

Sertleştirme (2026-09-14):
  * Servis başına tekil süreç kilidi (PID dosyası) — ikinci kopya başlayamaz.
  * Penceresiz başlatma (CREATE_NO_WINDOW) — ekranda konsol açılmaz.
  * Üstel backoff + ardışık başarısızlık üst sınırı — sonsuz restart döngüsü kırılır.
  * Durum değişimi loglama + log rotasyonu — jsonl/stderr şişmesi engellenir.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import URLError

ROOT = Path(__file__).resolve().parent.parent
LOG_DIR = ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)

DEFAULT_INTERVAL = int(os.getenv("WATCHDOG_INTERVAL", "30"))
DEFAULT_PYTHON = os.getenv("WATCHDOG_PYTHON", str(ROOT / ".venv" / "Scripts" / "python.exe"))

#: Servis kataloğu — her servisin sağlık adresi ve başlatma argümanları.
SERVISLER: dict[str, dict[str, object]] = {
    "web": {
        "baslik": "FastAPI web_app (musteri paneli + API)",
        "url": "http://127.0.0.1:8000/api/health",
        "argumanlar": [str(ROOT / "web_app.py")],
    },
    "admin": {
        "baslik": "Streamlit Super Admin paneli",
        "url": "http://127.0.0.1:8501/_stcore/health",
        "argumanlar": [
            "-m",
            "streamlit",
            "run",
            str(ROOT / "app.py"),
            "--server.port=8501",
            "--server.address=127.0.0.1",
            "--server.headless=true",
            "--browser.gatherUsageStats=false",
        ],
    },
}

# Geriye dönük uyumluluk: eski çağrılar servis adı vermeden çalışsın.
DEFAULT_SERVIS = os.getenv("WATCHDOG_SERVIS", "web")
DEFAULT_URL = os.getenv("WATCHDOG_URL", "")
DEFAULT_SCRIPT = os.getenv("WATCHDOG_SCRIPT", "")


def _log_yollari(servis: str) -> tuple[Path, Path, Path, Path]:
    """Servise özel (jsonl, stdout, stderr, pid) yollarını üretir."""
    ek = "" if servis == "web" else f"_{servis}"
    return (
        LOG_DIR / f"server_watchdog{ek}.jsonl",
        LOG_DIR / f"server_watchdog{ek}.stdout.log",
        LOG_DIR / f"server_watchdog{ek}.stderr.log",
        LOG_DIR / f"server_watchdog{ek}.pid",
    )


LOG_FILE, STDOUT_LOG, STDERR_LOG, PID_FILE = _log_yollari(DEFAULT_SERVIS)


def yollari_ayarla(servis: str) -> None:
    """Modül seviyesindeki log/pid yollarını seçilen servise bağlar."""
    global LOG_FILE, STDOUT_LOG, STDERR_LOG, PID_FILE
    LOG_FILE, STDOUT_LOG, STDERR_LOG, PID_FILE = _log_yollari(servis)

# Sonsuz döngü koruması
MAX_ARDISIK_HATA = int(os.getenv("WATCHDOG_MAX_RETRY", "5"))
BACKOFF_TABANI = int(os.getenv("WATCHDOG_BACKOFF", "2"))
BACKOFF_TAVAN = int(os.getenv("WATCHDOG_BACKOFF_MAX", "900"))  # 15 dk

# Log rotasyonu
LOG_MAX_BYTE = int(os.getenv("WATCHDOG_LOG_MAX", str(2 * 1024 * 1024)))  # 2 MB


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# --------------------------------------------------------------------------- #
# Log
# --------------------------------------------------------------------------- #
def _rotate(path: Path, limit: int = LOG_MAX_BYTE) -> None:
    """Dosya limiti aşarsa `.1` uzantısıyla devret; eski yedeği ezer."""
    try:
        if path.exists() and path.stat().st_size > limit:
            yedek = path.with_suffix(path.suffix + ".1")
            if yedek.exists():
                yedek.unlink()
            path.rename(yedek)
    except OSError:
        pass


def log_event(event: dict) -> None:
    event["ts"] = now_iso()
    _rotate(LOG_FILE)
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")


# --------------------------------------------------------------------------- #
# Tekil süreç kilidi
# --------------------------------------------------------------------------- #
def _pid_canli(pid: int) -> bool:
    """PID gerçekten çalışıyor mu? (Windows: OpenProcess, POSIX: signal 0)"""
    if pid <= 0:
        return False
    if sys.platform == "win32":
        import ctypes

        PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
        kernel32 = ctypes.windll.kernel32
        handle = kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
        if not handle:
            return False
        kod = ctypes.c_ulong()
        kernel32.GetExitCodeProcess(handle, ctypes.byref(kod))
        kernel32.CloseHandle(handle)
        return kod.value == 259  # STILL_ACTIVE
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    return True


def kilit_al() -> bool:
    """Başka bir watchdog çalışıyorsa False döner (bu kopya başlamaz)."""
    if PID_FILE.exists():
        try:
            eski = int(PID_FILE.read_text(encoding="utf-8").strip() or "0")
        except (ValueError, OSError):
            eski = 0
        if eski and eski != os.getpid() and _pid_canli(eski):
            return False
    try:
        PID_FILE.write_text(str(os.getpid()), encoding="utf-8")
    except OSError:
        return False
    return True


def kilit_birak() -> None:
    try:
        if PID_FILE.exists():
            mevcut = PID_FILE.read_text(encoding="utf-8").strip()
            if mevcut == str(os.getpid()):
                PID_FILE.unlink()
    except OSError:
        pass


# --------------------------------------------------------------------------- #
# Sağlık ve süreç
# --------------------------------------------------------------------------- #
def check_health(url: str, timeout: int = 10) -> tuple[bool, str]:
    req = Request(url, method="GET", headers={"User-Agent": "huginn-watchdog/1.0"})
    try:
        with urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8", errors="ignore")
            return resp.status == 200, body[:200]
    except URLError as e:
        return False, str(e.reason)
    except Exception as e:
        return False, str(e)


def _pencere_bayraklari() -> int:
    """Windows'ta konsol penceresi açılmasın; diğer platformlarda etkisiz."""
    if sys.platform != "win32":
        return 0
    return getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000) | subprocess.CREATE_NEW_PROCESS_GROUP


def start_server(python: str, argumanlar: list[str]) -> subprocess.Popen:
    """Servisi penceresiz başlatır. ``argumanlar`` python yorumlayıcısından sonraki parçalardır."""
    log_event({"type": "restart_attempt", "python": python, "argumanlar": argumanlar})
    _rotate(STDOUT_LOG)
    _rotate(STDERR_LOG)
    out = STDOUT_LOG.open("a", encoding="utf-8")
    err = STDERR_LOG.open("a", encoding="utf-8")
    proc = subprocess.Popen(
        [python, *argumanlar],
        cwd=str(ROOT),
        stdout=out,
        stderr=err,
        stdin=subprocess.DEVNULL,
        creationflags=_pencere_bayraklari(),
    )
    log_event({"type": "process_started", "pid": proc.pid})
    return proc


def backoff_suresi(ardisik_hata: int) -> int:
    """Üstel backoff: 2, 4, 8, 16 ... tavanla sınırlı."""
    return min(BACKOFF_TABANI ** max(ardisik_hata, 1), BACKOFF_TAVAN)


def tail_summary(limit: int = 20) -> list[dict]:
    if not LOG_FILE.exists():
        return []
    lines = LOG_FILE.read_text(encoding="utf-8").splitlines()
    return [json.loads(line) for line in lines[-limit:] if line.strip()]


# --------------------------------------------------------------------------- #
# Ana döngü
# --------------------------------------------------------------------------- #
def main() -> None:
    parser = argparse.ArgumentParser(description="Huginn servis nobetcisi")
    parser.add_argument(
        "--servis",
        choices=sorted(SERVISLER),
        default=DEFAULT_SERVIS,
        help="Izlenecek servis: web (8000) veya admin (8501)",
    )
    parser.add_argument("--url", default="", help="Saglik adresi (bos ise servis varsayilani)")
    parser.add_argument("--interval", type=int, default=DEFAULT_INTERVAL)
    parser.add_argument("--python", default=DEFAULT_PYTHON)
    parser.add_argument("--script", default="", help="Geriye donuk: tek dosyalik giris betigi")
    parser.add_argument("--no-restart", action="store_true", help="Sadece izle, yeniden başlatma")
    parser.add_argument("--status", action="store_true", help="Son log kayıtlarını göster ve çık")
    parser.add_argument(
        "--max-retry",
        type=int,
        default=MAX_ARDISIK_HATA,
        help="Ardışık başarısız restart üst sınırı (0 = sınırsız)",
    )
    args = parser.parse_args()

    yollari_ayarla(args.servis)
    tanim = SERVISLER[args.servis]
    url = args.url or DEFAULT_URL or str(tanim["url"])
    script = args.script or DEFAULT_SCRIPT
    argumanlar: list[str] = [script] if script else list(tanim["argumanlar"])  # type: ignore[arg-type]

    if args.status:
        print(f"Servis     : {args.servis} — {tanim['baslik']}")
        print(f"Saglik URL : {url}")
        print(f"Log dosyasi: {LOG_FILE}")
        print(f"PID dosyasi: {PID_FILE} (var: {PID_FILE.exists()})")
        for ev in tail_summary():
            print(ev)
        return

    if not kilit_al():
        mevcut = PID_FILE.read_text(encoding="utf-8").strip()
        print(f"[{args.servis}] Baska bir nobetci zaten calisiyor (PID {mevcut}). Bu kopya kapaniyor.")
        log_event({"type": "duplicate_blocked", "existing_pid": mevcut, "pid": os.getpid()})
        return

    log_event({
        "type": "watchdog_started",
        "servis": args.servis,
        "pid": os.getpid(),
        "url": url,
        "interval": args.interval,
        "restart": not args.no_restart,
        "max_retry": args.max_retry,
    })

    proc: subprocess.Popen | None = None
    down_since: str | None = None
    ardisik_hata = 0
    son_durum: str | None = None  # "healthy" | "down" — sadece değişimde logla
    duraklatildi = False

    try:
        while True:
            ok, detail = check_health(url)

            if ok:
                if down_since:
                    log_event({"type": "recovered", "down_since": down_since, "detail": detail})
                    down_since = None
                if son_durum != "healthy":
                    log_event({"type": "healthy", "detail": detail})
                    son_durum = "healthy"
                ardisik_hata = 0
                duraklatildi = False
                time.sleep(args.interval)
                continue

            # --- sağlıksız ---
            if not down_since:
                down_since = now_iso()
                log_event({"type": "down_detected", "detail": detail})
            son_durum = "down"

            if args.no_restart or duraklatildi:
                time.sleep(args.interval)
                continue

            if proc is not None and proc.poll() is None:
                log_event({"type": "unhealthy_process_alive", "pid": proc.pid, "detail": detail})
                time.sleep(args.interval)
                continue

            ardisik_hata += 1
            if args.max_retry and ardisik_hata > args.max_retry:
                duraklatildi = True
                log_event({
                    "type": "restart_paused",
                    "ardisik_hata": ardisik_hata,
                    "sebep": "max_retry_asildi",
                    "ipucu": f"Kok nedeni {STDERR_LOG.name} icinde arayin; duzeltince watchdog'u yeniden baslatin.",
                })
                time.sleep(args.interval)
                continue

            proc = start_server(args.python, argumanlar)
            bekle = backoff_suresi(ardisik_hata)
            log_event({"type": "backoff", "saniye": bekle, "ardisik_hata": ardisik_hata})
            time.sleep(max(bekle, args.interval))
    finally:
        kilit_birak()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log_event({"type": "watchdog_stopped", "reason": "keyboard_interrupt"})
        kilit_birak()
        sys.exit(0)
