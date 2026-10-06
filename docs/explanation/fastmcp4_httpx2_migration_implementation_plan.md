# FastMCP 4 and httpx2 Migration Implementation Plan

## Overview

Migrate `epr-mcp` from FastMCP 2.x (installed: 2.12.4) and `httpx` (0.28.1) to
FastMCP 4 and `httpx2`. Update the tutorials in `docs/tutorials/` into a single
end-to-end, workshop-teachable path, and update the demos in `demos/` so each
has a presenter script. Sources:

- <https://gofastmcp.com/getting-started/whats-new>
- <https://gofastmcp.com/getting-started/upgrading/from-fastmcp-3>
- <https://pydantic.dev/docs/httpx2/get-started/migration>

Facts taken from those pages (everything else in this plan must be verified in
Phase 0):

| Area            | Change                                                                                                                                                 |
| --------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ |
| HTTP library    | FastMCP 4 uses `httpx2` exclusively; exception hierarchy matches, so it is an import swap                                                              |
| Imports         | `fastmcp.server.openapi` moves to `fastmcp.server.providers.openapi`                                                                                   |
| Imports         | `fastmcp.server.proxy` moves to `fastmcp.server.providers.proxy`                                                                                       |
| Requirements    | Pydantic >= 2.12; httpx2 requires Python >= 3.10                                                                                                       |
| Removed         | `ctx.sample()`, `ctx.sample_step()`, `ctx.list_roots()`, `sampling_handler=`                                                                           |
| Protocol        | Modern sessionless protocol is default; `ctx.elicit()` needs `mode="legacy"` clients                                                                   |
| httpx2 behavior | `httpx2` and `httpcore2` package names, `python-httpx2/<version>` User-Agent, OS trust store via `truststore`, logger names `httpx2` and `httpcore2.*` |

## Current State Analysis

### Existing Infrastructure

| Item                                                     | State                                                                                                                                                                                                                                                                                                                                                                        |
| -------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [pyproject.toml](../../pyproject.toml)                   | Unpinned `fastmcp`, `httpx`, `pydantic`, `starlette`, `PyYAML`; `requires-python >= 3.12`                                                                                                                                                                                                                                                                                    |
| [server.py](../../src/epr_mcp/server.py)                 | `run(cfg)` registers 9 tools (fetch/search/create for events, receivers, groups) and 4 `custom_route` endpoints (`/health`, `/openapi.yaml`, `/openapi.json`, `/docs`); 9 `httpx.AsyncClient` call sites; `handle_http_errors` checks `httpx.ConnectError`, `httpx.TimeoutException`, `httpx.HTTPStatusError`; ends with `asyncio.run(mcp.run_async(transport="http", ...))` |
| [openapi_server.py](../../src/epr_mcp/openapi_server.py) | `EPROpenAPIHandler` (6 `httpx.AsyncClient` call sites) plus `create_openapi_server` using `FastMCPOpenAPI`, `MCPType`, `RouteMap` imported from `fastmcp.server.openapi`; not wired into [main.py](../../src/epr_mcp/main.py)                                                                                                                                                |
| [main.py](../../src/epr_mcp/main.py)                     | argparse dispatch; `start` calls `server.run(cfg)`; always binds `0.0.0.0:8000`                                                                                                                                                                                                                                                                                              |
| Tests                                                    | `tests/unit/test_server.py` covers only `filter_none_values`; `tests/test_smoke.py` imports modules; `tests/test_base.py` empty; `tests/functional/` empty                                                                                                                                                                                                                   |
| Docker                                                   | [Dockerfile](../../Dockerfile) installs prebuilt wheel `dist/epr_mcp-0.1.0-py2.py3-none-any.whl` on UBI8 Python 3.12; [docker-compose.yaml](../../docker-compose.yaml) healthchecks `/health`                                                                                                                                                                                |
| [docs/tutorials/](../tutorials/)                         | `00-intro` to `05-mcp-misc`; `README.md` is empty; tutorials 01 and 05 install `mcp[cli] mcp httpx` and import `mcp.server.fastmcp` (the official SDK), not the `fastmcp` package; 04 repeats the 9 `httpx.AsyncClient` snippets; one link points to "FastMCP 2.0"                                                                                                           |
| [demos/](../../demos/)                                   | `generate_epr_events.py` uses `httpx.Client` and `ulid`; `openapi_demo.py` is a print-only script; `requirements.txt` lists `httpx>=0.23.0` and `ulid>=1.1.0`; no demo has a script                                                                                                                                                                                          |
| `temp/`                                                  | Scratch `server.py` (SDK-style FastMCP) and `notes.md` (curl commands to seed EPR receivers)                                                                                                                                                                                                                                                                                 |

