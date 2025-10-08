# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: © 2025 Brett Smith <xbcsmith@gmail.com>
# SPDX-License-Identifier: Apache-2.0

import re
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, ValidationError, field_validator


class EventSearchInput(BaseModel):
    """Schema for event search input"""

    name: Optional[str] = Field(
        None,
        pattern=r"^[A-Za-z0-9]+([._-]?[A-Za-z0-9]+)*(/[A-Za-z0-9]+([._-]?[A-Za-z0-9]+)*)*$",
        description="Name of the event",
    )
    version: Optional[str] = Field(
        None,
        pattern=r"([0-9]+)(\\.[0-9]+)?(\\.[0-9]+)?(-([0-9A-Za-z\\-]+(\\.[0-9A-Za-z\\-]+)*))?(\\+([0-9A-Za-z\\-]+(\\.[0-9A-Za-z\\-]+)*))?",
        description="Version of the event",
    )
    release: Optional[str] = Field(None, pattern=r"^\S+$", description="Release version")
    platform_id: Optional[str] = Field(
        None, pattern=r"^([0-9a-zA-Z]+)(-[0-9a-zA-Z]+)+$", description="Platform identifier"
    )
    package: Optional[str] = Field(None, pattern=r"^([A-Za-z]+)$", description="Package name")
    description: Optional[str] = Field(None, pattern=r"^(.|\s)*$", description="Event description")
    success: Optional[bool] = Field(None, description="Success status")
    event_receiver_id: Optional[str] = Field(None, pattern=r"^([0-9A-Za-z]{26})$", description="Event receiver ID")

    @field_validator(
        "name", "version", "release", "platform_id", "package", "description", "event_receiver_id", mode="before"
    )
    @classmethod
    def strip_whitespace(cls, v):
        """Strip whitespace from string fields"""
        if isinstance(v, str):
            stripped = v.strip()
            return stripped if stripped else None
        return v


class EventReceiverSearchInput(BaseModel):
    """Schema for event receiver search input"""

    name: Optional[str] = Field(
        None,
        pattern=r"^[A-Za-z0-9]+([._-]?[A-Za-z0-9]+)*(/[A-Za-z0-9]+([._-]?[A-Za-z0-9]+)*)*$",
        description="Name of the event receiver",
    )
    type: Optional[str] = Field(None, pattern=r"^[^ ]+$", description="Type of the event receiver")
    version: Optional[str] = Field(
        None,
        pattern=r"([0-9]+)(\\.[0-9]+)?(\\.[0-9]+)?(-([0-9A-Za-z\\-]+(\\.[0-9A-Za-z\\-]+)*))?(\\+([0-9A-Za-z\\-]+(\\.[0-9A-Za-z\\-]+)*))?",
        description="Version of the event receiver",
    )
    description: Optional[str] = Field(None, pattern=r"^(.|\s)*$", description="Event receiver description")

    @field_validator("name", "type", "version", "description", mode="before")
    @classmethod
    def strip_whitespace(cls, v):
        """Strip whitespace from string fields"""
        if isinstance(v, str):
            stripped = v.strip()
            return stripped if stripped else None
        return v


class EventReceiverGroupSearchInput(BaseModel):
    """Schema for event receiver group search input"""

    name: Optional[str] = Field(
        None,
        pattern=r"^[A-Za-z0-9]+([._-]?[A-Za-z0-9]+)*(/[A-Za-z0-9]+([._-]?[A-Za-z0-9]+)*)*$",
        description="Name of the event receiver group",
    )
    type: Optional[str] = Field(None, pattern=r"^[^ ]+$", description="Type of the event receiver group")
    version: Optional[str] = Field(
        None,
        pattern=r"([0-9]+)(\\.[0-9]+)?(\\.[0-9]+)?(-([0-9A-Za-z\\-]+(\\.[0-9A-Za-z\\-]+)*))?(\\+([0-9A-Za-z\\-]+(\\.[0-9A-Za-z\\-]+)*))?",
        description="Version of the event receiver group",
    )
    description: Optional[str] = Field(None, pattern=r"^(.|\s)*$", description="Event receiver group description")

    @field_validator("name", "type", "version", "description", mode="before")
    @classmethod
    def strip_whitespace(cls, v):
        """Strip whitespace from string fields"""
        if isinstance(v, str):
            stripped = v.strip()
            return stripped if stripped else None
        return v


class SearchDataWrapper(BaseModel):
    """Wrapper for search data input"""

    data: Union[EventSearchInput, EventReceiverSearchInput, EventReceiverGroupSearchInput] = Field(
        ..., description="Search criteria data"
    )


