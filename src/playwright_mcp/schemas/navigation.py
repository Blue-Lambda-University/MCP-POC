"""Input/output schemas for navigation tools."""

from pydantic import BaseModel, Field


class NavigateInput(BaseModel):
    """Input for navigating the browser to a URL."""

    url: str = Field(..., description="URL to open or navigate to")


class NavigateResult(BaseModel):
    """Result of a navigation action."""

    message: str = Field(..., description="Human-readable navigation result (status, etc.)")


class SnapshotResult(BaseModel):
    """Result of a page snapshot (HTML/content)."""

    content: str = Field(..., description="HTML or text snapshot of the current page (may be truncated)")


class TabInfo(BaseModel):
    """Information about a single browser tab."""

    index: int = Field(..., description="Zero-based tab index")
    url: str = Field(..., description="Tab URL")
    title: str = Field(..., description="Tab title")


class TabsResult(BaseModel):
    """Result of listing browser tabs."""

    tabs: list[TabInfo] = Field(..., description="List of open tabs (pages)")