### Identified Issues

1. `FastMCP("EPR MCP Server", "1.0.0")` in `server.py` passes the version as the
   second positional argument, which in FastMCP 2.x is `instructions`, not
   `version`. Verify against FastMCP 4 and switch to keyword arguments.
2. `openapi_server.py` imports from the moved path `fastmcp.server.openapi`, is
   unused by the CLI, and contains an unfinished handler/route-map design
   (comment: "In a full implementation..."). Decision: delete it.
3. `server.py` is about 700 lines with almost no test coverage, but
   [AGENTS.md](../../AGENTS.md) requires 80% coverage. A migration without
   behavioral tests is unverifiable.
4. `demos/openapi_demo.py` is broken: it inserts `demos/src` on `sys.path` (does
   not exist) and imports `run` and `Config` it never uses.
5. Demo dependency drift: `requirements.txt` says `ulid`, the README says
   `ulid-py`, the script calls `ulid.ulid()`.
6. Tutorials teach the official `mcp` SDK, but the product ships on the
   `fastmcp` package; learners will not reproduce the real server.
7. Tutorial file names (`00-intro.md`) violate AGENTS.md Rule 1 (lowercase,
   underscores only); `docs/tutorials/README.md` is empty.
8. `MCP_HOST` and `MCP_PORT` are set in Docker but never read; host and port are
   hard-coded.
9. The `Dockerfile` installs a prebuilt wheel, so the image will not contain
   `httpx2` and `fastmcp` 4 unless the wheel is rebuilt after Phase 1.
10. `main.py` only supports HTTP transport, and running the MCP server in Docker
    from VS Code is unreliable. The workshop needs a path that works every time
    (see Phase 3 and Decisions).

## Decisions

| Topic               | Decision                                                                                                                       |
| ------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| `openapi_server.py` | Delete the module and every reference to it                                                                                    |
| `temp/`             | Git-ignored; the user deletes it locally; no repo change                                                                       |
| Auth token          | The shared client factory sends `Authorization: Bearer` on every request when a token is set                                   |
| Workshop EPR        | Attendees run EPR themselves with docker compose                                                                               |
| Workshop MCP server | Never in Docker; runs on the host over stdio from a local venv (see Phase 3)                                                   |
| Demo "script"       | Both a presenter walkthrough document and a runnable shell script                                                              |
| Deleted docs        | Recreate four with lowercase names per AGENTS.md Rule 1 (Phase 5); `docker_reference.md` and `troubleshooting.md` stay deleted |
| Delivery            | One PR for all phases                                                                                                          |
| Workshop launch     | Plain `uv run` launches the stdio server from VS Code and Claude Desktop; no other launcher is documented                      |
| Supported OS        | macOS and Linux only; Windows is out of scope (no Windows quoting, testing, or docs)                                           |
| Version             | The PR does not bump the version; after merge, tag and bump to 2.0.0 (breaking change)                                         |

## Implementation Phases

### Phase 0: Research and Baseline

#### 0.1 Foundation Work

- Create branch work from `pr-xbcsmith-fastmcp2`; record baseline results of
  `ruff check src/`, `pytest --cov=src`, and server start in a fresh venv.
- Read the full FastMCP 3-to-4 upgrade guide and the httpx2 migration page end
  to end; list any change not in the Overview table.

#### 0.2 Add Foundation Functionality

Resolve these by reading FastMCP 4 docs or source, recording answers in the
implementation doc:

| Question                                                                                | Affects                      |
| --------------------------------------------------------------------------------------- | ---------------------------- |
| Minimum Python and Starlette versions for FastMCP 4                                     | `pyproject.toml`, Dockerfile |
| `FastMCP(...)` constructor: is `version=` keyword the supported form                    | `server.py`                  |
| `ctx.debug`, `ctx.info`, `ctx.error` still present and awaitable                        | `server.py`                  |
| `custom_route` still supported and its signature                                        | `server.py`                  |
| `run_async(transport="http", host=, port=)` still valid                                 | `server.py`                  |
| Replacement for `FastMCPOpenAPI` / `RouteMap` / `MCPType` at `providers.openapi`        | `openapi_server.py`          |
| In-memory test client API (`fastmcp.Client` with a server instance) and `mode=` options | tests, tutorials             |
| Whether `Client` string/stdio inference warnings affect any code or demo                | demos, tutorials             |
| Exact `httpx2` API for `MockTransport`, `AsyncClient`, `Client`                         | tests, demos                 |

