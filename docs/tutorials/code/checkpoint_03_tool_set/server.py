# SPDX-FileCopyrightText: © 2025 Brett Smith <xbcsmith@gmail.com>
# SPDX-License-Identifier: Apache-2.0

"""EPR workshop MCP server, checkpoint 03: the complete tool set."""

import logging
import os
import sys

import httpx2
from fastmcp import FastMCP

# stdout carries the MCP protocol over stdio, so all logging goes to stderr.
logging.basicConfig(
    stream=sys.stderr,
    level=logging.DEBUG if os.environ.get("EPR_DEBUG") else logging.INFO,
    format="%(asctime)s %(name)s:[%(levelname)s] %(message)s",
)
logger = logging.getLogger("epr_workshop")

EPR_URL = os.environ.get("EPR_URL", "http://localhost:8042")
EPR_TOKEN = os.environ.get("EPR_TOKEN")

mcp = FastMCP(name="EPR Workshop MCP Server", version="0.3.0")


def new_client() -> httpx2.AsyncClient:
    """Create an HTTP client for EPR, with the bearer token when one is set."""
    headers = {"Authorization": f"Bearer {EPR_TOKEN}"} if EPR_TOKEN else {}
    return httpx2.AsyncClient(base_url=EPR_URL, headers=headers)


async def epr_request(method: str, path: str, json: dict | None = None) -> str:
    """Call EPR and return the response body, or a message if EPR said no."""
    logger.debug("%s %s", method, path)
    async with new_client() as client:
        response = await client.request(method, path, json=json)
    if response.is_success:
        return response.text
    return f"EPR returned {response.status_code}: {response.text}"


# Each GraphQL search names the input type, the argument, and the fields to return.
SEARCHES = {
    "events": (
        "FindEventInput!",
        "event",
        ["id", "name", "version", "release", "platform_id", "package", "description", "success", "event_receiver_id"],
    ),
    "event_receivers": (
        "FindEventReceiverInput!",
        "event_receiver",
        ["id", "name", "type", "version", "description"],
    ),
    "event_receiver_groups": (
        "FindEventReceiverGroupInput!",
        "event_receiver_group",
        ["id", "name", "type", "version", "description", "enabled", "event_receiver_ids"],
    ),
}


async def search(operation: str, criteria: dict) -> str:
    """Run one of the GraphQL searches in SEARCHES."""
    input_type, argument, fields = SEARCHES[operation]
    query = f"query ($obj: {input_type}){{{operation}({argument}: $obj) {{ {','.join(fields)} }}}}"
    return await epr_request("POST", "/api/v1/graphql/query", {"query": query, "variables": {"obj": criteria}})


@mcp.tool(title="Fetch Event", description="Fetch an event from EPR by its ID")
async def fetch_event(id: str) -> str:
    """Fetch an event from the EPR."""
    return await epr_request("GET", f"/api/v1/events/{id}")


@mcp.tool(title="Fetch Event Receiver", description="Fetch an event receiver from EPR by its ID")
async def fetch_receiver(id: str) -> str:
    """Fetch an event receiver from the EPR."""
    return await epr_request("GET", f"/api/v1/receivers/{id}")


@mcp.tool(title="Fetch Event Receiver Group", description="Fetch an event receiver group from EPR by its ID")
async def fetch_group(id: str) -> str:
    """Fetch an event receiver group from the EPR."""
    return await epr_request("GET", f"/api/v1/groups/{id}")


@mcp.tool(
    title="Search Events",
    description="Search for events. Criteria: name, version, release, platform_id, package, description, success.",
)
async def search_events(data: dict) -> str:
    """Search for events in the EPR."""
    return await search("events", data)


@mcp.tool(
    title="Search Event Receivers",
    description="Search for event receivers. Criteria: name, type, version, description.",
)
async def search_receivers(data: dict) -> str:
    """Search for event receivers in the EPR."""
    return await search("event_receivers", data)


@mcp.tool(
    title="Search Event Receiver Groups",
    description="Search for event receiver groups. Criteria: name, type, version, description.",
)
async def search_groups(data: dict) -> str:
    """Search for event receiver groups in the EPR."""
    return await search("event_receiver_groups", data)


@mcp.tool(title="Create Event", description="Create a new event in EPR")
async def create_event(event_data: dict) -> str:
    """Create a new event in the EPR."""
    return await epr_request("POST", "/api/v1/events", event_data)


@mcp.tool(title="Create Event Receiver", description="Create a new event receiver in EPR")
async def create_receiver(receiver_data: dict) -> str:
    """Create a new event receiver in the EPR."""
    return await epr_request("POST", "/api/v1/receivers", receiver_data)


@mcp.tool(title="Create Event Receiver Group", description="Create a new event receiver group in EPR")
async def create_group(group_data: dict) -> str:
    """Create a new event receiver group in the EPR."""
    return await epr_request("POST", "/api/v1/groups", group_data)


if __name__ == "__main__":
    logger.info("EPR URL: %s (token configured: %s)", EPR_URL, bool(EPR_TOKEN))
    mcp.run(show_banner=False)
