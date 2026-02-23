#!/usr/bin/env python3
"""
List tools exposed by the Playwright MCP server (or any MCP server URL).
Requires the server to be running.

Usage:
  python scripts/list_tools.py
  python scripts/list_tools.py http://localhost:9000/mcp
"""

import asyncio
import json
import os
import sys
from pathlib import Path

# Add project src to path when run from repo
repo_root = Path(__file__).resolve().parent.parent
src = repo_root / "src"
if src.exists() and str(src) not in sys.path:
    sys.path.insert(0, str(src))

from fastmcp import Client


def _tool_summary(tool) -> dict:
    """Extract name, description, and input schema for display."""
    out = {
        "name": getattr(tool, "name", None),
        "description": getattr(tool, "description", None) or "",
    }
    if hasattr(tool, "inputSchema") and tool.inputSchema:
        out["inputSchema"] = tool.inputSchema
    return out


async def main() -> None:
    base_url = os.environ.get("MCP_URL", "http://127.0.0.1:8000/mcp")
    if len(sys.argv) > 1:
        base_url = sys.argv[1].rstrip("/")

    if not base_url.startswith("http"):
        base_url = f"http://{base_url}"

    print(f"Connecting to {base_url} ...", file=sys.stderr)
    client = Client(base_url)

    async with client:
        tools = await client.list_tools()
        result = [_tool_summary(t) for t in tools]
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
