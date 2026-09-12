#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""9R-02e: NineRouter istemcisi URL normalizasyonu + embedder import regresyonu.

Kapsanan düzeltmeler:
  1. NINEROUTER_URL hem base ("http://host:port") hem "/v1" suffix'li
     ("http://host:port/v1") verilebilir; istemci sondaki "/v1" temizler
     (aksi halde "/v1/v1/embeddings" oluşurdu).
  2. embedder.py artık önce src-root deseniyle import eder; "kurulu degil"
     hatasının kök nedeni (company_master vs src.company_master uyuşmazlığı)
     giderildi.
"""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from src.company_master.gateway.ninerouter_client import NineRouter


class TestUrlNormalizasyonu:
    """base_url / NINEROUTER_URL normalizasyonu (network çağrısı yok)."""

    def test_v1_suffiksi_temizlenir(self) -> None:
        nr = NineRouter(base_url="https://r3qmzpf.abc-tunnel.us/v1")
        assert nr.base_url == "https://r3qmzpf.abc-tunnel.us"

    def test_v1_suffiksi_slash_ile_temizlenir(self) -> None:
        nr = NineRouter(base_url="https://r3qmzpf.abc-tunnel.us/v1/")
        assert nr.base_url == "https://r3qmzpf.abc-tunnel.us"

    def test_base_url_degismez(self) -> None:
        nr = NineRouter(base_url="http://localhost:20128")
        assert nr.base_url == "http://localhost:20128"

    def test_trailing_slash_temizlenir(self) -> None:
        nr = NineRouter(base_url="http://localhost:20128/")
        assert nr.base_url == "http://localhost:20128"

    def test_env_ile_v1_suffiksi_temizlenir(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("NINEROUTER_URL", "https://r3qmzpf.abc-tunnel.us/v1")
        nr = NineRouter()
        assert nr.base_url == "https://r3qmzpf.abc-tunnel.us"

    def test_env_yoksa_varsayilan_local(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.delenv("NINEROUTER_URL", raising=False)
        nr = NineRouter()
        assert nr.base_url == "http://localhost:20128"

    def test_v1_olmayan_path_korunur(self) -> None:
        # "v1" ile bitmeyen path'ler değişmez.
        nr = NineRouter(base_url="https://example.com/gateway")
        assert nr.base_url == "https://example.com/gateway"


class TestEmbedderImportUyusmazligi:
    """"kurulu degil" kök nedeni: import path uyuşmazlığı çözüldü mü?"""

    def test_embedder_get_client_import_edilebilir(self) -> None:
        import src.company_master.vector.embedder as embedder_mod

        # Çift try/except: get_client ya fonksiyondur ya da None kalır;
        # iki durumda da modül import edilir ve RuntimeError fırlamaz.
        gc = embedder_mod.get_client
        assert gc is not None, (
            "9Router istemcisi import edilemedi — .env'de NINEROUTER_* olmadığı "
            "için opsiyonel path tetiklenmemiş olabilir."
        )
        assert callable(gc)


class TestUtf8Decode:
    """9R-03: charset'siz/ISO-8859-1 etiketli yanıtlarda UTF-8 mojibake önlemi."""

    def _mock_resp(self, text: str) -> MagicMock:
        # resp.text (ISO-8859-1 kirliliği) ile content (gerçek UTF-8 baytları)
        # arasındaki farkı simüle et: text mojibake, content doğru.
        from unittest.mock import MagicMock

        r = MagicMock()
        r.status_code = 200
        r.encoding = "ISO-8859-1"
        r.text = text.encode("utf-8").decode("latin-1")  # mojibake
        r.content = text.encode("utf-8")  # gerçek baytlar
        return r

    def test_utf8_content_tercih_edilir(self, monkeypatch) -> None:
        from src.company_master.gateway.ninerouter_client import NineRouter

        nr = NineRouter(base_url="http://localhost:20128", max_retries=0)
        # Gerçek 9Router paket şekli: _request yalnızca hem "data" hem "success"
        # anahtarı varsa data["data"]'yı döndürür (bkz. ninerouter_client._request).
        resp = self._mock_resp('{"data": {"sektor": "BİLİŞİM"}, "success": true}')

        with monkeypatch.context() as m:
            import requests as _requests  # noqa: F401

            session = MagicMock()
            session.request.return_value = resp
            m.setattr(nr, "_session", session)
            payload = nr._request("POST", "/v1/chat/completions", json={})
        assert payload["sektor"] == "BİLİŞİM"


