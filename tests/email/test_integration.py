"""Integration tests for Gmail CLI.

These tests verify CLI command structure and error handling.
Full integration testing requires valid Gmail credentials.
"""

import pytest
from click.testing import CliRunner
from gwc.email import __main__ as email_cli


@pytest.fixture
def runner():
    """Create Click test runner."""
    return CliRunner()


class TestCLIStructure:
    """Test CLI command structure and help."""

    def test_main_help(self, runner):
        """Test main help command."""
        result = runner.invoke(email_cli.main, ["--help"])
        assert result.exit_code == 0
        assert "Gmail CLI" in result.output

    def test_list_help(self, runner):
        """Test list command help."""
        result = runner.invoke(email_cli.main, ["list", "--help"])
        assert result.exit_code == 0
        assert "--label" in result.output
        assert "--limit" in result.output
        assert "--query" in result.output

    def test_get_help(self, runner):
        """Test get command help."""
        result = runner.invoke(email_cli.main, ["get", "--help"])
        assert result.exit_code == 0
        assert "MESSAGE_ID" in result.output

    def test_search_help(self, runner):
        """Test search command help."""
        result = runner.invoke(email_cli.main, ["search", "--help"])
        assert result.exit_code == 0
        assert "QUERY" in result.output
        assert "Gmail search syntax" in result.output

    def test_search_help_command(self, runner):
        """Test search-help command."""
        result = runner.invoke(email_cli.main, ["search-help"])
        assert result.exit_code == 0
        assert "from:" in result.output
        assert "subject:" in result.output
        assert "has:attachment" in result.output

    def test_labels_help(self, runner):
        """Test labels group help."""
        result = runner.invoke(email_cli.main, ["labels", "--help"])
        assert result.exit_code == 0
        assert "Manage labels" in result.output

    def test_labels_list_help(self, runner):
        """Test labels list command help."""
        result = runner.invoke(email_cli.main, ["labels", "list", "--help"])
        assert result.exit_code == 0
        assert "--output" in result.output

    def test_labels_get_help(self, runner):
        """Test labels get command help."""
        result = runner.invoke(email_cli.main, ["labels", "get", "--help"])
        assert result.exit_code == 0
        assert "LABEL_NAME" in result.output

    def test_labels_map_help(self, runner):
        """Test labels map command help."""
        result = runner.invoke(email_cli.main, ["labels", "map", "--help"])
        assert result.exit_code == 0
        assert "mapping" in result.output.lower()

    def test_thread_help(self, runner):
        """Test thread command help."""
        result = runner.invoke(email_cli.main, ["thread", "--help"])
        assert result.exit_code == 0
        assert "THREAD_ID" in result.output


class TestOutputFormats:
    """Test that output format options are accepted."""

    def test_list_output_formats(self, runner):
        """Test that list accepts all output formats."""
        for output_fmt in ["unix", "json", "llm"]:
            result = runner.invoke(
                email_cli.main,
                ["list", "--output", output_fmt],
                catch_exceptions=False,
            )
            # May fail with auth error, but should accept the option
            # We're testing CLI parsing, not functionality
            assert "--output" not in result.output or result.exit_code in [0, 1]

    def test_get_output_formats(self, runner):
        """Test that get accepts all output formats."""
        for output_fmt in ["unix", "json", "llm"]:
            result = runner.invoke(
                email_cli.main,
                ["get", "test_id", "--output", output_fmt],
                catch_exceptions=False,
            )
            assert "--output" not in result.output or result.exit_code in [0, 1]

    def test_search_output_formats(self, runner):
        """Test that search accepts all output formats."""
        for output_fmt in ["unix", "json", "llm"]:
            result = runner.invoke(
                email_cli.main,
                ["search", "test", "--output", output_fmt],
                catch_exceptions=False,
            )
            assert "--output" not in result.output or result.exit_code in [0, 1]


class TestErrorHandling:
    """Test error handling."""

    def test_search_without_query(self, runner):
        """Test that search requires a query."""
        result = runner.invoke(email_cli.main, ["search"])
        assert result.exit_code != 0

    def test_get_without_message_id(self, runner):
        """Test that get requires a message ID."""
        result = runner.invoke(email_cli.main, ["get"])
        assert result.exit_code != 0

    def test_labels_get_without_name(self, runner):
        """Test that labels get requires a label name."""
        result = runner.invoke(email_cli.main, ["labels", "get"])
        assert result.exit_code != 0

    def test_thread_without_id(self, runner):
        """Test that thread requires a thread ID."""
        result = runner.invoke(email_cli.main, ["thread"])
        assert result.exit_code != 0

    def test_invalid_output_format(self, runner):
        """Test that invalid output format is rejected."""
        result = runner.invoke(
            email_cli.main,
            ["list", "--output", "invalid"],
        )
        assert result.exit_code != 0
        assert "Invalid value" in result.output or "invalid" in result.output.lower()

    def test_invalid_limit(self, runner):
        """Test that invalid limit is rejected."""
        result = runner.invoke(
            email_cli.main,
            ["list", "--limit", "not_a_number"],
        )
        assert result.exit_code != 0
