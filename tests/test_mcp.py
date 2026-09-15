# -*- coding: utf-8 -*-
"""MCP-01/MCP-02: MCP Policy Engine, Apify Adapter, Huginn Server testleri."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from company_master.mcp.policy_engine import PolicyEngine  # noqa: E402
from company_master.mcp.apify_adapter import ApifyAdapter  # noqa: E402
from company_master.mcp.huginn_server import HuginnMCPServer  # noqa: E402
from company_master.engine.source_registry import registry  # noqa: E402


class TestSourceRegistry:
    def test_apify_source_enabled(self) -> None:
        """Apify kaynağının source_registry'de enabled=True olduğu doğrulanır."""
        specs = registry()
        assert "apify" in specs
        assert specs["apify"].enabled is True


class TestPolicyEngine:
    def test_default_allowed_actors(self) -> None:
        pe = PolicyEngine()
        assert "kariyer_net" in pe.allowed_actors
        assert "company_career" in pe.allowed_actors

    def test_wildcard_never_allowed(self) -> None:
        pe = PolicyEngine(allowed_tools=["apify_run_actor:*"])
        dec = pe.check_tool_allowed("apify_run_actor", "kariyer_net")
        assert dec.allowed is False
        assert "wildcard" in dec.reason.lower()

    def test_explicit_tool_allowed(self) -> None:
        pe = PolicyEngine()
        dec = pe.check_tool_allowed("apify_get_dataset")
        assert dec.allowed is True

    def test_actor_not_in_whitelist(self) -> None:
        pe = PolicyEngine()
        dec = pe.check_tool_allowed("apify_run_actor", "linkedin_scraper")
        assert dec.allowed is False
        assert "whitelist" in dec.reason or "değil" in dec.reason

    def test_wildcard_actor_explicit_rejected(self) -> None:
        pe = PolicyEngine()
        dec = pe.check_tool_allowed("apify_run_actor", "*")
        assert dec.allowed is False

    def test_spend_limit_enforced(self) -> None:
        pe = PolicyEngine(daily_spend_limit=10.0)
        dec = pe.check_spend("apify_run_actor", cost_credits=15.0)
        assert dec.allowed is False
        assert "limit" in dec.reason.lower()

    def test_spend_under_limit_allowed(self) -> None:
        pe = PolicyEngine(daily_spend_limit=10.0)
        dec = pe.check_spend("apify_run_actor", cost_credits=5.0)
        assert dec.allowed is True

    def test_data_limit_enforced(self) -> None:
        pe = PolicyEngine(max_dataset_rows=100)
        dec = pe.check_data_limit(150)
        assert dec.allowed is False
        assert "sınır" in dec.reason.lower() or "limit" in dec.reason.lower()

    def test_data_limit_under_allowed(self) -> None:
        pe = PolicyEngine(max_dataset_rows=100)
        dec = pe.check_data_limit(50)
        assert dec.allowed is True

    def test_nace_scope_filter_pass(self) -> None:
        pe = PolicyEngine(nace_scope=["62.01", "62.02"])
        dec = pe.check_nace_scope("62.01")
        assert dec.allowed is True

    def test_nace_scope_filter_fail(self) -> None:
        pe = PolicyEngine(nace_scope=["62.01", "62.02"])
        dec = pe.check_nace_scope("99.00")
        assert dec.allowed is False
        assert "scope" in dec.reason.lower() or "değil" in dec.reason

    def test_nace_empty_scope_allows_all(self) -> None:
        pe = PolicyEngine(nace_scope=[])
        dec = pe.check_nace_scope("anything")
        assert dec.allowed is True

    def test_approve_spend_logs(self, tmp_path, monkeypatch) -> None:
        monkeypatch.setattr(
            "company_master.mcp.policy_engine.SPEND_LOG", tmp_path / "spend.jsonl"
        )
        pe = PolicyEngine(daily_spend_limit=10.0)
        pe.approve_spend(
            "apify_run_actor", "kariyer_net", cost=2.5, metadata={"run_id": "r1"}
        )
        assert (tmp_path / "spend.jsonl").exists()
        entry = json.loads((tmp_path / "spend.jsonl").read_text())
        assert entry["cost_credits"] == 2.5
        assert entry["actor_id"] == "kariyer_net"

    def test_daily_spent_tracks_entries(self, tmp_path, monkeypatch) -> None:
        monkeypatch.setattr(
            "company_master.mcp.policy_engine.SPEND_LOG", tmp_path / "spend.jsonl"
        )
        pe = PolicyEngine(daily_spend_limit=10.0)
        pe.approve_spend("t1", None, cost=3.0)
        pe.approve_spend("t2", None, cost=2.0)
        assert pe._daily_spent() == 5.0

    def test_evaluate_all_pass(self) -> None:
        pe = PolicyEngine()
        dec = pe.evaluate(
            tool_name="apify_run_actor",
            actor_id="kariyer_net",
            cost_credits=0.5,
            max_rows=100,
            nace_code="62.01",
        )
        assert dec.allowed is True

    def test_evaluate_blocked_by_tool(self) -> None:
        pe = PolicyEngine()
        dec = pe.evaluate(
            tool_name="apify_run_actor",
            actor_id="blocked_actor",
        )
        assert dec.allowed is False

    def test_evaluate_blocked_by_spend(self) -> None:
        pe = PolicyEngine(daily_spend_limit=1.0)
        dec = pe.evaluate(
            tool_name="apify_run_actor", actor_id="kariyer_net", cost_credits=5.0
        )
        assert dec.allowed is False


