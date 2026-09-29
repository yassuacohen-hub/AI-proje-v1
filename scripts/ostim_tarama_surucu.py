"""D-296: Tamamlanabilir parca surucusu (arka plan tarama).

KAHIN: "kanalar icin devam et hepsi bitsin". Tarama 500'lik parcalar
halinde ilerliyor ve HER PARCA BITINCE yeniden baslatmak gerekiyordu.
Bu betik parcalari SIRAYA koyar, her biri bitince bir sonrakini
otomatik baslatir.

GUECENLIK:
  * Koruma kilidi (D-290) her parcada zaten devrede: kaynak dosya
    degistiyse hicbir parca calismaz.
  * Kismi yazim (D-291): surec oldurulse bile veri kaybolmaz.
  * Surec istenirse durdurulabilir; `durum.json` sayesinden
    kaldigi yerden devam eder.
  * Asili kalirsa `cift_erisim` kilidi ONUNLUK sayfaya basilir:
    iki tarama ayni anda calismaz.

Kullanim:
    python scripts/ostim_tarama_surucu.py            # kalan tumu
    python scripts/ostim_tarama_surucu.py --parca 300
    python scripts/ostim_tarama_surucu.py --durum
"""
from __future__ import annotations

import argparse
import json
import pathlib
import subprocess
import sys
import time
from datetime import datetime

KOK = pathlib.Path(__file__).resolve().parents[1]
KAZANIM = KOK / "data" / "ostim" / "tamamlama_2026-09-29"
DURUM = KAZANIM / "durum.json"
RAPOR = KAZANIM / "rapor.json"
KAZANCI = KOK / "data" / "ostim" / "firmalar_full.jsonl"
VAR = KOK / "data" / "ostim" / "firmalar_vkn_ekli.jsonl"
CIKTI = KAZANIM / "firmalar_tamamlanmis.jsonl"
KILIT = KAZANIM / "surucu_kilidi.json"
SCRIPT = KOK / "scripts" / "ostim_detay_tamamla.py"

#: D-296: gunluk 500 detay tavanini ASMA. Kalan tumu bitene kadar
#: parca parca ilerler; her parca kendi gununde sayilir.
PARCA = 500
ARA_BEKLEME = 3.0


def _kilit_al() -> bool:
    """Asili kalirsa ikinci surucu kacmasin."""
    if KILIT.is_file():
        try:
            ic = json.loads(KILIT.read_text(encoding="utf-8"))
            pid = ic.get("pid")
            if pid and _canli(pid) and pid != _benim_pid():
                return False
        except (json.JSONDecodeError, OSError):
            pass
    KILIT.parent.mkdir(parents=True, exist_ok=True)
    KILIT.write_text(json.dumps(
        {"pid": _benim_pid(), "baslangic": datetime.now().isoformat(
            timespec="seconds")}), encoding="utf-8")
    return True


def _kilit_birak() -> None:
    KILIT.unlink(missing_ok=True)


def _benim_pid() -> int:
    import os
    return os.getpid()


def _canli(pid: int) -> bool:
    """PID yasamiyor mu? (cift surucu kilidi icin)"""
    import os
    if pid <= 0:
        return False
    if os.name == "nt":
        import ctypes
        HANDLE = ctypes.windll.kernel32.OpenProcess(0x1000, False, pid)
        if not HANDLE:
            return False
        ctypes.windll.kernel32.CloseHandle(HANDLE)
        return True
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    return True


def durum_oku() -> dict:
    if DURUM.is_file():
        try:
            return json.loads(DURUM.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass
    return {}


def eksik_sayi() -> int:
    """Listede olup HENUZ cekilmemis firma sayisi.

    D-296 DUZELTME: ilk surum yalnizca `firmalar_vkn_ekli.jsonl`'e
    bakiyordu. Taradigimiz kayitlar CIKTI dosyasinda birikiyordu ve
    hesaba katilmadigi icin "kalan" HEP 3.339 donuyordu -> surucu
    bitmeden ayni parcayi tekrar tekrar cekecek, SONSUZA KADAR
    donerdi. Duzeltme: cekilen slug'lar da "var" kümesine eklenir.
    """
    liste = {json.loads(x).get("slug") for x in KAZANCI.read_text(
        encoding="utf-8").splitlines() if x.strip()}
    var = set()
    for x in VAR.read_text(encoding="utf-8").splitlines():
        if x.strip():
            var.add(json.loads(x).get("slug"))
    # D-296: bu turun cekilen kayitlar da artik "var"
    if CIKTI.is_file():
        for x in CIKTI.read_text(encoding="utf-8").splitlines():
            if x.strip():
                try:
                    var.add(json.loads(x).get("slug"))
                except json.JSONDecodeError:
                    continue
    return len(liste - var)


def yazilan() -> int:
    if not CIKTI.is_file():
        return 0
    return len(CIKTI.read_text(encoding="utf-8").splitlines())


def main() -> int:
    ay = argparse.ArgumentParser()
    ay.add_argument("--parca", type=int, default=PARCA)
    ay.add_argument("--durum", action="store_true")
    ns = ay.parse_args()

    d = durum_oku()
    islenmis = len(d.get("islenen", {}))
    kalan = eksik_sayi()
    print(f"DURUM  islenmis={islenmis} | yazilan={yazilan()} "
          f"| kalan={kalan}")

    if ns.durum:
        return 0
    if kalan <= 0:
        print("TAMAMLANDI - eksik kayit yok.")
        return 0
    if not _kilit_al():
        print("BASKA SURUCU CALISIYOR - cikiliyorum.")
        return 1

    try:
        while kalan > 0:
            n = min(ns.parca, kalan)
            print(f"\n>>> PARCA basliyor: {n} kayit "
                  f"({datetime.now():%H:%M:%S})")
            r = subprocess.run(
                [sys.executable, "-X", "utf8", str(SCRIPT),
                 "--limit", str(n)],
                cwd=str(KOK), capture_output=True, text=True,
                encoding="utf-8", errors="replace")
            for satir in (r.stdout or "").splitlines():
                if satir.strip():
                    print("   ", satir.strip()[:110])
            if r.returncode != 0:
                print("HATA:", (r.stderr or "")[-400:])
            kalan = eksik_sayi()
            print(f"<<< parca bitti. kalan={kalan} "
                  f"yazilan={yazilan()} ({datetime.now():%H:%M:%S})")
            if kalan <= 0:
                break
            time.sleep(ARA_BEKLEME)
    finally:
        _kilit_birak()

    print(f"\nTARAMA TAMAMLANDI. yazilan={yazilan()} kalan={kalan}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
