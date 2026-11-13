# 06 Use It from an Editor

Time: 20 minutes.

Now an AI assistant uses your server. Both editors start your server as a local
process over stdio with `uv run`. Nothing runs in Docker except EPR.

## Why not Docker for the MCP server

Editors can start an MCP server with `docker run -i`, but it is fragile:
container networking to EPR, interactive stdin, image rebuilds after every edit,
and startup timeouts all cause failures that look like MCP problems. A local
`uv run` has none of these, so this workshop uses it.

## Check first

```bash
uv run python check_setup.py
```

This time leave out `--skip-stdio`. Two lines matter: "workshop server via uv
run" and "shipped server via uv run". They start servers with the exact commands
in the editor configs and list their tools. If both pass, the editors will
launch them. The first run can take a minute while uv installs packages; that is
also why you run this before opening the editor.

## VS Code

1. Make sure `work/` has your finished server, or use the checkpoint:
   `cp checkpoint_05_tests/server.py work/server.py`.
2. Open the folder `docs/tutorials/code` in VS Code (File, Open Folder). The
   workspace folder must be this one, because the configuration uses
   `${workspaceFolder}`.
3. Open `.vscode/mcp.json`. It defines two servers:
   - `epr-workshop` runs the finished workshop server,
     `checkpoint_05_tests/server.py`. To run your own, change the last argument
     to `work/server.py`.
   - `epr-mcp` runs the shipped server of this repository,
     `eprmcp start --transport stdio`.
4. Above each server in the file, click Start. When the status says Running, the
   tool count appears next to it. Or press Ctrl+Shift+P (Cmd+Shift+P on macOS),
   run MCP: List Servers, pick a server, and choose Start Server.
5. Open Chat, switch to Agent mode, click the tools icon, and make sure the EPR
   tools are ticked.
6. Ask in plain language:
   - "Search EPR for events named checkout-service."
   - "Which of those failed?"
   - "Fetch the event receiver that checkout-service events belong to."
   - "Create an event receiver called demo.build of type demo.build." (The model
     must also supply a version, a description, and a schema; watch what it asks
     you for.)
7. VS Code asks for confirmation before it runs a tool. Expand the call to see
   the exact arguments the model chose. Compare them with your input models from
   module 04.

If a server does not start, run MCP: List Servers, choose it, and select Show
Output. The error is usually one of the rows in the table at the end of this
module.

## Claude Desktop (macOS)

Claude Desktop does not inherit your shell PATH, so the config needs the full
path to uv and to the repository.

1. Find uv: `which uv`.
2. Find the repository path: run `pwd` in the repository root.
3. Open the Claude Desktop config at
   `~/Library/Application Support/Claude/claude_desktop_config.json`, or
   Settings, Developer, Edit Config.
4. Copy the contents of `claude_desktop_config.json` from this folder and
   replace `/ABSOLUTE/PATH/TO/uv` and `/ABSOLUTE/PATH/TO/epr-mcp-python` with
   the real paths. If the file already has other servers, merge the two
   `mcpServers` entries into it.
5. Quit Claude Desktop completely and reopen it. Ask: "What EPR tools do you
   have?"

Claude Desktop is not available on Linux; use VS Code there.

## Option: HTTP instead of stdio

The shipped server can also run as a long-lived HTTP server, which is what you
would deploy:

```bash
uv run --directory ../../.. eprmcp start --transport http --host 127.0.0.1 --port 8000 --url http://localhost:8042
```

Connect the Inspector to it with transport Streamable HTTP and URL
`http://localhost:8000/mcp`, or call it from Python with
`Client("http://localhost:8000/mcp")`. Its Swagger page is at
`http://localhost:8000/docs`. This is optional; the workshop path is stdio.

## The fallback ladder

If an editor will not cooperate, move down a rung. All three exercise the same
server.

1. The editor, as above.
2. The Inspector: module 02, pointed at `checkpoint_05_tests/server.py`.
3. The terminal: `client.py` from module 01, pointed at
   `checkpoint_05_tests/server.py`.

## When the editor cannot start the server

| Symptom                                  | Cause and fix                                                              |
| ---------------------------------------- | -------------------------------------------------------------------------- |
| `spawn uv ENOENT` or "command not found" | The editor cannot see uv. Use the full path from `which uv` as `command`   |
| Server starts, then exits at once        | Run the same command in a terminal; `check_setup.py` shows the real error  |
| Start times out the first time           | uv was still installing. Run `uv sync` in the folder, then Start again     |
| Tools list is empty or stale             | Stop and Start the server after editing the code                           |
| "Cannot reach EPR"                       | EPR is down: `docker compose up -d`, or `EPR_URL` points to the wrong host |
| Wrong folder                             | In VS Code, the opened folder must be `docs/tutorials/code`                |

## Checkpoint

An AI assistant, in VS Code or Claude Desktop, found events in EPR through your
server.

Next: [07 Misc and troubleshooting](07_misc_and_troubleshooting.md).
