"""Gmail API operations for gwc-email."""

import base64
import os
import mimetypes
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email import encoders
from typing import Any, Dict, List, Optional
from functools import lru_cache
from googleapiclient.discovery import build, Resource

from ..shared.auth import get_credentials, GMAIL_SCOPES


@lru_cache(maxsize=1)
def build_email_service() -> Resource:
    """Build Gmail API service with caching."""
    creds = get_credentials(scopes=GMAIL_SCOPES)
    return build("gmail", "v1", credentials=creds)


def parse_headers(headers: List[Dict[str, str]]) -> Dict[str, str]:
    """Convert Gmail header list to dict."""
    return {h["name"]: h["value"] for h in headers}


def extract_body(payload: Dict[str, Any]) -> str:
    """Extract message body from MIME payload.

    Handles nested multipart messages and base64url encoding.
    """
    if "body" in payload and "data" in payload["body"]:
        try:
            data = payload["body"]["data"]
            # base64url decode
            return base64.urlsafe_b64decode(data).decode("utf-8", errors="replace")
        except Exception:
            return "[Unable to decode body]"

    # Handle multipart - look for text/plain or text/html
    if "parts" in payload:
        for part in payload["parts"]:
            if part.get("mimeType") in ["text/plain", "text/html"]:
                if "body" in part and "data" in part["body"]:
                    try:
                        data = part["body"]["data"]
                        return base64.urlsafe_b64decode(data).decode("utf-8", errors="replace")
                    except Exception:
                        continue

    return "[No body content]"


def get_label_map() -> Dict[str, str]:
    """Get mapping of label names to IDs.

    Returns:
        Dict mapping label name -> label ID
    """
    service = build_email_service()
    labels = service.users().labels().list(userId="me").execute()

    label_map = {}
    for label in labels.get("labels", []):
        label_map[label["name"]] = label["id"]

    return label_map


def resolve_label_name_to_id(label_name: str) -> Optional[str]:
    """Resolve label name to ID.

    Args:
        label_name: Label name (e.g., "INBOX", "Important")

    Returns:
        Label ID or None if not found
    """
    label_map = get_label_map()
    return label_map.get(label_name)


def list_messages(
    label: str = "INBOX",
    query: str = "",
    max_results: int = 10,
    page_token: Optional[str] = None,
) -> Dict[str, Any]:
    """List messages from a label with optional search.

    Args:
        label: Label name (e.g., "INBOX") or ID
        query: Gmail search query (e.g., "from:user@example.com")
        max_results: Max messages to return
        page_token: Token for pagination

    Returns:
        Dict with 'messages' list and 'nextPageToken' if more results
    """
    service = build_email_service()

    # Resolve label name to ID if needed
    if not label.startswith("CATEGORY_"):
        label_map = get_label_map()
        label_id = label_map.get(label, label)
    else:
        label_id = label

    params = {
        "userId": "me",
        "maxResults": min(max_results, 100),  # API max is 100 per page
        "fields": "messages(id,threadId,labelIds,snippet,internalDate),nextPageToken",
    }

    if label_id:
        params["labelIds"] = [label_id]

    if query:
        params["q"] = query

    if page_token:
        params["pageToken"] = page_token

    return service.users().messages().list(**params).execute()


def get_message(
    message_id: str,
    format: str = "full",
) -> Dict[str, Any]:
    """Get full message details.

    Args:
        message_id: Message ID
        format: "full" for complete, "minimal" for minimal headers

    Returns:
        Message object with headers, payload, etc.
    """
    service = build_email_service()

    return service.users().messages().get(
        userId="me",
        id=message_id,
        format=format,
    ).execute()


def search_messages(
    query: str,
    max_results: int = 10,
) -> List[Dict[str, Any]]:
    """Search messages using Gmail search syntax.

    Args:
        query: Gmail search query (e.g., "from:alice@example.com", "subject:urgent")
        max_results: Max results to return

    Returns:
        List of message objects
    """
    if not query:
        return []

    service = build_email_service()

    results = service.users().messages().list(
        userId="me",
        q=query,
        maxResults=min(max_results, 100),
        fields="messages(id,threadId,labelIds,snippet,internalDate),nextPageToken",
    ).execute()

    return results.get("messages", [])


