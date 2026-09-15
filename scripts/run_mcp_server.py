#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""MCP-03: CLI entry point for running the Huginn MCP Server.

Usage:
    python scripts/run_mcp_server.py stdio       # stdio transport (for MCP clients)
    python scripts/run_mcp_server.py http        # Streamable HTTP (default port 8000)
    python scripts/run_mcp_server.py http --port 9000  # Custom port
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from company_master.mcp.mcp_server_entry import main  # noqa: E402

if __name__ == "__main__":
    main()
