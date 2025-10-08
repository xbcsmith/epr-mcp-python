"""Unit tests for epr_mcp.errors module."""

import io
from unittest.mock import Mock, patch

import pytest  # type: ignore

from epr_mcp.errors import (
    BaseError,
    CmdMissingError,
    EPRError,
    FileNotFoundError as EPRFileNotFoundError,
    GraphQLError,
    InvalidKeyError,
    KeyNotFoundError,
    NotImplemented,
    RunCmdError,
    debug_except_hook,
)


class TestBaseError:
    """Test BaseError exception class."""

    def test_base_error_is_exception(self):
        """Test that BaseError is an Exception."""
        assert issubclass(BaseError, Exception)

    def test_base_error_can_be_raised(self):
        """Test that BaseError can be raised and caught."""
        with pytest.raises(BaseError):
            raise BaseError("Test error")

    def test_base_error_with_message(self):
        """Test BaseError with custom message."""
        message = "Custom error message"
        error = BaseError(message)
        assert str(error) == message


class TestRunCmdError:
    """Test RunCmdError exception class."""

    def test_run_cmd_error_is_base_error(self):
        """Test that RunCmdError inherits from BaseError."""
        assert issubclass(RunCmdError, BaseError)

    def test_run_cmd_error_can_be_raised(self):
        """Test that RunCmdError can be raised and caught."""
        with pytest.raises(RunCmdError):
            raise RunCmdError("Command failed")

    def test_run_cmd_error_with_message(self):
        """Test RunCmdError with custom message."""
        message = "Failed to run command"
        error = RunCmdError(message)
        assert str(error) == message


class TestCmdMissingError:
    """Test CmdMissingError exception class."""

    def test_cmd_missing_error_is_base_error(self):
        """Test that CmdMissingError inherits from BaseError."""
        assert issubclass(CmdMissingError, BaseError)

    def test_cmd_missing_error_can_be_raised(self):
        """Test that CmdMissingError can be raised and caught."""
        with pytest.raises(CmdMissingError):
            raise CmdMissingError("Command missing")


class TestFileNotFoundError:
    """Test EPR FileNotFoundError exception class."""

    def test_file_not_found_error_is_base_error(self):
        """Test that EPRFileNotFoundError inherits from BaseError."""
        assert issubclass(EPRFileNotFoundError, BaseError)

    def test_file_not_found_error_can_be_raised(self):
        """Test that EPRFileNotFoundError can be raised and caught."""
        with pytest.raises(EPRFileNotFoundError):
            raise EPRFileNotFoundError("File not found")


class TestInvalidKeyError:
    """Test InvalidKeyError exception class."""

    def test_invalid_key_error_is_base_error(self):
        """Test that InvalidKeyError inherits from BaseError."""
        assert issubclass(InvalidKeyError, BaseError)

    def test_invalid_key_error_can_be_raised(self):
        """Test that InvalidKeyError can be raised and caught."""
        with pytest.raises(InvalidKeyError):
            raise InvalidKeyError("Invalid key")


class TestKeyNotFoundError:
    """Test KeyNotFoundError exception class."""

    def test_key_not_found_error_is_base_error(self):
        """Test that KeyNotFoundError inherits from BaseError."""
        assert issubclass(KeyNotFoundError, BaseError)

    def test_key_not_found_error_can_be_raised(self):
        """Test that KeyNotFoundError can be raised and caught."""
        with pytest.raises(KeyNotFoundError):
            raise KeyNotFoundError("Key not found")


class TestNotImplemented:
    """Test NotImplemented exception class."""

    def test_not_implemented_is_base_error(self):
        """Test that NotImplemented inherits from BaseError."""
        assert issubclass(NotImplemented, BaseError)

    def test_not_implemented_can_be_raised(self):
        """Test that NotImplemented can be raised and caught."""
        with pytest.raises(NotImplemented):
            raise NotImplemented("Function not implemented")  # noqa: F901


class TestEPRError:
    """Test EPRError exception class."""

    def test_epr_error_is_exception(self):
        """Test that EPRError is an Exception."""
        assert issubclass(EPRError, Exception)

    def test_epr_error_default_message(self):
        """Test EPRError default message."""
        error = EPRError()
        expected = "An error occurred with the request to EPR"
        assert error.message == expected

    def test_epr_error_with_custom_message(self):
        """Test EPRError with custom message."""
        custom_msg = "Custom error"
        error = EPRError(custom_msg)
        expected = "An error occurred with the request to EPR: Custom error"
        assert error.message == expected

    def test_epr_error_can_be_raised(self):
        """Test that EPRError can be raised and caught."""
        with pytest.raises(EPRError):
            raise EPRError("Test error")

    def test_epr_error_str_representation(self):
        """Test EPRError string representation."""
        custom_msg = "Test message"
        error = EPRError(custom_msg)
        # The str() should return the message passed to __init__
        assert str(error) == custom_msg


