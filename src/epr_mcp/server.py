# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: © 2025 Brett Smith <xbcsmith@gmail.com>
# SPDX-License-Identifier: Apache-2.0

import json
import logging
import os
import sys
from pathlib import Path
from typing import Annotated

import httpx2
import yaml
from fastmcp import FastMCP
from pydantic import Field, ValidationError
from starlette.requests import Request
from starlette.responses import PlainTextResponse

from .common import create_client, get_search_query
from .config import TRANSPORTS, Config
from .errors import debug_except_hook
from .models import Event, EventReceiver, EventReceiverGroup
from .schemas import (
    EventReceiverGroupResponse,
    EventReceiverResponse,
    EventResponse,
    validate_event_list_response,
    validate_event_receiver_group_list_response,
    validate_event_receiver_group_response,
    validate_event_receiver_list_response,
    validate_event_receiver_response,
    validate_event_response,
    validate_input,
)

logger = logging.getLogger(__name__)

# EPR answers a successful create with 200; some versions answer 201.
CREATED_STATUS_CODES = (200, 201)


def filter_none_values(data: dict) -> dict:
    """Filter out None values from a dictionary to avoid sending null values to GraphQL"""
    return {key: value for key, value in data.items() if value is not None}


def handle_http_errors(e: Exception, operation: str, cfg: Config) -> str:
    """Log an exception from an EPR call and return a user-friendly message.

    Args:
        e: The exception raised while calling the EPR API.
        operation: Name of the tool that failed, used in generic messages.
        cfg: Server configuration providing the EPR URL.

    Returns:
        A message describing the failure, suitable to return to the MCP client.

    Examples:
        >>> handle_http_errors(RuntimeError("boom"), "fetch_event", Config(url="http://epr"))
        'Error in fetch_event: boom'
    """
    if isinstance(e, httpx2.ConnectError):
        logger.error(f"Connection failed to {cfg.url}: {e!s}")
        return f"Connection failed to EPR server at {cfg.url}. Please check if the EPR server is running and accessible. Error: {e!s}"
    elif isinstance(e, httpx2.TimeoutException):
        logger.error(f"Request timeout to {cfg.url}: {e!s}")
        return f"Request timeout to EPR server at {cfg.url}. Error: {e!s}"
    elif isinstance(e, httpx2.HTTPStatusError):
        logger.error(f"HTTP error from {cfg.url}: {e!s}")
        return f"HTTP error from EPR server: {e.response.status_code} - {e.response.text}"
    else:
        logger.error(f"Error in {operation}: {e!s}")
        return f"Error in {operation}: {e!s}"


