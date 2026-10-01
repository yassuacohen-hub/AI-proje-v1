# -*- coding: utf-8 -*-
"""EVREN chat modellerini ayni Turkce prompt'la sinar (D-260: beyan degil olcum).

Kullanim:
    python scripts/evren_model_turkce_kalite.py
    python scripts/evren_model_turkce_kalite.py --self     # mandal (ag gerekmez)
"""
from __future__ import annotations

import json
import pathlib
import sys
import time
import urllib.error
import urllib.request

KOK = pathlib.Path(__file__).resolve().parents[1]
BASE = "https://evren-llmapi.ssyz.org.tr/v1"

ADAYLAR = [
    "deepseek-v4.1-flash",
    "mimo-v2.6-pro",
    "glm-5.3",
    "qwen3.8-flash-next",
    "gemma-4-31b",
]

PROMPT = (
    "Sen Ankara OSB firma verisi uzmanisin. Su firmayi iki cumlede yorumla: "
    "Unvan: OSTIM Dokum Sanayi A.S., NACE 24.51 (demir dokumculugu), "
    "calisan 85, kalite puani 3.2/7.5. Turkce yaz, kisa ol."
)


def anahtar() -> str:
    """.env icinden evren_llm_ ile baslayan anahtari okur."""
    for satir in (KOK / ".env").read_text(encoding="utf-8-sig").splitlines():
        if "evren_llm_" in satir:
            return "evren_llm_" + satir.split("evren_llm_", 1)[1].split()[0].strip()
    raise SystemExit("HATA: .env icinde evren_llm_ anahtari yok")


def icerik_oku(yanit: dict) -> str:
    """thinking modelleri content yerine reasoning_content doldurur (E43)."""
    msg = (yanit.get("choices") or [{}])[0].get("message") or {}
    return (msg.get("content") or msg.get("reasoning_content") or "").strip()


def sina(model: str, key: str) -> tuple[float, str]:
    govde = json.dumps(
        {"model": model, "messages": [{"role": "user", "content": PROMPT}],
         "max_tokens": 200, "temperature": 0.3}
    ).encode()
    istek = urllib.request.Request(
        f"{BASE}/chat/completions", data=govde,
        headers={"X-API-Key": key, "Content-Type": "application/json"},
    )
    t0 = time.time()
    with urllib.request.urlopen(istek, timeout=120) as r:
        yanit = json.load(r)
    return time.time() - t0, icerik_oku(yanit)


def _self() -> int:
    assert icerik_oku({"choices": [{"message": {"content": None,
                                               "reasoning_content": " x "}}]}) == "x"
    assert icerik_oku({"choices": [{"message": {"content": "a"}}]}) == "a"
    assert icerik_oku({}) == ""
    print("self-check OK")
    return 0


def main(argv: list[str]) -> int:
    if "--self" in argv:
        return _self()
    key = anahtar()
    for model in ADAYLAR:
        try:
            sure, metin = sina(model, key)
        except (urllib.error.URLError, OSError, ValueError) as e:
            print(f"\n=== {model} === HATA: {type(e).__name__}: {e}")
            continue
        print(f"\n=== {model} === {sure:.1f}s / {len(metin)} karakter")
        print(metin or "(BOS YANIT)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
