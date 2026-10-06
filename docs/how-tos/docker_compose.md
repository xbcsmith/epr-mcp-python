# Running the Server with Docker

The repository ships a Dockerfile and a `docker-compose.yaml`. Use them to run
the server as a long-lived HTTP service. Do not use a container for an MCP
server that an editor starts over stdio: use `uv run` (see
[workshop module 06](../tutorials/06_use_from_an_editor.md)).

## Requirements

- Docker with Compose v2 (`docker compose`)
- Python 3.12 or newer and `build` to make the wheel (`make wheel` installs it)
- A running EPR the container can reach

## Build

The image installs a prebuilt wheel from `dist/`, so build the wheel first.
`make docker-image` does both steps; `make wheel` cleans `build/` and `dist/`
first so a stale file cannot end up in the image.

```bash
make docker-image          # wheel, then docker build -t epr-mcp-python:latest .
```

The Dockerfile installs `dist/epr_mcp-*-py3-none-any.whl`, so the file name does
not change when the version does. `.dockerignore` keeps `.git`, `.venv`,
`tests`, `docs`, and `demos` out of the build context.

## Run with docker run

```bash
docker run -d --name epr-mcp-server -p 8000:8000 \
  -e EPR_URL=http://host.docker.internal:8042 \
  -e EPR_TOKEN=your-token \
  epr-mcp-python:latest

curl http://localhost:8000/health        # OK
docker logs -f epr-mcp-server
docker stop epr-mcp-server && docker rm epr-mcp-server
```

The container runs `python3 -m epr_mcp.main start`, the `http` transport, bound
to `0.0.0.0:8000`. The MCP endpoint is `http://localhost:8000/mcp`.

## Run with Compose

```bash
cp .env.example .env       # then edit EPR_URL and EPR_TOKEN
make wheel
docker compose up -d --build
docker compose ps          # the server shows (healthy) after a few seconds
docker compose logs -f epr-mcp-server
docker compose down
```

Compose reads `.env` for `EPR_URL`, `EPR_TOKEN`, and `EPR_DEBUG`. With no
`EPR_TOKEN` the server sends no `Authorization` header.

## Configuration

| Variable    | Default in Compose                 | Meaning                                                                  |
| ----------- | ---------------------------------- | ------------------------------------------------------------------------ |
| `EPR_URL`   | `http://host.docker.internal:8042` | EPR base URL, reachable from inside the container                        |
| `EPR_TOKEN` | empty                              | Bearer token sent on every EPR request                                   |
| `EPR_DEBUG` | `false`                            | Debug logging                                                            |
| `MCP_HOST`  | `0.0.0.0`                          | Bind address (fixed in the file)                                         |
| `MCP_PORT`  | `8000`                             | Bind port (fixed in the file; the port mapping and healthcheck use 8000) |

`EPR_URL` must be an address the container can reach, not `localhost`:

| EPR runs                   | Use                                            |
| -------------------------- | ---------------------------------------------- |
| On your machine            | `http://host.docker.internal:8042`             |
| In another Compose project | Join its network, then `http://<service>:8042` |
| On another host            | `http://that-host:8042`                        |

On Linux, `host.docker.internal` needs
`--add-host host.docker.internal:host-gateway` with `docker run`, or
`extra_hosts` in Compose.

## Health check

Compose and the Dockerfile both poll `curl -f http://localhost:8000/health`. To
see the state:

```bash
docker inspect --format '{{.State.Health.Status}}' epr-mcp-server
```

## Optional services (profiles)

Services under a profile do not start unless you ask for them.

| Profile      | Services                | Start with                                  |
| ------------ | ----------------------- | ------------------------------------------- |
| `production` | `nginx`                 | `docker compose --profile production up -d` |
| `monitoring` | `prometheus`, `grafana` | `docker compose --profile monitoring up -d` |

- `nginx` proxies ports 80 and 443 to the server using `nginx.conf`. It mounts
  `./ssl`, which does not exist in the repository; the HTTPS block in the file
  is commented out.
- `prometheus` scrapes `epr-mcp-server:8000/metrics`, but the server does not
  expose `/metrics`, so the target shows as down. `grafana` mounts
  `./grafana/provisioning`, which is not in the repository either. Treat the
  monitoring profile as scaffolding until the server exports metrics.

## Running EPR next to it

To try everything locally, start EPR with the workshop file and point the server
at it:

```bash
(cd docs/tutorials/code && docker compose up -d --build)
EPR_URL=http://host.docker.internal:8042 docker compose up -d --build
```

## Troubleshooting

| Symptom                                      | Fix                                                                               |
| -------------------------------------------- | --------------------------------------------------------------------------------- |
| `docker build` fails: no wheel found         | Run `make wheel` first (or use `make docker-image`)                               |
| `Connection failed to EPR server`            | `EPR_URL` is wrong for the container; see the table above                         |
| Health check stays `starting` or `unhealthy` | `docker compose logs epr-mcp-server`; the container needs a minute on first start |
| `/openapi.yaml` returns 404                  | The image was built from a wheel made before 2.0; rebuild with `make wheel`       |
| Port 8000 already in use                     | Stop the other process, or change the left side of `8000:8000`                    |
| EPR answers 401 or 403                       | Set `EPR_TOKEN`                                                                   |
