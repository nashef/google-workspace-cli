"""Integration tests for Google Docs CLI.

These tests verify CLI command structure and error handling.
Full integration testing requires valid Docs API credentials.
"""

import pytest
from click.testing import CliRunner
from gwc.docs import __main__ as docs_cli


@pytest.fixture
def runner():
    """Create Click test runner."""
    return CliRunner()


class TestCLIStructure:
    """Test CLI command structure and help."""

    def test_main_help(self, runner):
        """Test main help command."""
        result = runner.invoke(docs_cli.main, ["--help"])
        assert result.exit_code == 0
        assert "Google Docs CLI" in result.output

    def test_create_help(self, runner):
        """Test create command help."""
        result = runner.invoke(docs_cli.main, ["create", "--help"])
        assert result.exit_code == 0
        assert "--title" in result.output

    def test_get_help(self, runner):
        """Test get command help."""
        result = runner.invoke(docs_cli.main, ["get", "--help"])
        assert result.exit_code == 0
        assert "DOCUMENT_ID" in result.output

    def test_title_help(self, runner):
        """Test title command help."""
        result = runner.invoke(docs_cli.main, ["title", "--help"])
        assert result.exit_code == 0
        assert "DOCUMENT_ID" in result.output

    def test_read_help(self, runner):
        """Test read command help."""
        result = runner.invoke(docs_cli.main, ["read", "--help"])
        assert result.exit_code == 0
        assert "DOCUMENT_ID" in result.output

    def test_stats_help(self, runner):
        """Test stats command help."""
        result = runner.invoke(docs_cli.main, ["stats", "--help"])
        assert result.exit_code == 0
        assert "DOCUMENT_ID" in result.output

    def test_structure_help(self, runner):
        """Test structure command help."""
        result = runner.invoke(docs_cli.main, ["structure", "--help"])
        assert result.exit_code == 0
        assert "DOCUMENT_ID" in result.output

    def test_export_text_help(self, runner):
        """Test export-text command help."""
        result = runner.invoke(docs_cli.main, ["export-text", "--help"])
        assert result.exit_code == 0
        assert "DOCUMENT_ID" in result.output
        assert "--output-file" in result.output

    def test_export_json_help(self, runner):
        """Test export-json command help."""
        result = runner.invoke(docs_cli.main, ["export-json", "--help"])
        assert result.exit_code == 0
        assert "DOCUMENT_ID" in result.output
        assert "--output-file" in result.output

    def test_export_markdown_help(self, runner):
        """Test export-markdown command help."""
        result = runner.invoke(docs_cli.main, ["export-markdown", "--help"])
        assert result.exit_code == 0
        assert "DOCUMENT_ID" in result.output
        assert "--output-file" in result.output


class TestOutputFormats:
    """Test that output format options are accepted."""

    def test_create_output_formats(self, runner):
        """Test that create accepts all output formats."""
        for output_fmt in ["unix", "json", "llm"]:
            result = runner.invoke(
                docs_cli.main,
                ["create", "--title", "Test", "--output", output_fmt],
                catch_exceptions=False,
            )
            # May fail with auth error, but should accept the option
            assert "--output" not in result.output or result.exit_code in [0, 1]

    def test_get_output_formats(self, runner):
        """Test that get accepts all output formats."""
        for output_fmt in ["unix", "json", "llm"]:
            result = runner.invoke(
                docs_cli.main,
                ["get", "test_id", "--output", output_fmt],
                catch_exceptions=False,
            )
            assert "--output" not in result.output or result.exit_code in [0, 1]

    def test_stats_output_formats(self, runner):
        """Test that stats accepts all output formats."""
        for output_fmt in ["unix", "json", "llm"]:
            result = runner.invoke(
                docs_cli.main,
                ["stats", "test_id", "--output", output_fmt],
                catch_exceptions=False,
            )
            assert "--output" not in result.output or result.exit_code in [0, 1]

    def test_structure_output_formats(self, runner):
        """Test that structure accepts all output formats."""
        for output_fmt in ["unix", "json", "llm"]:
            result = runner.invoke(
                docs_cli.main,
                ["structure", "test_id", "--output", output_fmt],
                catch_exceptions=False,
            )
            assert "--output" not in result.output or result.exit_code in [0, 1]


class TestErrorHandling:
    """Test error handling."""

    def test_get_without_document_id(self, runner):
        """Test get without document ID."""
        result = runner.invoke(docs_cli.main, ["get"])
        assert result.exit_code != 0

    def test_title_without_document_id(self, runner):
        """Test title without document ID."""
        result = runner.invoke(docs_cli.main, ["title"])
        assert result.exit_code != 0

    def test_read_without_document_id(self, runner):
        """Test read without document ID."""
        result = runner.invoke(docs_cli.main, ["read"])
        assert result.exit_code != 0

    def test_stats_without_document_id(self, runner):
        """Test stats without document ID."""
        result = runner.invoke(docs_cli.main, ["stats"])
        assert result.exit_code != 0

    def test_structure_without_document_id(self, runner):
        """Test structure without document ID."""
        result = runner.invoke(docs_cli.main, ["structure"])
        assert result.exit_code != 0

    def test_export_text_without_document_id(self, runner):
        """Test export-text without document ID."""
        result = runner.invoke(docs_cli.main, ["export-text"])
        assert result.exit_code != 0

    def test_export_json_without_document_id(self, runner):
        """Test export-json without document ID."""
        result = runner.invoke(docs_cli.main, ["export-json"])
        assert result.exit_code != 0

    def test_export_markdown_without_document_id(self, runner):
        """Test export-markdown without document ID."""
        result = runner.invoke(docs_cli.main, ["export-markdown"])
        assert result.exit_code != 0

    def test_invalid_output_format(self, runner):
        """Test that invalid output format is rejected."""
        result = runner.invoke(
            docs_cli.main,
            ["get", "test_id", "--output", "invalid"],
        )
        assert result.exit_code != 0
        assert "Invalid value" in result.output or "invalid" in result.output.lower()


class TestCommandInvocation:
    """Test that all commands can be invoked without errors in structure."""

    def test_create_default_title(self, runner):
        """Test create with default title."""
        result = runner.invoke(
            docs_cli.main,
            ["create"],
            catch_exceptions=False,
        )
        # May fail with auth error, but command structure should be valid
        assert result.exit_code in [0, 1]

    def test_create_custom_title(self, runner):
        """Test create with custom title."""
        result = runner.invoke(
            docs_cli.main,
            ["create", "--title", "My Document"],
            catch_exceptions=False,
        )
        assert result.exit_code in [0, 1]