def create_server(cfg: Config) -> FastMCP:
    """Build the EPR MCP server with all tools and HTTP routes registered.

    The server is not started, so tests and embedding code can attach a client
    or an ASGI test client without binding a network port.

    Args:
        cfg: Server configuration (EPR URL, optional token, debug flag).

    Returns:
        A configured ``FastMCP`` instance.

    Examples:
        >>> mcp = create_server(Config(url="http://localhost:8042"))
        >>> mcp.name
        'EPR MCP Server'
    """
    mcp = FastMCP(name="EPR MCP Server", version="1.0.0")

    @mcp.tool(title="Fetch Event", description="Fetch an event from EPR")
    async def fetch_event(id: Annotated[str, Field(description="Unique identifier of the event to fetch")]) -> str:
        """Fetch an event from the EPR"""
        try:
            logger.debug(f"Starting fetch_event for ID: {id}")

            # Validate input using schema
            validated_data = validate_input("fetch_event", id)
            event_id = validated_data["id"]
            logger.debug(f"Input validation successful, validated ID: {event_id}")

            url = f"{cfg.url}/api/v1/events/{event_id}"
            logger.debug(f"Making GET request to: {url}")

            async with create_client(cfg) as client:
                response = await client.get(url)
                logger.debug(f"GET response status: {response.status_code}")
                if response.status_code == 200:
                    response_data = response.json()
                    logger.debug(f"Raw response data type: {type(response_data)}")
                    # Handle case where API wraps data in a 'data' field
                    event_data = (
                        response_data.get("data", response_data) if isinstance(response_data, dict) else response_data
                    )

                    # Handle case where data is an array (EPR API returns array even for single item)
                    if isinstance(event_data, list):
                        if len(event_data) == 0:
                            return json.dumps({"error": "No event found with the specified ID"}, indent=2)
                        # Take the first event from the array for single event fetch
                        event_data = event_data[0]

                    # Validate response data with Pydantic schema
                    validated_event = EventResponse.model_validate(event_data)
                    logger.debug("Response validation successful")
                    return json.dumps(validated_event.model_dump(), indent=2)
                else:
                    return f"Failed to fetch event: {response.status_code} - {response.text}"
        except ValidationError as e:
            # Handle both input validation and response validation errors
            if "response validation failed" in str(e):
                logger.error(f"Response validation error in fetch_event: {e!s}")
                return f"Response validation error: {e!s}"
            else:
                logger.error(f"Input validation error in fetch_event: {e!s}")
                return f"Input validation error: {e!s}"
        except ValueError as e:
            logger.error(f"Input validation error in fetch_event: {e!s}")
            return f"Input validation error: {e!s}"
        except Exception as e:
            return handle_http_errors(e, "fetch_event", cfg)

    @mcp.tool(title="Fetch Event Receiver", description="Fetch an event receiver from EPR")
    async def fetch_receiver(
        id: Annotated[str, Field(description="Unique identifier of the event receiver to fetch")],
    ) -> str:
        """Fetch an event receiver from the EPR"""
        try:
            logger.debug(f"Starting fetch_receiver for ID: {id}")

            # Validate input using schema
            validated_data = validate_input("fetch_receiver", id)
            receiver_id = validated_data["id"]
            logger.debug(f"Input validation successful, validated ID: {receiver_id}")

            url = f"{cfg.url}/api/v1/receivers/{receiver_id}"
            logger.debug(f"Making GET request to: {url}")

            async with create_client(cfg) as client:
                response = await client.get(url)
                logger.debug(f"GET response status: {response.status_code}")
                if response.status_code == 200:
                    response_data = response.json()
                    logger.debug(f"Raw response data type: {type(response_data)}")
                    # Handle case where API wraps data in a 'data' field
                    receiver_data = (
                        response_data.get("data", response_data) if isinstance(response_data, dict) else response_data
                    )

                    # Handle case where data is an array (EPR API returns array even for single item)
                    if isinstance(receiver_data, list):
                        if len(receiver_data) == 0:
                            return json.dumps({"error": "No event receiver found with the specified ID"}, indent=2)
                        # Take the first receiver from the array for single receiver fetch
                        receiver_data = receiver_data[0]

                    # Validate response data with Pydantic schema
                    validated_receiver = EventReceiverResponse.model_validate(receiver_data)
                    logger.debug("Response validation successful")
                    return json.dumps(validated_receiver.model_dump(), indent=2)
                else:
                    return f"Failed to fetch event receiver: {response.status_code} - {response.text}"
        except ValidationError as e:
            # Handle both input validation and response validation errors
            if "response validation failed" in str(e):
                logger.error(f"Response validation error in fetch_receiver: {e!s}")
                return f"Response validation error: {e!s}"
            else:
                logger.error(f"Input validation error in fetch_receiver: {e!s}")
                return f"Input validation error: {e!s}"
        except ValueError as e:
            logger.error(f"Input validation error in fetch_receiver: {e!s}")
            return f"Input validation error: {e!s}"
        except Exception as e:
            return handle_http_errors(e, "fetch_receiver", cfg)

    @mcp.tool(title="Fetch Event Receiver Group", description="Fetch an event receiver group from EPR")
    async def fetch_group(
        id: Annotated[str, Field(description="Unique identifier of the event receiver group to fetch")],
    ) -> str:
        """Fetch an event receiver group from the EPR"""
        try:
            logger.debug(f"Starting fetch_group for ID: {id}")

            # Validate input using schema
            validated_data = validate_input("fetch_group", id)
            group_id = validated_data["id"]
            logger.debug(f"Input validation successful, validated ID: {group_id}")

            url = f"{cfg.url}/api/v1/groups/{group_id}"
            logger.debug(f"Making GET request to: {url}")

            async with create_client(cfg) as client:
                response = await client.get(url)
                logger.debug(f"GET response status: {response.status_code}")
                if response.status_code == 200:
                    response_data = response.json()
                    logger.debug(f"Raw response data type: {type(response_data)}")
                    # Handle case where API wraps data in a 'data' field
                    group_data = (
                        response_data.get("data", response_data) if isinstance(response_data, dict) else response_data
                    )

                    # Handle case where data is an array (EPR API returns array even for single item)
                    if isinstance(group_data, list):
                        if len(group_data) == 0:
                            return json.dumps(
                                {"error": "No event receiver group found with the specified ID"}, indent=2
                            )
                        # Take the first group from the array for single group fetch
                        group_data = group_data[0]

                    # Validate response data with Pydantic schema
                    validated_group = EventReceiverGroupResponse.model_validate(group_data)
                    logger.debug("Response validation successful")
                    return json.dumps(validated_group.model_dump(), indent=2)
                else:
                    return f"Failed to fetch event receiver group: {response.status_code} - {response.text}"
        except ValidationError as e:
            # Handle both input validation and response validation errors
            if "response validation failed" in str(e):
                logger.error(f"Response validation error in fetch_group: {e!s}")
                return f"Response validation error: {e!s}"
            else:
                logger.error(f"Input validation error in fetch_group: {e!s}")
                return f"Input validation error: {e!s}"
        except ValueError as e:
            logger.error(f"Input validation error in fetch_group: {e!s}")
            return f"Input validation error: {e!s}"
        except Exception as e:
            return handle_http_errors(e, "fetch_group", cfg)

    @mcp.tool(title="Search Events", description="Search for events in EPR")
    async def search_events(
        data: Annotated[
            dict,
            Field(description="Search criteria including name, version, package, platform_id, success status, etc."),
        ],
    ) -> str:
        """Search for events in the EPR"""
        try:
            logger.debug(f"Starting search_events with data: {data}")

            # Validate input using schema
            validated_data = validate_input("search_events", {"data": data})
            search_params = validated_data["data"]
            logger.debug(f"Input validation successful, search params: {search_params}")

            # Filter out None values to avoid sending null parameters to GraphQL
            filtered_params = filter_none_values(search_params)
            logger.debug(f"Filtered search params (None values removed): {filtered_params}")

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
            query = get_search_query(operation="events", params=filtered_params, fields=fields)
            logger.debug(f"Generated GraphQL query: {query.as_dict_query()}")

            url = f"{cfg.url}/api/v1/graphql/query"
            logger.debug(f"Making POST request to: {url}")

            async with create_client(cfg) as client:
                response = await client.post(url, json=query.as_dict_query())
                logger.debug(f"POST response status: {response.status_code}")
                if response.status_code == 200:
                    result = response.json()
                    if result.get("errors"):
                        return f"Failed to search events: {result['errors']}"
                    logger.debug(f"Raw GraphQL response structure: {type(result)}")
                    events_data = result.get("data", {}).get("events", [])
                    logger.debug(f"Extracted events data: {len(events_data)} events found")
                    # Validate response data with Pydantic schema
                    validated_events = validate_event_list_response(events_data)
                    logger.debug("Response validation successful")
                    return json.dumps(validated_events, indent=2)
                else:
                    return f"Failed to search events: {response.status_code} - {response.text}"
        except ValidationError as e:
            # Handle input validation errors (from validate_input)
            logger.error(f"Input validation error in search_events: {e!s}")
            return f"Input validation error: {e!s}"
        except ValueError as e:
            # Handle response validation errors (from validate_event_list_response)
            if "validation failed" in str(e):
                logger.error(f"Response validation error in search_events: {e!s}")
                return f"Response validation error: {e!s}"
            else:
                logger.error(f"Input validation error in search_events: {e!s}")
                return f"Input validation error: {e!s}"
        except Exception as e:
            return handle_http_errors(e, "search_events", cfg)

    @mcp.tool(title="Search Event Receivers", description="Search for event receivers in EPR")
    async def search_receivers(
        data: Annotated[dict, Field(description="Search criteria including name, type, version, description, etc.")],
    ) -> str:
        """Search for event receivers in the EPR"""
        try:
            logger.debug(f"Starting search_receivers with data: {data}")

            # Validate input using schema
            validated_data = validate_input("search_receivers", {"data": data})
            search_params = validated_data["data"]
            logger.debug(f"Input validation successful, search params: {search_params}")

            # Filter out None values to avoid sending null parameters to GraphQL
            filtered_params = filter_none_values(search_params)
            logger.debug(f"Filtered search params (None values removed): {filtered_params}")

            fields = ["id", "name", "type", "version", "description", "schema", "fingerprint", "created_at"]
            query = get_search_query(operation="event_receivers", params=filtered_params, fields=fields)
            logger.debug(f"Generated GraphQL query: {query.as_dict_query()}")

            url = f"{cfg.url}/api/v1/graphql/query"
            logger.debug(f"Making POST request to: {url}")

            async with create_client(cfg) as client:
                response = await client.post(url, json=query.as_dict_query())
                logger.debug(f"POST response status: {response.status_code}")
                if response.status_code == 200:
                    result = response.json()
                    if result.get("errors"):
                        return f"Failed to search event receivers: {result['errors']}"
                    logger.debug(f"Raw GraphQL response structure: {type(result)}")
                    receivers_data = result.get("data", {}).get("event_receivers", [])
                    logger.debug(f"Extracted receivers data: {len(receivers_data)} receivers found")
                    # Validate response data with Pydantic schema
                    validated_receivers = validate_event_receiver_list_response(receivers_data)
                    logger.debug("Response validation successful")
                    return json.dumps(validated_receivers, indent=2)
                else:
                    return f"Failed to search event receivers: {response.status_code} - {response.text}"
        except ValidationError as e:
            # Handle input validation errors (from validate_input)
            logger.error(f"Input validation error in search_receivers: {e!s}")
            return f"Input validation error: {e!s}"
        except ValueError as e:
            # Handle response validation errors (from validate_event_receiver_list_response)
            if "validation failed" in str(e):
                logger.error(f"Response validation error in search_receivers: {e!s}")
                return f"Response validation error: {e!s}"
            else:
                logger.error(f"Input validation error in search_receivers: {e!s}")
                return f"Input validation error: {e!s}"
        except Exception as e:
            return handle_http_errors(e, "search_receivers", cfg)

    @mcp.tool(title="Search Event Receiver Groups", description="Search for event receiver groups in EPR")
    async def search_groups(
        data: Annotated[dict, Field(description="Search criteria: any of name, type, version, description")],
    ) -> str:
        """Search for event receiver groups in the EPR"""
        try:
            logger.debug(f"Starting search_groups with data: {data}")

            # Validate input using schema
            validated_data = validate_input("search_groups", {"data": data})
            search_params = validated_data["data"]
            logger.debug(f"Input validation successful, search params: {search_params}")

            # Filter out None values to avoid sending null parameters to GraphQL
            filtered_params = filter_none_values(search_params)
            logger.debug(f"Filtered search params (None values removed): {filtered_params}")

            fields = [
                "id",
                "name",
                "type",
                "version",
                "description",
                "enabled",
                "event_receiver_ids",
                "created_at",
                "updated_at",
            ]
            query = get_search_query(operation="event_receiver_groups", params=filtered_params, fields=fields)
            logger.debug(f"Generated GraphQL query: {query.as_dict_query()}")

            url = f"{cfg.url}/api/v1/graphql/query"
            logger.debug(f"Making POST request to: {url}")

            async with create_client(cfg) as client:
                response = await client.post(url, json=query.as_dict_query())
                logger.debug(f"POST response status: {response.status_code}")
                if response.status_code == 200:
                    result = response.json()
                    if result.get("errors"):
                        return f"Failed to search event receiver groups: {result['errors']}"
                    logger.debug(f"Raw GraphQL response structure: {type(result)}")
                    groups_data = result.get("data", {}).get("event_receiver_groups", [])
                    logger.debug(f"Extracted groups data: {len(groups_data)} groups found")
                    # Validate response data with Pydantic schema
                    validated_groups = validate_event_receiver_group_list_response(groups_data)
                    logger.debug("Response validation successful")
                    return json.dumps(validated_groups, indent=2)
                else:
                    return f"Failed to search event receiver groups: {response.status_code} - {response.text}"
        except ValidationError as e:
            # Handle input validation errors (from validate_input)
            logger.error(f"Input validation error in search_groups: {e!s}")
            return f"Input validation error: {e!s}"
        except ValueError as e:
            # Handle response validation errors (from validate_event_receiver_group_list_response)
            if "validation failed" in str(e):
                logger.error(f"Response validation error in search_groups: {e!s}")
                return f"Response validation error: {e!s}"
            else:
                logger.error(f"Input validation error in search_groups: {e!s}")
                return f"Input validation error: {e!s}"
        except Exception as e:
            return handle_http_errors(e, "search_groups", cfg)

    @mcp.tool(title="Create Event", description="Create a new event in EPR")
    async def create_event(
        event_data: Annotated[
            dict,
            Field(
                description="Event creation data containing name, version, release, platform_id, package, description, event_receiver_id, success status, and payload"
            ),
        ],
    ) -> str:
        """Create a new event in the EPR"""
        try:
            logger.debug(f"Starting create_event with data: {event_data}")

            # Validate input using schema
            validated_data = validate_input("create_event", {"data": event_data})
            create_params = validated_data["data"]
            logger.debug(f"Input validation successful, create params: {create_params}")

            # Create Event model from validated data for better structure
            event = Event(**create_params)
            logger.debug(f"Created Event model: {event.as_dict_query()}")

            url = f"{cfg.url}/api/v1/events"
            logger.debug(f"Making POST request to: {url}")

            async with create_client(cfg) as client:
                response = await client.post(url, json=event.as_dict_query())
                logger.debug(f"POST response status: {response.status_code}")
                if response.status_code in CREATED_STATUS_CODES:
                    response_data = response.json()
                    logger.debug(f"Raw response data type: {type(response_data)}")
                    # Handle case where API wraps data in a 'data' field
                    created_event_data = (
                        response_data.get("data", response_data) if isinstance(response_data, dict) else response_data
                    )

                    # Handle case where data is an array (EPR API returns array even for single item)
                    if isinstance(created_event_data, list):
                        if len(created_event_data) == 0:
                            return json.dumps({"error": "Event creation returned empty result"}, indent=2)
                        # Take the first event from the array
                        created_event_data = created_event_data[0]

                    # EPR normally answers a create with just the new ID: {"data": "<id>"}
                    if isinstance(created_event_data, str):
                        return json.dumps({"message": "Event created successfully", "id": created_event_data}, indent=2)

                    # Validate response data with Pydantic schema
                    validated_event_data = validate_event_response(created_event_data)
                    logger.debug("Event created and response validation successful")
                    return json.dumps(
                        {"message": "Event created successfully", "event": validated_event_data}, indent=2
                    )
                else:
                    return f"Failed to create event: {response.status_code} - {response.text}"
        except ValidationError as e:
            # Handle both input validation and response validation errors
            if "response validation failed" in str(e):
                logger.error(f"Response validation error in create_event: {e!s}")
                return f"Response validation error: {e!s}"
            else:
                logger.error(f"Input validation error in create_event: {e!s}")
                return f"Input validation error: {e!s}"
        except ValueError as e:
            logger.error(f"Input validation error in create_event: {e!s}")
            return f"Input validation error: {e!s}"
        except Exception as e:
            return handle_http_errors(e, "create_event", cfg)

    @mcp.tool(title="Create Event Receiver", description="Create a new event receiver in EPR")
    async def create_receiver(
        receiver_data: Annotated[
            dict,
            Field(
                description="Event receiver creation data containing name, type, version, description, and schema (a JSON schema that event payloads must match)"
            ),
        ],
    ) -> str:
        """Create a new event receiver in the EPR"""
        try:
            logger.debug(f"Starting create_receiver with data: {receiver_data}")

            # Validate input using schema
            validated_data = validate_input("create_receiver", {"data": receiver_data})
            create_params = validated_data["data"]
            logger.debug(f"Input validation successful, create params: {create_params}")

            # Create EventReceiver model from validated data for better structure
            receiver = EventReceiver(**create_params)
            logger.debug(f"Created EventReceiver model: {receiver.as_dict_query()}")

            url = f"{cfg.url}/api/v1/receivers"
            logger.debug(f"Making POST request to: {url}")

            async with create_client(cfg) as client:
                response = await client.post(url, json=receiver.as_dict_query())
                logger.debug(f"POST response status: {response.status_code}")
                if response.status_code in CREATED_STATUS_CODES:
                    response_data = response.json()
                    logger.debug(f"Raw response data type: {type(response_data)}")
                    # Handle case where API wraps data in a 'data' field
                    created_receiver_data = (
                        response_data.get("data", response_data) if isinstance(response_data, dict) else response_data
                    )

                    # Handle case where data is an array (EPR API returns array even for single item)
                    if isinstance(created_receiver_data, list):
                        if len(created_receiver_data) == 0:
                            return json.dumps({"error": "Event receiver creation returned empty result"}, indent=2)
                        # Take the first receiver from the array
                        created_receiver_data = created_receiver_data[0]

                    # EPR normally answers a create with just the new ID: {"data": "<id>"}
                    if isinstance(created_receiver_data, str):
                        return json.dumps(
                            {"message": "Event receiver created successfully", "id": created_receiver_data}, indent=2
                        )

                    # Validate response data with Pydantic schema
                    validated_receiver_data = validate_event_receiver_response(created_receiver_data)
                    logger.debug("Event receiver created and response validation successful")
                    return json.dumps(
                        {"message": "Event receiver created successfully", "receiver": validated_receiver_data},
                        indent=2,
                    )
                else:
                    return f"Failed to create event receiver: {response.status_code} - {response.text}"
        except ValidationError as e:
            # Handle both input validation and response validation errors
            if "response validation failed" in str(e):
                logger.error(f"Response validation error in create_receiver: {e!s}")
                return f"Response validation error: {e!s}"
            else:
                logger.error(f"Input validation error in create_receiver: {e!s}")
                return f"Input validation error: {e!s}"
        except ValueError as e:
            logger.error(f"Input validation error in create_receiver: {e!s}")
            return f"Input validation error: {e!s}"
        except Exception as e:
            return handle_http_errors(e, "create_receiver", cfg)

    @mcp.tool(title="Create Event Receiver Group", description="Create a new event receiver group in EPR")
    async def create_group(
        group_data: Annotated[
            dict,
            Field(
                description="Event receiver group creation data containing name, type, version, description, and event_receiver_ids list"
            ),
        ],
    ) -> str:
        """Create a new event receiver group in the EPR"""
        try:
            logger.debug(f"Starting create_group with data: {group_data}")

            # Validate input using schema
            validated_data = validate_input("create_group", {"data": group_data})
            create_params = validated_data["data"]
            logger.debug(f"Input validation successful, create params: {create_params}")

            # Create EventReceiverGroup model from validated data for better structure
            group = EventReceiverGroup(**create_params)
            logger.debug(f"Created EventReceiverGroup model: {group.as_dict_query()}")

            url = f"{cfg.url}/api/v1/groups"
            logger.debug(f"Making POST request to: {url}")

            async with create_client(cfg) as client:
                response = await client.post(url, json=group.as_dict_query())
                logger.debug(f"POST response status: {response.status_code}")
                if response.status_code in CREATED_STATUS_CODES:
                    response_data = response.json()
                    logger.debug(f"Raw response data type: {type(response_data)}")
                    # Handle case where API wraps data in a 'data' field
                    created_group_data = (
                        response_data.get("data", response_data) if isinstance(response_data, dict) else response_data
                    )

                    # Handle case where data is an array (EPR API returns array even for single item)
                    if isinstance(created_group_data, list):
                        if len(created_group_data) == 0:
                            return json.dumps(
                                {"error": "Event receiver group creation returned empty result"}, indent=2
                            )
                        # Take the first group from the array
                        created_group_data = created_group_data[0]

                    # EPR normally answers a create with just the new ID: {"data": "<id>"}
                    if isinstance(created_group_data, str):
                        return json.dumps(
                            {"message": "Event receiver group created successfully", "id": created_group_data}, indent=2
                        )

                    # Validate response data with Pydantic schema
                    validated_group_data = validate_event_receiver_group_response(created_group_data)
                    logger.debug("Event receiver group created and response validation successful")
                    return json.dumps(
                        {"message": "Event receiver group created successfully", "group": validated_group_data},
                        indent=2,
                    )
                else:
                    return f"Failed to create event receiver group: {response.status_code} - {response.text}"
        except ValidationError as e:
            # Handle both input validation and response validation errors
            if "response validation failed" in str(e):
                logger.error(f"Response validation error in create_group: {e!s}")
                return f"Response validation error: {e!s}"
            else:
                logger.error(f"Input validation error in create_group: {e!s}")
                return f"Input validation error: {e!s}"
        except ValueError as e:
            logger.error(f"Input validation error in create_group: {e!s}")
            return f"Input validation error: {e!s}"
        except Exception as e:
            return handle_http_errors(e, "create_group", cfg)

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
                with open(openapi_path, "r") as f:
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

    return mcp


