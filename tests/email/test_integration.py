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


# ============================================================================
# Phase 2: Compose Commands Tests
# ============================================================================


class TestComposeCommands:
    """Test message composition commands."""

    def test_send_help(self, runner):
        """Test send command help."""
        result = runner.invoke(email_cli.main, ["send", "--help"])
        assert result.exit_code == 0
        assert "--to" in result.output
        assert "--subject" in result.output
        assert "--body" in result.output

    def test_send_missing_required_options(self, runner):
        """Test send without required options."""
        result = runner.invoke(email_cli.main, ["send"])
        assert result.exit_code != 0

    def test_send_missing_to(self, runner):
        """Test send without --to option."""
        result = runner.invoke(
            email_cli.main,
            ["send", "--subject", "Test", "--body", "Test body"],
        )
        assert result.exit_code != 0

    def test_send_with_attachments_help(self, runner):
        """Test that send accepts --attachments option."""
        result = runner.invoke(email_cli.main, ["send", "--help"])
        assert result.exit_code == 0
        assert "--attachments" in result.output


class TestDraftCommands:
    """Test draft commands."""

    def test_draft_group_help(self, runner):
        """Test draft group help."""
        result = runner.invoke(email_cli.main, ["draft", "--help"])
        assert result.exit_code == 0
        assert "Manage draft" in result.output

    def test_draft_create_help(self, runner):
        """Test draft create command help."""
        result = runner.invoke(email_cli.main, ["draft", "create", "--help"])
        assert result.exit_code == 0
        assert "--to" in result.output
        assert "--subject" in result.output
        assert "--body" in result.output

    def test_draft_list_help(self, runner):
        """Test draft list command help."""
        result = runner.invoke(email_cli.main, ["draft", "list", "--help"])
        assert result.exit_code == 0
        assert "--limit" in result.output
        assert "--output" in result.output

    def test_draft_get_help(self, runner):
        """Test draft get command help."""
        result = runner.invoke(email_cli.main, ["draft", "get", "--help"])
        assert result.exit_code == 0
        assert "DRAFT_ID" in result.output

    def test_draft_send_help(self, runner):
        """Test draft send command help."""
        result = runner.invoke(email_cli.main, ["draft", "send", "--help"])
        assert result.exit_code == 0
        assert "DRAFT_ID" in result.output

    def test_draft_delete_help(self, runner):
        """Test draft delete command help."""
        result = runner.invoke(email_cli.main, ["draft", "delete", "--help"])
        assert result.exit_code == 0
        assert "DRAFT_ID" in result.output

    def test_draft_create_missing_required(self, runner):
        """Test draft create without required options."""
        result = runner.invoke(email_cli.main, ["draft", "create"])
        assert result.exit_code != 0


class TestReplyForwardCommands:
    """Test reply and forward commands."""

    def test_reply_help(self, runner):
        """Test reply command help."""
        result = runner.invoke(email_cli.main, ["reply", "--help"])
        assert result.exit_code == 0
        assert "MESSAGE_ID" in result.output
        assert "--body" in result.output
        assert "--reply-all" in result.output

    def test_reply_missing_body(self, runner):
        """Test reply without --body."""
        result = runner.invoke(email_cli.main, ["reply", "msg123"])
        assert result.exit_code != 0

    def test_forward_help(self, runner):
        """Test forward command help."""
        result = runner.invoke(email_cli.main, ["forward", "--help"])
        assert result.exit_code == 0
        assert "MESSAGE_ID" in result.output
        assert "--to" in result.output

    def test_forward_missing_to(self, runner):
        """Test forward without --to."""
        result = runner.invoke(email_cli.main, ["forward", "msg123"])
        assert result.exit_code != 0

    def test_forward_missing_message_id(self, runner):
        """Test forward without message ID."""
        result = runner.invoke(
            email_cli.main,
            ["forward", "--to", "alice@example.com"],
        )
        assert result.exit_code != 0


# ============================================================================
# Phase 3: Message Organization & Batch Operations Tests
# ============================================================================


