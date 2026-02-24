# Playwright MCP

FastMCP server with Playwright for browser automation and web scraping. Exposes tools over HTTP for use with MCP clients (e.g. GPT-based agents).

## Features

- **HTTP transport** – Server runs as an HTTP service; clients connect via URL.
- **Long-lived browser** – One Chromium instance started at server startup (Option A).
- **Structured logging** – Structlog with configurable level and JSON output.
- **Modular layout** – Config, logging, browser, tools, and server are separate; state is injected via lifespan context.

## Tools

| Tool | Description |
|------|-------------|
| `browser_navigate` | Navigate to a URL |
| `browser_snapshot` | Get HTML/text snapshot of the current page |
| `browser_tabs` | List open tabs (pages) |
| `browser_click` | Click an element by CSS selector |
| `browser_type` | Type text into an element |
| `browser_fill_form` | Fill multiple form fields (selector → value map) |
| `browser_scrape` | Extract content (text, HTML, or links) from current page or URL |
| `browser_screenshot` | Take a PNG screenshot (base64) of page or element |

## Requirements

- Python 3.10+
- Playwright browsers (install after `pip install`)

## Setup

```bash
# From project root
pip install -e .
python -m playwright install chromium
```

Optional: copy `.env.example` to `.env` and adjust `MCP_HOST`, `MCP_PORT`, `HEADLESS`, `LOG_LEVEL`, `LOG_JSON`.

## Testing

Install dev dependencies (or use `requirements.txt`, which includes pytest), then run tests from the project root:

```bash
# Install the package and test deps
pip install -e .
pip install -r requirements.txt   # or: pip install -e ".[dev]"

# Run all tests
pytest

# Verbose output
pytest -v

# Run a specific file or test
pytest tests/test_schemas.py
pytest tests/test_schemas.py -v
```

Tests include:
- **`tests/test_schemas.py`** – Pydantic schema validation (no browser).
- **`tests/test_tools.py`** – Tool behavior with a mocked browser context (no real browser).

## Run

```bash
# After pip install -e .
playwright-mcp

# Or
python -m playwright_mcp.main
```

Server listens at `http://127.0.0.1:8000` by default. MCP endpoint is typically at `http://127.0.0.1:8000/mcp` (see FastMCP HTTP deployment docs).

### Discovering tools (list available tools)

With the server running, you can list the tools it exposes in two ways:

**1. Script (recommended)** – from the project root:

```bash
python scripts/list_tools.py
```

This prints a JSON array of tools (name, description, inputSchema). To point at another URL:

```bash
python scripts/list_tools.py http://localhost:8000/mcp
# or
MCP_URL=http://127.0.0.1:8000/mcp python scripts/list_tools.py
```

**2. MCP clients** – Add the server as an MCP server in your client:

- **Cursor**: Settings → MCP → Add server; use URL `http://127.0.0.1:8000/mcp` (or your host/port). The client will list and call tools for you.
- **Claude Desktop / other MCP clients**: Configure the transport to use HTTP and the same URL. They will discover tools via the MCP protocol when connecting.

**3. Tools UI (web)** – With the server running, open in a browser:

