# SPDX-FileCopyrightText: © 2025 Brett Smith <xbcsmith@gmail.com>
# SPDX-License-Identifier: Apache-2.0

"""Tests for the helper functions in the OpenAPI and MCP client demos."""

import argparse
import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest  # type: ignore

DEMOS = Path(__file__).resolve().parents[2] / "demos"


def load(name: str):
    """Import a demo script as a module."""
    spec = importlib.util.spec_from_file_location(f"demo_helpers_{name}", DEMOS / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TestOpenapiDemoHelpers:
    """Tests for the helpers in openapi_demo.py."""

    def test_free_port_is_usable(self):
        """Test free port is usable."""
        demo = load("openapi_demo")
        assert 1024 <= demo.free_port() <= 65535

    def test_wait_until_healthy_fails_if_the_server_process_exits(self):
        """Test wait until healthy fails if the server process exits."""
        demo = load("openapi_demo")
        with subprocess.Popen([sys.executable, "-c", "pass"]) as process:
            process.wait()
            with pytest.raises(RuntimeError, match="exited before"):
                demo.wait_until_healthy("http://127.0.0.1:9", process, timeout=5)

    def test_wait_until_healthy_times_out_without_a_process(self):
        """Test wait until healthy times out without a process."""
        demo = load("openapi_demo")
        with pytest.raises(RuntimeError, match="no healthy server"):
            demo.wait_until_healthy("http://127.0.0.1:9", None, timeout=0.5)

    def test_running_server_terminates_the_child_when_the_block_ends(self):
        """Test running server terminates the child when the block ends."""
        demo = load("openapi_demo")
        with demo.running_server(demo.free_port(), "http://127.0.0.1:9") as process:
            assert process.poll() is None
        assert process.poll() is not None

    def test_main_returns_one_for_an_unreachable_server_url(self, monkeypatch, capsys):
        """Test main returns one for an unreachable server url."""
        demo = load("openapi_demo")
        monkeypatch.setattr(sys, "argv", ["openapi_demo.py", "--url", "http://127.0.0.1:9"])
        monkeypatch.setattr(demo.time, "sleep", lambda seconds: None)
        monkeypatch.setattr(demo, "wait_until_healthy", lambda *a, **k: (_ for _ in ()).throw(RuntimeError("down")))
        assert demo.main() == 1
        assert "Demo failed" in capsys.readouterr().err


class TestClientDemoHelpers:
    """Tests for the helpers in mcp_client_demo.py."""

    def test_make_client_uses_http_for_a_server_url(self):
        """Test make client uses http for a server url."""
        demo = load("mcp_client_demo")
        args = argparse.Namespace(server_url="http://127.0.0.1:8000/mcp", epr_url="http://epr", show_server_logs=False)
        assert type(demo.make_client(args).transport).__name__ == "StreamableHttpTransport"

    def test_make_client_uses_stdio_without_a_server_url(self):
        """Test make client uses stdio without a server url."""
        demo = load("mcp_client_demo")
        args = argparse.Namespace(server_url=None, epr_url="http://epr", show_server_logs=False)
        assert type(demo.make_client(args).transport).__name__ == "StdioTransport"

    def test_step_prints_a_numbered_heading(self, capsys):
        """Test step prints a numbered heading."""
        demo = load("mcp_client_demo")
        demo.step(2, "Create a receiver")
        assert "[2/6] Create a receiver" in capsys.readouterr().out

    def test_main_returns_one_when_the_demo_fails(self, monkeypatch, capsys):
        """Test main returns one when the demo fails."""
        demo = load("mcp_client_demo")

        async def fail(args):
            raise demo.DemoError("boom")

        monkeypatch.setattr(sys, "argv", ["mcp_client_demo.py"])
        monkeypatch.setattr(demo, "run", fail)
        assert demo.main() == 1
        assert "boom" in capsys.readouterr().err
