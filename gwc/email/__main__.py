"""Gmail CLI commands."""

import click
import json
from typing import Optional
from gwc.email.operations import (
    list_messages,
    get_message,
    search_messages,
    list_labels,
    get_label_by_name,
    format_message_for_display,
    get_label_map,
    get_message_threads,
    get_common_search_examples,
    # Phase 2: Compose operations
    send_message,
    create_draft,
    list_drafts,
    get_draft,
    send_draft,
    update_draft,
    delete_draft,
    reply_to_message,
    forward_message,
)
from gwc.shared.output import format_output


@click.group()
def main():
    """Gmail CLI (gwc-email)."""
    pass


@main.group()
def draft():
    """Manage draft messages."""
    pass


@main.group()
def labels():
    """Manage labels."""
    pass


# ============================================================================
# Message Commands
# ============================================================================


@main.command()
@click.option(
    "--label",
    default="INBOX",
    help='Label to list (default: INBOX). Use "ALL_MAIL" for all messages.',
)
@click.option("--limit", default=10, type=int, help="Max messages to return (1-100)")
@click.option(
    "--query",
    default="",
    help="Gmail search query (e.g., 'from:user@example.com')",
)
@click.option(
    "--output",
    type=click.Choice(["unix", "json", "llm"]),
    default="unix",
    help="Output format",
)
@click.option(
    "--page-token",
    default=None,
    help="Token for pagination (from previous results)",
)
def list(label: str, limit: int, query: str, output: str, page_token: Optional[str]):
    """List messages from a label."""
    try:
        results = list_messages(
            label=label,
            query=query,
            max_results=min(limit, 100),
            page_token=page_token,
        )

        messages = results.get("messages", [])

        if not messages:
            click.echo("No messages found.")
            return

        # Format for output
        data = []
        for msg in messages:
            data.append(
                {
                    "id": msg["id"],
                    "threadId": msg.get("threadId", ""),
                    "snippet": msg.get("snippet", "")[:80],
                    "date": msg.get("internalDate", ""),
                }
            )

        click.echo(format_output(data, output))

        # Show pagination info
        if "nextPageToken" in results:
            click.echo(
                f"\n[More results available. Use --page-token {results['nextPageToken']}]",
                err=True,
            )

    except Exception as e:
        click.echo(f"Error listing messages: {e}", err=True)
        raise click.Abort()


@main.command()
@click.argument("message_id")
@click.option(
    "--output",
    type=click.Choice(["unix", "json", "llm"]),
    default="unix",
    help="Output format",
)
def get(message_id: str, output: str):
    """Get full message details."""
    try:
        message = get_message(message_id)
        formatted = format_message_for_display(message)
        click.echo(format_output([formatted], output))
    except Exception as e:
        click.echo(f"Error getting message: {e}", err=True)
        raise click.Abort()


@main.command()
@click.argument("query")
@click.option("--limit", default=10, type=int, help="Max results (1-100)")
@click.option(
    "--output",
    type=click.Choice(["unix", "json", "llm"]),
    default="unix",
    help="Output format",
)
def search(query: str, limit: int, output: str):
    """Search messages using Gmail search syntax.

    Examples:
        gwc-email search "from:alice@example.com"
        gwc-email search "subject:urgent has:attachment"
        gwc-email search "before:2025-01-01"
    """
    try:
        if not query:
            click.echo("Error: search query required", err=True)
            raise click.Abort()

        messages = search_messages(query, max_results=limit)

        if not messages:
            click.echo("No messages found.")
            return

        # Format for output
        data = []
        for msg in messages:
            data.append(
                {
                    "id": msg["id"],
                    "threadId": msg.get("threadId", ""),
                    "snippet": msg.get("snippet", "")[:80],
                    "date": msg.get("internalDate", ""),
                }
            )

        click.echo(format_output(data, output))

    except Exception as e:
        click.echo(f"Error searching: {e}", err=True)
        raise click.Abort()


@main.command()
def search_help():
    """Show common search queries."""
    examples = get_common_search_examples()

    click.echo("Common Gmail Search Queries:")
    click.echo("")

    for name, query in examples.items():
        click.echo(f"  {name:20} {query}")

    click.echo("")
    click.echo("Combine multiple queries:")
    click.echo("  gwc-email search 'from:alice@example.com subject:urgent has:attachment'")


# ============================================================================
# Label Commands
# ============================================================================


