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

## Phase 1: Dependency and httpx2 Migration

### Changes

- `pyproject.toml`: `fastmcp>=4.0,<5`, `httpx2>=2.13`, `pydantic>=2.12`,
  `starlette>=1.0`; `httpx` removed; tox `extras` fixed to `test`.
- `src/epr_mcp/server.py`: `import httpx2`; the exception checks in
  `handle_http_errors` use `httpx2` types; the 9 client sites use
  `create_client(cfg)`.
- `src/epr_mcp/common.py`: new `create_client(cfg)` returning an
  `httpx2.AsyncClient` with a JSON content type and an optional bearer header.
- `src/epr_mcp/config.py`: `Config.token` is optional (default `None`); it was
  typed `str` but is passed `None` when no token is set.
- `src/epr_mcp/openapi_server.py`: deleted (decision); it imported the removed
  `fastmcp.server.openapi` and the legacy `httpx`.
- `tests/unit/test_http_errors.py`: new tests for `handle_http_errors` (connect,
  timeout, status, generic errors) and a guard against legacy `httpx` imports.
- `tests/unit/test_common.py`: new `TestCreateClient` covering the bearer
  header, no header without a token, and the client type.

The two baseline `ruff` errors are fixed.

### Behavior changes (for the 2.0 notes)

- The EPR token is now sent as `Authorization: Bearer` on every request made by
  `server.py`. Before, `server.py` never sent it.
- The User-Agent becomes `python-httpx2/<version>`.
- TLS verification uses the operating system trust store instead of the bundled
  `certifi` certificates; `SSL_CERT_FILE` and `SSL_CERT_DIR` are still honored.
- The three POST search tools no longer set their own `Content-Type` header; the
  shared client sets it.

### Results

`ruff check src/ tests/` passes, 134 tests pass (126 before), and no legacy
`httpx` import remains in `src/` or `tests/`. Coverage is 43% (was 40%);
`server.py` coverage arrives with the Phase 2 in-memory-client tests.

## Phase 2: FastMCP 4 API Migration

### Phase 2 changes

- `src/epr_mcp/server.py`:
  - `run(cfg)` is split into `create_server(cfg)` (builds the `FastMCP` instance
    with all tools and routes, binds nothing) and `run(cfg)` (picks the
    transport and starts it).
  - `FastMCP(name="EPR MCP Server", version="1.0.0")` uses keyword arguments;
    the server previously reported `"1.0.0"` as its instructions.
  - All `ctx.debug` and `ctx.error` calls are now `logger.debug` and
    `logger.error`, and the unused `ctx: Context` parameters are removed from
    the tools. `handle_http_errors(e, operation, cfg)` is a plain function.
  - `run` supports `stdio` (banner off, so nothing but protocol traffic is
    written to stdout) and `http` with the configured host and port, using
    `mcp.run(...)` instead of `asyncio.run(mcp.run_async(...))`. It rejects any
    other transport with `ValueError`, and no longer logs the token (it logs
    only whether one is configured).
- `src/epr_mcp/config.py`: `Config` gains `transport`, `host`, and `port`;
  `TRANSPORTS` lists the valid transports.
- `src/epr_mcp/main.py`: new `--transport`, `--host`, and `--port` options with
  `MCP_TRANSPORT`, `MCP_HOST`, and `MCP_PORT` as defaults. The token is read
  from `EPR_API_TOKEN` or `EPR_TOKEN`.
- `pyproject.toml`: `openapi.yaml` is package data; the build backend is the
  standard `setuptools.build_meta`; the `universal` wheel setting is removed so
  the wheel is tagged `py3-none-any`; `pytest-asyncio` and `pytest-cov` are in
  the test extra and tox deps.
- `Dockerfile`: installs `dist/epr_mcp-*-py3-none-any.whl` instead of a
  hard-coded `0.1.0` file name. `Makefile`: `make wheel` removes `build/` and
  `dist/` first, because a stale `build/lib` previously leaked deleted modules
  into the wheel.

### Phase 2 behavior changes

- New `--transport stdio|http`, `--host`, and `--port` options and matching
  environment variables. Defaults match the old behavior (`http`, `0.0.0.0`,
  `8000`).
- `EPR_TOKEN`, which `docker-compose.yaml` and `.env.example` set, now reaches
  the server. Before, only `EPR_API_TOKEN` was read, so the token never arrived
  in Docker.
