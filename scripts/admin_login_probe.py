# -*- coding: utf-8 -*-
"""Admin giriş API'sini `.env` kimliğiyle canlı yoklar (AUTH-01 teşhis aracı).

Kullanım: python scripts/admin_login_probe.py
Çıktı: API adresi, HTTP kodu, token var/yok (SEC-AUTH-01 O-2: POST kullanılır).
Şifre asla yazdırılmaz.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))
from dash04_api_client import _api_url  # noqa: E402


def main() -> int:
    try:
        from dotenv import load_dotenv

        load_dotenv(Path(__file__).resolve().parents[1] / ".env")
    except Exception:
        pass
    base = _api_url()
    email = os.getenv("ADMIN_EMAIL", "")
    sifre = os.getenv("ADMIN_PASSWORD", "")
    print(f"API: {base} | e-posta: {email or '(bos)'} | sifre: {'var' if sifre else 'YOK'}")
    try:
        r = requests.post(
            f"{base}/api/admin/login",
            json={"email": email, "password": sifre},
            timeout=10,
        )
    except requests.RequestException as exc:
        print(f"BAGLANTI HATASI: {exc}")
        return 2
    print(f"POST /api/admin/login -> HTTP {r.status_code}")
    try:
        j = r.json()
    except ValueError:
        j = r.text[:200]
    if isinstance(j, dict) and j.get("token"):
        print(f"token: VAR ({len(j['token'])} kr) -> giris CALISIYOR")
        kod = 0
    else:
        print(f"yanit: {j}")
        kod = 1
    return kod


if __name__ == "__main__":
    raise SystemExit(main())
