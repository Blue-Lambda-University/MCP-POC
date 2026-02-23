"""Screenshot tool: capture the current page or an element as PNG."""

import base64

from fastmcp import Context

from playwright_mcp.browser.state import BrowserState
from playwright_mcp.schemas.screenshots import ScreenshotInput, ScreenshotResult


async def browser_screenshot(
    ctx: Context,
    params: ScreenshotInput,
) -> ScreenshotResult:
    """Take a screenshot of the current page. Returns base64-encoded PNG.
    Use 'selector' to capture only that element, or set 'full_page' to True for the full scrollable page."""
    state: BrowserState = ctx.lifespan_context["browser_state"]
    logger = ctx.lifespan_context["logger"]
    logger.info(
        "browser_screenshot",
        selector=params.selector,
        full_page=params.full_page,
    )
    page = state.page

    if params.selector:
        element = await page.query_selector(params.selector)
        if element is None:
            return ScreenshotResult(
                image_base64=None,
                error=f"No element found for selector {params.selector}",
            )
        png_bytes = await element.screenshot(type="png")
    else:
        png_bytes = await page.screenshot(
            type="png", full_page=params.full_page
        )

    return ScreenshotResult(
        image_base64=base64.b64encode(png_bytes).decode("ascii"),
        error=None,
    )


def register_screenshot_tools(mcp: object) -> None:
    """Register screenshot tools with the FastMCP server."""
    mcp.add_tool(browser_screenshot)
