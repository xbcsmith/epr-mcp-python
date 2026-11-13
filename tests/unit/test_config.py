# SPDX-FileCopyrightText: © 2025 Brett Smith <xbcsmith@gmail.com>
# SPDX-License-Identifier: Apache-2.0

"""Unit tests for epr_mcp.config."""

import pytest  # type: ignore

from epr_mcp.config import TRANSPORTS, Config


class TestConfig:
    """Tests for the Config data class."""

    def test_defaults_match_the_documented_values(self):
        """Test defaults match the documented values."""
        cfg = Config(url="http://epr")
        assert (cfg.token, cfg.debug, cfg.transport, cfg.host, cfg.port) == (None, False, "http", "0.0.0.0", 8000)

    def test_as_dict_contains_every_field(self):
        """Test as dict contains every field."""
        data = Config(url="http://epr", token="t", port=9000).as_dict()
        assert data == {
            "url": "http://epr",
            "token": "t",
            "debug": False,
            "transport": "http",
            "host": "0.0.0.0",
            "port": 9000,
        }

    @pytest.mark.parametrize("transport", TRANSPORTS)
    def test_every_listed_transport_is_accepted_by_the_data_class(self, transport):
        """Test every listed transport is accepted by the data class."""
        assert Config(url="http://epr", transport=transport).transport == transport

    def test_transports_are_http_and_stdio(self):
        """Test transports are http and stdio."""
        assert set(TRANSPORTS) == {"http", "stdio"}
