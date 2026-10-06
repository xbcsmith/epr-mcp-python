# 01 First Tool

Time: 20 minutes.

You will write an MCP server with one tool, `fetch_event`, run it, and call it
from the terminal. The finished code is in `checkpoint_01_first_tool/server.py`.

## Create your file

```bash
mkdir -p work
touch work/server.py
```

Everything you write in this workshop goes in `work/`. Git ignores it.

## The server

Open `work/server.py` and build it up in four small steps.

### 1. Imports and settings

```python
import os

import httpx2
from fastmcp import FastMCP

EPR_URL = os.environ.get("EPR_URL", "http://localhost:8042")
```

- `fastmcp` is the framework. This workshop uses FastMCP 4.
- `httpx2` is the HTTP client. It is a drop-in successor to `httpx` with the
  same API; only the package name changed. FastMCP 4 depends on it.
- `EPR_URL` comes from the environment, so the same code works against any EPR.

### 2. Create the server

```python
mcp = FastMCP(name="EPR Workshop MCP Server", version="0.1.0")
```

Pass `name` and `version` by keyword. The second positional parameter of
`FastMCP` is `instructions`, not the version, so
`FastMCP("EPR Workshop MCP Server", "0.1.0")` quietly sets the instructions to
`"0.1.0"`. The shipped server had exactly this bug.

### 3. Register a tool

```python
@mcp.tool(title="Fetch Event", description="Fetch an event from EPR by its ID")
async def fetch_event(id: str) -> str:
    """Fetch an event from the EPR."""
    async with httpx2.AsyncClient() as client:
        response = await client.get(f"{EPR_URL}/api/v1/events/{id}")
        return response.text
```

What FastMCP does with this:

- The decorator registers the function as a tool.
- The function name becomes the tool name.
- The type hints become a JSON schema, so an AI client knows `id` is a string.
- `description` is what the model reads to decide when to call the tool.
- `async def` lets the server wait for EPR without blocking.

### 4. Run it

```python
if __name__ == "__main__":
    mcp.run()
```

`mcp.run()` serves over stdio by default: the host starts your script as a
subprocess and exchanges messages over its stdin and stdout. Because stdout is
the protocol channel, never `print()` in a tool. Write logs to stderr.

## Try it from the terminal

Starting the server directly looks like it hangs; it is waiting for an MCP
client on stdin. Press Ctrl+C to stop it.

```bash
uv run python work/server.py
```

Use the workshop client instead. It starts your server the way an editor would,
then talks to it:

```bash
uv run python client.py list work/server.py
```

You should see:

```text
fetch_event: Fetch an event from EPR by its ID
```

Now call the tool with an event ID from `seed_ids.json`:

```bash
uv run python client.py call work/server.py fetch_event '{"id": "PASTE_AN_EVENT_ID"}'
```

You should see the event as JSON, starting with `{"data":`.

## Checkpoint

- `client.py list` shows `fetch_event`.
- `client.py call` returns an event from EPR.
- Behind schedule? `cp checkpoint_01_first_tool/server.py work/server.py`.

## Things to notice

- The tool returns EPR's raw response text. If the ID does not exist, you get
  EPR's error text back as if it were a normal answer. Modules 03 and 04 fix
  that.
- There is no `Context` argument and no `ctx.debug()` logging. FastMCP 4
  deprecates sending logs to the client through the protocol; use Python's
  `logging` module, which goes to stderr.

Next: [02 Inspector](02_inspector.md).