- Tool diagnostics go to the server log, not to MCP client log notifications.
- `/openapi.yaml` and `/openapi.json` work from the installed wheel; the old
  wheel omitted the spec.

### Testing

203 tests pass and 2 functional tests are skipped by default; coverage is 87%
(`server.py` 82%, up from 5%). New files:

- `tests/unit/test_server_tools.py`: in-memory `Client` against `create_server`,
  with EPR replaced by `httpx2.MockTransport`; covers tool registration and
  schemas, success, empty, non-2xx, validation failure, connect error, and
  timeout for all 9 tools, plus the bearer header.
- `tests/unit/test_server_routes.py`: the four HTTP routes through the Starlette
  `TestClient`, and a check that the spec ships as package data.
- `tests/unit/test_server_run.py`: transport selection, host and port, token not
  logged, debug flag.
- `tests/unit/test_main.py`: command line and environment handling.
- `tests/functional/test_transports.py`: starts the real process over stdio and
  over HTTP and lists the tools. Run with `EPR_MCP_FUNCTIONAL=1`; both pass.

### Verified against a real build

A wheel built from a clean copy of the tree contains `openapi.yaml` and no
`openapi_server.py`. The image built from it reports `healthy`, serves
`/health`, `/openapi.yaml`, and `/openapi.json` with 200, lists 9 tools over
HTTP through a FastMCP 4 client, returns the "Connection failed" message with no
EPR running, and has no legacy `httpx` installed.

### Not yet verified

- A `fetch_event` call against a running EPR, `docker compose up`, and the MCP
  Inspector. They need a running EPR, which Phase 3 sets up; they remain part of
  the Phase 2 success criteria until then.
- `uv run` launching the stdio server from VS Code (Phase 3).

### Flat tool arguments

The search and create tools used to require their argument wrapped one level
deeper (`search_events` took `{"data": {"data": {"name": ...}}}`, `create_event`
took `{"event_data": {"data": {...}}}`), although the tool descriptions implied
flat input, so a normal MCP client got "Field required". This is fixed:

- `server.py` adds the `data` wrapper internally before `validate_input`, so
  tools take flat input: `search_events` takes `{"data": {"name": "foo"}}` and
  `create_event` takes `{"event_data": {...fields...}}`. The tool parameter
  names and the JSON schemas are unchanged.
- The six search and create input models in `schemas.py` now forbid unknown
  keys. Without this, a caller still using the old wrapped shape would have its
  criteria silently dropped and run an unfiltered search that returns every
  record. It now gets an input validation error and no request is sent.
- The `search_groups` description no longer mentions an `enabled` criterion,
  which the model never supported; sending it is now rejected.
- Tests: all tool tests use flat input; new `TestFlatArguments` covers the
  rejection of the old wrapped shape and of unknown criteria for every search
  and create tool, and `test_schemas.py` covers the unknown-key rejection.
  Totals: 215 tests pass, 2 functional tests skipped by default, coverage 88%.

This is a breaking change for any client that sent the old wrapped shape; list
it in the 2.0 notes.

### Existing problem found, left unchanged

`schemas.py` calls `raise ValidationError("...")` with the Pydantic class, which
cannot be constructed that way; those branches would fail with a `TypeError`
instead of a validation message.

## Phase 3: Tutorial Rewrite for Workshop Delivery

### Phase 3 changes

- `docs/tutorials/`: the six hyphenated tutorials (which taught the official
  `mcp` SDK, `pip install mcp[cli] httpx`, and Docker-launched stdio) are
  replaced by `README.md` (agenda, prerequisites, checkpoint table, facilitator
  notes) and eight lowercase modules: `00_intro`, `01_first_tool`,
  `02_inspector`, `03_complete_tool_set`, `04_validation_and_errors`,
  `05_test_it`, `06_use_from_an_editor`, and `07_misc_and_troubleshooting`.
- `docs/tutorials/code/`: `pyproject.toml` and `uv.lock` pinning `fastmcp`
  4.0.11 and `httpx2` 2.13.1; four checkpoint directories; `docker-compose.yaml`
  and `epr/Dockerfile` for EPR only; `seed_epr.py`; `check_setup.py`
  (preflight); `client.py` (terminal MCP client); `.vscode/mcp.json` and
  `claude_desktop_config.json` for two servers, the workshop server and the
  shipped `eprmcp`, both launched with `uv run` over stdio.
