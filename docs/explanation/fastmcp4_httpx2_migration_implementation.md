# FastMCP 4 and httpx2 Migration Implementation

This document records what was found and done during the migration. It is filled
in phase by phase; see
[the implementation plan](./fastmcp4_httpx2_migration_implementation_plan.md).

## Phase 0: Migration Findings

Research date: 2026-10-06. Method: read the upstream docs, then installed
`fastmcp` 4.0.11 and the pre-migration set into scratch virtualenvs outside the
repo and exercised the current code against them. No repository code changed in
this phase.

### Baseline (pre-migration code)

Environment: Python 3.12.11, `fastmcp` 2.12.4, `httpx` 0.28.1.

| Check                      | Result                                                                       |
| -------------------------- | ---------------------------------------------------------------------------- |
| `ruff check src/`          | 2 errors, 1 auto-fixable (import ordering in `server.py`); not clean         |
| `pytest`                   | 126 passed, 0 failed                                                         |
| Coverage over `src/`       | 40% total; `server.py` 5%, `schemas.py` 64%; below the 80% gate in AGENTS.md |
| Committed wheel in `dist/` | Contains no `openapi.yaml` (see Findings, item 6)                            |

### Verified facts about FastMCP 4.0.11 and httpx2 2.13.1

| Topic                         | Finding                                                                                                                 |
| ----------------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| Python requirement            | `fastmcp` requires Python >= 3.10; the project's `>= 3.12` stays valid                                                  |
| Installed dependency versions | `httpx2` 2.13.1, `httpcore2` 2.13.1, `mcp` 2.3.0, `pydantic` 2.13.5, `starlette` 1.7.0, `truststore` 0.10.4             |
| Legacy `httpx`                | Not installed alongside FastMCP 4; any leftover `import httpx` raises `ModuleNotFoundError`, so the swap is checkable   |
| `FastMCP(...)` constructor    | Second positional parameter is `instructions`; `version` is keyword-only                                                |
| `Context` logging             | `debug`, `info`, `warning`, `error`, `log` exist and are awaitable                                                      |
| `custom_route`                | Present, same shape (`path`, `methods`)                                                                                 |
| `run` / `run_async`           | Same signature: `transport`, `show_banner`, `**transport_kwargs`; `transport="http", host=, port=` works                |
| `fastmcp.server.openapi`      | Removed; `fastmcp.server.providers.openapi` provides `OpenAPIProvider`, `RouteMap`, `MCPType` (moot, module is deleted) |
| In-memory test client         | `Client(server_instance)` works; `mode` defaults to `"auto"`; `Client` also accepts `Path`, URL, and transport objects  |
| stdio transport               | `mcp.run(transport="stdio")` works; a `StdioTransport(command, args)` client lists and calls tools                      |
| httpx2 API                    | `httpx2.MockTransport` exists; default User-Agent is `python-httpx2/2.13.1`                                             |

### Experiment: current server on FastMCP 4

A copy of `src/` with `openapi_server.py` removed and `import httpx` replaced by
`import httpx2 as httpx` was run against FastMCP 4.0.11:

- `server.run(cfg)` constructs the server; all 9 tools register with unchanged
  decorators and `Annotated[..., Field(...)]` parameters.
- An in-memory `Client` lists the 9 tools and calls `fetch_event`; with EPR
  unreachable the tool returns the expected "Connection failed" message, so the
  `httpx2.ConnectError` branch in `handle_http_errors` works through the swap.
- Starlette `TestClient` returns 200 for `/health`, `/openapi.yaml`,
  `/openapi.json`, and `/docs`.

Conclusion: the migration is mostly mechanical; the risks are in the items
below.

### Findings that change the plan

1. **`version` bug confirmed.** The running server reports
   `instructions="1.0.0"` and `version="4.0.11"`. Fix with keyword arguments
   (Phase 2).
2. **Client logging is deprecated.** Every `ctx.debug` and `ctx.error` call
   emits an `MCPDeprecationWarning` stating that the logging capability is
   deprecated as of 2026-07-28 (SEP-2577). Decision needed in Phase 2: move
   diagnostics to Python `logging` (stderr, already configured in `main.py`) and
   keep `ctx` logging out of the tool bodies, which also reduces noise over
   stdio.
3. **Default HTTP bind.** `run()` binds `0.0.0.0:8000` regardless of `MCP_HOST`
   and `MCP_PORT`; unchanged by FastMCP 4, handled in Phase 2.
4. **Lint baseline is not clean.** Fix the 2 existing `ruff` errors in Phase 1
   so later phases can rely on the gate.
5. **Coverage baseline is 40%.** `server.py` needs the Phase 2 in-memory-client
   tests to reach the 80% gate.
6. **Packaging bug.** The wheel built from the current `pyproject.toml` does not
   include `openapi.yaml`, so `/openapi.yaml` and `/openapi.json` would return
   404 in the Docker image. Add package data (and a test that the file is found)
   in Phase 2.
7. **Build backend.** `build-backend = "setuptools.build_meta:__legacy__"` and
   the `py2.py3` universal wheel tag are stale; reconsider in Phase 2 together
   with the Dockerfile wheel glob.

### Target versions

| Dependency  | Constraint to set in `pyproject.toml` |
| ----------- | ------------------------------------- |
| Python      | `>= 3.12` (unchanged)                 |
| `fastmcp`   | `>= 4.0, < 5`                         |
| `httpx2`    | `>= 2.13`                             |
| `pydantic`  | `>= 2.12`                             |
| `starlette` | `>= 1.0` (FastMCP 4 resolves 1.7.0)   |
| `httpx`     | Removed                               |

### Remaining unverified items

- `uv run` launching the stdio server from VS Code and Claude Desktop (the stdio
  transport itself is verified). Confirmed in Phase 3 on macOS and Linux.
- Whether `fastmcp` 4 emits a deprecation warning for the `mcp.run(...)` call
  styles the tutorials will teach; check while writing module 01.
