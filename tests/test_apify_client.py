# -*- coding: utf-8 -*-
"""APIFY-02: Apify REST adaptoru birim testleri (mock'lu, ag yok)."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from company_master.intelligence.job_intelligence.sources.apify_client import (
    ApifyClient,
    ApifyError,
)

TOKEN = "test-token-123"


def make_client() -> ApifyClient:
    session = MagicMock()
    return ApifyClient(token=TOKEN, session=session)


def resp(status_code: int, json_data=None) -> MagicMock:
    r = MagicMock()
    r.status_code = status_code
    r.json.return_value = json_data if json_data is not None else {}
    r.text = ""
    return r


class TestTokenGuvenligi:
    def test_token_bos_ise_hata(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("APIFY_TOKEN", raising=False)
        with pytest.raises(ApifyError, match="APIFY_TOKEN"):
            ApifyClient(token="")

    def test_token_ortamdan_okunur(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("APIFY_TOKEN", "env-token")
        c = ApifyClient()
        assert c.token == "env-token"

    def test_token_url_sorgusuna_girer_loglansin_diye_param_ici(self) -> None:
        c = make_client()
        c.session.post.return_value = resp(
            201, {"data": {"id": "r1", "defaultDatasetId": "d1"}}
        )
        c.start_actor_run("a/b", {"startUrls": []})
        _, kwargs = c.session.post.call_args
        assert kwargs["params"]["token"] == TOKEN


class TestStartActorRun:
    def test_basarili_baslatici(self) -> None:
        c = make_client()
        c.session.post.return_value = resp(
            201, {"data": {"id": "run1", "defaultDatasetId": "ds1"}}
        )
        meta = c.start_actor_run(
            "apify/web-scraper",
            {"startUrls": [{"url": "https://ornek.com"}]},
            memory_mbytes=1024,
            timeout_secs=300,
            max_items=50,
            max_total_charge_usd=1.5,
        )
        assert meta["id"] == "run1"
        args, kwargs = c.session.post.call_args
        assert "acts/apify/web-scraper/runs" in args[0]
        assert kwargs["json"] == {"startUrls": [{"url": "https://ornek.com"}]}
        q = kwargs["params"]
        assert q["memory"] == 1024
        assert q["timeout"] == 300
        assert q["maxItems"] == 50
        assert q["maxTotalChargeUsd"] == 1.5

    def test_http_hatasinda_apify_error(self) -> None:
        c = make_client()
        c.session.post.return_value = resp(401, {"error": {"message": "unauthorized"}})
        with pytest.raises(ApifyError, match="baslatilamadi"):
            c.start_actor_run("a/b")


class TestWaitForRun:
    def test_terminal_durumda_doner(self) -> None:
        c = make_client()
        c.session.get.return_value = resp(200, {"data": {"status": "SUCCEEDED"}})
        meta = c.wait_for_run("run1", poll_interval=0)
        assert meta["status"] == "SUCCEEDED"

    def test_failed_durumu_hatadir(self) -> None:
        c = make_client()
        c.session.get.return_value = resp(200, {"data": {"status": "FAILED"}})
        meta = c.wait_for_run("run1", poll_interval=0)
        assert meta["status"] == "FAILED"
        with pytest.raises(ApifyError, match="basarisiz"):
            c.run_actor_and_collect("a/b", poll_interval=0, poll_timeout=1)

    def test_polling_zaman_asimi(self) -> None:
        c = make_client()
        c.session.get.return_value = resp(200, {"data": {"status": "READY"}})
        with pytest.raises(ApifyError, match="zaman asimi"):
            c.wait_for_run("run1", poll_interval=0, poll_timeout=0.05)


class TestFetchDatasetItems:
    def test_tek_sayfa(self) -> None:
        c = make_client()
        c.session.get.return_value = resp(200, [{"a": 1}, {"a": 2}])
        items = c.fetch_dataset_items("ds1")
        assert items == [{"a": 1}, {"a": 2}]
        q = c.session.get.call_args[1]["params"]
        assert q["clean"] == "true"
        assert q["offset"] == 0

    def test_cok_sayfali_okuma(self) -> None:
        c = make_client()
        sayfa1 = [{"i": i} for i in range(1000)]
        c.session.get.side_effect = [
            resp(200, sayfa1),
            resp(200, [{"i": 1000}]),
        ]
        items = c.fetch_dataset_items("ds1")
        assert len(items) == 1001
        ikinci = c.session.get.call_args_list[1][1]["params"]
        assert ikinci["offset"] == 1000

    def test_max_items_siniri(self) -> None:
        c = make_client()
        c.session.get.return_value = resp(200, [{"i": i} for i in range(1000)])
        items = c.fetch_dataset_items("ds1", max_items=5)
        assert len(items) == 5


class TestRunActorAndCollect:
    def test_basarili_akis(self) -> None:
        c = make_client()
        c.session.post.return_value = resp(
            201, {"data": {"id": "run1", "defaultDatasetId": "ds1"}}
        )
        c.session.get.side_effect = [
            resp(200, {"data": {"status": "SUCCEEDED", "defaultDatasetId": "ds1"}}),
            resp(200, [{"url": "https://x.com", "title": "Stajyer"}]),
        ]
        items, meta = c.run_actor_and_collect("apify/web-scraper", poll_interval=0)
        assert items[0]["title"] == "Stajyer"
        assert meta["status"] == "SUCCEEDED"
        assert meta["id"] == "run1"