def list_labels() -> List[Dict[str, Any]]:
    """List all labels.

    Returns:
        List of label objects with name, ID, and properties
    """
    service = build_email_service()
    results = service.users().labels().list(userId="me").execute()
    return results.get("labels", [])


def get_label(label_id: str) -> Dict[str, Any]:
    """Get label details.

    Args:
        label_id: Label ID

    Returns:
        Label object
    """
    service = build_email_service()
    return service.users().labels().get(userId="me", id=label_id).execute()


def get_label_by_name(label_name: str) -> Optional[Dict[str, Any]]:
    """Get label by name.

    Args:
        label_name: Label name (e.g., "INBOX", "Important")

    Returns:
        Label object or None if not found
    """
    label_id = resolve_label_name_to_id(label_name)
    if label_id:
        return get_label(label_id)
    return None


def format_message_for_display(message: Dict[str, Any]) -> Dict[str, Any]:
    """Format message for display/output.

    Args:
        message: Full message object from get_message()

    Returns:
        Formatted message with extracted fields
    """
    headers = parse_headers(message.get("payload", {}).get("headers", []))

    return {
        "id": message.get("id"),
        "threadId": message.get("threadId"),
        "from": headers.get("From", "Unknown"),
        "to": headers.get("To", ""),
        "cc": headers.get("Cc", ""),
        "subject": headers.get("Subject", "(no subject)"),
        "date": headers.get("Date", ""),
        "internalDate": message.get("internalDate"),
        "snippet": message.get("snippet", ""),
        "labelIds": message.get("labelIds", []),
        "body": extract_body(message.get("payload", {}))[:500] + "...",  # First 500 chars
    }


def batch_get_messages(message_ids: List[str]) -> List[Dict[str, Any]]:
    """Get multiple messages efficiently.

    Gmail API doesn't have a true batch.get for messages, so we fetch individually.
    Consider this for future optimization if needed.

    Args:
        message_ids: List of message IDs

    Returns:
        List of message objects
    """
    messages = []
    for msg_id in message_ids[:100]:  # Limit to 100
        try:
            msg = get_message(msg_id)
            messages.append(msg)
        except Exception:
            # Skip messages that can't be retrieved
            continue

    return messages


def get_message_threads(thread_id: str) -> List[Dict[str, Any]]:
    """Get all messages in a thread.

    Args:
        thread_id: Thread ID

    Returns:
        List of message objects in thread
    """
    service = build_email_service()

    thread = service.users().threads().get(
        userId="me",
        id=thread_id,
        format="full",
    ).execute()

    return thread.get("messages", [])


def get_common_search_examples() -> Dict[str, str]:
    """Return common Gmail search query examples."""
    return {
        "from_email": "from:user@example.com",
        "to_email": "to:alice@example.com",
        "subject": "subject:urgent",
        "has_attachment": "has:attachment",
        "is_unread": "is:unread",
        "before_date": "before:2025-01-01",
        "after_date": "after:2025-01-01",
        "larger_than": "larger:1M",
        "filename": "filename:pdf",
        "in_label": "label:Important",
    }


# ============================================================================
# Message Composition & Sending
# ============================================================================


