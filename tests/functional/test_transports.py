"""Functional tests that start the real server process.

Skipped unless ``EPR_MCP_FUNCTIONAL=1`` is set, since they spawn subprocesses
and bind a local port. EPR itself is not needed: the tests only list tools.
"""

import asyncio
import os
import socket
import subprocess
import sys
import time

import httpx2
import pytest  # type: ignore
from fastmcp import Client
from fastmcp.client.transports import StdioTransport

pytestmark = pytest.mark.skipif(os.environ.get("EPR_MCP_FUNCTIONAL") != "1", reason="set EPR_MCP_FUNCTIONAL=1 to run")

EXPECTED_TOOL_COUNT = 9


def free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def test_stdio_transport_lists_tools():
    transport = StdioTransport(
        command=sys.executable,
        args=["-m", "epr_mcp.main", "start", "--transport", "stdio", "--url", "http://127.0.0.1:9"],
    )

    async def go():
        async with Client(transport) as client:
            return await client.list_tools()

    assert len(asyncio.run(go())) == EXPECTED_TOOL_COUNT


def test_http_transport_serves_health_and_tools():
    port = free_port()
    proc = subprocess.Popen(
        [
            sys.executable, "-m", "epr_mcp.main", "start",
            "--transport", "http", "--host", "127.0.0.1", "--port", str(port),
            "--url", "http://127.0.0.1:9",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )  # fmt: skip
    try:
        deadline = time.time() + 30
        while True:
            try:
                if httpx2.get(f"http://127.0.0.1:{port}/health").status_code == 200:
                    break
            except httpx2.TransportError:
                pass
            assert proc.poll() is None, "server exited early"
            assert time.time() < deadline, "server did not become healthy"
            time.sleep(0.2)

        async def go():
            async with Client(f"http://127.0.0.1:{port}/mcp") as client:
                return await client.list_tools()

        assert len(asyncio.run(go())) == EXPECTED_TOOL_COUNT
    finally:
        proc.terminate()
        proc.wait(timeout=10)
