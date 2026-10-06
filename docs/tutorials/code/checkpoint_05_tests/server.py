# SPDX-FileCopyrightText: © 2025 Brett Smith <xbcsmith@gmail.com>
# SPDX-License-Identifier: Apache-2.0

"""EPR workshop MCP server, checkpoint 04: validation and error handling."""

import json
import logging
import os
import sys
from typing import Annotated, Any

import httpx2
from fastmcp import FastMCP
from fastmcp.exceptions import ToolError
from pydantic import BaseModel, ConfigDict, Field

# stdout carries the MCP protocol over stdio, so all logging goes to stderr.
logging.basicConfig(
    stream=sys.stderr,
    level=logging.DEBUG if os.environ.get("EPR_DEBUG") else logging.INFO,
    format="%(asctime)s %(name)s:[%(levelname)s] %(message)s",
)
logger = logging.getLogger("epr_workshop")

EPR_URL = os.environ.get("EPR_URL", "http://localhost:8042")
EPR_TOKEN = os.environ.get("EPR_TOKEN")

mcp = FastMCP(name="EPR Workshop MCP Server", version="0.4.0")

# --- Input types -----------------------------------------------------------
# FastMCP turns these annotations into the JSON schema the AI client sees, and
# validates every call against them before your function runs.

EprId = Annotated[str, Field(pattern=r"^[0-9A-Za-z]{26}$", description="26 character ULID of the record")]


class StrictModel(BaseModel):
    """Base for tool inputs: unknown fields are errors, not silently dropped."""

    model_config = ConfigDict(extra="forbid", populate_by_name=True)


class EventSearch(StrictModel):
    name: str | None = Field(None, description="Event name")
    version: str | None = Field(None, description="Event version")
    release: str | None = Field(None, description="Release")
    platform_id: str | None = Field(None, description="Platform identifier")
    package: str | None = Field(None, description="Package type, for example oci")
    description: str | None = Field(None, description="Event description")
    success: bool | None = Field(None, description="Whether the event succeeded")
    event_receiver_id: EprId | None = Field(None, description="ID of the receiving event receiver")


class ReceiverSearch(StrictModel):
    name: str | None = Field(None, description="Receiver name")
    type: str | None = Field(None, description="Receiver type")
    version: str | None = Field(None, description="Receiver version")
    description: str | None = Field(None, description="Receiver description")


class GroupSearch(ReceiverSearch):
    """Groups are searched by the same fields as receivers."""


class EventCreate(StrictModel):
    name: str = Field(description="Event name")
    version: str = Field(description="Event version")
    release: str = Field(description="Release")
    platform_id: str = Field(description="Platform identifier")
    package: str = Field(description="Package type, for example oci")
    description: str = Field(description="Event description")
    payload: dict[str, Any] = Field(description="Event payload; must match the receiver schema")
    success: bool = Field(description="Whether the event succeeded")
    event_receiver_id: EprId = Field(description="ID of the receiving event receiver")


class ReceiverCreate(StrictModel):
    name: str = Field(description="Receiver name")
    type: str = Field(description="Receiver type")
    version: str = Field(description="Receiver version")
    description: str = Field(description="Receiver description")
    schema_: dict[str, Any] = Field(alias="schema", description="JSON schema that event payloads must match")


class GroupCreate(StrictModel):
    name: str = Field(description="Group name")
    type: str = Field(description="Group type")
    version: str = Field(description="Group version")
    description: str = Field(description="Group description")
    event_receiver_ids: list[EprId] = Field(min_length=1, description="IDs of the receivers in the group")


# --- Talking to EPR --------------------------------------------------------


def new_client() -> httpx2.AsyncClient:
    """Create an HTTP client for EPR, with the bearer token when one is set."""
    headers = {"Authorization": f"Bearer {EPR_TOKEN}"} if EPR_TOKEN else {}
    return httpx2.AsyncClient(base_url=EPR_URL, headers=headers)


def describe_error(error: Exception, operation: str) -> str:
    """Turn an httpx2 exception into a message an AI client can act on."""
    if isinstance(error, httpx2.TimeoutException):
        return f"Request to EPR at {EPR_URL} timed out. ({error})"
    if isinstance(error, httpx2.TransportError):
        # Connection refused, reset, or dropped: the name says which, the message may be empty.
        return f"Cannot reach EPR at {EPR_URL}. Is the EPR server running? ({type(error).__name__}: {error})"
    if isinstance(error, httpx2.HTTPStatusError):
        return f"EPR returned {error.response.status_code} for {operation}: {error.response.text}"
    return f"Unexpected error in {operation}: {error}"


