# -*- coding: utf-8 -*-
"""Groq API doğrudan istemcisi (NineRouter bypass).

D-195: NineRouter proxy DNS hatası (Cloudflare 1016) nedeniyle OpenAI-uyumlu
endpoint'e doğrudan çağrı yapar. Groq free tier: ~30 req/min, ~6000 tokens/min.

Kullanım:
    client = GroqClient(api_key="gsk_...")
    response = client.chat("Merhaba", model="groq/llama-3.3-70b-versatile")
"""
from __future__ import annotations

import os
from typing import Any

import requests

__all__ = ["GroqClient", "GroqError"]


class GroqError(Exception):
    """Groq API çağrısı hatası."""


class GroqClient:
    """Groq OpenAI-uyumlu API istemcisi.

    Groq free tier rate limits:
    - RPM: ~30 requests/minute
    - TPM: ~6000 tokens/minute per model
    """

    BASE_URL = "https://api.groq.com/openai/v1"

    def __init__(self, api_key: str | None = None) -> None:
        """Groq API key'i env veya parametre'den oku.

        Args:
            api_key: Groq API anahtarı. Boşsa env'den (GROQ_API_KEY) okur.

        Raises:
            GroqError: API key bulunamazsa.
        """
        self.api_key = (api_key or os.getenv("GROQ_API_KEY", "")).strip()
        if not self.api_key:
            raise GroqError(
                "Groq API key bulunamadı. GROQ_API_KEY env değişkenini ayarla."
            )
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        })

    def chat(
        self,
        prompt: str,
        model: str = "groq/llama-3.3-70b-versatile",
        system: str | None = None,
        temperature: float = 0.2,
        max_tokens: int = 1024,
    ) -> str:
        """OpenAI-uyumlu /v1/chat/completions çağrısı.

        Args:
            prompt: Kullanıcı mesajı.
            model: Model adı (groq/* prefix'i kaldırılır).
            system: Sistem prompt'u.
            temperature: Sıcaklık (0.0-2.0).
            max_tokens: Maksimum yanıt token'ı.

        Returns:
            Modelin yanıt metni.

        Raises:
            GroqError: API hatası veya ağ sorunu.
        """
        # groq/ prefix kaldır (model adı normalizasyonu)
        model_name = model.replace("groq/", "")

        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": model_name,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        try:
            resp = self.session.post(
                f"{self.BASE_URL}/chat/completions",
                json=payload,
                timeout=30,
            )
            resp.raise_for_status()
        except requests.RequestException as exc:
            # Detaylı hata mesajı
            try:
                error_detail = resp.json() if resp.status_code >= 400 else str(exc)
            except Exception:
                error_detail = str(exc)
            raise GroqError(f"Groq API hatası ({resp.status_code}): {error_detail}") from exc

        try:
            data = resp.json()
            choices = data.get("choices", [])
            if not choices:
                raise GroqError("Groq API yanıt boş (choices yok)")

            message = choices[0].get("message", {})
            content = message.get("content", "").strip()
            if not content:
                raise GroqError("Groq API yanıt boş (content yok)")

            return content
        except (ValueError, KeyError) as exc:
            raise GroqError(f"Groq API yanıt parse hatası: {exc}") from exc

    def __del__(self) -> None:
        """Session temizle."""
        if hasattr(self, "session"):
            try:
                self.session.close()
            except Exception:
                pass