- `tests/tutorials/test_tutorial_code.py`: every checkpoint server imports and
  lists the right tools, the checkpoint 05 tests pass, checkpoint 05's server
  equals checkpoint 04's, both editor configs reference existing files, the
  compose file runs only EPR services, file names follow AGENTS.md Rule 1, and
  no stale `mcp.server.fastmcp`, `import httpx`, or FastMCP 2 references remain
  outside module 07.
- `Makefile`: new `workshop-check` target. `.gitignore`: `work/`,
  `seed_ids.json`, and the saved EPR image are ignored, and the tutorial's
  `.vscode/` is re-included (`.vscode` is ignored repository-wide).
- `pyproject.toml`: `testpaths = ["tests"]` so a plain `pytest` does not collect
  the tutorial code.

### Deviations from the plan

- Checkpoints hold the finished code at the end of a module (the starter for a
  module is the previous checkpoint) instead of separate starter and solution
  directories. There is no checkpoint 02 or 06 because those modules do not
  change code.
- The workshop server is a standalone file, not a copy of the shipped package.
  Module 04 uses `ToolError` for failures; the shipped server returns error
  text.
- The plan's dry run with a person new to the project has not happened, so the
  timings in the agenda are estimates.

### Found by running everything against a real EPR

EPR was built and started with the workshop compose file, then the seed script,
the tutorial servers, and the shipped server were run against it. This found
problems that mocked tests could not:

1. **EPR's own image does not start.** Its Dockerfile builds `FROM scratch` with
   no time zone database, and the server always connects to Postgres with
   `TimeZone=America/New_York`, so it exits with "unknown time zone". The
   workshop `epr/Dockerfile` builds the same pinned commit
   (`f8f115b790c58b8fab3bfd47278e51e4f15e9f0e`) and adds `/usr/share/zoneinfo`.
   There is no published EPR image; the first build takes about three minutes.
2. **The shipped create tools reported failure on success.** EPR answers a
   create with HTTP 200, but the shipped tools only accepted 201, so every
   `create_*` call returned "Failed to create..." although the record was
   created. They now accept 200 and 201.
3. **The shipped create tools failed after a successful create.** EPR returns
   only the new ID (`{"data": "<id>"}`), but the tools tried to validate it as a
   record. They now return
   `{"message": "... created successfully", "id": "<id>"}` when EPR returns an
   ID, and still handle a full record.
4. **`create_receiver` could not work.** EPR requires a `schema` ("invalid
   input: schema is required"), and the input model had no `schema` field (after
   the Phase 2 change to forbid unknown keys, supplying one was rejected too).
   The model now requires `schema`, accepted under that name.
5. **`search_groups` always returned an empty list.** It asked for a
   `fingerprint` field that the EPR GraphQL type `EventReceiverGroup` does not
   have, the query failed, and the error was swallowed. The field is removed,
   and all three search tools now report a GraphQL `errors` list instead of
   hiding it.
6. **Error shapes differ by case.** A well-formed missing ID is HTTP 404; a
   malformed ID or a bad GraphQL query is HTTP 200 with
   `{"data": null, "errors": [...]}`. The tutorial server checks for both. A
   stopped EPR behind Docker's port proxy surfaces as `ReadError` with an empty
   message rather than `ConnectError`, so the tutorial maps `TransportError` and
   shows the exception name.
7. The Inspector is now version 2.9.0 with a different interface and an access
   token in the URL. Module 02 pins that version and describes only the steps
   that hold across versions.

Unit tests were added for items 2 to 5 (`TestAgainstRealEprBehavior` and
`TestCreateReturnsIdOnly` in `tests/unit/test_server_tools.py`); the suite is
238 tests passing with 88% coverage.

### Verified

- On macOS: the full preflight (`check_setup.py`) passes, including starting the
  workshop server and the shipped server with the exact `uv run` commands from
  the editor configs and listing 9 tools each; every command in modules 00 to 05
  was run against the live EPR; `uv run pytest work` and
  `uv run pytest checkpoint_05_tests` pass.
- On Linux (a `uv` Docker image with Python 3.12 and uv 0.9.30): the same
  preflight passes against the macOS-hosted EPR.
