# -*- coding: utf-8 -*-
"""Huginn MCP (Model Context Protocol) entegrasyon modülü.

Bu paket, Apify ve Huginn sistemlerini MCP protokolü üzerinden ajanlara
sunar. MCP paketi (`pip install mcp`) opsiyoneldir; core logic
framework-agnostic çalışır.

Bileşenler:
  - PolicyEngine: araç whitelist + harcama limiti + veri sınırları
  - ApifyAdapter: Apify'ı MCP tool set olarak sunar (kontrollü)
  - huginn_server: Huginn verilerini MCP server olarak sunar
  - mcp_server_entry: mcp paketi ile gerçek MCP server (stdio + HTTP)

Kaynak: data/orchestrator/mcp01_apify_controlled_result.json
"""

from __future__ import annotations

from .policy_engine import PolicyEngine, PolicyDecision
from .apify_adapter import ApifyAdapter, ApifyToolResult
from .huginn_server import HuginnMCPServer

__all__ = [
    "PolicyEngine",
    "PolicyDecision",
    "ApifyAdapter",
    "ApifyToolResult",
    "HuginnMCPServer",
]
