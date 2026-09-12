# -*- coding: utf-8 -*-
"""9R-04: ollama/tavily/firecrawl kayitlarinin data alanini JSON dosyasina yazar (guclu maskeli)."""
import json
import sqlite3
import sys
from pathlib import Path

DB = Path.home() / "AppData/Roaming/9router/db/data.sqlite"
OUT = Path(__file__).resolve().parent / "_9r04_ollama_data.json"


def _maskele(v) -> str:
    s = str(v)
    if len(s) <= 10:
        return "***"
    return f"{s[:6]}...{s[-4:]}"


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if not DB.exists():
        print("DB yok:", DB)
        return 1
    con = sqlite3.connect(str(DB))
    con.row_factory = sqlite3.Row
    rows = con.execute(
        "SELECT provider, authType, name, email, priority, isActive, data, updatedAt "
        "FROM providerConnections WHERE provider IN ('ollama','tavily','firecrawl') "
        "ORDER BY provider"
    ).fetchall()
    kayitlar = []
    for r in rows:
        data = r["data"]
        d = None
        if data:
            try:
                d = json.loads(data)
            except Exception:
                d = {"HAM": str(data)[:400]}
        # Gizli alanlari maskele
        if isinstance(d, dict):
            for k, v in list(d.items()):
                if any(t in k.lower() for t in ("key", "token", "secret", "pass", "auth", "apikey")):
                    d[k] = _maskele(v)
        kayitlar.append(
            {
                "provider": r["provider"],
                "authType": r["authType"],
                "name": r["name"],
                "email": r["email"],
                "priority": r["priority"],
                "isActive": r["isActive"],
                "updatedAt": r["updatedAt"],
                "data": d,
            }
        )
    OUT.write_text(json.dumps(kayitlar, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"OK:{len(kayitlar)} -> {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())