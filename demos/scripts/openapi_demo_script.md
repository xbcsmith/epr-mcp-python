# Presenter Script: The HTTP Side of the MCP Server

Demo file: `demos/openapi_demo.py`. Time: 5 minutes.

## Goal

Show that the MCP server is also an ordinary HTTP service: it has a health
check, a published OpenAPI description, and a Swagger page, and it serves the
MCP protocol on `/mcp`. End by listing the tools the way an AI client sees them.

## Prerequisites

- A terminal in the repository root, with uv installed.
- EPR is not needed for this demo: it never calls EPR.
- Port 8000 is not required; the demo picks a free port.

## Before you start

- Run it once ahead of time so uv has installed everything. The first run can
  take a minute.
- Have a browser ready for the Swagger step.

## Steps

### 1. Run the demo

Say: "The script starts the server over HTTP, calls its endpoints one by one,
and then connects an MCP client."

```bash
uv run python demos/openapi_demo.py
```

Expected output (abridged; the port differs):

```text
EPR MCP Server: HTTP endpoints demo
========================================
Starting the server on http://127.0.0.1:60193

[1/5] Health check
GET http://127.0.0.1:60193/health -> 200 'OK'

[2/5] OpenAPI specification as YAML
GET http://127.0.0.1:60193/openapi.yaml -> 200
Title: EPR (Event Processing Registry) API (OpenAPI 3.1.0, API version 1.0.0)
Paths: 10
  GET    /api/v1/events/{id}          Fetch an event by ID
  ...

[3/5] The same specification as JSON
JSON matches the YAML document: True

[4/5] Swagger UI
GET http://127.0.0.1:60193/docs -> 200, 1658 bytes of HTML

[5/5] MCP tools, listed by a FastMCP client
Connected to http://127.0.0.1:60193/mcp and found 9 tools:
  fetch_event        required arguments: id
  ...

Demo completed.
```

### 2. Walk through the steps

1. Health check. "Orchestrators such as Docker and Kubernetes poll this. The
   Docker image's healthcheck uses it."
2. OpenAPI as YAML. "This documents the REST API of the registry that the tools
   wrap." Be accurate about it: the document describes the EPR REST resources
   (events, receivers, groups) and calls the service the Event Processing
   Registry. EPR itself is the Event Provenance Registry, and its search is a
   GraphQL endpoint, so treat the listed `/search` paths as a description of
   intent, not a map of the real service. Do not promise that every path exists.
3. OpenAPI as JSON. "Same document, for tools that prefer JSON. The script
   checks that the two agree."
4. Swagger UI. In a browser, open the URL the demo printed. Note it is only
   reachable while the demo's server runs; to keep one running, see below.
5. MCP tools. "This is the important part. The same server speaks MCP on `/mcp`.
   A client connects, asks for the tools, and gets nine, each with a schema.
   Required arguments are listed: fetch tools take an `id`, search tools take
   `data`, create tools take a named object."

### 3. Optional: keep a server running to show Swagger

```bash
uv run eprmcp start --transport http --host 127.0.0.1 --port 8000
```

Open <http://localhost:8000/docs>, then run
`uv run python demos/openapi_demo.py --url http://localhost:8000` in a second
terminal. Stop the server with Ctrl+C.

## Failure recovery

| Symptom                                              | Cause and fix                                                                         |
| ---------------------------------------------------- | ------------------------------------------------------------------------------------- |
| `the server process exited before it became healthy` | A dependency is missing. Run `uv run eprmcp version`; use `uv run`, not bare `python` |
| `no healthy server ... after 30 seconds`             | First start is slow or blocked. Run once more                                         |
| `ModuleNotFoundError: epr_mcp`                       | Run from the repository root with `uv run`, or `pip install -e .`                     |
| Step 5 fails with a connection error                 | With `--url`, the server must serve `/mcp` over HTTP, not stdio                       |
| Swagger page is blank                                | The page loads its scripts from a CDN; it needs internet access                       |

Next: [Client demo](mcp_client_demo_script.md).
