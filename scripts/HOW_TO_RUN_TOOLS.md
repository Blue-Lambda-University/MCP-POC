# How to run each MCP tool

Start the Playwright MCP server first (`playwright-mcp` in another terminal), then use either the **REPL** or the **Streamlit UI** to call tools.

- **REPL:** `playwright-mcp-repl` or `python -m scripts.mcp_repl` (from project root)
- **Streamlit UI:** `playwright-mcp-ui` or `streamlit run scripts/mcp_streamlit_ui.py`
- **List tools in REPL:** type `list` or `tools` at the `mcp>` prompt

In the REPL, type the tool name followed by a JSON object. All tools use a `params` object for their arguments.

---

## browser_navigate

Navigate the browser to a URL.

**Params:**

| Field | Type   | Required | Description        |
|-------|--------|----------|--------------------|
| `url` | string | Yes      | URL to open        |

**REPL example:**

```
mcp> browser_navigate {"params": {"url": "https://www.medicare.gov"}}
```

---

## browser_snapshot

Get an HTML/text snapshot of the current page (for layout and elements). No arguments.

**REPL example:**

```
mcp> browser_snapshot {"params": {}}
```

Or:

```
mcp> browser_snapshot {}
```

---

## browser_tabs

List open browser tabs (pages). No arguments.

**REPL example:**

```
mcp> browser_tabs {}
```

---

## browser_click

Click an element on the page using a CSS selector.

**Params:**

| Field      | Type   | Required | Description                          |
|------------|--------|----------|--------------------------------------|
| `selector` | string | Yes      | CSS selector (e.g. `button`, `#submit`) |

**REPL example:**

```
mcp> browser_click {"params": {"selector": "button.primary"}}
```

---

## browser_type

Type text into an input or textarea.

**Params:**

| Field      | Type   | Required | Description              |
|------------|--------|----------|--------------------------|
| `selector` | string | Yes      | CSS selector for the field |
| `text`     | string | Yes      | Text to type             |

**REPL example:**

```
mcp> browser_type {"params": {"selector": "#search", "text": "medicare"}}
```

---

## browser_fill_form

Fill multiple form fields at once. Pass a map of CSS selectors to values.

**Params:**

| Field   | Type         | Required | Description                    |
|---------|--------------|----------|--------------------------------|
| `fields`| object       | Yes      | `{"selector": "value", ...}`  |

**REPL example:**

```
mcp> browser_fill_form {"params": {"fields": {"#email": "user@example.com", "#password": "secret123"}}}
```

---

## browser_scrape

Extract content from the current page or from a URL. Can return plain text, HTML, or a list of links.

**Params:**

| Field         | Type   | Required | Description |
|---------------|--------|----------|-------------|
| `url`         | string | No       | URL to open and scrape; if omitted, uses current page |
| `selector`    | string | No       | CSS selector to scrape only that element (e.g. `main`, `#content`) |
| `format`      | string | No       | `"text"` (default), `"html"`, or `"links"` |
| `wait_selector` | string | No     | CSS selector to wait for before scraping (for slow/JS-rendered pages) |
| `wait_ms`     | number | No       | Delay in milliseconds before scraping |
| `max_length`  | number | No       | Max characters for text/html (default 100000) |

**REPL examples:**

Plain text from a URL:

```
mcp> browser_scrape {"params": {"url": "https://www.medicare.gov", "format": "text"}}
```

HTML:

```
mcp> browser_scrape {"params": {"url": "https://www.medicare.gov", "format": "html"}}
```

List of links:

```
mcp> browser_scrape {"params": {"url": "https://www.medicare.gov", "format": "links"}}
```

With wait for slow pages:

```
mcp> browser_scrape {"params": {"url": "https://www.medicare.gov", "format": "text", "wait_ms": 3000}}
```

Only a specific element:

```
mcp> browser_scrape {"params": {"url": "https://www.medicare.gov", "selector": "main", "format": "text"}}
```

---

## browser_screenshot

Take a PNG screenshot of the page or a specific element. Returns base64-encoded image (or an error message).

**Params:**

| Field       | Type    | Required | Description |
|-------------|---------|----------|-------------|
| `selector`  | string  | No       | CSS selector to capture only that element |
| `full_page` | boolean | No       | If `true`, capture the full scrollable page (ignored when `selector` is set) |

**REPL examples:**

Current viewport:

```
mcp> browser_screenshot {"params": {}}
```

Full page:

```
mcp> browser_screenshot {"params": {"full_page": true}}
```

One element:

```
mcp> browser_screenshot {"params": {"selector": "main"}}
```

---

## Using a different server URL

If the server runs on another host or port, set `MCP_URL` before starting the REPL or UI:

```bash
MCP_URL=http://127.0.0.1:9000/mcp python -m scripts.mcp_repl
```

In the Streamlit UI, enter the URL in the sidebar and click **Connect / Refresh tools**.
