"""Tests for Gmail operations."""

import pytest
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from gwc.email.operations import (
    parse_headers,
    extract_body,
    format_message_for_display,
    get_common_search_examples,
    create_message,
    reply_to_message,
    forward_message,
)


class TestParseHeaders:
    """Test Gmail header parsing."""

    def test_parse_headers_basic(self):
        """Test basic header parsing."""
        headers = [
            {"name": "From", "value": "alice@example.com"},
            {"name": "To", "value": "bob@example.com"},
            {"name": "Subject", "value": "Test"},
        ]

        result = parse_headers(headers)

        assert result["From"] == "alice@example.com"
        assert result["To"] == "bob@example.com"
        assert result["Subject"] == "Test"

    def test_parse_headers_empty(self):
        """Test empty headers list."""
        result = parse_headers([])
        assert result == {}

    def test_parse_headers_duplicate_names(self):
        """Test headers with duplicate names (last wins)."""
        headers = [
            {"name": "X-Custom", "value": "first"},
            {"name": "X-Custom", "value": "second"},
        ]

        result = parse_headers(headers)
        assert result["X-Custom"] == "second"


class TestExtractBody:
    """Test Gmail message body extraction."""

    def test_extract_body_simple(self):
        """Test extracting body from simple payload."""
        import base64

        text = "Hello, world!"
        encoded = base64.urlsafe_b64encode(text.encode()).decode()

        payload = {"body": {"data": encoded}}

        result = extract_body(payload)
        assert result == text

    def test_extract_body_multipart(self):
        """Test extracting body from multipart message."""
        import base64

        text = "This is the text part"
        encoded = base64.urlsafe_b64encode(text.encode()).decode()

        payload = {
            "parts": [
                {
                    "mimeType": "text/plain",
                    "body": {"data": encoded},
                }
            ]
        }

        result = extract_body(payload)
        assert result == text

    def test_extract_body_no_content(self):
        """Test extracting body with no content."""
        payload = {}

        result = extract_body(payload)
        assert result == "[No body content]"

    def test_extract_body_decode_error(self):
        """Test handling of decode errors."""
        payload = {"body": {"data": "invalid_base64!!!"}}

        result = extract_body(payload)
        # Should not crash, returns error message
        assert "[Unable to decode body]" in result or "invalid_base64" in result

    def test_extract_body_prefers_plain_text(self):
        """Test that plain text is preferred over HTML."""
        import base64

        plain_text = "This is plain"
        html_text = "<p>This is HTML</p>"

        plain_encoded = base64.urlsafe_b64encode(plain_text.encode()).decode()
        html_encoded = base64.urlsafe_b64encode(html_text.encode()).decode()

        payload = {
            "parts": [
                {"mimeType": "text/plain", "body": {"data": plain_encoded}},
                {"mimeType": "text/html", "body": {"data": html_encoded}},
            ]
        }

        result = extract_body(payload)
        # Should get the plain text version (whichever comes first)
        assert "plain" in result.lower()


class TestFormatMessageForDisplay:
    """Test message formatting for display."""

    def test_format_message_basic(self):
        """Test basic message formatting."""
        message = {
            "id": "msg123",
            "threadId": "thread456",
            "snippet": "Hello world",
            "internalDate": "1700000000000",
            "labelIds": ["INBOX"],
            "payload": {
                "headers": [
                    {"name": "From", "value": "alice@example.com"},
                    {"name": "To", "value": "bob@example.com"},
                    {"name": "Subject", "value": "Test"},
                ],
                "body": {},
            },
        }

        result = format_message_for_display(message)

        assert result["id"] == "msg123"
        assert result["threadId"] == "thread456"
        assert result["from"] == "alice@example.com"
        assert result["to"] == "bob@example.com"
        assert result["subject"] == "Test"

    def test_format_message_missing_headers(self):
        """Test formatting with missing headers."""
        message = {
            "id": "msg123",
            "threadId": "thread456",
            "snippet": "Test",
            "payload": {"headers": []},
        }

        result = format_message_for_display(message)

        assert result["from"] == "Unknown"
        assert result["subject"] == "(no subject)"

    def test_format_message_long_snippet(self):
        """Test that snippet is truncated."""
        long_snippet = "x" * 1000
        message = {
            "id": "msg123",
            "threadId": "thread456",
            "snippet": long_snippet,
            "payload": {"headers": []},
        }

        result = format_message_for_display(message)

        # Body should be truncated with ellipsis
        assert len(result["body"]) < len(long_snippet)


