# HTTP Endpoints and the OpenAPI Description

When the server runs with the `http` transport it serves a few ordinary HTTP
endpoints next to the MCP endpoint. They are registered in
`src/epr_mcp/server.py` with `custom_route`. With the `stdio` transport there is
no HTTP server, so none of this applies.

## Endpoints

On the default address `http://127.0.0.1:8000`:

| Endpoint        | Method | Returns                                                     |
| --------------- | ------ | ----------------------------------------------------------- |
| `/mcp`          | MCP    | The MCP endpoint, spoken to by an MCP client                |
| `/health`       | GET    | `200` with the text `OK`; used by Docker and load balancers |
| `/openapi.yaml` | GET    | The OpenAPI document as YAML                                |
| `/openapi.json` | GET    | The same document as JSON                                   |
| `/docs`         | GET    | A Swagger UI page that loads `/openapi.json`                |

If the document cannot be found, `/openapi.yaml` and `/openapi.json` answer
`404` with `{"error": "OpenAPI specification not found"}`.

```bash
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/openapi.json
```

The [OpenAPI demo](../../demos/openapi_demo.py) calls each endpoint and lists
the tools; its presenter script is
[openapi_demo_script.md](../../demos/scripts/openapi_demo_script.md).

## The document

The document is `src/epr_mcp/openapi.yaml`, an OpenAPI 3.1 file. It is shipped
as package data (`[tool.setuptools.package-data]` in `pyproject.toml`), so it is
in the wheel and the Docker image. Before 2.0 it was left out of the wheel and
these routes answered `404` in the container.

Read it with some care:

- It describes REST-style resources (events, receivers, groups: fetch by ID,
  create, and a `/search` operation for each) and a `/health` path. It is
  documentation, not something the server generates its tools from or serves.
- It calls the service the "Event Processing Registry". The service is the Event
  Provenance Registry.
- The real EPR searches through GraphQL at `/api/v1/graphql/query`, which is
  what the search tools use, and it has no `/search` paths or `/health` path
  (its health endpoints are `/healthz/liveness` and `/healthz/readiness`).

Treat it as a sketch of the data model, and the tools as the source of truth.
Correcting it is not part of the 2.0 migration.

## What was removed

Versions before 2.0 also contained `openapi_server.py`, an unfinished
alternative server that tried to generate tools from this document with
FastMCP's OpenAPI provider. Nothing started it, it had no route handling, and it
imported a module that FastMCP 4 moved, so 2.0 removes it. The nine tools are
written by hand in `server.py` and validated as described in
[schema_validation.md](./schema_validation.md).

## Changing the endpoints

Add a route with `@mcp.custom_route(path, methods=[...])` inside
`create_server`, add a test to `tests/unit/test_server_routes.py` (it uses
Starlette's `TestClient` against `mcp.http_app()`), and list the route here.