@labels.command("list")
@click.option(
    "--output",
    type=click.Choice(["unix", "json", "llm"]),
    default="unix",
    help="Output format",
)
def labels_list(output: str):
    """List all labels."""
    try:
        all_labels = list_labels()

        if not all_labels:
            click.echo("No labels found.")
            return

        # Format for output
        data = []
        for label in all_labels:
            data.append(
                {
                    "id": label["id"],
                    "name": label["name"],
                    "type": label.get("type", "user"),
                    "messagesTotal": label.get("messagesTotal", 0),
                    "messagesUnread": label.get("messagesUnread", 0),
                }
            )

        click.echo(format_output(data, output))

    except Exception as e:
        click.echo(f"Error listing labels: {e}", err=True)
        raise click.Abort()


@labels.command("get")
@click.argument("label_name")
@click.option(
    "--output",
    type=click.Choice(["unix", "json", "llm"]),
    default="unix",
    help="Output format",
)
def labels_get(label_name: str, output: str):
    """Get label details by name."""
    try:
        label = get_label_by_name(label_name)

        if not label:
            click.echo(f"Label '{label_name}' not found.", err=True)
            raise click.Abort()

        data = [
            {
                "id": label["id"],
                "name": label["name"],
                "type": label.get("type", "user"),
                "messagesTotal": label.get("messagesTotal", 0),
                "messagesUnread": label.get("messagesUnread", 0),
                "labelListVisibility": label.get("labelListVisibility", "labelShow"),
            }
        ]

        click.echo(format_output(data, output))

    except Exception as e:
        click.echo(f"Error getting label: {e}", err=True)
        raise click.Abort()


@labels.command("map")
@click.option(
    "--output",
    type=click.Choice(["unix", "json", "llm"]),
    default="unix",
    help="Output format",
)
def labels_map(output: str):
    """Show label name to ID mapping (useful for API calls)."""
    try:
        label_map = get_label_map()

        if not label_map:
            click.echo("No labels found.")
            return

        # Format for output
        data = [{"name": name, "id": label_id} for name, label_id in sorted(label_map.items())]

        click.echo(format_output(data, output))

    except Exception as e:
        click.echo(f"Error mapping labels: {e}", err=True)
        raise click.Abort()


@main.command()
@click.argument("thread_id")
@click.option(
    "--output",
    type=click.Choice(["unix", "json", "llm"]),
    default="unix",
    help="Output format",
)
def thread(thread_id: str, output: str):
    """Get all messages in a thread."""
    try:
        messages = get_message_threads(thread_id)

        if not messages:
            click.echo("Thread not found or has no messages.", err=True)
            raise click.Abort()

        # Format for output
        data = []
        for msg in messages:
            data.append(
                {
                    "id": msg["id"],
                    "from": msg.get("headers", {}).get("from", "Unknown"),
                    "subject": msg.get("headers", {}).get("subject", "(no subject)"),
                    "date": msg.get("internalDate", ""),
                }
            )

        click.echo(format_output(data, output))

    except Exception as e:
        click.echo(f"Error getting thread: {e}", err=True)
        raise click.Abort()


# ============================================================================
# Compose Commands (Phase 2)
# ============================================================================


@main.command()
@click.option("--to", required=True, help="Recipient email address (required)")
@click.option("--subject", required=True, help="Message subject (required)")
@click.option("--body", required=True, help="Message body (required)")
@click.option("--cc", default="", help="CC recipients (comma-separated)")
@click.option("--bcc", default="", help="BCC recipients (comma-separated)")
@click.option(
    "--attachments",
    multiple=True,
    help="File paths to attach (can specify multiple times)",
)
def send(to: str, subject: str, body: str, cc: str, bcc: str, attachments):
    """Send a message directly (no draft).

    Examples:
        gwc-email send --to alice@example.com --subject "Hello" --body "Hi there!"
        gwc-email send --to alice@example.com --subject "Report" --body "See attached" \\
          --attachments /path/to/file.pdf
    """
    try:
        message_id = send_message(to, subject, body, cc, bcc, list(attachments))
        click.echo(f"Message sent! ID: {message_id}")
    except FileNotFoundError as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort()
    except Exception as e:
        click.echo(f"Error sending message: {e}", err=True)
        raise click.Abort()


