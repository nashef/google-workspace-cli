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


class TestPhase2Permissions:
    """Test Phase 2: Permission commands."""

    def test_create_permission_help(self, runner):
        """Test create-permission command help."""
        result = runner.invoke(drive_cli.main, ["create-permission", "--help"])
        assert result.exit_code == 0
        assert "--email" in result.output
        assert "--role" in result.output

    def test_get_permission_help(self, runner):
        """Test get-permission command help."""
        result = runner.invoke(drive_cli.main, ["get-permission", "--help"])
        assert result.exit_code == 0
        assert "FILE_ID" in result.output
        assert "PERMISSION_ID" in result.output

    def test_list_permissions_help(self, runner):
        """Test list-permissions command help."""
        result = runner.invoke(drive_cli.main, ["list-permissions", "--help"])
        assert result.exit_code == 0
        assert "FILE_ID" in result.output

    def test_update_permission_help(self, runner):
        """Test update-permission command help."""
        result = runner.invoke(drive_cli.main, ["update-permission", "--help"])
        assert result.exit_code == 0
        assert "FILE_ID" in result.output
        assert "PERMISSION_ID" in result.output
        assert "--role" in result.output

    def test_delete_permission_help(self, runner):
        """Test delete-permission command help."""
        result = runner.invoke(drive_cli.main, ["delete-permission", "--help"])
        assert result.exit_code == 0
        assert "FILE_ID" in result.output
        assert "PERMISSION_ID" in result.output

    def test_create_permission_without_email(self, runner):
        """Test create-permission without --email option."""
        result = runner.invoke(drive_cli.main, ["create-permission", "file_id"])
        assert result.exit_code != 0

    def test_get_permission_without_ids(self, runner):
        """Test get-permission without file_id and permission_id."""
        result = runner.invoke(drive_cli.main, ["get-permission"])
        assert result.exit_code != 0

    def test_list_permissions_without_file_id(self, runner):
        """Test list-permissions without file_id."""
        result = runner.invoke(drive_cli.main, ["list-permissions"])
        assert result.exit_code != 0

    def test_update_permission_without_ids(self, runner):
        """Test update-permission without file_id and permission_id."""
        result = runner.invoke(drive_cli.main, ["update-permission"])
        assert result.exit_code != 0

    def test_delete_permission_without_ids(self, runner):
        """Test delete-permission without file_id and permission_id."""
        result = runner.invoke(drive_cli.main, ["delete-permission"])
        assert result.exit_code != 0

    def test_permission_output_formats(self, runner):
        """Test that permission commands accept all output formats."""
        for output_fmt in ["unix", "json", "llm"]:
            result = runner.invoke(
                drive_cli.main,
                ["list-permissions", "test_id", "--output", output_fmt],
                catch_exceptions=False,
            )
            assert "--output" not in result.output or result.exit_code in [0, 1]


class TestPhase2Drives:
    """Test Phase 2: Shared drive commands."""

    def test_create_drive_help(self, runner):
        """Test create-drive command help."""
        result = runner.invoke(drive_cli.main, ["create-drive", "--help"])
        assert result.exit_code == 0
        assert "--name" in result.output

    def test_get_drive_help(self, runner):
        """Test get-drive command help."""
        result = runner.invoke(drive_cli.main, ["get-drive", "--help"])
        assert result.exit_code == 0
        assert "DRIVE_ID" in result.output

    def test_list_drives_help(self, runner):
        """Test list-drives command help."""
        result = runner.invoke(drive_cli.main, ["list-drives", "--help"])
        assert result.exit_code == 0
        assert "--limit" in result.output

    def test_update_drive_help(self, runner):
        """Test update-drive command help."""
        result = runner.invoke(drive_cli.main, ["update-drive", "--help"])
        assert result.exit_code == 0
        assert "DRIVE_ID" in result.output
        assert "--name" in result.output

    def test_delete_drive_help(self, runner):
        """Test delete-drive command help."""
        result = runner.invoke(drive_cli.main, ["delete-drive", "--help"])
        assert result.exit_code == 0
        assert "DRIVE_ID" in result.output

    def test_hide_drive_help(self, runner):
        """Test hide-drive command help."""
        result = runner.invoke(drive_cli.main, ["hide-drive", "--help"])
        assert result.exit_code == 0
        assert "DRIVE_ID" in result.output

    def test_unhide_drive_help(self, runner):
        """Test unhide-drive command help."""
        result = runner.invoke(drive_cli.main, ["unhide-drive", "--help"])
        assert result.exit_code == 0
        assert "DRIVE_ID" in result.output

    def test_create_drive_without_name(self, runner):
        """Test create-drive without --name option."""
        result = runner.invoke(drive_cli.main, ["create-drive"])
        assert result.exit_code != 0

    def test_get_drive_without_id(self, runner):
        """Test get-drive without drive_id."""
        result = runner.invoke(drive_cli.main, ["get-drive"])
        assert result.exit_code != 0

    def test_update_drive_without_id(self, runner):
        """Test update-drive without drive_id."""
        result = runner.invoke(drive_cli.main, ["update-drive"])
        assert result.exit_code != 0

    def test_delete_drive_without_id(self, runner):
        """Test delete-drive without drive_id."""
        result = runner.invoke(drive_cli.main, ["delete-drive"])
        assert result.exit_code != 0

    def test_hide_drive_without_id(self, runner):
        """Test hide-drive without drive_id."""
        result = runner.invoke(drive_cli.main, ["hide-drive"])
        assert result.exit_code != 0

    def test_unhide_drive_without_id(self, runner):
        """Test unhide-drive without drive_id."""
        result = runner.invoke(drive_cli.main, ["unhide-drive"])
        assert result.exit_code != 0

    def test_drive_output_formats(self, runner):
        """Test that drive commands accept all output formats."""
        for output_fmt in ["unix", "json", "llm"]:
            result = runner.invoke(
                drive_cli.main,
                ["list-drives", "--output", output_fmt],
                catch_exceptions=False,
            )
            assert "--output" not in result.output or result.exit_code in [0, 1]


