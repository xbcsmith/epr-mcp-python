# epr-mcp-python

An MCP (Model Context Protocol) server for the
[Event Provenance Registry](https://github.com/xbcsmith/event-provenance-registry)
(EPR). It gives an AI assistant tools to fetch, search, and create EPR events,
event receivers, and event receiver groups. Built on FastMCP 4 and httpx2.

New here? Build the server step by step in the
[workshop](./docs/tutorials/README.md), or watch it work with the
[demos](./demos/README.md).

## Requirements

- Python 3.12 or newer
- A running EPR (the
  [workshop compose file](./docs/tutorials/code/docker-compose.yaml) starts one)
- [uv](https://docs.astral.sh/uv/) is recommended; pip works too

## Install and run

```bash
git clone https://github.com/xbcsmith/epr-mcp-python.git
cd epr-mcp-python
uv run eprmcp start --url http://localhost:8042
```

`uv run` creates the environment on first use. Without uv:

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e .
eprmcp start --url http://localhost:8042
```

The server speaks MCP over one of two transports:

| Transport | Use it for                                                        | Command                          |
| --------- | ----------------------------------------------------------------- | -------------------------------- |
| `http`    | A long-running server; Docker; remote clients                     | `eprmcp start` (the default)     |
| `stdio`   | An editor that starts the server itself (VS Code, Claude Desktop) | `eprmcp start --transport stdio` |

With `http` the MCP endpoint is `http://127.0.0.1:8000/mcp`. With `stdio` the
server must not write anything but protocol messages to stdout; it logs to
stderr.

### Options and environment

Every option has an environment variable; the command line wins.

| Option        | Environment                  | Default                 | Meaning                                                  |
| ------------- | ---------------------------- | ----------------------- | -------------------------------------------------------- |
| `--url`       | `EPR_URL`                    | `http://localhost:8042` | EPR base URL                                             |
| `--token`     | `EPR_API_TOKEN`, `EPR_TOKEN` | none                    | Sent as `Authorization: Bearer` on every EPR request     |
| `--transport` | `MCP_TRANSPORT`              | `http`                  | `http` or `stdio`                                        |
| `--host`      | `MCP_HOST`                   | `0.0.0.0`               | Bind address for `http`                                  |
| `--port`      | `MCP_PORT`                   | `8000`                  | Bind port for `http`                                     |
| `--debug`     | `EPR_DEBUG`                  | off                     | Debug logging and a debugger on errors (not for `stdio`) |

`eprmcp version` prints the version.

## Tools

The server registers nine tools. Arguments are passed flat; there is no extra
`data` wrapper inside them.

| Tool               | Arguments                                                                                                                      |
| ------------------ | ------------------------------------------------------------------------------------------------------------------------------ |
| `fetch_event`      | `id`: 26 character ULID                                                                                                        |
| `fetch_receiver`   | `id`                                                                                                                           |
| `fetch_group`      | `id`                                                                                                                           |
| `search_events`    | `data`: any of `name`, `version`, `release`, `platform_id`, `package`, `description`, `success`, `event_receiver_id`           |
| `search_receivers` | `data`: any of `name`, `type`, `version`, `description`                                                                        |
| `search_groups`    | `data`: any of `name`, `type`, `version`, `description`                                                                        |
| `create_event`     | `event_data`: `name`, `version`, `release`, `platform_id`, `package`, `description`, `payload`, `success`, `event_receiver_id` |
| `create_receiver`  | `receiver_data`: `name`, `type`, `version`, `description`, `schema`                                                            |
| `create_group`     | `group_data`: `name`, `type`, `version`, `description`, `event_receiver_ids`                                                   |

Unknown fields are rejected, so a typo cannot silently turn a filtered search
into an unfiltered one. Create tools return the new record's ID. See
[schema_validation.md](./docs/reference/schema_validation.md) for the exact
rules.

### Calling the tools from Python

```python
import asyncio

from fastmcp import Client


async def main():
    async with Client("http://127.0.0.1:8000/mcp") as client:
        result = await client.call_tool("search_events", {"data": {"name": "checkout-service"}})
        print(result.content[0].text)


asyncio.run(main())
```

## HTTP endpoints

With the `http` transport the server also serves:

| Endpoint                             | Purpose                                                                                               |
| ------------------------------------ | ----------------------------------------------------------------------------------------------------- |
| `GET /health`                        | Health check (plain text `OK`)                                                                        |
| `GET /openapi.yaml`, `/openapi.json` | The OpenAPI description (see [openapi_implementation.md](./docs/reference/openapi_implementation.md)) |
| `GET /docs`                          | Swagger UI for that description                                                                       |
| `/mcp`                               | The MCP endpoint                                                                                      |

## Use it from an editor

Both editors start the server themselves over stdio. VS Code, in
`.vscode/mcp.json`:

```json
{
  "servers": {
    "epr-mcp": {
      "type": "stdio",
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/path/to/epr-mcp-python",
        "eprmcp",
        "start",
        "--transport",
        "stdio"
      ],
      "env": { "EPR_URL": "http://localhost:8042" }
    }
  }
}
```

Claude Desktop needs the full path to `uv` (it does not inherit your shell
PATH). A working pair of configurations and a troubleshooting table are in
[module 06 of the workshop](./docs/tutorials/06_use_from_an_editor.md). Running
the server inside a container that an editor launches is unreliable; use
`uv run`.

To explore the server in a browser, use the MCP Inspector (see
[module 02](./docs/tutorials/02_inspector.md)).

## Docker

The image installs the built wheel, so build the wheel first:

```bash
make docker-image                 # builds the wheel, then the image
docker run -p 8000:8000 \
  -e EPR_URL=http://host.docker.internal:8042 \
  -e EPR_TOKEN=your-token \
  epr-mcp-python:latest
```

Or with Compose, which reads `.env` (copy `.env.example`):

```bash
make wheel
docker compose up -d --build
curl http://localhost:8000/health
```

Inside a container `EPR_URL` must be an address the container can reach, such as
`http://host.docker.internal:8042` for an EPR on the host. See
[docker_compose.md](./docs/how-tos/docker_compose.md).

## Development

```bash
uv sync --extra lint --extra test     # or: pip install -e '.[lint,test,build]'
make lint                             # ruff format and check: src, tests, demos
uv run pytest --cov=src --cov-fail-under=80
```

| Make target      | Does                                                    |
| ---------------- | ------------------------------------------------------- |
| `install`        | Installs into a virtualenv                              |
| `lint`           | Runs ruff on `src/epr_mcp`, `tests`, and `demos`        |
| `tests`          | Runs the tests with tox                                 |
| `wheel`          | Cleans, then builds the sdist and wheel into `dist/`    |
| `docker-image`   | Builds the wheel, then the Docker image                 |
| `workshop-check` | Preflight for the workshop (needs uv and a running EPR) |
| `release`        | Runs the tox release environment                        |
| `clean`          | Removes build output and caches                         |

Functional tests that start the real server are skipped unless
`EPR_MCP_FUNCTIONAL=1` is set.

## Upgrading to 2.0

Version 2.0 moves to FastMCP 4 and httpx2 and changes some behavior. If you run
the server, check these:

- **Dependencies.** `fastmcp>=4,<5` and `httpx2` replace `httpx`;
  `pydantic>=2.12` and `starlette>=1.0` are required. Anything that imported
  `httpx` from this package's environment must switch to `httpx2`. TLS
  verification now uses the operating system trust store; set `SSL_CERT_FILE` or
  `SSL_CERT_DIR` for a private CA.
- **Tool arguments are flat.** `search_events` takes `{"data": {"name": "x"}}`,
  not `{"data": {"data": {"name": "x"}}}`, and `create_event` takes
  `{"event_data": {...}}`. The old wrapped shape is rejected, and so are unknown
  fields.
- **Receivers need a schema.** `create_receiver` requires `schema`, which EPR
  itself requires.
- **Creates work against a real EPR.** The create tools used to report failure
  because EPR answers 200 (not 201) and returns only the new ID. They now accept
  both and return `{"message": ..., "id": ...}`.
- **The token is sent.** `EPR_TOKEN` (and `EPR_API_TOKEN`) is now sent as a
  bearer token on every EPR request. Before, it was read but never sent.
- **`openapi_server` is removed.** It was not reachable from the command line.
  The `/openapi.yaml`, `/openapi.json`, and `/docs` routes stay.
- **New options.** `--transport stdio|http`, `--host`, and `--port`, with
  `MCP_TRANSPORT`, `MCP_HOST`, and `MCP_PORT`.
- **Logging.** Tool diagnostics go to the server log (stderr). They are no
  longer sent to MCP clients as log notifications, which FastMCP 4 deprecates.
- **Packaging.** The wheel is `py3-none-any` and now includes `openapi.yaml`.

## Troubleshooting

- `Connection failed to EPR server`: EPR is down or `EPR_URL` is wrong. Inside
  Docker use `http://host.docker.internal:8042` for an EPR on the host.
- Check EPR: `curl http://localhost:8042/healthz/readiness` prints `200` when
  ready.
- Check this server: `curl http://localhost:8000/health` prints `OK`.
- Compose logs: `docker compose logs -f epr-mcp-server`.
- Setting up the workshop or demos:
  [workshop troubleshooting](./docs/tutorials/07_misc_and_troubleshooting.md).

## Documentation

- [Workshop](./docs/tutorials/README.md): build the server step by step
- [Demos](./demos/README.md): runnable demonstrations with presenter scripts
- [Docker Compose](./docs/how-tos/docker_compose.md)
- [OpenAPI endpoints](./docs/reference/openapi_implementation.md)
- [Schema validation](./docs/reference/schema_validation.md)
- [Migration notes and implementation plan](./docs/explanation/fastmcp4_httpx2_migration_implementation.md)

## License

Apache 2.0. See [LICENSE](./LICENSE).
