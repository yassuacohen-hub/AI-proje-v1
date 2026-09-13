# -*- coding: utf-8 -*-
"""P7-30: Proxy Rotator — Rotating proxy ve user-agent yoneticisi.

Kullanim:
    from src.company_master.utils.proxy_rotator import ProxyRotator
    rotator = ProxyRotator()
    proxy = rotator.get_proxy()
    ua = rotator.get_user_agent()
    rotator.rotate()
"""
from __future__ import annotations

import json
import logging
import random
import sys
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

DEFAULT_PROXIES: list[str] = []
DEFAULT_USER_AGENTS: list[str] = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0",
]


class ProxyRotator:
    """Proxy ve user-agent rotator.

    Ozellikler:
    - Rotating proxy listesi (SOCKS/HTTP)
    - User-Agent rotation
    - Auto-detection proxy listesi icin dosya
    """

    def __init__(
        self,
        proxies: list[str] | str | None = None,
        user_agents: list[str] | None = None,
    ) -> None:
        if isinstance(proxies, str):
            proxies = self._load_proxies_from_file(proxies)
        elif proxies is None:
            proxies = self._auto_detect_proxies()

        self.proxies: list[str] = proxies
        self._current_index: int = 0

        self.user_agents: list[str] = user_agents or DEFAULT_USER_AGENTS
        self._ua_index: int = random.randint(0, len(self.user_agents) - 1)

    @staticmethod
    def _load_proxies_from_file(path: str) -> list[str]:
        """Dosyadan proxy listesi yukle."""
        p = Path(path)
        if not p.exists():
            logger.warning("Proxy dosyasi bulunamadi: %s", path)
            return []
        lines = p.read_text(encoding="utf-8").strip().split("\n")
        return [l.strip() for l in lines if l.strip() and not l.strip().startswith("#")]

    @staticmethod
    def _auto_detect_proxies() -> list[str]:
        """Sistem proxy ayarlarini kontrol et."""
        proxies: list[str] = []
        for env_key in ("HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy"):
            import os
            val = os.environ.get(env_key)
            if val:
                proxies.append(val)
        return list(set(proxies))

    @property
    def current_proxy(self) -> str | None:
        """Mevcut proxy."""
        if not self.proxies:
            return None
        return self.proxies[self._current_index % len(self.proxies)]

    def get_proxy(self) -> dict[str, str] | None:
        """Mevcut proxy dondur (requests formati)."""
        proxy = self.current_proxy
        if proxy is None:
            return None
        self._current_index += 1
        return {"http": proxy, "https": proxy}

    def get_user_agent(self) -> str:
        """Mevcut user-agent dondur."""
        ua = self.user_agents[self._ua_index % len(self.user_agents)]
        self._ua_index += 1
        return ua

    def rotate(self) -> None:
        """Proxy ve user-agent dondur."""
        self._current_index = random.randint(0, max(len(self.proxies) - 1, 0))
        self._ua_index = random.randint(0, len(self.user_agents) - 1)
        logger.debug("Proxy/UA rotated")

    def add_proxy(self, proxy: str) -> None:
        """Yeni proxy ekle."""
        if proxy not in self.proxies:
            self.proxies.append(proxy)

    def remove_proxy(self, proxy: str) -> None:
        """Proxy cikar."""
        if proxy in self.proxies:
            self.proxies.remove(proxy)

    @property
    def status(self) -> dict[str, Any]:
        """Durum bilgisi."""
        return {
            "proxy_count": len(self.proxies),
            "current_index": self._current_index,
            "current_proxy": self.current_proxy,
            "user_agent_count": len(self.user_agents),
            "user_agents": self.user_agents,
        }
