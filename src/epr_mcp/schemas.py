# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: © 2025 Brett Smith <xbcsmith@gmail.com>
# SPDX-License-Identifier: Apache-2.0

import re
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, ValidationError, field_validator


class EventSearchInput(BaseModel):
    """Schema for event search input"""

    model_config = {"extra": "forbid"}

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
        None, pattern=r"^([0-9a-zA-Z]+)(-[0-9a-zA-Z]+)*$", description="Platform identifier"
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
        """Strip whitespace from string fields; a blank value becomes None.

        Args:
            v: The raw field value.

        Returns:
            The stripped string, None if it was blank, or the value unchanged if it is not a string.

        Examples:
            >>> EventSearchInput(name="  foo ").name
            'foo'
            >>> EventSearchInput(name="   ").name is None
            True
        """
        if isinstance(v, str):
            stripped = v.strip()
            return stripped if stripped else None
        return v


class EventReceiverSearchInput(BaseModel):
    """Schema for event receiver search input"""

    model_config = {"extra": "forbid"}

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
        """Strip whitespace from string fields; a blank value becomes None.

        Args:
            v: The raw field value.

        Returns:
            The stripped string, None if it was blank, or the value unchanged if it is not a string.

        Examples:
            >>> EventReceiverSearchInput(name="  foo ").name
            'foo'
            >>> EventReceiverSearchInput(name="   ").name is None
            True
        """
        if isinstance(v, str):
            stripped = v.strip()
            return stripped if stripped else None
        return v


class EventReceiverGroupSearchInput(BaseModel):
    """Schema for event receiver group search input"""

    model_config = {"extra": "forbid"}

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
        """Strip whitespace from string fields; a blank value becomes None.

        Args:
            v: The raw field value.

        Returns:
            The stripped string, None if it was blank, or the value unchanged if it is not a string.

        Examples:
            >>> EventReceiverGroupSearchInput(name="  foo ").name
            'foo'
            >>> EventReceiverGroupSearchInput(name="   ").name is None
            True
        """
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

    model_config = {"extra": "forbid"}

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
        ...,
        pattern=r"^([0-9a-zA-Z]+)(-[0-9a-zA-Z]+)*$",
        description="Platform identifier",
        min_length=1,
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
        """Strip whitespace from string fields; a blank value is kept so it fails validation.

        Args:
            v: The raw field value.

        Returns:
            The stripped string, or the value unchanged if it is not a string.

        Examples:
            >>> EventCreateInput.model_validate(
            ...     {
            ...         "name": " foo ",
            ...         "version": "1.0.0",
            ...         "release": "r1",
            ...         "platform_id": "linux",
            ...         "package": "oci",
            ...         "description": "d",
            ...         "success": True,
            ...         "payload": {},
            ...         "event_receiver_id": "01JYRZ96R690ZTQ15Q53GEY6E6",
            ...     }
            ... ).name
            'foo'
        """
        if isinstance(v, str):
            stripped = v.strip()
            return stripped if stripped else v  # Don't convert to None for required fields
        return v

    @field_validator("payload", mode="before")
    @classmethod
    def validate_payload(cls, v):
        """Require the payload to be a dictionary.

        Args:
            v: The value to check.

        Returns:
            The value, unchanged.

        Examples:
            >>> EventCreateInput.model_validate(
            ...     {
            ...         "name": "foo",
            ...         "version": "1.0.0",
            ...         "release": "r1",
            ...         "platform_id": "linux",
            ...         "package": "oci",
            ...         "description": "d",
            ...         "success": True,
            ...         "payload": {"a": 1},
            ...         "event_receiver_id": "01JYRZ96R690ZTQ15Q53GEY6E6",
            ...     }
            ... ).payload
            {'a': 1}
        """
        if not isinstance(v, dict):
            raise ValidationError("Payload must be a dictionary")
        return _sanitize_dict(v)


