"""REPL client for the MCP server: mcp> prompt, tool name + optional JSON."""

import asyncio
import json
import sys
from pathlib import Path

# Ensure project root is on path when run as __main__ (so scripts package is importable)
if __name__ == "__main__":
    root = Path(__file__).resolve().parent.parent
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))

from scripts.client_helper import (
    call_tool_async,
    default_mcp_url,
    format_tool_result,
    list_tools_async,
)


HELP_TEXT = """
Commands:
  <tool_name> [<json>]   Call tool with optional JSON arguments (e.g. browser_navigate {"params": {"url": "https://example.com"}})
  list, tools            List available tools
  help                  Show this help
  quit, exit            Exit the REPL
"""


def parse_line(line: str) -> tuple[str, dict]:
    """Parse 'tool_name {"key": "value"}' into (name, dict). JSON optional."""
    line = line.strip()
    if not line:
        return "", {}
    parts = line.split(maxsplit=1)
    name = parts[0].strip()
    if len(parts) == 1:
        return name, {}
    rest = parts[1].strip()
    if not rest:
        return name, {}
    try:
        args = json.loads(rest)
        return name, args if isinstance(args, dict) else {}
    except json.JSONDecodeError:
        return name, {"_raw": rest}


def main() -> int:
    url = default_mcp_url()
    print(f"Connecting to {url} ...")
    try:
        tools = asyncio.run(list_tools_async(url))
    except Exception as e:
        print(f"Connection failed: {e}", file=sys.stderr)
        return 1
    names = [t["name"] for t in tools if t.get("name")]
    print(f"Connected. Tools: {', '.join(names)}")
    print("Type a tool name and optional JSON. 'list' to list tools, 'quit' to exit.")
    print(HELP_TEXT.strip())

    while True:
        try:
            line = input("mcp> ").strip()
        except EOFError:
            print()
            break
        if not line:
            continue
        cmd, args = parse_line(line)
        cmd_lower = cmd.lower()
        if cmd_lower in ("quit", "exit"):
            print("Bye.")
            break
        if cmd_lower in ("list", "tools"):
            try:
                tools = asyncio.run(list_tools_async(url))
                for t in tools:
                    name = t.get("name", "")
                    desc = (t.get("description") or "")[:60]
                    print(f"  {name}  {desc}")
            except Exception as e:
                print(f"Error: {e}", file=sys.stderr)
            continue
        if cmd_lower == "help":
            print(HELP_TEXT.strip())
            continue
        if not cmd:
            continue
        try:
            result = asyncio.run(call_tool_async(cmd, args, url))
            print(format_tool_result(result))
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
