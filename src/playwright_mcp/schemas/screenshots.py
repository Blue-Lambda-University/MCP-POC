"""Input/output schemas for screenshot tool."""

from pydantic import BaseModel, Field


class ScreenshotInput(BaseModel):
    """Input for taking a screenshot."""

    selector: str | None = Field(
        default=None,
        description="Optional CSS selector to capture only that element",
    )
    full_page: bool = Field(
        default=False,
        description="If True, capture the full scrollable page; ignored when selector is set",
    )


class ScreenshotResult(BaseModel):
    """Result of a screenshot: base64 PNG or an error message."""

    image_base64: str | None = Field(
        default=None,
        description="Base64-encoded PNG image data",
    )
    error: str | None = Field(
        default=None,
        description="Error message if screenshot failed (e.g. selector not found)",
    )
