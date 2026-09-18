# -*- coding: utf-8 -*-
"""ADMIN-LOGIN-FIX-01: canli admin girisi dogrulama (POST /api/admin/login).

Kullanim:
    python scripts/admin_giris_dogrula.py
    python scripts/admin_giris_dogrula.py --email x@y.z --sifre 1234

Sifre argumanla verilmezse ADMIN_PASSWORD / ADMIN2_PASSWORD ortam degiskeninden
okunur; hicbiri yoksa hesap atlanir (kaynak kodda sifre tutulmaz).
Cikis kodu: tum hesaplar 200 ise 0, degilse 1.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request

TABAN = os.getenv("HUGINN_API_TABAN", "http://localhost:8000")


def _istek(yol: str, govde: dict | None = None, zaman_asimi: int = 20) -> tuple[int, str]:
    veri = json.dumps(govde).encode() if govde is not None else None
    istek = urllib.request.Request(
        f"{TABAN}{yol}", data=veri, headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(istek, timeout=zaman_asimi) as yanit:
            return yanit.status, yanit.read().decode()[:200]
    except urllib.error.HTTPError as hata:
        return hata.code, hata.read().decode()[:200]
    except OSError as hata:  # baglanti yok / DNS / timeout
        return 0, str(hata)[:200]


def api_bekle(deneme: int = 10, aralik: int = 3) -> bool:
    """Konteyner acilisini bekler; /health 200 donerse True."""
    for _ in range(deneme):
        if _istek("/api/health", zaman_asimi=5)[0] == 200:
            return True
        time.sleep(aralik)
    return False


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Admin girisi canli dogrulama")
    ap.add_argument("--email", action="append", default=[])
    ap.add_argument("--sifre", action="append", default=[])
    args = ap.parse_args(argv)

    if args.email:
        hesaplar = list(zip(args.email, args.sifre + [""] * len(args.email)))
    else:
        hesaplar = [
            (os.getenv("ADMIN_EMAIL", "admin@huginn.local"), os.getenv("ADMIN_PASSWORD", "")),
            (os.getenv("ADMIN2_EMAIL", ""), os.getenv("ADMIN2_PASSWORD", "")),
        ]

    if not api_bekle():
        print(f"HATA: {TABAN}/api/health yanit vermedi (Docker kapali olabilir).")
        return 1

    hatali = 0
    for email, sifre in hesaplar:
        if not email or not sifre:
            print(f"ATLANDI: {email or '(email yok)'} — sifre/email tanimsiz")
            continue
        kod, govde = _istek("/api/admin/login", {"email": email, "password": sifre})
        durum = "OK" if kod == 200 else "HATA"
        if kod != 200:
            hatali += 1
        print(f"{durum} {email} -> {kod} {govde}")
    return 1 if hatali else 0


if __name__ == "__main__":
    sys.exit(main())