#### 0.3 Integrate Foundation Work

Add a "Migration Findings" section to the implementation doc (Phase 6) so later
phases cite verified facts, not assumptions.

#### 0.4 Testing Requirements

Baseline suite must be green on the pre-migration code, or pre-existing failures
are listed explicitly.

#### 0.5 Deliverables

- [x] Baseline lint, test, coverage numbers recorded (2 ruff errors, 126 tests
      pass, 40% coverage)
- [x] Open-question table above fully answered (see the implementation doc,
      Phase 0 findings)
- [x] Target versions chosen (`fastmcp` >= 4.0 < 5, `httpx2` >= 2.13,
      `pydantic` >= 2.12, `starlette` >= 1.0, Python >= 3.12)

#### 0.6 Success Criteria

Every row in the question table has a sourced answer; target versions are
decided and written down.

### Phase 1: Dependency and httpx2 Migration

#### 1.1 Foundation Work

- Fix the 2 baseline `ruff check src/` errors (import ordering in `server.py`).
- Edit [pyproject.toml](../../pyproject.toml): replace `httpx` with `httpx2`,
  set lower bounds for `fastmcp` (>= 4), `pydantic` (>= 2.12), and `starlette`
  per Phase 0; adjust `requires-python` and classifiers if FastMCP 4 requires.
- Update `[tool.tox]` deps and `extras` so test envs install the same set (note
  `extras = testing` does not match the `test` extra name; fix).

#### 1.2 Add Foundation Functionality

- In [server.py](../../src/epr_mcp/server.py): swap `import httpx` for
  `import httpx2`; update the 9 `AsyncClient` call sites and the three exception
  checks in `handle_http_errors`.
- Search tests and docs for logger names `httpx` and `httpcore` and rename to
  `httpx2` and `httpcore2`.

#### 1.3 Integrate Foundation Work

- Extract one shared client factory in [common.py](../../src/epr_mcp/common.py)
  (timeout, headers, `Authorization` bearer from `cfg.token` when set) to
  replace the 9 repeated `AsyncClient()` constructions in `server.py`;
  `server.py` currently never sends the token, so this is a behavior change to
  call out in the migration notes. `openapi_server.py` was deleted in Phase 1
  (it imports the removed `fastmcp.server.openapi` and legacy `httpx`, so it
  blocked the Phase 1 success criteria).
- Check for external services reached through the OS trust store change (httpx2
  uses `truststore`); document `SSL_CERT_FILE` / `SSL_CERT_DIR` fallbacks in
  tutorial module 07 (misc and troubleshooting).

#### 1.4 Testing Requirements

- Add `tests/unit/test_http_errors.py` covering `handle_http_errors` for
  `ConnectError`, `TimeoutException`, `HTTPStatusError`, and generic errors,
  using `httpx2` exception types.
- Add a unit test asserting no `import httpx` remains in `src/`.

#### 1.5 Deliverables

- [x] `pyproject.toml` and tox config updated
- [x] All `src/` HTTP code on `httpx2`
- [x] Shared client factory with tests
- [x] `ruff check src/` and `pytest` pass

#### 1.6 Success Criteria

`grep -rn "import httpx$" src/ tests/` returns nothing; `pip install -e .` in a
clean venv pulls `httpx2` and no direct `httpx` dependency of this project.

### Phase 2: FastMCP 4 API Migration

#### 2.1 Feature Work

- Fix the `FastMCP(...)` construction in `server.py` to keyword arguments
  (`name`, `version`, optional `instructions`), per Phase 0 findings.
- Re-verify each `@mcp.tool(title=, description=)` registration and the
  `Annotated[str, Field(...)]` parameter style still produce correct tool
  schemas; fix any decorator argument changes.
- Replace `ctx.debug` and `ctx.error` calls in all 9 tools and
  `handle_http_errors` with module `logger` calls: FastMCP 4 deprecates the
  client logging capability (SEP-2577) and warns on every call (Phase 0 finding
  2). `handle_http_errors` no longer needs the `ctx` argument.
