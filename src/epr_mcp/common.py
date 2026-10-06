# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: © 2025Brett Smith <xbcsmith@gmail.com>
# SPDX-License-Identifier: Apache-2.0

import logging
import os
import sys
from typing import Optional

import httpx2

from .config import Config
from .errors import debug_except_hook
from .models import GraphQLQuery

logger = logging.getLogger(__name__)


debug = os.environ.get("EPR_DEBUG")
if debug:
    sys.excepthook = debug_except_hook
    logger.setLevel(logging.DEBUG)


def create_client(cfg: Config) -> httpx2.AsyncClient:
    """Create an HTTP client for the EPR API.

    The client sends a JSON content type and, when the configuration has a
    token, an ``Authorization: Bearer`` header on every request.

    Args:
        cfg: Server configuration providing the optional API token.

    Returns:
        A new ``httpx2.AsyncClient``; use it as an async context manager.

    Examples:
        >>> client = create_client(Config(url="http://epr", token="abc"))
        >>> client.headers["Authorization"]
        'Bearer abc'
    """
    headers = {"Content-Type": "application/json"}
    if cfg.token:
        headers["Authorization"] = f"Bearer {cfg.token}"
    return httpx2.AsyncClient(headers=headers)


def get_operation(name: str, operation: str) -> str:
    """Look up a GraphQL type or field name.

    Args:
        name: Kind of lookup: "search", "mutation", "operation", or "create".
        operation: The operation inside that kind, for example "events" or "create_event".

    Returns:
        The GraphQL input type or field name.

    Raises:
        KeyError: If the name or operation is not known.

    Examples:
        >>> get_operation("operation", "events")
        'event'
    """
    operation_map = {
        "search": {
            "events": "FindEventInput!",
            "event_receivers": "FindEventReceiverInput!",
            "event_receiver_groups": "FindEventReceiverGroupInput!",
        },
        "mutation": {
            "create_event": "CreateEventInput!",
            "create_event_receiver": "CreateEventReceiverInput!",
            "create_event_receiver_group": "CreateEventReceiverGroupInput!",
        },
        "operation": {
            "events": "event",
            "event_receivers": "event_receiver",
            "event_receiver_groups": "event_receiver_group",
        },
        "create": {
            "create_event": "event",
            "create_event_receiver": "event_receiver",
            "create_event_receiver_group": "event_receiver_group",
        },
    }
    return operation_map[name][operation]


def get_search_query(operation: str, params: Optional[dict] = None, fields: Optional[list] = None) -> GraphQLQuery:
    """Convert a query dictionary to a GraphQL query string."""
    variables = dict(obj=params)
    method = get_operation("search", operation)
    op = get_operation("operation", operation)
    _fields = ",".join(fields) if fields is not None else "id"
    query = f"""query ($obj: {method}){{{operation}({op}: $obj) {{ {_fields} }}}}"""
    return GraphQLQuery(query=query, variables=variables)


def get_mutation_query(operation: str, params: Optional[dict] = None) -> GraphQLQuery:
    """Convert a mutation dictionary to a GraphQL mutation string."""
    variables = dict(obj=params)
    method = get_operation("mutation", operation)
    op = get_operation("create", operation)
    query = f"""mutation ($obj: {method}){{{operation}({op}: $obj)}}"""
    return GraphQLQuery(query=query, variables=variables)
