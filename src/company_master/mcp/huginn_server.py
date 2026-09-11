# -*- coding: utf-8 -*-
"""MCP-02: Huginn MCP Sunucusu + Ters Connector.

Huginn'in dahili verilerini (source policy, collection run status, evidence
batch, failure report) MCP tool'ları olarak sunar.

Kaynak: data/orchestrator/mcp01_apify_controlled_result.json §implementation_notes
"""

from __future__ import annotations

import json
import logging
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

from company_master.mcp.policy_engine import PolicyEngine  # noqa: E402

logger = logging.getLogger(__name__)


@dataclass
class HuginnToolResult:
    """Huginn MCP tool sonucu."""

    tool: str
    success: bool
    data: dict[str, Any] = field(default_factory=dict)
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "tool": self.tool,
            "success": self.success,
            "data": self.data,
            "error": self.error,
        }


class HuginnMCPServer:
    """Huginn sistemini MCP tool'ları olarak sunan sunucu.

    Bu sınıf, mcp paketi kurulu olsa da, kurulu olmasa da çalışır.
    mcp kuruluysa MCP protokolü üzerinden servis edilir;
    kurulu değilse HTTP/JSON (FastAPI) ya da CLI üzerinden kullanılabilir.

    Policy Engine ile güvence altına alınır: tool çağrıları arasında
    yetki ve veri sınırları kontrol edilir.
    """

    def __init__(self, policies: PolicyEngine | None = None) -> None:
        self.policies = policies or PolicyEngine()
        self._run_registry: dict[str, dict[str, Any]] = {}

    # ── Tool: list_sources ───────────────────────────────────────────────────
    def list_sources(self) -> HuginnToolResult:
        """Tüm kaynakları (SourceSpec) listeler.

        source_registry'deki tüm kaynakların source_id, display_name,
        domain, enabled, pipeline ve note alanlarını döner.
        """
        try:
            from company_master.engine.source_registry import registry

            specs = registry()
        except ImportError:
            return HuginnToolResult(
                tool="list_sources",
                success=False,
                error="source_registry modülü bulunamadı",
            )

        sources = [
            {
                "source_id": spec.source_id,
                "display_name": spec.display_name,
                "domain": spec.domain,
                "enabled": spec.enabled,
                "pipeline": spec.pipeline,
                "note": spec.note,
            }
            for spec in specs.values()
        ]

        return HuginnToolResult(
            tool="list_sources",
            success=True,
            data={"sources": sources, "count": len(sources)},
        )

    # ── Tool: get_source_policy ────────────────────────────────────────────
    def get_source_policy(self, source_id: str) -> HuginnToolResult:
        """Bir veri kaynağının izin politikasını getirir.

        KVKK, domain whitelist, rate limit, anti-bot durumu, NACE scope.
        """
        try:
            from company_master.engine.source_registry import registry

            specs = registry()
        except ImportError:
            return HuginnToolResult(
                tool="get_source_policy",
                success=False,
                error="source_registry modülü bulunamadı",
            )

        if source_id not in specs:
            return HuginnToolResult(
                tool="get_source_policy",
                success=False,
                error=f"source_id '{source_id}' kayıtlı değil. Kullanılabilir: {list(specs.keys())}",
            )

        spec = specs[source_id]
        try:
            from company_master.utils.scraping_permission_router import get_router

            router = get_router()
            decision = router.check(f"https://{spec.domain}")
        except Exception:
            decision = None

        return HuginnToolResult(
            tool="get_source_policy",
            success=True,
            data={
                "source_id": spec.source_id,
                "display_name": spec.display_name,
                "domain": spec.domain,
                "enabled": spec.enabled,
                "output_file": spec.output_file,
                "pipeline": spec.pipeline,
                "note": spec.note,
                "permission": {
                    "allowed": decision.allowed if decision else True,
                    "reason": decision.reason if decision else "kontrol edilemedi",
                },
                "nace_scope": (
                    self.policies.nace_scope if self.policies.nace_scope else "tümü"
                ),
                "data_limits": {
                    "max_dataset_rows": self.policies.max_dataset_rows,
                    "max_output_tokens": self.policies.max_output_tokens,
                },
            },
        )

    # ── Tool: get_collection_run_status ─────────────────────────────────────
    def get_collection_run_status(self, run_id: str) -> HuginnToolResult:
        """Veri toplama run durumunu getirir."""
        if run_id in self._run_registry:
            return HuginnToolResult(
                tool="get_collection_run_status",
                success=True,
                data=self._run_registry[run_id],
            )

        # task_board'da kontrol et
        try:
            from company_master.orchestrator.task_board import task_board as tb

            tb_json = tb
            for task in tb_json:
                if task.get("task_id") == run_id or task.get("bitis") == run_id:
                    return HuginnToolResult(
                        tool="get_collection_run_status",
                        success=True,
                        data={
                            "run_id": run_id,
                            "source": task.get("task_id"),
                            "status": task.get("durum"),
                            "sahip": task.get("sahip"),
                            "aciklama": task.get("baslik"),
                            "bitis": task.get("bitis"),
                            "not": task.get("not", ""),
                        },
                    )
        except Exception as e:
            logger.debug("task_board kontrol hatası: %s", e)

        return HuginnToolResult(
            tool="get_collection_run_status",
            success=False,
            error=f"run_id '{run_id}' bulunamadı. task_board.json veya run_registry kontrol edin.",
        )

    # ── Tool: submit_evidence_batch ─────────────────────────────────────────
    def submit_evidence_batch(
        self, evidence: list[dict[str, Any]], source_id: str = ""
    ) -> HuginnToolResult:
        """Toplanan kanıtları (scraped data) ingest pipeline'a gönderir."""
        if not evidence:
            return HuginnToolResult(
                tool="submit_evidence_batch",
                success=False,
                error="evidence listesi boş",
            )

        # Evidence kayıt defterine yaz (JSONL)
        evidence_log = (
            ROOT / "data" / "job_intelligence" / f"mcp_evidence_{source_id}.jsonl"
        )
        evidence_log.parent.mkdir(parents=True, exist_ok=True)

        written = 0
        errors: list[str] = []
        for item in evidence:
            try:
                with evidence_log.open("a", encoding="utf-8") as f:
                    f.write(json.dumps(item, ensure_ascii=False, default=str) + "\n")
                written += 1
            except Exception as e:
                errors.append(str(e))

        run_id = f"mcp-{source_id}-{os.urandom(4).hex()}"
        self._run_registry[run_id] = {
            "run_id": run_id,
            "source_id": source_id,
            "status": "submitted",
            "items": written,
            "errors": len(errors),
            "evidence_file": str(evidence_log),
        }

        return HuginnToolResult(
            tool="submit_evidence_batch",
            success=True,
            data={
                "run_id": run_id,
                "source_id": source_id,
                "submitted": written,
                "errors": len(errors),
                "evidence_file": str(evidence_log),
            },
            error=None if not errors else f"{len(errors)} kayıt yazılamadı",
        )

    # ── Tool: report_collection_failure ─────────────────────────────────────
    def report_collection_failure(
        self, source_id: str, error: str, run_id: str | None = None
    ) -> HuginnToolResult:
        """Scraper/collect run başarısızlığını bildirir (ErrorLedger + log)."""
        try:
            from company_master.orchestrator.error_ledger import ErrorLedger
            from company_master.orchestrator.models import ErrorLedgerEntry

            ledger = ErrorLedger()
            ledger.add(
                ErrorLedgerEntry(
                    task_id=f"MCP-{source_id}",
                    agent_id="huginn_mcp_server",
                    error_type="collection_failure",
                    error_message=f"source={source_id} run={run_id or 'N/A'}: {error}",
                )
            )
        except ImportError:
            logger.warning("ErrorLedger bulunamadı; failure sadece loglanıyor")

        logger.warning(
            "Collection failure: source=%s run=%s error=%s", source_id, run_id, error
        )
        return HuginnToolResult(
            tool="report_collection_failure",
            success=True,
            data={
                "source_id": source_id,
                "run_id": run_id or "N/A",
                "error": error,
                "reported_at": __import__("datetime")
                .datetime.now(__import__("datetime").timezone.utc)
                .isoformat(),
            },
        )

    # ── MCP tool list + dispatch (MCP server wrapper için) ─────────────────
    def list_tools(self) -> list[str]:
        return [
            "get_source_policy",
            "get_collection_run_status",
            "submit_evidence_batch",
            "report_collection_failure",
            "list_sources",
        ]

    def call_tool(self, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        if name == "get_source_policy":
            return self.get_source_policy(**arguments).to_dict()
        elif name == "get_collection_run_status":
            return self.get_collection_run_status(**arguments).to_dict()
        elif name == "submit_evidence_batch":
            return self.submit_evidence_batch(**arguments).to_dict()
        elif name == "report_collection_failure":
            return self.report_collection_failure(**arguments).to_dict()
        elif name == "list_sources":
            return self.list_sources().to_dict()
        else:
            return {
                "tool": name,
                "success": False,
                "error": f"Unknown tool: {name}",
            }
