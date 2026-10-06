# EPR MCP Server Demos

Three demonstrations of the EPR (Event Provenance Registry) MCP server, each
with a presenter script, plus a script that runs them all in order. They use
FastMCP 4 and httpx2.

## The demos

| Demo                                               | What it shows                                                                       | Needs EPR                 | Presenter script                                                 |
| -------------------------------------------------- | ----------------------------------------------------------------------------------- | ------------------------- | ---------------------------------------------------------------- |
| [generate_epr_events.py](./generate_epr_events.py) | Generates 11 receivers and 44 CDEvents and posts them, prints curl, or writes files | Yes (not for `--dry-run`) | [generate_events_script.md](./scripts/generate_events_script.md) |
| [openapi_demo.py](./openapi_demo.py)               | The server's HTTP endpoints, the OpenAPI documents, Swagger UI, and the tool list   | No                        | [openapi_demo_script.md](./scripts/openapi_demo_script.md)       |
| [mcp_client_demo.py](./mcp_client_demo.py)         | A FastMCP client creates, fetches, and searches records through the MCP tools       | Yes                       | [mcp_client_demo_script.md](./scripts/mcp_client_demo_script.md) |

Run them in that order. The presenter scripts say what to type, what you will
see, and what to say at each step. [scripts/run_all.sh](./scripts/run_all.sh)
runs all three unattended, which is how to rehearse.

## Quick start

You need [uv](https://docs.astral.sh/uv/), Docker, and curl. From the repository
root, start EPR with the workshop compose file (the first build takes about
three minutes):

```bash
cd docs/tutorials/code && docker compose up -d --build && cd ../../..
```

Wait until this prints `200`:

```bash
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8042/healthz/readiness
```

Then run everything:

```bash
demos/scripts/run_all.sh
```

Or one demo at a time. Always run from the repository root with `uv run`, which
installs the dependencies the first time:

```bash
uv run python demos/generate_epr_events.py --dry-run
uv run python demos/generate_epr_events.py
uv run python demos/openapi_demo.py
uv run python demos/mcp_client_demo.py
```

Without uv, install the package and run the scripts with that Python:
`pip install -e .`. `generate_epr_events.py` alone needs only httpx2
(`pip install -r demos/requirements.txt`).

## Options

`generate_epr_events.py`

| Option            | Meaning                                                            |
| ----------------- | ------------------------------------------------------------------ |
| `--url`, `-u`     | EPR URL, default `http://localhost:8042`                           |
| `--dry-run`       | Print curl commands and send nothing                               |
| `--write-to-disk` | Write JSON files and curl commands to `epr_reports/`, post nothing |
| `--timeout`, `-t` | Request timeout in seconds, default 10                             |

It exits 0 if everything posted and 1 if any request failed. Set `EPR_DEBUG=1`
for debug logging and a debugger on errors.

`openapi_demo.py`

| Option      | Meaning                                                                   |
| ----------- | ------------------------------------------------------------------------- |
| `--url`     | Use a server that is already running, for example `http://localhost:8000` |
| `--epr-url` | EPR URL passed to the server it starts; never contacted                   |

`mcp_client_demo.py`

| Option               | Meaning                                                                                                            |
| -------------------- | ------------------------------------------------------------------------------------------------------------------ |
| `--epr-url`          | EPR URL, default `$EPR_URL` or `http://localhost:8042`                                                             |
| `--server-url`       | Connect to a server running over HTTP, for example `http://localhost:8000/mcp`, instead of starting one over stdio |
| `--show-server-logs` | Show the log output of the server started over stdio                                                               |

Both client demos exit 0 when every step works and 1 otherwise.

`scripts/run_all.sh` takes `--skip-generate` to leave EPR's data alone and reads
`EPR_URL`.

## What the demos change

The generator adds 11 receivers and 44 events on every run. The client demo adds
one receiver and one event on every run, with unique names. `openapi_demo.py`
changes nothing. To start clean:

```bash
cd docs/tutorials/code && docker compose down -v && docker compose up -d
```

## Troubleshooting

| Symptom                                              | Fix                                                               |
| ---------------------------------------------------- | ----------------------------------------------------------------- |
| `Connection refused` or `ERROR` on every line        | EPR is not running; run the quick start and the readiness check   |
| `ModuleNotFoundError: epr_mcp` or `fastmcp`          | Run from the repository root with `uv run`, or `pip install -e .` |
| `the server process exited before it became healthy` | Run `uv run eprmcp version` to see the real error                 |
| `Connection failed to EPR server`                    | `--epr-url` is wrong or EPR is down                               |
| The first run is slow                                | uv is installing packages; later runs start in seconds            |

## Adding a demo

1. Write the script in this directory with the SPDX header, a docstring that has
   a Usage section, and exit codes 0 for success and 1 for failure.
2. Add a presenter script in `scripts/` with the goal, prerequisites, exact
   commands, expected output, talking points, and failure recovery.
3. Add it to the table above and to `scripts/run_all.sh`.
4. Make sure `ruff check demos/` passes and add a smoke test under
   `tests/demos/`.

The server documentation is in [../docs/](../docs/), and the workshop that
builds the server step by step is in [../docs/tutorials/](../docs/tutorials/).