- **Tools page:** [http://127.0.0.1:8000/tools-ui](http://127.0.0.1:8000/tools-ui)  
  Lists all tools with name, description, and input schema in a simple dark UI.
- **Tools JSON:** [http://127.0.0.1:8000/api/tools](http://127.0.0.1:8000/api/tools)  
  Returns the same list as JSON (for scripts or API use).

Use your configured host/port if different (e.g. `http://localhost:8000/tools-ui`).

### MCP Inspector (official debugging UI)

The [MCP Inspector](https://github.com/modelcontextprotocol/inspector) is the official visual tool for testing and debugging MCP servers. You can list tools, call them with custom arguments, and inspect requests and responses.

**Requirements:** Node.js (for `npx`).

**1. Start the Playwright MCP server** (in one terminal):

```bash
playwright-mcp
```

**2. Start the MCP Inspector** (in another terminal):

```bash
npx @modelcontextprotocol/inspector
```

**3. Open the Inspector** in your browser at **http://localhost:6274** (or the URL printed by the command).

**4. Connect to this server:** In the Inspector, add a new server and choose **HTTP** (or URL) as the transport. Set the URL to:

```
http://127.0.0.1:8000/mcp
```

Use your configured host/port if different (e.g. `http://localhost:8000/mcp`). Do **not** use STDIO or a command for this server—it only speaks HTTP.

Once connected, you can browse and invoke tools (e.g. `browser_navigate`, `browser_scrape`) from the Inspector UI.

## Scrape a URL from the command line

To scrape a single URL **without** running the MCP server, use the standalone scraper (same browser and tool logic):

```bash
# Plain text (default)
python -m playwright_mcp.scrape_url https://example.com

# HTML
python -m playwright_mcp.scrape_url https://example.com --format html

# List of links (JSON)
python -m playwright_mcp.scrape_url https://example.com --format links

# Only a specific element and limit length
python -m playwright_mcp.scrape_url https://example.com --selector "main" --max-length 5000
```

| Option | Description |
|--------|-------------|
| `url` | URL to scrape (required) |
| `--format` | `text`, `html`, or `links` (default: `text`) |
| `--selector` | Optional CSS selector to scrape only that element |
| `--max-length` | Max characters for text/html (default: 100000) |

Requires the package installed (`pip install -e .`) and Chromium (`python -m playwright install chromium`).

## MCP client (REPL and Streamlit UI)

Client and UI live under **`scripts/`**, separate from the server. **Start the server first** (`playwright-mcp`) in another terminal.

### REPL (terminal)

```bash
playwright-mcp-repl
# Or: python -m scripts.mcp_repl   (from project root)
# Or: python scripts/mcp_repl.py   (from project root)
```

At the `mcp>` prompt, type a tool name and optional JSON arguments. Examples:

```
mcp> list
mcp> browser_navigate {"params": {"url": "https://example.com"}}
mcp> browser_scrape {"params": {"url": "https://example.com", "format": "text"}}
mcp> quit
```

Commands: `list` / `tools` (list tools), `help`, `quit` / `exit`. Use `MCP_URL=http://127.0.0.1:9000/mcp` if the server runs on another port.

### Streamlit UI (browser)

Install the UI optional dependency, then run:

```bash
pip install -e ".[ui]"
playwright-mcp-ui
```

Or run Streamlit directly:

```bash
pip install -e ".[ui]"
streamlit run scripts/mcp_streamlit_ui.py
```

Open the URL shown (e.g. http://localhost:8501). In the sidebar, enter the MCP server URL and click **Connect / Refresh tools**. Select a tool, fill the form or switch to **Edit as JSON**, then click **Run tool**. Screenshot results show the image inline.

## Project layout

```
src/playwright_mcp/     # Server
├── main.py             # Entrypoint (playwright-mcp)
├── scrape_url.py      # Standalone CLI to scrape a URL (no server)
├── config/             # Env-based settings
├── logging_/           # Structlog setup and get_logger
├── schemas/            # Pydantic input/output models (no server/browser deps)
├── browser/            # Lifecycle and BrowserState
├── tools/              # Navigation, interaction, scraping, screenshot
└── server/             # FastMCP app and dependency registration

scripts/                # MCP client (separate from server)
├── client_helper.py    # Shared client logic (list_tools, call_tool, format result)
├── mcp_repl.py        # REPL (playwright-mcp-repl)
└── mcp_streamlit_ui.py # Streamlit UI (playwright-mcp-ui)
```

## Configuration

| Env var | Default | Description |
|---------|---------|-------------|
| `MCP_HOST` | `127.0.0.1` | HTTP bind host |
| `MCP_PORT` | `8000` | HTTP bind port |
| `HEADLESS` | `true` | Run browser headless |
| `LOG_LEVEL` | `INFO` | Log level (DEBUG, INFO, WARNING, ERROR) |
| `LOG_JSON` | `false` | Output logs as JSON |
