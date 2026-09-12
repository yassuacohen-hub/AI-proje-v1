# -*- coding: utf-8 -*-
"""9R-04: Sadece firecrawl kaydının DB'ye düşmesini izler."""
from __future__ import annotations

import json
import sqlite3
import sys
import time
from datetime import datetime

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

DB = r"C:\Users\yasin\AppData\Roaming\9router\db\data.sqlite"
HEDEF = "firecrawl"
DENEME = 60
BEKLEME_SN = 5


def _api_key_ozet(data: str | None) -> str:
    if not data:
        return "VERİ YOK"
    try:
        o = json.loads(data)
        ak = o.get("apiKey") or o.get("api_key") or ""
        if ak:
            return f"apiKey dolu ({len(ak)} karakter: {ak[:4]}...{ak[-4:]})"
        return "apiKey YOK (data JSON var)"
    except Exception:  # noqa: BLE001
        return f"JSON değil ({len(data)} char)"


def _tarat() -> list[tuple]:
    con = sqlite3.connect(DB)
    try:
        return con.execute(
            "SELECT id, provider, name, isActive, data, updatedAt FROM providerConnections WHERE provider LIKE ?",
            ("%firecrawl%",),
        ).fetchall()
    finally:
        con.close()


def main() -> int:
    print(f"[{datetime.now().strftime('%H:%M:%S')}] firecrawl izleniyor (her {BEKLEME_SN}sn, max {DENEME * BEKLEME_SN}sn)...")
    for i in range(1, DENEME + 1):
        rows = _tarat()
        if rows:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] FIRECRAWL KAYIT GÖRÜLDÜ (deneme #{i})")
            for r in rows:
                print(f"   id={r[0][:8]} provider={r[1]} isActive={r[3]} upd={r[5]} {_api_key_ozet(r[4])}")
            return 0
        if i % 6 == 0:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] henüz yok... ({i * BEKLEME_SN}sn)")
            sys.stdout.flush()
        time.sleep(BEKLEME_SN)
    print(f"[{datetime.now().strftime('%H:%M:%S')}] ZAMAN AŞIMI: firecrawl kaydı görülmedi.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())