"""Unit tests for epr_mcp.models module."""

from epr_mcp.models import (
    Data,
    Event,
    EventReceiver,
    EventReceiverGroup,
    GraphQLQuery,
    Message,
    Model,
    ModelType,
)


class TestModelType:
    """Test ModelType enum."""

    def test_model_type_values(self):
        """Test ModelType enum values."""
        assert ModelType.EVENT.value == "Event"
        assert ModelType.RECEIVER.value == "EventReceiver"
        assert ModelType.GROUP.value == "EventReceiverGroup"

    def test_model_type_lower(self):
        """Test ModelType lower() method."""
        assert ModelType.EVENT.lower() == "event"
        assert ModelType.RECEIVER.lower() == "eventreceiver"
        assert ModelType.GROUP.lower() == "eventreceivergroup"

    def test_model_type_lower_plural(self):
        """Test ModelType lower_plural() method."""
        assert ModelType.EVENT.lower_plural() == "events"
        assert ModelType.RECEIVER.lower_plural() == "eventreceivers"
        assert ModelType.GROUP.lower_plural() == "eventreceivergroups"

    def test_model_type_enum_membership(self):
        """Test ModelType enum membership."""
        assert ModelType.EVENT in ModelType
        assert ModelType.RECEIVER in ModelType
        assert ModelType.GROUP in ModelType


class TestModel:
    """Test Model base class."""

    def test_model_as_dict(self):
        """Test Model as_dict method."""
        model = Model()
        result = model.as_dict()

        assert isinstance(result, dict)
        # Model has no fields, so should be empty
        assert result == {}

    def test_model_as_dict_query(self):
        """Test Model as_dict_query method."""
        model = Model()
        result = model.as_dict_query()

        assert isinstance(result, dict)
        # Should filter out falsy values
        assert result == {}


class TestEvent:
    """Test Event model class."""

    def test_event_default_values(self):
        """Test Event default field values."""
        event = Event()

        assert event.id == ""
        assert event.name == ""
        assert event.version == ""
        assert event.release == ""
        assert event.platform_id == ""
        assert event.package == ""
        assert event.description == ""
        assert event.payload == {}
        assert event.success is False
        assert event.created_at == ""
        assert event.event_receiver_id == ""
        assert event.event_receiver == {}

    def test_event_with_values(self):
        """Test Event with provided values."""
        event = Event(
            id="test-id",
            name="test-event",
            version="1.0.0",
            release="stable",
            platform_id="platform-123",
            package="TestPackage",
            description="Test event description",
            payload={"key": "value"},
            success=True,
            created_at="2023-01-01T00:00:00Z",
            event_receiver_id="receiver-123",
            event_receiver={"name": "test-receiver"},
        )

        assert event.id == "test-id"
        assert event.name == "test-event"
        assert event.version == "1.0.0"
        assert event.release == "stable"
        assert event.platform_id == "platform-123"
        assert event.package == "TestPackage"
        assert event.description == "Test event description"
        assert event.payload == {"key": "value"}
        assert event.success is True
        assert event.created_at == "2023-01-01T00:00:00Z"
        assert event.event_receiver_id == "receiver-123"
        assert event.event_receiver == {"name": "test-receiver"}

    def test_event_as_dict(self):
        """Test Event as_dict method."""
        event = Event(name="test", version="1.0.0", success=True)
        result = event.as_dict()

        assert isinstance(result, dict)
        assert result["name"] == "test"
        assert result["version"] == "1.0.0"
        assert result["success"] is True
        assert "id" in result  # Should include all fields
        assert "payload" in result

    def test_event_as_dict_query(self):
        """Test Event as_dict_query method filters falsy values."""
        event = Event(name="test", version="1.0.0", success=True)
        result = event.as_dict_query()

        assert isinstance(result, dict)
        assert result["name"] == "test"
        assert result["version"] == "1.0.0"
        assert result["success"] is True
        # Should exclude empty strings and empty dicts
        assert "id" not in result
        assert "description" not in result

    def test_event_comparison_excludes_compare_false_fields(self):
        """Test that fields with compare=False don't affect equality."""
        event1 = Event(name="test", id="id1", created_at="time1")
        event2 = Event(name="test", id="id2", created_at="time2")

        # Should be equal despite different id and created_at (compare=False)
        assert event1 == event2

    def test_event_payload_default_factory(self):
        """Test that payload uses default_factory for dict."""
        event1 = Event()
        event2 = Event()

        # Should be different dict instances
        assert event1.payload is not event2.payload

        # Modifying one shouldn't affect the other
        event1.payload["key"] = "value"
        assert "key" not in event2.payload


