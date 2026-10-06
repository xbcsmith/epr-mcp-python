"""Unit tests for HTTP error handling and the httpx2 migration."""

import asyncio
import re
from pathlib import Path

import httpx2
import pytest  # type: ignore

from epr_mcp.config import Config
from epr_mcp.server import handle_http_errors


class FakeContext:
    """Minimal stand-in for the FastMCP context that records error calls."""

    def __init__(self):
        self.errors = []

    async def error(self, message):
        self.errors.append(message)


@pytest.fixture
def cfg():
    return Config(url="http://epr.test:8042", token=None)


def run_handler(error, cfg, operation="fetch_event"):
    ctx = FakeContext()
    message = asyncio.run(handle_http_errors(ctx, error, operation, cfg))
    return ctx, message


class TestHandleHttpErrors:
    """Test handle_http_errors with httpx2 exception types."""

    def test_connect_error(self, cfg):
        ctx, message = run_handler(httpx2.ConnectError("refused"), cfg)
        assert "Connection failed to EPR server at http://epr.test:8042" in message
        assert "refused" in message
        assert len(ctx.errors) == 1

    def test_timeout_error(self, cfg):
        ctx, message = run_handler(httpx2.ReadTimeout("too slow"), cfg)
        assert message.startswith("Request timeout to EPR server at http://epr.test:8042")
        assert len(ctx.errors) == 1

    def test_http_status_error(self, cfg):
        request = httpx2.Request("GET", "http://epr.test:8042/api/v1/events/1")
        response = httpx2.Response(500, text="boom", request=request)
        error = httpx2.HTTPStatusError("server error", request=request, response=response)
        ctx, message = run_handler(error, cfg)
        assert message == "HTTP error from EPR server: 500 - boom"
        assert len(ctx.errors) == 1

    def test_generic_error(self, cfg):
        ctx, message = run_handler(RuntimeError("unexpected"), cfg, operation="create_event")
        assert message == "Error in create_event: unexpected"
        assert len(ctx.errors) == 1


class TestNoLegacyHttpx:
    """Guard against reintroducing the legacy httpx package."""

    def test_src_does_not_import_httpx(self):
        src = Path(__file__).resolve().parents[2] / "src" / "epr_mcp"
        pattern = re.compile(r"^\s*(import httpx|from httpx)\b(?!2)", re.MULTILINE)
        offenders = [str(p) for p in src.rglob("*.py") if pattern.search(p.read_text())]
        assert offenders == []
