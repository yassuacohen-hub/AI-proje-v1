# -*- coding: utf-8 -*-
"""9R-02: Embedder — 9Router embedding sarmalayici.

NineRouter.embed() cagrisini batch + retry + VPN bilinci ile sarar.
Her chunk ayri dener; basarisiz chunk'lar errors listesine eklenir,
digerleri yine de sonuca eklenir (kismi basari korunur).
"""
from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Any, Iterable

logger = logging.getLogger(__name__)

DEFAULT_EMBED_MODEL = "openrouter/openai/text-embedding-3-small"

try:  # 9Router istemcisi opsiyonel
    # Önce src-root deseni (pytest/src.company_master), sonra eski desen
    from src.company_master.gateway.ninerouter_client import get_client
except ImportError:  # pragma: no cover
    try:
        from company_master.gateway.ninerouter_client import get_client
    except ImportError:
        get_client = None  # type: ignore[assignment]


@dataclass
class EmbeddingResult:
    """Batch embed sonucu."""
    embeddings: list[list[float]]
    model: str
    errors: list[tuple[int, str]] = field(default_factory=list)

    @property
    def ok_count(self) -> int:
        return len(self.embeddings)

    @property
    def failed_count(self) -> int:
        return len(self.errors)

    def to_dict(self) -> dict[str, Any]:
        return {
            "model": self.model,
            "ok": self.ok_count,
            "failed": self.failed_count,
            "dim": len(self.embeddings[0]) if self.embeddings else 0,
            "errors": [{"index": i, "detail": d} for i, d in self.errors],
        }


class Embedder:
    """Metin listesini 9Router uzerinden vektore cevirir."""

    def __init__(
        self,
        model: str = DEFAULT_EMBED_MODEL,
        batch_size: int = 32,
        max_retries: int = 3,
        retry_delay_s: float = 1.5,
        client: Any | None = None,
    ) -> None:
        self.model = model
        self.batch_size = max(1, batch_size)
        self.max_retries = max(1, max_retries)
        self.retry_delay_s = max(0.0, retry_delay_s)
        self._client = client

    @property
    def client(self) -> Any:
        if self._client is None:
            if get_client is None:
                raise RuntimeError(
                    "9Router istemcisi kurulu degil; once .env'de NINEROUTER_* "
                    "ve requirements kurulumu gerekli."
                )
            self._client = get_client()
        return self._client

    def embed(self, texts: Iterable[str]) -> EmbeddingResult:
        """Metinleri vektore cevirir; basarisiz chunk'lar errors'a eklenir."""
        items = [t for t in texts if t and t.strip()]
        out: list[list[float]] = []
        errors: list[tuple[int, str]] = []

        for start in range(0, len(items), self.batch_size):
            chunk = items[start : start + self.batch_size]
            try:
                vecs = self._embed_chunk(chunk)
                out.extend(vecs)
            except Exception as exc:  # noqa: BLE001
                for k in range(len(chunk)):
                    errors.append((start + k, _kisa_hata(exc)))
                logger.warning(
                    "embed chunk basarisiz (items %d-%d): %s",
                    start, start + len(chunk) - 1, exc,
                )

        return EmbeddingResult(embeddings=out, model=self.model, errors=errors)

    def _embed_chunk(self, chunk: list[str]) -> list[list[float]]:
        """Tek batch'lik embed; retry mantigi.

        Sistem hatasi (istemci kurulu degil) icin retry/anlamsizdir — hizli
        basarisiz olur. Geçici ag hatalari (VPN/timeout) icin ustel backoff.
        """
        last_exc: Exception | None = None
        for attempt in range(1, self.max_retries + 1):
            try:
                raw = self.client.embed(chunk, model=self.model)
                return raw if isinstance(raw, list) else list(raw.get("embeddings", []))
            except Exception as exc:  # noqa: BLE001
                last_exc = exc
                if type(exc).__name__ == "RuntimeError" and "kurulu degil" in str(exc):
                    # sistem hatasi: retry boşuna bekleme yapar, hizli fail
                    break
                if attempt < self.max_retries:
                    logger.warning(
                        "embed retry %d/%d: %s", attempt, self.max_retries, exc
                    )
                    time.sleep(self.retry_delay_s * attempt)
        raise RuntimeError(
            f"Embed chunk basarisiz ({self.max_retries} deneme). Son hata: {last_exc}."
        ) from last_exc


def _kisa_hata(exc: Exception) -> str:
    """Hata kisa ozeti (VPN notu dahil)."""
    text = str(exc)
    if "VPN" in text or "timeout" in text.lower() or "connect" in text.lower():
        return f"{text[:200]} (olası neden: VPN / gateway)"
    return text[:200]


def embed_texts(texts: list[str], **kw: Any) -> EmbeddingResult:
    """Basit fonksiyon giris noktasi."""
    return Embedder(**kw).embed(texts)