class EventCreateInput(BaseModel):
    """Schema for event creation input"""

    name: str = Field(
        ...,
        pattern=r"^[A-Za-z0-9]+([._-]?[A-Za-z0-9]+)*(/[A-Za-z0-9]+([._-]?[A-Za-z0-9]+)*)*$",
        description="Name of the event",
        min_length=1,
    )
    version: str = Field(
        ...,
        pattern=r"([0-9]+)(\\.[0-9]+)?(\\.[0-9]+)?(-([0-9A-Za-z\\-]+(\\.[0-9A-Za-z\\-]+)*))?(\\+([0-9A-Za-z\\-]+(\\.[0-9A-Za-z\\-]+)*))?",
        description="Version of the event",
        min_length=1,
    )
    release: str = Field(..., pattern=r"^\S+$", description="Release version", min_length=1)
    platform_id: str = Field(
        ..., pattern=r"^([0-9a-zA-Z]+)(-[0-9a-zA-Z]+)+$", description="Platform identifier", min_length=1
    )
    package: str = Field(..., pattern=r"^([A-Za-z]+)$", description="Package name", min_length=1)
    description: str = Field(..., pattern=r"^(.|\s)*$", description="Event description", min_length=1)
    event_receiver_id: str = Field(..., pattern=r"^([0-9A-Za-z]{26})$", description="Event receiver ID", min_length=1)
    success: bool = Field(..., description="Success status")
    payload: Dict[str, Any] = Field(..., description="Event payload data")

    @field_validator(
        "name", "version", "release", "platform_id", "package", "description", "event_receiver_id", mode="before"
    )
    @classmethod
    def strip_whitespace(cls, v):
        """Strip whitespace from string fields"""
        if isinstance(v, str):
            stripped = v.strip()
            return stripped if stripped else v  # Don't convert to None for required fields
        return v

    @field_validator("payload", mode="before")
    @classmethod
    def validate_payload(cls, v):
        if not isinstance(v, dict):
            raise ValidationError("Payload must be a dictionary")
        return _sanitize_dict(v)


class EventReceiverCreateInput(BaseModel):
    """Schema for event receiver creation input"""

    name: str = Field(
        ...,
        pattern=r"^[A-Za-z0-9]+([._-]?[A-Za-z0-9]+)*(/[A-Za-z0-9]+([._-]?[A-Za-z0-9]+)*)*$",
        description="Name of the event receiver",
        min_length=1,
    )
    type: str = Field(..., pattern=r"^[^ ]+$", description="Type of the event receiver", min_length=1)
    version: str = Field(
        ...,
        pattern=r"([0-9]+)(\\.[0-9]+)?(\\.[0-9]+)?(-([0-9A-Za-z\\-]+(\\.[0-9A-Za-z\\-]+)*))?(\\+([0-9A-Za-z\\-]+(\\.[0-9A-Za-z\\-]+)*))?",
        description="Version of the event receiver",
        min_length=1,
    )
    description: str = Field(..., pattern=r"^(.|\s)*$", description="Event receiver description", min_length=1)

    @field_validator("name", "type", "version", "description", mode="before")
    @classmethod
    def strip_whitespace(cls, v):
        """Strip whitespace from string fields"""
        if isinstance(v, str):
            stripped = v.strip()
            return stripped if stripped else v  # Don't convert to None for required fields
        return v


