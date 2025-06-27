# epr-mcp-python

## Overview

EPR MCP Python is a python MCP server for the Event Provenance Registry server.

## Development

```bash
python3 -m venv ~/.virtualenvs/epr-mcp-python
source ~/.virtualenvs/epr-mcp-python/bin/activate

git clone git@github.com:xbcsmith/epr-mcp-python.git
cd epr-mcp-python

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