class EventReceiverCreateInput(BaseModel):
    """Schema for event receiver creation input"""

    model_config = {"extra": "forbid", "populate_by_name": True}

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
    schema_data: Dict[str, Any] = Field(
        ..., alias="schema", description="JSON schema that event payloads sent to this receiver must match"
    )

    @field_validator("name", "type", "version", "description", mode="before")
    @classmethod
    def strip_whitespace(cls, v):
        """Strip whitespace from string fields; a blank value is kept so it fails validation.

        Args:
            v: The raw field value.

        Returns:
            The stripped string, or the value unchanged if it is not a string.

        Examples:
            >>> EventReceiverCreateInput.model_validate(
            ...     {"name": " foo ", "type": "t", "version": "1.0.0", "description": "d", "schema": {}}
            ... ).name
            'foo'
        """
        if isinstance(v, str):
            stripped = v.strip()
            return stripped if stripped else v  # Don't convert to None for required fields
        return v


class EventReceiverGroupCreateInput(BaseModel):
    """Schema for event receiver group creation input"""

    model_config = {"extra": "forbid"}

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
        """Strip whitespace from string fields; a blank value is kept so it fails validation.

        Args:
            v: The raw field value.

        Returns:
            The stripped string, or the value unchanged if it is not a string.

        Examples:
            >>> EventReceiverGroupCreateInput.model_validate(
            ...     {
            ...         "name": " foo ",
            ...         "type": "t",
            ...         "version": "1.0.0",
            ...         "description": "d",
            ...         "event_receiver_ids": ["01JYRZ96R690ZTQ15Q53GEY6E6"],
            ...     }
            ... ).name
            'foo'
        """
        if isinstance(v, str):
            stripped = v.strip()
            return stripped if stripped else v  # Don't convert to None for required fields
        return v

    @field_validator("event_receiver_ids")
    @classmethod
    def validate_event_receiver_ids(cls, v):
        """Strip each receiver ID and require it to be a 26 character ULID.

        Args:
            v: The list of receiver IDs.

        Returns:
            The cleaned list of IDs.

        Raises:
            ValueError: If the list is empty or an ID is not a valid ULID.

        Examples:
            >>> EventReceiverGroupCreateInput.model_validate(
            ...     {
            ...         "name": "foo",
            ...         "type": "t",
            ...         "version": "1.0.0",
            ...         "description": "d",
            ...         "event_receiver_ids": [" 01JYRZ96R690ZTQ15Q53GEY6E6 "],
            ...     }
            ... ).event_receiver_ids
            ['01JYRZ96R690ZTQ15Q53GEY6E6']
        """
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
        """Strip the ID and reject an empty one.

        Args:
            v: The ID to check.

        Returns:
            The ID without surrounding whitespace.

        Examples:
            >>> FetchInput(id="01JYRZ96R690ZTQ15Q53GEY6E6").id
            '01JYRZ96R690ZTQ15Q53GEY6E6'
        """
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
    platform_id: str = Field(..., pattern=r"^([0-9a-zA-Z]+)(-[0-9a-zA-Z]+)*$", description="Platform identifier")
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
        """Turn a missing value into an empty dictionary and reject other non-dictionaries.

        Args:
            v: The value to check.

        Returns:
            A dictionary.

        Examples:
            >>> EventResponse.model_validate(
            ...     {
            ...         "id": "01JYRZ96R690ZTQ15Q53GEY6E6",
            ...         "name": "foo",
            ...         "version": "1.0.0",
            ...         "release": "r1",
            ...         "platform_id": "linux",
            ...         "package": "oci",
            ...         "description": "d",
            ...         "success": True,
            ...         "event_receiver_id": "01JYRZ96R690ZTQ15Q53GEY6E6",
            ...     }
            ... ).payload
            {}
        """
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
        """Turn a missing schema into an empty dictionary and reject other non-dictionaries.

        Args:
            v: The value to check.

        Returns:
            A dictionary.

        Examples:
            >>> EventReceiverResponse.model_validate(
            ...     {
            ...         "id": "01JYRZ96R690ZTQ15Q53GEY6E6",
            ...         "name": "foo",
            ...         "type": "foo.type",
            ...         "version": "1.0.0",
            ...         "description": "d",
            ...     }
            ... ).schema_data
            {}
        """
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
        """Strip each receiver ID and require it to be a 26 character ULID.

        Args:
            v: The list of receiver IDs.

        Returns:
            The cleaned list of IDs.

        Raises:
            ValueError: If the list is empty or an ID is not a valid ULID.

        Examples:
            >>> EventReceiverGroupCreateInput.model_validate(
            ...     {
            ...         "name": "foo",
            ...         "type": "t",
            ...         "version": "1.0.0",
            ...         "description": "d",
            ...         "event_receiver_ids": [" 01JYRZ96R690ZTQ15Q53GEY6E6 "],
            ...     }
            ... ).event_receiver_ids
            ['01JYRZ96R690ZTQ15Q53GEY6E6']
        """
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
    """Validate the arguments of a tool call.

    Args:
        operation: The tool: a ``fetch_*``, ``search_*``, or ``create_*`` name.
        input_data: An ID string for a fetch; for the others, a dictionary with a
            ``data`` key that holds the criteria or fields.

    Returns:
        The validated data as a dictionary, with field aliases applied.

    Raises:
        ValidationError: If the operation is not supported or the data does not match the schema.

    Examples:
        >>> validate_input("fetch_event", " 01JYRZ96R690ZTQ15Q53GEY6E6 ")
        {'id': '01JYRZ96R690ZTQ15Q53GEY6E6'}
        >>> validate_input("search_events", {"data": {"name": "foo"}})["data"]["name"]
        'foo'
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
    return validated.model_dump(by_alias=True)


def get_validation_schema(operation: str) -> BaseModel:
    """Get the validation schema class for a given operation.

    Args:
        operation: The operation name, for example "search_events".

    Returns:
        The Pydantic model class used to validate that operation.

    Raises:
        ValidationError: If the operation is not supported.

    Examples:
        >>> get_validation_schema("fetch_group").__name__
        'FetchInput'
    """
    if operation not in SCHEMA_MAP:
        raise ValidationError(f"Unsupported operation: {operation}")

    return SCHEMA_MAP[operation]


def validate_event_response(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate an event from the EPR API.

    Args:
        data: The raw record as returned by EPR.

    Returns:
        The validated record as a dictionary.

    Raises:
        ValueError: If the record does not match the expected schema.

    Examples:
        >>> validate_event_response(
        ...     {
        ...         "id": "01JYRZ96R690ZTQ15Q53GEY6E6",
        ...         "name": "foo",
        ...         "version": "1.0.0",
        ...         "release": "r1",
        ...         "platform_id": "linux",
        ...         "package": "oci",
        ...         "description": "d",
        ...         "success": True,
        ...         "event_receiver_id": "01JYRZ96R690ZTQ15Q53GEY6E6",
        ...     }
        ... )["name"]
        'foo'
    """
    try:
        validated = EventResponse(**data)
        return validated.model_dump(by_alias=True)
    except ValidationError as e:
        raise ValueError(f"Event response validation failed: {e!s}") from e


