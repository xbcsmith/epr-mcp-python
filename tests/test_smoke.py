"""Smoke tests for epr_mcp module."""

import pytest  # type: ignore


def test_epr_mcp_is_importable():
    """Test that epr_mcp module can be imported without errors."""
    try:
        import epr_mcp  # noqa: F401
    except ImportError as e:
        pytest.fail(f"Failed to import epr_mcp: {e}")


def test_epr_mcp_schemas_is_importable():
    """Test that epr_mcp.schemas module can be imported without errors."""
    try:
        import epr_mcp.schemas  # noqa: F401
    except ImportError as e:
        pytest.fail(f"Failed to import epr_mcp.schemas: {e}")


def test_epr_mcp_server_is_importable():
    """Test that epr_mcp.server module can be imported without errors."""
    try:
        import epr_mcp.server  # noqa: F401
    except ImportError as e:
        pytest.fail(f"Failed to import epr_mcp.server: {e}")


def test_key_classes_importable():
    """Test that key classes can be imported."""
    try:
        from epr_mcp.schemas import EventCreateInput, EventSearchInput  # noqa: F401
    except ImportError as e:
        pytest.fail(f"Failed to import key classes: {e}")
