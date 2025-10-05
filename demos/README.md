# EPR MCP Server Demos

This directory contains demonstration scripts and examples showing how to use the EPR (Event Provenance Registry) MCP Server. These demos illustrate various features, integration patterns, and usage scenarios.

## Overview

The demos provide practical examples of:

- **OpenAPI Integration**: How to interact with the server's OpenAPI endpoints
- **MCP Tool Usage**: Examples of calling MCP tools programmatically
- **API Documentation**: How to access and use the interactive Swagger UI
- **Configuration**: Setting up the server for different environments
- **Testing Scenarios**: Common usage patterns and workflows

## Demo Files

| Name | Description |
|------|-------------|
| [openapi_demo.py](./openapi_demo.py) | Interactive demonstration script showcasing OpenAPI endpoints, available MCP tools, data models, and example usage patterns with detailed output formatting |

## Running the Demos

### Prerequisites

Make sure you have the EPR MCP Server installed:

```bash
# From the project root
pip install -e .
```

### OpenAPI Demo

The OpenAPI demo showcases the server's OpenAPI capabilities:

```bash
# Run the demo
python openapi_demo.py
```

This demo will display:
- Available OpenAPI endpoints (YAML/JSON specs, Swagger UI)
- Complete list of MCP tools generated from the OpenAPI specification
- Data models and schemas used by the server
- Key features and capabilities
- Example usage patterns for MCP tools
- Next steps for getting started

### Demo Output

When you run `openapi_demo.py`, you'll see comprehensive information including:

#### 📝 OpenAPI Endpoints
- YAML specification: `http://localhost:8000/openapi.yaml`
- JSON specification: `http://localhost:8000/openapi.json`
- Interactive documentation: `http://localhost:8000/docs`

#### 🔍 Available MCP Tools
- `fetchEvent` - Retrieve events by ID
- `fetchReceiver` - Retrieve event receivers by ID
- `fetchGroup` - Retrieve event receiver groups by ID
- `createEvent` - Create new events
- `createReceiver` - Create new event receivers
- `createGroup` - Create new event receiver groups
- `searchEvents` - Search for events with criteria
- `searchReceivers` - Search for event receivers
- `searchGroups` - Search for event receiver groups
- `healthCheck` - Server health status

#### 🏗️ Data Models
- Event, EventReceiver, EventReceiverGroup
- SearchCriteria, Error schemas
- Type-safe request/response handling

## Usage Examples

### Basic MCP Tool Usage

```python
# Fetch a specific event
result = mcp.call_tool('fetchEvent', {'id': 'event-123'})

# Search for events
results = mcp.call_tool('searchEvents', {
    'name': 'deployment',
    'version': '1.0.0',
    'platform_id': 'linux'
})

# Create a new event
new_event = mcp.call_tool('createEvent', {
    'name': 'test-event',
    'version': '1.0.0',
    'release': '1.0.0',
    'platform_id': 'linux',
    'package': 'test-package',
    'description': 'Test event for demonstration',
    'event_receiver_id': 'receiver-123',
    'success': True,
    'payload': {'environment': 'demo', 'status': 'completed'}
})
```

### Accessing OpenAPI Documentation

Once the server is running:

1. **Interactive API Explorer**: Visit [http://localhost:8000/docs](http://localhost:8000/docs)
2. **OpenAPI Specification**: 
   - JSON: [http://localhost:8000/openapi.json](http://localhost:8000/openapi.json)
   - YAML: [http://localhost:8000/openapi.yaml](http://localhost:8000/openapi.yaml)
3. **Health Check**: [http://localhost:8000/health](http://localhost:8000/health)

### Integration Patterns

#### With Claude Desktop

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

#### With MCP Client Libraries

```python
from mcp.client import Client

# Connect to the server
async with Client("stdio", ["python", "-m", "epr_mcp.main"]) as client:
    # List available tools
    tools = await client.list_tools()
    
    # Call a tool
    result = await client.call_tool("searchEvents", {
        "name": "deployment"
    })
```

## Development and Testing

### Creating New Demos

When creating new demonstration scripts:

1. **Follow the Pattern**: Use the same structure as `openapi_demo.py`
2. **Add Documentation**: Include clear docstrings and comments
3. **Update This README**: Add your demo to the table above
4. **Test Thoroughly**: Ensure demos work with different configurations

### Demo Script Template

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: © 2025 Brett Smith <xbcsmith@gmail.com>
# SPDX-License-Identifier: Apache-2.0

"""
Demo script for [specific feature].

This script demonstrates:
1. [Feature 1]
2. [Feature 2]
3. [Feature 3]

Usage:
    python your_demo.py
"""

def main():
    print("🚀 Your Demo Title")
    print("=" * 50)
    # Your demo code here
    print("Demo completed! 🎉")

if __name__ == "__main__":
    main()
```

## Troubleshooting

### Common Issues

1. **Server Not Running**: Make sure to start the EPR MCP Server before running demos
2. **Port Conflicts**: Default port is 8000, change if needed
3. **Missing Dependencies**: Run `pip install -e .` from project root
4. **Configuration**: Check EPR_URL and EPR_TOKEN environment variables

### Getting Help

- **Documentation**: Check the [../docs/](../docs/) directory for detailed guides
- **Issues**: Report problems on [GitHub Issues](https://github.com/xbcsmith/epr-mcp-python/issues)
- **Examples**: All demos include extensive comments and examples

## Contributing

To contribute new demos:

1. Create a new Python script following the template above
2. Add comprehensive documentation and examples
3. Update this README with your demo in the table
4. Test with different configurations
5. Submit a pull request

Your demos help other developers understand and use the EPR MCP Server effectively!