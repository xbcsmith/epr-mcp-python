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
install         Installs epr into a virtualenv called epr-mcp-python
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
        "erp_mcp_docker": {
            "command": "docker",
            "args": [
                "run",
                "-i",
                "--rm",
                "--network=host",
                "-e",
                "EPR_URL",
                "epr-mcp-python:latest"
            ],
            "env": {
                "EPR_URL": "http://localhost:8042"
            }
        }
    }
}
```