class TestCommonSearchExamples:
    """Test search query examples."""

    def test_get_common_search_examples(self):
        """Test that common search examples are defined."""
        examples = get_common_search_examples()

        assert "from_email" in examples
        assert "to_email" in examples
        assert "subject" in examples
        assert "has_attachment" in examples
        assert "is_unread" in examples

    def test_search_examples_are_valid_queries(self):
        """Test that examples are valid Gmail search queries."""
        examples = get_common_search_examples()

        for name, query in examples.items():
            # Basic validation: queries should contain : or keywords
            assert ":" in query or "is:" in query or "has:" in query, f"Invalid query: {query}"


# ============================================================================
# Phase 2: Compose Operations Tests
# ============================================================================


class TestCreateMessage:
    """Test message creation for sending."""

    def test_create_simple_message(self):
        """Test creating a simple text message."""
        result = create_message(
            to="alice@example.com",
            subject="Test",
            body="Hello world",
        )

        assert "raw" in result
        assert result["raw"]  # Should have base64 encoded data

    def test_create_message_with_cc_bcc(self):
        """Test message with CC and BCC."""
        result = create_message(
            to="alice@example.com",
            subject="Test",
            body="Hello",
            cc="bob@example.com",
            bcc="charlie@example.com",
        )

        assert "raw" in result
        # The raw field should contain encoded message with headers
        assert isinstance(result["raw"], str)

    def test_create_message_with_attachment(self):
        """Test message with file attachment."""
        # Create a temporary file
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
            f.write("Test file content")
            temp_file = f.name

        try:
            result = create_message(
                to="alice@example.com",
                subject="Test",
                body="See attached",
                attachments=[temp_file],
            )

            assert "raw" in result
            assert result["raw"]
        finally:
            os.unlink(temp_file)

    def test_create_message_nonexistent_attachment(self):
        """Test error handling for missing attachment."""
        with pytest.raises(FileNotFoundError):
            create_message(
                to="alice@example.com",
                subject="Test",
                body="Attached",
                attachments=["/nonexistent/file.pdf"],
            )

    def test_create_message_multiple_attachments(self):
        """Test message with multiple attachments."""
        temp_files = []
        try:
            # Create multiple temp files
            for i in range(2):
                with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
                    f.write(f"File {i}")
                    temp_files.append(f.name)

            result = create_message(
                to="alice@example.com",
                subject="Test",
                body="Multiple attachments",
                attachments=temp_files,
            )

            assert "raw" in result
            assert result["raw"]
        finally:
            for f in temp_files:
                if os.path.exists(f):
                    os.unlink(f)


class TestReplyMessage:
    """Test reply to message operations."""

    @patch("gwc.email.operations.get_message")
    @patch("gwc.email.operations.build_email_service")
    def test_reply_to_message(self, mock_service, mock_get_message):
        """Test replying to a message."""
        # Mock original message
        mock_get_message.return_value = {
            "id": "msg123",
            "threadId": "thread456",
            "payload": {
                "headers": [
                    {"name": "From", "value": "alice@example.com"},
                    {"name": "To", "value": "me@example.com"},
                    {"name": "Subject", "value": "Hello"},
                    {"name": "Cc", "value": ""},
                ]
            },
        }

        # Mock service
        mock_send = MagicMock(return_value={"id": "reply_msg_id"})
        mock_service.return_value.users().messages().send.return_value = mock_send
        mock_send.execute.return_value = {"id": "reply_msg_id"}

        result = reply_to_message("msg123", "Thanks for your message")

        assert result == "reply_msg_id"
        mock_get_message.assert_called_once_with("msg123")

    @patch("gwc.email.operations.get_message")
    @patch("gwc.email.operations.build_email_service")
    def test_reply_all(self, mock_service, mock_get_message):
        """Test reply all to a message."""
        mock_get_message.return_value = {
            "id": "msg123",
            "threadId": "thread456",
            "payload": {
                "headers": [
                    {"name": "From", "value": "alice@example.com"},
                    {"name": "To", "value": "me@example.com"},
                    {"name": "Subject", "value": "Hello"},
                    {"name": "Cc", "value": "bob@example.com"},
                ]
            },
        }

        mock_send = MagicMock(return_value={"id": "reply_msg_id"})
        mock_service.return_value.users().messages().send.return_value = mock_send
        mock_send.execute.return_value = {"id": "reply_msg_id"}

        result = reply_to_message("msg123", "Reply all", all_recipients=True)

        assert result == "reply_msg_id"


class TestForwardMessage:
    """Test forward message operations."""

    @patch("gwc.email.operations.get_message")
    @patch("gwc.email.operations.extract_body")
    @patch("gwc.email.operations.build_email_service")
    def test_forward_message(self, mock_service, mock_extract_body, mock_get_message):
        """Test forwarding a message."""
        mock_get_message.return_value = {
            "id": "msg123",
            "threadId": "thread456",
            "payload": {
                "headers": [
                    {"name": "From", "value": "alice@example.com"},
                    {"name": "Subject", "value": "Original"},
                    {"name": "Date", "value": "Mon, 18 Nov 2025 12:00:00 +0000"},
                ]
            },
        }
        mock_extract_body.return_value = "Original message body"

        mock_send = MagicMock(return_value={"id": "forward_msg_id"})
        mock_service.return_value.users().messages().send.return_value = mock_send
        mock_send.execute.return_value = {"id": "forward_msg_id"}

        result = forward_message("msg123", "bob@example.com")

        assert result == "forward_msg_id"
        assert mock_get_message.called


