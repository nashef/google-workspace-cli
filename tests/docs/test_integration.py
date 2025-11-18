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


class TestPhase2TextOperations:
    """Test Phase 2 text manipulation and formatting commands."""

    def test_insert_text_help(self, runner):
        """Test insert-text command help."""
        result = runner.invoke(docs_cli.main, ["insert-text", "--help"])
        assert result.exit_code == 0
        assert "DOCUMENT_ID" in result.output
        assert "--text" in result.output
        assert "--index" in result.output

    def test_delete_help(self, runner):
        """Test delete command help."""
        result = runner.invoke(docs_cli.main, ["delete", "--help"])
        assert result.exit_code == 0
        assert "DOCUMENT_ID" in result.output
        assert "--start-index" in result.output
        assert "--end-index" in result.output

    def test_replace_help(self, runner):
        """Test replace command help."""
        result = runner.invoke(docs_cli.main, ["replace", "--help"])
        assert result.exit_code == 0
        assert "DOCUMENT_ID" in result.output
        assert "--find" in result.output
        assert "--replace" in result.output

    def test_format_text_help(self, runner):
        """Test format-text command help."""
        result = runner.invoke(docs_cli.main, ["format-text", "--help"])
        assert result.exit_code == 0
        assert "DOCUMENT_ID" in result.output
        assert "--start-index" in result.output
        assert "--end-index" in result.output
        assert "--bold" in result.output
        assert "--italic" in result.output
        assert "--color" in result.output

    def test_format_paragraph_help(self, runner):
        """Test format-paragraph command help."""
        result = runner.invoke(docs_cli.main, ["format-paragraph", "--help"])
        assert result.exit_code == 0
        assert "DOCUMENT_ID" in result.output
        assert "--align" in result.output
        assert "--heading" in result.output
        assert "--line-spacing" in result.output


class TestPhase2TextOperationsMissing:
    """Test error handling for Phase 2 text operations."""

    def test_insert_text_missing_text(self, runner):
        """Test insert-text without text."""
        result = runner.invoke(docs_cli.main, ["insert-text", "test_id", "--index", "0"])
        assert result.exit_code != 0

    def test_insert_text_missing_index(self, runner):
        """Test insert-text without index."""
        result = runner.invoke(docs_cli.main, ["insert-text", "test_id", "--text", "hello"])
        assert result.exit_code != 0

    def test_insert_text_without_document_id(self, runner):
        """Test insert-text without document ID."""
        result = runner.invoke(docs_cli.main, ["insert-text", "--text", "hello", "--index", "0"])
        assert result.exit_code != 0

    def test_delete_missing_indices(self, runner):
        """Test delete without indices."""
        result = runner.invoke(docs_cli.main, ["delete", "test_id"])
        assert result.exit_code != 0

    def test_delete_without_document_id(self, runner):
        """Test delete without document ID."""
        result = runner.invoke(docs_cli.main, ["delete", "--start-index", "0", "--end-index", "5"])
        assert result.exit_code != 0

    def test_replace_missing_find(self, runner):
        """Test replace without find."""
        result = runner.invoke(docs_cli.main, ["replace", "test_id", "--replace", "new"])
        assert result.exit_code != 0

    def test_replace_missing_replace(self, runner):
        """Test replace without replace."""
        result = runner.invoke(docs_cli.main, ["replace", "test_id", "--find", "old"])
        assert result.exit_code != 0

    def test_replace_without_document_id(self, runner):
        """Test replace without document ID."""
        result = runner.invoke(docs_cli.main, ["replace", "--find", "old", "--replace", "new"])
        assert result.exit_code != 0

    def test_format_text_missing_indices(self, runner):
        """Test format-text without indices."""
        result = runner.invoke(docs_cli.main, ["format-text", "test_id", "--bold"])
        assert result.exit_code != 0

    def test_format_text_without_document_id(self, runner):
        """Test format-text without document ID."""
        result = runner.invoke(docs_cli.main, ["format-text", "--start-index", "0", "--end-index", "5", "--bold"])
        assert result.exit_code != 0

    def test_format_paragraph_missing_indices(self, runner):
        """Test format-paragraph without indices."""
        result = runner.invoke(docs_cli.main, ["format-paragraph", "test_id", "--align", "center"])
        assert result.exit_code != 0

    def test_format_paragraph_without_document_id(self, runner):
        """Test format-paragraph without document ID."""
        result = runner.invoke(docs_cli.main, ["format-paragraph", "--start-index", "0", "--end-index", "5"])
        assert result.exit_code != 0

    def test_format_paragraph_invalid_alignment(self, runner):
        """Test format-paragraph with invalid alignment."""
        result = runner.invoke(
            docs_cli.main,
            ["format-paragraph", "test_id", "--start-index", "0", "--end-index", "5", "--align", "invalid"],
        )
        assert result.exit_code != 0

    def test_format_paragraph_invalid_heading(self, runner):
        """Test format-paragraph with invalid heading."""
        result = runner.invoke(
            docs_cli.main,
            ["format-paragraph", "test_id", "--start-index", "0", "--end-index", "5", "--heading", "INVALID"],
        )
        assert result.exit_code != 0


