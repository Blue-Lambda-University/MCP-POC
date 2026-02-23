"""
Standalone script to scrape a URL using the same browser and tool logic as the MCP server.
Usage:
  python -m playwright_mcp.scrape_url <url> [--format text|html|links] [--selector CSS] [--max-length N]
"""

import argparse
import asyncio
import json
import sys
from pathlib import Path

# Ensure src is on path when run as __main__
if __name__ == "__main__" and (src := Path(__file__).resolve().parent.parent) not in sys.path:
    sys.path.insert(0, str(src))

from playwright.async_api import async_playwright

from playwright_mcp.browser.state import BrowserState
from playwright_mcp.tools.scraping import browser_scrape
from playwright_mcp.schemas.scraping import ScrapeInput, ScrapeTextResult, ScrapeLinksResult


def _make_ctx(state: BrowserState):
    """Minimal context object with lifespan_context for the scrape tool."""
    class Ctx:
        lifespan_context = {
            "browser_state": None,
            "logger": type("Logger", (), {"info": lambda *a, **k: None})(),
        }
    Ctx.lifespan_context["browser_state"] = state
    return Ctx()


async def _run(url: str, format: str, selector: str | None, max_length: int) -> None:
    async with async_playwright() as pw:
        state = BrowserState()
        state.set_playwright(pw)
        browser = await pw.chromium.launch(headless=True)
        state.set_browser(browser)
        context = await browser.new_context()
        state.set_context(context)
        page = await context.new_page()
        state.set_page(page)
        try:
            ctx = _make_ctx(state)
            params = ScrapeInput(
                url=url,
                format=format,
                selector=selector or None,
                max_length=max_length,
            )
            result = await browser_scrape(ctx, params)
            if isinstance(result, ScrapeTextResult):
                print(result.content)
            elif isinstance(result, ScrapeLinksResult):
                print(json.dumps([{"href": l.href, "text": l.text} for l in result.links], indent=2))
            else:
                print(result)
        finally:
            await state.close()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Scrape a URL (text, HTML, or links) using Playwright.",
        epilog="Example: python -m playwright_mcp.scrape_url https://example.com --format links",
    )
    parser.add_argument("url", help="URL to scrape")
    parser.add_argument(
        "--format",
        choices=("text", "html", "links"),
        default="text",
        help="Output format: text, html, or links (default: text)",
    )
    parser.add_argument(
        "--selector",
        default=None,
        help="Optional CSS selector to scrape only that element",
    )
    parser.add_argument(
        "--max-length",
        type=int,
        default=100_000,
        help="Max characters for text/html (default: 100000)",
    )
    args = parser.parse_args()
    asyncio.run(_run(args.url, args.format, args.selector, args.max_length))


if __name__ == "__main__":
    main()
