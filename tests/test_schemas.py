#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: © 2025 Brett Smith <xbcsmith@gmail.com>
# SPDX-License-Identifier: Apache-2.0

"""
Test script to validate the schema validation functionality
"""

from pydantic import ValidationError
from epr_mcp.schemas import validate_input


def test_search_events_validation():
    """Test event search validation"""
    print("Testing search_events validation...")
    
    # Valid input
    valid_data = {
        "data": {
            "name": "foo",
            "version": "1.0.0"
        }
    }
    try:
        result = validate_input("search_events", valid_data)
        print("✓ Valid search_events input passed validation")
        print(f"  Validated data: {result}")
    except (ValidationError, ValueError) as e:
        print(f"✗ Valid search_events input failed: {e}")
    
    # Invalid input - missing data wrapper
    invalid_data = {
        "name": "foo",
        "version": "1.0.0"
    }
    try:
        result = validate_input("search_events", invalid_data)
        print("✗ Invalid search_events input incorrectly passed validation")
    except (ValidationError, ValueError) as e:
        print("✓ Invalid search_events input correctly failed validation")
        print(f"  Error: {e}")


def test_create_event_validation():
    """Test event creation validation"""
    print("\nTesting create_event validation...")
    
    # Valid input
    valid_data = {
        "data": {
            "name": "test-event",
            "version": "1.0.0",
            "release": "2025.01.001",
            "platform_id": "x64-linux",
            "package": "test-package",
            "description": "Test event description",
            "event_receiver_id": "receiver-123",
            "success": True,
            "payload": {"test": "data"}
        }
    }
    try:
        result = validate_input("create_event", valid_data)
        print("✓ Valid create_event input passed validation")
        print(f"  Validated data keys: {list(result.keys())}")
    except (ValidationError, ValueError) as e:
        print(f"✗ Valid create_event input failed: {e}")
    
    # Invalid input - missing required field
    invalid_data = {
        "data": {
            "name": "test-event",
            "version": "1.0.0",
            # missing required fields
        }
    }
    try:
        result = validate_input("create_event", invalid_data)
        print("✗ Invalid create_event input incorrectly passed validation")
    except (ValidationError, ValueError) as e:
        print("✓ Invalid create_event input correctly failed validation")
        print(f"  Error: {e}")


def test_fetch_validation():
    """Test fetch operations validation"""
    print("\nTesting fetch validation...")
    
    # Valid input
    valid_id = "event-123"
    try:
        result = validate_input("fetch_event", valid_id)
        print("✓ Valid fetch_event input passed validation")
        print(f"  Validated data: {result}")
    except (ValidationError, ValueError) as e:
        print(f"✗ Valid fetch_event input failed: {e}")
    
    # Invalid input - empty string
    invalid_id = ""
    try:
        result = validate_input("fetch_event", invalid_id)
        print("✗ Invalid fetch_event input incorrectly passed validation")
    except (ValidationError, ValueError) as e:
        print("✓ Invalid fetch_event input correctly failed validation")
        print(f"  Error: {e}")


def test_create_group_validation():
    """Test group creation validation"""
    print("\nTesting create_group validation...")
    
    # Valid input
    valid_data = {
        "data": {
            "name": "test-group",
            "type": "processing",
            "version": "1.0.0",
            "description": "Test group description",
            "event_receiver_ids": ["receiver-1", "receiver-2"]
        }
    }
    try:
        result = validate_input("create_group", valid_data)
        print("✓ Valid create_group input passed validation")
    except (ValidationError, ValueError) as e:
        print(f"✗ Valid create_group input failed: {e}")
    
    # Invalid input - empty event_receiver_ids list
    invalid_data = {
        "data": {
            "name": "test-group",
            "type": "processing",
            "version": "1.0.0",
            "description": "Test group description",
            "event_receiver_ids": []  # Empty list should fail
        }
    }
    try:
        result = validate_input("create_group", invalid_data)
        print("✗ Invalid create_group input incorrectly passed validation")
    except (ValidationError, ValueError) as e:
        print("✓ Invalid create_group input correctly failed validation")
        print(f"  Error: {e}")


if __name__ == "__main__":
    print("EPR MCP Server Schema Validation Tests")
    print("=" * 40)
    
    test_search_events_validation()
    test_create_event_validation()
    test_fetch_validation()
    test_create_group_validation()
    
    print("\nSchema validation tests completed!")