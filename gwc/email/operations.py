"""Gmail API operations for gwc-email."""

import base64
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
