# -*- coding: utf-8 -*-
"""9R-04: Dashboard'dan firecrawl/tavily eklenmesini izler.

DB'yi periyodik yoklar; providerConnections'ta firecrawl/tavily kaydı
gördüğü anda kaydı, apiKey durumunu ve canlılık kanıtını raporlar.
"""
from __future__ import annotations

import json
import sqlite3
import sys
import time
from datetime import datetime, timezone

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

DB = r"C:\Users\yasin\AppData\Roaming\9router\db\data.sqlite"
HEDEF = ("firecrawl", "tavily")
DENEME = 60          # max ~5dk
BEKLEME_SN = 5


def _utc(z: str) -> str:
    try:
        t = datetime.fromisoformat(z.replace("Z", "+00:00"))
        return t.astimezone().strftime("%H:%M:%S")
    except Exception:  # noqa: BLE001
        return z


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
        kosul = " OR ".join(
            f"(provider LIKE '%{a}%' OR name LIKE '%{a}%' OR data LIKE '%{a}%')" for a in HEDEF
        )
        return con.execute(
            f"SELECT id, provider, name, isActive, data, updatedAt FROM providerConnections WHERE {kosul}"
        ).fetchall()
    finally:
        con.close()


def main() -> int:
    print(f"[{datetime.now().strftime('%H:%M:%S')}] DB izleme başladı: {DB}")
    print(f"[{datetime.now().strftime('%H:%M:%S')}] firecrawl/tavily kaydı bekleniyor (her {BEKLEME_SN}sn)...")
    for i in range(1, DENEME + 1):
        rows = _tarat()
        gercek = [
            r for r in rows
            if r[1].lower() in ("firecrawl", "tavily")
            or any(r[1].lower().startswith(a) for a in HEDEF)
        ]
        if gercek:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] KAYIT GÖRÜLDÜ (deneme #{i})")
            for r in gercek:
                print(f"   id={r[0][:8]} provider={r[1]} isActive={r[3]} upd={_utc(r[5])} {_api_key_ozet(r[4])}")
            print("=> Canlı doğrulama için _9r04_dogrula.py çalıştırılabilir.")
            return 0
        if i % 6 == 0:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] henüz yok... ({i * BEKLEME_SN}sn geçti)")
            sys.stdout.flush()
        time.sleep(BEKLEME_SN)
    print(f"[{datetime.now().strftime('%H:%M:%S')}] ZAMAN AŞIMI: {DENEME * BEKLEME_SN}sn içinde kayıt görülmedi.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())