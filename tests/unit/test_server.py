"""Unit tests for epr_mcp.server module."""

from epr_mcp.server import filter_none_values


class TestFilterNoneValues:
    """Test filter_none_values function."""

    def test_filter_none_values_removes_none(self):
        """Test that None values are filtered out."""
        input_data = {
            "name": "foo",
            "version": "1.0.0",
            "release": None,
            "platform_id": None,
            "package": None,
            "description": None,
            "success": None,
            "event_receiver_id": None,
        }

        expected = {
            "name": "foo",
            "version": "1.0.0",
        }

        result = filter_none_values(input_data)
        assert result == expected

    def test_filter_none_values_preserves_non_none(self):
        """Test that non-None values are preserved."""
        input_data = {
            "name": "test",
            "version": "2.0.0",
            "success": True,
            "description": "test description",
            "platform_id": "linux-x64",
        }

        result = filter_none_values(input_data)
        assert result == input_data

    def test_filter_none_values_empty_dict(self):
        """Test with empty dictionary."""
        result = filter_none_values({})
        assert result == {}

    def test_filter_none_values_all_none(self):
        """Test with dictionary containing only None values."""
        input_data = {
            "field1": None,
            "field2": None,
            "field3": None,
        }

        result = filter_none_values(input_data)
        assert result == {}

    def test_filter_none_values_preserves_falsy_non_none(self):
        """Test that falsy but non-None values are preserved."""
        input_data = {
            "name": "",
            "version": "1.0.0",
            "success": False,
            "count": 0,
            "tags": [],
            "metadata": {},
            "description": None,
        }

        expected = {
            "name": "",
            "version": "1.0.0",
            "success": False,
            "count": 0,
            "tags": [],
            "metadata": {},
        }

        result = filter_none_values(input_data)
        assert result == expected

    def test_filter_none_values_mixed_types(self):
        """Test with various data types."""
        input_data = {
            "string": "hello",
            "integer": 42,
            "float": 3.14,
            "boolean": True,
            "list": [1, 2, 3],
            "dict": {"key": "value"},
            "none_field": None,
        }

        expected = {
            "string": "hello",
            "integer": 42,
            "float": 3.14,
            "boolean": True,
            "list": [1, 2, 3],
            "dict": {"key": "value"},
        }

        result = filter_none_values(input_data)
        assert result == expected