class EventReceiverGroupCreateInput(BaseModel):
    """Schema for event receiver group creation input"""

    name: str = Field(
        ...,
        pattern=r"^[A-Za-z0-9]+([._-]?[A-Za-z0-9]+)*(/[A-Za-z0-9]+([._-]?[A-Za-z0-9]+)*)*$",
        description="Name of the event receiver group",
        min_length=1,
    )
    type: str = Field(..., pattern=r"^[^ ]+$", description="Type of the event receiver group", min_length=1)
    version: str = Field(
        ...,
        pattern=r"([0-9]+)(\\.[0-9]+)?(\\.[0-9]+)?(-([0-9A-Za-z\\-]+(\\.[0-9A-Za-z\\-]+)*))?(\\+([0-9A-Za-z\\-]+(\\.[0-9A-Za-z\\-]+)*))?",
        description="Version of the event receiver group",
        min_length=1,
    )
    description: str = Field(..., pattern=r"^(.|\s)*$", description="Event receiver group description", min_length=1)
    event_receiver_ids: List[str] = Field(..., description="List of event receiver IDs")

    @field_validator("name", "type", "version", "description", mode="before")
    @classmethod
    def strip_whitespace(cls, v):
        """Strip whitespace from string fields"""
        if isinstance(v, str):
            stripped = v.strip()
            return stripped if stripped else v  # Don't convert to None for required fields
        return v

    @field_validator("event_receiver_ids")
    @classmethod
    def validate_event_receiver_ids(cls, v):
        if not v:  # Check if list is empty
            raise ValidationError("Event receiver IDs list cannot be empty")

        # Strip whitespace from each ID and validate
        sanitized_ids = []
        ulid_pattern = re.compile(r"^([0-9A-Za-z]{26})$")
        for id_str in v:
            if not isinstance(id_str, str):
                raise ValidationError("All event receiver IDs must be strings")

            stripped_id = id_str.strip()
            if len(stripped_id) == 0:
                raise ValidationError("All event receiver IDs must be non-empty strings")

            if not ulid_pattern.match(stripped_id):
                raise ValidationError(
                    f'Event receiver ID "{stripped_id}" must be a valid ULID (26 alphanumeric characters)'
                )

            sanitized_ids.append(stripped_id)

        return sanitized_ids


class EventCreateDataWrapper(BaseModel):
    """Wrapper for event creation data input"""

    data: EventCreateInput = Field(..., description="Event creation data")


class EventReceiverCreateDataWrapper(BaseModel):
    """Wrapper for event receiver creation data input"""

    data: EventReceiverCreateInput = Field(..., description="Event receiver creation data")


class EventReceiverGroupCreateDataWrapper(BaseModel):
    """Wrapper for event receiver group creation data input"""

    data: EventReceiverGroupCreateInput = Field(..., description="Event receiver group creation data")


class FetchInput(BaseModel):
    """Schema for fetch operations input"""

    id: str = Field(..., pattern=r"^([0-9A-Za-z]{26})$", description="Resource ID to fetch (ULID)", min_length=1)

    @field_validator("id")
    @classmethod
    def validate_id(cls, v):
        if not v or not v.strip():
            raise ValidationError("ID cannot be empty")
        return v.strip()


# Response validation models
class EventResponse(BaseModel):
    """Schema for validating event response data"""

    model_config = {"populate_by_name": True}

    id: str = Field(..., pattern=r"^([0-9A-Za-z]{26})$", description="Event ID (ULID)")
    name: str = Field(
        ...,
        pattern=r"^[A-Za-z0-9]+([._-]?[A-Za-z0-9]+)*(/[A-Za-z0-9]+([._-]?[A-Za-z0-9]+)*)*$",
        description="Event name",
    )
    version: str = Field(
        ...,
        pattern=r"([0-9]+)(\\.[0-9]+)?(\\.[0-9]+)?(-([0-9A-Za-z\\-]+(\\.[0-9A-Za-z\\-]+)*))?(\\+([0-9A-Za-z\\-]+(\\.[0-9A-Za-z\\-]+)*))?",
        description="Event version",
    )
    release: str = Field(..., pattern=r"^\S+$", description="Release version")
    platform_id: str = Field(..., pattern=r"^([0-9a-zA-Z]+)(-[0-9a-zA-Z]+)+$", description="Platform identifier")
    package: str = Field(..., pattern=r"^([A-Za-z]+)$", description="Package name")
    description: str = Field(..., pattern=r"^(.|\s)*$", description="Event description")
    payload: Dict[str, Any] = Field(default_factory=dict, description="Event payload")
    success: bool = Field(..., description="Success status")
    created_at: Optional[str] = Field(None, description="Creation timestamp")
    event_receiver_id: str = Field(..., pattern=r"^([0-9A-Za-z]{26})$", description="Event receiver ID (ULID)")
    event_receiver: Dict[str, Any] = Field(
        default_factory=dict, description="Event receiver data", alias="EventReceiver"
    )

    @field_validator("payload", "event_receiver")
    @classmethod
    def validate_dict_fields(cls, v):
        if v is None:
            return {}
        if not isinstance(v, dict):
            raise ValidationError("Field must be a dictionary")
        return v


