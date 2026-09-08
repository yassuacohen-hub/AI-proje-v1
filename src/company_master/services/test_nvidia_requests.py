"""NVIDIA NIM dogrudan HTTP testi.

Bu modul, langchain gibi agir bagimliliklar kullanmadan
requests kutuphanesi ile NVIDIA NIM API'ye istek atar.
Windows AppLocker/Defender kisitlamalarinda daha guvenilir calisir.

Kullanim:
    NVIDIA_API_KEY=nvapi-... python src/services/test_nvidia_requests.py
"""

import json
import os
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

# Proje kokunden .env yukle
project_root = Path(__file__).resolve().parents[2]
load_dotenv(project_root / ".env")


def get_env_key(name: str) -> str:
    """Ortam degiskenini guvenli sekilde okur."""
    value = os.getenv(name)
    if not value:
        raise EnvironmentError(
            f"{name} ortam degiskeni bulunamadi. "
            f"Lutfen .env dosyasina {name}=nvapi-... satirini ekleyin."
        )
    return value


def chat_with_nvidia(model: str, prompt: str) -> None:
    """NVIDIA NIM API'ye dogrudan chat.completions istegi atar.

    Args:
        model: NVIDIA model ID (ornek: nvidia/...).
        prompt: Kullanici mesaji.
    """
    api_key = get_env_key("NVIDIA_API_KEY")
    url = "https://integrate.api.nvidia.com/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.6,
        "top_p": 0.95,
        "max_tokens": 1024,
    }

    response = requests.post(url, headers=headers, json=payload, timeout=120)

    if response.status_code != 200:
        raise RuntimeError(
            f"HTTP {response.status_code}: {response.text}"
        )

    data = response.json()
    message = data["choices"][0]["message"]

    if message.get("reasoning_content"):
        print("Reasoning:")
        print(message["reasoning_content"])

    print("Cevap:")
    print(message.get("content", "(icerik bos)"))


if __name__ == "__main__":
    model_id = "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning"
    prompt = "Merhaba, kendini 1 cümleyle Türkçe tanit."

    try:
        chat_with_nvidia(model_id, prompt)
    except Exception as exc:  # noqa: BLE001
        print(f"Hata: {exc}", file=sys.stderr)
        sys.exit(1)
