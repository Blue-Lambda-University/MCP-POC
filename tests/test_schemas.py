"""Tests for Pydantic schemas (no browser required)."""

import pytest

from playwright_mcp.schemas import (
    ClickInput,
    NavigateInput,
    NavigateResult,
    ScrapeInput,
    ScreenshotInput,
    TabInfo,
    TabsResult,
)


class TestNavigateInput:
    def test_requires_url(self):
        n = NavigateInput(url="https://example.com")
        assert n.url == "https://example.com"


class TestNavigateResult:
    def test_message_required(self):
        r = NavigateResult(message="OK")
        assert r.message == "OK"


class TestClickInput:
    def test_selector_required(self):
        c = ClickInput(selector="button.submit")
        assert c.selector == "button.submit"


class TestScrapeInput:
    def test_defaults(self):
        s = ScrapeInput()
        assert s.url is None
        assert s.selector is None
        assert s.format == "text"
        assert s.max_length == 100_000

    def test_format_literal(self):
        for fmt in ("text", "html", "links"):
            s = ScrapeInput(format=fmt)
            assert s.format == fmt


class TestScreenshotInput:
    def test_defaults(self):
        s = ScreenshotInput()
        assert s.selector is None
        assert s.full_page is False


class TestTabInfo:
    def test_fields(self):
        t = TabInfo(index=0, url="https://a.com", title="A")
        assert t.index == 0
        assert t.url == "https://a.com"
        assert t.title == "A"


class TestTabsResult:
    def test_tabs_list(self):
        tabs = [TabInfo(index=0, url="https://a.com", title="A")]
        r = TabsResult(tabs=tabs)
        assert len(r.tabs) == 1
        assert r.tabs[0].url == "https://a.com"