class EventReceiverResponse(BaseModel):
    """Schema for validating event receiver response data"""

    id: str = Field(..., pattern=r"^([0-9A-Za-z]{26})$", description="Event receiver ID (ULID)")
    name: str = Field(
        ...,
        pattern=r"^[A-Za-z0-9]+([._-]?[A-Za-z0-9]+)*(/[A-Za-z0-9]+([._-]?[A-Za-z0-9]+)*)*$",
        description="Event receiver name",
    )
    type: str = Field(..., pattern=r"^[^ ]+$", description="Event receiver type")
    version: str = Field(
        ...,
        pattern=r"([0-9]+)(\\.[0-9]+)?(\\.[0-9]+)?(-([0-9A-Za-z\\-]+(\\.[0-9A-Za-z\\-]+)*))?(\\+([0-9A-Za-z\\-]+(\\.[0-9A-Za-z\\-]+)*))?",
        description="Event receiver version",
    )
    description: str = Field(..., pattern=r"^(.|\s)*$", description="Event receiver description")
    schema_data: Dict[str, Any] = Field(default_factory=dict, description="Event receiver schema", alias="schema")
    fingerprint: Optional[str] = Field(
        None, pattern=r"^([A-Fa-f0-9]{64})$", description="Event receiver fingerprint (SHA256)"
    )
    created_at: Optional[str] = Field(None, description="Creation timestamp")

    @field_validator("schema_data")
    @classmethod
    def validate_schema_field(cls, v):
        if v is None:
            return {}
        if not isinstance(v, dict):
            raise ValidationError("Schema must be a dictionary")
        return v


class EventReceiverGroupResponse(BaseModel):
    """Schema for validating event receiver group response data"""

    id: str = Field(..., pattern=r"^([0-9A-Za-z]{26})$", description="Event receiver group ID (ULID)")
    name: str = Field(
        ...,
        pattern=r"^[A-Za-z0-9]+([._-]?[A-Za-z0-9]+)*(/[A-Za-z0-9]+([._-]?[A-Za-z0-9]+)*)*$",
        description="Event receiver group name",
    )
    type: str = Field(..., pattern=r"^[^ ]+$", description="Event receiver group type")
    version: str = Field(
        ...,
        pattern=r"([0-9]+)(\\.[0-9]+)?(\\.[0-9]+)?(-([0-9A-Za-z\\-]+(\\.[0-9A-Za-z\\-]+)*))?(\\+([0-9A-Za-z\\-]+(\\.[0-9A-Za-z\\-]+)*))?",
        description="Event receiver group version",
    )
    description: str = Field(..., pattern=r"^(.|\s)*$", description="Event receiver group description")
    enabled: bool = Field(default=True, description="Group enabled status")
    event_receiver_ids: List[str] = Field(default_factory=list, description="List of event receiver IDs")
    fingerprint: Optional[str] = Field(
        None, pattern=r"^([A-Fa-f0-9]{64})$", description="Event receiver group fingerprint (SHA256)"
    )
    created_at: Optional[str] = Field(None, description="Creation timestamp")
    updated_at: Optional[str] = Field(None, description="Last update timestamp")

    @field_validator("event_receiver_ids")
    @classmethod
    def validate_event_receiver_ids(cls, v):
        if v is None:
            return []
        if not isinstance(v, list):
            raise ValidationError("Event receiver IDs must be a list")

        # Strip whitespace from each ID and validate
        sanitized_ids = []
        ulid_pattern = re.compile(r"^([0-9A-Za-z]{26})$")
        for id_str in v:
            if not isinstance(id_str, str):
                raise ValidationError("All event receiver IDs must be strings")

            stripped_id = id_str.strip()
            if not ulid_pattern.match(stripped_id):
                raise ValidationError(
                    f'Event receiver ID "{stripped_id}" must be a valid ULID (26 alphanumeric characters)'
                )

            sanitized_ids.append(stripped_id)

        return sanitized_ids


# Schema mapping for different operations
SCHEMA_MAP = {
    # Search operations
    "search_events": SearchDataWrapper,
    "search_receivers": SearchDataWrapper,
    "search_groups": SearchDataWrapper,
    # Create operations
    "create_event": EventCreateDataWrapper,
    "create_receiver": EventReceiverCreateDataWrapper,
    "create_group": EventReceiverGroupCreateDataWrapper,
    # Fetch operations
    "fetch_event": FetchInput,
    "fetch_receiver": FetchInput,
    "fetch_group": FetchInput,
}


def _sanitize_string(value: Any) -> Any:
    """
    Sanitize string values by stripping leading/trailing whitespace.

    Args:
        value: The value to sanitize

    Returns:
        Sanitized value (stripped if string, unchanged otherwise)
    """
    if isinstance(value, str):
        return value.strip()
    return value


