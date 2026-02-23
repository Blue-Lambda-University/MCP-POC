"""FastMCP instance, lifespan, tool registration, and tools UI. No business logic."""

from fastmcp import FastMCP

from playwright_mcp.browser import create_browser_lifespan
from playwright_mcp.server.dependencies import register_all_tools
from playwright_mcp.server.ui import api_tools, tools_ui


def create_app() -> FastMCP:
    """Build the FastMCP app with browser lifespan, all tools, and tools UI routes."""
    mcp = FastMCP(
        name="Playwright MCP",
        instructions=(
            "Browser automation and web scraping. Use the tools to navigate, click, type, "
            "fill forms, take screenshots, and extract content from pages. For data extraction "
            "use browser_scrape with format 'text', 'html', or 'links'."
        ),
        lifespan=create_browser_lifespan,
    )
    register_all_tools(mcp)
    mcp.custom_route("/api/tools", methods=["GET"])(api_tools)
    mcp.custom_route("/tools-ui", methods=["GET"])(tools_ui)
    return mcp
