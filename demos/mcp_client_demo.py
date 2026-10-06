#!/usr/bin/env python3
# SPDX-FileCopyrightText: © 2025 Brett Smith <xbcsmith@gmail.com>
# SPDX-License-Identifier: Apache-2.0

"""Use the EPR MCP server the way an AI assistant does: through an MCP client.

The demo connects a FastMCP 4 client, lists the tools, then creates an event
receiver, creates an event for it, fetches the event, and searches for it. It
changes data in EPR: each run adds one receiver and one event with a unique name.

By default the client starts the server itself over stdio (the way editors do).
Use --server-url to talk to a server that is already running over HTTP.

Usage:
    uv run python demos/mcp_client_demo.py
    uv run python demos/mcp_client_demo.py --epr-url http://localhost:8042
    uv run python demos/mcp_client_demo.py --server-url http://localhost:8000/mcp

Exits 0 when every step works, 1 otherwise.
"""

import argparse
import asyncio
import json
import os
import sys
import time
from pathlib import Path

from fastmcp import Client
from fastmcp.client.transports import StdioTransport

TOTAL_STEPS = 6


class DemoError(Exception):
    """A step of the demo did not work."""


def step(number: int, title: str) -> None:
    print(f"\n[{number}/{TOTAL_STEPS}] {title}")


def shorten(text: str, width: int = 100) -> str:
    text = " ".join(text.split())
    return text if len(text) <= width else text[: width - 3] + "..."


async def call(client: Client, tool: str, arguments: dict, expect_error: bool = False) -> str:
    """Call a tool and return its text.

    The server reports most problems as plain text instead of an MCP error, so a reply
    that is not JSON counts as a failure unless the caller expects one.
    """
    print(f"  tool: {tool}")
    print(f"  arguments: {shorten(json.dumps(arguments), 140)}")
    result = await client.call_tool(tool, arguments, raise_on_error=False)
    text = result.content[0].text if result.content else ""
    if result.is_error:
        raise DemoError(f"{tool} failed: {shorten(text, 300)}")
    print(f"  result: {shorten(text)}")
    if not expect_error and not text.lstrip().startswith(("{", "[")):
        raise DemoError(f"{tool} returned an error: {shorten(text, 300)}")
    return text


def make_client(args: argparse.Namespace) -> Client:
    if args.server_url:
        return Client(args.server_url)
    env = {**os.environ, "EPR_URL": args.epr_url}
    transport = StdioTransport(
        command=sys.executable,
        args=["-m", "epr_mcp.main", "start", "--transport", "stdio", "--url", args.epr_url],
        env=env,
        log_file=None if args.show_server_logs else Path(os.devnull),
    )
    return Client(transport)


async def run(args: argparse.Namespace) -> None:
    suffix = str(int(time.time()))
    receiver = {
        "name": f"demo.client.{suffix}",
        "type": "demo.client",
        "version": "1.0.0",
        "description": "Receiver created by mcp_client_demo.py",
        "schema": {"type": "object", "properties": {"service": {"type": "string"}}},
    }
    async with make_client(args) as client:
        step(1, "List the tools the server offers")
        tools = await client.list_tools()
        for tool in tools:
            print(f"  {tool.name}")
        if len(tools) != 9:
            raise DemoError(f"expected 9 tools, found {len(tools)}")

        step(2, "Create an event receiver (declares a kind of event and its payload schema)")
        receiver_id = json.loads(await call(client, "create_receiver", {"receiver_data": receiver}))["id"]
        print(f"  new receiver id: {receiver_id}")

        step(3, "Create an event for that receiver")
        event = {
            "name": f"demo-service-{suffix}",
            "version": "1.0.0",
            "release": "2025.10.0",
            "platform_id": "linux",
            "package": "oci",
            "description": "Event created by mcp_client_demo.py",
            "payload": {"service": "demo-service"},
            "success": True,
            "event_receiver_id": receiver_id,
        }
        event_id = json.loads(await call(client, "create_event", {"event_data": event}))["id"]
        print(f"  new event id: {event_id}")

        step(4, "Fetch the event by its ID")
        fetched = json.loads(await call(client, "fetch_event", {"id": event_id}))
        if fetched["id"] != event_id or fetched["name"] != event["name"]:
            raise DemoError("the fetched event is not the one that was created")

        step(5, "Search for the event by name")
        found = json.loads(await call(client, "search_events", {"data": {"name": event["name"]}}))
        if [item["id"] for item in found] != [event_id]:
            raise DemoError(f"expected exactly the new event, found {len(found)} events")

        step(6, "Show that bad input is rejected before it reaches EPR")
        message = await call(client, "fetch_event", {"id": "not-a-valid-id"}, expect_error=True)
        if not message.startswith("Input validation error"):
            raise DemoError("a malformed ID was accepted")
        print("  rejected as expected: the server never called EPR")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--epr-url", default=os.environ.get("EPR_URL", "http://localhost:8042"), help="EPR URL")
    parser.add_argument("--server-url", help="MCP server over HTTP, for example http://localhost:8000/mcp")
    parser.add_argument("--show-server-logs", action="store_true", help="show the stdio server's log output")
    args = parser.parse_args()

    print("EPR MCP Server: client demo")
    print("=" * 40)
    try:
        asyncio.run(run(args))
    except DemoError as error:
        print(f"\nDemo failed: {error}", file=sys.stderr)
        return 1
    except Exception as error:
        print(f"\nDemo failed: {error!r}", file=sys.stderr)
        return 1
    print("\nDemo completed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
