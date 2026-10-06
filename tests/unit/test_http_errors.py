"""Unit tests for HTTP error handling and the httpx2 migration."""

import logging
import re
from pathlib import Path

import httpx2
import pytest  # type: ignore

from epr_mcp.config import Config
from epr_mcp.server import handle_http_errors


@pytest.fixture
def cfg():
    return Config(url="http://epr.test:8042", token=None)


class TestHandleHttpErrors:
    """Test handle_http_errors with httpx2 exception types."""

    def test_connect_error(self, cfg, caplog):
        with caplog.at_level(logging.ERROR, logger="epr_mcp.server"):
            message = handle_http_errors(httpx2.ConnectError("refused"), "fetch_event", cfg)
        assert "Connection failed to EPR server at http://epr.test:8042" in message
        assert "refused" in message
        assert "Connection failed to http://epr.test:8042" in caplog.text

    def test_timeout_error(self, cfg, caplog):
        with caplog.at_level(logging.ERROR, logger="epr_mcp.server"):
            message = handle_http_errors(httpx2.ReadTimeout("too slow"), "fetch_event", cfg)
        assert message.startswith("Request timeout to EPR server at http://epr.test:8042")
        assert "Request timeout" in caplog.text

    def test_http_status_error(self, cfg, caplog):
        request = httpx2.Request("GET", "http://epr.test:8042/api/v1/events/1")
        response = httpx2.Response(500, text="boom", request=request)
        error = httpx2.HTTPStatusError("server error", request=request, response=response)
        with caplog.at_level(logging.ERROR, logger="epr_mcp.server"):
            message = handle_http_errors(error, "fetch_event", cfg)
        assert message == "HTTP error from EPR server: 500 - boom"
        assert "HTTP error from" in caplog.text

    def test_generic_error(self, cfg, caplog):
        with caplog.at_level(logging.ERROR, logger="epr_mcp.server"):
            message = handle_http_errors(RuntimeError("unexpected"), "create_event", cfg)
        assert message == "Error in create_event: unexpected"
        assert "Error in create_event" in caplog.text


class TestNoLegacyHttpx:
    """Guard against reintroducing the legacy httpx package."""

    def test_src_does_not_import_httpx(self):
        src = Path(__file__).resolve().parents[2] / "src" / "epr_mcp"
        pattern = re.compile(r"^\s*(import httpx|from httpx)\b(?!2)", re.MULTILINE)
        offenders = [str(p) for p in src.rglob("*.py") if pattern.search(p.read_text())]
        assert offenders == []
