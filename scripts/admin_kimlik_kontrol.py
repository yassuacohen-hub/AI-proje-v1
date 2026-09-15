# -*- coding: utf-8 -*-
"""Admin giriş kimliğinin nerede tanımlı olduğunu raporlar.

Güvenlik: şifre veya hash ASLA yazdırılmaz; yalnızca "var/yok" bilgisi verilir.
Kullanım: python scripts/admin_kimlik_kontrol.py
"""
from __future__ import annotations

import pathlib
import sys
import tomllib

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


def main() -> int:
    p = ROOT / ".streamlit" / "secrets.toml"
    d = tomllib.load(p.open("rb")) if p.exists() else {}
    print("secrets.toml:", "VAR" if p.exists() else "YOK",
          "| admin_password anahtari:", "VAR" if d.get("admin_password") else "YOK",
          "| dev e-posta: admin@huginn.local")

    try:
        from sqlalchemy import text

        from company_master.db import get_engine

        with get_engine().connect() as c:
            rows = c.execute(
                text(
                    "SELECT email, role, status, "
                    "COALESCE(password_hash,'') <> '' AS sifre_var "
                    "FROM users WHERE role='admin'"
                )
            ).fetchall()
        print("DB admin kullanicilari (email, rol, durum, sifre_var):", [tuple(r) for r in rows])
    except Exception as e:  # noqa: BLE001
        print("DB hata:", type(e).__name__, e)

    env = ROOT / ".env"
    if env.exists():
        keys = [
            satir.split("=", 1)[0]
            for satir in env.read_text(encoding="utf-8", errors="ignore").splitlines()
            if "ADMIN" in satir.upper() and "=" in satir and not satir.startswith("#")
        ]
        print(".env ADMIN anahtarlari (yalniz isim):", keys)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
