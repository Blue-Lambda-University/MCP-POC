"""Input/output schemas for scraping tools."""

from typing import Literal

from pydantic import BaseModel, Field


class ScrapeInput(BaseModel):
    """Input for scraping content from the current page or a URL."""

    url: str | None = Field(
        default=None,
        description="Optional URL to navigate to before scraping; if omitted, uses current page",
    )
    selector: str | None = Field(
        default=None,
        description="Optional CSS selector to scrape only that element (e.g. 'article', '#content')",
    )
    format: Literal["text", "html", "links"] = Field(
        default="text",
        description="Output format: 'text' (plain text), 'html' (raw HTML), or 'links' (list of {href, text})",
    )
    wait_selector: str | None = Field(
        default=None,
        description="Optional CSS selector to wait for before scraping (for JS-rendered content)",
    )
    wait_ms: int | None = Field(
        default=None,
        description="Optional delay in milliseconds before scraping",
    )
    max_length: int = Field(
        default=100_000,
        ge=1,
        le=1_000_000,
        description="Maximum characters to return for text/html output",
    )


class LinkItem(BaseModel):
    """A single link extracted from a page."""

    href: str = Field(..., description="Link URL")
    text: str = Field(..., description="Link text (truncated if long)")


class ScrapeTextResult(BaseModel):
    """Result of scraping when format is 'text' or 'html'."""

    content: str = Field(..., description="Extracted text or HTML (may be truncated)")


class ScrapeLinksResult(BaseModel):
    """Result of scraping when format is 'links'."""

    links: list[LinkItem] = Field(..., description="List of links (href, text)")