class TestApifyAdapter:
    def test_list_tools(self) -> None:
        adapter = ApifyAdapter(policy_engine=PolicyEngine())
        assert "apify_run_actor" in adapter.list_tools()
        assert "apify_get_dataset" in adapter.list_tools()
        assert "apify_list_actors" in adapter.list_tools()
        assert "get_apify_source_spec" in adapter.list_tools()

    def test_apify_run_actor_denied_wildcard_actor(self) -> None:
        adapter = ApifyAdapter(policy_engine=PolicyEngine())
        result = adapter.apify_run_actor(actor_id="blocked_actor")
        assert result.success is False
        assert "whitelist" in result.error or "değil" in result.error

    def test_apify_run_actor_no_client(self) -> None:
        adapter = ApifyAdapter(
            policy_engine=PolicyEngine(),
            apify_client=None,
        )
        result = adapter.apify_run_actor(actor_id="kariyer_net")
        assert result.success is False
        assert "ApifyClient" in result.error or "yok" in result.error

    def test_apify_get_dataset_no_client(self) -> None:
        adapter = ApifyAdapter(
            policy_engine=PolicyEngine(),
            apify_client=None,
        )
        result = adapter.apify_get_dataset(dataset_id="ds123")
        assert result.success is False

    def test_apify_list_actors_returns_limits(self) -> None:
        adapter = ApifyAdapter(policy_engine=PolicyEngine(daily_spend_limit=10.0))
        result = adapter.apify_list_actors()
        assert result.success is True
        assert "allowed_actors" in result.data
        assert "daily_limit" in result.data

    def test_apify_run_actor_with_mock_client(self) -> None:
        mock_client = MagicMock()
        mock_client.start_actor_run.return_value = {
            "id": "run1",
            "defaultDatasetId": "ds1",
            "status": "SUCCEEDED",
        }
        mock_client.wait_for_run.return_value = {
            "status": "SUCCEEDED",
            "defaultDatasetId": "ds1",
        }
        mock_client.fetch_dataset_items.return_value = [{"title": "Job1"}]

        adapter = ApifyAdapter(
            policy_engine=PolicyEngine(),
            apify_client=mock_client,
        )
        result = adapter.apify_run_actor(actor_id="kariyer_net", max_items=10)
        assert result.success is True
        assert result.data["items_fetched"] == 1
        assert result.data["run_id"] == "run1"

    def test_apify_adapter_get_source_spec(self) -> None:
        """get_apify_source_spec method testi."""
        adapter = ApifyAdapter(policy_engine=PolicyEngine(), apify_client=None)
        result = adapter.get_apify_source_spec()
        assert result.success is True
        assert result.data["source_id"] == "apify"
        assert result.data["display_name"] == "Apify REST Adaptör"
        assert result.data["domain"] == "api.apify.com"
        assert result.data["enabled"] is True
        assert result.data["pipeline"] is True
        assert "output_file" in result.data
        assert "note" in result.data
        # Token asla döndürülmez
        assert "token" not in result.data
        assert "APIFY_TOKEN" not in str(result.data)

    def test_call_tool_dispatch(self) -> None:
        adapter = ApifyAdapter(policy_engine=PolicyEngine(), apify_client=None)
        result = adapter.call_tool("apify_list_actors", {})
        assert result["success"] is True
        assert "allowed_actors" in result["data"]

    def test_call_tool_unknown(self) -> None:
        adapter = ApifyAdapter(policy_engine=PolicyEngine(), apify_client=None)
        result = adapter.call_tool("unknown_tool", {})
        assert result["success"] is False
        assert "Unknown tool" in result["error"]

    def test_call_tool_get_apify_source_spec(self) -> None:
        """call_tool dispatch testi - get_apify_source_spec."""
        adapter = ApifyAdapter(policy_engine=PolicyEngine(), apify_client=None)
        result = adapter.call_tool("get_apify_source_spec", {})
        assert result["success"] is True
        assert result["data"]["source_id"] == "apify"


