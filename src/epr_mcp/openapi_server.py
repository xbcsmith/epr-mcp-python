# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: © 2025 Brett Smith <xbcsmith@gmail.com>
# SPDX-License-Identifier: Apache-2.0

import logging
import os
import sys
from pathlib import Path

import httpx
from fastmcp.server.openapi import FastMCPOpenAPI, MCPType, RouteMap

from .errors import debug_except_hook
from .models import Event, EventReceiver, EventReceiverGroup
from .schemas import validate_input

logger = logging.getLogger(__name__)


class EPROpenAPIHandler:
    """Handler class for EPR API operations."""

    def __init__(self, epr_url: str, token: str | None = None):
        self.epr_url = epr_url
        self.token = token
        self.headers = {"Content-Type": "application/json"}
        if token:
            self.headers["Authorization"] = f"Bearer {token}"

    async def handle_fetch_event(self, id: str) -> dict:
        """Handle fetching a single event."""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.epr_url}/api/v1/events/{id}", headers=self.headers)
            if response.status_code == 200:
                event_data = response.json()
                event = Event(**event_data)
                return event.as_dict()
            else:
                raise Exception(f"Failed to fetch event: {response.status_code} - {response.text}")

    async def handle_fetch_receiver(self, id: str) -> dict:
        """Handle fetching a single event receiver."""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.epr_url}/api/v1/receivers/{id}", headers=self.headers)
            if response.status_code == 200:
                receiver_data = response.json()
                receiver = EventReceiver(**receiver_data)
                return receiver.as_dict()
            else:
                raise Exception(f"Failed to fetch event receiver: {response.status_code} - {response.text}")

    async def handle_fetch_group(self, id: str) -> dict:
        """Handle fetching a single event receiver group."""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.epr_url}/api/v1/groups/{id}", headers=self.headers)
            if response.status_code == 200:
                group_data = response.json()
                group = EventReceiverGroup(**group_data)
                return group.as_dict()
            else:
                raise Exception(f"Failed to fetch event receiver group: {response.status_code} - {response.text}")

    async def handle_create_event(self, event_data: dict) -> dict:
        """Handle creating a new event."""
        # Validate using schemas
        validated_data = validate_input("create_event", {"data": event_data})
        create_params = validated_data["data"]

        # Create Event model from validated data
        event = Event(**create_params)

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.epr_url}/api/v1/events", json=event.as_dict_query(), headers=self.headers
            )
            if response.status_code == 201:
                created_event_data = response.json()
                created_event = Event(**created_event_data)
                return {"message": "Event created successfully", "event": created_event.as_dict()}
            else:
                raise Exception(f"Failed to create event: {response.status_code} - {response.text}")

    async def handle_create_receiver(self, receiver_data: dict) -> dict:
        """Handle creating a new event receiver."""
        # Validate using schemas
        validated_data = validate_input("create_receiver", {"data": receiver_data})
        create_params = validated_data["data"]

        # Create EventReceiver model from validated data
        receiver = EventReceiver(**create_params)

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.epr_url}/api/v1/receivers", json=receiver.as_dict_query(), headers=self.headers
            )
            if response.status_code == 201:
                created_receiver_data = response.json()
                created_receiver = EventReceiver(**created_receiver_data)
                return {"message": "Event receiver created successfully", "receiver": created_receiver.as_dict()}
            else:
                raise Exception(f"Failed to create event receiver: {response.status_code} - {response.text}")

    async def handle_create_group(self, group_data: dict) -> dict:
        """Handle creating a new event receiver group."""
        # Validate using schemas
        validated_data = validate_input("create_group", {"data": group_data})
        create_params = validated_data["data"]

        # Create EventReceiverGroup model from validated data
        group = EventReceiverGroup(**create_params)

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.epr_url}/api/v1/groups", json=group.as_dict_query(), headers=self.headers
            )
            if response.status_code == 201:
                created_group_data = response.json()
                created_group = EventReceiverGroup(**created_group_data)
                return {"message": "Event receiver group created successfully", "group": created_group.as_dict()}
            else:
                raise Exception(f"Failed to create event receiver group: {response.status_code} - {response.text}")


def create_openapi_server(cfg):
    """Create FastMCP server using OpenAPI integration."""
    debug = cfg.debug or os.environ.get("EPR_DEBUG", False)
    if debug:
        sys.excepthook = debug_except_hook
        logger.setLevel(logging.DEBUG)

    # Get the path to the OpenAPI specification
    openapi_path = Path(__file__).parent / "openapi.yaml"

    # Create the EPR handler
    handler = EPROpenAPIHandler(cfg.url, cfg.token)

    # Define route mappings - map OpenAPI paths to MCP component types
    route_map = RouteMap(
        {
            # Fetch operations as Tools
            "/api/v1/events/{id}": MCPType.TOOL,
            "/api/v1/receivers/{id}": MCPType.TOOL,
            "/api/v1/groups/{id}": MCPType.TOOL,
            # Create operations as Tools
            "/api/v1/events": MCPType.TOOL,
            "/api/v1/receivers": MCPType.TOOL,
            "/api/v1/groups": MCPType.TOOL,
            # Search operations as Tools
            "/api/v1/events/search": MCPType.TOOL,
            "/api/v1/receivers/search": MCPType.TOOL,
            "/api/v1/groups/search": MCPType.TOOL,
            # Health check
            "/health": MCPType.TOOL,
        }
    )

    # Create FastMCP OpenAPI server
    mcp = FastMCPOpenAPI(
        name="EPR MCP Server", version="1.0.0", openapi_spec=openapi_path, route_map=route_map, base_url=cfg.url
    )

    # Register custom handlers for the operations
    # Note: In a full implementation, you would need to handle the routing
    # and parameter extraction from the OpenAPI operations

    return mcp


def run_openapi(cfg):
    """Run the MCP server with OpenAPI integration."""
    mcp = create_openapi_server(cfg)

    logger.info("EPR MCP Server (OpenAPI) is running with the following configuration:")
    logger.info(f"Debug mode: {cfg.debug}")
    logger.info(f"EPR URL: {cfg.url}")
    logger.info(f"EPR Token: {cfg.token}")
    logger.info("MCP Server is running on http://localhost:8000/mcp")

    mcp.run_async(transport="http", host="127.0.0.1", port=8000)
    return "MCP is running"
