# 03 Complete the Tool Set

Time: 30 minutes.

You will grow the server from one tool to nine: fetch, search, and create for
events, event receivers, and event receiver groups. The finished code is in
`checkpoint_03_tool_set/server.py`. Start from your module 01 file, or copy the
checkpoint for module 01 into `work/server.py`.

## Plan

Nine tools would be a lot of repeated code, so first write two helpers. Every
tool then becomes one or two lines.

| Tool                                                 | EPR endpoint                 |
| ---------------------------------------------------- | ---------------------------- |
| `fetch_event`, `fetch_receiver`, `fetch_group`       | `GET /api/v1/{kind}/{id}`    |
| `search_events`, `search_receivers`, `search_groups` | `POST /api/v1/graphql/query` |
| `create_event`, `create_receiver`, `create_group`    | `POST /api/v1/{kind}`        |

Here `kind` is `events`, `receivers`, or `groups`.

## Step 1: logging and settings

Replace the top of your file. All logging goes to stderr because stdout belongs
to the protocol.

```python
import logging
import os
import sys

import httpx2
from fastmcp import FastMCP

logging.basicConfig(
    stream=sys.stderr,
    level=logging.DEBUG if os.environ.get("EPR_DEBUG") else logging.INFO,
    format="%(asctime)s %(name)s:[%(levelname)s] %(message)s",
)
logger = logging.getLogger("epr_workshop")

EPR_URL = os.environ.get("EPR_URL", "http://localhost:8042")
EPR_TOKEN = os.environ.get("EPR_TOKEN")

mcp = FastMCP(name="EPR Workshop MCP Server", version="0.3.0")
```

`EPR_TOKEN` is optional. The workshop EPR needs no token, but a real EPR might.

## Step 2: one client factory and one request helper

```python
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
```

Why a factory? Every request gets the same base URL and token, and in module 05
a test replaces this one function to fake EPR.

## Step 3: the three fetch tools

```python
@mcp.tool(title="Fetch Event", description="Fetch an event from EPR by its ID")
async def fetch_event(id: str) -> str:
    """Fetch an event from the EPR."""
    return await epr_request("GET", f"/api/v1/events/{id}")
```

Add `fetch_receiver` (`/api/v1/receivers/{id}`) and `fetch_group`
(`/api/v1/groups/{id}`) the same way.

## Step 4: search

EPR searches go through GraphQL. A table says, for each search, the GraphQL
input type, the argument name, and the fields to return:

```python
SEARCHES = {
    "events": (
        "FindEventInput!",
        "event",
        ["id", "name", "version", "release", "platform_id", "package", "description", "success", "event_receiver_id"],
    ),
    "event_receivers": ("FindEventReceiverInput!", "event_receiver", ["id", "name", "type", "version", "description"]),
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
```

Then the tools:

```python
@mcp.tool(
    title="Search Events",
    description="Search for events. Criteria: name, version, release, platform_id, package, description, success.",
)
async def search_events(data: dict) -> str:
    """Search for events in the EPR."""
    return await search("events", data)
```

Add `search_receivers` (operation `event_receivers`) and `search_groups`
(operation `event_receiver_groups`). Their criteria are name, type, version, and
description.

The criteria are passed flat: to find events named `checkout-service`, the tool
argument is `{"data": {"name": "checkout-service"}}`. The parameter is called
`data` and its value is the criteria object.

## Step 5: create

```python
@mcp.tool(title="Create Event", description="Create a new event in EPR")
async def create_event(event_data: dict) -> str:
    """Create a new event in the EPR."""
    return await epr_request("POST", "/api/v1/events", event_data)
```

Add `create_receiver` (`/api/v1/receivers`, argument `receiver_data`) and
`create_group` (`/api/v1/groups`, argument `group_data`). These change EPR's
data, so write good descriptions: the model decides when to call them.

Finish with the run block:

```python
if __name__ == "__main__":
    logger.info("EPR URL: %s (token configured: %s)", EPR_URL, bool(EPR_TOKEN))
    mcp.run()
```

Never log the token itself, only whether one is set.

## Try it

```bash
uv run python client.py list work/server.py
```

You should see nine tools. Then:

```bash
uv run python client.py call work/server.py search_events '{"data": {"name": "checkout-service"}}'
uv run python client.py call work/server.py search_receivers '{"data": {}}'
uv run python client.py call work/server.py fetch_group '{"id": "PASTE_THE_GROUP_ID"}'
```

Search with `{}` returns everything, because every criterion is optional. Now
create a receiver and an event for it. The receiver call returns the new ID in
`{"data": "..."}`; use it as `event_receiver_id`:

```bash
uv run python client.py call work/server.py create_receiver '{"receiver_data": {"name": "demo.build", "type": "demo.build", "version": "1.0.0", "description": "My receiver", "schema": {"type": "object", "properties": {"name": {"type": "string"}}}}}'
```

```bash
uv run python client.py call work/server.py create_event '{"event_data": {"name": "demo-service", "version": "0.0.1", "release": "2025.10.0", "platform_id": "linux", "package": "oci", "description": "My first event", "payload": {"name": "demo-service"}, "success": true, "event_receiver_id": "PASTE_THE_RECEIVER_ID"}}'
```

## Checkpoint

- `client.py list work/server.py` shows nine tools.
- You created a receiver and an event and found the event with `search_events`.
- Behind schedule? `cp checkpoint_03_tool_set/server.py work/server.py`.

## Things to notice

- Every tool still returns text, including errors. EPR answers a missing record
  with HTTP 404, and a malformed ID or a bad search with HTTP 200 and
  `{"data": null, "errors": [...]}`. Your tool hands all of these back as normal
  successful results, so the client cannot tell the call failed. Module 04 fixes
  this.
- `data: dict` accepts anything. A typo such as `{"nmae": "x"}` is sent to EPR
  as is. Module 04 fixes this too.

Next: [04 Validation and errors](04_validation_and_errors.md).
