# -*- coding: utf-8 -*-
"""MCP-03: Transport integration tests for HuginnMCPServer + ApifyAdapter.

Tests the real MCP protocol (JSON-RPC 2.0) over two transports:
  1. stdio  - subprocess spawned server, connected via mcp.client.stdio
  2. HTTP   - Streamable HTTP server, connected via mcp.client.streamable_http

Requires: pip install mcp (installed as part of MCP-03 task).

Run: PYTHONPATH=src pytest tests/test_mcp_transport.py -v -s
"""

from __future__ import annotations

import asyncio
import json
import os
import socket
import sys
import threading
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

pytest.importorskip("mcp")

from mcp import StdioServerParameters  # noqa: E402
from mcp import ClientSession  # noqa: E402
from mcp.client.stdio import stdio_client  # noqa: E402
from mcp.client.streamable_http import streamable_http_client  # noqa: E402

from company_master.mcp.mcp_server_entry import create_mcp_server  # noqa: E402


EXPECTED_TOOLS = [
    "apify_list_actors",
    "apify_run_actor",
    "apify_get_dataset",
    "get_source_policy",
    "get_collection_run_status",
    "submit_evidence_batch",
    "report_collection_failure",
]


def _find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _env() -> dict[str, str]:
    env = dict(os.environ)
    src_path = str(ROOT / "src")
    env["PYTHONPATH"] = src_path + os.pathsep + env.get("PYTHONPATH", "")
    # Isolate subprocess tests from the real persistent spend log.
    env["MCP_SPEND_LOG"] = str(ROOT / "data" / "orchestrator" / "mcp_spend_test.jsonl")
    return env


def _server_params() -> StdioServerParameters:
    return StdioServerParameters(
        command=sys.executable,
        args=["-m", "company_master.mcp.mcp_server_entry", "stdio"],
        env=_env(),
    )


def _extract_result(result) -> dict:
    """Extract structured content or parse text from CallToolResult."""
    if getattr(result, "structured_content", None) is not None:
        return result.structured_content
    if result.content:
        text = result.content[0].text
        try:
            return json.loads(text)
        except (json.JSONDecodeError, AttributeError):
            return {"raw": text}
    return {}


def _wait_for_port(port: int, timeout: float = 10.0) -> None:
    start = time.time()
    while time.time() - start < timeout:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                s.connect(("127.0.0.1", port))
                return
        except (ConnectionRefusedError, socket.timeout, OSError):
            time.sleep(0.2)
    raise TimeoutError(f"Port {port} did not open within {timeout}s")


class _HTTPServerRunner:
    """Starts an MCP Streamable HTTP server in a background daemon thread."""

    def __init__(self, port: int):
        self.port = port
        self._uvicorn_server = None
        self._thread: threading.Thread | None = None

    def __enter__(self):
        import uvicorn  # noqa: PLC0415

        server = create_mcp_server(path="/mcp")
        starlette_app = server.streamable_http_app()
        config = uvicorn.Config(
            starlette_app,
            host="127.0.0.1",
            port=self.port,
            log_level="warning",
            access_log=False,
        )
        self._uvicorn_server = uvicorn.Server(config)

        def _run():
            self._uvicorn_server.run()

        self._thread = threading.Thread(target=_run, daemon=True)
        self._thread.start()
        _wait_for_port(self.port)
        return self

    def __exit__(self, *exc):
        if self._uvicorn_server:
            self._uvicorn_server.should_exit = True


# ── stdio transport tests ────────────────────────────────────────────────────