class TestPhase3Revisions:
    """Test Phase 3: Revision commands."""

    def test_get_revision_help(self, runner):
        """Test get-revision command help."""
        result = runner.invoke(drive_cli.main, ["get-revision", "--help"])
        assert result.exit_code == 0
        assert "FILE_ID" in result.output
        assert "REVISION_ID" in result.output

    def test_list_revisions_help(self, runner):
        """Test list-revisions command help."""
        result = runner.invoke(drive_cli.main, ["list-revisions", "--help"])
        assert result.exit_code == 0
        assert "FILE_ID" in result.output
        assert "--limit" in result.output

    def test_delete_revision_help(self, runner):
        """Test delete-revision command help."""
        result = runner.invoke(drive_cli.main, ["delete-revision", "--help"])
        assert result.exit_code == 0
        assert "FILE_ID" in result.output
        assert "REVISION_ID" in result.output

    def test_keep_revision_help(self, runner):
        """Test keep-revision command help."""
        result = runner.invoke(drive_cli.main, ["keep-revision", "--help"])
        assert result.exit_code == 0
        assert "FILE_ID" in result.output
        assert "REVISION_ID" in result.output

    def test_restore_revision_help(self, runner):
        """Test restore-revision command help."""
        result = runner.invoke(drive_cli.main, ["restore-revision", "--help"])
        assert result.exit_code == 0
        assert "FILE_ID" in result.output
        assert "REVISION_ID" in result.output

    def test_get_revision_without_ids(self, runner):
        """Test get-revision without file_id and revision_id."""
        result = runner.invoke(drive_cli.main, ["get-revision"])
        assert result.exit_code != 0

    def test_list_revisions_without_file_id(self, runner):
        """Test list-revisions without file_id."""
        result = runner.invoke(drive_cli.main, ["list-revisions"])
        assert result.exit_code != 0

    def test_delete_revision_without_ids(self, runner):
        """Test delete-revision without ids."""
        result = runner.invoke(drive_cli.main, ["delete-revision"])
        assert result.exit_code != 0

    def test_keep_revision_without_ids(self, runner):
        """Test keep-revision without ids."""
        result = runner.invoke(drive_cli.main, ["keep-revision"])
        assert result.exit_code != 0

    def test_restore_revision_without_ids(self, runner):
        """Test restore-revision without ids."""
        result = runner.invoke(drive_cli.main, ["restore-revision"])
        assert result.exit_code != 0

    def test_revision_output_formats(self, runner):
        """Test that revision commands accept all output formats."""
        for output_fmt in ["unix", "json", "llm"]:
            result = runner.invoke(
                drive_cli.main,
                ["list-revisions", "test_id", "--output", output_fmt],
                catch_exceptions=False,
            )
            assert "--output" not in result.output or result.exit_code in [0, 1]


