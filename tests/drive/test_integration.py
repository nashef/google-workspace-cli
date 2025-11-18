"""Integration tests for Google Drive CLI.

These tests verify CLI command structure and error handling.
Full integration testing requires valid Drive API credentials.
"""

import pytest
from click.testing import CliRunner
from gwc.drive import __main__ as drive_cli


@pytest.fixture
def runner():
    """Create Click test runner."""
    return CliRunner()


class TestCLIStructure:
    """Test CLI command structure and help."""

    def test_main_help(self, runner):
        """Test main help command."""
        result = runner.invoke(drive_cli.main, ["--help"])
        assert result.exit_code == 0
        assert "Google Drive CLI" in result.output

    def test_create_help(self, runner):
        """Test create command help."""
        result = runner.invoke(drive_cli.main, ["create", "--help"])
        assert result.exit_code == 0
        assert "--name" in result.output
        assert "--mime-type" in result.output

    def test_get_help(self, runner):
        """Test get command help."""
        result = runner.invoke(drive_cli.main, ["get", "--help"])
        assert result.exit_code == 0
        assert "FILE_ID" in result.output

    def test_list_help(self, runner):
        """Test list command help."""
        result = runner.invoke(drive_cli.main, ["list", "--help"])
        assert result.exit_code == 0
        assert "--query" in result.output
        assert "--limit" in result.output

    def test_update_help(self, runner):
        """Test update command help."""
        result = runner.invoke(drive_cli.main, ["update", "--help"])
        assert result.exit_code == 0
        assert "FILE_ID" in result.output
        assert "--name" in result.output

    def test_delete_help(self, runner):
        """Test delete command help."""
        result = runner.invoke(drive_cli.main, ["delete", "--help"])
        assert result.exit_code == 0
        assert "FILE_ID" in result.output

    def test_copy_help(self, runner):
        """Test copy command help."""
        result = runner.invoke(drive_cli.main, ["copy", "--help"])
        assert result.exit_code == 0
        assert "FILE_ID" in result.output
        assert "--name" in result.output

    def test_export_help(self, runner):
        """Test export command help."""
        result = runner.invoke(drive_cli.main, ["export", "--help"])
        assert result.exit_code == 0
        assert "FILE_ID" in result.output
        assert "--mime-type" in result.output
        assert "--output-file" in result.output

    def test_download_help(self, runner):
        """Test download command help."""
        result = runner.invoke(drive_cli.main, ["download", "--help"])
        assert result.exit_code == 0
        assert "FILE_ID" in result.output
        assert "--output-file" in result.output

    def test_labels_help(self, runner):
        """Test labels command help."""
        result = runner.invoke(drive_cli.main, ["labels", "--help"])
        assert result.exit_code == 0
        assert "FILE_ID" in result.output

    def test_modify_labels_help(self, runner):
        """Test modify-labels command help."""
        result = runner.invoke(drive_cli.main, ["modify-labels", "--help"])
        assert result.exit_code == 0
        assert "--add" in result.output
        assert "--remove" in result.output

    def test_trash_help(self, runner):
        """Test trash command help."""
        result = runner.invoke(drive_cli.main, ["trash", "--help"])
        assert result.exit_code == 0
        assert "FILE_ID" in result.output

    def test_untrash_help(self, runner):
        """Test untrash command help."""
        result = runner.invoke(drive_cli.main, ["untrash", "--help"])
        assert result.exit_code == 0
        assert "FILE_ID" in result.output

    def test_empty_trash_help(self, runner):
        """Test empty-trash command help."""
        result = runner.invoke(drive_cli.main, ["empty-trash", "--help"])
        assert result.exit_code == 0

    def test_about_help(self, runner):
        """Test about command help."""
        result = runner.invoke(drive_cli.main, ["about", "--help"])
        assert result.exit_code == 0
        assert "--output" in result.output

    def test_quota_help(self, runner):
        """Test quota command help."""
        result = runner.invoke(drive_cli.main, ["quota", "--help"])
        assert result.exit_code == 0
        assert "--output" in result.output

    def test_mime_types_help(self, runner):
        """Test mime-types command help."""
        result = runner.invoke(drive_cli.main, ["mime-types", "--help"])
        assert result.exit_code == 0

    def test_export_formats_help(self, runner):
        """Test export-formats command help."""
        result = runner.invoke(drive_cli.main, ["export-formats", "--help"])
        assert result.exit_code == 0