class TestStdioTransport:
    """MCP-03: Test HuginnMCPServer + ApifyAdapter over stdio transport."""

    def test_stdio_list_tools(self):
        async def run():
            async with stdio_client(_server_params()) as (r, w):
                async with ClientSession(r, w) as session:
                    await session.initialize()
                    result = await session.list_tools()
                    return [t.name for t in result.tools]

        tool_names = asyncio.run(asyncio.wait_for(run(), timeout=30))
        assert sorted(tool_names) == sorted(EXPECTED_TOOLS)

    def test_stdio_apify_list_actors(self):
        async def run():
            async with stdio_client(_server_params()) as (r, w):
                async with ClientSession(r, w) as session:
                    await session.initialize()
                    result = await session.call_tool("apify_list_actors", {})
                    return _extract_result(result)

        data = asyncio.run(asyncio.wait_for(run(), timeout=30))
        assert data["success"] is True
        assert "kariyer_net" in data["data"]["allowed_actors"]
        assert "daily_limit" in data["data"]

    def test_stdio_apify_run_actor_denied(self):
        async def run():
            async with stdio_client(_server_params()) as (r, w):
                async with ClientSession(r, w) as session:
                    await session.initialize()
                    result = await session.call_tool(
                        "apify_run_actor", {"actor_id": "blocked_actor"}
                    )
                    return _extract_result(result)

        data = asyncio.run(asyncio.wait_for(run(), timeout=30))
        assert data["success"] is False
        assert "whitelist" in data["error"] or "değil" in data["error"]

    def test_stdio_apify_run_actor_no_client(self):
        async def run():
            async with stdio_client(_server_params()) as (r, w):
                async with ClientSession(r, w) as session:
                    await session.initialize()
                    result = await session.call_tool(
                        "apify_run_actor", {"actor_id": "kariyer_net"}
                    )
                    return _extract_result(result)

        data = asyncio.run(asyncio.wait_for(run(), timeout=30))
        assert data["success"] is False
        assert "ApifyClient" in data["error"] or "yok" in data["error"]

    def test_stdio_get_source_policy_existing(self):
        async def run():
            async with stdio_client(_server_params()) as (r, w):
                async with ClientSession(r, w) as session:
                    await session.initialize()
                    result = await session.call_tool(
                        "get_source_policy", {"source_id": "apify"}
                    )
                    return _extract_result(result)

        data = asyncio.run(asyncio.wait_for(run(), timeout=30))
        assert data["success"] is True
        assert data["data"]["source_id"] == "apify"
        assert "domain" in data["data"]

    def test_stdio_get_source_policy_unknown(self):
        async def run():
            async with stdio_client(_server_params()) as (r, w):
                async with ClientSession(r, w) as session:
                    await session.initialize()
                    result = await session.call_tool(
                        "get_source_policy", {"source_id": "nonexistent-src"}
                    )
                    return _extract_result(result)

        data = asyncio.run(asyncio.wait_for(run(), timeout=30))
        assert data["success"] is False

    def test_stdio_submit_evidence_batch(self):
        evidence = [
            {"title": "MCP Test Job", "url": "https://example.com/job/1", "company": "Test Co"},
        ]
        try:
            async def run():
                async with stdio_client(_server_params()) as (r, w):
                    async with ClientSession(r, w) as session:
                        await session.initialize()
                        result = await session.call_tool(
                            "submit_evidence_batch",
                            {"evidence": evidence, "source_id": "transport_test"},
                        )
                        return _extract_result(result)

            data = asyncio.run(asyncio.wait_for(run(), timeout=30))
            assert data["success"] is True
            assert data["data"]["submitted"] == 1
            assert data["data"]["errors"] == 0
            assert "run_id" in data["data"]
        finally:
            evidence_file = ROOT / "data" / "job_intelligence" / "mcp_evidence_transport_test.jsonl"
            if evidence_file.exists():
                evidence_file.unlink()

    def test_stdio_submit_evidence_batch_empty(self):
        async def run():
            async with stdio_client(_server_params()) as (r, w):
                async with ClientSession(r, w) as session:
                    await session.initialize()
                    result = await session.call_tool(
                        "submit_evidence_batch",
                        {"evidence": [], "source_id": "empty_test"},
                    )
                    return _extract_result(result)

        data = asyncio.run(asyncio.wait_for(run(), timeout=30))
        assert data["success"] is False
        assert "boş" in data["error"]

    def test_stdio_report_collection_failure(self):
        async def run():
            async with stdio_client(_server_params()) as (r, w):
                async with ClientSession(r, w) as session:
                    await session.initialize()
                    result = await session.call_tool(
                        "report_collection_failure",
                        {"source_id": "transport_test", "error": "timeout"},
                    )
                    return _extract_result(result)

        data = asyncio.run(asyncio.wait_for(run(), timeout=30))
        assert data["success"] is True
        assert data["data"]["source_id"] == "transport_test"
        assert data["data"]["error"] == "timeout"


# ── HTTP transport tests ─────────────────────────────────────────────────────

class TestHTTPTransport:
    """MCP-03: Test HuginnMCPServer + ApifyAdapter over Streamable HTTP transport."""

    @pytest.fixture
    def http_port(self):
        return _find_free_port()

    def test_http_list_tools(self, http_port):
        async def run():
            url = f"http://127.0.0.1:{http_port}/mcp"
            async with streamable_http_client(url) as (r, w, _):
                async with ClientSession(r, w) as session:
                    await session.initialize()
                    result = await session.list_tools()
                    return [t.name for t in result.tools]

        with _HTTPServerRunner(http_port):
            tool_names = asyncio.run(asyncio.wait_for(run(), timeout=30))
            assert sorted(tool_names) == sorted(EXPECTED_TOOLS)

    def test_http_call_apify_list_actors(self, http_port):
        async def run():
            url = f"http://127.0.0.1:{http_port}/mcp"
            async with streamable_http_client(url) as (r, w, _):
                async with ClientSession(r, w) as session:
                    await session.initialize()
                    result = await session.call_tool("apify_list_actors", {})
                    return _extract_result(result)

        with _HTTPServerRunner(http_port):
            data = asyncio.run(asyncio.wait_for(run(), timeout=30))
            assert data["success"] is True
            assert "kariyer_net" in data["data"]["allowed_actors"]

    def test_http_call_get_source_policy(self, http_port):
        async def run():
            url = f"http://127.0.0.1:{http_port}/mcp"
            async with streamable_http_client(url) as (r, w, _):
                async with ClientSession(r, w) as session:
                    await session.initialize()
                    result = await session.call_tool(
                        "get_source_policy", {"source_id": "apify"}
                    )
                    return _extract_result(result)

        with _HTTPServerRunner(http_port):
            data = asyncio.run(asyncio.wait_for(run(), timeout=30))
            assert data["success"] is True
            assert data["data"]["source_id"] == "apify"

    def test_http_call_submit_evidence_batch(self, http_port):
        evidence = [
            {"title": "HTTP Test Job", "company": "HTTP Test Co"},
        ]
        evidence_file = ROOT / "data" / "job_intelligence" / "mcp_evidence_transport_test.jsonl"
        try:
            async def run():
                url = f"http://127.0.0.1:{http_port}/mcp"
                async with streamable_http_client(url) as (r, w, _):
                    async with ClientSession(r, w) as session:
                        await session.initialize()
                        result = await session.call_tool(
                            "submit_evidence_batch",
                            {"evidence": evidence, "source_id": "transport_test"},
                        )
                        return _extract_result(result)

            with _HTTPServerRunner(http_port):
                data = asyncio.run(asyncio.wait_for(run(), timeout=30))
                assert data["success"] is True
                assert data["data"]["submitted"] == 1
        finally:
            if evidence_file.exists():
                evidence_file.unlink()
