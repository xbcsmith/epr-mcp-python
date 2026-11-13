# 02 Inspector

Time: 15 minutes.

The [MCP Inspector](https://github.com/modelcontextprotocol/inspector) is a
browser tool for exploring any MCP server. It starts your server, lists its
tools, and lets you call them with a form. Use it whenever you want to see what
an AI client would see, without involving an AI.

## Start it

Run this from `docs/tutorials/code`. The command pins Inspector 2.9.0, the
version this workshop was tested with, so everyone sees the same screen.

```bash
npx @modelcontextprotocol/inspector@2.9.0 \
  -e EPR_URL=http://localhost:8042 \
  uv run --directory "$PWD" python work/server.py
```

The first run downloads the Inspector. It prints a local URL that includes an
access token. Open that exact URL in a browser.

If the connection pane does not already show your server, fill it in by hand:

| Field                | Value                                                                     |
| -------------------- | ------------------------------------------------------------------------- |
| Transport type       | `STDIO`                                                                   |
| Command              | `uv`                                                                      |
| Arguments            | `run --directory /full/path/to/docs/tutorials/code python work/server.py` |
| Environment variable | `EPR_URL` = `http://localhost:8042`                                       |

Two details matter:

- `--directory` makes uv use this folder's environment no matter where the
  Inspector starts it from. Use the full path in the pane.
- The server is started over stdio, the same way VS Code will start it in
  module 06. If it works here, the command is right.

The Inspector's screens change between versions. What you need from it never
does: connect, list the tools, pick one, fill in its arguments, run it, read the
result.

## Explore

1. Connect to the server.
2. Open the tools view and list the tools. You see `fetch_event`.
3. Select `fetch_event`. The input form is built from the tool's schema: one
   string field, `id`. That schema is generated from your type hints.
4. Enter an event ID from `seed_ids.json` and run the tool. The result is the
   event JSON.
5. Run it again with an ID that does not exist, such as `nope`. Notice what
   comes back: EPR's error as plain text, with no sign that the call failed. You
   will fix that in module 04.
6. Look for the server's log output in the Inspector. Your server does not log
   anything yet; module 03 adds logging to stderr.

## The edit-and-reconnect loop

When you change `work/server.py`, disconnect and connect again. The Inspector
starts a fresh server process each time, so your edit takes effect.

## If the Inspector does not work

Skip it. The terminal client does the same job:

```bash
uv run python client.py list work/server.py
uv run python client.py call work/server.py fetch_event '{"id": "PASTE_AN_EVENT_ID"}'
```

| Problem                        | Cause and fix                                                       |
| ------------------------------ | ------------------------------------------------------------------- |
| Page says unauthorized         | Open the full URL, token included, that the terminal printed        |
| `npx: command not found`       | Install Node.js                                                     |
| Connection error               | Run your server with `client.py` (below) to see the real error      |
| Port already in use            | Stop the other Inspector, or set `CLIENT_PORT` and `SERVER_PORT`    |
| Inspector shows another server | It also reads your own MCP config file; pick the server you started |

## Checkpoint

You called `fetch_event` from the Inspector (or `client.py`) and got an event.

Next: [03 Complete the tool set](03_complete_tool_set.md).
