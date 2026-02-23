"""Interaction tools: click, type, fill."""

from fastmcp import Context

from playwright_mcp.browser.state import BrowserState
from playwright_mcp.schemas.interaction import (
    ClickInput,
    ClickResult,
    FillFormInput,
    FillFormResult,
    TypeInput,
    TypeResult,
)


async def browser_click(ctx: Context, params: ClickInput) -> ClickResult:
    """Click an element on the page. Provide a CSS selector (e.g. 'button.submit', '#login')."""
    state: BrowserState = ctx.lifespan_context["browser_state"]
    logger = ctx.lifespan_context["logger"]
    logger.info("browser_click", selector=params.selector)
    page = state.page
    await page.click(params.selector, timeout=10_000)
    return ClickResult(message=f"Clicked: {params.selector}")


async def browser_type(ctx: Context, params: TypeInput) -> TypeResult:
    """Type text into an element. Use a CSS selector to target the input/textarea."""
    state: BrowserState = ctx.lifespan_context["browser_state"]
    logger = ctx.lifespan_context["logger"]
    logger.info("browser_type", selector=params.selector)
    page = state.page
    await page.fill(params.selector, params.text)
    return TypeResult(message=f"Typed into {params.selector}")


async def browser_fill_form(ctx: Context, params: FillFormInput) -> FillFormResult:
    """Fill multiple form fields at once. Pass a JSON object mapping CSS selectors to values, e.g. {\"#email\": \"user@example.com\", \"#password\": \"secret\"}."""
    state: BrowserState = ctx.lifespan_context["browser_state"]
    logger = ctx.lifespan_context["logger"]
    logger.info("browser_fill_form", keys=list(params.fields.keys()))
    page = state.page
    for selector, value in params.fields.items():
        await page.fill(selector, value)
    return FillFormResult(message=f"Filled {len(params.fields)} field(s)")


async def add(a, b):
    return a + b


def register_interaction_tools(mcp: object) -> None:
    """Register interaction tools with the FastMCP server."""
    mcp.add_tool(browser_click)
    mcp.add_tool(browser_type)
    mcp.add_tool(browser_fill_form)
    mcp.add_tool(add)