# ============================================================================
# Phase 3: Message Organization & Batch Operations Tests
# ============================================================================


class TestLabelOperations:
    """Test label creation and modification."""

    @patch("gwc.email.operations.build_email_service")
    def test_create_label(self, mock_service):
        """Test creating a new label."""
        from gwc.email.operations import create_label

        mock_create = MagicMock(return_value={"id": "label_123"})
        mock_service.return_value.users().labels().create.return_value = mock_create
        mock_create.execute.return_value = {"id": "label_123"}

        result = create_label("Project X")

        assert result == "label_123"
        mock_service.return_value.users().labels().create.assert_called_once()

    @patch("gwc.email.operations.resolve_label_name_to_id")
    @patch("gwc.email.operations.build_email_service")
    def test_add_label_to_message(self, mock_service, mock_resolve):
        """Test adding a label to a message."""
        from gwc.email.operations import add_label_to_message

        mock_resolve.return_value = "label_123"
        mock_modify = MagicMock()
        mock_service.return_value.users().messages().modify.return_value = mock_modify
        mock_modify.execute.return_value = {}

        add_label_to_message("msg123", "Project X")

        mock_service.return_value.users().messages().modify.assert_called_once()

    @patch("gwc.email.operations.resolve_label_name_to_id")
    def test_add_label_not_found(self, mock_resolve):
        """Test adding non-existent label raises error."""
        from gwc.email.operations import add_label_to_message

        mock_resolve.return_value = None

        with pytest.raises(ValueError):
            add_label_to_message("msg123", "NonExistent")

    @patch("gwc.email.operations.resolve_label_name_to_id")
    @patch("gwc.email.operations.build_email_service")
    def test_remove_label_from_message(self, mock_service, mock_resolve):
        """Test removing a label from a message."""
        from gwc.email.operations import remove_label_from_message

        mock_resolve.return_value = "label_123"
        mock_modify = MagicMock()
        mock_service.return_value.users().messages().modify.return_value = mock_modify
        mock_modify.execute.return_value = {}

        remove_label_from_message("msg123", "Project X")

        mock_service.return_value.users().messages().modify.assert_called_once()


class TestReadUnreadOperations:
    """Test read/unread status management."""

    @patch("gwc.email.operations.build_email_service")
    def test_set_message_read(self, mock_service):
        """Test marking a message as read."""
        from gwc.email.operations import set_message_read

        mock_modify = MagicMock()
        mock_service.return_value.users().messages().modify.return_value = mock_modify
        mock_modify.execute.return_value = {}

        set_message_read("msg123")

        mock_service.return_value.users().messages().modify.assert_called_once()

    @patch("gwc.email.operations.build_email_service")
    def test_set_message_unread(self, mock_service):
        """Test marking a message as unread."""
        from gwc.email.operations import set_message_unread

        mock_modify = MagicMock()
        mock_service.return_value.users().messages().modify.return_value = mock_modify
        mock_modify.execute.return_value = {}

        set_message_unread("msg123")

        mock_service.return_value.users().messages().modify.assert_called_once()


class TestArchiveOperations:
    """Test archive/unarchive operations."""

    @patch("gwc.email.operations.build_email_service")
    def test_archive_message(self, mock_service):
        """Test archiving a message."""
        from gwc.email.operations import archive_message

        mock_modify = MagicMock()
        mock_service.return_value.users().messages().modify.return_value = mock_modify
        mock_modify.execute.return_value = {}

        archive_message("msg123")

        mock_service.return_value.users().messages().modify.assert_called_once()

    @patch("gwc.email.operations.build_email_service")
    def test_unarchive_message(self, mock_service):
        """Test restoring archived message to inbox."""
        from gwc.email.operations import unarchive_message

        mock_modify = MagicMock()
        mock_service.return_value.users().messages().modify.return_value = mock_modify
        mock_modify.execute.return_value = {}

        unarchive_message("msg123")

        mock_service.return_value.users().messages().modify.assert_called_once()


class TestSpamOperations:
    """Test spam marking."""

    @patch("gwc.email.operations.build_email_service")
    def test_mark_message_spam(self, mock_service):
        """Test marking a message as spam."""
        from gwc.email.operations import mark_message_spam

        mock_modify = MagicMock()
        mock_service.return_value.users().messages().modify.return_value = mock_modify
        mock_modify.execute.return_value = {}

        mark_message_spam("msg123")

        mock_service.return_value.users().messages().modify.assert_called_once()


