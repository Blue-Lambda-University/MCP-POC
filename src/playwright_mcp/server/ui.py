"""Tools UI: HTML page and /api/tools endpoint. No business logic."""

from fastmcp import Client
from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse

from playwright_mcp.config import get_settings


TOOLS_UI_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Playwright MCP – Tools</title>
  <style>
    :root { --bg: #0f0f12; --card: #1a1a1f; --text: #e4e4e7; --muted: #71717a; --accent: #a78bfa; --border: #27272a; }
    * { box-sizing: border-box; }
    body { font-family: system-ui, -apple-system, sans-serif; background: var(--bg); color: var(--text); margin: 0; padding: 1.5rem; line-height: 1.5; }
    h1 { font-size: 1.5rem; font-weight: 600; margin: 0 0 0.5rem; }
    p.muted { color: var(--muted); font-size: 0.875rem; margin: 0 0 1.5rem; }
    .tools { display: grid; gap: 1rem; }
    .tool { background: var(--card); border: 1px solid var(--border); border-radius: 8px; padding: 1rem 1.25rem; }
    .tool h2 { font-size: 1rem; font-weight: 600; margin: 0 0 0.35rem; color: var(--accent); }
    .tool .desc { color: var(--muted); font-size: 0.875rem; margin: 0 0 0.5rem; }
    .tool pre { font-size: 0.75rem; background: var(--bg); padding: 0.75rem; border-radius: 6px; overflow: auto; margin: 0; color: var(--muted); }
    .error { color: #f87171; background: #1c1917; padding: 1rem; border-radius: 8px; margin-bottom: 1rem; }
    .loading { color: var(--muted); }
  </style>
</head>
<body>
  <h1>Playwright MCP – Tools</h1>
  <p class="muted">Tools exposed by this MCP server. Use an MCP client or the API to call them.</p>
  <div id="root" class="loading">Loading tools…</div>
  <script>
    fetch('/api/tools')
      .then(r => r.ok ? r.json() : Promise.reject(new Error(r.statusText)))
      .then(tools => {
        const root = document.getElementById('root');
        root.className = 'tools';
        root.innerHTML = tools.map(t => `
          <div class="tool">
            <h2>${escapeHtml(t.name || '')}</h2>
            <div class="desc">${escapeHtml(t.description || '')}</div>
            ${t.inputSchema && Object.keys(t.inputSchema).length ? `<pre>${escapeHtml(JSON.stringify(t.inputSchema, null, 2))}</pre>` : ''}
          </div>
        `).join('');
      })
      .catch(err => {
        document.getElementById('root').className = '';
        document.getElementById('root').innerHTML = `<div class="error">Failed to load tools: ${escapeHtml(err.message)}</div>`;
      });
    function escapeHtml(s) {
      const div = document.createElement('div');
      div.textContent = s;
      return div.innerHTML;
    }
  </script>
</body>
</html>
"""


def _tool_to_json(tool) -> dict:
    out = {
        "name": getattr(tool, "name", None),
        "description": (getattr(tool, "description", None) or "").strip(),
    }
    if hasattr(tool, "inputSchema") and tool.inputSchema:
        out["inputSchema"] = tool.inputSchema
    return out


async def _get_tools_json() -> list[dict]:
    settings = get_settings()
    base = f"http://{settings.mcp_host}:{settings.mcp_port}/mcp"
    client = Client(base)
    async with client:
        tools = await client.list_tools()
    return [_tool_to_json(t) for t in tools]


async def api_tools(_request: Request) -> JSONResponse:
    """GET /api/tools – return list of tools as JSON."""
    try:
        tools = await _get_tools_json()
        return JSONResponse(tools)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


async def tools_ui(_request: Request) -> HTMLResponse:
    """GET /tools-ui – serve HTML page that lists tools."""
    return HTMLResponse(TOOLS_UI_HTML)
