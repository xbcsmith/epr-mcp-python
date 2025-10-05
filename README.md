# epr-mcp-python

## Overview

EPR MCP Python is a python MCP server for the Event Provenance Registry server.

## Development

```bash
git clone git@github.com:xbcsmith/epr-mcp-python.git
cd epr-mcp-python

python3 -m venv .venv/epr-mcp-python
source .venv/epr-mcp-python/bin/activate

pip install -e .
```

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

```text

```

### VSCode

```json
"mcp": {
	"servers": {
		"epr-mcp-server": {
			"command": "docker",
			"args": [
				"run",
				"-i",
				"--rm",
				"--network=host",
				"-e",
				"EPR_URL",
				"-e",
				"EPR_TOKEN",
				"epr-mcp-python:latest"
			],
			"env": {
				"EPR_URL": "${input:epr_url}",
				"EPR_TOKEN": "${input:epr_token}"
			},
			"type": "stdio"
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
