#!/usr/bin/env python3
# SPDX-FileCopyrightText: © 2025 Brett Smith <xbcsmith@gmail.com>
# SPDX-License-Identifier: Apache-2.0

"""Terminal MCP client for the workshop servers.

Use it when an editor or the Inspector will not cooperate: it starts a server
over stdio exactly as they do, then lists tools or calls one.

Usage:
    uv run python client.py list checkpoint_03_tool_set/server.py
    uv run python client.py call checkpoint_03_tool_set/server.py fetch_event '{"id": "<event id>"}'
"""

import argparse
import asyncio
import json
import sys
from pathlib import Path

from fastmcp import Client
from fastmcp.client.transports import StdioTransport


async def run(server: Path, tool: str | None, arguments: dict) -> int:
    transport = StdioTransport(command=sys.executable, args=[str(server)])
    async with Client(transport) as client:
        if tool is None:
            for item in await client.list_tools():
                print(f"{item.name}: {item.description}")
            return 0
        result = await client.call_tool(tool, arguments, raise_on_error=False)
        print(result.content[0].text if result.content else result.data)
        return 1 if result.is_error else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    list_parser = sub.add_parser("list", help="list the tools a server exposes")
    list_parser.add_argument("server", type=Path)
    call_parser = sub.add_parser("call", help="call one tool")
    call_parser.add_argument("server", type=Path)
    call_parser.add_argument("tool")
    call_parser.add_argument("arguments", nargs="?", default="{}", help="tool arguments as a JSON object")
    args = parser.parse_args()
    if args.command == "list":
        return asyncio.run(run(args.server, None, {}))
    return asyncio.run(run(args.server, args.tool, json.loads(args.arguments)))


if __name__ == "__main__":
    sys.exit(main())
