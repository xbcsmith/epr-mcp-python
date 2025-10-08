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
from fastmcp import FastMCP, Context
from starlette.requests import Request
from starlette.responses import PlainTextResponse
from pydantic import ValidationError, Field

from .common import get_search_query, get_mutation_query
from .errors import debug_except_hook
from .models import Event, EventReceiver, EventReceiverGroup
from .schemas import (
    validate_input, 
    validate_event_response, 
    validate_event_receiver_response, 
    validate_event_receiver_group_response,
    validate_event_list_response,
    validate_event_receiver_list_response,
    validate_event_receiver_group_list_response,
    EventResponse,
    EventReceiverResponse,
    EventReceiverGroupResponse
)

logger = logging.getLogger(__name__)


def run(cfg):
    debug = cfg.debug or os.environ.get("EPR_DEBUG", False)
    if debug:
        sys.excepthook = debug_except_hook
        logger.setLevel(logging.DEBUG)

    mcp = FastMCP("EPR MCP Server", "1.0.0")

    @mcp.tool(title="Fetch Event", description="Fetch an event from EPR")
    async def fetch_event(
        ctx: Context,
        id: str = Field(description="Unique identifier of the event to fetch")
    ) -> str:
        """Fetch an event from the EPR"""
        try:
            await ctx.debug(f"Starting fetch_event for ID: {id}")
            
            # Validate input using schema
            validated_data = validate_input("fetch_event", id)
            event_id = validated_data["id"]
            await ctx.debug(f"Input validation successful, validated ID: {event_id}")
            
            url = f"{cfg.url}/api/v1/events/{event_id}"
            await ctx.debug(f"Making GET request to: {url}")
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url)
                await ctx.debug(f"GET response status: {response.status_code}")
                if response.status_code == 200:
                    response_data = response.json()
                    await ctx.debug(f"Raw response data type: {type(response_data)}")
                    # Handle case where API wraps data in a 'data' field
                    event_data = response_data.get('data', response_data) if isinstance(response_data, dict) else response_data
                    
                    # Handle case where data is an array (EPR API returns array even for single item)
                    if isinstance(event_data, list):
                        if len(event_data) == 0:
                            return json.dumps({"error": "No event found with the specified ID"}, indent=2)
                        # Take the first event from the array for single event fetch
                        event_data = event_data[0]
                    
                    # Validate response data with Pydantic schema
                    validated_event = EventResponse.model_validate(event_data)
                    await ctx.debug("Response validation successful")
                    return json.dumps(validated_event.model_dump(), indent=2)
                else:
                    return f"Failed to fetch event: {response.status_code} - {response.text}"
        except ValidationError as e:
            # Handle both input validation and response validation errors
            if "response validation failed" in str(e):
                await ctx.error(f"Response validation error in fetch_event: {str(e)}")
                return f"Response validation error: {str(e)}"
            else:
                await ctx.error(f"Input validation error in fetch_event: {str(e)}")
                return f"Input validation error: {str(e)}"
        except ValueError as e:
            await ctx.error(f"Input validation error in fetch_event: {str(e)}")
            return f"Input validation error: {str(e)}"
        except Exception as e:
            await ctx.error(f"Error fetching event: {str(e)}")
            return f"Error fetching event: {str(e)}"

    @mcp.tool(title="Fetch Event Receiver", description="Fetch an event receiver from EPR")
    async def fetch_receiver(
        ctx: Context,
        id: str = Field(description="Unique identifier of the event receiver to fetch")
    ) -> str:
        """Fetch an event receiver from the EPR"""
        try:
            await ctx.debug(f"Starting fetch_receiver for ID: {id}")
            
            # Validate input using schema
            validated_data = validate_input("fetch_receiver", id)
            receiver_id = validated_data["id"]
            await ctx.debug(f"Input validation successful, validated ID: {receiver_id}")
            
            url = f"{cfg.url}/api/v1/receivers/{receiver_id}"
            await ctx.debug(f"Making GET request to: {url}")
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url)
                await ctx.debug(f"GET response status: {response.status_code}")
                if response.status_code == 200:
                    response_data = response.json()
                    await ctx.debug(f"Raw response data type: {type(response_data)}")
                    # Handle case where API wraps data in a 'data' field
                    receiver_data = response_data.get('data', response_data) if isinstance(response_data, dict) else response_data
                    
                    # Handle case where data is an array (EPR API returns array even for single item)
                    if isinstance(receiver_data, list):
                        if len(receiver_data) == 0:
                            return json.dumps({"error": "No event receiver found with the specified ID"}, indent=2)
                        # Take the first receiver from the array for single receiver fetch
                        receiver_data = receiver_data[0]
                    
                    # Validate response data with Pydantic schema
                    validated_receiver = EventReceiverResponse.model_validate(receiver_data)
                    await ctx.debug("Response validation successful")
                    return json.dumps(validated_receiver.model_dump(), indent=2)
                else:
                    return f"Failed to fetch event receiver: {response.status_code} - {response.text}"
        except ValidationError as e:
            # Handle both input validation and response validation errors
            if "response validation failed" in str(e):
                await ctx.error(f"Response validation error in fetch_receiver: {str(e)}")
                return f"Response validation error: {str(e)}"
            else:
                await ctx.error(f"Input validation error in fetch_receiver: {str(e)}")
                return f"Input validation error: {str(e)}"
        except ValueError as e:
            await ctx.error(f"Input validation error in fetch_receiver: {str(e)}")
            return f"Input validation error: {str(e)}"
        except Exception as e:
            await ctx.error(f"Error fetching event receiver: {str(e)}")
            return f"Error fetching event receiver: {str(e)}"

    @mcp.tool(title="Fetch Event Receiver Group", description="Fetch an event receiver group from EPR")
    async def fetch_group(
        ctx: Context,
        id: str = Field(description="Unique identifier of the event receiver group to fetch")
    ) -> str:
        """Fetch an event receiver group from the EPR"""
        try:
            await ctx.debug(f"Starting fetch_group for ID: {id}")
            
            # Validate input using schema
            validated_data = validate_input("fetch_group", id)
            group_id = validated_data["id"]
            await ctx.debug(f"Input validation successful, validated ID: {group_id}")
            
            url = f"{cfg.url}/api/v1/groups/{group_id}"
            await ctx.debug(f"Making GET request to: {url}")
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url)
                await ctx.debug(f"GET response status: {response.status_code}")
                if response.status_code == 200:
                    response_data = response.json()
                    await ctx.debug(f"Raw response data type: {type(response_data)}")
                    # Handle case where API wraps data in a 'data' field
                    group_data = response_data.get('data', response_data) if isinstance(response_data, dict) else response_data
                    
                    # Handle case where data is an array (EPR API returns array even for single item)
                    if isinstance(group_data, list):
                        if len(group_data) == 0:
                            return json.dumps({"error": "No event receiver group found with the specified ID"}, indent=2)
                        # Take the first group from the array for single group fetch
                        group_data = group_data[0]
                    
                    # Validate response data with Pydantic schema
                    validated_group = EventReceiverGroupResponse.model_validate(group_data)
                    await ctx.debug("Response validation successful")
                    return json.dumps(validated_group.model_dump(), indent=2)
                else:
                    return f"Failed to fetch event receiver group: {response.status_code} - {response.text}"
        except ValidationError as e:
            # Handle both input validation and response validation errors
            if "response validation failed" in str(e):
                await ctx.error(f"Response validation error in fetch_group: {str(e)}")
                return f"Response validation error: {str(e)}"
            else:
                await ctx.error(f"Input validation error in fetch_group: {str(e)}")
                return f"Input validation error: {str(e)}"
        except ValueError as e:
            await ctx.error(f"Input validation error in fetch_group: {str(e)}")
            return f"Input validation error: {str(e)}"
        except Exception as e:
            await ctx.error(f"Error fetching event receiver group: {str(e)}")
            return f"Error fetching event receiver group: {str(e)}"

    @mcp.tool(title="Search Events", description="Search for events in EPR")
    async def search_events(
        ctx: Context,
        data: dict = Field(description="Search criteria including name, version, package, platform_id, success status, etc.")
    ) -> str:
        """Search for events in the EPR"""
        try:
            await ctx.debug(f"Starting search_events with data: {data}")
            
            # Validate input using schema
            validated_data = validate_input("search_events", data)
            search_params = validated_data["data"]
            await ctx.debug(f"Input validation successful, search params: {search_params}")
            
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
            await ctx.debug(f"Generated GraphQL query: {query.as_dict_query()}")
            
            url = f"{cfg.url}/api/v1/graphql/query"
            await ctx.debug(f"Making POST request to: {url}")
            
            async with httpx.AsyncClient() as client:
                headers = {"Content-Type": "application/json"}
                response = await client.post(url, json=query.as_dict_query(), headers=headers)
                await ctx.debug(f"POST response status: {response.status_code}")
                if response.status_code == 200:
                    result = response.json()
                    await ctx.debug(f"Raw GraphQL response structure: {type(result)}")
                    events_data = result.get('data', {}).get('events', [])
                    await ctx.debug(f"Extracted events data: {len(events_data)} events found")
                    # Validate response data with Pydantic schema
                    validated_events = validate_event_list_response(events_data)
                    await ctx.debug("Response validation successful")
                    return json.dumps(validated_events, indent=2)
                else:
                    return f"Failed to search events: {response.status_code} - {response.text}"
        except ValidationError as e:
            # Handle both input validation and response validation errors
            if "response validation failed" in str(e):
                await ctx.error(f"Response validation error in search_events: {str(e)}")
                return f"Response validation error: {str(e)}"
            else:
                await ctx.error(f"Input validation error in search_events: {str(e)}")
                return f"Input validation error: {str(e)}"
        except ValueError as e:
            await ctx.error(f"Input validation error in search_events: {str(e)}")
            return f"Input validation error: {str(e)}"
        except Exception as e:
            await ctx.error(f"Error searching events: {str(e)}")
            return f"Error searching events: {str(e)}"

    @mcp.tool(title="Search Event Receivers", description="Search for event receivers in EPR")
    async def search_receivers(
        ctx: Context,
        data: dict = Field(description="Search criteria including name, type, version, description, etc.")
    ) -> str:
        """Search for event receivers in the EPR"""
        try:
            await ctx.debug(f"Starting search_receivers with data: {data}")
            
            # Validate input using schema
            validated_data = validate_input("search_receivers", data)
            search_params = validated_data["data"]
            await ctx.debug(f"Input validation successful, search params: {search_params}")
            
            fields = ["id", "name", "type", "version", "description", "schema", "fingerprint", "created_at"]
            query = get_search_query(operation="event_receivers", params=search_params, fields=fields)
            await ctx.debug(f"Generated GraphQL query: {query.as_dict_query()}")
            
            url = f"{cfg.url}/api/v1/graphql/query"
            await ctx.debug(f"Making POST request to: {url}")
            
            async with httpx.AsyncClient() as client:
                headers = {"Content-Type": "application/json"}
                response = await client.post(url, json=query.as_dict_query(), headers=headers)
                await ctx.debug(f"POST response status: {response.status_code}")
                if response.status_code == 200:
                    result = response.json()
                    await ctx.debug(f"Raw GraphQL response structure: {type(result)}")
                    receivers_data = result.get('data', {}).get('event_receivers', [])
                    await ctx.debug(f"Extracted receivers data: {len(receivers_data)} receivers found")
                    # Validate response data with Pydantic schema
                    validated_receivers = validate_event_receiver_list_response(receivers_data)
                    await ctx.debug("Response validation successful")
                    return json.dumps(validated_receivers, indent=2)
                else:
                    return f"Failed to search event receivers: {response.status_code} - {response.text}"
        except ValidationError as e:
            # Handle both input validation and response validation errors
            if "response validation failed" in str(e):
                await ctx.error(f"Response validation error in search_receivers: {str(e)}")
                return f"Response validation error: {str(e)}"
            else:
                await ctx.error(f"Input validation error in search_receivers: {str(e)}")
                return f"Input validation error: {str(e)}"
        except ValueError as e:
            await ctx.error(f"Input validation error in search_receivers: {str(e)}")
            return f"Input validation error: {str(e)}"
        except Exception as e:
            await ctx.error(f"Error searching event receivers: {str(e)}")
            return f"Error searching event receivers: {str(e)}"

    @mcp.tool(title="Search Event Receiver Groups", description="Search for event receiver groups in EPR")
    async def search_groups(
        ctx: Context,
        data: dict = Field(description="Search criteria including name, type, version, description, enabled status, etc.")
    ) -> str:
        """Search for event receiver groups in the EPR"""
        try:
            await ctx.debug(f"Starting search_groups with data: {data}")
            
            # Validate input using schema
            validated_data = validate_input("search_groups", data)
            search_params = validated_data["data"]
            await ctx.debug(f"Input validation successful, search params: {search_params}")
            
            fields = ["id", "name", "type", "version", "description", "enabled", "event_receiver_ids", "fingerprint", "created_at", "updated_at"]
            query = get_search_query(operation="event_receiver_groups", params=search_params, fields=fields)
            await ctx.debug(f"Generated GraphQL query: {query.as_dict_query()}")
            
            url = f"{cfg.url}/api/v1/graphql/query"
            await ctx.debug(f"Making POST request to: {url}")
            
            async with httpx.AsyncClient() as client:
                headers = {"Content-Type": "application/json"}
                response = await client.post(url, json=query.as_dict_query(), headers=headers)
                await ctx.debug(f"POST response status: {response.status_code}")
                if response.status_code == 200:
                    result = response.json()
                    await ctx.debug(f"Raw GraphQL response structure: {type(result)}")
                    groups_data = result.get('data', {}).get('event_receiver_groups', [])
                    await ctx.debug(f"Extracted groups data: {len(groups_data)} groups found")
                    # Validate response data with Pydantic schema
                    validated_groups = validate_event_receiver_group_list_response(groups_data)
                    await ctx.debug("Response validation successful")
                    return json.dumps(validated_groups, indent=2)
                else:
                    return f"Failed to search event receiver groups: {response.status_code} - {response.text}"
        except ValidationError as e:
            # Handle both input validation and response validation errors
            if "response validation failed" in str(e):
                await ctx.error(f"Response validation error in search_groups: {str(e)}")
                return f"Response validation error: {str(e)}"
            else:
                await ctx.error(f"Input validation error in search_groups: {str(e)}")
                return f"Input validation error: {str(e)}"
        except ValueError as e:
            await ctx.error(f"Input validation error in search_groups: {str(e)}")
            return f"Input validation error: {str(e)}"
        except Exception as e:
            await ctx.error(f"Error searching event receiver groups: {str(e)}")
            return f"Error searching event receiver groups: {str(e)}"

    @mcp.tool(title="Create Event", description="Create a new event in EPR")
    async def create_event(
        ctx: Context,
        event_data: dict = Field(description="Event creation data containing name, version, release, platform_id, package, description, event_receiver_id, success status, and payload")
    ) -> str:
        """Create a new event in the EPR"""
        try:
            await ctx.debug(f"Starting create_event with data: {event_data}")
            
            # Validate input using schema
            validated_data = validate_input("create_event", event_data)
            create_params = validated_data["data"]
            await ctx.debug(f"Input validation successful, create params: {create_params}")
            
            # Create Event model from validated data for better structure
            event = Event(**create_params)
            await ctx.debug(f"Created Event model: {event.as_dict_query()}")
            
            url = f"{cfg.url}/api/v1/events"
            await ctx.debug(f"Making POST request to: {url}")
            
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=event.as_dict_query())
                await ctx.debug(f"POST response status: {response.status_code}")
                if response.status_code == 201:
                    response_data = response.json()
                    await ctx.debug(f"Raw response data type: {type(response_data)}")
                    # Handle case where API wraps data in a 'data' field
                    created_event_data = response_data.get('data', response_data) if isinstance(response_data, dict) else response_data
                    
                    # Handle case where data is an array (EPR API returns array even for single item)
                    if isinstance(created_event_data, list):
                        if len(created_event_data) == 0:
                            return json.dumps({"error": "Event creation returned empty result"}, indent=2)
                        # Take the first event from the array
                        created_event_data = created_event_data[0]
                    
                    # Validate response data with Pydantic schema
                    validated_event_data = validate_event_response(created_event_data)
                    await ctx.debug("Event created and response validation successful")
                    return json.dumps({"message": "Event created successfully", "event": validated_event_data}, indent=2)
                else:
                    return f"Failed to create event: {response.status_code} - {response.text}"
        except ValidationError as e:
            # Handle both input validation and response validation errors
            if "response validation failed" in str(e):
                await ctx.error(f"Response validation error in create_event: {str(e)}")
                return f"Response validation error: {str(e)}"
            else:
                await ctx.error(f"Input validation error in create_event: {str(e)}")
                return f"Input validation error: {str(e)}"
        except ValueError as e:
            await ctx.error(f"Input validation error in create_event: {str(e)}")
            return f"Input validation error: {str(e)}"
        except Exception as e:
            await ctx.error(f"Error creating event: {str(e)}")
            return f"Error creating event: {str(e)}"

    @mcp.tool(title="Create Event Receiver", description="Create a new event receiver in EPR")
    async def create_receiver(
        ctx: Context,
        receiver_data: dict = Field(description="Event receiver creation data containing name, type, version, and description")
    ) -> str:
        """Create a new event receiver in the EPR"""
        try:
            await ctx.debug(f"Starting create_receiver with data: {receiver_data}")
            
            # Validate input using schema
            validated_data = validate_input("create_receiver", receiver_data)
            create_params = validated_data["data"]
            await ctx.debug(f"Input validation successful, create params: {create_params}")
            
            # Create EventReceiver model from validated data for better structure
            receiver = EventReceiver(**create_params)
            await ctx.debug(f"Created EventReceiver model: {receiver.as_dict_query()}")
            
            url = f"{cfg.url}/api/v1/receivers"
            await ctx.debug(f"Making POST request to: {url}")
            
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=receiver.as_dict_query())
                await ctx.debug(f"POST response status: {response.status_code}")
                if response.status_code == 201:
                    response_data = response.json()
                    await ctx.debug(f"Raw response data type: {type(response_data)}")
                    # Handle case where API wraps data in a 'data' field
                    created_receiver_data = response_data.get('data', response_data) if isinstance(response_data, dict) else response_data
                    
                    # Handle case where data is an array (EPR API returns array even for single item)
                    if isinstance(created_receiver_data, list):
                        if len(created_receiver_data) == 0:
                            return json.dumps({"error": "Event receiver creation returned empty result"}, indent=2)
                        # Take the first receiver from the array
                        created_receiver_data = created_receiver_data[0]
                    
                    # Validate response data with Pydantic schema
                    validated_receiver_data = validate_event_receiver_response(created_receiver_data)
                    await ctx.debug("Event receiver created and response validation successful")
                    return json.dumps({"message": "Event receiver created successfully", "receiver": validated_receiver_data}, indent=2)
                else:
                    return f"Failed to create event receiver: {response.status_code} - {response.text}"
        except ValidationError as e:
            # Handle both input validation and response validation errors
            if "response validation failed" in str(e):
                await ctx.error(f"Response validation error in create_receiver: {str(e)}")
                return f"Response validation error: {str(e)}"
            else:
                await ctx.error(f"Input validation error in create_receiver: {str(e)}")
                return f"Input validation error: {str(e)}"
        except ValueError as e:
            await ctx.error(f"Input validation error in create_receiver: {str(e)}")
            return f"Input validation error: {str(e)}"
        except Exception as e:
            await ctx.error(f"Error creating event receiver: {str(e)}")
            return f"Error creating event receiver: {str(e)}"

    @mcp.tool(title="Create Event Receiver Group", description="Create a new event receiver group in EPR")
    async def create_group(
        ctx: Context,
        group_data: dict = Field(description="Event receiver group creation data containing name, type, version, description, and event_receiver_ids list")
    ) -> str:
        """Create a new event receiver group in the EPR"""
        try:
            await ctx.debug(f"Starting create_group with data: {group_data}")
            
            # Validate input using schema
            validated_data = validate_input("create_group", group_data)
            create_params = validated_data["data"]
            await ctx.debug(f"Input validation successful, create params: {create_params}")
            
            # Create EventReceiverGroup model from validated data for better structure
            group = EventReceiverGroup(**create_params)
            await ctx.debug(f"Created EventReceiverGroup model: {group.as_dict_query()}")
            
            url = f"{cfg.url}/api/v1/groups"
            await ctx.debug(f"Making POST request to: {url}")
            
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=group.as_dict_query())
                await ctx.debug(f"POST response status: {response.status_code}")
                if response.status_code == 201:
                    response_data = response.json()
                    await ctx.debug(f"Raw response data type: {type(response_data)}")
                    # Handle case where API wraps data in a 'data' field
                    created_group_data = response_data.get('data', response_data) if isinstance(response_data, dict) else response_data
                    
                    # Handle case where data is an array (EPR API returns array even for single item)
                    if isinstance(created_group_data, list):
                        if len(created_group_data) == 0:
                            return json.dumps({"error": "Event receiver group creation returned empty result"}, indent=2)
                        # Take the first group from the array
                        created_group_data = created_group_data[0]
                    
                    # Validate response data with Pydantic schema
                    validated_group_data = validate_event_receiver_group_response(created_group_data)
                    await ctx.debug("Event receiver group created and response validation successful")
                    return json.dumps({"message": "Event receiver group created successfully", "group": validated_group_data}, indent=2)
                else:
                    return f"Failed to create event receiver group: {response.status_code} - {response.text}"
        except ValidationError as e:
            # Handle both input validation and response validation errors
            if "response validation failed" in str(e):
                await ctx.error(f"Response validation error in create_group: {str(e)}")
                return f"Response validation error: {str(e)}"
            else:
                await ctx.error(f"Input validation error in create_group: {str(e)}")
                return f"Input validation error: {str(e)}"
        except ValueError as e:
            await ctx.error(f"Input validation error in create_group: {str(e)}")
            return f"Input validation error: {str(e)}"
        except Exception as e:
            await ctx.error(f"Error creating event receiver group: {str(e)}")
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
