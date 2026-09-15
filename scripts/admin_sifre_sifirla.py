# -*- coding: utf-8 -*-
"""Admin şifre sıfırlama (yerel araç, Ürün Sahibi için).

Kullanım:
    python scripts/admin_sifre_sifirla.py --email yassuacohen@gmail.com
    python scripts/admin_sifre_sifirla.py --email ... --sifre "GizliSifre" --env-yaz

- Şifre `--sifre` verilmezse getpass ile gizli istenir.
- Hash formatı web_app._hash_password ile birebir aynı: pbkdf2$iter$salt$hash.
- `--env-yaz` verilirse `.env` içine ADMIN_EMAIL / ADMIN_PASSWORD upsert edilir
  (.env gitignore'da; asla depoya girmez). Giriş formu bu değerleri ön-doldurur.
- Şifre veya hash ekrana basılmaz.
"""
from __future__ import annotations

import argparse
import getpass
import hashlib
import hmac
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

PBKDF2_ITER = 120_000
MIN_UZUNLUK = 8


def hash_password(password: str) -> str:
    """web_app._hash_password ile aynı format (pbkdf2$iter$salt$hash)."""
    salt = os.urandom(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, PBKDF2_ITER)
    return f"pbkdf2${PBKDF2_ITER}${salt.hex()}${dk.hex()}"


def verify_password(password: str, stored: str) -> bool:
    try:
        _, iters, salt_hex, hash_hex = stored.split("$")
        dk = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt_hex), int(iters))
        return hmac.compare_digest(dk.hex(), hash_hex)
    except Exception:
        return False


def env_upsert(env_path: Path, degerler: dict[str, str]) -> None:
    """`.env` içinde anahtarları günceller/ekler; diğer satırlara dokunmaz (UTF-8, BOM yok).

    D-24: Aynı anahtarın tekrar eden kopyaları silinir (ilk satır güncellenir, sonrakiler
    düşer). Aksi halde `load_dotenv` son kopyayı okuyup DB ile uyumsuz şifre ön-doldurur.
    """
    satirlar: list[str] = []
    if env_path.exists():
        satirlar = env_path.read_text(encoding="utf-8-sig").splitlines()
    kalan = dict(degerler)
    yeni: list[str] = []
    for satir in satirlar:
        m = re.match(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=", satir)
        anahtar = m.group(1) if m else None
        if anahtar in degerler:
            if anahtar in kalan:
                yeni.append(f"{anahtar}={kalan.pop(anahtar)}")
            continue  # tekrar eden kopya → düşür
        yeni.append(satir)
    for anahtar, deger in kalan.items():
        yeni.append(f"{anahtar}={deger}")
    env_path.write_text("\n".join(yeni) + "\n", encoding="utf-8")


def db_sifre_guncelle(email: str, sifre_hash: str) -> int:
    """users.password_hash günceller; etkilenen satır sayısını döner."""
    from sqlalchemy import text

    from company_master.db import get_engine

    with get_engine().begin() as c:
        r = c.execute(
            text("UPDATE users SET password_hash=:h, status='onayli' WHERE email=:e AND role='admin'"),
            {"h": sifre_hash, "e": email},
        )
        return int(r.rowcount or 0)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Admin şifresini sıfırlar.")
    ap.add_argument("--email", required=True)
    ap.add_argument("--sifre", default=None, help="Verilmezse gizli istenir.")
    ap.add_argument("--env-yaz", action="store_true", help=".env'e ADMIN_EMAIL/ADMIN_PASSWORD yaz.")
    args = ap.parse_args(argv)

    sifre = args.sifre or getpass.getpass("Yeni şifre: ")
    if len(sifre) < MIN_UZUNLUK:
        print(f"HATA: sifre en az {MIN_UZUNLUK} karakter olmali.")
        return 2
    if args.sifre is None and getpass.getpass("Tekrar: ") != sifre:
        print("HATA: sifreler uyusmuyor.")
        return 2

    h = hash_password(sifre)
    assert verify_password(sifre, h)
    n = db_sifre_guncelle(args.email, h)
    if n == 0:
        print(f"HATA: role='admin' olan '{args.email}' bulunamadi (python scripts/admin_kimlik_kontrol.py).")
        return 1
    # Konsol çıktıları ASCII: Windows cp1254 konsolunda Unicode ok/Türkçe çökmesin.
    print(f"OK: {args.email} sifresi guncellendi ({n} kayit).")

    if args.env_yaz:
        env_upsert(ROOT / ".env", {"ADMIN_EMAIL": args.email, "ADMIN_PASSWORD": sifre})
        print("OK: .env -> ADMIN_EMAIL / ADMIN_PASSWORD yazildi (giris formu on-dolar).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
