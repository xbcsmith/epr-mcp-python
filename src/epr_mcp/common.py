# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: © 2025Brett Smith <xbcsmith@gmail.com>
# SPDX-License-Identifier: Apache-2.0

import logging
import os
import sys
from typing import Dict, List, Optional

from .errors import debug_except_hook
from .models import GraphQLQuery

logger = logging.getLogger(__name__)


debug = os.environ.get("EPR_DEBUG")
if debug:
    sys.excepthook = debug_except_hook
    logger.setLevel(logging.DEBUG)


def get_operation(name: str, operation: str) -> str:
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
