# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: © 2025 Brett Smith <xbcsmith@gmail.com>
# SPDX-License-Identifier: Apache-2.0

import asyncio
import logging
import os
import sys
from pathlib import Path

import json
import yaml

try:
    import yaml
except ImportError:
    yaml = None

import httpx
from fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import PlainTextResponse
from pydantic import ValidationError

from .common import get_search_query, get_mutation_query
from .errors import debug_except_hook
from .models import Event, EventReceiver, EventReceiverGroup
from .schemas import validate_input

logger = logging.getLogger(__name__)


def run(cfg):
    debug = cfg.debug or os.environ.get("EPR_DEBUG", False)
    if debug:
        sys.excepthook = debug_except_hook
        logger.setLevel(logging.DEBUG)

    mcp = FastMCP("EPR MCP Server", "1.0.0")

    @mcp.tool(title="Fetch Event", description="Fetch an event from EPR")
    async def fetch_event(epr_url: str, id: str) -> str:
        """Fetch an event from the EPR"""
        try:
            # Validate input using schema
            validated_data = validate_input("fetch_event", id)
            event_id = validated_data["id"]
            
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{epr_url}/api/v1/events/{event_id}")
                if response.status_code == 200:
                    event_data = response.json()
                    event = Event(**event_data)
                    return json.dumps(event.as_dict(), indent=2)
                else:
                    return f"Failed to fetch event: {response.status_code} - {response.text}"
        except (ValidationError, ValueError) as e:
            return f"Input validation error: {str(e)}"
        except Exception as e:
            return f"Error fetching event: {str(e)}"

    @mcp.tool(title="Fetch Event Receiver", description="Fetch an event receiver from EPR")
    async def fetch_receiver(epr_url: str, id: str) -> str:
        """Fetch an event receiver from the EPR"""
        try:
            # Validate input using schema
            validated_data = validate_input("fetch_receiver", id)
            receiver_id = validated_data["id"]
            
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{epr_url}/api/v1/receivers/{receiver_id}")
                if response.status_code == 200:
                    receiver_data = response.json()
                    receiver = EventReceiver(**receiver_data)
                    return json.dumps(receiver.as_dict(), indent=2)
                else:
                    return f"Failed to fetch event receiver: {response.status_code} - {response.text}"
        except (ValidationError, ValueError) as e:
            return f"Input validation error: {str(e)}"
        except Exception as e:
            return f"Error fetching event receiver: {str(e)}"

    @mcp.tool(title="Fetch Event Receiver Group", description="Fetch an event receiver group from EPR")
    async def fetch_group(epr_url: str, id: str) -> str:
        """Fetch an event receiver group from the EPR"""
        try:
            # Validate input using schema
            validated_data = validate_input("fetch_group", id)
            group_id = validated_data["id"]
            
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{epr_url}/api/v1/groups/{group_id}")
                if response.status_code == 200:
                    group_data = response.json()
                    group = EventReceiverGroup(**group_data)
                    return json.dumps(group.as_dict(), indent=2)
                else:
                    return f"Failed to fetch event receiver group: {response.status_code} - {response.text}"
        except (ValidationError, ValueError) as e:
            return f"Input validation error: {str(e)}"
        except Exception as e:
            return f"Error fetching event receiver group: {str(e)}"

    @mcp.tool(title="Search Events", description="Search for events in EPR")
    async def search_events(epr_url: str, data: dict) -> str:
        """Search for events in the EPR"""
        try:
            # Validate input using schema
            validated_data = validate_input("search_events", data)
            search_params = validated_data["data"]
            
            fields = [
                "id",
                "name",
                "version",
                "release",
                "platform_id",
                "package",
                "description",
                "success",
                "event_receiver_id",
                "created_at",
                "payload",
            ]
            query = get_search_query(operation="events", params=search_params, fields=fields)
            async with httpx.AsyncClient() as client:
                headers = {"Content-Type": "application/json"}
                response = await client.post(f"{epr_url}/api/v1/graphql/query", json=query.as_dict_query(), headers=headers)
                if response.status_code == 200:
                    result = response.json()
                    events = [Event(**event_data) for event_data in result.get('data', {}).get('events', [])]
                    return json.dumps([event.as_dict() for event in events], indent=2)
                else:
                    return f"Failed to search events: {response.status_code} - {response.text}"
        except (ValidationError, ValueError) as e:
            return f"Input validation error: {str(e)}"
        except Exception as e:
            return f"Error searching events: {str(e)}"

    @mcp.tool(title="Search Event Receivers", description="Search for event receivers in EPR")
    async def search_receivers(epr_url: str, data: dict) -> str:
        """Search for event receivers in the EPR"""
        try:
            # Validate input using schema
            validated_data = validate_input("search_receivers", data)
            search_params = validated_data["data"]
            
            fields = ["id", "name", "type", "version", "description", "schema", "fingerprint", "created_at"]
            query = get_search_query(operation="event_receivers", params=search_params, fields=fields)
            async with httpx.AsyncClient() as client:
                headers = {"Content-Type": "application/json"}
                response = await client.post(f"{epr_url}/api/v1/graphql/query", json=query.as_dict_query(), headers=headers)
                if response.status_code == 200:
                    result = response.json()
                    receivers = [EventReceiver(**receiver_data) for receiver_data in result.get('data', {}).get('event_receivers', [])]
                    return json.dumps([receiver.as_dict() for receiver in receivers], indent=2)
                else:
                    return f"Failed to search event receivers: {response.status_code} - {response.text}"
        except (ValidationError, ValueError) as e:
            return f"Input validation error: {str(e)}"
        except Exception as e:
            return f"Error searching event receivers: {str(e)}"

    @mcp.tool(title="Search Event Receiver Groups", description="Search for event receiver groups in EPR")
    async def search_groups(epr_url: str, data: dict) -> str:
        """Search for event receiver groups in the EPR"""
        try:
            # Validate input using schema
            validated_data = validate_input("search_groups", data)
            search_params = validated_data["data"]
            
            fields = ["id", "name", "type", "version", "description", "enabled", "event_receiver_ids", "fingerprint", "created_at", "updated_at"]
            query = get_search_query(operation="event_receiver_groups", params=search_params, fields=fields)
            async with httpx.AsyncClient() as client:
                headers = {"Content-Type": "application/json"}
                response = await client.post(f"{epr_url}/api/v1/graphql/query", json=query.as_dict_query(), headers=headers)
                if response.status_code == 200:
                    result = response.json()
                    groups = [EventReceiverGroup(**group_data) for group_data in result.get('data', {}).get('event_receiver_groups', [])]
                    return json.dumps([group.as_dict() for group in groups], indent=2)
                else:
                    return f"Failed to search event receiver groups: {response.status_code} - {response.text}"
        except (ValidationError, ValueError) as e:
            return f"Input validation error: {str(e)}"
        except Exception as e:
            return f"Error searching event receiver groups: {str(e)}"

    @mcp.tool(title="Create Event", description="Create a new event in EPR")
    async def create_event(epr_url: str, event_data: dict) -> str:
        """Create a new event in the EPR"""
        try:
            # Validate input using schema
            validated_data = validate_input("create_event", event_data)
            create_params = validated_data["data"]
            
            # Create Event model from validated data for better structure
            event = Event(**create_params)
            
            async with httpx.AsyncClient() as client:
                response = await client.post(f"{epr_url}/api/v1/events", json=event.as_dict_query())
                if response.status_code == 201:
                    created_event_data = response.json()
                    created_event = Event(**created_event_data)
                    return json.dumps({"message": "Event created successfully", "event": created_event.as_dict()}, indent=2)
                else:
                    return f"Failed to create event: {response.status_code} - {response.text}"
        except (ValidationError, ValueError) as e:
            return f"Input validation error: {str(e)}"
        except Exception as e:
            return f"Error creating event: {str(e)}"

    @mcp.tool(title="Create Event Receiver", description="Create a new event receiver in EPR")
    async def create_receiver(epr_url: str, receiver_data: dict) -> str:
        """Create a new event receiver in the EPR"""
        try:
            # Validate input using schema
            validated_data = validate_input("create_receiver", receiver_data)
            create_params = validated_data["data"]
            
            # Create EventReceiver model from validated data for better structure
            receiver = EventReceiver(**create_params)
            
            async with httpx.AsyncClient() as client:
                response = await client.post(f"{epr_url}/api/v1/receivers", json=receiver.as_dict_query())
                if response.status_code == 201:
                    created_receiver_data = response.json()
                    created_receiver = EventReceiver(**created_receiver_data)
                    return json.dumps({"message": "Event receiver created successfully", "receiver": created_receiver.as_dict()}, indent=2)
                else:
                    return f"Failed to create event receiver: {response.status_code} - {response.text}"
        except (ValidationError, ValueError) as e:
            return f"Input validation error: {str(e)}"
        except Exception as e:
            return f"Error creating event receiver: {str(e)}"

    @mcp.tool(title="Create Event Receiver Group", description="Create a new event receiver group in EPR")
    async def create_group(epr_url: str, group_data: dict) -> str:
        """Create a new event receiver group in the EPR"""
        try:
            # Validate input using schema
            validated_data = validate_input("create_group", group_data)
            create_params = validated_data["data"]
            
            # Create EventReceiverGroup model from validated data for better structure
            group = EventReceiverGroup(**create_params)
            
            async with httpx.AsyncClient() as client:
                response = await client.post(f"{epr_url}/api/v1/groups", json=group.as_dict_query())
                if response.status_code == 201:
                    created_group_data = response.json()
                    created_group = EventReceiverGroup(**created_group_data)
                    return json.dumps({"message": "Event receiver group created successfully", "group": created_group.as_dict()}, indent=2)
                else:
                    return f"Failed to create event receiver group: {response.status_code} - {response.text}"
        except (ValidationError, ValueError) as e:
            return f"Input validation error: {str(e)}"
        except Exception as e:
            return f"Error creating event receiver group: {str(e)}"

    @mcp.custom_route("/health", methods=["GET"])
    async def health_check(request: Request) -> PlainTextResponse:
        return PlainTextResponse("OK")

    @mcp.custom_route("/openapi.yaml", methods=["GET"])
    async def openapi_spec_yaml(request: Request):
        """Serve the OpenAPI specification as YAML"""
        from starlette.responses import FileResponse
        openapi_path = Path(__file__).parent / "openapi.yaml"
        if openapi_path.exists():
            return FileResponse(openapi_path, media_type="text/yaml")
        else:
            from starlette.responses import JSONResponse
            return JSONResponse({"error": "OpenAPI specification not found"}, status_code=404)
    
    @mcp.custom_route("/openapi.json", methods=["GET"])
    async def openapi_spec_json(request: Request):
        """Serve the OpenAPI specification as JSON"""
        from starlette.responses import JSONResponse
        openapi_path = Path(__file__).parent / "openapi.yaml"
        if openapi_path.exists():
            if yaml is not None:
                with open(openapi_path, 'r') as f:
                    spec = yaml.safe_load(f)
                return JSONResponse(spec)
            else:
                return JSONResponse({"error": "YAML library not available"}, status_code=500)
        else:
            return JSONResponse({"error": "OpenAPI specification not found"}, status_code=404)
    
    @mcp.custom_route("/docs", methods=["GET"])
    async def swagger_ui(request: Request):
        """Serve Swagger UI for API documentation"""
        from starlette.responses import HTMLResponse
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>EPR API Documentation</title>
            <link rel="stylesheet" type="text/css" href="https://unpkg.com/swagger-ui-dist@3.25.0/swagger-ui.css" />
            <style>
                html {{
                    box-sizing: border-box;
                    overflow: -moz-scrollbars-vertical;
                    overflow-y: scroll;
                }}
                *, *:before, *:after {{
                    box-sizing: inherit;
                }}
                body {{
                    margin:0;
                    background: #fafafa;
                }}
            </style>
        </head>
        <body>
            <div id="swagger-ui"></div>
            <script src="https://unpkg.com/swagger-ui-dist@3.25.0/swagger-ui-bundle.js"></script>
            <script src="https://unpkg.com/swagger-ui-dist@3.25.0/swagger-ui-standalone-preset.js"></script>
            <script>
                window.onload = function() {{
                    const ui = SwaggerUIBundle({{
                        url: '{request.url.scheme}://{request.url.netloc}/openapi.json',
                        dom_id: '#swagger-ui',
                        deepLinking: true,
                        presets: [
                            SwaggerUIBundle.presets.apis,
                            SwaggerUIStandalonePreset
                        ],
                        plugins: [
                            SwaggerUIBundle.plugins.DownloadUrl
                        ],
                        layout: "StandaloneLayout"
                    }})
                }}
            </script>
        </body>
        </html>
        """
        return HTMLResponse(html)

    """Run the MCP"""
    logger.info("MCP is running with the following configuration:")
    logger.info(f"Debug mode: {debug}")
    logger.info(f"MCP Server is running on http://localhost:8000/mcp")
    logger.info(f"EPR URL: {cfg.url}")
    logger.info(f"EPR Token: {cfg.token}")
    asyncio.run(mcp.run_async(transport="http", host="127.0.0.1", port=8000))
    return "MCP is running"
