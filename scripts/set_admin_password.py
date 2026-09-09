#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Admin olusturma + sifre atama yardimcisi.

Kullanim:
  python scripts/set_admin_password.py add <email> <sifre> [firma_adi]   # yeni admin
  python scripts/set_admin_password.py set <email> <sifre>               # sifre ata/guncelle
  python scripts/set_admin_password.py --list                            # adminleri listele
"""
import os
import sys
from pathlib import Path

from sqlalchemy import create_engine, text

ROOT = Path(__file__).resolve().parents[1]

# web_app.py ile ayni PBKDF2 sablonu
_ITER = 120_000


def _hash_password(password: str) -> str:
    import hashlib
    salt = os.urandom(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, _ITER)
    return f"pbkdf2${_ITER}${salt.hex()}${dk.hex()}"


def load_urls() -> list[str]:
    urls = []
    if os.environ.get("DATABASE_URL"):
        urls.append(os.environ["DATABASE_URL"])
    env = ROOT / ".env"
    if env.exists():
        for line in env.read_text(encoding="utf-8", errors="ignore").splitlines():
            line = line.strip()
            if line.startswith("DATABASE_URL") and "=" in line:
                u = line.split("=", 1)[1].strip().strip('"').strip("'")
                if u and u not in urls:
                    urls.append(u)
    return urls


if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) >= 3 and args[0] == "add":
        email, password = args[1].strip().lower(), args[2]
        firma = args[3] if len(args) > 3 else "Huginn Yonetim"
        if len(password) < 8:
            raise SystemExit("sifre en az 8 karakter olmali")
        if "@" not in email:
            raise SystemExit("gecerli e-posta girin")
        ph = _hash_password(password)
        domain = email.split("@")[-1]
        for url in load_urls():
            try:
                eng = create_engine(url)
                with eng.begin() as conn:
                    conn.execute(text("""
                        INSERT INTO users (email, email_domain, company_name, role, status,
                                           tier, credit_balance, kvkk_consent, password_hash)
                        VALUES (:e, :d, :f, 'admin', 'onayli', 'enterprise', -1, TRUE, :p)
                        ON CONFLICT (email) DO UPDATE SET
                          role = 'admin', status = 'onayli', tier = 'enterprise',
                          credit_balance = -1, password_hash = :p, kvkk_consent = TRUE
                    """), {"e": email, "d": domain, "f": firma, "p": ph})
            except Exception as e:
                print(f"SKIP: {e}")
        print(f"OK: admin olusturuldu -> {email}")
    elif len(args) >= 3 and args[0] == "set":
        email, password = args[1].strip().lower(), args[2]
        if len(password) < 8:
            raise SystemExit("sifre en az 8 karakter olmali")
        ph = _hash_password(password)
        for url in load_urls():
            try:
                eng = create_engine(url)
                with eng.begin() as conn:
                    conn.execute(text(
                        "UPDATE users SET password_hash = :p, updated_at = CURRENT_TIMESTAMP "
                        "WHERE email = :e"), {"p": ph, "e": email})
            except Exception as e:
                print(f"SKIP: {e}")
        print(f"OK: sifre guncellendi -> {email}")
    elif args and args[0] == "--list":
        for url in load_urls():
            try:
                eng = create_engine(url)
                with eng.connect() as conn:
                    rows = conn.execute(text(
                        "SELECT email, role, status, tier FROM users WHERE role = 'admin'")).mappings().all()
                for r in rows:
                    print(dict(r))
            except Exception as e:
                print(f"SKIP: {e}")
    else:
        print(__doc__)