def run(cfg: Config) -> str:
    """Create the server and run it with the transport in the configuration.

    Args:
        cfg: Server configuration; ``transport`` is ``"http"`` or ``"stdio"``,
            and ``host`` and ``port`` apply to the HTTP transport.

    Returns:
        A short status message after the server stops.

    Raises:
        ValueError: If ``cfg.transport`` is not ``"http"`` or ``"stdio"``.
    """
    if cfg.transport not in TRANSPORTS:
        raise ValueError(f"Unsupported transport {cfg.transport!r}; expected one of {', '.join(TRANSPORTS)}")

    debug = cfg.debug or os.environ.get("EPR_DEBUG", False)
    if debug:
        sys.excepthook = debug_except_hook
        logger.setLevel(logging.DEBUG)

    mcp = create_server(cfg)

    logger.info("MCP is running with the following configuration:")
    logger.info(f"Debug mode: {debug}")
    logger.info(f"Transport: {cfg.transport}")
    logger.info(f"EPR URL: {cfg.url}")
    logger.info(f"EPR Token configured: {bool(cfg.token)}")
    if cfg.transport == "stdio":
        mcp.run(transport="stdio", show_banner=False)
    else:
        logger.info(f"MCP Server is running on http://{cfg.host}:{cfg.port}/mcp")
        mcp.run(transport="http", host=cfg.host, port=cfg.port)
    return "MCP stopped"
