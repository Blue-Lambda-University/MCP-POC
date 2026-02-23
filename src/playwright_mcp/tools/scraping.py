"""Web scraping tool: extract content from the current page or a URL."""

import asyncio

from fastmcp import Context

from playwright_mcp.browser.state import BrowserState
from playwright_mcp.schemas.scraping import (
    LinkItem,
    ScrapeInput,
    ScrapeLinksResult,
    ScrapeTextResult,
)


async def browser_scrape(
    ctx: Context,
    params: ScrapeInput,
) -> ScrapeTextResult | ScrapeLinksResult:
    """Extract content from the current page or from a URL. Use 'url' to navigate first, then scrape.
    'selector': optional CSS selector to scrape only that element (e.g. 'article', '#content').
    'format': 'text' (plain text), 'html' (raw HTML), or 'links' (list of {href, text}).
    'wait_selector': optional selector to wait for before scraping (for JS-rendered content).
    'wait_ms': optional delay in milliseconds before scraping.
    'max_length': maximum characters to return (default 100000)."""
    state: BrowserState = ctx.lifespan_context["browser_state"]
    logger = ctx.lifespan_context["logger"]
    logger.info(
        "browser_scrape",
        url=params.url,
        selector=params.selector,
        format=params.format,
    )
    page = state.page

    if params.url:
        await page.goto(params.url, wait_until="domcontentloaded")
    if params.wait_selector:
        await page.wait_for_selector(params.wait_selector, timeout=15_000)
    if params.wait_ms is not None and params.wait_ms > 0:
        await asyncio.sleep(params.wait_ms / 1000.0)

    root = page
    if params.selector:
        el = await page.query_selector(params.selector)
        if el is None:
            return ScrapeTextResult(
                content=f"No element found for selector: {params.selector}"
            )
        root = el

    def truncate(s: str) -> str:
        if len(s) <= params.max_length:
            return s
        return s[: params.max_length] + "\n... [truncated]"

    if params.format == "html":
        content = await root.inner_html() if root != page else await page.content()
        return ScrapeTextResult(content=truncate(content))
    if params.format == "links":
        anchors = await root.query_selector_all("a[href]")
        links = []
        for a in anchors[:500]:
            href = await a.get_attribute("href") or ""
            text = (await a.inner_text()).strip()[:200]
            links.append(LinkItem(href=href, text=text))
        return ScrapeLinksResult(links=links)
    # default: text
    content = await root.inner_text()
    return ScrapeTextResult(content=truncate(content))


def register_scraping_tools(mcp: object) -> None:
    """Register scraping tools with the FastMCP server."""
    mcp.add_tool(browser_scrape)
