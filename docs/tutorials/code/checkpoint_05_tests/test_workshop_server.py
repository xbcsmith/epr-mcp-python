# SPDX-FileCopyrightText: © 2025 Brett Smith <xbcsmith@gmail.com>
# SPDX-License-Identifier: Apache-2.0

"""Tests for the workshop server: no EPR and no network needed.

An in-memory FastMCP client talks to the server, and httpx2.MockTransport plays EPR.

Run from the code directory:
    uv run pytest checkpoint_05_tests
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
    async with Client(server.mcp) as client:
        return await client.call_tool(tool, arguments, raise_on_error=raise_on_error)


@pytest.mark.asyncio
async def test_server_lists_nine_tools():
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
    result = await call("fetch_event", {"id": EPR_ID})
    assert json.loads(result.content[0].text)["data"]["id"] == EPR_ID
    assert epr["requests"][0].url.path == f"/api/v1/events/{EPR_ID}"


@pytest.mark.asyncio
async def test_fetch_event_rejects_a_malformed_id_without_calling_epr(epr):
    result = await call("fetch_event", {"id": "not-an-id"}, raise_on_error=False)
    assert result.is_error
    assert epr["requests"] == []


@pytest.mark.asyncio
async def test_search_sends_only_the_criteria_that_were_set(epr):
    epr["respond"] = lambda request: httpx2.Response(200, json={"data": {"events": []}})
    await call("search_events", {"data": {"name": "checkout-service"}})
    body = json.loads(epr["requests"][0].content)
    assert body["variables"] == {"obj": {"name": "checkout-service"}}


@pytest.mark.asyncio
async def test_search_rejects_unknown_criteria(epr):
    result = await call("search_events", {"data": {"nmae": "typo"}}, raise_on_error=False)
    assert result.is_error
    assert epr["requests"] == []


@pytest.mark.asyncio
async def test_create_receiver_sends_schema_under_its_epr_name(epr):
    epr["respond"] = lambda request: httpx2.Response(201, json={"data": EPR_ID})
    receiver = {
        "name": "workshop.build",
        "type": "workshop.build",
        "version": "1.0.0",
        "description": "builds",
        "schema": {"type": "object"},
    }
    await call("create_receiver", {"receiver_data": receiver})
    assert json.loads(epr["requests"][0].content)["schema"] == {"type": "object"}


@pytest.mark.asyncio
async def test_epr_error_status_becomes_a_tool_error(epr):
    epr["respond"] = lambda request: httpx2.Response(404, text="not found")
    result = await call("fetch_event", {"id": EPR_ID}, raise_on_error=False)
    assert result.is_error
    assert "404" in result.content[0].text


@pytest.mark.asyncio
async def test_epr_error_in_a_200_body_becomes_a_tool_error(epr):
    epr["respond"] = lambda request: httpx2.Response(200, json={"data": None, "errors": ["event not found"]})
    result = await call("fetch_event", {"id": EPR_ID}, raise_on_error=False)
    assert result.is_error
    assert "event not found" in result.content[0].text


@pytest.mark.asyncio
async def test_dropped_connection_is_reported_with_its_error_name(epr):
    def drop(request):
        raise httpx2.RemoteProtocolError("", request=request)

    epr["respond"] = drop
    result = await call("fetch_event", {"id": EPR_ID}, raise_on_error=False)
    assert result.is_error
    assert "RemoteProtocolError" in result.content[0].text


@pytest.mark.asyncio
async def test_unreachable_epr_says_so(epr):
    def refuse(request):
        raise httpx2.ConnectError("refused", request=request)

    epr["respond"] = refuse
    result = await call("fetch_event", {"id": EPR_ID}, raise_on_error=False)
    assert result.is_error
    assert "Cannot reach EPR" in result.content[0].text


@pytest.mark.asyncio
async def test_bearer_token_is_sent_when_configured(monkeypatch):
    monkeypatch.setattr(server, "EPR_TOKEN", "secret")
    assert server.new_client().headers["Authorization"] == "Bearer secret"