class TestDeleteOperations:
    """Test message deletion."""

    @patch("gwc.email.operations.build_email_service")
    def test_permanently_delete_message(self, mock_service):
        """Test permanently deleting a message."""
        from gwc.email.operations import permanently_delete_message

        mock_delete = MagicMock()
        mock_service.return_value.users().messages().delete.return_value = mock_delete
        mock_delete.execute.return_value = {}

        permanently_delete_message("msg123")

        mock_service.return_value.users().messages().delete.assert_called_once()


class TestBatchOperations:
    """Test batch operations on multiple messages."""

    @patch("gwc.email.operations.resolve_label_name_to_id")
    @patch("gwc.email.operations.build_email_service")
    def test_batch_add_label(self, mock_service, mock_resolve):
        """Test adding label to multiple messages."""
        from gwc.email.operations import batch_add_label

        mock_resolve.return_value = "label_123"
        mock_modify = MagicMock()
        mock_service.return_value.users().messages().modify.return_value = mock_modify
        mock_modify.execute.return_value = {}

        result = batch_add_label(["msg1", "msg2", "msg3"], "Project X")

        assert result["success_count"] == 3
        assert result["failure_count"] == 0
        assert len(result["errors"]) == 0

    @patch("gwc.email.operations.resolve_label_name_to_id")
    @patch("gwc.email.operations.build_email_service")
    def test_batch_add_label_with_failures(self, mock_service, mock_resolve):
        """Test batch add with some failures."""
        from gwc.email.operations import batch_add_label

        mock_resolve.return_value = "label_123"
        mock_modify = MagicMock()
        mock_service.return_value.users().messages().modify.return_value = mock_modify

        # First call succeeds, second fails, third succeeds
        mock_modify.execute.side_effect = [
            {},
            Exception("API Error"),
            {},
        ]

        result = batch_add_label(["msg1", "msg2", "msg3"], "Project X")

        assert result["success_count"] == 2
        assert result["failure_count"] == 1
        assert len(result["errors"]) == 1

    @patch("gwc.email.operations.resolve_label_name_to_id")
    @patch("gwc.email.operations.build_email_service")
    def test_batch_remove_label(self, mock_service, mock_resolve):
        """Test removing label from multiple messages."""
        from gwc.email.operations import batch_remove_label

        mock_resolve.return_value = "label_123"
        mock_modify = MagicMock()
        mock_service.return_value.users().messages().modify.return_value = mock_modify
        mock_modify.execute.return_value = {}

        result = batch_remove_label(["msg1", "msg2"], "Project X")

        assert result["success_count"] == 2
        assert result["failure_count"] == 0

    @patch("gwc.email.operations.build_email_service")
    def test_batch_set_read(self, mock_service):
        """Test marking multiple messages as read."""
        from gwc.email.operations import batch_set_read

        mock_modify = MagicMock()
        mock_service.return_value.users().messages().modify.return_value = mock_modify
        mock_modify.execute.return_value = {}

        result = batch_set_read(["msg1", "msg2", "msg3"])

        assert result["success_count"] == 3
        assert result["failure_count"] == 0

    @patch("gwc.email.operations.build_email_service")
    def test_batch_set_unread(self, mock_service):
        """Test marking multiple messages as unread."""
        from gwc.email.operations import batch_set_unread

        mock_modify = MagicMock()
        mock_service.return_value.users().messages().modify.return_value = mock_modify
        mock_modify.execute.return_value = {}

        result = batch_set_unread(["msg1", "msg2"])

        assert result["success_count"] == 2
        assert result["failure_count"] == 0

    @patch("gwc.email.operations.build_email_service")
    def test_batch_archive(self, mock_service):
        """Test archiving multiple messages."""
        from gwc.email.operations import batch_archive

        mock_modify = MagicMock()
        mock_service.return_value.users().messages().modify.return_value = mock_modify
        mock_modify.execute.return_value = {}

        result = batch_archive(["msg1", "msg2", "msg3"])

        assert result["success_count"] == 3
        assert result["failure_count"] == 0

    @patch("gwc.email.operations.build_email_service")
    def test_batch_delete(self, mock_service):
        """Test permanently deleting multiple messages."""
        from gwc.email.operations import batch_delete

        mock_delete = MagicMock()
        mock_service.return_value.users().messages().delete.return_value = mock_delete
        mock_delete.execute.return_value = {}

        result = batch_delete(["msg1", "msg2", "msg3", "msg4"])

        assert result["success_count"] == 4
        assert result["failure_count"] == 0
        assert mock_service.return_value.users().messages().delete.call_count == 4
