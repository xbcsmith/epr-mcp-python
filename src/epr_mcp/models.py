# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: © 2024 Brett Smith <xbcsmith@gmail.com>
# SPDX-License-Identifier: Apache-2.0

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Dict, List


class ModelType(Enum):
    EVENT = "Event"
    RECEIVER = "EventReceiver"
    GROUP = "EventReceiverGroup"

    def lower(self):
        return self.value.lower()

    def lower_plural(self):
        return self.lower() + "s"


@dataclass
class Model:
    """Base class for data objects. Provides as_dict"""

    def as_dict(self):
        """Get a dictionary contain object properties"""
        return asdict(self)

    def as_dict_query(self):
        """Get a dictionary contain object properties"""
        return {k: v for k, v in self.as_dict().items() if v}


@dataclass
class Event(Model):
    """Data class for Events"""

    id: str = field(default="", compare=False)
    name: str = ""
    version: str = ""
    release: str = ""
    platform_id: str = ""
    package: str = ""
    description: str = ""
    payload: Dict[str, Any] = field(default_factory=dict)
    success: bool = False
    created_at: str = field(default="", compare=False)
    event_receiver_id: str = ""
    event_receiver: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EventReceiver(Model):
    """Data class for EventReceivers"""

    id: str = field(default="", compare=False)
    name: str = ""
    type: str = ""
    version: str = ""
    description: str = ""
    schema: Dict[str, str] = field(default_factory=dict)
    fingerprint: str = ""
    created_at: str = field(default="", compare=False)


@dataclass
class EventReceiverGroup(Model):
    """Data class for EventReceiverGroups"""

    id: str = field(default="", compare=False)
    name: str = ""
    type: str = ""
    version: str = ""
    description: str = ""
    enabled: bool = False
    event_receiver_ids: List[str] = field(default_factory=list)
    created_at: str = field(default="", compare=False)
    updated_at: str = field(default="", compare=False)
    fingerprint: str = ""


@dataclass
class Data(Model):
    """Data class for Data"""

    events = List[Event]
    receivers = List[EventReceiver]
    receiver_groups = List[EventReceiverGroup]


@dataclass
class Message(Model):
    """Data class for message to be sent to the message bus"""

    success: bool
    id: str
    specversion: str
    type: str
    source: str
    api_version: str
    name: str
    version: str
    release: str
    platform_id: str
    package: str
    data: Data


@dataclass
class GraphQLQuery(Model):
    query: str
    variables: Dict[str, Any] = field(default_factory=dict)
