"""Unit tests for epr_mcp.schemas module."""

import pytest  # type: ignore
from pydantic import ValidationError

from epr_mcp.schemas import (
    EventCreateInput,
    EventSearchInput,
    _sanitize_dict,
    _sanitize_string,
)


class TestSanitizationFunctions:
    """Test sanitization helper functions."""

    def test_sanitize_string_strips_whitespace(self):
        """Test that _sanitize_string removes leading/trailing whitespace."""
        assert _sanitize_string("  hello  ") == "hello"
        assert _sanitize_string("\n\tworld\n") == "world"
        assert _sanitize_string("") == ""
        assert _sanitize_string("   ") == ""

    def test_sanitize_string_handles_none(self):
        """Test that _sanitize_string handles None values."""
        assert _sanitize_string(None) is None

    def test_sanitize_string_handles_non_strings(self):
        """Test that _sanitize_string passes through non-string values."""
        assert _sanitize_string(123) == 123
        assert _sanitize_string(True) is True
        assert _sanitize_string([1, 2, 3]) == [1, 2, 3]

    def test_sanitize_dict_recursive(self):
        """Test that _sanitize_dict recursively sanitizes string values."""
        input_dict = {
            "name": "  test  ",
            "nested": {
                "value": "  nested_value  ",
                "number": 42,
            },
            "list": ["  item1  ", "item2", 123],
        }

        expected = {
            "name": "test",
            "nested": {
                "value": "nested_value",
                "number": 42,
            },
            "list": ["item1", "item2", 123],
        }

        result = _sanitize_dict(input_dict)
        assert result == expected

    def test_sanitize_dict_handles_none(self):
        """Test that _sanitize_dict handles None input gracefully."""
        # Type ignore needed for testing edge case where None is passed
        # This tests the defensive programming in the function
        result = _sanitize_dict(None)  # type: ignore
        assert result is None

    def test_sanitize_dict_handles_empty_strings(self):
        """Test that _sanitize_dict converts whitespace-only strings to empty strings."""
        input_dict = {"empty": "   ", "value": "test"}
        result = _sanitize_dict(input_dict)
        assert result == {"empty": "", "value": "test"}


class TestEventSearchInput:
    """Test EventSearchInput schema validation and sanitization."""

    def test_whitespace_sanitization(self):
        """Test that whitespace is stripped from input fields."""
        data = {
            "name": "  test-event  ",
            "version": "  1.0.0  ",
            "release": "  stable  ",
            "platform_id": "  plat-form-123  ",
            "package": "  TestPackage  ",
            "description": "  A test event  ",
            "success": None,
            "event_receiver_id": "  01ARZ3NDEKTSV4RRFFQ69G5FAV  ",
        }

        schema = EventSearchInput(**data)
        assert schema.name == "test-event"
        assert schema.version == "1.0.0"
        assert schema.release == "stable"
        assert schema.platform_id == "plat-form-123"
        assert schema.package == "TestPackage"
        assert schema.description == "A test event"
        assert schema.event_receiver_id == "01ARZ3NDEKTSV4RRFFQ69G5FAV"

    def test_empty_string_handling(self):
        """Test that empty strings after stripping are converted to None."""
        data = {
            "name": "   ",
            "version": "1.0.0",
            "success": True,
        }

        schema = EventSearchInput(**data)
        assert schema.name is None
        assert schema.version == "1.0.0"

    def test_invalid_patterns(self):
        """Test that invalid patterns raise ValidationError."""
        # Note: Using keyword arguments to satisfy type checker
        with pytest.raises(ValidationError):
            EventSearchInput(
                name="invalid name with spaces",
                version=None,
                release=None,
                platform_id=None,
                package=None,
                description=None,
                success=None,
                event_receiver_id=None,
            )

    def test_all_optional_fields(self):
        """Test that all fields are optional."""
        # Create with no arguments - all should default to None
        schema = EventSearchInput(
            name=None,
            version=None,
            release=None,
            platform_id=None,
            package=None,
            description=None,
            success=None,
            event_receiver_id=None,
        )
        assert schema.name is None
        assert schema.version is None
        assert schema.success is None

    def test_valid_patterns(self):
        """Test that valid patterns are accepted."""
        valid_data = {
            "name": "valid-event_name",
            "version": "1.2.3-alpha.1+build.123",
            "platform_id": "platform-id-123",
            "package": "ValidPackage",
            "event_receiver_id": "01ARZ3NDEKTSV4RRFFQ69G5FAV",
            "success": True,
        }

        schema = EventSearchInput(**valid_data)
        assert schema.name == "valid-event_name"
        assert schema.version == "1.2.3-alpha.1+build.123"
        assert schema.platform_id == "platform-id-123"


