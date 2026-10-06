# Presenter Script: Using the Tools as an AI Assistant Does

Demo file: `demos/mcp_client_demo.py`. Time: 10 minutes.

## Goal

Show the full life of a record through MCP tools: create a receiver, create an
event for it, fetch the event, find it by search, and see bad input rejected.
The client plays the role an AI assistant plays in an editor.

## Prerequisites

- EPR running at `http://localhost:8042`:
  `cd docs/tutorials/code && docker compose up -d --build`
- Check:
  `curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8042/healthz/readiness`
  prints `200`.
- A terminal in the repository root, with uv installed.

## Before you start

- Run the demo once to warm uv. Each run adds one receiver and one event with a
  unique name, so reruns are safe.
- Optionally run [the events generator](generate_events_script.md) first so
  searches have more to find.

## Steps

### 1. Run the demo

Say: "No AI model here, just a small client calling the same tools a model
would. By default it starts the server itself over stdio, which is how VS Code
and Claude Desktop run it."

```bash
uv run python demos/mcp_client_demo.py
```

### 2. Walk through the steps

Expected output (abridged; IDs and numbers differ):

```text
[1/6] List the tools the server offers
  fetch_event
  ...
  create_group

[2/6] Create an event receiver (declares a kind of event and its payload schema)
  tool: create_receiver
  arguments: {"receiver_data": {"name": "demo.client.1791298518", ...
  result: { "message": "Event receiver created successfully", "id": "01M48VCDJEXDES63JKS7MYYC95" }

[3/6] Create an event for that receiver
  tool: create_event
  result: { "message": "Event created successfully", "id": "01M48VCDQ4X251XDTR46JR75TV" }

[4/6] Fetch the event by its ID
  tool: fetch_event
  arguments: {"id": "01M48VCDQ4X251XDTR46JR75TV"}

[5/6] Search for the event by name
  tool: search_events
  arguments: {"data": {"name": "demo-service-1791298518"}}

[6/6] Show that bad input is rejected before it reaches EPR
  result: Input validation error: 1 validation error for FetchInput id String should match pattern ...
  rejected as expected: the server never called EPR

Demo completed.
```

Talking points per step:

1. List tools. "Nine tools: fetch, search, and create for each of the three
   record types. The client discovered them; nothing was hard-coded."
2. Create a receiver. "A receiver must carry a JSON schema. Events sent to it
   must match. EPR answers with the new ID, and so does the tool."
3. Create an event. "It points at the receiver by ID. This is the provenance
   link: what happened, and which receiver it belongs to."
4. Fetch. "Same ID, full record back."
5. Search. "Searches go to EPR's GraphQL endpoint. The tool takes plain
   criteria. Every field is optional, and only the ones you set are sent."
6. Bad input. "The server checks the ID format and rejects the call before
   contacting EPR. Guessing is what language models do, so catching bad
   arguments early matters."

### 3. Optional: the same thing over HTTP

In one terminal:

```bash
uv run eprmcp start --transport http --host 127.0.0.1 --port 8000 --url http://localhost:8042
```

In another:

```bash
uv run python demos/mcp_client_demo.py --server-url http://localhost:8000/mcp
```

Say: "Same tools, different transport. stdio is for an editor that launches the
server; HTTP is for a server that stays running."

### 4. Optional: see the server's own log

```bash
uv run python demos/mcp_client_demo.py --show-server-logs
```

## Failure recovery

| Symptom                                | Cause and fix                                                                       |
| -------------------------------------- | ----------------------------------------------------------------------------------- |
| `Connection failed to EPR server`      | EPR is down or `--epr-url` is wrong. Run the readiness check                        |
| `Client failed to connect`             | The server did not start. Run `uv run eprmcp version`; run from the repository root |
| Step 2 fails with `schema is required` | An old copy of the demo or server. Pull the latest, run `uv sync`                   |
| Step 5 finds more than one event       | A name collision from a rerun in the same second. Run it again                      |
| `expected 9 tools`                     | A different server version answered. Check `--server-url`                           |

## Reset

`(cd docs/tutorials/code && docker compose down -v)` removes all EPR data.

Back to the [rehearsal script](run_all.sh), which runs every demo in order.
