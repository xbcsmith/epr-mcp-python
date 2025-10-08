# epr-mcp-python

## Overview

EPR MCP Python is a python MCP server for the Event Provenance Registry server.

## Development

### Local Development

```bash
git clone git@github.com:xbcsmith/epr-mcp-python.git
cd epr-mcp-python

python3 -m venv .venv/epr-mcp-python
source .venv/epr-mcp-python/bin/activate

pip install -e .
```

### Docker Development

```bash
git clone git@github.com:xbcsmith/epr-mcp-python.git
cd epr-mcp-python

# Copy and configure environment
cp .env.example .env
# Edit .env with your EPR_URL and EPR_TOKEN

# Start with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f epr-mcp-server
```

See [docker_compose.md](./docs/docker_compose.md) for detailed Docker Compose documentation.

### Development dependencies

```bash
pip install -e .[lint,test,build]
```

## Makefile

```text
install         Installs epr-mcp-python into a virtualenv called epr-mcp
lint            Run linter (requires ruff)
tests           Run tests
release         Run tox
wheel           Create an sdist bdist_wheel
clean           Cleanup everything
```

## Usage

The EPR MCP server provides both MCP tools and OpenAPI endpoints for interacting with the Event Provenance Registry.

### MCP Tools

The server automatically generates MCP tools from the OpenAPI specification:

- `fetchEvent` - Fetch an event by ID
- `fetchReceiver` - Fetch an event receiver by ID  
- `fetchGroup` - Fetch an event receiver group by ID
- `createEvent` - Create a new event
- `createReceiver` - Create a new event receiver
- `createGroup` - Create a new event receiver group
- `searchEvents` - Search for events
- `searchReceivers` - Search for event receivers
- `searchGroups` - Search for event receiver groups
- `healthCheck` - Health check endpoint

### OpenAPI Endpoints

When the server is running, the following OpenAPI endpoints are available:

- **OpenAPI Specification**:
  - YAML format: `http://localhost:8000/openapi.yaml`
  - JSON format: `http://localhost:8000/openapi.json`

- **API Documentation**:
  - Swagger UI: `http://localhost:8000/docs`

- **Health Check**:
  - `http://localhost:8000/health`

### Example Usage

```python
# Using MCP tools
mcp.call_tool('fetchEvent', {'id': 'event-123'})

mcp.call_tool('searchEvents', {
    'name': 'deployment', 
    'version': '1.0.0'
})

mcp.call_tool('createEvent', {
    'name': 'test-event',
    'version': '1.0.0',
    'release': '1.0.0',
    'platform_id': 'linux',
    'package': 'test-package',
    'description': 'Test event',
    'event_receiver_id': 'receiver-123',
    'success': True,
    'payload': {'key': 'value'}
})
```

### VSCode

#### HTTP Transport Configuration

```json
"mcp": {
	"servers": {
		"epr-mcp-server": {
			"type": "http",
			"url": "http://localhost:8000/mcp"
		}
	}
}
```

#### Docker Configuration (Alternative)

If running via Docker, you can use this configuration:

```json
"mcp": {
	"servers": {
		"epr-mcp-server": {
			"command": "docker",
			"args": [
				"run",
				"-d",
				"--rm",
				"--network=host",
				"-e",
				"EPR_URL=${input:epr_url}",
				"-e",
				"EPR_TOKEN=${input:epr_token}",
				"epr-mcp-python:latest"
			],
			"type": "http",
			"url": "http://localhost:8000/mcp"
		}
	},
	"inputs": [
		{
			"type": "promptString",
			"id": "epr_token",
			"description": "EPR API Token",
			"password": true
		},
		{
			"type": "promptString",
			"id": "epr_url",
			"description": "EPR URL",
			"default": "http://localhost:8042",
			"password": false
		}
	]
}
```

#### Local Development Configuration

For local development, start the server first and then use this configuration:

```json
"mcp": {
	"servers": {
		"epr-mcp-server": {
			"type": "http",
			"url": "http://localhost:8000/mcp",
			"env": {
				"EPR_URL": "${input:epr_url}",
				"EPR_TOKEN": "${input:epr_token}"
			}
		}
	},
	"inputs": [
		{
			"type": "promptString",
			"id": "epr_token",
			"description": "EPR API Token",
			"password": true
		},
		{
			"type": "promptString",
			"id": "epr_url",
			"description": "EPR URL",
			"default": "http://localhost:8042",
			"password": false
		}
	]
}
```

#### Starting the Server

Before using the VSCode integration, start the EPR MCP Server:

```bash
# Set environment variables
export EPR_URL="http://your-epr-server:8042"
export EPR_TOKEN="your-api-token"

# Start the server
python -m epr_mcp.main start
```

The server will be available at `http://localhost:8000/mcp` for MCP connections and `http://localhost:8000/docs` for API documentation.