@draft.command("create")
@click.option("--to", required=True, help="Recipient email address (required)")
@click.option("--subject", required=True, help="Message subject (required)")
@click.option("--body", required=True, help="Message body (required)")
@click.option("--cc", default="", help="CC recipients (comma-separated)")
@click.option("--bcc", default="", help="BCC recipients (comma-separated)")
@click.option(
    "--attachments",
    multiple=True,
    help="File paths to attach (can specify multiple times)",
)
def draft_create(to: str, subject: str, body: str, cc: str, bcc: str, attachments):
    """Create a draft message (unsent).

    Examples:
        gwc-email draft create --to alice@example.com --subject "Hello" --body "Draft message"
        gwc-email draft create --to alice@example.com --subject "Report" --body "Draft" \\
          --attachments /path/to/file.pdf
    """
    try:
        draft_id = create_draft(to, subject, body, cc, bcc, list(attachments))
        click.echo(f"Draft created! ID: {draft_id}")
    except FileNotFoundError as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort()
    except Exception as e:
        click.echo(f"Error creating draft: {e}", err=True)
        raise click.Abort()


@draft.command("list")
@click.option("--limit", default=10, type=int, help="Max drafts to return (1-100)")
@click.option(
    "--output",
    type=click.Choice(["unix", "json", "llm"]),
    default="unix",
    help="Output format",
)
def draft_list(limit: int, output: str):
    """List all draft messages."""
    try:
        drafts = list_drafts(max_results=limit)

        if not drafts:
            click.echo("No drafts found.")
            return

        data = []
        for d in drafts:
            msg = d.get("message", {})
            data.append(
                {
                    "id": d.get("id"),
                    "messageId": msg.get("id"),
                    "snippet": msg.get("snippet", "")[:80],
                    "date": msg.get("internalDate", ""),
                }
            )

        click.echo(format_output(data, output))

    except Exception as e:
        click.echo(f"Error listing drafts: {e}", err=True)
        raise click.Abort()


@draft.command("get")
@click.argument("draft_id")
@click.option(
    "--output",
    type=click.Choice(["unix", "json", "llm"]),
    default="unix",
    help="Output format",
)
def draft_get(draft_id: str, output: str):
    """Get a draft message details."""
    try:
        d = get_draft(draft_id)
        msg = d.get("message", {})

        # Format similar to message display
        data = [
            {
                "id": d.get("id"),
                "messageId": msg.get("id"),
                "snippet": msg.get("snippet", ""),
                "date": msg.get("internalDate", ""),
            }
        ]

        click.echo(format_output(data, output))

    except Exception as e:
        click.echo(f"Error getting draft: {e}", err=True)
        raise click.Abort()


@draft.command("send")
@click.argument("draft_id")
def draft_send(draft_id: str):
    """Send an existing draft."""
    try:
        message_id = send_draft(draft_id)
        click.echo(f"Draft sent! Message ID: {message_id}")
    except Exception as e:
        click.echo(f"Error sending draft: {e}", err=True)
        raise click.Abort()


@draft.command("delete")
@click.argument("draft_id")
def draft_delete(draft_id: str):
    """Delete a draft message."""
    try:
        delete_draft(draft_id)
        click.echo(f"Draft {draft_id} deleted.")
    except Exception as e:
        click.echo(f"Error deleting draft: {e}", err=True)
        raise click.Abort()


@main.command()
@click.argument("message_id")
@click.option("--reply-all", is_flag=True, help="Reply to all recipients")
@click.option("--body", required=True, help="Reply message body")
def reply(message_id: str, reply_all: bool, body: str):
    """Reply to a message.

    Examples:
        gwc-email reply msg123 --body "Thanks for your message!"
        gwc-email reply msg123 --reply-all --body "Everyone, please see below."
    """
    try:
        message_id = reply_to_message(message_id, body, all_recipients=reply_all)
        click.echo(f"Reply sent! Message ID: {message_id}")
    except Exception as e:
        click.echo(f"Error sending reply: {e}", err=True)
        raise click.Abort()


@main.command()
@click.argument("message_id")
@click.option("--to", required=True, help="Recipient to forward to")
@click.option("--subject", default="", help="Custom subject (optional)")
@click.option("--body", default="", help="Additional text to include (optional)")
def forward(message_id: str, to: str, subject: str, body: str):
    """Forward a message to recipients.

    Examples:
        gwc-email forward msg123 --to alice@example.com
        gwc-email forward msg123 --to alice@example.com --body "Please see this."
    """
    try:
        message_id = forward_message(message_id, to, subject, body)
        click.echo(f"Message forwarded! ID: {message_id}")
    except Exception as e:
        click.echo(f"Error forwarding message: {e}", err=True)
        raise click.Abort()


if __name__ == "__main__":
    main()
