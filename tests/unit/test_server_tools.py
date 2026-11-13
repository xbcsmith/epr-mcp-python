# SPDX-FileCopyrightText: © 2025 Brett Smith <xbcsmith@gmail.com>
# SPDX-License-Identifier: Apache-2.0

"""Tests for the EPR MCP tools, using an in-memory FastMCP client.

EPR calls are intercepted with ``httpx2.MockTransport`` so no network is used.
"""

import json

import httpx2
import pytest  # type: ignore
from fastmcp import Client
from fastmcp.exceptions import ToolError

from epr_mcp import common, server
from epr_mcp.config import Config

EVENT_ID = "01JYRZ96R690ZTQ15Q53GEY6E6"
EXPECTED_TOOLS = {
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

EVENT = {
    "id": EVENT_ID,
    "name": "foo",
    "version": "1.0.0",
    "release": "2025.1",
    "platform_id": "linux",
    "package": "oci",
    "description": "an event",
    "success": True,
    "event_receiver_id": "01JYRZ96R690ZTQ15Q53GEY6E7",
    "created_at": "2025-01-01T00:00:00Z",
    "payload": {"a": 1},
}


@pytest.fixture
def cfg():
    """Provide a configuration with a token, pointing at a fake EPR."""
    return Config(url="http://epr.test", token="secret")


@pytest.fixture
def mock_epr(monkeypatch):
    """Route every EPR request through a handler the test installs."""
    state = {"handler": lambda request: httpx2.Response(404), "requests": []}

    def create_client(cfg):
        def handler(request):
            state["requests"].append(request)
            return state["handler"](request)

        client = common.create_client(cfg)
        return httpx2.AsyncClient(headers=client.headers, transport=httpx2.MockTransport(handler))

    monkeypatch.setattr(server, "create_client", create_client)
    return state


async def call(mcp, tool, args):
    """Call a tool through an in-memory client and return the reply text."""
    async with Client(mcp) as client:
        result = await client.call_tool(tool, args)
    return result.content[0].text


class TestServerRegistration:
    """The server exposes the expected tools and metadata."""

    @pytest.mark.asyncio
    async def test_lists_all_tools(self, cfg):
        """Test lists all tools."""
        async with Client(server.create_server(cfg)) as client:
            tools = await client.list_tools()
        assert {t.name for t in tools} == EXPECTED_TOOLS

    @pytest.mark.asyncio
    async def test_tool_schemas_have_required_inputs(self, cfg):
        """Test tool schemas have required inputs."""
        async with Client(server.create_server(cfg)) as client:
            tools = {t.name: t for t in await client.list_tools()}
        assert tools["fetch_event"].input_schema["required"] == ["id"]
        assert "ctx" not in tools["fetch_event"].input_schema["properties"]
        assert tools["search_events"].input_schema["required"] == ["data"]
        assert tools["create_event"].input_schema["required"] == ["event_data"]

    def test_version_is_not_instructions(self, cfg):
        """Test version is not instructions."""
        mcp = server.create_server(cfg)
        assert mcp.name == "EPR MCP Server"
        assert mcp.version == "1.0.0"
        assert mcp.instructions != "1.0.0"


class TestFetchTools:
    """Tests for the fetch tools."""

    @pytest.mark.asyncio
    async def test_fetch_event_success_sends_bearer_token(self, cfg, mock_epr):
        """Test fetch event success sends bearer token."""
        mock_epr["handler"] = lambda request: httpx2.Response(200, json={"data": [EVENT]})
        text = await call(server.create_server(cfg), "fetch_event", {"id": EVENT_ID})
        assert json.loads(text)["id"] == EVENT_ID
        request = mock_epr["requests"][0]
        assert request.url.path == f"/api/v1/events/{EVENT_ID}"
        assert request.headers["Authorization"] == "Bearer secret"

    @pytest.mark.asyncio
    async def test_fetch_event_empty_result(self, cfg, mock_epr):
        """Test fetch event empty result."""
        mock_epr["handler"] = lambda request: httpx2.Response(200, json={"data": []})
        text = await call(server.create_server(cfg), "fetch_event", {"id": EVENT_ID})
        assert "No event found" in text

    @pytest.mark.asyncio
    async def test_fetch_event_not_found(self, cfg, mock_epr):
        """Test fetch event not found."""
        mock_epr["handler"] = lambda request: httpx2.Response(404, text="missing")
        text = await call(server.create_server(cfg), "fetch_event", {"id": EVENT_ID})
        assert text == "Failed to fetch event: 404 - missing"

    @pytest.mark.asyncio
    async def test_fetch_event_invalid_id(self, cfg, mock_epr):
        """Test fetch event invalid id."""
        text = await call(server.create_server(cfg), "fetch_event", {"id": "   "})
        assert "validation" in text.lower()
        assert mock_epr["requests"] == []

    @pytest.mark.asyncio
    async def test_fetch_event_response_validation_failure(self, cfg, mock_epr):
        """Test fetch event response validation failure."""
        mock_epr["handler"] = lambda request: httpx2.Response(200, json={"data": {"unexpected": True}})
        text = await call(server.create_server(cfg), "fetch_event", {"id": EVENT_ID})
        assert "validation" in text.lower()

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        ("tool", "path"),
        [("fetch_receiver", "/api/v1/receivers/"), ("fetch_group", "/api/v1/groups/")],
    )
    async def test_fetch_other_tools_call_expected_path(self, cfg, mock_epr, tool, path):
        """Test fetch other tools call expected path."""
        mock_epr["handler"] = lambda request: httpx2.Response(200, json={"data": []})
        await call(server.create_server(cfg), tool, {"id": EVENT_ID})
        assert mock_epr["requests"][0].url.path == f"{path}{EVENT_ID}"


