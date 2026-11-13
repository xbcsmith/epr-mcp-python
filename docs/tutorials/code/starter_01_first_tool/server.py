# SPDX-FileCopyrightText: © 2025 Brett Smith <xbcsmith@gmail.com>
# SPDX-License-Identifier: Apache-2.0

"""EPR workshop MCP server, module 01 starter: add your first tool.

This file has the imports and the server instance ready.
Your job in module 01 is to add the fetch_event tool below.
"""

import os

import httpx2  # noqa: F401 -- you will use this when you write the tool
from fastmcp import FastMCP

EPR_URL = os.environ.get("EPR_URL", "http://localhost:8042")

mcp = FastMCP(name="EPR Workshop MCP Server", version="0.1.0")

# TODO: register fetch_event here.
#
# Shape:
#   @mcp.tool(title="Fetch Event", description="Fetch an event from EPR by its ID")
#   async def fetch_event(id: str) -> str:
#       async with httpx2.AsyncClient() as client:
#           response = await client.get(f"{EPR_URL}/api/v1/events/{id}")
#           return response.text


if __name__ == "__main__":
    # Default transport is stdio: the editor or Inspector starts this process
    # and talks to it over stdin and stdout.
    mcp.run(show_banner=False)
