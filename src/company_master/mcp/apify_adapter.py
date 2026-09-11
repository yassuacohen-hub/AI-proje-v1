# -*- coding: utf-8 -*-
"""MCP-01: Apify MCP Adapter — Apify'ı kontrollü MCP tool seti olarak sunar.

Policy Engine ile korunur: sadece whitelist'teki actor'lar çalıştırılabilir,
harcama limiti vardır, veri sınırları uygulanır.

Kaynak: data/orchestrator/mcp01_apify_controlled_result.json
"""

from __future__ import annotations

import logging
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

from company_master.mcp.policy_engine import PolicyEngine  # noqa: E402

try:
    from company_master.intelligence.job_intelligence.sources.apify_client import (  # noqa: E402
        ApifyClient,
        ApifyError,
    )
except ImportError:
    ApifyClient = None  # type: ignore[assignment]
    ApifyError = RuntimeError  # type: ignore[assignment]

logger = logging.getLogger(__name__)


@dataclass
class ApifyToolResult:
    """MCP tool çağrısı sonucu."""

    tool: str
    success: bool
    data: dict[str, Any] = field(default_factory=dict)
    error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "tool": self.tool,
            "success": self.success,
            "data": self.data,
            "error": self.error,
            "metadata": self.metadata,
        }


class ApifyAdapter:
    """Apify'ı MCP tool'ları olarak sunar.

    MCP protokolü yerine, bu sınıf tool'ları method olarak sunar;
    dışarıdan bir MCP server wrapper'ı bu metodları MCP tool'larına
    dönüştürebilir (mcp paketi kuruluysa).
    """

    def __init__(
        self,
        policy_engine: PolicyEngine | None = None,
        apify_client: ApifyClient | None = None,
    ) -> None:
        self.policies = policy_engine or PolicyEngine()
        self.client = apify_client

        if self.client is None:
            token = os.getenv("APIFY_TOKEN")
            if token:
                try:
                    self.client = ApifyClient(token=token)
                except (ApifyError, Exception):
                    logger.warning(
                        "ApifyClient initialize edilemedi; tools mock/readonly modda çalışır"
                    )

    # ── Tool: apify_run_actor ──────────────────────────────────────────────
    def apify_run_actor(
        self,
        actor_id: str,
        run_input: dict[str, Any] | None = None,
        max_items: int | None = None,
        max_charge_usd: float | None = None,
    ) -> ApifyToolResult:
        """Whitelist'teki bir Apify actor'ını çalıştırır.

        Wildcard (apify_run_actor:*) asla onaylanmaz.
        """
        decision = self.policies.evaluate(
            tool_name="apify_run_actor",
            actor_id=actor_id,
            cost_credits=max_charge_usd or 0.5,
            max_rows=max_items or 0,
        )
        if not decision.allowed:
            return ApifyToolResult(
                tool="apify_run_actor",
                success=False,
                error=decision.reason,
            )

        if self.client is None:
            return ApifyToolResult(
                tool="apify_run_actor",
                success=False,
                error="ApifyClient yok (APIFY_TOKEN eksik)",
            )

        try:
            run_meta = self.client.start_actor_run(
                actor_id=actor_id,
                run_input=run_input or {},
                max_items=max_items,
                max_total_charge_usd=max_charge_usd,
            )
            final_meta = self.client.wait_for_run(run_meta.get("id", ""))
            items = self.client.fetch_dataset_items(
                dataset_id=run_meta.get("defaultDatasetId", ""),
                max_items=max_items,
            )

            self.policies.approve_spend(
                "apify_run_actor",
                actor_id,
                cost=max_charge_usd or 0.5,
                metadata={"run_id": run_meta.get("id"), "items": len(items)},
            )

            return ApifyToolResult(
                tool="apify_run_actor",
                success=True,
                data={
                    "actor_id": actor_id,
                    "run_id": run_meta.get("id"),
                    "status": final_meta.get("status"),
                    "items_fetched": len(items),
                    "items": items[:10],
                    "dataset_id": run_meta.get("defaultDatasetId"),
                },
                metadata={
                    "allowed_actors": self.policies.allowed_actors,
                    "daily_spend_remaining": decision.spend_remaining,
                },
            )
        except (ApifyError, Exception) as e:
            return ApifyToolResult(
                tool="apify_run_actor",
                success=False,
                error=str(e),
            )

    # ── Tool: apify_get_dataset ────────────────────────────────────────────
    def apify_get_dataset(
        self,
        dataset_id: str,
        max_items: int | None = None,
        clean: bool = True,
    ) -> ApifyToolResult:
        """Apify dataset'ini okur (policy kontrolü ile)."""
        decision = self.policies.evaluate(
            tool_name="apify_get_dataset",
            cost_credits=0.0,
            max_rows=max_items or 0,
        )
        if not decision.allowed:
            return ApifyToolResult(
                tool="apify_get_dataset",
                success=False,
                error=decision.reason,
            )

        if self.client is None:
            return ApifyToolResult(
                tool="apify_get_dataset",
                success=False,
                error="ApifyClient yok",
            )

        try:
            items = self.client.fetch_dataset_items(
                dataset_id=dataset_id,
                max_items=max_items,
                clean=clean,
            )
            return ApifyToolResult(
                tool="apify_get_dataset",
                success=True,
                data={
                    "dataset_id": dataset_id,
                    "count": len(items),
                    "items": items[:100],
                },
                metadata={"max_rows_remaining": decision.data_remaining},
            )
        except (ApifyError, Exception) as e:
            return ApifyToolResult(
                tool="apify_get_dataset",
                success=False,
                error=str(e),
            )

    # ── Tool: apify_list_actors ─────────────────────────────────────────────
    def apify_list_actors(self) -> ApifyToolResult:
        """Whitelist'teki actor'ları listeler (credential vermez)."""
        return ApifyToolResult(
            tool="apify_list_actors",
            success=True,
            data={
                "allowed_actors": self.policies.allowed_actors,
                "allowed_tools": list(self.policies.allowed_tools),
                "daily_limit": self.policies.daily_spend_limit,
                "daily_spent": self.policies._daily_spent(),
                "monthly_limit": self.policies.monthly_spend_limit,
                "monthly_spent": self.policies._monthly_spent(),
            },
        )

    # ── Tool: get_apify_source_spec ─────────────────────────────────────────
    def get_apify_source_spec(self) -> ApifyToolResult:
        """Apify kaynağının SourceSpec kaydını döner.

        source_registry'den apify spec'ini getirir; token gereksinimini
        duyurur (gerçek token asla döndürülmez).
        """
        try:
            from company_master.engine.source_registry import registry

            specs = registry()
        except ImportError:
            return ApifyToolResult(
                tool="get_apify_source_spec",
                success=False,
                error="source_registry modülü bulunamadı",
            )

        if "apify" not in specs:
            return ApifyToolResult(
                tool="get_apify_source_spec",
                success=False,
                error="apify kaynağı source_registry'de bulunamadı",
            )

        spec = specs["apify"]
        return ApifyToolResult(
            tool="get_apify_source_spec",
            success=True,
            data={
                "source_id": spec.source_id,
                "display_name": spec.display_name,
                "domain": spec.domain,
                "enabled": spec.enabled,
                "pipeline": spec.pipeline,
                "output_file": spec.output_file,
                "note": spec.note,
            },
        )

    # ── MCP tool listesi (opt-in) ──────────────────────────────────────────
    def list_tools(self) -> list[str]:
        """MCP server için tool isimleri."""
        return [
            "apify_run_actor",
            "apify_get_dataset",
            "apify_list_actors",
            "get_apify_source_spec",
        ]

    def call_tool(self, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        """Tool'u isim + argümanlarla çağırır (MCP server wrapper için)."""
        if name == "apify_run_actor":
            return self.apify_run_actor(**arguments).to_dict()
        elif name == "apify_get_dataset":
            return self.apify_get_dataset(**arguments).to_dict()
        elif name == "apify_list_actors":
            return self.apify_list_actors().to_dict()
        elif name == "get_apify_source_spec":
            return self.get_apify_source_spec().to_dict()
        else:
            return {
                "tool": name,
                "success": False,
                "error": f"Unknown tool: {name}. Use list_tools() to see available.",
            }