class TestSearchTools:
    """Tests for the search tools."""

    @pytest.mark.asyncio
    async def test_search_events_success(self, cfg, mock_epr):
        """Test search events success."""
        mock_epr["handler"] = lambda request: httpx2.Response(200, json={"data": {"events": [EVENT]}})
        text = await call(server.create_server(cfg), "search_events", {"data": {"name": "foo"}})
        assert json.loads(text)[0]["name"] == "foo"
        request = mock_epr["requests"][0]
        assert request.url.path == "/api/v1/graphql/query"
        assert json.loads(request.content)["variables"]["obj"] == {"name": "foo"}

    @pytest.mark.asyncio
    @pytest.mark.parametrize("tool", ["search_events", "search_receivers", "search_groups"])
    async def test_search_non_200(self, cfg, mock_epr, tool):
        """Test search non 200."""
        mock_epr["handler"] = lambda request: httpx2.Response(500, text="bad")
        text = await call(server.create_server(cfg), tool, {"data": {"name": "foo"}})
        assert text.startswith("Failed to search")
        assert "500 - bad" in text

    @pytest.mark.asyncio
    @pytest.mark.parametrize("tool", ["search_receivers", "search_groups"])
    async def test_search_empty_results(self, cfg, mock_epr, tool):
        """Test search empty results."""
        mock_epr["handler"] = lambda request: httpx2.Response(200, json={"data": {}})
        text = await call(server.create_server(cfg), tool, {"data": {"name": "foo"}})
        assert json.loads(text) == []


class TestCreateTools:
    """Tests for the create tools."""

    @pytest.mark.asyncio
    async def test_create_event_non_201(self, cfg, mock_epr):
        """Test create event non 201."""
        mock_epr["handler"] = lambda request: httpx2.Response(400, text="nope")
        data = {
            "name": "foo",
            "version": "1.0.0",
            "release": "2025.1",
            "platform_id": "linux",
            "package": "oci",
            "description": "an event",
            "payload": {"a": 1},
            "event_receiver_id": EVENT_ID,
            "success": True,
        }
        text = await call(server.create_server(cfg), "create_event", {"event_data": data})
        assert text == "Failed to create event: 400 - nope"

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        ("tool", "arg"),
        [("create_event", "event_data"), ("create_receiver", "receiver_data"), ("create_group", "group_data")],
    )
    async def test_create_rejects_invalid_input(self, cfg, mock_epr, tool, arg):
        """Test create rejects invalid input."""
        text = await call(server.create_server(cfg), tool, {arg: {}})
        assert "validation" in text.lower()
        assert mock_epr["requests"] == []