class TestOutputFormats:
    """Test that output format options are accepted."""

    def test_list_output_formats(self, runner):
        """Test that list accepts all output formats."""
        for output_fmt in ["unix", "json", "llm"]:
            result = runner.invoke(
                drive_cli.main,
                ["list", "--output", output_fmt],
                catch_exceptions=False,
            )
            # May fail with auth error, but should accept the option
            assert "--output" not in result.output or result.exit_code in [0, 1]

    def test_get_output_formats(self, runner):
        """Test that get accepts all output formats."""
        for output_fmt in ["unix", "json", "llm"]:
            result = runner.invoke(
                drive_cli.main,
                ["get", "test_id", "--output", output_fmt],
                catch_exceptions=False,
            )
            assert "--output" not in result.output or result.exit_code in [0, 1]

    def test_about_output_formats(self, runner):
        """Test that about accepts all output formats."""
        for output_fmt in ["unix", "json", "llm"]:
            result = runner.invoke(
                drive_cli.main,
                ["about", "--output", output_fmt],
                catch_exceptions=False,
            )
            assert "--output" not in result.output or result.exit_code in [0, 1]


class TestErrorHandling:
    """Test error handling."""

    def test_create_without_name(self, runner):
        """Test create without --name option."""
        result = runner.invoke(drive_cli.main, ["create"])
        assert result.exit_code != 0

    def test_get_without_file_id(self, runner):
        """Test get without file ID."""
        result = runner.invoke(drive_cli.main, ["get"])
        assert result.exit_code != 0

    def test_update_without_file_id(self, runner):
        """Test update without file ID."""
        result = runner.invoke(drive_cli.main, ["update"])
        assert result.exit_code != 0

    def test_delete_without_file_id(self, runner):
        """Test delete without file ID."""
        result = runner.invoke(drive_cli.main, ["delete"])
        assert result.exit_code != 0

    def test_copy_without_file_id(self, runner):
        """Test copy without file ID."""
        result = runner.invoke(drive_cli.main, ["copy"])
        assert result.exit_code != 0

    def test_copy_without_name(self, runner):
        """Test copy without --name option."""
        result = runner.invoke(
            drive_cli.main,
            ["copy", "test_id"],
        )
        assert result.exit_code != 0

    def test_export_without_file_id(self, runner):
        """Test export without file ID."""
        result = runner.invoke(drive_cli.main, ["export"])
        assert result.exit_code != 0

    def test_export_without_output_file(self, runner):
        """Test export without --output-file option."""
        result = runner.invoke(
            drive_cli.main,
            ["export", "test_id"],
        )
        assert result.exit_code != 0

    def test_download_without_file_id(self, runner):
        """Test download without file ID."""
        result = runner.invoke(drive_cli.main, ["download"])
        assert result.exit_code != 0

    def test_download_without_output_file(self, runner):
        """Test download without --output-file option."""
        result = runner.invoke(
            drive_cli.main,
            ["download", "test_id"],
        )
        assert result.exit_code != 0

    def test_labels_without_file_id(self, runner):
        """Test labels without file ID."""
        result = runner.invoke(drive_cli.main, ["labels"])
        assert result.exit_code != 0

    def test_trash_without_file_id(self, runner):
        """Test trash without file ID."""
        result = runner.invoke(drive_cli.main, ["trash"])
        assert result.exit_code != 0

    def test_untrash_without_file_id(self, runner):
        """Test untrash without file ID."""
        result = runner.invoke(drive_cli.main, ["untrash"])
        assert result.exit_code != 0

    def test_invalid_output_format(self, runner):
        """Test that invalid output format is rejected."""
        result = runner.invoke(
            drive_cli.main,
            ["list", "--output", "invalid"],
        )
        assert result.exit_code != 0
        assert "Invalid value" in result.output or "invalid" in result.output.lower()

    def test_invalid_limit(self, runner):
        """Test that invalid limit is rejected."""
        result = runner.invoke(
            drive_cli.main,
            ["list", "--limit", "not_a_number"],
        )
        assert result.exit_code != 0