class TestPhase2CommandInvocation:
    """Test that all Phase 2 commands can be invoked."""

    def test_insert_text_invocation(self, runner):
        """Test insert-text command invocation."""
        result = runner.invoke(
            docs_cli.main,
            ["insert-text", "test_id", "--text", "Hello", "--index", "0"],
            catch_exceptions=False,
        )
        # May fail with auth error, but command structure should be valid
        assert result.exit_code in [0, 1]

    def test_delete_invocation(self, runner):
        """Test delete command invocation."""
        result = runner.invoke(
            docs_cli.main,
            ["delete", "test_id", "--start-index", "0", "--end-index", "5"],
            catch_exceptions=False,
        )
        assert result.exit_code in [0, 1]

    def test_replace_invocation(self, runner):
        """Test replace command invocation."""
        result = runner.invoke(
            docs_cli.main,
            ["replace", "test_id", "--find", "old", "--replace", "new"],
            catch_exceptions=False,
        )
        assert result.exit_code in [0, 1]

    def test_format_text_with_bold(self, runner):
        """Test format-text with bold."""
        result = runner.invoke(
            docs_cli.main,
            ["format-text", "test_id", "--start-index", "0", "--end-index", "5", "--bold"],
            catch_exceptions=False,
        )
        assert result.exit_code in [0, 1]

    def test_format_text_with_formatting(self, runner):
        """Test format-text with multiple formatting options."""
        result = runner.invoke(
            docs_cli.main,
            [
                "format-text",
                "test_id",
                "--start-index",
                "0",
                "--end-index",
                "10",
                "--bold",
                "--italic",
                "--font",
                "Arial",
                "--size",
                "14",
            ],
            catch_exceptions=False,
        )
        assert result.exit_code in [0, 1]

    def test_format_paragraph_with_alignment(self, runner):
        """Test format-paragraph with alignment."""
        result = runner.invoke(
            docs_cli.main,
            ["format-paragraph", "test_id", "--start-index", "0", "--end-index", "10", "--align", "center"],
            catch_exceptions=False,
        )
        assert result.exit_code in [0, 1]

    def test_format_paragraph_with_heading(self, runner):
        """Test format-paragraph with heading."""
        result = runner.invoke(
            docs_cli.main,
            ["format-paragraph", "test_id", "--start-index", "0", "--end-index", "10", "--heading", "HEADING_1"],
            catch_exceptions=False,
        )
        assert result.exit_code in [0, 1]

    def test_format_paragraph_with_spacing(self, runner):
        """Test format-paragraph with spacing options."""
        result = runner.invoke(
            docs_cli.main,
            [
                "format-paragraph",
                "test_id",
                "--start-index",
                "0",
                "--end-index",
                "10",
                "--spacing-after",
                "12",
                "--line-spacing",
                "1.5",
            ],
            catch_exceptions=False,
        )
        assert result.exit_code in [0, 1]


