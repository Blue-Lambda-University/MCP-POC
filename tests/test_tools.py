"""Tests for tools (with mocked browser context)."""

import pytest

from playwright_mcp.schemas import NavigateInput, NavigateResult
from playwright_mcp.tools.navigation import browser_navigate


@pytest.fixture
def mock_ctx():
    """Minimal mock Context with fake page that records goto calls."""
    class FakeResponse:
        status = 200
        status_text = "OK"

    class FakePage:
        def __init__(self):
            self._last_url = None

        async def goto(self, url, wait_until=None):
            self._last_url = url
            return FakeResponse()

    class MockContext:
        lifespan_context = {
            "browser_state": type("State", (), {"page": FakePage()})(),
            "logger": type("Logger", (), {"info": lambda *a, **k: None})(),
        }

    return MockContext()


@pytest.mark.asyncio
async def test_browser_navigate_returns_navigate_result(mock_ctx):
    """browser_navigate accepts NavigateInput and returns NavigateResult."""
    params = NavigateInput(url="https://example.com")
    result = await browser_navigate(mock_ctx, params)
    assert isinstance(result, NavigateResult)
    assert "example.com" in result.message
    state = mock_ctx.lifespan_context["browser_state"]
    assert state.page._last_url == "https://example.com"
