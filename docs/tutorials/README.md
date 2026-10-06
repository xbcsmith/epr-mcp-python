# Build an MCP Server for the Event Provenance Registry

A hands-on workshop. You build an MCP server in Python that lets an AI assistant
read from and write to an Event Provenance Registry (EPR), then use it from VS
Code and Claude Desktop. It uses FastMCP 4 and httpx2, the same stack as the
shipped `epr-mcp` server in this repository.

## Who this is for

Developers who can read Python and use a terminal. You do not need to know MCP,
EPR, async Python, or Docker in depth.

## What you will have at the end

- A working MCP server with nine tools: fetch, search, and create for events,
  event receivers, and event receiver groups.
- Input validation, clear error messages, and tests that need no network.
- The server running in an editor, plus three ways to test it when the editor
  misbehaves.

## Agenda

| Module                                                        | What you do                                            | Time   |
| ------------------------------------------------------------- | ------------------------------------------------------ | ------ |
| [00 Intro and prerequisites](00_intro.md)                     | Install tools, start EPR, seed data, run the preflight | 15 min |
| [01 First tool](01_first_tool.md)                             | One `fetch_event` tool, called from the terminal       | 20 min |
| [02 Inspector](02_inspector.md)                               | Explore and call the tool in the MCP Inspector         | 15 min |
| [03 Complete the tool set](03_complete_tool_set.md)           | Add receivers, groups, search, and create              | 30 min |
| [04 Validation and errors](04_validation_and_errors.md)       | Typed inputs, strict models, useful errors             | 20 min |
| [05 Test it](05_test_it.md)                                   | In-memory client tests with a mocked EPR               | 20 min |
| [06 Use it from an editor](06_use_from_an_editor.md)          | VS Code and Claude Desktop over stdio                  | 20 min |
| [07 Misc and troubleshooting](07_misc_and_troubleshooting.md) | uv tips, FastMCP 4 notes, fixes                        | 10 min |

Total: 2 hours 30 minutes, including a break. Modules 00 to 06 are the core
path.

## How the workshop is set up

Only EPR runs in Docker. Your MCP server always runs on your machine, started by
a uv-managed Python environment, and talks to the editor over stdin and stdout
(the `stdio` transport). Running an MCP server inside a container that an editor
launches is unreliable, so this workshop never does it.

```text
docs/tutorials/code/
  docker-compose.yaml        EPR, Postgres, and Redpanda (no MCP server)
  epr/Dockerfile             builds the EPR server
  pyproject.toml             pinned workshop dependencies (uv)
  seed_epr.py                creates sample data in EPR
  check_setup.py             preflight check
  client.py                  terminal MCP client, the editor-free fallback
  checkpoint_01_first_tool/  finished code at the end of module 01
  checkpoint_03_tool_set/    finished code at the end of module 03
  checkpoint_04_validation/  finished code at the end of module 04
  checkpoint_05_tests/       module 04 server plus its tests
  .vscode/mcp.json           VS Code server configuration
  claude_desktop_config.json Claude Desktop server configuration
  work/                      your own code (you create it, git ignores it)
```

All commands in the modules run from `docs/tutorials/code` unless they say
otherwise.

## Stuck? Jump to a checkpoint

Each checkpoint holds the finished code for a module. Copy it into `work/` and
carry on.

| You are stuck in | Copy this                                              |
| ---------------- | ------------------------------------------------------ |
| Module 01 or 02  | `cp checkpoint_01_first_tool/server.py work/server.py` |
| Module 03        | `cp checkpoint_03_tool_set/server.py work/server.py`   |
| Module 04        | `cp checkpoint_04_validation/server.py work/server.py` |
| Module 05 or 06  | `cp -r checkpoint_05_tests/. work/`                    |

Modules 02 and 06 do not change your code, so a checkpoint from the module
before them is enough.

## If something does not work

1. Run `uv run python check_setup.py`. The first FAIL line says what to fix.
2. Use [07 Misc and troubleshooting](07_misc_and_troubleshooting.md).
3. Skip the editor. `uv run python client.py` exercises any server from the
   terminal, and the Inspector in module 02 works without VS Code.

## Notes for facilitators

Before the session:

- Ask attendees to complete [module 00](00_intro.md) at home, including
  `uv run python check_setup.py`. The first EPR image build takes about three
  minutes and downloads about a gigabyte.
- Build the EPR image once, then share it for the room with
  `docker save epr-server:workshop | gzip > epr-server.tar.gz`. Attendees run
  `docker load < epr-server.tar.gz` and `docker compose up -d` and skip the
  build. Pull the `postgres:16` and Redpanda images the same way.
- Pre-warm uv: run `uv sync` in `docs/tutorials/code` and
  `uv run eprmcp version` in the repository root while online. The first
  `uv run` in an editor config can exceed the editor's start timeout if packages
  still need downloading.
- The supported systems are macOS and Linux. Claude Desktop is macOS only; Linux
  attendees use VS Code.

During the session:

- Keep the fallback ladder in mind: editor, then Inspector, then `client.py`.
  Move an attendee down a rung rather than spend the room's time debugging one
  editor.
- At the start of each module, ask who is not at the previous checkpoint and
  have them copy it from the table above.
- Module 04 breaks and repairs EPR on purpose (`docker compose stop`); warn the
  room first.
- To reset everything, run `docker compose down -v`, then `docker compose up -d`
  and `uv run python seed_epr.py` again.

Timings are estimates until the agenda has been dry-run; record actual times in
[the implementation notes](../explanation/fastmcp4_httpx2_migration_implementation.md).