- Re-verify `custom_route` handlers for `/health`, `/openapi.yaml`,
  `/openapi.json`, `/docs`.
- Remove any use of `ctx.sample`, `ctx.sample_step`, `ctx.list_roots`,
  `sampling_handler`, `ctx.elicit` (none found in the current scan; re-confirm
  with grep).

#### 2.2 Integrate Feature

- `openapi_server.py` is already deleted (Phase 1); remove every remaining
  reference: imports, `docs/openapi_implementation.md` (rewrite to describe only
  the `/openapi.yaml`, `/openapi.json`, and `/docs` routes that remain in
  `server.py`), the demos, and `tests/test_smoke.py` if referenced. Keep
  `openapi.yaml`, which `server.py` serves.
- Add a `--transport` option to `main.py start` with values `stdio` and `http`
  (default `http` to keep Docker behavior). The stdio path calls the framework's
  stdio run method; logging already goes to stderr, and no code path may print
  to stdout in stdio mode.
- Replace `asyncio.run(mcp.run_async(...))` with the FastMCP 4 recommended entry
  point (`mcp.run(...)` if supported) so event-loop handling is the framework's
  job.
- Read `MCP_HOST` and `MCP_PORT` from the environment in `main.py` and pass them
  via `config.Config` ([config.py](../../src/epr_mcp/config.py)) instead of
  hard-coded `0.0.0.0:8000`.
- Stop logging `cfg.token` in `server.py`.

#### 2.3 Configuration Updates

- Add `openapi.yaml` as package data so the built wheel serves `/openapi.yaml`
  and `/openapi.json` (the current wheel omits it); review the legacy build
  backend and `py2.py3` wheel tag at the same time.
- Do not change the version in this PR (the 2.0.0 bump happens after merge, see
  Phase 5). Rebuild the wheel (`make wheel`), then fix the hard-coded wheel
  filename `epr_mcp-0.1.0-...` in the [Dockerfile](../../Dockerfile) (use a glob
  or build arg) so the later version bump does not break the image build.
- Confirm the Docker base image Python version satisfies FastMCP 4; if not,
  change the base image.
- Update [docker-compose.yaml](../../docker-compose.yaml) env if new variables
  are added; keep `.yaml` extension per Rule 1.

#### 2.4 Testing Requirements

- Add `tests/unit/test_server_tools.py`: build the server through `run`-style
  factory (split `run(cfg)` into `create_server(cfg)` plus `run(cfg)` so tests
  need no network bind), connect with the FastMCP 4 in-memory client, assert the
  9 tool names and input schemas.
- For each tool, test success, 404/non-200, `ConnectError`, timeout, and
  response-validation failure using `httpx2.MockTransport` (or the Phase 0
  equivalent).
- Test the 4 custom routes with Starlette `TestClient`.
- Add one functional test in `tests/functional/` that starts the server in HTTP
  mode and calls `/health` and `tools/list` (skipped unless an env flag is set).

#### 2.5 Deliverables

- [x] `create_server` / `run` split with tests
- [x] `openapi_server.py` deleted with all references removed
- [x] `--transport stdio|http` option with tests
- [x] Host and port configurable
- [x] Dockerfile builds and container passes `/health` healthcheck
- [x] Coverage >= 80% over `src/`

#### 2.6 Success Criteria

`pytest --cov=src --cov-fail-under=80` passes; `docker compose up` shows a
healthy `epr-mcp-server`; MCP Inspector lists all 9 tools and a `fetch_event`
call returns data from a running EPR.

### Phase 3: Tutorial Rewrite for Workshop Delivery

#### 3.1 Feature Work

Rework [docs/tutorials/](../tutorials/) as one linear path where every module
ends with a runnable checkpoint. Rename files to lowercase underscores
(`00_intro.md`, `01_first_tool.md`, ...) and fix inbound links.

| Module | Title                    | Content                                                                         | Time   |
| ------ | ------------------------ | ------------------------------------------------------------------------------- | ------ |
| 00     | Intro and prerequisites  | What MCP and EPR are; Python, uv, Docker, Node (Inspector) check; seed EPR      | 15 min |
| 01     | First tool               | `fastmcp` 4 + `httpx2`; one `fetch_event` tool; `mcp.run()`                     | 20 min |
| 02     | Inspector                | Connect, list tools, call `fetch_event` (replaces current 02)                   | 15 min |
| 03     | Complete the tool set    | Receivers, groups, search, create; `Annotated`/`Field` schemas                  | 30 min |
| 04     | Validation and errors    | Pydantic schemas, `handle_http_errors`, `httpx2` exceptions                     | 20 min |
| 05     | Test it                  | In-memory client plus `httpx2.MockTransport` tests                              | 20 min |
| 06     | Use it from an editor    | stdio config for VS Code and Claude Desktop; HTTP and Docker as optional extras | 20 min |
| 07     | Misc and troubleshooting | uv tips, FastMCP 4 migration notes (legacy vs modern mode)                      | 10 min |