class TestPhase3TableAndImages:
    """Test Phase 3 table and image commands."""

    def test_insert_table_help(self, runner):
        """Test insert-table command help."""
        result = runner.invoke(docs_cli.main, ["insert-table", "--help"])
        assert result.exit_code == 0
        assert "DOCUMENT_ID" in result.output
        assert "--rows" in result.output
        assert "--columns" in result.output
        assert "--index" in result.output

    def test_insert_image_help(self, runner):
        """Test insert-image command help."""
        result = runner.invoke(docs_cli.main, ["insert-image", "--help"])
        assert result.exit_code == 0
        assert "DOCUMENT_ID" in result.output
        assert "--image-url" in result.output
        assert "--index" in result.output

    def test_insert_page_break_help(self, runner):
        """Test insert-page-break command help."""
        result = runner.invoke(docs_cli.main, ["insert-page-break", "--help"])
        assert result.exit_code == 0
        assert "DOCUMENT_ID" in result.output
        assert "--index" in result.output

    def test_insert_footnote_help(self, runner):
        """Test insert-footnote command help."""
        result = runner.invoke(docs_cli.main, ["insert-footnote", "--help"])
        assert result.exit_code == 0
        assert "DOCUMENT_ID" in result.output
        assert "--text" in result.output
        assert "--index" in result.output

    def test_create_header_help(self, runner):
        """Test create-header command help."""
        result = runner.invoke(docs_cli.main, ["create-header", "--help"])
        assert result.exit_code == 0
        assert "DOCUMENT_ID" in result.output

    def test_create_footer_help(self, runner):
        """Test create-footer command help."""
        result = runner.invoke(docs_cli.main, ["create-footer", "--help"])
        assert result.exit_code == 0
        assert "DOCUMENT_ID" in result.output

    def test_delete_header_help(self, runner):
        """Test delete-header command help."""
        result = runner.invoke(docs_cli.main, ["delete-header", "--help"])
        assert result.exit_code == 0
        assert "DOCUMENT_ID" in result.output

    def test_delete_footer_help(self, runner):
        """Test delete-footer command help."""
        result = runner.invoke(docs_cli.main, ["delete-footer", "--help"])
        assert result.exit_code == 0
        assert "DOCUMENT_ID" in result.output


class TestPhase3MissingArgs:
    """Test error handling for Phase 3 commands."""

    def test_insert_table_missing_rows(self, runner):
        """Test insert-table without rows."""
        result = runner.invoke(docs_cli.main, ["insert-table", "test_id", "--columns", "2", "--index", "0"])
        assert result.exit_code != 0

    def test_insert_table_missing_columns(self, runner):
        """Test insert-table without columns."""
        result = runner.invoke(docs_cli.main, ["insert-table", "test_id", "--rows", "3", "--index", "0"])
        assert result.exit_code != 0

    def test_insert_table_missing_index(self, runner):
        """Test insert-table without index."""
        result = runner.invoke(docs_cli.main, ["insert-table", "test_id", "--rows", "3", "--columns", "2"])
        assert result.exit_code != 0

    def test_insert_image_missing_url(self, runner):
        """Test insert-image without URL."""
        result = runner.invoke(docs_cli.main, ["insert-image", "test_id", "--index", "0"])
        assert result.exit_code != 0

    def test_insert_image_missing_index(self, runner):
        """Test insert-image without index."""
        result = runner.invoke(
            docs_cli.main, ["insert-image", "test_id", "--image-url", "https://example.com/img.png"]
        )
        assert result.exit_code != 0

    def test_insert_page_break_missing_index(self, runner):
        """Test insert-page-break without index."""
        result = runner.invoke(docs_cli.main, ["insert-page-break", "test_id"])
        assert result.exit_code != 0

    def test_insert_footnote_missing_text(self, runner):
        """Test insert-footnote without text."""
        result = runner.invoke(docs_cli.main, ["insert-footnote", "test_id", "--index", "0"])
        assert result.exit_code != 0

    def test_insert_footnote_missing_index(self, runner):
        """Test insert-footnote without index."""
        result = runner.invoke(docs_cli.main, ["insert-footnote", "test_id", "--text", "footnote"])
        assert result.exit_code != 0

    def test_delete_header_missing_header_id(self, runner):
        """Test delete-header without header ID."""
        result = runner.invoke(docs_cli.main, ["delete-header", "test_id"])
        assert result.exit_code != 0

    def test_delete_footer_missing_footer_id(self, runner):
        """Test delete-footer without footer ID."""
        result = runner.invoke(docs_cli.main, ["delete-footer", "test_id"])
        assert result.exit_code != 0


