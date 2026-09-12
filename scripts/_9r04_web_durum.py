# -*- coding: utf-8 -*-
"""9R-04: Web provider kayıtlarının son durumu (tavily/firecrawl) — hızlı özet."""
from __future__ import annotations

import json
import sqlite3
import sys
from datetime import datetime, timezone

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

DB = r"C:\Users\yasin\AppData\Roaming\9router\db\data.sqlite"


def _utc(z: str) -> str:
    try:
        return datetime.fromisoformat(z.replace("Z", "+00:00")).astimezone().strftime("%H:%M:%S")
    except Exception:  # noqa: BLE001
        return z


def main() -> int:
    con = sqlite3.connect(DB)
    def q(provider: str):
        rows = con.execute(
            "SELECT id, provider, name, authType, isActive, data, updatedAt FROM providerConnections WHERE provider LIKE ?",
            (f"%{provider}%",),
        ).fetchall()
        for r in rows:
            ak = ""
            try:
                d = json.loads(r[5])
                ak = d.get("apiKey") or d.get("api_key") or ""
            except Exception:  # noqa: BLE001
                pass
            print(f"  {r[1]:12s} isActive={r[4]} auth={r[3]} apiKey={'DOLU(' + str(len(ak)) + ')' if ak else 'YOK'} upd={_utc(r[6])}")
        return len(rows)

    for p in ("firecrawl", "tavily"):
        n = q(p)
        if n == 0:
            print(f"  {p}: HENÜZ KAYIT YOK")

    # model görünürlüğü: /v1/models/web için provider listesi
    print()
    print("providerConnections toplam:", con.execute("SELECT COUNT(*) FROM providerConnections").fetchone()[0])
    con.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())