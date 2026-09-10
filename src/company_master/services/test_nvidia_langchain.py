"""NVIDIA NIM Langchain entegrasyon testi.

Bu modul, NVIDIA NIM API uzerinden ChatNVIDIA ile tek bir istek atar.
API anahtari .env dosyasindaki NVIDIA_API_KEY degiskeninden okunur.

Kullanim:
    NVIDIA_API_KEY=nvapi-... python src/services/test_nvidia_langchain.py
"""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage

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


def invoke_nemotron(prompt: str) -> None:
    """Nemotron Nano Omni modeline istek atip yaniti yazdirir.

    Args:
        prompt: Modele gonderilecek kullanici mesaji.
    """
    from langchain_nvidia_ai_endpoints import ChatNVIDIA

    api_key = get_env_key("NVIDIA_API_KEY")

    client = ChatNVIDIA(
        model="nvidia/nemotron-3-nano-omni-30b-a3b-reasoning",
        api_key=api_key,
        temperature=0.6,
        top_p=0.95,
        max_tokens=1024,  # guvenli baslangic degeri
    )

    messages = [HumanMessage(content=prompt)]
    response = client.invoke(messages)

    if response.additional_kwargs and "reasoning_content" in response.additional_kwargs:
        print("Reasoning:")
        print(response.additional_kwargs["reasoning_content"])

    print("Cevap:")
    print(response.content)


if __name__ == "__main__":
    prompt = "Merhaba, kendini 1 cümleyle Türkçe tanit."
    try:
        invoke_nemotron(prompt)
    except Exception as exc:  # noqa: BLE001
        print(f"Hata: {exc}", file=sys.stderr)
        sys.exit(1)