class TestPhase3CommandInvocation:
    """Test that all Phase 3 commands can be invoked."""

    def test_insert_table_invocation(self, runner):
        """Test insert-table command invocation."""
        result = runner.invoke(
            docs_cli.main,
            ["insert-table", "test_id", "--rows", "3", "--columns", "2", "--index", "0"],
            catch_exceptions=False,
        )
        assert result.exit_code in [0, 1]

    def test_insert_image_invocation(self, runner):
        """Test insert-image command invocation."""
        result = runner.invoke(
            docs_cli.main,
            ["insert-image", "test_id", "--image-url", "https://example.com/img.png", "--index", "0"],
            catch_exceptions=False,
        )
        assert result.exit_code in [0, 1]

    def test_insert_page_break_invocation(self, runner):
        """Test insert-page-break command invocation."""
        result = runner.invoke(
            docs_cli.main,
            ["insert-page-break", "test_id", "--index", "50"],
            catch_exceptions=False,
        )
        assert result.exit_code in [0, 1]

    def test_insert_footnote_invocation(self, runner):
        """Test insert-footnote command invocation."""
        result = runner.invoke(
            docs_cli.main,
            ["insert-footnote", "test_id", "--text", "See appendix", "--index", "50"],
            catch_exceptions=False,
        )
        assert result.exit_code in [0, 1]

    def test_create_header_invocation(self, runner):
        """Test create-header command invocation."""
        result = runner.invoke(
            docs_cli.main,
            ["create-header", "test_id"],
            catch_exceptions=False,
        )
        assert result.exit_code in [0, 1]

    def test_create_header_with_section(self, runner):
        """Test create-header with section ID."""
        result = runner.invoke(
            docs_cli.main,
            ["create-header", "test_id", "--section-id", "1"],
            catch_exceptions=False,
        )
        assert result.exit_code in [0, 1]

    def test_create_footer_invocation(self, runner):
        """Test create-footer command invocation."""
        result = runner.invoke(
            docs_cli.main,
            ["create-footer", "test_id"],
            catch_exceptions=False,
        )
        assert result.exit_code in [0, 1]

    def test_create_footer_with_section(self, runner):
        """Test create-footer with section ID."""
        result = runner.invoke(
            docs_cli.main,
            ["create-footer", "test_id", "--section-id", "1"],
            catch_exceptions=False,
        )
        assert result.exit_code in [0, 1]

    def test_delete_header_invocation(self, runner):
        """Test delete-header command invocation."""
        result = runner.invoke(
            docs_cli.main,
            ["delete-header", "test_id", "header_id_123"],
            catch_exceptions=False,
        )
        assert result.exit_code in [0, 1]

    def test_delete_footer_invocation(self, runner):
        """Test delete-footer command invocation."""
        result = runner.invoke(
            docs_cli.main,
            ["delete-footer", "test_id", "footer_id_123"],
            catch_exceptions=False,
        )
        assert result.exit_code in [0, 1]
