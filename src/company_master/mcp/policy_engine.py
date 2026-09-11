# -*- coding: utf-8 -*-
"""MCP-01: Kontrollü Apify MCP Erişimi — Policy Engine.

Ajanların Apify'ı kullanan MCP tool'larına erişimini kontrol eder.
- Tool whitelist (wildcard engeli: apify_run_actor:* yasak)
- Günlük/aylık harcama limiti (Apify credits)
- Veri limitleri: max dataset rows, max output tokens, NACE scope

Kaynak: data/orchestrator/mcp01_apify_controlled_result.json §findings
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
_SPEND_LOG_ENV = os.environ.get("MCP_SPEND_LOG", "")
SPEND_LOG = (
    Path(_SPEND_LOG_ENV)
    if _SPEND_LOG_ENV
    else ROOT / "data" / "orchestrator" / "mcp_spend_log.jsonl"
)
SPEND_LOG.parent.mkdir(parents=True, exist_ok=True)


@dataclass
class PolicyDecision:
    """Policy Engine kararı."""

    allowed: bool
    reason: str = ""
    tool_name: str = ""
    actor_id: str | None = None
    spend_remaining: float | None = None
    data_remaining: int | None = None


@dataclass
class SpendEntry:
    """Harcama günlüğü kaydı."""

    tool_name: str
    actor_id: str | None
    cost_credits: float
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "tool_name": self.tool_name,
            "actor_id": self.actor_id,
            "cost_credits": self.cost_credits,
            "timestamp": self.timestamp,
            "metadata": self.metadata,
        }


class PolicyEngine:
    """Apify MCP tool'ları için yetki ve harcama kontrolü.

    Design (MCP-01 research):
    - allowed_tools: explicit allowlist, wildcard 'apify_run_actor:*' RED
    - spend_approval: günlük/apı maksimum harcama (Apify credits)
    - data_limits: max dataset rows, max output tokens, NACE scope
    """

    DEFAULT_ALLOWED_ACTORS = [
        "kariyer_net",
        "company_career",
    ]

    def __init__(
        self,
        allowed_tools: list[str] | None = None,
        allowed_actors: list[str] | None = None,
        daily_spend_limit: float = 5.0,
        monthly_spend_limit: float = 150.0,
        max_dataset_rows: int = 10000,
        max_output_tokens: int = 50000,
        nace_scope: list[str] | None = None,
    ) -> None:
        """
        Args:
            allowed_tools: Explicit tool whitelist (örn: ["apify_run_actor:kariyer_net", "apify_get_dataset"]).
                           Boş bırakılırsa DEFAULT_ALLOWED_ACTORS'dan otomatik üretilir.
            allowed_actors: Actor ID whitelist (örn: ["kariyer_net", "company_career"]).
                            apify_run_actor:{actor_id} olarak whitelist'e eklenir.
            daily_spend_limit: Günlük Apify credit harcama limiti.
            monthly_spend_limit: Aylık Apify credit harcama limiti.
            max_dataset_rows: Tek seferde maks dataset satır sayısı.
            max_output_tokens: Tek seferde maks token çıktısı.
            nace_scope: İzin verilen NACE kodları (örn: ["62.01", "62.02"]).
        """
        self.allowed_actors = allowed_actors or self.DEFAULT_ALLOWED_ACTORS[:]
        self.daily_spend_limit = daily_spend_limit
        self.monthly_spend_limit = monthly_spend_limit
        self.max_dataset_rows = max_dataset_rows
        self.max_output_tokens = max_output_tokens
        self.nace_scope = nace_scope or []

        if allowed_tools:
            self.allowed_tools = set(allowed_tools)
        else:
            self.allowed_tools = set()
            for actor in self.allowed_actors:
                self.allowed_tools.add(f"apify_run_actor:{actor}")
            self.allowed_tools.add("apify_get_dataset")
            self.allowed_tools.add("apify_list_actors")

    def _load_spend_log(self) -> list[dict[str, Any]]:
        """Spend log JSONL'yi okur."""
        if not SPEND_LOG.exists():
            return []
        entries: list[dict[str, Any]] = []
        try:
            for line in SPEND_LOG.read_text(encoding="utf-8").splitlines():
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
        except OSError:
            return []
        return entries

    def _daily_spent(self) -> float:
        """Bugüne kadar harcanılan toplam credit."""
        today = datetime.now(timezone.utc).date().isoformat()
        total = 0.0
        for entry in self._load_spend_log():
            if entry.get("timestamp", "").startswith(today):
                total += entry.get("cost_credits", 0.0)
        return total

    def _monthly_spent(self) -> float:
        """Bu aya kadar harcanılan toplam credit."""
        month = datetime.now(timezone.utc).date().isoformat()[:7]
        total = 0.0
        for entry in self._load_spend_log():
            if entry.get("timestamp", "").startswith(month):
                total += entry.get("cost_credits", 0.0)
        return total

    def _append_spend_log(self, entry: SpendEntry) -> None:
        """Spend log'a yeni kayıt ekler."""
        with SPEND_LOG.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry.to_dict(), ensure_ascii=False) + "\n")

    def check_tool_allowed(
        self, tool_name: str, actor_id: str | None = None
    ) -> PolicyDecision:
        """Tool + actor whitelist kontrolü.

        Wildcard kuralı: 'apify_run_actor:*' asla onaylanmaz.
        """
        # Wildcard engeli
        if "apify_run_actor:*" in self.allowed_tools:
            return PolicyDecision(
                allowed=False,
                reason="Wildcard apify_run_actor:* güvenlik nedeniyle engellendi",
                tool_name=tool_name,
            )

        # Explicit tool_name kontrol
        if tool_name in self.allowed_tools:
            return PolicyDecision(
                allowed=True,
                tool_name=tool_name,
                actor_id=actor_id,
                spend_remaining=self.daily_spend_limit - self._daily_spent(),
                data_remaining=self.max_dataset_rows,
            )

        # apify_run_actor:{actor_id} formatı (her actor ayrı onay)
        if tool_name == "apify_run_actor" and actor_id:
            full_tool = f"apify_run_actor:{actor_id}"
            if full_tool in self.allowed_tools:
                return PolicyDecision(
                    allowed=True,
                    tool_name=tool_name,
                    actor_id=actor_id,
                    spend_remaining=self.daily_spend_limit - self._daily_spent(),
                    data_remaining=self.max_dataset_rows,
                )
            return PolicyDecision(
                allowed=False,
                reason=f"Actor '{actor_id}' whitelist'te değil. İzin verilenler: {self.allowed_actors}",
                tool_name=tool_name,
                actor_id=actor_id,
            )

        return PolicyDecision(
            allowed=False,
            reason=f"Tool '{tool_name}' whitelist'te değil",
            tool_name=tool_name,
        )

    def check_spend(self, tool_name: str, cost_credits: float = 0.0) -> PolicyDecision:
        """Harcama limiti kontrolü."""
        daily_remaining = self.daily_spend_limit - self._daily_spent()
        monthly_remaining = self.monthly_spend_limit - self._monthly_spent()

        if cost_credits > 0:
            if daily_remaining < cost_credits:
                return PolicyDecision(
                    allowed=False,
                    reason=f"Günlük harcama limiti aşıldı: {cost_credits:.2f} > {daily_remaining:.2f} kalan",
                    tool_name=tool_name,
                    spend_remaining=daily_remaining,
                )
            if monthly_remaining < cost_credits:
                return PolicyDecision(
                    allowed=False,
                    reason=f"Aylık harcama limiti aşıldı: {cost_credits:.2f} > {monthly_remaining:.2f} kalan",
                    tool_name=tool_name,
                    spend_remaining=monthly_remaining,
                )

        return PolicyDecision(
            allowed=True,
            tool_name=tool_name,
            spend_remaining=daily_remaining,
            data_remaining=self.max_dataset_rows,
        )

    def check_data_limit(self, requested_rows: int) -> PolicyDecision:
        """Veri sınırı kontrolü."""
        if requested_rows > self.max_dataset_rows:
            return PolicyDecision(
                allowed=False,
                reason=f"Satır sınırı aşıldı: {requested_rows} > {self.max_dataset_rows}",
                data_remaining=self.max_dataset_rows,
            )
        return PolicyDecision(
            allowed=True,
            data_remaining=self.max_dataset_rows - requested_rows,
        )

    def check_nace_scope(self, nace_code: str | None) -> PolicyDecision:
        """NACE kodu scope kontrolü."""
        if not self.nace_scope or not nace_code:
            return PolicyDecision(
                allowed=True, reason="NACE scope boş; tüm veriler onaylı"
            )
        nace_prefix = nace_code[:2]
        if nace_code in self.nace_scope or any(
            nace_prefix == allowed[:2] for allowed in self.nace_scope
        ):
            return PolicyDecision(allowed=True)
        return PolicyDecision(
            allowed=False,
            reason=f"NACE kodu '{nace_code}' scope'de değil. İzin: {self.nace_scope}",
        )

    def approve_spend(
        self,
        tool_name: str,
        actor_id: str | None,
        cost: float,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Harcamayı loglar (approval kaydı)."""
        if cost > 0:
            entry = SpendEntry(
                tool_name=tool_name,
                actor_id=actor_id,
                cost_credits=cost,
                metadata=metadata or {},
            )
            self._append_spend_log(entry)

    def evaluate(
        self,
        tool_name: str,
        actor_id: str | None = None,
        cost_credits: float = 0.0,
        max_rows: int = 0,
        nace_code: str | None = None,
    ) -> PolicyDecision:
        """Tüm policy kurallarını tek seferde değerlendirir."""
        # 1. Tool whitelist
        tool_decision = self.check_tool_allowed(tool_name, actor_id)
        if not tool_decision.allowed:
            return tool_decision

        # 2. Spend limit
        spend_decision = self.check_spend(tool_name, cost_credits)
        if not spend_decision.allowed:
            return spend_decision

        # 3. Data limit
        if max_rows > 0:
            data_decision = self.check_data_limit(max_rows)
            if not data_decision.allowed:
                return data_decision

        # 4. NACE scope
        nace_decision = self.check_nace_scope(nace_code)
        if not nace_decision.allowed:
            return nace_decision

        return PolicyDecision(
            allowed=True,
            tool_name=tool_name,
            actor_id=actor_id,
            spend_remaining=spend_decision.spend_remaining,
            data_remaining=(
                data_decision.data_remaining if max_rows > 0 else self.max_dataset_rows
            ),
        )
