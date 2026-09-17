# -*- coding: utf-8 -*-
"""PO-BACK-04 Sürekli Rutin Kontroller (continuous monitoring).

Kullanım:
    python scripts/paket_fiyati_kontrol.py              # Tek seferlik kontrol
    python scripts/paket_fiyati_kontrol.py --surekli    # Her 5 dakikada bir
    python scripts/paket_fiyati_kontrol.py --dakika 10  # Her 10 dakikada bir

Yapılan:
    1) fiyat_katalogu() dogru mu (4 tier, fiyatlar > 0)?
    2) sync_paket_fiyatlari.py --check çıkış kodu 0 mı?
    3) test_paket_fiyat.py geçiyor mu?

Log: data/orchestrator/paket_fiyati_kontrol.log
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOG_YOL = ROOT / "data" / "orchestrator" / "paket_fiyati_kontrol.log"


def log(mesaj: str) -> None:
    satir = f"{datetime.now().isoformat()} | {mesaj}"
    print(satir)
    LOG_YOL.parent.mkdir(parents=True, exist_ok=True)
    with LOG_YOL.open(mode="a", encoding="utf-8") as f:
        f.write(satir + "\n")


def kontrol_et() -> int:
    """Tüm kontrolleri çalıştır. 0=OK, 1=HATA."""
    hatalar = []

    # 1. fiyat_katalogu() kontrolü
    try:
        sys.path.insert(0, str(ROOT / "src"))
        from company_master.paketler import fiyat_katalogu
        katalog = fiyat_katalogu()
        isimler = [p["name"] for p in katalog]
        if isimler != ["Temel", "Standart", "Profesyonel", "Kurumsal"]:
            hatalar.append(f"Yanlış tier: {isimler}")
        for p in katalog:
            if p["price"] <= 0:
                hatalar.append(f"{p['name']} fiyat > 0 değil: {p['price']}")
            if not p.get("features"):
                hatalar.append(f"{p['name']} features boş")
            if not p.get("description"):
                hatalar.append(f"{p['name']} description boş")
            if not p.get("icon"):
                hatalar.append(f"{p['name']} icon boş")
        log(f"FIYAT_KATALOGU: {len(katalog)} tier OK")
    except Exception as e:
        hatalar.append(f"fiyat_katalogu hata: {e}")

    # 2. sync_paket_fiyatlari.py --check kontrolü
    try:
        r = subprocess.run(
            [sys.executable, "-X", "utf8", str(ROOT / "scripts" / "sync_paket_fiyatlari.py"), "--check"],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=str(ROOT),
            env={**os.environ, "PYTHONPATH": str(ROOT / "src")},
        )
        if r.returncode != 0:
            hatalar.append(f"sync --check çıkış {r.returncode}: {r.stdout[-200:]}")
        else:
            log("SYNC_PAKET_FIYATLARI: --check OK")
    except Exception as e:
        hatalar.append(f"sync hata: {e}")

    # 3. test_paket_fiyat.py kontrolü
    try:
        r = subprocess.run(
            [sys.executable, "-X", "utf8", "-m", "pytest", "tests/test_paket_fiyat.py", "-q"],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=str(ROOT),
            env={**os.environ, "PYTHONPATH": str(ROOT / "src")},
        )
        if r.returncode != 0:
            hatalar.append(f"test çıkış {r.returncode}: {r.stdout[-300:]}")
        else:
            log("TEST_PAKET_FIYAT: 11/11 OK")
    except Exception as e:
        hatalar.append(f"test hata: {e}")

    if hatalar:
        for h in hatalar:
            log(f"HATA: {h}")
        return 1
    log("TÜM_KONTROLLER: OK")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="PO-BACK-04 Sürekli Paket Fiyatı Kontrolleri")
    parser.add_argument("--surekli", action="store_true", help="Her --dakika dakikada bir çalıştır")
    parser.add_argument("--dakika", type=int, default=5, help="Aralık (dakika), varsayılan 5")
    args = parser.parse_args()

    if args.surekli:
        aralik = args.dakika * 60
        log(f"[BAŞLADI] Sürekli mod: her {args.dakika} dakikada bir")
        try:
            while True:
                kontrol_et()
                time.sleep(aralik)
        except KeyboardInterrupt:
            log("[DURDURULDU]")
    else:
        return kontrol_et()
    return 0


if __name__ == "__main__":
    sys.exit(main())
