"""Tests for the eprmcp command line."""

from unittest import mock

import pytest  # type: ignore

from epr_mcp import main


def start(monkeypatch, *args, env=None):
    for key in ("EPR_URL", "EPR_API_TOKEN", "EPR_TOKEN", "MCP_TRANSPORT", "MCP_HOST", "MCP_PORT"):
        monkeypatch.delenv(key, raising=False)
    for key, value in (env or {}).items():
        monkeypatch.setenv(key, value)
    monkeypatch.setattr("sys.argv", ["eprmcp", "start", *args])
    with mock.patch.object(main.server, "run") as run:
        main.main()
    return run.call_args.args[0]


class TestStart:
    def test_defaults(self, monkeypatch):
        cfg = start(monkeypatch)
        assert (cfg.url, cfg.token, cfg.transport, cfg.host, cfg.port) == (
            "http://localhost:8042",
            None,
            "http",
            "0.0.0.0",
            8000,
        )

    def test_flags(self, monkeypatch):
        cfg = start(
            monkeypatch,
            "--url", "http://epr:1",
            "--token", "t",
            "--transport", "stdio",
            "--host", "127.0.0.1",
            "--port", "9001",
            "--debug",
        )  # fmt: skip
        assert (cfg.url, cfg.token, cfg.transport, cfg.host, cfg.port, cfg.debug) == (
            "http://epr:1",
            "t",
            "stdio",
            "127.0.0.1",
            9001,
            True,
        )

    def test_environment_defaults(self, monkeypatch):
        cfg = start(
            monkeypatch,
            env={"EPR_URL": "http://e:2", "MCP_TRANSPORT": "stdio", "MCP_HOST": "1.2.3.4", "MCP_PORT": "7"},
        )
        assert (cfg.url, cfg.transport, cfg.host, cfg.port) == ("http://e:2", "stdio", "1.2.3.4", 7)

    @pytest.mark.parametrize("variable", ["EPR_API_TOKEN", "EPR_TOKEN"])
    def test_token_from_either_environment_variable(self, monkeypatch, variable):
        assert start(monkeypatch, env={variable: "abc"}).token == "abc"

    def test_invalid_transport_exits(self, monkeypatch):
        with pytest.raises(SystemExit):
            start(monkeypatch, "--transport", "sse")


def test_unknown_command_exits(monkeypatch):
    monkeypatch.setattr("sys.argv", ["eprmcp", "bogus"])
    with pytest.raises(SystemExit):
        main.main()


def test_version_prints(monkeypatch, capsys):
    monkeypatch.setattr("sys.argv", ["eprmcp", "version"])
    main.main()
    assert "epr-mcp" in capsys.readouterr().out
