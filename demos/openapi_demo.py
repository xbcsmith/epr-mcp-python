#!/usr/bin/env python3
# SPDX-FileCopyrightText: © 2025 Brett Smith <xbcsmith@gmail.com>
# SPDX-License-Identifier: Apache-2.0

"""Show the HTTP side of the EPR MCP server: health, OpenAPI documents, Swagger UI, and tools.

The demo starts the server over HTTP on a free local port (or uses one you point it
at), fetches each endpoint, then connects an MCP client and lists the tools. It does
not need a running EPR: listing tools never calls EPR.

Usage:
    uv run python demos/openapi_demo.py
    uv run python demos/openapi_demo.py --url http://localhost:8000

Exits 0 when every step works, 1 otherwise.
"""

import argparse
import asyncio
import contextlib
import socket
import subprocess
import sys
import time
from collections.abc import Iterator

import httpx2
import yaml
from fastmcp import Client

HTTP_METHODS = {"get", "post", "put", "patch", "delete"}


def step(number: int, total: int, title: str) -> None:
    """Print a numbered step heading.

    Args:
        number: The step number.
        total: The number of steps.
        title: What the step does.

    Examples:
        ``step(1, 5, 'Health check')``
    """
    print(f"\n[{number}/{total}] {title}")


def free_port() -> int:
    """Find a free local TCP port.

    Returns:
        A port number that was free a moment ago.

    Examples:
        >>> 1024 <= free_port() <= 65535
        True
    """
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


@contextlib.contextmanager
def running_server(port: int, epr_url: str) -> Iterator[subprocess.Popen]:
    """Run the MCP server over HTTP in a child process for the duration of a with block.

    Args:
        port: The port to bind on 127.0.0.1.
        epr_url: The EPR URL given to the server; it is not contacted.

    Yields:
        The running process. It is terminated when the block ends.

    Examples:
        ``with running_server(free_port(), 'http://localhost:8042') as server: ...``
    """
    command = [
        sys.executable, "-m", "epr_mcp.main", "start",
        "--transport", "http", "--host", "127.0.0.1", "--port", str(port),
        "--url", epr_url,
    ]  # fmt: skip
    with subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) as process:
        try:
            yield process
        finally:
            process.terminate()
            process.wait(timeout=10)


def wait_until_healthy(base_url: str, server: subprocess.Popen | None, timeout: float = 30) -> None:
    """Wait until the server answers its health check.

    Args:
        base_url: The server's base URL.
        server: The child process, if the demo started it, so an early exit is noticed.
        timeout: Seconds to wait.

    Raises:
        RuntimeError: If the process exits early or the server is not healthy in time.

    Examples:
        ``wait_until_healthy('http://127.0.0.1:8000', None)``
    """
    deadline = time.time() + timeout
    while True:
        try:
            if httpx2.get(f"{base_url}/health", timeout=2).status_code == 200:
                return
        except httpx2.TransportError:
            pass
        if server is not None and server.poll() is not None:
            raise RuntimeError("the server process exited before it became healthy")
        if time.time() > deadline:
            raise RuntimeError(f"no healthy server at {base_url} after {timeout:.0f} seconds")
        time.sleep(0.3)


def show_endpoints(base_url: str) -> None:
    """Call the health, OpenAPI, and Swagger endpoints and print what they return.

    Args:
        base_url: The server's base URL.

    Raises:
        httpx2.HTTPError: If an endpoint cannot be reached or answers with an error.

    Examples:
        ``show_endpoints('http://127.0.0.1:8000')``
    """
    step(1, 5, "Health check")
    response = httpx2.get(f"{base_url}/health")
    print(f"GET {base_url}/health -> {response.status_code} {response.text!r}")

    step(2, 5, "OpenAPI specification as YAML")
    response = httpx2.get(f"{base_url}/openapi.yaml")
    response.raise_for_status()
    spec = yaml.safe_load(response.text)
    print(f"GET {base_url}/openapi.yaml -> {response.status_code}")
    print(f"Title: {spec['info']['title']} (OpenAPI {spec['openapi']}, API version {spec['info']['version']})")
    print(f"Paths: {len(spec['paths'])}")
    for path, operations in spec["paths"].items():
        for method, operation in operations.items():
            if method in HTTP_METHODS:
                print(f"  {method.upper():<6} {path:<28} {operation.get('summary', '')}")

    step(3, 5, "The same specification as JSON")
    response = httpx2.get(f"{base_url}/openapi.json")
    response.raise_for_status()
    print(f"GET {base_url}/openapi.json -> {response.status_code}")
    print(f"JSON matches the YAML document: {response.json() == spec}")

    step(4, 5, "Swagger UI")
    response = httpx2.get(f"{base_url}/docs")
    response.raise_for_status()
    print(f"GET {base_url}/docs -> {response.status_code}, {len(response.text)} bytes of HTML")
    print(f"Open {base_url}/docs in a browser to try the API interactively.")


async def show_tools(base_url: str) -> None:
    """Connect an MCP client and list the tools.

    Args:
        base_url: The server's base URL; the MCP endpoint is ``/mcp`` under it.

    Examples:
        ``asyncio.run(show_tools('http://127.0.0.1:8000'))``
    """
    step(5, 5, "MCP tools, listed by a FastMCP client")
    async with Client(f"{base_url}/mcp") as client:
        tools = await client.list_tools()
    print(f"Connected to {base_url}/mcp and found {len(tools)} tools:")
    for tool in tools:
        required = ", ".join(tool.input_schema.get("required", [])) or "none"
        print(f"  {tool.name:<18} required arguments: {required}")


def main() -> int:
    """Parse the command line, start a server if needed, and run the demo.

    Returns:
        0 if every step worked, 1 otherwise.

    Examples:
        ``python demos/openapi_demo.py``
    """
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--url", help="use a server that is already running instead of starting one")
    parser.add_argument(
        "--epr-url", default="http://localhost:8042", help="EPR URL given to the server (not contacted)"
    )
    args = parser.parse_args()

    print("EPR MCP Server: HTTP endpoints demo")
    print("=" * 40)
    try:
        if args.url:
            base_url = args.url.rstrip("/")
            server_context = contextlib.nullcontext(None)
        else:
            port = free_port()
            base_url = f"http://127.0.0.1:{port}"
            print(f"Starting the server on {base_url}")
            server_context = running_server(port, args.epr_url)
        with server_context as server:
            wait_until_healthy(base_url, server)
            show_endpoints(base_url)
            asyncio.run(show_tools(base_url))
    except (RuntimeError, httpx2.HTTPError, KeyError) as error:
        print(f"\nDemo failed: {error!r}", file=sys.stderr)
        return 1
    print("\nDemo completed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
