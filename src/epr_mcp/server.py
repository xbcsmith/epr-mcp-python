# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: © 2025 Brett Smith <xbcsmith@gmail.com>
# SPDX-License-Identifier: Apache-2.0

import logging
import os
import sys

import httpx
from mcp.server.fastmcp import FastMCP

from .errors import debug_except_hook

logger = logging.getLogger(__name__)

debug = os.environ.get("EPR_DEBUG")
if debug:
    sys.excepthook = debug_except_hook
    logger.setLevel(logging.DEBUG)

mcp = FastMCP("epr-mcp")


@mcp.tool(title="Event Fetcher", description="Fetch events from EPR")
async def fetch_event(id: str) -> str:
    """Fetch an event from the EPR"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"http://localhost:8042/api/v1/events/{id}")
        return response.text


@mcp.tool(title="Event Receiver Fetcher", description="Fetch events from EPR")
async def fetch_receiver(id: str) -> str:
    """Fetch an event receiver from the EPR"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"http://localhost:8042/api/v1/receivers/{id}")
        return response.text


@mcp.tool(title="Event Receiver Fetcher", description="Fetch events from EPR")
async def fetch_group(id: str) -> str:
    """Fetch an event receiver group from the EPR"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"http://localhost:8042/api/v1/groups/{id}")
        return response.text


def run(cfg):
    """Run the MCP"""
    logger.info("MCP is running with the following configuration:")
    logger.info(f"URL: {cfg.url}")
    logger.info(f"Token: {cfg.token}")
    mcp.run()
    return "MCP is running"
