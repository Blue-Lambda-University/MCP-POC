"""Pydantic schemas for tool inputs and outputs. No server or browser dependencies."""

from playwright_mcp.schemas.interaction import (
    ClickInput,
    ClickResult,
    FillFormInput,
    FillFormResult,
    TypeInput,
    TypeResult,
)
from playwright_mcp.schemas.navigation import (
    NavigateInput,
    NavigateResult,
    SnapshotResult,
    TabInfo,
    TabsResult,
)
from playwright_mcp.schemas.scraping import (
    LinkItem,
    ScrapeInput,
    ScrapeLinksResult,
    ScrapeTextResult,
)
from playwright_mcp.schemas.screenshots import ScreenshotInput, ScreenshotResult

__all__ = [
    "ClickInput",
    "ClickResult",
    "FillFormInput",
    "FillFormResult",
    "TypeInput",
    "TypeResult",
    "NavigateInput",
    "NavigateResult",
    "SnapshotResult",
    "TabInfo",
    "TabsResult",
    "LinkItem",
    "ScrapeInput",
    "ScrapeLinksResult",
    "ScrapeTextResult",
    "ScreenshotInput",
    "ScreenshotResult",
]
