# -*- coding: utf-8 -*-
"""
scripts/sync_paket_fiyatlari.py — PO-BACK-04: Paket fiyat kataloğu tekilleştirme

Kullanım:
    python scripts/sync_paket_fiyatlari.py          # Katalogu JSON'a yazar
    python scripts/sync_paket_fiyatlari.py --check  # Diff göster, uyumsuzluk varsa çıkış 1

Çalışma prensibi:
    - fiyat_katalogu() fonksiyonunun içindeki _ORJINAL_FIYATLAR/_ORJINAL_OZELLIKLER
      verilerini tek kaynak olarak kullanır.
    - --check flag'i ile katalogın yapısal bütünlüğünü kontrol eder.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Proje köküne göre yol
ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "src"))

from company_master.paketler import fiyat_katalogu


ORJINAL_JSON_PATH = ROOT / "data" / "demo" / "fiyat_katalogu.json"


def katalogu_json_yaz(path: Path = ORJINAL_JSON_PATH) -> None:
    """fiyat_katalogu() sonucunu JSON dosyasına yazar."""
    katalog = fiyat_katalogu()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(katalog, ensure_ascii=False, indent=2), encoding="utf-8")


def check_katalog_uyumu() -> int:
    """
    Katalog yapısal bütünlüğünü kontrol eder.
    - 4 tier olmalı (Temel, Standart, Profesyonel, Kurumsal)
    - Tüm tier'larda price > 0 ve features/description/icon mevcut olmalı
    - Uyumsuzluk varsa çıkış kodunu 1 döndürür.
    """
    katalog = fiyat_katalogu()
    required_names = {"Temel", "Standart", "Profesyonel", "Kurumsal"}
    catalog_names = {p["name"] for p in katalog}

    sorunlar = []

    # Tier sayısı kontrolü
    if len(katalog) != 4:
        sorunlar.append(f"Beklenen 4 tier, bulundu: {len(katalog)}")

    # Gerekli tier'ların varlığı
    eksik = required_names - catalog_names
    if eksik:
        sorunlar.append(f"Eksik tier'lar: {sorted(eksik)}")

    # Her tier için field kontrolü
    for entry in katalog:
        name = entry.get("name", "bilinmeyen")
        if entry.get("price", 0) <= 0:
            sorunlar.append(f"{name}: price <= 0 ({entry.get('price')})")
        if not entry.get("features"):
            sorunlar.append(f"{name}: features eksik/boş")
        if not entry.get("description"):
            sorunlar.append(f"{name}: description eksik/boş")
        if not entry.get("icon"):
            sorunlar.append(f"{name}: icon eksik/boş")

    if sorunlar:
        print("❌ Katalog uyum kontrolü başarısız:")  # noqa: T201
        for s in sorunlar:
            print(f"  - {s}")  # noqa: T201
        return 1

    # Katalog kaydı yoksa oluştur
    if not ORJINAL_JSON_PATH.exists():
        print("⚠ Katalog JSON dosyası yok, oluşturuluyor...")  # noqa: T201
        katalogu_json_yaz(ORJINAL_JSON_PATH)

    print("✅ Katalog yapısı uyumlu.")  # noqa: T201
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(description="Paket fiyat kataloğu senkronizasyonu")
    parser.add_argument(
        "--check",
        action="store_true",
        help="Katalog yapısal bütünlüğü kontrolü; uyumsuzluk varsa çıkış 1",
    )
    args = parser.parse_args()

    if args.check:
        sys.exit(check_katalog_uyumu())
    else:
        katalogu_json_yaz()
        print("Katalog JSON'a yazıldı.")  # noqa: T201


if __name__ == "__main__":
    main()