# -*- coding: utf-8 -*-
"""MCP-03: MCP Server entry point for Huginn + Apify integration.

Wraps ApifyAdapter and HuginnMCPServer tool sets into a real MCP server
using the mcp Python package (pip install mcp). Supports two transports:

- stdio:  python -m company_master.mcp.mcp_server_entry stdio
- HTTP:   python -m company_master.mcp.mcp_server_entry http --port 8000

The server exposes the following tools:
Apify:    apify_list_actors, apify_run_actor, apify_get_dataset
Huginn:   get_source_policy, get_collection_run_status,
submit_evidence_batch, report_collection_failure

All tools are gated by the PolicyEngine (whitelist, spend limits, data limits).
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import sys
import os
from pathlib import Path
from typing import Any, Optional

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

from mcp.server.mcpserver.server import MCPServer  # noqa: E402

from company_master.mcp.policy_engine import PolicyEngine  # noqa: E402
from company_master.mcp.apify_adapter import ApifyAdapter  # noqa: E402
from company_master.mcp.huginn_server import HuginnMCPServer  # noqa: E402

logger = logging.getLogger(__name__)

# OpenTelemetry tracing
try:
    from opentelemetry import trace
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.exporter.jaeger.thrift import JaegerExporter
    from opentelemetry.instrumentation.requests import RequestsInstrumentor
    OTEL_AVAILABLE = True
except ImportError:
    OTEL_AVAILABLE = False

if OTEL_AVAILABLE:
    trace.set_tracer_provider(TracerProvider())
    tracer = trace.get_tracer(__name__)
    jaeger_host = os.getenv("JAEGER_HOST", "localhost")
    jaeger_port = int(os.getenv("JAEGER_PORT", "6831"))
    jaeger_exporter = JaegerExporter(
        agent_host_name=jaeger_host,
        agent_port=jaeger_port,
    )
    trace.get_tracer_provider().add_span_processor(
        BatchSpanProcessor(jaeger_exporter)
    )
    RequestsInstrumentor().instrument()

INSTRUCTIONS = (
    "Huginn B2B Intelligence MCP Server. "
    "Apify scraping ve Huginn veri erişim araçları. "
    "Tüm tool çağrıları Policy Engine tarafından kontrol edilir."
)


def create_mcp_server(
        apify_adapter: Optional[ApifyAdapter] = None,
        huginn_server: Optional[HuginnMCPServer] = None,
    ) -> MCPServer:
        """Create an MCPServer with Apify + Huginn tools registered.
    
        Args:
        apify_adapter: Pre-configured ApifyAdapter (or None for default).
        huginn_server: Pre-configured HuginnMCPServer (or None for default).
        """
        server = MCPServer(
            name="huginn-mcp",
            version="1.0.0",
            title="Huginn MCP Server",
            description="Huginn B2B Intelligence - Apify ve Huginn verilerine MCP erişimi",
            instructions=INSTRUCTIONS,
        )
    
        adapter = apify_adapter or ApifyAdapter(policy_engine=PolicyEngine())
        huginn = huginn_server or HuginnMCPServer(policies=PolicyEngine())
    
        # -- Apify tools --
    
        @server.tool(
            name="apify_list_actors",
            title="List Apify Actors",
            description="Whitelist listesindeki Apify actorlarini ve harcama limitlerini listeler.",
        )
        async def handle_apify_list_actors() -> dict[str, Any]:
            return adapter.apify_list_actors().to_dict()
    
        @server.tool(
            name="apify_run_actor",
            title="Run Apify Actor",
            description="Whitelist listesindeki bir Apify actorunu calistirir ve sonuclari getirir.",
        )
        async def handle_apify_run_actor(
            actor_id: str,
            run_input: Optional[dict[str, Any]] = None,
            max_items: Optional[int] = None,
            max_charge_usd: Optional[float] = None,
        ) -> dict[str, Any]:
            return adapter.apify_run_actor(
                actor_id=actor_id,
                run_input=run_input,
                max_items=max_items,
                max_charge_usd=max_charge_usd,
            ).to_dict()
    
        @server.tool(
            name="apify_get_dataset",
            title="Get Apify Dataset",
            description="Bir Apify datasetini okur (policy kontrolu ile).",
        )
        async def handle_apify_get_dataset(
            dataset_id: str,
            max_items: Optional[int] = None,
            clean: bool = True,
        ) -> dict[str, Any]:
            return adapter.apify_get_dataset(
                dataset_id=dataset_id,
                max_items=max_items,
                clean=clean,
            ).to_dict()
    
        # -- Huginn tools --
    
        @server.tool(
            name="get_source_policy",
            title="Get Source Policy",
            description="Bir veri kaynaginin izin politikasini getirir (KVKK, domain whitelist, rate limit, NACE scope).",
        )
        async def handle_get_source_policy(source_id: str) -> dict[str, Any]:
            return huginn.get_source_policy(source_id=source_id).to_dict()
    
        @server.tool(
            name="get_collection_run_status",
            title="Get Collection Run Status",
            description="Veri toplama run durumunu getirir.",
        )
        async def handle_get_collection_run_status(run_id: str) -> dict[str, Any]:
            return huginn.get_collection_run_status(run_id=run_id).to_dict()
    
        @server.tool(
            name="submit_evidence_batch",
            title="Submit Evidence Batch",
            description="Toplanan kanitlari (scraped data) ingest pipeline'a gönderir.",
        )
        async def handle_submit_evidence_batch(
            evidence: list[dict[str, Any]],
            source_id: str = "",
        ) -> dict[str, Any]:
            return huginn.submit_evidence_batch(
                evidence=evidence,
                source_id=source_id,
            ).to_dict()
    
        @server.tool(
            name="report_collection_failure",
            title="Report Collection Failure",
            description="Scraper/collect run basarisizligini bildirir.",
        )
        async def handle_report_collection_failure(
            source_id: str,
            error: str,
            run_id: Optional[str] = None,
        ) -> dict[str, Any]:
            return huginn.report_collection_failure(
                source_id=source_id,
                error=error,
                run_id=run_id,
            ).to_dict()
    
        return server


def main_stdio() -> None:
    """Run the MCP server over stdio transport (subprocess mode)."""
    server = create_mcp_server()
    asyncio.run(server.run_stdio_async())


def main_http(
    host: str = "127.0.0.1",
    port: int = 8000,
    path: str = "/mcp",
) -> None:
    """Run the MCP server over Streamable HTTP transport."""
    server = create_mcp_server()
    asyncio.run(
        server.run_streamable_http_async(
            host=host,
            port=port,
            streamable_http_path=path,
        )
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Huginn MCP Server (MCP-03)"
    )
    parser.add_argument(
        "transport",
        choices=["stdio", "http"],
        default="stdio",
        nargs="?",
        help="Transport: stdio (default) or http"
    )
    parser.add_argument("--host", default="127.0.0.1", help="HTTP host")
    parser.add_argument("--port", type=int, default=8000, help="HTTP port")
    parser.add_argument("--path", default="/mcp", help="HTTP endpoint path")
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
    )

    args = parser.parse_args()
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        stream=sys.stderr,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    if args.transport == "stdio":
        main_stdio()
    elif args.transport == "http":
        main_http(host=args.host, port=args.port, path=args.path)


if __name__ == "__main__":
    main()