async def epr_request(operation: str, method: str, path: str, body: Any = None) -> str:
    """Call EPR and return the body; failures become ToolError, which MCP marks as errors."""
    logger.debug("%s: %s %s", operation, method, path)
    try:
        async with new_client() as client:
            response = await client.request(method, path, json=body)
            response.raise_for_status()
    except httpx2.HTTPError as error:
        message = describe_error(error, operation)
        logger.error(message)
        raise ToolError(message) from error
    # EPR can answer 200 and still report a failure in the body: {"data": null, "errors": [...]}.
    try:
        errors = json.loads(response.text).get("errors")
    except (ValueError, AttributeError):
        errors = None
    if errors:
        details = "; ".join(str(e.get("message", e)) if isinstance(e, dict) else str(e) for e in errors)
        message = f"EPR reported an error for {operation}: {details}"
        logger.error(message)
        raise ToolError(message)
    return response.text


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


async def search(operation: str, criteria: BaseModel) -> str:
    """Run one of the GraphQL searches in SEARCHES, sending only the criteria that were set."""
    input_type, argument, fields = SEARCHES[operation]
    query = f"query ($obj: {input_type}){{{operation}({argument}: $obj) {{ {','.join(fields)} }}}}"
    variables = {"obj": criteria.model_dump(exclude_none=True)}
    return await epr_request(
        f"search {operation}", "POST", "/api/v1/graphql/query", {"query": query, "variables": variables}
    )


# --- Tools -----------------------------------------------------------------


@mcp.tool(title="Fetch Event", description="Fetch an event from EPR by its ID")
async def fetch_event(id: EprId) -> str:
    """Fetch an event from the EPR."""
    return await epr_request("fetch_event", "GET", f"/api/v1/events/{id}")


@mcp.tool(title="Fetch Event Receiver", description="Fetch an event receiver from EPR by its ID")
async def fetch_receiver(id: EprId) -> str:
    """Fetch an event receiver from the EPR."""
    return await epr_request("fetch_receiver", "GET", f"/api/v1/receivers/{id}")


@mcp.tool(title="Fetch Event Receiver Group", description="Fetch an event receiver group from EPR by its ID")
async def fetch_group(id: EprId) -> str:
    """Fetch an event receiver group from the EPR."""
    return await epr_request("fetch_group", "GET", f"/api/v1/groups/{id}")


@mcp.tool(title="Search Events", description="Search for events; every criterion is optional")
async def search_events(data: EventSearch) -> str:
    """Search for events in the EPR."""
    return await search("events", data)


@mcp.tool(title="Search Event Receivers", description="Search for event receivers; every criterion is optional")
async def search_receivers(data: ReceiverSearch) -> str:
    """Search for event receivers in the EPR."""
    return await search("event_receivers", data)


@mcp.tool(
    title="Search Event Receiver Groups", description="Search for event receiver groups; every criterion is optional"
)
async def search_groups(data: GroupSearch) -> str:
    """Search for event receiver groups in the EPR."""
    return await search("event_receiver_groups", data)


@mcp.tool(title="Create Event", description="Create a new event in EPR")
async def create_event(event_data: EventCreate) -> str:
    """Create a new event in the EPR."""
    return await epr_request("create_event", "POST", "/api/v1/events", event_data.model_dump())


@mcp.tool(title="Create Event Receiver", description="Create a new event receiver in EPR")
async def create_receiver(receiver_data: ReceiverCreate) -> str:
    """Create a new event receiver in the EPR."""
    return await epr_request("create_receiver", "POST", "/api/v1/receivers", receiver_data.model_dump(by_alias=True))


@mcp.tool(title="Create Event Receiver Group", description="Create a new event receiver group in EPR")
async def create_group(group_data: GroupCreate) -> str:
    """Create a new event receiver group in the EPR."""
    return await epr_request("create_group", "POST", "/api/v1/groups", group_data.model_dump())


if __name__ == "__main__":
    logger.info("EPR URL: %s (token configured: %s)", EPR_URL, bool(EPR_TOKEN))
    mcp.run(show_banner=False)
