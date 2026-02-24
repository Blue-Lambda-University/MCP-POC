"""Shared MCP client helpers for REPL and Streamlit UI. No server or browser deps."""

import asyncio
import os
from typing import Any

from fastmcp import Client


def default_mcp_url() -> str:
    """Server URL from MCP_URL env or default."""
    return os.environ.get("MCP_URL", "http://127.0.0.1:8000/mcp").rstrip("/")


def _tool_to_dict(tool: Any) -> dict:
    return {
        "name": getattr(tool, "name", None),
        "description": (getattr(tool, "description", None) or "").strip(),
        "inputSchema": getattr(tool, "inputSchema", None),
    }


async def list_tools_async(url: str | None = None) -> list[dict]:
    """Return list of tools (name, description, inputSchema) from the MCP server."""
    base = url or default_mcp_url()
    client = Client(base)
    async with client:
        tools = await client.list_tools()
    return [_tool_to_dict(t) for t in tools]


async def call_tool_async(name: str, arguments: dict, url: str | None = None) -> Any:
    """Call an MCP tool by name with the given arguments. Returns raw tool result."""
    base = url or default_mcp_url()
    client = Client(base)
    async with client:
        result = await client.call_tool(name, arguments)
    return result


def list_tools(url: str | None = None) -> list[dict]:
    """Sync wrapper for list_tools_async."""
    return asyncio.run(list_tools_async(url))


def call_tool(name: str, arguments: dict, url: str | None = None) -> Any:
    """Sync wrapper for call_tool_async."""
    return asyncio.run(call_tool_async(name, arguments, url))


def format_tool_result(result: Any) -> str:
    """Turn tool result into a string for REPL or UI display."""
    if result is None:
        return "(no output)"
    if hasattr(result, "content") and result.content:
        parts = []
        for item in result.content:
            if hasattr(item, "text") and item.text:
                parts.append(item.text)
            if hasattr(item, "type") and getattr(item, "type") == "text" and hasattr(item, "text"):
                parts.append(item.text)
        if parts:
            return "\n".join(parts)
    if hasattr(result, "data"):
        d = result.data
        if isinstance(d, dict):
            if "content" in d and isinstance(d["content"], str):
                return d["content"]
            if "message" in d:
                return d["message"]
            if "error" in d:
                return f"Error: {d['error']}"
            if "image_base64" in d and d["image_base64"]:
                return f"[Screenshot received, base64 length {len(d['image_base64'])}]"
        return str(d)
    if hasattr(result, "structured_content") and result.structured_content:
        sc = result.structured_content
        if isinstance(sc, dict):
            if "content" in sc and isinstance(sc["content"], str):
                return sc["content"]
            if "result" in sc and isinstance(sc["result"], dict):
                r = sc["result"]
                if "content" in r:
                    return r["content"]
                if "image_base64" in r and r["image_base64"]:
                    return f"[Screenshot received, base64 length {len(r['image_base64'])}]"
                if "error" in r:
                    return f"Error: {r['error']}"
            if "error" in sc:
                return f"Error: {sc['error']}"
        return str(sc)
    return str(result)


def get_result_image_base64(result: Any) -> str | None:
    """Extract base64 image from a screenshot tool result, or None."""
    if result is None:
        return None
    if hasattr(result, "structured_content") and isinstance(result.structured_content, dict):
        sc = result.structured_content
        if "result" in sc and isinstance(sc["result"], dict):
            return sc["result"].get("image_base64")
        return sc.get("image_base64")
    if hasattr(result, "data") and isinstance(result.data, dict):
        return result.data.get("image_base64")
    return None