def validate_event_receiver_response(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate an event receiver from the EPR API.

    Args:
        data: The raw record as returned by EPR.

    Returns:
        The validated record as a dictionary.

    Raises:
        ValueError: If the record does not match the expected schema.

    Examples:
        >>> validate_event_receiver_response(
        ...     {
        ...         "id": "01JYRZ96R690ZTQ15Q53GEY6E6",
        ...         "name": "foo",
        ...         "type": "foo.type",
        ...         "version": "1.0.0",
        ...         "description": "d",
        ...     }
        ... )["name"]
        'foo'
    """
    try:
        validated = EventReceiverResponse(**data)
        return validated.model_dump(by_alias=True)
    except ValidationError as e:
        raise ValueError(f"Event receiver response validation failed: {e!s}") from e


def validate_event_receiver_group_response(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate an event receiver group from the EPR API.

    Args:
        data: The raw record as returned by EPR.

    Returns:
        The validated record as a dictionary.

    Raises:
        ValueError: If the record does not match the expected schema.

    Examples:
        >>> validate_event_receiver_group_response(
        ...     {
        ...         "id": "01JYRZ96R690ZTQ15Q53GEY6E6",
        ...         "name": "foo",
        ...         "type": "foo.type",
        ...         "version": "1.0.0",
        ...         "description": "d",
        ...     }
        ... )["name"]
        'foo'
    """
    try:
        validated = EventReceiverGroupResponse(**data)
        return validated.model_dump(by_alias=True)
    except ValidationError as e:
        raise ValueError(f"Event receiver group response validation failed: {e!s}") from e


def validate_event_list_response(data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Validate a list of events from the EPR API.

    Args:
        data: The list of raw records as returned by EPR.

    Returns:
        The validated records as a list of dictionaries.

    Raises:
        ValueError: If any record does not match the expected schema.

    Examples:
        >>> [
        ...     r["name"]
        ...     for r in validate_event_list_response(
        ...         [
        ...             {
        ...                 "id": "01JYRZ96R690ZTQ15Q53GEY6E6",
        ...                 "name": "foo",
        ...                 "version": "1.0.0",
        ...                 "release": "r1",
        ...                 "platform_id": "linux",
        ...                 "package": "oci",
        ...                 "description": "d",
        ...                 "success": True,
        ...                 "event_receiver_id": "01JYRZ96R690ZTQ15Q53GEY6E6",
        ...             }
        ...         ]
        ...     )
        ... ]
        ['foo']
    """
    try:
        return [validate_event_response(event) for event in data]
    except (ValidationError, ValueError) as e:
        raise ValueError(f"Event list response validation failed: {e!s}") from e


def validate_event_receiver_list_response(data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Validate a list of event receivers from the EPR API.

    Args:
        data: The list of raw records as returned by EPR.

    Returns:
        The validated records as a list of dictionaries.

    Raises:
        ValueError: If any record does not match the expected schema.

    Examples:
        >>> [
        ...     r["name"]
        ...     for r in validate_event_receiver_list_response(
        ...         [
        ...             {
        ...                 "id": "01JYRZ96R690ZTQ15Q53GEY6E6",
        ...                 "name": "foo",
        ...                 "type": "foo.type",
        ...                 "version": "1.0.0",
        ...                 "description": "d",
        ...             }
        ...         ]
        ...     )
        ... ]
        ['foo']
    """
    try:
        return [validate_event_receiver_response(receiver) for receiver in data]
    except (ValidationError, ValueError) as e:
        raise ValueError(f"Event receiver list response validation failed: {e!s}") from e


def validate_event_receiver_group_list_response(data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Validate a list of event receiver groups from the EPR API.

    Args:
        data: The list of raw records as returned by EPR.

    Returns:
        The validated records as a list of dictionaries.

    Raises:
        ValueError: If any record does not match the expected schema.

    Examples:
        >>> [
        ...     r["name"]
        ...     for r in validate_event_receiver_group_list_response(
        ...         [
        ...             {
        ...                 "id": "01JYRZ96R690ZTQ15Q53GEY6E6",
        ...                 "name": "foo",
        ...                 "type": "foo.type",
        ...                 "version": "1.0.0",
        ...                 "description": "d",
        ...             }
        ...         ]
        ...     )
        ... ]
        ['foo']
    """
    try:
        return [validate_event_receiver_group_response(group) for group in data]
    except (ValidationError, ValueError) as e:
        raise ValueError(f"Event receiver group list response validation failed: {e!s}") from e