class TestEventReceiver:
    """Test EventReceiver model class."""

    def test_event_receiver_default_values(self):
        """Test EventReceiver default field values."""
        receiver = EventReceiver()

        assert receiver.id == ""
        assert receiver.name == ""
        assert receiver.type == ""
        assert receiver.version == ""
        assert receiver.description == ""
        assert receiver.schema == {}
        assert receiver.fingerprint == ""
        assert receiver.created_at == ""

    def test_event_receiver_with_values(self):
        """Test EventReceiver with provided values."""
        receiver = EventReceiver(
            id="receiver-id",
            name="test-receiver",
            type="webhook",
            version="1.0.0",
            description="Test receiver",
            schema={"type": "object"},
            fingerprint="abc123",
            created_at="2023-01-01T00:00:00Z",
        )

        assert receiver.id == "receiver-id"
        assert receiver.name == "test-receiver"
        assert receiver.type == "webhook"
        assert receiver.version == "1.0.0"
        assert receiver.description == "Test receiver"
        assert receiver.schema == {"type": "object"}
        assert receiver.fingerprint == "abc123"
        assert receiver.created_at == "2023-01-01T00:00:00Z"

    def test_event_receiver_as_dict_query(self):
        """Test EventReceiver as_dict_query filters falsy values."""
        receiver = EventReceiver(name="test", type="webhook")
        result = receiver.as_dict_query()

        assert result["name"] == "test"
        assert result["type"] == "webhook"
        assert "id" not in result
        assert "description" not in result

    def test_event_receiver_schema_default_factory(self):
        """Test that schema uses default_factory for dict."""
        receiver1 = EventReceiver()
        receiver2 = EventReceiver()

        # Should be different dict instances
        assert receiver1.schema is not receiver2.schema


class TestEventReceiverGroup:
    """Test EventReceiverGroup model class."""

    def test_event_receiver_group_default_values(self):
        """Test EventReceiverGroup default field values."""
        group = EventReceiverGroup()

        assert group.id == ""
        assert group.name == ""
        assert group.type == ""
        assert group.version == ""
        assert group.description == ""
        assert group.enabled is False
        assert group.event_receiver_ids == []
        assert group.created_at == ""
        assert group.updated_at == ""
        assert group.fingerprint == ""

    def test_event_receiver_group_with_values(self):
        """Test EventReceiverGroup with provided values."""
        group = EventReceiverGroup(
            id="group-id",
            name="test-group",
            type="collection",
            version="1.0.0",
            description="Test group",
            enabled=True,
            event_receiver_ids=["recv1", "recv2"],
            created_at="2023-01-01T00:00:00Z",
            updated_at="2023-01-02T00:00:00Z",
            fingerprint="def456",
        )

        assert group.id == "group-id"
        assert group.name == "test-group"
        assert group.type == "collection"
        assert group.version == "1.0.0"
        assert group.description == "Test group"
        assert group.enabled is True
        assert group.event_receiver_ids == ["recv1", "recv2"]
        assert group.created_at == "2023-01-01T00:00:00Z"
        assert group.updated_at == "2023-01-02T00:00:00Z"
        assert group.fingerprint == "def456"

    def test_event_receiver_group_as_dict_query(self):
        """Test EventReceiverGroup as_dict_query filters falsy values."""
        group = EventReceiverGroup(name="test", enabled=True, event_receiver_ids=["recv1"])
        result = group.as_dict_query()

        assert result["name"] == "test"
        assert result["enabled"] is True
        assert result["event_receiver_ids"] == ["recv1"]
        assert "id" not in result
        assert "description" not in result

    def test_event_receiver_group_comparison_excludes_compare_false_fields(self):
        """Test that compare=False fields don't affect equality."""
        group1 = EventReceiverGroup(name="test", id="id1", created_at="time1", updated_at="time1")
        group2 = EventReceiverGroup(name="test", id="id2", created_at="time2", updated_at="time2")

        # Should be equal despite different timestamps and id
        assert group1 == group2

    def test_event_receiver_group_ids_default_factory(self):
        """Test that event_receiver_ids uses default_factory for list."""
        group1 = EventReceiverGroup()
        group2 = EventReceiverGroup()

        # Should be different list instances
        assert group1.event_receiver_ids is not group2.event_receiver_ids

        # Modifying one shouldn't affect the other
        group1.event_receiver_ids.append("recv1")
        assert "recv1" not in group2.event_receiver_ids