#### 3.2 Integrate Feature

- Add a `docs/tutorials/code/` tree with one checkpoint directory per module
  (starter and solution) so attendees can resync; CI-check that every solution
  imports and passes its tests.
- Write `docs/tutorials/README.md` (currently empty): audience, prerequisites,
  agenda table above, facilitator notes, and a "stuck? jump to checkpoint N"
  table.
- Fold useful content from the local, git-ignored `temp/notes.md` (seed curl
  commands) into module 00 as a seed script before the user deletes `temp/`.
- Replace every `mcp.server.fastmcp` import and `pip install mcp[cli] mcp httpx`
  with `fastmcp` 4 and `httpx2`; replace the "FastMCP 2.0" link with the FastMCP
  4 docs.

#### 3.3 Configuration Updates

- Reliability design: only EPR (and its database) runs in Docker, via a workshop
  `docs/tutorials/code/docker-compose.yaml`. The MCP server always runs on the
  host from a uv-managed venv over stdio, so VS Code launches a local process
  and no container networking or Docker-exec stdio is involved.
- Ship `.vscode/mcp.json` in the tutorial code that launches the server with
  `uv run` (command, args, and `EPR_URL` env), plus the equivalent Claude
  Desktop config.
- Add a `make workshop-check` (or `docs/tutorials/code/check_setup.py`)
  preflight that verifies: Python and uv versions, EPR reachable at `EPR_URL`,
  `eprmcp version` runs, and an in-process MCP client can list the 9 tools.
  Attendees run it before the session and after any failure.
- Provide editor-independent fallbacks in the same modules so no one is blocked
  by VS Code: MCP Inspector (module 02) and a small FastMCP client script
  (`check_setup.py` or the Phase 4 client demo) that exercises the tools from a
  terminal.
- Pin tutorial dependency versions in a `requirements.txt` or `pyproject.toml`
  inside `docs/tutorials/code/`; facilitators pre-build a wheel cache or provide
  an offline install note for poor venue networks.

#### 3.4 Testing Requirements

- Run every tutorial command and code block on a clean machine or container
  (macOS and Linux); log deviations as doc fixes.
- Run `markdownlint --fix --config .markdownlint.json` and
  `prettier --write --parser markdown --prose-wrap always` on every changed file
  (AGENTS.md Rule 2).
- Dry run the full agenda with someone who has not seen the project; record
  timings and adjust the table.

#### 3.5 Deliverables

- [ ] Eight renamed, rewritten tutorial modules
- [ ] `docs/tutorials/README.md` with agenda and facilitator notes
- [ ] Checkpoint code directories with CI check
- [ ] One-command EPR environment and a host-run stdio MCP server
- [ ] `.vscode/mcp.json` and Claude Desktop config tested on macOS and Linux
- [ ] Preflight check script with Inspector and terminal-client fallbacks
- [ ] No references to `mcp.server.fastmcp`, `httpx` imports, or FastMCP 2.0

#### 3.6 Success Criteria

A new attendee completes modules 00 to 06 in the time budget starting from a
fresh clone, and the end state matches the shipped server's tool list.

### Phase 4: Demos With Scripts

#### 4.1 Feature Work

- Port [generate_epr_events.py](../../demos/generate_epr_events.py) to `httpx2`
  (the `httpx.Client` and `HTTPStatusError` use at lines 252 to 256 and type
  hints at 266 and 280).
- Rewrite [openapi_demo.py](../../demos/openapi_demo.py): remove the bad
  `sys.path` insert, unused imports, and any `openapi_server` references; it
  demonstrates only the `/openapi.yaml`, `/openapi.json`, and `/docs` endpoints
  of the HTTP server and lists tools via the FastMCP 4 client, rather than
  printing a hard-coded list.
- Add `demos/mcp_client_demo.py`: connect with the FastMCP 4 client, list tools,
  create a receiver, create an event, fetch it, search for it.