class TestTransportErrors:
    """Tests for connection errors and timeouts."""

    @pytest.mark.asyncio
    async def test_connect_error_is_reported(self, cfg, mock_epr):
        """Test connect error is reported."""

        def handler(request):
            raise httpx2.ConnectError("refused", request=request)

        mock_epr["handler"] = handler
        text = await call(server.create_server(cfg), "fetch_event", {"id": EVENT_ID})
        assert "Connection failed to EPR server at http://epr.test" in text

    @pytest.mark.asyncio
    async def test_timeout_is_reported(self, cfg, mock_epr):
        """Test timeout is reported."""

        def handler(request):
            raise httpx2.ReadTimeout("slow", request=request)

        mock_epr["handler"] = handler
        text = await call(server.create_server(cfg), "fetch_event", {"id": EVENT_ID})
        assert text.startswith("Request timeout to EPR server")


def test_unknown_tool_raises(cfg):
    """Test unknown tool raises."""
    import asyncio

    async def go():
        async with Client(server.create_server(cfg)) as client:
            await client.call_tool("nope", {})

    with pytest.raises(ToolError):
        asyncio.run(go())


RECEIVER = {
    "id": EVENT_ID,
    "name": "foobar",
    "type": "foo.bar",
    "version": "1.1.3",
    "description": "a receiver",
    "schema": {"type": "object"},
    "fingerprint": "a" * 64,
    "created_at": "2025-01-01T00:00:00Z",
}

GROUP = {
    "id": EVENT_ID,
    "name": "agroup",
    "type": "foo.group",
    "version": "1.0.0",
    "description": "a group",
    "enabled": True,
    "event_receiver_ids": [EVENT_ID],
    "created_at": "2025-01-01T00:00:00Z",
    "updated_at": "2025-01-01T00:00:00Z",
}

EVENT_INPUT = {
    "name": "foo",
    "version": "1.0.0",
    "release": "2025.1",
    "platform_id": "linux",
    "package": "oci",
    "description": "an event",
    "payload": {"a": 1},
    "event_receiver_id": EVENT_ID,
    "success": True,
}
RECEIVER_INPUT = {
    "name": "foobar",
    "type": "foo.bar",
    "version": "1.1.3",
    "description": "a receiver",
    "schema": {"type": "object", "properties": {"name": {"type": "string"}}},
}
GROUP_INPUT = {
    "name": "agroup",
    "type": "foo.group",
    "version": "1.0.0",
    "description": "a group",
    "event_receiver_ids": [EVENT_ID],
}


