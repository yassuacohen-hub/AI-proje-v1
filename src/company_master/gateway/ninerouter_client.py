"""9Router AI Gateway istemcisi.

OpenAI-uyumlu REST geçidi üzerinden chat, embeddings, web-fetch ve
web-search çağrılarını tek noktadan yönetir.

Kurulum (.env):
    NINEROUTER_URL=http://localhost:20128
    NINEROUTER_KEY=sk-...            # requireApiKey=true ise zorunlu
    NINEROUTER_MODEL=yasu-9router    # varsayılan model (opsiyonel)

Hata yönetimi:
    - 401  -> NINEROUTER_KEY hatalı/eksik
    - 400  -> model kimliği /v1/models altında yok
    - 503  -> sağlayıcı tarafı geçici kapalı (retry-after önerisi)
    - Ağ hatası / timeout -> GatewayUnavailable
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any

import requests

# --- Ortam yükleme (db/connection.py ile aynı desen) ---


def _find_root() -> Path:
    here = Path(__file__).resolve().parent
    for candidate in [here, *here.parents]:
        env_path = candidate / ".env"
        if env_path.exists():
            try:
                if "NINEROUTER_URL" in env_path.read_text(encoding="utf-8"):
                    return candidate
            except Exception:
                pass
    return here.parents[2]  # src/company_master/gateway -> proje kökü


try:
    from dotenv import load_dotenv
    load_dotenv(_find_root() / ".env")
except ImportError:
    pass


class NineRouterError(Exception):
    """9Router çağrısı başarısız oldu."""


class GatewayUnavailable(NineRouterError):
    """Sunucuya ulaşılamadı (ağ / timeout / DNS)."""


class NineRouter:
    """9Router gateway istemcisi.

    Kullanım::

        nr = NineRouter()
        yanit = nr.chat("Merhaba")
        emb = nr.embed(["firma bilgisi"])
        md = nr.web_fetch("https://example.com/kariyer")
    """

    def __init__(
        self,
        base_url: str | None = None,
        api_key: str | None = None,
        default_model: str | None = None,
        timeout: float = 60.0,
        max_retries: int = 2,
    ) -> None:
        # URL normalizasyonu: NINEROUTER_URL hem base ("http://host:port") hem
        # de "/v1" suffix'li ("http://host:port/v1") verilebilir. Tüm api path'leri
        # istemci tarafinda "/v1/..." eklendigi icin sondaki "/v1" asama temizlenir
        # (aksi halde "/v1/v1/embeddings" olusur).
        base = (
            base_url or os.getenv("NINEROUTER_URL", "http://localhost:20128")
        ).rstrip("/")
        if base.endswith("/v1"):
            base = base[: -len("/v1")]
        self.base_url = base
        self.api_key = api_key or os.getenv("NINEROUTER_KEY")
        self.default_model = default_model or os.getenv(
            "NINEROUTER_MODEL", "yasu-9router"
        )
        self.timeout = timeout
        self.max_retries = max_retries
        self._session = requests.Session()

    # ---- düşük seviye yardımcılar ----

    @staticmethod
    def _parse_body(text: str) -> Any:
        """9Router yanıtını normalize eder.

        SSE format (data: {json}\n\ndata: [DONE]) veya çok satırlı
        tek JSON dönebildiği için requests.json() yetmez. Bu metod:
          - İlk satırda JSON varsa onu döner,
          - 'data:' prefix'lerini ayıklayıp ilk geçerli JSON'u
            döner,
          - hiçbiri yoksa dict/str olarak geri döner.
        """
        text = (text or "").strip()
        if not text:
            return {}

        # 1) Tek parça JSON (normal yanıt)
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # 2) SSE / satır satır: her 'data:' satırını dene
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            if line.startswith("data:"):
                line = line[len("data:"):].strip()
                if line == "[DONE]":
                    continue
            try:
                return json.loads(line)
            except json.JSONDecodeError:
                continue

        # 3) Elde edilemediyse ham metni döndür
        return {"text": text}

    def _headers(self, json_body: bool = True) -> dict[str, str]:
        h: dict[str, str] = {}
        if json_body:
            h["Content-Type"] = "application/json"
        if self.api_key:
            h["Authorization"] = f"Bearer {self.api_key}"
        return h

    def _request(self, method: str, path: str, **kw: Any) -> dict[str, Any]:
        url = f"{self.base_url}{path}"
        headers = kw.pop("_headers", None) or self._headers(
            json_body=kw.get("json") is not None
        )
        last_err: Exception | None = None
        for attempt in range(self.max_retries + 1):
            try:
                resp = self._session.request(
                    method, url, headers=headers, timeout=self.timeout, **kw
                )
            except requests.RequestException as exc:
                last_err = exc
                if attempt < self.max_retries:
                    time.sleep(0.5 * (attempt + 1))
                    continue
                raise GatewayUnavailable(
                    f"9Router'a ulaşılamadı ({self.base_url}): {exc}"
                ) from exc

            if resp.status_code == 200:
                # resp.text requests tarafından charset'siz yanıtta ISO-8859-1
                # ile decode edilir → UTF-8 Türkçe karakterler mojibake olur.
                # 9Router JSON API'dir (RFC 8259 → UTF-8); bu yüzden content
                # baytlarını doğrudan UTF-8 ile çözeriz. Mock/eksik nesnede
                # resp.text'e güvenli düşüş yapılır.
                text = resp.text
                try:
                    content = resp.content
                    if isinstance(content, bytes):
                        text = content.decode("utf-8", errors="replace")
                except Exception:  # noqa: BLE001 — mock/eksik nesnede resp.text'e düş
                    pass
                data = self._parse_body(text)
                # 9Router bazen {data:{...}, success:true} paketi döner
                if isinstance(data, dict) and "data" in data and "success" in data:
                    return data["data"]
                return data

            # 503 -> anlık sağlayıcı hatası; bir kez daha dene
            if resp.status_code == 503 and attempt < self.max_retries:
                retry_after = resp.headers.get("retry-after")
                try:
                    time.sleep(float(retry_after or 1.0))
                except ValueError:
                    time.sleep(1.0)
                continue

            try:
                detail = resp.json()
            except ValueError:
                detail = resp.text
            raise NineRouterError(
                f"9Router {resp.status_code} {path}: {detail}"
            )
        raise NineRouterError(f"9Router tekrar denemeleri tükendi: {last_err}")

    # ---- sağlık / keşif ----

    def health(self) -> bool:
        """/api/health — gateway ayakta mı?"""
        try:
            data = self._request("GET", "/api/health")
            return bool(data.get("ok"))
        except NineRouterError:
            return False

    def list_models(self, kind: str = "") -> list[dict[str, Any]]:
        """Model listesi: kind='embedding' | 'web' | 'image' | '' (chat)."""
        path = "/v1/models"
        if kind:
            path += f"/{kind}"
        data = self._request("GET", path)
        return data.get("data", []) if isinstance(data, dict) else []

    def model_ids(self, kind: str = "") -> list[str]:
        return [m.get("id", "") for m in self.list_models(kind)]

    # ---- chat ----

    def chat(
        self,
        prompt: str,
        model: str | None = None,
        system: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = 1024,
    ) -> str:
        """OpenAI /v1/chat/completions çağrısı; yanıt metnini döner."""
        messages: list[dict[str, str]] = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        body: dict[str, Any] = {
            "model": model or self.default_model,
            "messages": messages,
        }
        if temperature is not None:
            body["temperature"] = temperature
        if max_tokens is not None:
            body["max_tokens"] = max_tokens
        data = self._request("POST", "/v1/chat/completions", json=body)
        try:
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise NineRouterError(f"Chat yanıtı beklenen şekilde değil: {data}") from exc

    # ---- embeddings ----

    def embed(
        self,
        inputs: list[str] | str,
        model: str = "openrouter/openai/text-embedding-3-small",
    ) -> list[list[float]]:
        """Metinleri vektöre çevirir (ChromaDB / benzerlik için)."""
        texts = [inputs] if isinstance(inputs, str) else inputs
        body: dict[str, Any] = {"model": model, "input": texts}
        data = self._request("POST", "/v1/embeddings", json=body)
        try:
            return [item["embedding"] for item in data["data"]]
        except (KeyError, TypeError) as exc:
            raise NineRouterError(
                f"Embedding yanıtı beklenen şekilde değil: {data}"
            ) from exc

    # ---- web fetch ----

    def web_fetch(
        self,
        url: str,
        provider: str = "firecrawl",
        output_format: str = "markdown",
        max_characters: int | None = None,
        extra: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """URL'den markdown/html çeker (kariyer sayfaları, OSINT kaynakları).

        9R-04: 9Router /v1/web/fetch sözleşmesine uyum (skill dokümanı):
          - provider suffix'siz kullanılır: firecrawl | jina-reader | tavily |
            exa | ollama | fetch-combo ("Provider IS the model").
          - İstek alanı ``format`` (markdown/text/html) + opsiyonel
            ``max_characters`` — ``outputFormat`` değil.
          - Yanıt: ``content: {format, text, length}`` normalize edilir.

        Not: 9Router'da webFetch sağlayıcısı yapılandırılmamışsa
        (Dashboard → Providers → firecrawl / jina-reader / tavily)
        bu çağrı başarısız olur. Kullanmadan önce sağlayıcı ekleyin.
        """
        body: dict[str, Any] = {
            "model": provider,
            "url": url,
            "format": output_format,
        }
        if max_characters is not None:
            body["max_characters"] = max_characters
        if extra:
            body.update(extra)
        data = self._request("POST", "/v1/web/fetch", json=body)
        # Farklı sağlayıcılar farklı şekil döner; en yaygın olanları normalize et.
        if isinstance(data, str):
            return {"content": data}
        if isinstance(data, dict):
            # 9Router skill şekli: content -> {"format": ..., "text": ..., "length": ...}
            ic = data.get("content")
            if isinstance(ic, dict):
                text = ic.get("text", ic)
                return {**data, "content": text}
            for key in ("markdown", "text", "html", "data"):
                if data.get(key):
                    return {"content": data.get(key), "provider": provider}
            if "content" in data:
                return {**data, "provider": data.get("provider", provider)}
        return {"content": data, "provider": provider}

    # ---- web search ----

    def web_search(
        self,
        query: str,
        provider: str = "tavily",
        max_results: int = 5,
        extra: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Web araması yapar (OSINT / şirket araştırması).

        9R-04: 9Router /v1/search sözleşmesine uyum (skill dokümanı):
          - provider suffix'siz kullanılır: tavily | exa | brave | serper |
            perplexity | linkup | google-pse | searchapi | youcom | xquik.
          - Sonuç sayısı alanı ``max_results`` (alt çizgili) — ``maxResults`` değil.
          - Opsiyonel: search_type, country, language, time_range, domain_filter
            (provider'a bağlı) extra sözlüğüyle geçirilebilir.

        Uyarı: 9Router'da webSearch sağlayıcısı yapılandırılmamışsa
        bu çağrı başarısız olur. Sağlayıcı eklemek için Dashboard →
        Providers üzerinden tavily/exa/brave vb. bağlayın.
        """
        body: dict[str, Any] = {
            "model": provider,
            "query": query,
            "max_results": max_results,
        }
        if extra:
            body.update(extra)
        data = self._request("POST", "/v1/search", json=body)
        return data if isinstance(data, dict) else {"results": data}


# Tekil örnek (hafif cache) — uygulama genelinde paylaşılır
_default_client: NineRouter | None = None


def get_client() -> NineRouter:
    global _default_client
    if _default_client is None:
        _default_client = NineRouter()
    return _default_client