class TestLabelCommands:
    """Test label-related commands."""

    def test_create_label_help(self, runner):
        """Test create-label command help."""
        result = runner.invoke(email_cli.main, ["create-label", "--help"])
        assert result.exit_code == 0
        assert "Create a new label" in result.output

    def test_add_label_help(self, runner):
        """Test add-label command help."""
        result = runner.invoke(email_cli.main, ["add-label", "--help"])
        assert result.exit_code == 0
        assert "Add a label to a message" in result.output

    def test_remove_label_help(self, runner):
        """Test remove-label command help."""
        result = runner.invoke(email_cli.main, ["remove-label", "--help"])
        assert result.exit_code == 0
        assert "Remove a label from a message" in result.output


class TestReadUnreadCommands:
    """Test read/unread status commands."""

    def test_mark_read_help(self, runner):
        """Test mark-read command help."""
        result = runner.invoke(email_cli.main, ["mark-read", "--help"])
        assert result.exit_code == 0
        assert "Mark a message as read" in result.output

    def test_mark_unread_help(self, runner):
        """Test mark-unread command help."""
        result = runner.invoke(email_cli.main, ["mark-unread", "--help"])
        assert result.exit_code == 0
        assert "Mark a message as unread" in result.output


class TestArchiveCommands:
    """Test archive-related commands."""

    def test_archive_help(self, runner):
        """Test archive command help."""
        result = runner.invoke(email_cli.main, ["archive", "--help"])
        assert result.exit_code == 0
        assert "Archive a message" in result.output

    def test_unarchive_help(self, runner):
        """Test unarchive command help."""
        result = runner.invoke(email_cli.main, ["unarchive", "--help"])
        assert result.exit_code == 0
        assert "Restore a message to INBOX" in result.output


class TestSpamDeleteCommands:
    """Test spam and delete commands."""

    def test_spam_help(self, runner):
        """Test spam command help."""
        result = runner.invoke(email_cli.main, ["spam", "--help"])
        assert result.exit_code == 0
        assert "Mark a message as spam" in result.output

    def test_delete_help(self, runner):
        """Test delete command help."""
        result = runner.invoke(email_cli.main, ["delete", "--help"])
        assert result.exit_code == 0
        assert "Permanently delete a message" in result.output

    def test_delete_missing_message_id(self, runner):
        """Test delete without message ID."""
        result = runner.invoke(email_cli.main, ["delete"])
        assert result.exit_code != 0


class TestBatchCommands:
    """Test batch operation commands."""

    def test_batch_add_label_help(self, runner):
        """Test batch-add-label command help."""
        result = runner.invoke(email_cli.main, ["batch-add-label", "--help"])
        assert result.exit_code == 0
        assert "Add a label to multiple messages" in result.output

    def test_batch_remove_label_help(self, runner):
        """Test batch-remove-label command help."""
        result = runner.invoke(email_cli.main, ["batch-remove-label", "--help"])
        assert result.exit_code == 0
        assert "Remove a label from multiple messages" in result.output

    def test_batch_mark_read_help(self, runner):
        """Test batch-mark-read command help."""
        result = runner.invoke(email_cli.main, ["batch-mark-read", "--help"])
        assert result.exit_code == 0
        assert "Mark multiple messages as read" in result.output

    def test_batch_mark_unread_help(self, runner):
        """Test batch-mark-unread command help."""
        result = runner.invoke(email_cli.main, ["batch-mark-unread", "--help"])
        assert result.exit_code == 0
        assert "Mark multiple messages as unread" in result.output

    def test_batch_archive_help(self, runner):
        """Test batch-archive command help."""
        result = runner.invoke(email_cli.main, ["batch-archive", "--help"])
        assert result.exit_code == 0
        assert "Archive multiple messages" in result.output

    def test_batch_delete_help(self, runner):
        """Test batch-delete command help."""
        result = runner.invoke(email_cli.main, ["batch-delete", "--help"])
        assert result.exit_code == 0
        assert "Permanently delete multiple messages" in result.output

    def test_batch_commands_missing_ids(self, runner):
        """Test batch commands without message IDs."""
        result = runner.invoke(email_cli.main, ["batch-mark-read"])
        assert result.exit_code != 0

    def test_batch_add_label_missing_label(self, runner):
        """Test batch-add-label without label name."""
        result = runner.invoke(email_cli.main, ["batch-add-label", "msg1"])
        assert result.exit_code != 0
