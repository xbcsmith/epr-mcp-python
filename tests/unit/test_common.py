"""Unit tests for epr_mcp.common module."""

import pytest  # type: ignore

from epr_mcp.common import get_mutation_query, get_operation, get_search_query
from epr_mcp.models import GraphQLQuery


class TestGetOperation:
    """Test get_operation function."""

    def test_search_operations(self):
        """Test search operation mappings."""
        assert get_operation("search", "events") == "FindEventInput!"
        assert get_operation("search", "event_receivers") == "FindEventReceiverInput!"
        assert get_operation("search", "event_receiver_groups") == "FindEventReceiverGroupInput!"

    def test_mutation_operations(self):
        """Test mutation operation mappings."""
        assert get_operation("mutation", "create_event") == "CreateEventInput!"
        assert get_operation("mutation", "create_event_receiver") == "CreateEventReceiverInput!"
        assert get_operation("mutation", "create_event_receiver_group") == "CreateEventReceiverGroupInput!"

    def test_operation_mappings(self):
        """Test operation name mappings."""
        assert get_operation("operation", "events") == "event"
        assert get_operation("operation", "event_receivers") == "event_receiver"
        assert get_operation("operation", "event_receiver_groups") == "event_receiver_group"

    def test_create_mappings(self):
        """Test create operation mappings."""
        assert get_operation("create", "create_event") == "event"
        assert get_operation("create", "create_event_receiver") == "event_receiver"
        assert get_operation("create", "create_event_receiver_group") == "event_receiver_group"

    def test_invalid_operation_name(self):
        """Test that invalid operation name raises KeyError."""
        with pytest.raises(KeyError):
            get_operation("invalid", "events")

    def test_invalid_operation_type(self):
        """Test that invalid operation type raises KeyError."""
        with pytest.raises(KeyError):
            get_operation("search", "invalid")


class TestGetSearchQuery:
    """Test get_search_query function."""

    def test_basic_search_query(self):
        """Test basic search query generation."""
        result = get_search_query("events")

        assert isinstance(result, GraphQLQuery)
        assert "query" in result.query
        assert "FindEventInput!" in result.query
        assert "events(event: $obj)" in result.query
        assert "id" in result.query
        assert result.variables == {"obj": None}

    def test_search_query_with_params(self):
        """Test search query with parameters."""
        params = {"name": "test-event", "version": "1.0.0"}
        result = get_search_query("events", params=params)

        assert isinstance(result, GraphQLQuery)
        assert result.variables == {"obj": params}

    def test_search_query_with_fields(self):
        """Test search query with custom fields."""
        fields = ["id", "name", "version", "created_at"]
        result = get_search_query("events", fields=fields)

        assert isinstance(result, GraphQLQuery)
        assert "id,name,version,created_at" in result.query

    def test_search_query_with_params_and_fields(self):
        """Test search query with both parameters and fields."""
        params = {"name": "test-event"}
        fields = ["id", "name", "description"]
        result = get_search_query("events", params=params, fields=fields)

        assert isinstance(result, GraphQLQuery)
        assert result.variables == {"obj": params}
        assert "id,name,description" in result.query

    def test_search_query_event_receivers(self):
        """Test search query for event receivers."""
        result = get_search_query("event_receivers")

        assert "FindEventReceiverInput!" in result.query
        assert "event_receivers(event_receiver: $obj)" in result.query

    def test_search_query_event_receiver_groups(self):
        """Test search query for event receiver groups."""
        result = get_search_query("event_receiver_groups")

        assert "FindEventReceiverGroupInput!" in result.query
        assert "event_receiver_groups(event_receiver_group: $obj)" in result.query

    def test_search_query_empty_fields_list(self):
        """Test search query with empty fields list."""
        result = get_search_query("events", fields=[])

        # Empty fields should result in empty string, not "id"
        assert " {  }" in result.query

    def test_search_query_none_params(self):
        """Test search query with explicit None params."""
        result = get_search_query("events", params=None)

        assert result.variables == {"obj": None}


class TestGetMutationQuery:
    """Test get_mutation_query function."""

    def test_basic_mutation_query(self):
        """Test basic mutation query generation."""
        result = get_mutation_query("create_event")

        assert isinstance(result, GraphQLQuery)
        assert "mutation" in result.query
        assert "CreateEventInput!" in result.query
        assert "create_event(event: $obj)" in result.query
        assert result.variables == {"obj": None}

    def test_mutation_query_with_params(self):
        """Test mutation query with parameters."""
        params = {"name": "test-event", "version": "1.0.0", "description": "Test event"}
        result = get_mutation_query("create_event", params=params)

        assert isinstance(result, GraphQLQuery)
        assert result.variables == {"obj": params}

    def test_mutation_query_create_event_receiver(self):
        """Test mutation query for creating event receiver."""
        result = get_mutation_query("create_event_receiver")

        assert "CreateEventReceiverInput!" in result.query
        assert "create_event_receiver(event_receiver: $obj)" in result.query

    def test_mutation_query_create_event_receiver_group(self):
        """Test mutation query for creating event receiver group."""
        result = get_mutation_query("create_event_receiver_group")

        assert "CreateEventReceiverGroupInput!" in result.query
        assert "create_event_receiver_group(event_receiver_group: $obj)" in result.query

    def test_mutation_query_none_params(self):
        """Test mutation query with explicit None params."""
        result = get_mutation_query("create_event", params=None)

        assert result.variables == {"obj": None}

    def test_mutation_query_structure(self):
        """Test that mutation query has correct GraphQL structure."""
        params = {"name": "test"}
        result = get_mutation_query("create_event", params=params)

        # Verify it follows GraphQL mutation syntax
        assert result.query.startswith("mutation")
        assert "$obj: CreateEventInput!" in result.query
        assert "{create_event(event: $obj)}" in result.query
