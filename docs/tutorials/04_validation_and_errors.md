# 04 Validation and Errors

Time: 20 minutes.

Your server works when callers behave. Real AI clients guess: they send
malformed IDs, misspell fields, and call EPR when it is down. In this module you
make the server reject bad input before it reaches EPR and report failures as
real errors. The finished code is in `checkpoint_04_validation/server.py`.

## 1. Typed inputs

FastMCP turns type hints into the JSON schema that the AI client sees, and it
validates every call against that schema before your function runs. So the
better your types, the less code you write.

Add a type for IDs. EPR IDs are 26 character ULIDs:

```python
from typing import Annotated, Any

from pydantic import BaseModel, ConfigDict, Field

EprId = Annotated[str, Field(pattern=r"^[0-9A-Za-z]{26}$", description="26 character ULID of the record")]
```

Use it in the fetch tools:

```python
async def fetch_event(id: EprId) -> str:
```

A call with `{"id": "nope"}` is now rejected by the schema, and EPR is never
called.

## 2. Strict models for the dict arguments

`data: dict` accepts anything. Replace it with models. The base class forbids
unknown fields so a typo is an error, not a silently ignored filter:

```python
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
```

Add `ReceiverSearch` (name, type, version, description) and `GroupSearch`, which
inherits from it. Add create models too: `EventCreate`, `ReceiverCreate`, and
`GroupCreate`. Required fields have no default. `ReceiverCreate` needs a field
called `schema`, but `schema` clashes with a Pydantic built-in, so name the
attribute `schema_` and give it `Field(alias="schema")`.

The full models are in the checkpoint file. Then the tools take the models:

```python
async def search_events(data: EventSearch) -> str:
    return await search("events", data)
```

The tool call is unchanged: `{"data": {"name": "checkout-service"}}`. Inside
`search`, send only the criteria that were set:

```python
variables = {"obj": criteria.model_dump(exclude_none=True)}
```

For create tools, send `model_dump()`; for receivers use
`model_dump(by_alias=True)` so `schema_` goes out as `schema`.

## 3. Errors that look like errors

In module 03, a failed call came back as normal text. MCP has a proper way to
say "this call failed": raise `ToolError`. The client sees an error result, and
a good AI client reacts to it (retries, asks the user, or explains).

Replace `epr_request` and add a helper that turns httpx2 exceptions into
messages a model can act on. (Add `import json` at the top as well.)

```python
import httpx2
from fastmcp.exceptions import ToolError


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
```

Points worth knowing:

- `httpx2` has the same exception hierarchy as `httpx`. `TransportError` covers
  everything that goes wrong before a response arrives: `TimeoutException`,
  `ConnectError` (connection refused), and protocol errors such as
  `RemoteProtocolError` (the connection was dropped). `HTTPStatusError` comes
  from `raise_for_status()`. All inherit from `HTTPError`. Catch the specific
  case you can explain (timeout) first, then the broad one, and include the
  exception's class name in the message: a dropped connection often has an empty
  message.
- Exceptions from the old `httpx` package are different classes. If you mix the
  two packages, `except httpx2.HTTPError` will not catch an `httpx` error. Use
  `httpx2` everywhere.
- A successful HTTP status is not always a successful call. EPR answers some
  failures, for example a malformed ID or a bad GraphQL search, with `200` and a
  body like `{"data": null, "errors": [...]}`. `epr_request` checks the body for
  `errors` too, which is the check most often forgotten.
- Put the operation name in each message. Models use it to work out what
  happened.
- The shipped `epr-mcp` server returns error text instead of raising; this
  workshop version uses `ToolError`, which is the more precise choice.

Pass an operation name to every `epr_request` call, for example
`epr_request("fetch_event", "GET", f"/api/v1/events/{id}")`.

## Try it

```bash
uv run python client.py call work/server.py fetch_event '{"id": "nope"}'
uv run python client.py call work/server.py search_events '{"data": {"nmae": "typo"}}'
uv run python client.py call work/server.py search_events '{"data": {"name": "checkout-service"}}'
```

The first two fail with validation errors and never reach EPR. The third works.
A well-formed ID that does not exist is different: it passes validation, EPR
answers `404`, and the tool reports it as an error:

```bash
uv run python client.py call work/server.py fetch_event '{"id": "01JYRZ96R690ZTQ15Q53GEY6E6"}'
```

Now take EPR down and call again:

```bash
docker compose stop epr-server
uv run python client.py call work/server.py fetch_event '{"id": "PASTE_AN_EVENT_ID"}'
docker compose start epr-server
```

You should see `Cannot reach EPR at http://localhost:8042` with the name of the
underlying error, and the exit code of `client.py` is 1. Tell the room before
you stop EPR, and wait a few seconds after starting it again.

## Checkpoint

- A bad ID and a misspelled field are both rejected, and a well-formed ID that
  does not exist comes back as an error naming the 404.
- Stopping EPR gives a clear "Cannot reach EPR" error.
- Behind schedule? `cp checkpoint_04_validation/server.py work/server.py`.

Next: [05 Test it](05_test_it.md).