class TestSuccessPaths:
    """Every tool returns validated EPR data on success."""

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        ("tool", "record"),
        [("fetch_event", EVENT), ("fetch_receiver", RECEIVER), ("fetch_group", GROUP)],
    )
    @pytest.mark.parametrize("wrap", [lambda r: {"data": r}, lambda r: {"data": [r]}, lambda r: r])
    async def test_fetch_success_handles_epr_response_shapes(self, cfg, mock_epr, tool, record, wrap):
        """Test fetch success handles epr response shapes."""
        mock_epr["handler"] = lambda request: httpx2.Response(200, json=wrap(record))
        text = await call(server.create_server(cfg), tool, {"id": EVENT_ID})
        assert json.loads(text)["id"] == EVENT_ID

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        ("tool", "key", "record"),
        [
            ("search_events", "events", EVENT),
            ("search_receivers", "event_receivers", RECEIVER),
            ("search_groups", "event_receiver_groups", GROUP),
        ],
    )
    async def test_search_success(self, cfg, mock_epr, tool, key, record):
        """Test search success."""
        mock_epr["handler"] = lambda request: httpx2.Response(200, json={"data": {key: [record]}})
        text = await call(server.create_server(cfg), tool, {"data": {"name": record["name"]}})
        assert json.loads(text)[0]["id"] == EVENT_ID

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        ("tool", "arg", "payload", "record", "path", "key"),
        [
            ("create_event", "event_data", EVENT_INPUT, EVENT, "/api/v1/events", "event"),
            ("create_receiver", "receiver_data", RECEIVER_INPUT, RECEIVER, "/api/v1/receivers", "receiver"),
            ("create_group", "group_data", GROUP_INPUT, GROUP, "/api/v1/groups", "group"),
        ],
    )
    @pytest.mark.parametrize("status", [200, 201])
    async def test_create_success(self, cfg, mock_epr, tool, arg, payload, record, path, key, status):
        """EPR answers a create with 200; some versions answer 201."""
        mock_epr["handler"] = lambda request: httpx2.Response(status, json={"data": [record]})
        text = await call(server.create_server(cfg), tool, {arg: payload})
        result = json.loads(text)
        assert "created successfully" in result["message"]
        assert result[key]["id"] == EVENT_ID
        request = mock_epr["requests"][0]
        assert request.method == "POST"
        assert request.url.path == path

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        ("tool", "arg", "payload"),
        [
            ("create_receiver", "receiver_data", RECEIVER_INPUT),
            ("create_group", "group_data", GROUP_INPUT),
        ],
    )
    async def test_create_non_success(self, cfg, mock_epr, tool, arg, payload):
        """Test create non success."""
        mock_epr["handler"] = lambda request: httpx2.Response(409, text="conflict")
        text = await call(server.create_server(cfg), tool, {arg: payload})
        assert text.startswith("Failed to create")
        assert "409 - conflict" in text

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        ("tool", "arg", "payload"),
        [
            ("create_event", "event_data", EVENT_INPUT),
            ("create_receiver", "receiver_data", RECEIVER_INPUT),
            ("create_group", "group_data", GROUP_INPUT),
        ],
    )
    async def test_create_empty_result(self, cfg, mock_epr, tool, arg, payload):
        """Test create empty result."""
        mock_epr["handler"] = lambda request: httpx2.Response(201, json={"data": []})
        text = await call(server.create_server(cfg), tool, {arg: payload})
        assert "empty result" in text

    @pytest.mark.asyncio
    @pytest.mark.parametrize("tool", ["fetch_receiver", "fetch_group"])
    async def test_fetch_empty_result(self, cfg, mock_epr, tool):
        """Test fetch empty result."""
        mock_epr["handler"] = lambda request: httpx2.Response(200, json={"data": []})
        text = await call(server.create_server(cfg), tool, {"id": EVENT_ID})
        assert "No event" in text

    @pytest.mark.asyncio
    @pytest.mark.parametrize("tool", ["fetch_receiver", "fetch_group"])
    async def test_fetch_non_200_and_invalid_id(self, cfg, mock_epr, tool):
        """Test fetch non 200 and invalid id."""
        mock_epr["handler"] = lambda request: httpx2.Response(500, text="bad")
        assert (await call(server.create_server(cfg), tool, {"id": EVENT_ID})).startswith("Failed to fetch")
        assert "validation" in (await call(server.create_server(cfg), tool, {"id": "short"})).lower()

    @pytest.mark.asyncio
    @pytest.mark.parametrize("tool", ["fetch_receiver", "fetch_group"])
    async def test_fetch_response_validation_failure(self, cfg, mock_epr, tool):
        """Test fetch response validation failure."""
        mock_epr["handler"] = lambda request: httpx2.Response(200, json={"data": {"unexpected": True}})
        assert "validation" in (await call(server.create_server(cfg), tool, {"id": EVENT_ID})).lower()


