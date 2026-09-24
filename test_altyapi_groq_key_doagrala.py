#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""ALTYAPI-GROQ-KEY-DOGRULA-01: GroqClient canlı doğrulama testi."""

from __future__ import annotations

import sys
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / ".env")
sys.path.insert(0, str(ROOT / "src"))

from company_master.gateway.groq_client import GroqClient, GroqError


def test_groq_key_canli() -> bool:
    """GroqClient doğrudan çağrısını canlı API ile doğrular."""
    try:
        client = GroqClient()
        yanit = client.chat(
            "Kısa yanıt ver: Groq canlı doğrulama testi.",
            model="groq/openai/gpt-oss-20b",
        )
    except GroqError as exc:
        print(f"FAIL: {exc}")
        return False

    if not yanit or not yanit.strip():
        print("FAIL: Groq API boş yanıt verdi")
        return False

    print(f"PASS: GroqClient canlı çağrısı başarılı ({len(yanit)} karakter)")
    print(f"Yanıt: {yanit[:200]}")
    return True


if __name__ == "__main__":
    raise SystemExit(0 if test_groq_key_canli() else 1)