class TestEventCreateInput:
    """Test EventCreateInput schema validation and sanitization."""

    def test_required_fields_validation(self):
        """Test that required fields are validated."""
        # Test with minimal required fields
        minimal_data = {
            "name": "test-event",
            "version": "1.0.0",
            "release": "stable",
            "platform_id": "plat-123",
            "package": "Package",
            "description": "Test description",
            "event_receiver_id": "01ARZ3NDEKTSV4RRFFQ69G5FAV",
            "success": True,
            "payload": {"key": "value"},
        }

        schema = EventCreateInput(**minimal_data)
        assert schema.name == "test-event"
        assert schema.success is True
        assert schema.payload == {"key": "value"}

    def test_payload_sanitization(self):
        """Test that payload dictionary is sanitized."""
        data = {
            "name": "test-event",
            "version": "1.0.0",
            "release": "stable",
            "platform_id": "plat-123",
            "package": "Package",
            "description": "Test description",
            "event_receiver_id": "01ARZ3NDEKTSV4RRFFQ69G5FAV",
            "success": True,
            "payload": {
                "key1": "  value1  ",
                "nested": {
                    "key2": "  value2  ",
                },
            },
        }

        schema = EventCreateInput(**data)
        assert schema.payload["key1"] == "value1"
        assert schema.payload["nested"]["key2"] == "value2"

    def test_ulid_pattern_validation(self):
        """Test ULID pattern validation works correctly."""
        valid_ulid = "01ARZ3NDEKTSV4RRFFQ69G5FAV"
        invalid_ulid = "invalid_ulid"

        # Valid ULID should work
        valid_data = {
            "name": "test-event",
            "version": "1.0.0",
            "release": "stable",
            "platform_id": "plat-123",
            "package": "Package",
            "description": "Test description",
            "event_receiver_id": f"  {valid_ulid}  ",  # Test with whitespace
            "success": True,
            "payload": {"key": "value"},
        }
        result = EventCreateInput(**valid_data)
        assert result.event_receiver_id == valid_ulid

        # Invalid ULID should raise ValidationError
        invalid_data = {
            "name": "test-event",
            "version": "1.0.0",
            "release": "stable",
            "platform_id": "plat-123",
            "package": "Package",
            "description": "Test description",
            "event_receiver_id": invalid_ulid,
            "success": True,
            "payload": {"key": "value"},
        }
        with pytest.raises(ValidationError):
            EventCreateInput(**invalid_data)


class TestSchemaIntegration:
    """Test integration scenarios with schemas."""

    def test_model_dump_functionality(self):
        """Test that schemas can be converted to dictionaries."""
        data = {
            "name": "test",
            "version": "1.0.0",
            "release": None,
            "platform_id": None,
            "package": None,
            "description": None,
            "success": None,
            "event_receiver_id": None,
        }
        result = EventSearchInput(**data)
        result_dict = result.model_dump()

        assert result_dict["name"] == "test"
        assert result_dict["version"] == "1.0.0"
        # Check that None values are included in the dump
        assert "success" in result_dict
        assert result_dict["success"] is None

    def test_empty_input_handling(self):
        """Test handling of empty input data."""
        # Explicitly pass None values to satisfy type checker
        result = EventSearchInput(
            name=None,
            version=None,
            release=None,
            platform_id=None,
            package=None,
            description=None,
            success=None,
            event_receiver_id=None,
        )

        # All fields should be None for empty input
        assert result.name is None
        assert result.version is None
        assert result.success is None
        assert result.event_receiver_id is None

    def test_partial_data_validation(self):
        """Test validation with partial data."""
        data = {
            "name": "test-event",
            "success": True,
        }

        result = EventSearchInput(**data)
        assert result.name == "test-event"
        assert result.success is True
        assert result.version is None
        assert result.platform_id is None
