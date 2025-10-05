# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: © 2025 Brett Smith <xbcsmith@gmail.com>
# SPDX-License-Identifier: Apache-2.0

"""Test the OpenAPI integration."""

import json
from pathlib import Path
from unittest.mock import Mock

import yaml
import pytest


def test_openapi_spec_exists():
    """Test that the OpenAPI specification file exists."""
    openapi_path = Path(__file__).parent.parent / "src" / "epr_mcp" / "openapi.yaml"
    assert openapi_path.exists(), "OpenAPI specification file should exist"


def test_openapi_spec_valid():
    """Test that the OpenAPI specification is valid YAML and has required fields."""
    openapi_path = Path(__file__).parent.parent / "src" / "epr_mcp" / "openapi.yaml"
    
    with open(openapi_path, 'r') as f:
        spec = yaml.safe_load(f)
    
    # Check required OpenAPI fields
    assert "openapi" in spec, "OpenAPI specification should have 'openapi' field"
    assert "info" in spec, "OpenAPI specification should have 'info' field"
    assert "paths" in spec, "OpenAPI specification should have 'paths' field"
    
    # Check info section
    assert "title" in spec["info"], "Info section should have 'title'"
    assert "version" in spec["info"], "Info section should have 'version'"
    
    # Check that we have our expected paths
    expected_paths = [
        "/api/v1/events/{id}",
        "/api/v1/events",
        "/api/v1/events/search",
        "/api/v1/receivers/{id}",
        "/api/v1/receivers",
        "/api/v1/receivers/search", 
        "/api/v1/groups/{id}",
        "/api/v1/groups",
        "/api/v1/groups/search",
        "/health"
    ]
    
    for path in expected_paths:
        assert path in spec["paths"], f"Path {path} should be in OpenAPI spec"


def test_openapi_spec_schemas():
    """Test that the OpenAPI specification has the required schemas."""
    openapi_path = Path(__file__).parent.parent / "src" / "epr_mcp" / "openapi.yaml"
    
    with open(openapi_path, 'r') as f:
        spec = yaml.safe_load(f)
    
    # Check components and schemas
    assert "components" in spec, "OpenAPI specification should have 'components'"
    assert "schemas" in spec["components"], "Components should have 'schemas'"
    
    expected_schemas = ["Event", "EventReceiver", "EventReceiverGroup", "SearchCriteria", "Error"]
    
    for schema in expected_schemas:
        assert schema in spec["components"]["schemas"], f"Schema {schema} should be defined"


def test_event_schema_structure():
    """Test that the Event schema has the correct structure."""
    openapi_path = Path(__file__).parent.parent / "src" / "epr_mcp" / "openapi.yaml"
    
    with open(openapi_path, 'r') as f:
        spec = yaml.safe_load(f)
    
    event_schema = spec["components"]["schemas"]["Event"]
    
    # Check required fields exist in properties
    required_fields = ["name", "version", "release", "platform_id", "package", 
                      "description", "event_receiver_id", "success", "payload"]
    
    assert "properties" in event_schema, "Event schema should have properties"
    assert "required" in event_schema, "Event schema should have required fields"
    
    for field in required_fields:
        assert field in event_schema["properties"], f"Event schema should have {field} property"
        assert field in event_schema["required"], f"Event schema should require {field}"


@pytest.mark.asyncio
async def test_openapi_endpoints_structure():
    """Test the structure of OpenAPI endpoints."""
    openapi_path = Path(__file__).parent.parent / "src" / "epr_mcp" / "openapi.yaml"
    
    with open(openapi_path, 'r') as f:
        spec = yaml.safe_load(f)
    
    # Test fetch endpoints (GET with path parameter)
    fetch_paths = ["/api/v1/events/{id}", "/api/v1/receivers/{id}", "/api/v1/groups/{id}"]
    
    for path in fetch_paths:
        assert "get" in spec["paths"][path], f"{path} should have GET method"
        get_spec = spec["paths"][path]["get"]
        assert "operationId" in get_spec, f"{path} GET should have operationId"
        assert "parameters" in get_spec, f"{path} GET should have parameters"
        assert "responses" in get_spec, f"{path} GET should have responses"
    
    # Test create endpoints (POST)
    create_paths = ["/api/v1/events", "/api/v1/receivers", "/api/v1/groups"]
    
    for path in create_paths:
        assert "post" in spec["paths"][path], f"{path} should have POST method"
        post_spec = spec["paths"][path]["post"]
        assert "operationId" in post_spec, f"{path} POST should have operationId"
        assert "requestBody" in post_spec, f"{path} POST should have requestBody"
        assert "responses" in post_spec, f"{path} POST should have responses"
    
    # Test search endpoints (POST)
    search_paths = ["/api/v1/events/search", "/api/v1/receivers/search", "/api/v1/groups/search"]
    
    for path in search_paths:
        assert "post" in spec["paths"][path], f"{path} should have POST method"
        post_spec = spec["paths"][path]["post"]
        assert "operationId" in post_spec, f"{path} POST should have operationId"
        assert "requestBody" in post_spec, f"{path} POST should have requestBody"