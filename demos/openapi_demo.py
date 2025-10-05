#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: © 2025 Brett Smith <xbcsmith@gmail.com>
# SPDX-License-Identifier: Apache-2.0

"""
Demo script to test the EPR MCP Server OpenAPI endpoints.

This script demonstrates how to:
1. Start the MCP server with OpenAPI support
2. Access the OpenAPI specification endpoints
3. View the Swagger UI documentation

Usage:
    python openapi_demo.py
"""

import asyncio
import sys
from pathlib import Path

# Add the src directory to the path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent / "src"))

from epr_mcp.server import run
from epr_mcp.config import Config


class DemoConfig:
    """Mock configuration for demo purposes."""
    def __init__(self):
        self.url = "https://api.epr.example.com"
        self.token = "demo-token"
        self.debug = True


async def demo_openapi_endpoints():
    """Demonstrate the OpenAPI endpoints."""
    print("🚀 EPR MCP Server OpenAPI Demo")
    print("=" * 50)
    
    print("\n📝 OpenAPI Specification Available at:")
    print("   • YAML format: http://localhost:8000/openapi.yaml")
    print("   • JSON format: http://localhost:8000/openapi.json")
    
    print("\n📚 API Documentation Available at:")
    print("   • Swagger UI: http://localhost:8000/docs")
    
    print("\n🔍 Available MCP Tools (generated from OpenAPI spec):")
    
    # List the operations that would be available as MCP tools
    operations = [
        ("fetchEvent", "GET /api/v1/events/{id} - Fetch a single event"),
        ("fetchReceiver", "GET /api/v1/receivers/{id} - Fetch a single event receiver"),
        ("fetchGroup", "GET /api/v1/groups/{id} - Fetch a single event receiver group"),
        ("createEvent", "POST /api/v1/events - Create a new event"),
        ("createReceiver", "POST /api/v1/receivers - Create a new event receiver"),
        ("createGroup", "POST /api/v1/groups - Create a new event receiver group"),
        ("searchEvents", "POST /api/v1/events/search - Search for events"),
        ("searchReceivers", "POST /api/v1/receivers/search - Search for event receivers"),
        ("searchGroups", "POST /api/v1/groups/search - Search for event receiver groups"),
        ("healthCheck", "GET /health - Health check endpoint"),
    ]
    
    for op_id, description in operations:
        print(f"   • {op_id}: {description}")
    
    print("\n🏗️  Data Models:")
    models = ["Event", "EventReceiver", "EventReceiverGroup", "SearchCriteria", "Error"]
    for model in models:
        print(f"   • {model}")
    
    print("\n💡 Key Features:")
    print("   • Automatic MCP tool generation from OpenAPI spec")
    print("   • Type-safe request/response handling")
    print("   • Built-in API documentation")
    print("   • Schema validation using Pydantic models")
    print("   • Swagger UI for interactive testing")
    
    print("\n🎯 Next Steps:")
    print("   1. Start the server: python -m epr_mcp.main")
    print("   2. Visit http://localhost:8000/docs to explore the API")
    print("   3. Use MCP tools to interact with EPR endpoints")
    print("   4. Access OpenAPI spec at http://localhost:8000/openapi.json")
    
    print("\n📋 Example MCP Tool Usage:")
    print("   # Fetch an event")
    print("   mcp.call_tool('fetchEvent', {'id': 'event-123'})")
    print("")
    print("   # Search for events")
    print("   mcp.call_tool('searchEvents', {'name': 'deployment', 'version': '1.0.0'})")
    print("")
    print("   # Create a new event")
    print("   mcp.call_tool('createEvent', {")
    print("       'name': 'test-event',")
    print("       'version': '1.0.0',")
    print("       'release': '1.0.0',")
    print("       'platform_id': 'linux',")
    print("       'package': 'test-package',")
    print("       'description': 'Test event',")
    print("       'event_receiver_id': 'receiver-123',")
    print("       'success': True,")
    print("       'payload': {'key': 'value'}")
    print("   })")
    
    print("\n" + "=" * 50)
    print("Demo completed! 🎉")


if __name__ == "__main__":
    asyncio.run(demo_openapi_endpoints())