class TestWebFetchSözleşmesi:
    """9R-04: /v1/web/fetch sözleşmesi — suffix'siz provider + format alanı.

    Skill dokümanı referansı: plans/9router_web_fetch_SKILL.md
      - "model (or provider)": firecrawl | jina-reader | tavily | exa | ollama
      - İstek alanı ``format`` (markdown/text/html), ``outputFormat`` DEĞİL.
      - Yanıt: ``content: {format, text, length}``.
    """

    def _kur(self, monkeypatch, yanit_json: str):
        from src.company_master.gateway.ninerouter_client import NineRouter

        import requests as _requests  # noqa: F401

        nr = NineRouter(base_url="http://localhost:20128", max_retries=0)
        r = MagicMock()
        r.status_code = 200
        r.text = yanit_json
        r.content = yanit_json.encode("utf-8")
        session = MagicMock()
        session.request.return_value = r
        monkeypatch.setattr(nr, "_session", session)
        return nr, session

    def test_suffixsiz_provider_ve_format_alani(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # Gerçek 9Router paketli yanıt şekli:
        #   {"data": {...}, "success": true} → _request data["data"]'yı döndürür.
        nr, session = self._kur(
            monkeypatch,
            '{"data": {"provider": "firecrawl", "url": "https://9router.com", '
            '"content": {"format": "markdown", "text": "# Başlık", "length": 7}}, '
            '"success": true}',
        )
        sonuc = nr.web_fetch("https://9router.com")
        # Gövde: model suffix'siz, format alanı, outputFormat yok.
        g = session.request.call_args.kwargs
        body = g.get("json", {})
        assert body["model"] == "firecrawl"
        assert body["format"] == "markdown"
        assert "outputFormat" not in body
        # content dict normalizasyonu → düz metin.
        assert sonuc["content"] == "# Başlık"

    def test_max_characters_eklenir(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        nr, session = self._kur(
            monkeypatch,
            '{"data": {"content": {"format": "text", "text": "metin"}}, "success": true}',
        )
        nr.web_fetch(
            "https://example.com", max_characters=2000
        )
        body = session.request.call_args.kwargs.get("json", {})
        assert body["max_characters"] == 2000

    def test_str_yanit_content_olarak_doner(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # Skill dokümanındaki düz (paketsiz) yanıt şekli:
        #   {provider, url, title, content: {format, text, length}}.
        nr, session = self._kur(
            monkeypatch,
            '{"provider": "jina-reader", "url": "https://example.com", '
            '"content": {"format": "text", "text": "ham metin", "length": 9}}',
        )
        sonuc = nr.web_fetch("https://example.com", provider="jina-reader")
        assert sonuc["content"] == "ham metin"
        assert sonuc.get("provider") == "jina-reader"


class TestWebSearchSözleşmesi:
    """9R-04: /v1/search sözleşmesi — suffix'siz provider + max_results.

    Skill dokümanı referansı: plans/9router_web_search_SKILL.md
      - "Provider IS the model": tavily ≡ model=tavily.
      - Sonuç sayısı alanı ``max_results`` (alt çizgili), ``maxResults`` DEĞİL.
    """

    def test_suffixsiz_provider_ve_max_results_alani(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from src.company_master.gateway.ninerouter_client import NineRouter

        import requests as _requests  # noqa: F401

        nr = NineRouter(base_url="http://localhost:20128", max_retries=0)
        r = MagicMock()
        r.status_code = 200
        y = '{"data": {"provider": "tavily", "results": [{"title": "x"}]}, "success": true}'
        r.text = y
        r.content = y.encode("utf-8")
        session = MagicMock()
        session.request.return_value = r
        monkeypatch.setattr(nr, "_session", session)

        nr.web_search("yapay zeka girişimleri", max_results=7)
        body = session.request.call_args.kwargs.get("json", {})
        assert body["model"] == "tavily"
        assert body["max_results"] == 7
        assert "maxResults" not in body

    def test_extra_parametreler_govdeye_eklenir(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from src.company_master.gateway.ninerouter_client import NineRouter

        import requests as _requests  # noqa: F401

        nr = NineRouter(base_url="http://localhost:20128", max_retries=0)
        r = MagicMock()
        r.status_code = 200
        y = '{"data": {"provider": "tavily", "results": []}, "success": true}'
        r.text = y
        r.content = y.encode("utf-8")
        session = MagicMock()
        session.request.return_value = r
        monkeypatch.setattr(nr, "_session", session)

        nr.web_search(
            "ostim yazılım", provider="tavily",
            extra={"country": "TR", "search_type": "news"},
        )
        body = session.request.call_args.kwargs.get("json", {})
        assert body["country"] == "TR"
        assert body["search_type"] == "news"