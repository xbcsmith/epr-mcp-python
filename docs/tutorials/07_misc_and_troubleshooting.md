# 07 Misc and Troubleshooting

Time: 10 minutes. Reference material; skim it now and come back when needed.

## uv cheat sheet

```bash
uv sync                                  # create or update the environment
uv run python script.py                  # run in the project environment
uv run --directory /path python x.py     # run against another project folder
uv run pytest work                       # run tests
uv add some-package                      # add a dependency to pyproject.toml
uv --version
```

A private package index or mirror: set `UV_INDEX_URL`.

## FastMCP 4 notes

This workshop uses FastMCP 4. If you have FastMCP 2 or 3 code, these are the
changes that matter here:

| Topic                 | Change                                                                                                                     |
| --------------------- | -------------------------------------------------------------------------------------------------------------------------- |
| HTTP client           | FastMCP uses `httpx2`. Replace `import httpx` with `import httpx2`                                                         |
| Server constructor    | Pass `name=` and `version=` by keyword; the second positional is `instructions`                                            |
| Logging to the client | `ctx.debug()` and `ctx.error()` still exist but now warn that the capability is deprecated. Use Python `logging` to stderr |
| OpenAPI integration   | Moved from `fastmcp.server.openapi` to `fastmcp.server.providers.openapi`                                                  |
| Removed               | `ctx.sample()`, `ctx.sample_step()`, `ctx.list_roots()`, and the `sampling_handler` argument                               |
| Protocol modes        | The client negotiates the modern protocol by default. `Client(..., mode="legacy")` forces the older handshake protocol     |
| Local server clients  | `Client("server.py")` as a plain string warns. Pass a `Path`, or use `StdioTransport` as `client.py` does                  |

The upgrade guide is at
<https://gofastmcp.com/getting-started/upgrading/from-fastmcp-3> and the release
notes at <https://gofastmcp.com/getting-started/whats-new>.

## httpx2 notes

httpx2 has the same API as httpx 0.28; only names changed.

- Install `httpx2` and import `httpx2`. The two packages can be installed side
  by side, but their classes are different: an `httpx.HTTPError` is not an
  `httpx2.HTTPError`.
- The default User-Agent is `python-httpx2/<version>`.
- TLS verification uses the operating system trust store. If a corporate proxy
  or private CA breaks it, point `SSL_CERT_FILE` or `SSL_CERT_DIR` at your
  certificate bundle; both are still honored.
- Loggers are named `httpx2` and `httpcore2`. To see requests, set
  `logging.getLogger("httpx2").setLevel(logging.DEBUG)`.

## Troubleshooting

| Symptom                                        | Fix                                                                                |
| ---------------------------------------------- | ---------------------------------------------------------------------------------- |
| `check_setup.py` says EPR is not reachable     | `docker compose ps` in `docs/tutorials/code`; then `docker compose up -d`          |
| `epr-server` keeps restarting                  | `docker compose logs epr-server`; see "EPR server" below                           |
| `seed_epr.py` says it cannot reach EPR         | EPR is still starting. Wait for the readiness curl in module 00 to print 200       |
| `Cannot reach EPR` from a tool                 | `EPR_URL` is wrong or EPR is down. The workshop default is `http://localhost:8042` |
| Tool call fails with a validation error        | You are on the module 04 server. Read the message; it names the field              |
| `ModuleNotFoundError: httpx2`                  | You ran `python` outside uv. Use `uv run python ...`                               |
| `ModuleNotFoundError: No module named 'httpx'` | Code still imports `httpx`. Change it to `httpx2`                                  |
| Garbled or missing MCP responses               | Something printed to stdout. Use `logger`, not `print`                             |
| Port 8042 already in use                       | Stop the other EPR, or change the port mapping in `docker-compose.yaml`            |

### EPR server

EPR needs Postgres and Redpanda healthy before it starts, so the first start
takes a minute. If it still restarts:

```bash
docker compose ps
docker compose logs epr-server
docker compose logs redpanda
```

To start over with empty data:

```bash
docker compose down -v
docker compose up -d
uv run python seed_epr.py
```

## Offline and slow networks

Prepare while online:

```bash
uv sync
docker compose build
docker save epr-server:workshop | gzip > epr-server.tar.gz
docker pull postgres:16
docker pull docker.redpanda.com/redpandadata/redpanda:v23.2.8
```

On another machine, `docker load < epr-server.tar.gz`, then
`docker compose up -d` skips the build because the image already exists.

## Where to go next

- The shipped server that this workshop mirrors: `src/epr_mcp/` in this
  repository.
- The demos in `demos/`.
- FastMCP documentation: <https://gofastmcp.com>.
- The MCP specification: <https://modelcontextprotocol.io>.
