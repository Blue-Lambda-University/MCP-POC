"""Navigation tools: goto, snapshot, tabs."""

from fastmcp import Context

from playwright_mcp.browser.state import BrowserState
from playwright_mcp.schemas.navigation import (
    NavigateInput,
    NavigateResult,
    SnapshotResult,
    TabInfo,
    TabsResult,
)


async def browser_navigate(ctx: Context, params: NavigateInput) -> NavigateResult:
    """Navigate the browser to a URL. Use this to open or change the current page."""
    state: BrowserState = ctx.lifespan_context["browser_state"]
    logger = ctx.lifespan_context["logger"]
    logger.info("browser_navigate", url=params.url)
    page = state.page
    response = await page.goto(params.url, wait_until="domcontentloaded")
    if response is None:
        return NavigateResult(message="Navigation initiated (no response).")
    return NavigateResult(
        message=f"Navigated to {params.url}. Status: {response.status} {response.status_text}"
    )


async def browser_snapshot(ctx: Context) -> SnapshotResult:
    """Get a text snapshot of the current page (accessibility tree / main content) for understanding layout and elements."""
    state: BrowserState = ctx.lifespan_context["browser_state"]
    logger = ctx.lifespan_context["logger"]
    logger.info("browser_snapshot")
    page = state.page
    try:
        content = await page.content()
        body_start = content.find("<body")
        if body_start != -1:
            content = content[body_start:]
        if len(content) > 50_000:
            content = content[:50_000] + "\n... [truncated]"
        return SnapshotResult(content=content)
    except Exception as e:
        logger.exception("browser_snapshot failed")
        return SnapshotResult(content=f"Error getting snapshot: {e!s}")


async def browser_tabs(ctx: Context) -> TabsResult:
    """List open browser tabs (pages) in the current context."""
    state: BrowserState = ctx.lifespan_context["browser_state"]
    logger = ctx.lifespan_context["logger"]
    logger.info("browser_tabs")
    context = state.context
    pages = context.pages
    tabs = [
        TabInfo(index=i, url=await p.url(), title=await p.title())
        for i, p in enumerate(pages)
    ]
    return TabsResult(tabs=tabs)


def register_navigation_tools(mcp: object) -> None:
    """Register navigation tools with the FastMCP server."""
    mcp.add_tool(browser_navigate)
    mcp.add_tool(browser_snapshot)
    mcp.add_tool(browser_tabs)