- The Phase 2 items that needed a running EPR are now checked: all nine shipped
  tools work against the live EPR, over stdio and over HTTP.

### Not verified

- The VS Code and Claude Desktop screens and the Inspector 2.9.0 interface were
  not opened. Modules 02 and 06 describe the steps from the documentation and
  the launch commands are tested, but the on-screen wording is unconfirmed.
- No dry run of the agenda with a new attendee, so timings are estimates.

## Phase 4: Demos With Scripts

### Phase 4 changes

- `demos/generate_epr_events.py`: moved to `httpx2`; the `ulid` dependency is
  gone (the script now builds ULIDs itself: a 48-bit millisecond timestamp plus
  80 random bits in Crockford base32, covered by tests); the release string used
  `strftime("%Y.%m.%s")`, where `%s` is the epoch seconds on some platforms and
  unsupported on others, and is now `%d`; the script exits 1 when any request
  fails; the `httpx2` request log is quiet so the demo output is readable.
- `demos/openapi_demo.py`: rewritten. The old script was broken (it inserted a
  non-existent `demos/src` on `sys.path`, imported unused modules, and only
  printed a hard-coded tool list). The new one starts the server over HTTP on a
  free port (or uses `--url`), calls `/health`, `/openapi.yaml`,
  `/openapi.json`, and `/docs`, checks that the YAML and JSON agree, and lists
  the tools through a FastMCP 4 client. It needs no EPR.
- `demos/mcp_client_demo.py`: new. A FastMCP 4 client lists the tools, creates a
  receiver and an event, fetches the event, searches for it, and shows a
  malformed ID being rejected. It starts the server over stdio, or uses
  `--server-url` for HTTP.
- `demos/scripts/`: presenter scripts `generate_events_script.md`,
  `openapi_demo_script.md`, and `mcp_client_demo_script.md` (goal,
  prerequisites, commands, expected output, talking points, failure recovery,
  reset) and `run_all.sh`, an unattended rehearsal run that checks
  prerequisites, stops at the first failure, and supports `--skip-generate`.
- `demos/requirements.txt` lists `fastmcp`, `httpx2`, and `PyYAML` (it listed
  `httpx` and `ulid`, while the README said `ulid-py`, and the script called
  `ulid.ulid()`). `demos/README.md` is rewritten: it had an OpenAPI tool list of
  `fetchEvent`-style names that the server never had, an MCP client example that
  used a non-existent API, and said the generator posts 33 events when it
  posts 44.
- `Makefile` `lint` and the tox `check` and `format` environments now include
  `demos/`; `.gitignore` ignores `epr_reports/`, which `--write-to-disk`
  creates.
- `tests/demos/test_demos.py`: ULID format and ordering, the 11 receivers and 44
  events, the dry run (55 curl commands, exit 0), an unreachable EPR (exit 1),
  `--write-to-disk`, the OpenAPI demo end to end, the client demo helpers, no
  legacy `httpx` import, `run_all.sh` syntax and option handling, and that every
  demo has a presenter script and a README entry.

### Phase 4 results

- The 255 tests pass (2 skipped by default) at 88% coverage, and
  `ruff check src tests demos docs/tutorials/code` is clean.
- Against the live EPR on macOS: the generator posts 11 receivers and 44 events
  (exit 0); the client demo passes over stdio and over HTTP; the OpenAPI demo
  passes; `demos/scripts/run_all.sh` exits 0, and exits 1 with a clear message
  when EPR is unreachable.
- On Linux (the `uv` Docker image): `run_all.sh --skip-generate` exits 0 against
  the same EPR.

### Phase 4 notes

- The shipped tools report most problems (validation, EPR unreachable) as plain
  text instead of an MCP error result, so the client demo treats a reply that is
  not JSON as a failure. The workshop server (module 04) uses `ToolError`; the
  shipped server could be changed to match in a later release.
- `src/epr_mcp/openapi.yaml`, which the server serves, calls the service the
  "Event Processing Registry" (it is the Event Provenance Registry) and lists
  `/search` and `/health` paths that the real EPR does not have; its search is
  GraphQL. The presenter script tells the presenter not to promise that every
  listed path exists. Correcting the document is outside this migration.
- The generator does not post its events to groups, and `--write-to-disk` writes
  to the current directory.
