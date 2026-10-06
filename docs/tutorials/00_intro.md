# 00 Intro and Prerequisites

Time: 15 minutes.

## What is MCP

An MCP server (Model Context Protocol server) is a standard way to give an AI
assistant tools. The assistant asks the server what it can do, then calls those
tools with typed arguments and reads the results. Think of it as a universal
adapter between AI models and your own systems.

Three words to know:

- Host: the application the user sits in, such as VS Code or Claude Desktop.
- Client: the part of the host that speaks MCP to a server.
- Server: your code. It exposes tools.

A tool is a function with a name, a description, and a typed input. The
description matters most: it is what the model reads to decide when to use the
tool.

MCP also defines resources and prompts. This workshop only uses tools.

## What is EPR

The Event Provenance Registry stores a trail of what happened to software as it
moved through a delivery pipeline. It has three kinds of records:

- Event receiver: declares a kind of event and the JSON schema its payload must
  match.
- Event receiver group: a named set of receivers.
- Event: something that happened, such as a build, linked to one receiver.

EPR has a REST API for fetching and creating records and a GraphQL endpoint for
searching. Your server wraps both.

## Prerequisites

| Tool            | Needed for                    | Check                    |
| --------------- | ----------------------------- | ------------------------ |
| Python 3.12+    | running the code              | `python3 --version`      |
| uv              | Python environments           | `uv --version`           |
| Docker, Compose | running EPR                   | `docker compose version` |
| Node.js         | the MCP Inspector (module 02) | `npx --version`          |
| VS Code         | module 06                     | `code --version`         |

Install uv from <https://docs.astral.sh/uv/>. The workshop supports macOS and
Linux.

## Set up

Clone the repository and move to the workshop code. Every command from here on
runs in this directory.

```bash
git clone https://github.com/xbcsmith/epr-mcp-python.git
cd epr-mcp-python/docs/tutorials/code
```

Install the pinned Python dependencies (FastMCP 4 and httpx2):

```bash
uv sync
```

Start EPR, Postgres, and Redpanda. The first run builds the EPR server, which
takes about three minutes.

```bash
docker compose up -d --build
```

Wait until EPR answers. This prints `200` when it is ready:

```bash
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8042/healthz/readiness
```

Create sample data: one receiver, one group, and three events.

```bash
uv run python seed_epr.py
```

It prints the new IDs and saves them to `seed_ids.json`. You will use an event
ID in the next module.

## Checkpoint: run the preflight

```bash
uv run python check_setup.py --skip-stdio
```

Every line should say PASS or SKIP. A SKIP line is a check that does not apply
yet, such as your own `work/server.py` before you have written it. If a line
says FAIL, fix it before continuing:

| Line that failed     | Fix                                                      |
| -------------------- | -------------------------------------------------------- |
| Python 3.12 or newer | Install Python 3.12 or newer                             |
| uv on PATH           | Install uv, then open a new terminal                     |
| EPR reachable        | `docker compose up -d --build`, wait a minute, run again |

You can leave out `--skip-stdio` once module 06 is done; that run also starts
the servers exactly the way an editor does.

Next: [01 First tool](01_first_tool.md).
