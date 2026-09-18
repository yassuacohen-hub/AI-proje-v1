# -*- coding: utf-8 -*-
"""ORCH-09: Nöbetçi periyodik çalıştırıcı.

Her 10 dakikada bir (varsayılan) geciken tetikleri kontrol eder,
uyarıları fırlatır ve opsiyonel Telegram bildirimi gönderir.

Kullanım:
    python scripts/nobetci_periodic.py              # sonsuz döngü (10 dk aralık)
    python scripts/nobetci_periodic.py --once        # tek seferlik kontrol
    python scripts/nobetci_periodic.py --interval 600
    python scripts/nobetci_periodic.py --interval 60 --once
"""
from __future__ import annotations

import argparse
import os
import sys
import time
import traceback
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(ROOT))

from src.company_master.orchestrator.nobetci import (
    nobet_tut,
    nobetci_ayar_oku,
)

DEFAULT_INTERVAL = 600  # 10 dakika = 600 saniye


def run_once() -> list[dict]:
    """Tek seferlik nöbetçi kontrolü yapar."""
    ayar = nobetci_ayar_oku()
    if ayar.get("devre_disi"):
        print(f"[{time.strftime('%H:%M:%S')}] Nöbetçi devre dışı, atlanıyor.")
        return []

    print(f"[{time.strftime('%H:%M:%S')}] Nöbetçi kontrolü başlıyor... (kademe: {ayar.get('kademe_sn', 600)} sn)")
    sonuc = nobet_tut()

    if sonuc:
        print(f"[{time.strftime('%H:%M:%S')}] {len(sonuc)} geciken tetik fırlatıldı:")
        for s in sonuc:
            print(f"  - {s['task_id']} ({s['ajan']}) → tetik #{s['tetik_sayisi']}")
    else:
        print(f"[{time.strftime('%H:%M:%S')}] Geciken tetik yok.")

    return sonuc


def run_forever(interval_seconds: int = DEFAULT_INTERVAL) -> None:
    """Sonsuz döngüde belirli aralıklarla çalıştırır."""
    print(f"Nöbetçi periyodik başlatıldı: her {interval_seconds} saniyede bir kontrol edilecek.")
    print("Durdurmak için Ctrl+C basın.")

    while True:
        try:
            run_once()
        except KeyboardInterrupt:
            print("\nKullanıcı tarafından durduruldu.")
            break
        except Exception as exc:
            print(f"[{time.strftime('%H:%M:%S')}] Hata: {exc}", file=sys.stderr)
            traceback.print_exc()

        print(f"[{time.strftime('%H:%M:%S')}] {interval_seconds} saniye bekleniyor...")
        time.sleep(interval_seconds)


def main() -> int:
    parser = argparse.ArgumentParser(description="Nöbetçi periyodik çalıştırıcı")
    parser.add_argument(
        "--interval",
        type=int,
        default=DEFAULT_INTERVAL,
        help=f"Kontrol aralığı saniye cinsinden (varsayılan: {DEFAULT_INTERVAL} = 10 dk)",
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Tek seferlik çalıştır ve çık",
    )
    parser.add_argument(
        "--config",
        action="store_true",
        help="Mevcut ayarları göster ve çık",
    )
    args = parser.parse_args()

    if args.config:
        ayar = nobetci_ayar_oku()
        import json
        print(json.dumps(ayar, ensure_ascii=False, indent=2))
        return 0

    if args.once:
        run_once()
        return 0

    run_forever(args.interval)
    return 0


if __name__ == "__main__":
    import traceback
    import time
    sys.exit(main())
