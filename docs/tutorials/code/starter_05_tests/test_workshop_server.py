# SPDX-FileCopyrightText: © 2025 Brett Smith <xbcsmith@gmail.com>
# SPDX-License-Identifier: Apache-2.0

"""Tests for the workshop server: no EPR and no network needed.

An in-memory FastMCP client talks to the server, and httpx2.MockTransport plays EPR.

Run from the code directory:
    uv run pytest starter_05_tests

This is the starter skeleton for module 05. One test is already written so
you can run the suite right away and see it pass.  Add the remaining tests
following the same pattern.
"""

import json

import httpx2
import pytest
import server
from fastmcp import Client

EPR_ID = "01JYRZ96R690ZTQ15Q53GEY6E6"
EVENT = {"id": EPR_ID, "name": "checkout-service", "version": "1.2.3"}


@pytest.fixture
def epr(monkeypatch):
    """Replace the EPR client; set epr["respond"] to choose what EPR answers."""
    state = {"requests": [], "respond": lambda request: httpx2.Response(200, json={"data": EVENT})}

    def handler(request):
        state["requests"].append(request)
        return state["respond"](request)

    monkeypatch.setattr(
        server,
        "new_client",
        lambda: httpx2.AsyncClient(base_url="http://epr.test", transport=httpx2.MockTransport(handler)),
    )
    return state


async def call(tool, arguments, raise_on_error=True):
    """Call a tool through an in-memory client."""
    async with Client(server.mcp) as client:
        return await client.call_tool(tool, arguments, raise_on_error=raise_on_error)


@pytest.mark.asyncio
async def test_server_lists_nine_tools():
    """Test server lists nine tools."""
    async with Client(server.mcp) as client:
        names = {tool.name for tool in await client.list_tools()}
    assert names == {
        "fetch_event",
        "fetch_receiver",
        "fetch_group",
        "search_events",
        "search_receivers",
        "search_groups",
        "create_event",
        "create_receiver",
        "create_group",
    }


@pytest.mark.asyncio
async def test_fetch_event_returns_epr_body(epr):
    """Test fetch event returns epr body."""
    result = await call("fetch_event", {"id": EPR_ID})
    assert json.loads(result.content[0].text)["data"]["id"] == EPR_ID
    assert epr["requests"][0].url.path == f"/api/v1/events/{EPR_ID}"


# TODO: test that fetch_event rejects a malformed ID without calling EPR.
#
# Hint: call with raise_on_error=False, then assert result.is_error
# and that epr["requests"] is empty (EPR was never contacted).
#
# @pytest.mark.asyncio
# async def test_fetch_event_rejects_a_malformed_id_without_calling_epr(epr):
#     ...


# TODO: test that search_events sends only the criteria that were given.
#
# Hint: set epr["respond"] to return {"data": {"events": []}}, then call
# search_events with one criterion and read the request body to check
# that only that criterion appears in body["variables"]["obj"].
#
# @pytest.mark.asyncio
# async def test_search_sends_only_the_criteria_that_were_set(epr):
#     ...


# TODO: test that an unknown search criterion is rejected (strict model).
#
# @pytest.mark.asyncio
# async def test_search_rejects_unknown_criteria(epr):
#     ...


# TODO: test that create_receiver sends the schema under the "schema" key
# (not "schema_", which is the Python alias to avoid shadowing the builtin).
#
# @pytest.mark.asyncio
# async def test_create_receiver_sends_schema_under_its_epr_name(epr):
#     ...


# TODO: test that an HTTP error status from EPR becomes a ToolError.
#
# Hint: set epr["respond"] to return httpx2.Response(404, text="not found"),
# then assert result.is_error and "404" in result.content[0].text.
#
# @pytest.mark.asyncio
# async def test_epr_error_status_becomes_a_tool_error(epr):
#     ...


# TODO: test that an error message in a 200-OK body also becomes a ToolError.
#
# Hint: return {"data": None, "errors": ["event not found"]} in a 200 response.
#
# @pytest.mark.asyncio
# async def test_epr_error_in_a_200_body_becomes_a_tool_error(epr):
#     ...
