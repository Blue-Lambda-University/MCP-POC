"""Pytest fixtures and test configuration."""

import pytest


@pytest.fixture
def anyio_backend() -> str:
    """Use asyncio as the backend for anyio (if used)."""
    return "asyncio"