class TestPhase3Changes:
    """Test Phase 3: Change tracking commands."""

    def test_get_start_page_token_help(self, runner):
        """Test get-start-page-token command help."""
        result = runner.invoke(drive_cli.main, ["get-start-page-token", "--help"])
        assert result.exit_code == 0

    def test_list_changes_help(self, runner):
        """Test list-changes command help."""
        result = runner.invoke(drive_cli.main, ["list-changes", "--help"])
        assert result.exit_code == 0
        assert "PAGE_TOKEN" in result.output
        assert "--limit" in result.output

    def test_list_changes_without_token(self, runner):
        """Test list-changes without page_token."""
        result = runner.invoke(drive_cli.main, ["list-changes"])
        assert result.exit_code != 0

    def test_list_changes_output_formats(self, runner):
        """Test that list-changes accepts all output formats."""
        for output_fmt in ["unix", "json", "llm"]:
            result = runner.invoke(
                drive_cli.main,
                ["list-changes", "test_token", "--output", output_fmt],
                catch_exceptions=False,
            )
            assert "--output" not in result.output or result.exit_code in [0, 1]


class TestPhase3Comments:
    """Test Phase 3: Comment commands."""

    def test_create_comment_help(self, runner):
        """Test create-comment command help."""
        result = runner.invoke(drive_cli.main, ["create-comment", "--help"])
        assert result.exit_code == 0
        assert "FILE_ID" in result.output
        assert "--content" in result.output

    def test_get_comment_help(self, runner):
        """Test get-comment command help."""
        result = runner.invoke(drive_cli.main, ["get-comment", "--help"])
        assert result.exit_code == 0
        assert "FILE_ID" in result.output
        assert "COMMENT_ID" in result.output

    def test_list_comments_help(self, runner):
        """Test list-comments command help."""
        result = runner.invoke(drive_cli.main, ["list-comments", "--help"])
        assert result.exit_code == 0
        assert "FILE_ID" in result.output
        assert "--limit" in result.output

    def test_update_comment_help(self, runner):
        """Test update-comment command help."""
        result = runner.invoke(drive_cli.main, ["update-comment", "--help"])
        assert result.exit_code == 0
        assert "FILE_ID" in result.output
        assert "COMMENT_ID" in result.output

    def test_delete_comment_help(self, runner):
        """Test delete-comment command help."""
        result = runner.invoke(drive_cli.main, ["delete-comment", "--help"])
        assert result.exit_code == 0
        assert "FILE_ID" in result.output
        assert "COMMENT_ID" in result.output

    def test_create_reply_help(self, runner):
        """Test create-reply command help."""
        result = runner.invoke(drive_cli.main, ["create-reply", "--help"])
        assert result.exit_code == 0
        assert "FILE_ID" in result.output
        assert "COMMENT_ID" in result.output
        assert "--content" in result.output

    def test_list_replies_help(self, runner):
        """Test list-replies command help."""
        result = runner.invoke(drive_cli.main, ["list-replies", "--help"])
        assert result.exit_code == 0
        assert "FILE_ID" in result.output
        assert "COMMENT_ID" in result.output

    def test_create_comment_without_content(self, runner):
        """Test create-comment without --content option."""
        result = runner.invoke(drive_cli.main, ["create-comment", "file_id"])
        assert result.exit_code != 0

    def test_get_comment_without_ids(self, runner):
        """Test get-comment without file_id and comment_id."""
        result = runner.invoke(drive_cli.main, ["get-comment"])
        assert result.exit_code != 0

    def test_list_comments_without_file_id(self, runner):
        """Test list-comments without file_id."""
        result = runner.invoke(drive_cli.main, ["list-comments"])
        assert result.exit_code != 0

    def test_update_comment_without_ids(self, runner):
        """Test update-comment without file_id and comment_id."""
        result = runner.invoke(drive_cli.main, ["update-comment"])
        assert result.exit_code != 0

    def test_delete_comment_without_ids(self, runner):
        """Test delete-comment without file_id and comment_id."""
        result = runner.invoke(drive_cli.main, ["delete-comment"])
        assert result.exit_code != 0

    def test_create_reply_without_content(self, runner):
        """Test create-reply without --content option."""
        result = runner.invoke(drive_cli.main, ["create-reply", "file_id", "comment_id"])
        assert result.exit_code != 0

    def test_list_replies_without_ids(self, runner):
        """Test list-replies without file_id and comment_id."""
        result = runner.invoke(drive_cli.main, ["list-replies"])
        assert result.exit_code != 0

    def test_comment_output_formats(self, runner):
        """Test that comment commands accept all output formats."""
        for output_fmt in ["unix", "json", "llm"]:
            result = runner.invoke(
                drive_cli.main,
                ["list-comments", "test_id", "--output", output_fmt],
                catch_exceptions=False,
            )
            assert "--output" not in result.output or result.exit_code in [0, 1]