class TestData:
    """Test Data model class."""

    def test_data_class_definition(self):
        """Test that Data class can be instantiated."""
        # Data has class-level type annotations, not dataclass fields
        data = Data()
        assert isinstance(data, Data)
        assert isinstance(data, Model)

        # Check that class-level attributes exist
        assert hasattr(Data, "events")
        assert hasattr(Data, "receivers")
        assert hasattr(Data, "receiver_groups")


class TestMessage:
    """Test Message model class."""

    def test_message_with_required_fields(self):
        """Test that Message can be instantiated with required fields."""
        data = Data()
        message = Message(
            success=True,
            id="msg-123",
            specversion="1.0",
            type="test.event",
            source="test-source",
            api_version="v1",
            name="test-message",
            version="1.0.0",
            release="stable",
            platform_id="platform-123",
            package="TestPackage",
            data=data,
        )

        assert isinstance(message, Message)
        assert isinstance(message, Model)
        assert message.success is True
        assert message.id == "msg-123"
        assert message.specversion == "1.0"
        assert message.type == "test.event"
        assert message.source == "test-source"
        assert message.api_version == "v1"
        assert message.name == "test-message"
        assert message.version == "1.0.0"
        assert message.release == "stable"
        assert message.platform_id == "platform-123"
        assert message.package == "TestPackage"
        assert message.data == data

    def test_message_as_dict(self):
        """Test Message as_dict method."""
        data = Data()
        message = Message(
            success=True,
            id="msg-123",
            specversion="1.0",
            type="test.event",
            source="test-source",
            api_version="v1",
            name="test-message",
            version="1.0.0",
            release="stable",
            platform_id="platform-123",
            package="TestPackage",
            data=data,
        )

        result = message.as_dict()
        assert isinstance(result, dict)
        assert result["success"] is True
        assert result["id"] == "msg-123"
        assert result["name"] == "test-message"
        assert "data" in result


class TestGraphQLQuery:
    """Test GraphQLQuery model class."""

    def test_graphql_query_default_values(self):
        """Test GraphQLQuery default field values."""
        query = GraphQLQuery(query="{ test }")

        assert query.query == "{ test }"
        assert query.variables == {}

    def test_graphql_query_with_variables(self):
        """Test GraphQLQuery with variables."""
        variables = {"param1": "value1", "param2": 123}
        query = GraphQLQuery(query="query($param1: String) { test }", variables=variables)

        assert query.query == "query($param1: String) { test }"
        assert query.variables == variables

    def test_graphql_query_as_dict(self):
        """Test GraphQLQuery as_dict method."""
        variables = {"param": "value"}
        query = GraphQLQuery(query="{ test }", variables=variables)
        result = query.as_dict()

        assert result == {"query": "{ test }", "variables": variables}

    def test_graphql_query_as_dict_query(self):
        """Test GraphQLQuery as_dict_query method."""
        query = GraphQLQuery(query="{ test }")
        result = query.as_dict_query()

        # Should include query but not empty variables dict
        assert result == {"query": "{ test }"}

    def test_graphql_query_variables_default_factory(self):
        """Test that variables uses default_factory for dict."""
        query1 = GraphQLQuery(query="{ test1 }")
        query2 = GraphQLQuery(query="{ test2 }")

        # Should be different dict instances
        assert query1.variables is not query2.variables

        # Modifying one shouldn't affect the other
        query1.variables["key"] = "value"
        assert "key" not in query2.variables


class TestModelInheritance:
    """Test model inheritance and polymorphism."""

    def test_all_models_inherit_from_model(self):
        """Test that all model classes inherit from Model."""
        model_classes = [Event, EventReceiver, EventReceiverGroup, Data, Message, GraphQLQuery]

        for model_class in model_classes:
            assert issubclass(model_class, Model)

    def test_model_methods_available_on_all_subclasses(self):
        """Test that Model methods are available on all subclasses."""
        data = Data()
        message = Message(
            success=True,
            id="test",
            specversion="1.0",
            type="test",
            source="test",
            api_version="v1",
            name="test",
            version="1.0",
            release="stable",
            platform_id="test",
            package="test",
            data=data,
        )
        models = [Event(), EventReceiver(), EventReceiverGroup(), data, message, GraphQLQuery(query="test")]

        for model in models:
            assert hasattr(model, "as_dict")
            assert hasattr(model, "as_dict_query")
            assert callable(model.as_dict)
            assert callable(model.as_dict_query)

    def test_models_are_dataclasses(self):
        """Test that all models are dataclasses."""
        model_classes = [Model, Event, EventReceiver, EventReceiverGroup, Data, Message, GraphQLQuery]

        for model_class in model_classes:
            # Check if class has dataclass metadata
            assert hasattr(model_class, "__dataclass_fields__")
