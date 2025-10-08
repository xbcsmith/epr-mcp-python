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
| [generate_epr_events.py](./generate_epr_events.py) | Event and receiver generation tool that creates sample CDEvents for testing and demonstration, with support for posting to EPR servers, dry-run mode, and file output |

## Running the Demos

### Quick Setup

For first-time users, here's the complete setup process:

```bash
# 1. Clone the repository (if not already done)
git clone https://github.com/xbcsmith/epr-mcp-python.git
cd epr-mcp-python/demos

# 2. Create and activate virtual environment
python -m venv .venv/epr-demos
source .venv/epr-demos/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install all dependencies
pip install -r requirements.txt

# 4. Run a demo
python openapi_demo.py
```

### Prerequisites

#### Setting up a Virtual Environment

It's recommended to use a virtual environment to avoid dependency conflicts:

```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate
```

#### Installing Dependencies

Install the EPR MCP Server and demo script dependencies:

```bash
# From the project root - install the main package
pip install -e .

# Install additional dependencies for demo scripts
pip install httpx ulid-py

# Or install all demo dependencies at once
pip install -e . httpx ulid-py
```

#### Required Dependencies for Demo Scripts

- **httpx**: Modern async HTTP client (required for `generate_epr_events.py`)
- **ulid-py**: ULID generation library (required for `generate_epr_events.py`)
- **epr-mcp-python**: The main package (provides OpenAPI demo functionality)

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

### EPR Events Generator

The events generator creates sample CDEvents and event receivers for testing and demonstration.

**Dependencies**: Requires `httpx` and `ulid-py` - install with `pip install httpx ulid-py`

```bash
# Generate and post events to a running EPR server
python generate_epr_events.py --url http://localhost:8042

# Dry run - show curl commands without posting
python generate_epr_events.py --dry-run

# Write events to disk as JSON files
python generate_epr_events.py --write-to-disk

# Custom timeout for requests
python generate_epr_events.py --timeout 30.0
```

This script will:
- Generate event receivers for 11 different CDEvent types
- Create sample events for services named "foo", "bar", "baz", "qux"  
- Support three modes: live posting, dry-run with curl commands, or file output
- Generate realistic CDEvent payloads with proper context and subject data
- Create ULID identifiers and timestamps for each event
- Output detailed status information for posted events

#### Generated Event Types

The script creates event receivers and events for these CDEvent types:
- `dev.cdevents.pipelinerun.started.0.2.0`
- `dev.cdevents.pipelinerun.queued.0.2.0`
- `dev.cdevents.pipelinerun.finished.0.2.0`
- `dev.cdevents.artifact.packaged.0.2.0`
- `dev.cdevents.artifact.published.0.2.0`
- `dev.cdevents.build.started.0.2.0`
- `dev.cdevents.build.finished.0.2.0`
- `dev.cdevents.testcaserun.finished.0.2.0`
- `dev.cdevents.testsuiterun.finished.0.2.0`
- `dev.cdevents.environment.created.0.2.0`
- `dev.cdevents.service.deployed.0.2.0`

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

### EPR Events Generator Usage

#### Basic Event Generation

```bash
# Generate and post sample events to local EPR server
python generate_epr_events.py

# Post to a different EPR server
python generate_epr_events.py --url https://your-epr-server.com:8042

# Use custom timeout (useful for slow networks)
python generate_epr_events.py --timeout 60.0
```

#### Development and Testing Workflows

```bash
# Preview what would be posted (dry run)
python generate_epr_events.py --dry-run | head -20

# Generate test data files for development
python generate_epr_events.py --write-to-disk

# Generated files will be in:
# epr_reports/event_receivers/  - Event receiver JSON files
# epr_reports/events/           - Event JSON files  
# epr_reports/curl_commands_*.txt - Ready-to-use curl commands
```

#### Integration with EPR Server Testing

```bash
# Start EPR server (in another terminal)
docker run -p 8042:8042 your-epr-server

# Generate realistic test data
python generate_epr_events.py --url http://localhost:8042

# Check results (44 total: 11 event receivers + 33 events)
# Output shows: "Posted 33/33 events successfully"
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
3. **Missing Dependencies**: Install all required packages:
   ```bash
   # Main package and demo dependencies
   pip install -e . httpx ulid-py
   
   # If you get import errors, verify installation:
   python -c "import httpx, ulid; print('Dependencies OK')"
   ```
4. **Virtual Environment**: Make sure you're in an activated virtual environment
   ```bash
   # Check if virtual environment is active (should show venv path)
   which python
   
   # Activate if needed
   source venv/bin/activate  # macOS/Linux
   # venv\Scripts\activate   # Windows
   ```
5. **Configuration**: Check EPR_URL and EPR_TOKEN environment variables

#### EPR Events Generator Specific Issues

1. **Import Errors**: Make sure required dependencies are installed
   ```bash
   # Install missing dependencies
   pip install httpx ulid-py
   
   # Verify imports work
   python -c "import httpx, ulid, json, logging; print('All imports OK')"
   ```

2. **Connection Refused**: Ensure the EPR server is running on the specified URL
   ```bash
   # Check if server is responding
   curl http://localhost:8042/health
   ```

3. **Event Receiver Creation Fails**: The script creates event receivers first, then events that reference them
   ```bash
   # Run in dry-run mode to see the exact requests
   python generate_epr_events.py --dry-run
   ```

3. **Timeout Errors**: For slow networks or servers, increase the timeout
   ```bash
   python generate_epr_events.py --timeout 60.0
   ```

4. **Debug Mode**: Enable debug logging to see detailed event payloads
   ```bash
   EPR_DEBUG=1 python generate_epr_events.py --dry-run
   ```

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