class TestGraphQLError:
    """Test GraphQLError exception class."""

    def test_graphql_error_is_epr_error(self):
        """Test that GraphQLError inherits from EPRError."""
        assert issubclass(GraphQLError, EPRError)

    def test_graphql_error_default_message(self):
        """Test GraphQLError default message."""
        error = GraphQLError()
        expected = "Error making GraphQL request to EPR"
        assert error.message == expected

    def test_graphql_error_with_custom_message(self):
        """Test GraphQLError with custom message."""
        custom_msg = "Query failed"
        error = GraphQLError(custom_msg)
        expected = "Error making GraphQL request to EPR: Query failed"
        assert error.message == expected

    def test_graphql_error_can_be_raised(self):
        """Test that GraphQLError can be raised and caught."""
        with pytest.raises(GraphQLError):
            raise GraphQLError("GraphQL request failed")


class TestDebugExceptHook:
    """Test debug_except_hook function."""

    @patch("traceback.print_exception")
    @patch("pdb.post_mortem")
    @patch("builtins.print")
    def test_debug_except_hook_calls(self, mock_print, mock_post_mortem, mock_print_exception):
        """Test that debug_except_hook calls expected functions."""
        # Create mock exception info
        exc_type = ValueError
        exc_value = ValueError("Test error")
        exc_traceback = Mock()

        # Call the function
        debug_except_hook(exc_type, exc_value, exc_traceback)

        # Verify print calls
        assert mock_print.call_count == 2
        mock_print.assert_any_call("epr python hates ValueError")
        mock_print.assert_any_call(str(exc_type))

        # Verify traceback.print_exception was called
        mock_print_exception.assert_called_once_with(exc_type, exc_value, exc_traceback)

        # Verify pdb.post_mortem was called
        mock_post_mortem.assert_called_once_with(exc_traceback)

    @patch("traceback.print_exception")
    @patch("pdb.post_mortem")
    def test_debug_except_hook_with_different_exception_types(self, mock_post_mortem, mock_print_exception):
        """Test debug_except_hook with different exception types."""
        exception_types = [KeyError, RuntimeError, TypeError, AttributeError]

        for exc_type in exception_types:
            exc_value = exc_type("Test error")
            exc_traceback = Mock()

            with patch("builtins.print") as mock_print:
                debug_except_hook(exc_type, exc_value, exc_traceback)

                # Should print the exception type name
                mock_print.assert_any_call(f"epr python hates {exc_type.__name__}")

    @patch("sys.stdout", new_callable=io.StringIO)
    @patch("pdb.post_mortem")
    @patch("traceback.print_exception")
    def test_debug_except_hook_output_format(self, mock_print_exception, mock_post_mortem, mock_stdout):
        """Test the output format of debug_except_hook."""
        exc_type = RuntimeError
        exc_value = RuntimeError("Test runtime error")
        exc_traceback = Mock()

        debug_except_hook(exc_type, exc_value, exc_traceback)

        output = mock_stdout.getvalue()
        assert "epr python hates RuntimeError" in output
        assert str(exc_type) in output


class TestErrorHierarchy:
    """Test the error class hierarchy."""

    def test_all_base_errors_inherit_properly(self):
        """Test that all BaseError subclasses inherit correctly."""
        base_error_subclasses = [
            RunCmdError,
            CmdMissingError,
            EPRFileNotFoundError,
            InvalidKeyError,
            KeyNotFoundError,
            NotImplemented,
        ]

        for error_class in base_error_subclasses:
            assert issubclass(error_class, BaseError)
            assert issubclass(error_class, Exception)

    def test_epr_error_hierarchy(self):
        """Test EPRError and GraphQLError hierarchy."""
        assert issubclass(EPRError, Exception)
        assert issubclass(GraphQLError, EPRError)
        assert issubclass(GraphQLError, Exception)

    def test_error_instantiation(self):
        """Test that all error classes can be instantiated."""
        error_classes = [
            BaseError,
            RunCmdError,
            CmdMissingError,
            EPRFileNotFoundError,
            InvalidKeyError,
            KeyNotFoundError,
            NotImplemented,
            EPRError,
            GraphQLError,
        ]

        for error_class in error_classes:
            # Should be able to instantiate without arguments
            error = error_class()
            assert isinstance(error, error_class)

            # Should be able to instantiate with message
            error_with_msg = error_class("Test message")
            assert isinstance(error_with_msg, error_class)