#### 4.2 Integrate Feature

For each demo add a presenter script in `demos/scripts/` (lowercase
underscores): `generate_events_script.md`, `openapi_demo_script.md`,
`mcp_client_demo_script.md`. Each has: goal, prerequisites, exact commands in
order, expected output, talking points per step, failure recovery. Add a
`demos/scripts/run_all.sh` that runs the full sequence unattended for rehearsal.
Both the presenter documents and the shell script are required.

#### 4.3 Configuration Updates

- Fix [requirements.txt](../../demos/requirements.txt): `httpx2`, `fastmcp`, and
  the correct ULID package (verify which provides `ulid.ulid()`); update
  [demos/README.md](../../demos/README.md) (remove `pip install httpx ulid-py`,
  document the scripts, add a demo table row each).

#### 4.4 Testing Requirements

- Run each demo against the Phase 3 EPR compose stack and compare to the
  expected output in its script.
- Add a `--dry-run` smoke test for `generate_epr_events.py` in `tests/`.
- `ruff check demos/` passes (extend lint targets in Makefile and tox).

#### 4.5 Deliverables

- [ ] Three demos working on FastMCP 4 and `httpx2`
- [ ] Three presenter scripts plus `run_all.sh`
- [ ] Updated `demos/README.md` and `requirements.txt`

#### 4.6 Success Criteria

`demos/scripts/run_all.sh` exits 0 against the compose stack; a presenter can
run a demo using only its script.

### Phase 5: Documentation, Infrastructure, and Release

#### 5.1 Feature Work

- Recreate four of the docs deleted from the working tree under AGENTS.md Rule 1
  names (lowercase, underscores; only `README.md` may be uppercase):
  `docs/docker_compose.md`, `docs/openapi_implementation.md`,
  `docs/schema_validation.md`, and `docs/README.md`. Take the starting content
  from `git show HEAD:docs/<OLD_NAME>`. `docs/docker_reference.md` and
  `docs/troubleshooting.md` stay deleted (decision); remove their rows from the
  `docs/README.md` index. Do not recreate the all-caps names.
- Update the recreated docs and the root [README.md](../../README.md) for
  FastMCP 4, `httpx2`, the `--transport` option, token handling, and the removal
  of `openapi_server`; `openapi_implementation.md` covers only the routes that
  remain in `server.py`.
- Run markdownlint and prettier on each recreated file (Rule 8).
- Write `docs/explanation/fastmcp4_httpx2_migration_implementation.md`
  (AGENTS.md Rule 3: Overview, Components, Implementation Details, Testing,
  Examples) including the Phase 0 findings.

#### 5.2 Integrate Feature

- Add a short "Upgrading to 2.0" section to the root README for users of the
  package, listing breaking changes: FastMCP 4, `httpx2`, token now sent on all
  requests, `openapi_server` removed, new `--transport` option, search and
  create tools take flat arguments (the old wrapped shape is rejected).
- Update the Makefile `lint` target and tox `check`/`format` to include
  `demos/`; confirm `make tests`, `make wheel`, `make docker-image` work.

#### 5.3 Configuration Updates

- Do not bump the version in this PR. Update `.env.example` for new variables
  (`MCP_HOST`, `MCP_PORT`).
- Post-merge release steps (outside the PR, by the maintainer): bump the version
  to 2.0.0 in `pyproject.toml` and `constants.py`, rebuild the wheel, tag
  `v2.0.0`, build the Docker image, and publish.

#### 5.4 Testing Requirements

Full gate from AGENTS.md Rule 2: `ruff check src/`, `ruff format src/`,
`pytest --cov=src --cov-report=html --cov-fail-under=80 --cov-report=term-missing`,
and markdownlint plus prettier on every changed `.md` file.

#### 5.5 Deliverables

- [ ] All docs reference FastMCP 4 and `httpx2`
- [ ] Implementation doc written
- [ ] Post-merge release checklist (2.0.0 bump, wheel, tag, image) written in
      the implementation doc

#### 5.6 Success Criteria

All quality gates green; no stale `httpx` or FastMCP 2 references outside the
migration notes (`grep` clean).

## Recommended Order

Phase 0, then 1, 2, 3, 4, 5, all in a single PR with one commit per phase so
review stays tractable. Phases 3 and 4 depend on Phase 2; Phase 4 reuses the
Phase 3 EPR compose environment.

## Open Questions

None.
