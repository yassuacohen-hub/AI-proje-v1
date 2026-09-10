# -*- coding: utf-8 -*-
"""APIFY-02: Apify REST API adaptoru (polling tabanli pilot).

Tasarim kararları (bkz. V10/07_referanslar/10_apify_entegrasyon_arastirmasi_20260910.md):
- Uretim veri akisi REST + polling; MCP sadece arastirma/denetim icin.
- Token yalnizca ortam degiskeninden okunur (APIFY_TOKEN); loglara yazilmaz.
- Run kimligi/limitleri cagiran taraf tarafindan kaydedilir (kalici run takibi).
- Dataset sayfali okunur (limit/offset); tek istekte tum veri cekilmez.
- Izin/butce kontrolu bu modulun DIŞINDA (scraping_permission_router) yapilir;
  bu modul yalnizca transport saglar.

API referansi: https://docs.apify.com/api/v2
"""

from __future__ import annotations

import logging
import os
import time
from typing import Any

import requests

logger = logging.getLogger(__name__)

APIFY_API_BASE = "https://api.apify.com/v2"
DEFAULT_POLL_INTERVAL_S = 5.0
DEFAULT_POLL_TIMEOUT_S = 900.0
PAGE_LIMIT = 1000


class ApifyError(RuntimeError):
    """Apify REST cagrisi basarisiz oldugunda uretilir."""


class ApifyClient:
    """Apify Actor calistirma ve dataset okuma icin minimal REST istemcisi."""

    def __init__(
        self,
        token: str | None = None,
        api_base: str = APIFY_API_BASE,
        session: requests.Session | None = None,
    ) -> None:
        self.token = token or os.getenv("APIFY_TOKEN", "")
        if not self.token:
            raise ApifyError(
                "APIFY_TOKEN bos; token yalnizca ortam degiskeninden gelir."
            )
        self.api_base = api_base.rstrip("/")
        self.session = session or requests.Session()

    # ------------------------------------------------------------------
    # Actor calistirma
    # ------------------------------------------------------------------
    def start_actor_run(
        self,
        actor_id: str,
        run_input: dict[str, Any] | None = None,
        memory_mbytes: int | None = None,
        timeout_secs: int | None = None,
        max_items: int | None = None,
        max_total_charge_usd: float | None = None,
    ) -> dict[str, Any]:
        """Actor'u asenkron baslatir; run metadata dondurur.

        Maliyet/sure sinirlari iste gomulur; butce kontrolu cagiran tarafa aittir.
        """
        payload: dict[str, Any] = run_input or {}
        query: dict[str, Any] = {"token": self.token}
        if memory_mbytes is not None:
            query["memory"] = memory_mbytes
        if timeout_secs is not None:
            query["timeout"] = timeout_secs
        if max_items is not None:
            query["maxItems"] = max_items
        if max_total_charge_usd is not None:
            query["maxTotalChargeUsd"] = max_total_charge_usd
        url = f"{self.api_base}/acts/{actor_id}/runs"
        resp = self.session.post(url, json=payload, params=query)
        if resp.status_code not in (200, 201):
            raise ApifyError(
                f"Actor run baslatilamadi ({resp.status_code}): {resp.text[:300]}"
            )
        data = resp.json().get("data", {})
        logger.info(
            "Apify run baslatildi: actor=%s run_id=%s dataset=%s",
            actor_id,
            data.get("id"),
            data.get("defaultDatasetId"),
        )
        return data

    def wait_for_run(
        self,
        run_id: str,
        poll_interval: float = DEFAULT_POLL_INTERVAL_S,
        poll_timeout: float = DEFAULT_POLL_TIMEOUT_S,
    ) -> dict[str, Any]:
        """Run tamamlanana kadar polling yapar; son run metadata dondurur."""
        deadline = time.monotonic() + poll_timeout
        terminal = {"SUCCEEDED", "FAILED", "ABORTED", "TIMED_OUT"}
        url = f"{self.api_base}/actor-runs/{run_id}"
        while True:
            resp = self.session.get(url, params={"token": self.token})
            if resp.status_code != 200:
                raise ApifyError(
                    f"Run durumu alinamadi ({resp.status_code}): {resp.text[:300]}"
                )
            data = resp.json().get("data", {})
            status = data.get("status", "")
            if status in terminal:
                return data
            if time.monotonic() >= deadline:
                raise ApifyError(f"Run polling zaman asimi: run_id={run_id}")
            time.sleep(poll_interval)


    # ------------------------------------------------------------------
    # Dataset okuma
    # ------------------------------------------------------------------
    def fetch_dataset_items(
        self,
        dataset_id: str,
        clean: bool = True,
        max_items: int | None = None,
    ) -> list[dict[str, Any]]:
        """Dataset ogelerini sayfali olarak okur (limit/offset)."""
        items: list[dict[str, Any]] = []
        offset = 0
        limit = PAGE_LIMIT
        if max_items is not None:
            limit = min(limit, max_items)
        url = f"{self.api_base}/datasets/{dataset_id}/items"
        while True:
            params: dict[str, Any] = {
                "token": self.token,
                "clean": "true" if clean else "false",
                "limit": limit,
                "offset": offset,
            }
            resp = self.session.get(url, params=params)
            if resp.status_code != 200:
                raise ApifyError(
                    f"Dataset okunamadi ({resp.status_code}): {resp.text[:300]}"
                )
            page = resp.json()
            if not isinstance(page, list):
                raise ApifyError("Dataset yaniti liste beklenirken farkli tipte geldi.")
            items.extend(page)
            offset += len(page)
            if not page or len(page) < limit:
                break
            if max_items is not None and len(items) >= max_items:
                items = items[:max_items]
                break
        return items

    # ------------------------------------------------------------------
    # Yuksek seviye akis
    # ------------------------------------------------------------------
    def run_actor_and_collect(
        self,
        actor_id: str,
        run_input: dict[str, Any] | None = None,
        clean: bool = True,
        max_items: int | None = None,
        poll_interval: float = DEFAULT_POLL_INTERVAL_S,
        poll_timeout: float = DEFAULT_POLL_TIMEOUT_S,
        **run_kwargs: Any,
    ) -> tuple[list[dict[str, Any]], dict[str, Any]]:
        """Actor calistirir, tamamlanmasini bekler, dataset'i okur.

        Donus: (items, run_meta). run_meta; kalici run kaydi icin gerekli
        alanlari icerir (id, defaultDatasetId, status, startedAt, stats).
        """
        run_meta = self.start_actor_run(actor_id, run_input=run_input, **run_kwargs)
        run_id = run_meta.get("id")
        if not run_id:
            raise ApifyError("Run metadata icinde id yok.")
        final_meta = self.wait_for_run(
            run_id, poll_interval=poll_interval, poll_timeout=poll_timeout
        )
        if final_meta.get("status") != "SUCCEEDED":
            raise ApifyError(
                f"Run basarisiz: status={final_meta.get('status')} run_id={run_id}"
            )
        dataset_id = final_meta.get("defaultDatasetId") or run_meta.get(
            "defaultDatasetId"
        )
        if not dataset_id:
            raise ApifyError(f"Dataset kimligi bulunamadi: run_id={run_id}")
        items = self.fetch_dataset_items(dataset_id, clean=clean, max_items=max_items)
        return items, final_meta