def create_message(
    to: str,
    subject: str,
    body: str,
    cc: str = "",
    bcc: str = "",
    attachments: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Create a message object for sending.

    Args:
        to: Recipient email address (required)
        subject: Message subject (required)
        body: Message body (plain text)
        cc: CC recipients (comma-separated)
        bcc: BCC recipients (comma-separated)
        attachments: List of file paths to attach

    Returns:
        Message dict ready for sending to Gmail API
    """
    if attachments is None:
        attachments = []

    if attachments:
        message = MIMEMultipart()
    else:
        message = MIMEText(body)
        message["To"] = to
        message["Subject"] = subject
        if cc:
            message["Cc"] = cc
        if bcc:
            message["Bcc"] = bcc

        return {"raw": base64.urlsafe_b64encode(message.as_bytes()).decode()}

    # Handle multipart with attachments
    message["To"] = to
    message["Subject"] = subject
    if cc:
        message["Cc"] = cc
    if bcc:
        message["Bcc"] = bcc

    # Add body
    message.attach(MIMEText(body, "plain"))

    # Add attachments
    for file_path in attachments:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Attachment not found: {file_path}")

        filename = os.path.basename(file_path)
        mime_type, encoding = mimetypes.guess_type(file_path)

        if mime_type is None:
            mime_type = "application/octet-stream"

        maintype, subtype = mime_type.split("/", 1)

        try:
            with open(file_path, "rb") as attachment:
                part = MIMEBase(maintype, subtype)
                part.set_payload(attachment.read())

            encoders.encode_base64(part)
            part.add_header("Content-Disposition", "attachment", filename=filename)
            message.attach(part)

        except Exception as e:
            raise IOError(f"Failed to attach {file_path}: {e}")

    return {"raw": base64.urlsafe_b64encode(message.as_bytes()).decode()}


def send_message(
    to: str,
    subject: str,
    body: str,
    cc: str = "",
    bcc: str = "",
    attachments: Optional[List[str]] = None,
) -> str:
    """Send a message directly (no draft).

    Args:
        to: Recipient email address
        subject: Message subject
        body: Message body
        cc: CC recipients
        bcc: BCC recipients
        attachments: List of file paths to attach

    Returns:
        Message ID of sent message
    """
    service = build_email_service()

    message = create_message(to, subject, body, cc, bcc, attachments)

    result = service.users().messages().send(userId="me", body=message).execute()

    return result.get("id", "")


def create_draft(
    to: str,
    subject: str,
    body: str,
    cc: str = "",
    bcc: str = "",
    attachments: Optional[List[str]] = None,
) -> str:
    """Create a draft message (unsent).

    Args:
        to: Recipient email address
        subject: Message subject
        body: Message body
        cc: CC recipients
        bcc: BCC recipients
        attachments: List of file paths to attach

    Returns:
        Draft ID
    """
    service = build_email_service()

    message = create_message(to, subject, body, cc, bcc, attachments)

    draft = service.users().drafts().create(userId="me", body={"message": message}).execute()

    return draft.get("id", "")


def list_drafts(max_results: int = 10) -> List[Dict[str, Any]]:
    """List all draft messages.

    Args:
        max_results: Max drafts to return

    Returns:
        List of draft objects
    """
    service = build_email_service()

    results = service.users().drafts().list(
        userId="me",
        maxResults=min(max_results, 100),
        fields="drafts(id,message(id,threadId,snippet,internalDate))",
    ).execute()

    return results.get("drafts", [])


def get_draft(draft_id: str) -> Dict[str, Any]:
    """Get a draft message.

    Args:
        draft_id: Draft ID

    Returns:
        Draft object with full message content
    """
    service = build_email_service()

    return service.users().drafts().get(userId="me", id=draft_id, format="full").execute()


def send_draft(draft_id: str) -> str:
    """Send an existing draft.

    Args:
        draft_id: Draft ID to send

    Returns:
        Message ID of sent message
    """
    service = build_email_service()

    result = service.users().drafts().send(userId="me", body={"id": draft_id}).execute()

    return result.get("id", "")


def update_draft(
    draft_id: str,
    to: str,
    subject: str,
    body: str,
    cc: str = "",
    bcc: str = "",
    attachments: Optional[List[str]] = None,
) -> str:
    """Update/replace a draft message.

    Args:
        draft_id: Draft ID to update
        to: Recipient email address
        subject: Message subject
        body: Message body
        cc: CC recipients
        bcc: BCC recipients
        attachments: List of file paths to attach

    Returns:
        Updated draft ID
    """
    service = build_email_service()

    message = create_message(to, subject, body, cc, bcc, attachments)

    result = service.users().drafts().update(
        userId="me",
        id=draft_id,
        body={"message": message},
    ).execute()

    return result.get("id", "")


def delete_draft(draft_id: str) -> None:
    """Delete a draft message.

    Args:
        draft_id: Draft ID to delete
    """
    service = build_email_service()
    service.users().drafts().delete(userId="me", id=draft_id).execute()


def reply_to_message(
    message_id: str,
    reply_body: str,
    all_recipients: bool = False,
) -> str:
    """Reply to a message.

    Args:
        message_id: Message ID to reply to
        reply_body: Reply message body
        all_recipients: If True, reply to all; if False, reply to sender only

    Returns:
        Message ID of reply
    """
    service = build_email_service()

    # Get original message
    original = get_message(message_id)
    headers = parse_headers(original.get("payload", {}).get("headers", []))

    # Get recipient
    from_addr = headers.get("From", "")
    subject = headers.get("Subject", "(no subject)")
    thread_id = original.get("threadId")

    # Create reply subject
    if not subject.startswith("Re:"):
        reply_subject = f"Re: {subject}"
    else:
        reply_subject = subject

    # Create reply message
    if all_recipients:
        # Reply to all
        to = from_addr
        cc = headers.get("Cc", "")
    else:
        # Reply to sender only
        to = from_addr
        cc = ""

    message = create_message(to, reply_subject, reply_body, cc)

    # Send in thread
    result = service.users().messages().send(
        userId="me",
        body=message,
    ).execute()

    return result.get("id", "")


def forward_message(
    message_id: str,
    to: str,
    subject: str = "",
    body: str = "",
) -> str:
    """Forward a message to recipients.

    Args:
        message_id: Message ID to forward
        to: Recipient to forward to
        subject: Custom subject (optional)
        body: Additional text to include (optional)

    Returns:
        Message ID of forwarded message
    """
    service = build_email_service()

    # Get original message
    original = get_message(message_id)
    headers = parse_headers(original.get("payload", {}).get("headers", []))
    original_subject = headers.get("Subject", "(no subject)")

    # Create forward subject
    if not subject:
        if not original_subject.startswith("Fwd:"):
            subject = f"Fwd: {original_subject}"
        else:
            subject = original_subject

    # Create forward message
    original_from = headers.get("From", "Unknown")
    original_date = headers.get("Date", "")
    original_body = extract_body(original.get("payload", {}))

    forward_text = body + "\n\n" if body else ""
    forward_text += f"---------- Forwarded message --------- \nFrom: {original_from}\nDate: {original_date}\nSubject: {original_subject}\n\n{original_body}"

    message = create_message(to, subject, forward_text)

    # Send forward
    result = service.users().messages().send(
        userId="me",
        body=message,
    ).execute()

    return result.get("id", "")


# ============================================================================
# Message Organization & Batch Operations (Phase 3)
# ============================================================================


def create_label(name: str, labelListVisibility: str = "labelShow") -> str:
    """Create a new label.

    Args:
        name: Label name (e.g., "Project X")
        labelListVisibility: "labelShow" (default) or "labelHide"

    Returns:
        Label ID of the created label
    """
    service = build_email_service()

    label_object = {
        "name": name,
        "labelListVisibility": labelListVisibility,
    }

    result = service.users().labels().create(userId="me", body=label_object).execute()

    return result.get("id", "")


def add_label_to_message(message_id: str, label_name: str) -> None:
    """Add a label to a message.

    Args:
        message_id: Message ID
        label_name: Label name (e.g., "Important", "Project X")
    """
    service = build_email_service()

    # Resolve label name to ID
    label_id = resolve_label_name_to_id(label_name)
    if not label_id:
        raise ValueError(f"Label '{label_name}' not found")

    # Get current labels
    message = get_message(message_id)
    current_labels = message.get("labelIds", [])

    # Add new label if not already present
    if label_id not in current_labels:
        current_labels.append(label_id)

    # Update message with new labels
    service.users().messages().modify(
        userId="me",
        id=message_id,
        body={"addLabelIds": [label_id]},
    ).execute()


def remove_label_from_message(message_id: str, label_name: str) -> None:
    """Remove a label from a message.

    Args:
        message_id: Message ID
        label_name: Label name (e.g., "Important", "Project X")
    """
    service = build_email_service()

    # Resolve label name to ID
    label_id = resolve_label_name_to_id(label_name)
    if not label_id:
        raise ValueError(f"Label '{label_name}' not found")

    # Remove label
    service.users().messages().modify(
        userId="me",
        id=message_id,
        body={"removeLabelIds": [label_id]},
    ).execute()


def set_message_read(message_id: str) -> None:
    """Mark a message as read.

    Args:
        message_id: Message ID
    """
    service = build_email_service()

    service.users().messages().modify(
        userId="me",
        id=message_id,
        body={"removeLabelIds": ["UNREAD"]},
    ).execute()


def set_message_unread(message_id: str) -> None:
    """Mark a message as unread.

    Args:
        message_id: Message ID
    """
    service = build_email_service()

    service.users().messages().modify(
        userId="me",
        id=message_id,
        body={"addLabelIds": ["UNREAD"]},
    ).execute()


def archive_message(message_id: str) -> None:
    """Archive a message (remove from INBOX).

    Args:
        message_id: Message ID
    """
    service = build_email_service()

    service.users().messages().modify(
        userId="me",
        id=message_id,
        body={"removeLabelIds": ["INBOX"]},
    ).execute()


def unarchive_message(message_id: str) -> None:
    """Restore a message to INBOX.

    Args:
        message_id: Message ID
    """
    service = build_email_service()

    service.users().messages().modify(
        userId="me",
        id=message_id,
        body={"addLabelIds": ["INBOX"]},
    ).execute()


def mark_message_spam(message_id: str) -> None:
    """Mark a message as spam and move to Spam label.

    Args:
        message_id: Message ID
    """
    service = build_email_service()

    service.users().messages().modify(
        userId="me",
        id=message_id,
        body={"addLabelIds": ["SPAM"], "removeLabelIds": ["INBOX"]},
    ).execute()


def permanently_delete_message(message_id: str) -> None:
    """Permanently delete a message.

    Args:
        message_id: Message ID
    """
    service = build_email_service()

    service.users().messages().delete(userId="me", id=message_id).execute()


def batch_add_label(message_ids: List[str], label_name: str) -> Dict[str, Any]:
    """Add a label to multiple messages.

    Args:
        message_ids: List of message IDs
        label_name: Label name

    Returns:
        Dict with success/failure counts
    """
    service = build_email_service()

    # Resolve label name to ID
    label_id = resolve_label_name_to_id(label_name)
    if not label_id:
        raise ValueError(f"Label '{label_name}' not found")

    success_count = 0
    failure_count = 0
    errors = []

    for msg_id in message_ids:
        try:
            service.users().messages().modify(
                userId="me",
                id=msg_id,
                body={"addLabelIds": [label_id]},
            ).execute()
            success_count += 1
        except Exception as e:
            failure_count += 1
            errors.append({"message_id": msg_id, "error": str(e)})

    return {
        "success_count": success_count,
        "failure_count": failure_count,
        "errors": errors,
    }


def batch_remove_label(message_ids: List[str], label_name: str) -> Dict[str, Any]:
    """Remove a label from multiple messages.

    Args:
        message_ids: List of message IDs
        label_name: Label name

    Returns:
        Dict with success/failure counts
    """
    service = build_email_service()

    # Resolve label name to ID
    label_id = resolve_label_name_to_id(label_name)
    if not label_id:
        raise ValueError(f"Label '{label_name}' not found")

    success_count = 0
    failure_count = 0
    errors = []

    for msg_id in message_ids:
        try:
            service.users().messages().modify(
                userId="me",
                id=msg_id,
                body={"removeLabelIds": [label_id]},
            ).execute()
            success_count += 1
        except Exception as e:
            failure_count += 1
            errors.append({"message_id": msg_id, "error": str(e)})

    return {
        "success_count": success_count,
        "failure_count": failure_count,
        "errors": errors,
    }


def batch_set_read(message_ids: List[str]) -> Dict[str, Any]:
    """Mark multiple messages as read.

    Args:
        message_ids: List of message IDs

    Returns:
        Dict with success/failure counts
    """
    service = build_email_service()

    success_count = 0
    failure_count = 0
    errors = []

    for msg_id in message_ids:
        try:
            service.users().messages().modify(
                userId="me",
                id=msg_id,
                body={"removeLabelIds": ["UNREAD"]},
            ).execute()
            success_count += 1
        except Exception as e:
            failure_count += 1
            errors.append({"message_id": msg_id, "error": str(e)})

    return {
        "success_count": success_count,
        "failure_count": failure_count,
        "errors": errors,
    }


def batch_set_unread(message_ids: List[str]) -> Dict[str, Any]:
    """Mark multiple messages as unread.

    Args:
        message_ids: List of message IDs

    Returns:
        Dict with success/failure counts
    """
    service = build_email_service()

    success_count = 0
    failure_count = 0
    errors = []

    for msg_id in message_ids:
        try:
            service.users().messages().modify(
                userId="me",
                id=msg_id,
                body={"addLabelIds": ["UNREAD"]},
            ).execute()
            success_count += 1
        except Exception as e:
            failure_count += 1
            errors.append({"message_id": msg_id, "error": str(e)})

    return {
        "success_count": success_count,
        "failure_count": failure_count,
        "errors": errors,
    }


def batch_archive(message_ids: List[str]) -> Dict[str, Any]:
    """Archive multiple messages.

    Args:
        message_ids: List of message IDs

    Returns:
        Dict with success/failure counts
    """
    service = build_email_service()

    success_count = 0
    failure_count = 0
    errors = []

    for msg_id in message_ids:
        try:
            service.users().messages().modify(
                userId="me",
                id=msg_id,
                body={"removeLabelIds": ["INBOX"]},
            ).execute()
            success_count += 1
        except Exception as e:
            failure_count += 1
            errors.append({"message_id": msg_id, "error": str(e)})

    return {
        "success_count": success_count,
        "failure_count": failure_count,
        "errors": errors,
    }


def batch_delete(message_ids: List[str]) -> Dict[str, Any]:
    """Permanently delete multiple messages.

    Args:
        message_ids: List of message IDs

    Returns:
        Dict with success/failure counts
    """
    service = build_email_service()

    success_count = 0
    failure_count = 0
    errors = []

    for msg_id in message_ids:
        try:
            service.users().messages().delete(userId="me", id=msg_id).execute()
            success_count += 1
        except Exception as e:
            failure_count += 1
            errors.append({"message_id": msg_id, "error": str(e)})

    return {
        "success_count": success_count,
        "failure_count": failure_count,
        "errors": errors,
    }


# ============================================================================
# Advanced Features (Phase 4)
# ============================================================================


def create_filter(
    criteria: Dict[str, Any],
    action: Dict[str, Any],
) -> str:
    """Create a message filter/rule.

    Args:
        criteria: Filter criteria (from, to, subject, hasAttachment, query, etc.)
            Example: {"from": "sender@example.com", "subject": "urgent"}
        action: Actions to apply (addLabelIds, removeLabel, archive, delete, etc.)
            Example: {"addLabelIds": ["label_id"], "archive": True}

    Returns:
        Filter ID
    """
    service = build_email_service()

    filter_object = {
        "criteria": criteria,
        "action": action,
    }

    result = service.users().settings().filters().create(userId="me", body=filter_object).execute()

    return result.get("id", "")


def list_filters() -> List[Dict[str, Any]]:
    """List all message filters.

    Returns:
        List of filter objects
    """
    service = build_email_service()

    result = service.users().settings().filters().list(userId="me").execute()

    return result.get("filter", [])


def get_filter(filter_id: str) -> Dict[str, Any]:
    """Get filter details.

    Args:
        filter_id: Filter ID

    Returns:
        Filter object
    """
    service = build_email_service()

    return service.users().settings().filters().get(userId="me", id=filter_id).execute()


def delete_filter(filter_id: str) -> None:
    """Delete a message filter.

    Args:
        filter_id: Filter ID to delete
    """
    service = build_email_service()

    service.users().settings().filters().delete(userId="me", id=filter_id).execute()


def get_signature(send_as: Optional[str] = None) -> str:
    """Get email signature.

    Args:
        send_as: Send-as address (defaults to primary email)

    Returns:
        Signature text
    """
    service = build_email_service()

    if not send_as:
        send_as = "me"

    result = service.users().settings().sendAs().get(userId="me", sendAsEmail=send_as).execute()

    return result.get("signature", "")


def update_signature(signature_text: str, send_as: Optional[str] = None) -> None:
    """Update email signature.

    Args:
        signature_text: New signature text (can include HTML)
        send_as: Send-as address (defaults to primary email)
    """
    service = build_email_service()

    if not send_as:
        send_as = "me"

    body = {"signature": signature_text}

    service.users().settings().sendAs().patch(userId="me", sendAsEmail=send_as, body=body).execute()


def list_signatures() -> List[Dict[str, Any]]:
    """List all email signatures (for all send-as addresses).

    Returns:
        List of send-as configurations with signatures
    """
    service = build_email_service()

    result = service.users().settings().sendAs().list(userId="me").execute()

    return result.get("sendAs", [])


def create_auto_responder(
    enabled: bool,
    response_text: str,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    response_subject: Optional[str] = None,
) -> None:
    """Create or update vacation auto-responder.

    Args:
        enabled: Whether auto-responder is active
        response_text: Message to send in response
        start_time: Start time (ISO8601 format, e.g., "2025-12-01T00:00:00Z")
        end_time: End time (ISO8601 format)
        response_subject: Subject line for auto-response (optional)
    """
    service = build_email_service()

    vacation_settings = {
        "enableAutoReply": enabled,
        "responseBodyHtml": response_text,
    }

    if response_subject:
        vacation_settings["responseSubject"] = response_subject

    if start_time:
        vacation_settings["startTime"] = start_time

    if end_time:
        vacation_settings["endTime"] = end_time

    # Note: restrictToContacts and restrictToDomain can be added here for more control
    vacation_settings["restrictToContacts"] = False  # Respond to all
    vacation_settings["restrictToDomain"] = False    # Respond to all domains

    service.users().settings().updateVacationSettings(userId="me", body=vacation_settings).execute()


def get_auto_responder() -> Dict[str, Any]:
    """Get current auto-responder/vacation settings.

    Returns:
        Vacation settings dict with enabled, response_text, start/end times, etc.
    """
    service = build_email_service()

    return service.users().settings().getVacationSettings(userId="me").execute()


def disable_auto_responder() -> None:
    """Disable the auto-responder."""
    service = build_email_service()

    vacation_settings = {"enableAutoReply": False}

    service.users().settings().updateVacationSettings(userId="me", body=vacation_settings).execute()


def create_template(
    name: str,
    body: str,
    subject: str = "",
) -> str:
    """Create a message template.

    Note: Gmail API doesn't have native templates, so we store them as
    drafts with a special naming convention: "__template__<name>"

    Args:
        name: Template name
        body: Template body text
        subject: Template subject line (optional)

    Returns:
        Draft ID of the template
    """
    service = build_email_service()

    # Create a special draft that serves as a template
    # Using a naming convention to identify templates
    template_subject = f"__template__{name}"

    message = MIMEText(body)
    message["To"] = ""  # Empty - templates have no recipient
    message["Subject"] = template_subject
    message["X-Template-Name"] = name

    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()

    draft = service.users().drafts().create(
        userId="me",
        body={"message": {"raw": raw}},
    ).execute()

    return draft.get("id", "")


def list_templates() -> List[Dict[str, Any]]:
    """List all message templates.

    Returns:
        List of template objects (stored as special drafts)
    """
    service = build_email_service()

    # Get all drafts and filter for templates
    results = service.users().drafts().list(
        userId="me",
        maxResults=100,
        q="subject:__template__",
    ).execute()

    drafts = results.get("drafts", [])
    templates = []

    for draft in drafts:
        draft_id = draft.get("id")
        msg = draft.get("message", {})
        headers = parse_headers(msg.get("payload", {}).get("headers", []))
        subject = headers.get("Subject", "")

        # Extract template name from subject
        if subject.startswith("__template__"):
            template_name = subject.replace("__template__", "")
            templates.append({
                "id": draft_id,
                "name": template_name,
                "subject": headers.get("X-Template-Name", template_name),
            })

    return templates


def get_template(template_id: str) -> Dict[str, Any]:
    """Get a template by ID.

    Args:
        template_id: Template draft ID

    Returns:
        Template dict with name, subject, and body
    """
    service = build_email_service()

    draft = service.users().drafts().get(userId="me", id=template_id, format="full").execute()

    msg = draft.get("message", {})
    headers = parse_headers(msg.get("payload", {}).get("headers", []))
    body = extract_body(msg.get("payload", {}))
    subject = headers.get("Subject", "")

    template_name = subject.replace("__template__", "") if subject.startswith("__template__") else ""

    return {
        "id": template_id,
        "name": template_name,
        "subject": headers.get("X-Template-Name", ""),
        "body": body,
    }


def delete_template(template_id: str) -> None:
    """Delete a template.

    Args:
        template_id: Template draft ID to delete
    """
    service = build_email_service()

    service.users().drafts().delete(userId="me", id=template_id).execute()


def use_template(
    template_id: str,
    to: str,
    subject_override: Optional[str] = None,
) -> str:
    """Create a draft from a template.

    Args:
        template_id: Template draft ID
        to: Recipient email address
        subject_override: Override template subject (optional)

    Returns:
        New draft ID
    """
    service = build_email_service()

    # Get the template
    template = get_template(template_id)
    template_body = template.get("body", "")
    template_subject = subject_override or template.get("subject", "")

    # Create new draft with template content
    message = MIMEText(template_body)
    message["To"] = to
    message["Subject"] = template_subject

    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()

    draft = service.users().drafts().create(
        userId="me",
        body={"message": {"raw": raw}},
    ).execute()

    return draft.get("id", "")