class TestAgainstRealEprBehavior:
    """Behavior observed against a running EPR rather than assumed from its docs."""

    @pytest.mark.asyncio
    async def test_create_receiver_requires_a_schema(self, cfg, mock_epr):
        """Test create receiver requires a schema."""
        without_schema = {k: v for k, v in RECEIVER_INPUT.items() if k != "schema"}
        text = await call(server.create_server(cfg), "create_receiver", {"receiver_data": without_schema})
        assert text.startswith("Input validation error")
        assert mock_epr["requests"] == []

    @pytest.mark.asyncio
    async def test_create_receiver_sends_schema_to_epr(self, cfg, mock_epr):
        """Test create receiver sends schema to epr."""
        mock_epr["handler"] = lambda request: httpx2.Response(200, json={"data": [RECEIVER]})
        await call(server.create_server(cfg), "create_receiver", {"receiver_data": RECEIVER_INPUT})
        assert json.loads(mock_epr["requests"][0].content)["schema"] == RECEIVER_INPUT["schema"]

    @pytest.mark.asyncio
    async def test_group_search_does_not_request_unknown_fingerprint_field(self, cfg, mock_epr):
        """The EPR GraphQL type EventReceiverGroup has no fingerprint; asking for it fails the query."""
        mock_epr["handler"] = lambda request: httpx2.Response(200, json={"data": {"event_receiver_groups": []}})
        await call(server.create_server(cfg), "search_groups", {"data": {"name": "agroup"}})
        assert "fingerprint" not in json.loads(mock_epr["requests"][0].content)["query"]

    @pytest.mark.asyncio
    @pytest.mark.parametrize("tool", ["search_events", "search_receivers", "search_groups"])
    async def test_graphql_errors_are_reported_not_hidden(self, cfg, mock_epr, tool):
        """Test graphql errors are reported not hidden."""
        mock_epr["handler"] = lambda request: httpx2.Response(200, json={"errors": [{"message": "Cannot query field"}]})
        text = await call(server.create_server(cfg), tool, {"data": {}})
        assert text.startswith("Failed to search")
        assert "Cannot query field" in text


class TestCreateReturnsIdOnly:
    """A running EPR answers a create with only the new ID: {"data": "<id>"}."""

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        ("tool", "arg", "payload", "label"),
        [
            ("create_event", "event_data", EVENT_INPUT, "Event created"),
            ("create_receiver", "receiver_data", RECEIVER_INPUT, "Event receiver created"),
            ("create_group", "group_data", GROUP_INPUT, "Event receiver group created"),
        ],
    )
    async def test_create_reports_the_new_id(self, cfg, mock_epr, tool, arg, payload, label):
        """Test create reports the new id."""
        mock_epr["handler"] = lambda request: httpx2.Response(200, json={"data": EVENT_ID})
        result = json.loads(await call(server.create_server(cfg), tool, {arg: payload}))
        assert result == {"message": f"{label} successfully", "id": EVENT_ID}


class TestFlatArguments:
    """Tools take their criteria or fields directly, not wrapped in a data key."""

    @pytest.mark.asyncio
    @pytest.mark.parametrize("tool", ["search_events", "search_receivers", "search_groups"])
    async def test_search_rejects_legacy_wrapped_argument(self, cfg, mock_epr, tool):
        """A wrapped argument must fail loudly, not run an unfiltered search."""
        text = await call(server.create_server(cfg), tool, {"data": {"data": {"name": "foo"}}})
        assert text.startswith("Input validation error")
        assert mock_epr["requests"] == []

    @pytest.mark.asyncio
    async def test_search_rejects_unknown_criteria(self, cfg, mock_epr):
        """Test search rejects unknown criteria."""
        text = await call(server.create_server(cfg), "search_events", {"data": {"nme": "foo"}})
        assert text.startswith("Input validation error")
        assert mock_epr["requests"] == []

    @pytest.mark.asyncio
    async def test_search_without_criteria_is_allowed(self, cfg, mock_epr):
        """Test search without criteria is allowed."""
        mock_epr["handler"] = lambda request: httpx2.Response(200, json={"data": {"events": []}})
        text = await call(server.create_server(cfg), "search_events", {"data": {}})
        assert json.loads(text) == []
        assert json.loads(mock_epr["requests"][0].content)["variables"]["obj"] == {}

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        ("tool", "arg", "payload"),
        [
            ("create_event", "event_data", EVENT_INPUT),
            ("create_receiver", "receiver_data", RECEIVER_INPUT),
            ("create_group", "group_data", GROUP_INPUT),
        ],
    )
    async def test_create_rejects_legacy_wrapped_argument(self, cfg, mock_epr, tool, arg, payload):
        """Test create rejects legacy wrapped argument."""
        text = await call(server.create_server(cfg), tool, {arg: {"data": payload}})
        assert text.startswith("Input validation error")
        assert mock_epr["requests"] == []


