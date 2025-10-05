# EPR MCP Server Documentation

Welcome to the documentation for the EPR (Event Provenance Registry) MCP Server. This directory contains comprehensive documentation covering all aspects of the server implementation, including OpenAPI integration, schema validation, and usage examples.

## Overview

The EPR MCP Server is a Python-based Model Context Protocol (MCP) server that provides tools for interacting with the Event Provenance Registry. It features:

- **FastMCP Integration**: Built on the FastMCP framework for robust MCP server implementation
- **OpenAPI Support**: Complete OpenAPI 3.0 specification with interactive Swagger UI documentation
- **Schema Validation**: Comprehensive input validation using Pydantic models
- **Type Safety**: Full type annotations and structured data handling
- **REST API Compatibility**: HTTP endpoints alongside MCP tools

## Documentation Index

| Name | Description |
|------|-------------|
| [DOCKER_COMPOSE.md](./DOCKER_COMPOSE.md) | Complete Docker Compose setup guide including service profiles (production, monitoring), configuration management, deployment strategies, and troubleshooting for containerized environments |
| [OPENAPI_IMPLEMENTATION.md](./OPENAPI_IMPLEMENTATION.md) | Comprehensive guide to the OpenAPI 3.0 implementation, including endpoint definitions, schema documentation, Swagger UI integration, and examples of API usage |
| [SCHEMA_VALIDATION.md](./SCHEMA_VALIDATION.md) | Detailed documentation of Pydantic validation schemas for all MCP tools, including search criteria, creation inputs, and validation rules with examples |

## Quick Start

### 1. Installation

```bash
git clone https://github.com/xbcsmith/epr-mcp-python.git
cd epr-mcp-python
pip install -e .
```

### 2. Configuration

Set up your EPR server connection:

```bash
export EPR_URL="http://your-epr-server:8042"
export EPR_TOKEN="your-api-token"
```

### 3. Start the Server

```bash
python -m epr_mcp.main
```

### 4. Access Documentation

Once running, visit:
- **API Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **OpenAPI Spec (JSON)**: [http://localhost:8000/openapi.json](http://localhost:8000/openapi.json)
- **OpenAPI Spec (YAML)**: [http://localhost:8000/openapi.yaml](http://localhost:8000/openapi.yaml)

## Available MCP Tools

The server provides the following MCP tools:

### Fetch Operations
- `fetchEvent` - Retrieve a specific event by ID
- `fetchReceiver` - Retrieve a specific event receiver by ID
- `fetchGroup` - Retrieve a specific event receiver group by ID

### Search Operations
- `searchEvents` - Search for events using various criteria
- `searchReceivers` - Search for event receivers using filters
- `searchGroups` - Search for event receiver groups

### Create Operations  
- `createEvent` - Create a new event in EPR
- `createReceiver` - Create a new event receiver
- `createGroup` - Create a new event receiver group

### Utility Operations
- `healthCheck` - Check server health status

## Architecture

The EPR MCP Server is built with a modular architecture:

```
src/epr_mcp/
├── server.py              # Main MCP server implementation
├── openapi_server.py      # Alternative OpenAPI-first implementation
├── models.py              # Data models (Event, EventReceiver, etc.)
├── schemas.py             # Pydantic validation schemas
├── common.py              # Shared utilities and GraphQL query builders
├── config.py              # Configuration management
├── errors.py              # Error handling utilities
└── openapi.yaml           # OpenAPI 3.0 specification
```

## Data Models

### Core Entities

- **Event**: Represents an event in the provenance registry with metadata like name, version, platform, and payload
- **EventReceiver**: Defines endpoints that can receive events with schema validation
- **EventReceiverGroup**: Collections of event receivers for organized event routing

### Supporting Models

- **GraphQLQuery**: Structured GraphQL query representation
- **SearchCriteria**: Flexible search parameters for filtering operations
- **ValidationSchemas**: Pydantic models ensuring data integrity

## Development

### Running Tests

```bash
# Install test dependencies
pip install -e .[test]

# Run all tests
python -m pytest

# Run specific test files
python -m pytest tests/test_openapi.py -v
python -m pytest tests/test_schemas.py -v
```

### Linting

```bash
# Install lint dependencies
pip install -e .[lint]

# Run linting
ruff check src/ tests/
```

### Building

```bash
# Install build dependencies
pip install -e .[build]

# Create distributions
python -m build
```

## Integration Examples

### Using with Claude Desktop

Add to your Claude Desktop configuration:

```json
{
  "mcp": {
    "servers": {
      "epr-mcp-server": {
        "command": "python",
        "args": ["-m", "epr_mcp.main"],
        "env": {
          "EPR_URL": "http://your-epr-server:8042",
          "EPR_TOKEN": "your-api-token"
        },
        "type": "stdio"
      }
    }
  }
}
```

### Using with MCP Client Libraries

```python
from mcp.client import Client

# Connect to the server
client = Client("stdio", ["python", "-m", "epr_mcp.main"])

# Use MCP tools
result = client.call_tool("searchEvents", {
    "name": "deployment",
    "version": "1.0.0"
})
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## Support

For questions, issues, or contributions:

- **GitHub Issues**: [https://github.com/xbcsmith/epr-mcp-python/issues](https://github.com/xbcsmith/epr-mcp-python/issues)
- **Documentation**: This docs directory contains comprehensive guides
- **Examples**: See `openapi_demo.py` for interactive examples

## License

This project is licensed under the Apache License 2.0. See the [LICENSE](../LICENSE) file for details.