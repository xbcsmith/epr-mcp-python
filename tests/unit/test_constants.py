"""Unit tests for epr_mcp.constants module."""

import pytest  # type: ignore

from epr_mcp import constants


class TestConstants:
    """Test constants module values and functionality."""

    def test_title_constant(self):
        """Test that __title__ is correctly set."""
        assert constants.__title__ == "epr-mcp"

    def test_version_constant_exists(self):
        """Test that __version__ exists and is a string."""
        assert hasattr(constants, "__version__")
        assert isinstance(constants.__version__, str)
        assert len(constants.__version__) > 0

    def test_build_constant(self):
        """Test that __build__ is correctly set."""
        assert constants.__build__ == "1"

    def test_author_constant(self):
        """Test that __author__ is correctly set."""
        assert constants.__author__ == "Brett Smith"

    def test_license_constant(self):
        """Test that __license__ is correctly set."""
        assert constants.__license__ == "Apache 2.0"

    def test_version_info_is_tuple(self):
        """Test that __version_info__ is a tuple of version parts."""
        assert hasattr(constants, "__version_info__")
        assert isinstance(constants.__version_info__, tuple)
        assert len(constants.__version_info__) >= 2  # At least major.minor

        # All parts should be strings (from split)
        for part in constants.__version_info__:
            assert isinstance(part, str)

    def test_version_info_matches_version(self):
        """Test that __version_info__ matches __version__."""
        expected_parts = constants.__version__.split(".")
        assert constants.__version_info__ == tuple(expected_parts)

    def test_info_function_exists(self):
        """Test that info function exists and is callable."""
        assert hasattr(constants, "info")
        assert callable(constants.info)

    def test_info_function_returns_string(self):
        """Test that info function returns expected format."""
        result = constants.info()

        assert isinstance(result, str)
        assert constants.__title__ in result
        assert constants.__version__ in result
        assert "\n" in result  # Should have newline between title and version

    def test_info_function_format(self):
        """Test the exact format of info function output."""
        result = constants.info()
        expected = f"{constants.__title__}\n{constants.__version__}"

        assert result == expected

    def test_all_constants_are_strings(self):
        """Test that all main constants are strings."""
        string_constants = ["__title__", "__version__", "__build__", "__author__", "__license__"]

        for const_name in string_constants:
            assert hasattr(constants, const_name)
            const_value = getattr(constants, const_name)
            assert isinstance(const_value, str)
            assert len(const_value) > 0

    def test_version_follows_semver_pattern(self):
        """Test that version follows semantic versioning pattern."""
        version = constants.__version__

        # Should have at least major.minor format
        parts = version.split(".")
        assert len(parts) >= 2

        # First two parts should be numeric
        try:
            int(parts[0])  # major
            int(parts[1])  # minor
        except ValueError:
            pytest.fail(f"Version {version} does not follow semantic versioning")

    def test_constants_are_not_empty(self):
        """Test that no constants are empty strings."""
        constants_to_check = [
            constants.__title__,
            constants.__version__,
            constants.__build__,
            constants.__author__,
            constants.__license__,
        ]

        for const in constants_to_check:
            assert const != ""
            assert const.strip() != ""