ALL_TOOL_CALLS = [
    ("fetch_event", {"id": EVENT_ID}),
    ("fetch_receiver", {"id": EVENT_ID}),
    ("fetch_group", {"id": EVENT_ID}),
    ("search_events", {"data": {"name": "foo"}}),
    ("search_receivers", {"data": {"name": "foo"}}),
    ("search_groups", {"data": {"name": "foo"}}),
    ("create_event", {"event_data": EVENT_INPUT}),
    ("create_receiver", {"receiver_data": RECEIVER_INPUT}),
    ("create_group", {"group_data": GROUP_INPUT}),
]


class TestEveryToolHandlesEprFailures:
    """Every one of the nine tools reports connection errors, timeouts, and bad responses."""

    @pytest.mark.asyncio
    @pytest.mark.parametrize(("tool", "arguments"), ALL_TOOL_CALLS)
    async def test_connect_error_is_reported(self, cfg, mock_epr, tool, arguments):
        """Test connect error is reported."""

        def refuse(request):
            raise httpx2.ConnectError("refused", request=request)

        mock_epr["handler"] = refuse
        text = await call(server.create_server(cfg), tool, arguments)
        assert text.startswith("Connection failed to EPR server at http://epr.test")

    @pytest.mark.asyncio
    @pytest.mark.parametrize(("tool", "arguments"), ALL_TOOL_CALLS)
    async def test_timeout_is_reported(self, cfg, mock_epr, tool, arguments):
        """Test timeout is reported."""

        def slow(request):
            raise httpx2.ReadTimeout("slow", request=request)

        mock_epr["handler"] = slow
        text = await call(server.create_server(cfg), tool, arguments)
        assert text.startswith("Request timeout to EPR server")

    @pytest.mark.asyncio
    @pytest.mark.parametrize(("tool", "arguments"), ALL_TOOL_CALLS)
    async def test_error_status_is_reported(self, cfg, mock_epr, tool, arguments):
        """Test error status is reported."""
        mock_epr["handler"] = lambda request: httpx2.Response(500, text="boom")
        text = await call(server.create_server(cfg), tool, arguments)
        assert text.startswith("Failed to") and "500" in text and "boom" in text

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        ("tool", "arguments", "body"),
        [
            ("fetch_event", {"id": EVENT_ID}, {"data": {"unexpected": True}}),
            ("fetch_receiver", {"id": EVENT_ID}, {"data": {"unexpected": True}}),
            ("fetch_group", {"id": EVENT_ID}, {"data": {"unexpected": True}}),
            ("search_events", {"data": {}}, {"data": {"events": [{"unexpected": True}]}}),
            ("search_receivers", {"data": {}}, {"data": {"event_receivers": [{"unexpected": True}]}}),
            ("search_groups", {"data": {}}, {"data": {"event_receiver_groups": [{"unexpected": True}]}}),
            ("create_event", {"event_data": EVENT_INPUT}, {"data": {"unexpected": True}}),
            ("create_receiver", {"receiver_data": RECEIVER_INPUT}, {"data": {"unexpected": True}}),
            ("create_group", {"group_data": GROUP_INPUT}, {"data": {"unexpected": True}}),
        ],
    )
    async def test_response_that_fails_validation_is_reported(self, cfg, mock_epr, tool, arguments, body):
        """Test response that fails validation is reported."""
        mock_epr["handler"] = lambda request: httpx2.Response(200, json=body)
        text = await call(server.create_server(cfg), tool, arguments)
        assert "validation" in text.lower()
