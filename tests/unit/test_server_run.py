"""Tests for server.run transport selection."""

import logging
from unittest import mock

import pytest  # type: ignore
from fastmcp import FastMCP

from epr_mcp import server
from epr_mcp.config import Config


@pytest.fixture
def fake_run():
    with mock.patch.object(FastMCP, "run") as run:
        yield run


class TestRun:
    def test_http_transport_uses_configured_host_and_port(self, fake_run):
        server.run(Config(url="http://epr", host="127.0.0.1", port=9000))
        fake_run.assert_called_once_with(transport="http", host="127.0.0.1", port=9000)

    def test_stdio_transport_hides_banner(self, fake_run):
        server.run(Config(url="http://epr", transport="stdio"))
        fake_run.assert_called_once_with(transport="stdio", show_banner=False)

    def test_unknown_transport_is_rejected(self, fake_run):
        with pytest.raises(ValueError, match="Unsupported transport"):
            server.run(Config(url="http://epr", transport="sse"))
        fake_run.assert_not_called()

    def test_token_is_never_logged(self, fake_run, caplog):
        with caplog.at_level(logging.DEBUG, logger="epr_mcp.server"):
            server.run(Config(url="http://epr", token="super-secret"))
        assert "super-secret" not in caplog.text
        assert "EPR Token configured: True" in caplog.text

    def test_debug_flag_sets_debug_logging(self, fake_run):
        previous = server.logger.level
        try:
            with mock.patch.object(server.sys, "excepthook"):
                server.run(Config(url="http://epr", debug=True))
            assert server.logger.level == logging.DEBUG
        finally:
            server.logger.setLevel(previous)
