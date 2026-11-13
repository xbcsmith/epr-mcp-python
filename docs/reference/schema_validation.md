# Schema Validation

Every tool checks its input before it contacts EPR, and checks what EPR sends
back before it hands it on. This document lists the rules. The code is in
`src/epr_mcp/schemas.py`.

## Why validate

An AI client guesses at arguments. Rejecting a malformed ID or a misspelled
field before the request means a clear error message, no wasted EPR call, and no
silently wrong result. The most important rule is that unknown fields are
rejected: a misspelled search field would otherwise be dropped and the search
would return every record.

## Input rules

All six search and create input models reject unknown fields. String values are
trimmed of leading and trailing whitespace first.

### Fetch tools

`fetch_event`, `fetch_receiver`, and `fetch_group` take an `id`: a 26 character
alphanumeric ULID (`^[0-9A-Za-z]{26}$`).

### Search tools

`search_events`, `search_receivers`, and `search_groups` take `data`, an object
whose fields are all optional. A blank string counts as not set. An empty object
searches for everything.

| Tool               | Fields                                                                                                |
| ------------------ | ----------------------------------------------------------------------------------------------------- |
| `search_events`    | `name`, `version`, `release`, `platform_id`, `package`, `description`, `success`, `event_receiver_id` |
| `search_receivers` | `name`, `type`, `version`, `description`                                                              |
| `search_groups`    | `name`, `type`, `version`, `description`                                                              |

Only the fields that are set are sent to EPR.

### Create tools

All fields are required.

| Tool              | Argument        | Fields                                                                                                                              |
| ----------------- | --------------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| `create_event`    | `event_data`    | `name`, `version`, `release`, `platform_id`, `package`, `description`, `event_receiver_id`, `success` (boolean), `payload` (object) |
| `create_receiver` | `receiver_data` | `name`, `type`, `version`, `description`, `schema` (object: the JSON schema that event payloads must match)                         |
| `create_group`    | `group_data`    | `name`, `type`, `version`, `description`, `event_receiver_ids` (a non-empty list of ULIDs)                                          |

Field formats:

- `name`: letters and digits, optionally separated by `.`, `_`, or `-`, and by
  `/` for nested names.
- `version`: a semantic version such as `1.2.3`.
- `release`: any text without whitespace.
- `platform_id`: letters and digits separated by `-`, such as `x64-linux-oci-2`.
- `package`: letters only, such as `oci`.
- `type`: any text without spaces.
- `event_receiver_id` and each of `event_receiver_ids`: a 26 character ULID.

`create_receiver` requires `schema` because EPR does. In the Python models the
attribute is `schema_data`, with the alias `schema`, because `schema` clashes
with a Pydantic built-in. The wire name is always `schema`.

## Arguments are flat

The argument is the object itself, with no extra `data` wrapper:

```json
{ "data": { "name": "checkout-service", "success": true } }
```

for `search_events`, and

```json
{
  "event_data": {
    "name": "checkout-service",
    "version": "1.2.3",
    "release": "2025.10.0",
    "platform_id": "linux",
    "package": "oci",
    "description": "A build",
    "payload": { "name": "checkout-service" },
    "success": true,
    "event_receiver_id": "01JYRZ96R690ZTQ15Q53GEY6E6"
  }
}
```

for `create_event`. Inside the server, `validate_input` still validates a model
that has a `data` key; the tools add that wrapper themselves. The older shape
`{"data": {"data": {...}}}` is rejected as an unknown field.

## Response rules

EPR's answers are validated too, with the `EventResponse`,
`EventReceiverResponse`, and `EventReceiverGroupResponse` models and the
`validate_*_response` helpers:

- IDs must be ULIDs and the main text fields must have the same formats as the
  input rules; fingerprints, when present, are 64 hex characters.
- A single record can arrive as an object, a one-item list, or inside
  `{"data": ...}`; the tools accept all three. An empty list becomes a "not
  found" message.
- A create answers with only the new ID (`{"data": "<id>"}`). The create tools
  return `{"message": "... created successfully", "id": "<id>"}`.
- A GraphQL failure arrives as an `errors` list. The search tools return it as
  `Failed to search ...` instead of an empty result.

## How errors look

The tools return text, not an MCP error result:

| Problem                        | Result                                                  |
| ------------------------------ | ------------------------------------------------------- |
| Invalid or unknown input       | `Input validation error: ...` with the Pydantic message |
| EPR returned an invalid record | `Response validation error: ...`                        |
| EPR is down                    | `Connection failed to EPR server at <url>. ...`         |
| EPR timed out                  | `Request timeout to EPR server at <url>. ...`           |
| EPR returned a failing status  | `Failed to <do thing>: <status> - <body>`               |

Callers that need to tell success from failure check whether the text is JSON,
as `demos/mcp_client_demo.py` does.

## Operations

`validate_input(operation, input_data)` is the entry point. Its operations are
`search_events`, `search_receivers`, `search_groups`, `create_event`,
`create_receiver`, `create_group`, and the three `fetch_*` operations. It
returns the validated data as a dictionary, with aliases applied.

```python
from epr_mcp.schemas import validate_input

validated = validate_input("search_events", {"data": {"name": "foo", "version": "1.0.0"}})
```

## Tests

`tests/unit/test_schemas.py` covers the models and
`tests/unit/test_server_tools.py` covers the tools end to end with a mocked EPR:

```bash
uv run pytest tests/unit/test_schemas.py tests/unit/test_server_tools.py
```