class TestHuginnMCPServer:
    def test_list_tools(self) -> None:
        server = HuginnMCPServer(policies=PolicyEngine())
        tools = server.list_tools()
        assert "get_source_policy" in tools
        assert "get_collection_run_status" in tools
        assert "submit_evidence_batch" in tools
        assert "report_collection_failure" in tools
        assert "list_sources" in tools

    def test_get_source_policy_existing(self) -> None:
        server = HuginnMCPServer()
        result = server.get_source_policy("apify")
        assert result.success is True
        assert result.data["source_id"] == "apify"
        assert "domain" in result.data

    def test_get_source_policy_unknown(self) -> None:
        server = HuginnMCPServer()
        result = server.get_source_policy("nonexistent-source")
        assert result.success is False
        assert "kayıtlı" in result.error or "bulunamadı" in result.error

    def test_get_collection_run_status_not_found(self) -> None:
        server = HuginnMCPServer()
        result = server.get_collection_run_status("UNKNOWN-RUN")
        assert result.success is False

    def test_submit_evidence_batch(self, tmp_path) -> None:
        evidence = [
            {"title": "Developer", "url": "https://x.com/1", "company": "Test Inc"},
            {"title": "Engineer", "url": "https://x.com/2", "company": "Test Inc"},
        ]
        with (
            patch("scripts.apify_webhook_receiver.ROOT", tmp_path)
            if False
            else patch("company_master.mcp.huginn_server.ROOT", tmp_path)
        ):
            server = HuginnMCPServer()
            result = server.submit_evidence_batch(evidence, source_id="test-source")
            assert result.success is True
            assert result.data["submitted"] == 2

    def test_submit_evidence_batch_empty(self) -> None:
        server = HuginnMCPServer()
        result = server.submit_evidence_batch([], source_id="test")
        assert result.success is False
        assert "boş" in result.error

    def test_report_collection_failure(self) -> None:
        server = HuginnMCPServer()
        result = server.report_collection_failure(
            source_id="kariyer-net",
            error="anti-bot blocked",
        )
        assert result.success is True
        assert result.data["source_id"] == "kariyer-net"

    def test_huginn_list_sources(self) -> None:
        """list_sources tool testi: tüm kaynaklar döner."""
        server = HuginnMCPServer()
        result = server.list_sources()
        assert result.success is True
        assert "sources" in result.data
        assert "count" in result.data
        assert result.data["count"] >= 1

        sources = result.data["sources"]
        source_ids = [s["source_id"] for s in sources]
        assert "apify" in source_ids
        assert "ostim-detail" in source_ids
        assert "aso" in source_ids

        for src in sources:
            assert "source_id" in src
            assert "display_name" in src
            assert "domain" in src
            assert "enabled" in src
            assert "pipeline" in src
            assert "note" in src

    def test_call_tool_dispatch(self) -> None:
        server = HuginnMCPServer()
        result = server.call_tool("get_source_policy", {"source_id": "apify"})
        assert result["success"] is True

    def test_huginn_call_tool_list_sources(self) -> None:
        """call_tool dispatch testi - list_sources."""
        server = HuginnMCPServer()
        result = server.call_tool("list_sources", {})
        assert result["success"] is True
        assert "sources" in result["data"]
        assert "count" in result["data"]