def _sanitize_dict(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Recursively sanitize dictionary values by stripping whitespace from strings.

    Args:
        data: Dictionary to sanitize

    Returns:
        Sanitized dictionary with string values stripped
    """
    if data is None:
        return None

    sanitized = {}
    for key, value in data.items():
        if isinstance(value, str):
            sanitized[key] = value.strip()
        elif isinstance(value, dict):
            sanitized[key] = _sanitize_dict(value)
        elif isinstance(value, list):
            sanitized[key] = [_sanitize_string(item) if isinstance(item, str) else item for item in value]
        else:
            sanitized[key] = value
    return sanitized


def validate_input(operation: str, input_data: Union[str, Dict[str, Any]]) -> Dict[str, Any]:
    """
    Validate input data for a given operation.

    Args:
        operation: The operation name (e.g., 'search_events', 'create_event')
        input_data: The input data to validate

    Returns:
        Validated data as a dictionary

    Raises:
        ValidationError: If the operation is not supported or input data doesn't match the schema
    """
    if operation not in SCHEMA_MAP:
        raise ValidationError(f"Unsupported operation: {operation}")

    schema_class = SCHEMA_MAP[operation]

    # For fetch operations, the input is just an ID string
    if operation.startswith("fetch_"):
        # Sanitize string input by stripping whitespace
        sanitized_input = _sanitize_string(input_data)
        validated = schema_class(id=sanitized_input)
        return {"id": validated.id}

    # For other operations, validate the full structure
    if not isinstance(input_data, dict):
        raise ValidationError(f"Input data for {operation} must be a dictionary")

    # Sanitize dictionary inputs before validation
    sanitized_data = _sanitize_dict(input_data)
    validated = schema_class(**sanitized_data)
    return validated.dict()


def get_validation_schema(operation: str) -> BaseModel:
    """
    Get the validation schema class for a given operation.

    Args:
        operation: The operation name

    Returns:
        The Pydantic model class for validation

    Raises:
        ValidationError: If the operation is not supported
    """
    if operation not in SCHEMA_MAP:
        raise ValidationError(f"Unsupported operation: {operation}")

    return SCHEMA_MAP[operation]


def validate_event_response(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate event response data from EPR API.

    Args:
        data: Raw response data from API

    Returns:
        Validated event data as dictionary

    Raises:
        ValidationError: If data doesn't match expected schema
    """
    try:
        validated = EventResponse(**data)
        return validated.model_dump(by_alias=True)
    except ValidationError as e:
        raise ValidationError(f"Event response validation failed: {e!s}") from e


def validate_event_receiver_response(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate event receiver response data from EPR API.

    Args:
        data: Raw response data from API

    Returns:
        Validated event receiver data as dictionary

    Raises:
        ValidationError: If data doesn't match expected schema
    """
    try:
        validated = EventReceiverResponse(**data)
        return validated.model_dump(by_alias=True)
    except ValidationError as e:
        raise ValidationError(f"Event receiver response validation failed: {e!s}") from e


def validate_event_receiver_group_response(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate event receiver group response data from EPR API.

    Args:
        data: Raw response data from API

    Returns:
        Validated event receiver group data as dictionary

    Raises:
        ValidationError: If data doesn't match expected schema
    """
    try:
        validated = EventReceiverGroupResponse(**data)
        return validated.model_dump(by_alias=True)
    except ValidationError as e:
        raise ValidationError(f"Event receiver group response validation failed: {e!s}") from e


def validate_event_list_response(data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Validate list of events response data from EPR API.

    Args:
        data: Raw list of event data from API

    Returns:
        Validated list of event data

    Raises:
        ValidationError: If any event doesn't match expected schema
    """
    try:
        return [validate_event_response(event) for event in data]
    except ValidationError as e:
        raise ValidationError(f"Event list response validation failed: {e!s}") from e


def validate_event_receiver_list_response(data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Validate list of event receivers response data from EPR API.

    Args:
        data: Raw list of event receiver data from API

    Returns:
        Validated list of event receiver data

    Raises:
        ValidationError: If any receiver doesn't match expected schema
    """
    try:
        return [validate_event_receiver_response(receiver) for receiver in data]
    except ValidationError as e:
        raise ValidationError(f"Event receiver list response validation failed: {e!s}") from e


def validate_event_receiver_group_list_response(data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Validate list of event receiver groups response data from EPR API.

    Args:
        data: Raw list of event receiver group data from API

    Returns:
        Validated list of event receiver group data

    Raises:
        ValidationError: If any group doesn't match expected schema
    """
    try:
        return [validate_event_receiver_group_response(group) for group in data]
    except ValidationError as e:
        raise ValidationError(f"Event receiver group list response validation failed: {e!s}") from e
