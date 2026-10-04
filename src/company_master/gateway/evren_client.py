# -*- coding: utf-8 -*-
"""EVREN istemcisi — OpenAI-uyumlu geçit (yalnız embedding).

Neden ayrı istemci: 9Router üzerinden `qwen3-embedding-8b` **404** veriyor
(ölçüldü 2026-10-02: "model does not exist or you do not have access").
EVREN'in kendi uç noktası aynı modeli **0 kredi** ile döndürüyor.

Ölçüm (ALTYAPI-RAG-EMBEDDER-01):
    GET  /v1/models   → 12 model, `task=embedding` olan TEK model:
                        `qwen3-embedding-8b`, free_until 2026-11-01
    POST /v1/embeddings → 4096 boyut, prompt_tokens 22, credits 0.0000

KÖPRÜ (D-184): kullanan `src/company_master/vector/embedder.py` ·
görev `plans/brief_yasu_ALTYAPI-RAG-EMBEDDER-01.md` ·
test `tests/test_rag_embedder.py` · hub `hubs/TOOLS_SCRIPTS_HUB.md`
"""
from __future__ import annotations

import json
import logging
import urllib.error
import urllib.request
from typing import Any

logger = logging.getLogger(__name__)

__all__ = ["EvrenClient", "EvrenHatasi"]


class EvrenHatasi(RuntimeError):
    """EVREN çağrısı başarısız."""


class EvrenClient:
    """Minimal OpenAI-uyumlu embedding istemcisi.

    Yalnız `embed()` sağlar — EVREN'de sohbet/araç kullanımı bu görevin
    kapsamı dışıdır (brif: RAG embedding'i).
    """

    def __init__(self, base_url: str, api_key: str, timeout: float = 60.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout

    def embed(self, texts: list[str], model: str) -> list[list[float]]:
        """Metin listesini vektöre çevirir. Boş liste dönerse hata verir."""
        if not texts:
            return []
        govde = json.dumps({"model": model, "input": list(texts)}).encode("utf-8")
        istek = urllib.request.Request(
            f"{self.base_url}/v1/embeddings",
            data=govde,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
        )
        try:
            with urllib.request.urlopen(istek, timeout=self.timeout) as yanit:
                veri: Any = json.loads(yanit.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:  # pragma: no cover - ağ yolu
            govde_hata = exc.read().decode("utf-8", "replace")[:200]
            raise EvrenHatasi(f"EVREN {exc.code}: {govde_hata}") from exc
        except urllib.error.URLError as exc:  # pragma: no cover - ağ yolu
            raise EvrenHatasi(f"EVREN erisilemedi: {exc.reason}") from exc

        vektorler = [x["embedding"] for x in veri.get("data", [])]
        if not vektorler:
            raise EvrenHatasi("EVREN bos vektor dondurdu")
        return vektorler
