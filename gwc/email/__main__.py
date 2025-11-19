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
    # Phase 3: Message organization & batch operations
    create_label,
    add_label_to_message,
    remove_label_from_message,
    set_message_read,
    set_message_unread,
    archive_message,
    unarchive_message,
    mark_message_spam,
    permanently_delete_message,
    batch_add_label,
    batch_remove_label,
    batch_set_read,
    batch_set_unread,
    batch_archive,
    batch_delete,
    # Phase 4: Advanced features
    create_filter,
    list_filters,
    get_filter,
    delete_filter,
    get_signature,
    update_signature,
    list_signatures,
    create_auto_responder,
    get_auto_responder,
    disable_auto_responder,
    create_template,
    list_templates,
    get_template,
    delete_template,
    use_template,
)
from gwc.shared.output import format_output, OutputFormat


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


@main.group()
def filters():
    """Manage message filters/rules."""
    pass


@main.group()
def signatures():
    """Manage email signatures."""
    pass


@main.group()
def auto_responder():
    """Manage auto-responders (vacation messages)."""
    pass


@main.group()
def templates():
    """Manage message templates."""
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

        # Format for output - fetch full message details for each
        data = []
        for msg in messages:
            try:
                # Fetch full message to get headers
                full_msg = get_message(msg["id"])
                formatted = format_message_for_display(full_msg)
                data.append(formatted)
            except Exception:
                # Fallback to basic info if fetch fails
                data.append(
                    {
                        "id": msg["id"],
                        "threadId": msg.get("threadId", ""),
                        "snippet": msg.get("snippet", "")[:80],
                        "date": msg.get("internalDate", ""),
                    }
                )

        click.echo(format_output(data, OutputFormat(output)))

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
        click.echo(format_output([formatted], OutputFormat(output)))
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

        # Format for output - fetch full message details for each
        data = []
        for msg in messages:
            try:
                # Fetch full message to get headers
                full_msg = get_message(msg["id"])
                formatted = format_message_for_display(full_msg)
                data.append(formatted)
            except Exception:
                # Fallback to basic info if fetch fails
                data.append(
                    {
                        "id": msg["id"],
                        "threadId": msg.get("threadId", ""),
                        "snippet": msg.get("snippet", "")[:80],
                        "date": msg.get("internalDate", ""),
                    }
                )

        click.echo(format_output(data, OutputFormat(output)))

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

        click.echo(format_output(data, OutputFormat(output)))

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

        click.echo(format_output(data, OutputFormat(output)))

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

        click.echo(format_output(data, OutputFormat(output)))

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

        click.echo(format_output(data, OutputFormat(output)))

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
        attachment_list = tuple(attachments) if attachments else []
        message_id = send_message(to, subject, body, cc, bcc, attachment_list)
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
        attachment_list = tuple(attachments) if attachments else []
        draft_id = create_draft(to, subject, body, cc, bcc, attachment_list)
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

        click.echo(format_output(data, OutputFormat(output)))

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

        click.echo(format_output(data, OutputFormat(output)))

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


# ============================================================================
# Message Organization & Batch Operations (Phase 3)
# ============================================================================


@main.command()
@click.argument("label_name")
@click.option(
    "--visibility",
    type=click.Choice(["show", "hide"]),
    default="show",
    help="Show or hide label in label list",
)
def create_label_cmd(label_name: str, visibility: str):
    """Create a new label.

    Examples:
        gwc-email create-label "Project X"
        gwc-email create-label "To Review" --visibility hide
    """
    try:
        visibility_map = {"show": "labelShow", "hide": "labelHide"}
        label_id = create_label(label_name, visibility_map[visibility])
        click.echo(f"Label created! ID: {label_id}")
    except Exception as e:
        click.echo(f"Error creating label: {e}", err=True)
        raise click.Abort()


@main.command()
@click.argument("message_id")
@click.argument("label_name")
def add_label(message_id: str, label_name: str):
    """Add a label to a message.

    Examples:
        gwc-email add-label msg123 "Important"
        gwc-email add-label msg123 "Project X"
    """
    try:
        add_label_to_message(message_id, label_name)
        click.echo(f"Label '{label_name}' added to message {message_id}")
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort()
    except Exception as e:
        click.echo(f"Error adding label: {e}", err=True)
        raise click.Abort()


@main.command()
@click.argument("message_id")
@click.argument("label_name")
def remove_label(message_id: str, label_name: str):
    """Remove a label from a message.

    Examples:
        gwc-email remove-label msg123 "Important"
        gwc-email remove-label msg123 "Project X"
    """
    try:
        remove_label_from_message(message_id, label_name)
        click.echo(f"Label '{label_name}' removed from message {message_id}")
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort()
    except Exception as e:
        click.echo(f"Error removing label: {e}", err=True)
        raise click.Abort()


@main.command()
@click.argument("message_id")
def mark_read(message_id: str):
    """Mark a message as read.

    Examples:
        gwc-email mark-read msg123
    """
    try:
        set_message_read(message_id)
        click.echo(f"Message {message_id} marked as read")
    except Exception as e:
        click.echo(f"Error marking message as read: {e}", err=True)
        raise click.Abort()


@main.command()
@click.argument("message_id")
def mark_unread(message_id: str):
    """Mark a message as unread.

    Examples:
        gwc-email mark-unread msg123
    """
    try:
        set_message_unread(message_id)
        click.echo(f"Message {message_id} marked as unread")
    except Exception as e:
        click.echo(f"Error marking message as unread: {e}", err=True)
        raise click.Abort()


@main.command()
@click.argument("message_id")
def archive(message_id: str):
    """Archive a message (remove from INBOX).

    Examples:
        gwc-email archive msg123
    """
    try:
        archive_message(message_id)
        click.echo(f"Message {message_id} archived")
    except Exception as e:
        click.echo(f"Error archiving message: {e}", err=True)
        raise click.Abort()


@main.command()
@click.argument("message_id")
def unarchive(message_id: str):
    """Restore a message to INBOX.

    Examples:
        gwc-email unarchive msg123
    """
    try:
        unarchive_message(message_id)
        click.echo(f"Message {message_id} restored to inbox")
    except Exception as e:
        click.echo(f"Error unarchiving message: {e}", err=True)
        raise click.Abort()


@main.command()
@click.argument("message_id")
def spam(message_id: str):
    """Mark a message as spam.

    Examples:
        gwc-email spam msg123
    """
    try:
        mark_message_spam(message_id)
        click.echo(f"Message {message_id} marked as spam")
    except Exception as e:
        click.echo(f"Error marking message as spam: {e}", err=True)
        raise click.Abort()


@main.command()
@click.argument("message_id")
@click.option("--confirm", is_flag=True, help="Confirm deletion without prompting")
def delete(message_id: str, confirm: bool):
    """Permanently delete a message.

    Examples:
        gwc-email delete msg123 --confirm
    """
    try:
        if not confirm:
            if not click.confirm(f"Permanently delete message {message_id}?"):
                click.echo("Cancelled.")
                return
        permanently_delete_message(message_id)
        click.echo(f"Message {message_id} deleted permanently")
    except Exception as e:
        click.echo(f"Error deleting message: {e}", err=True)
        raise click.Abort()


@main.command()
@click.argument("message_ids", nargs=-1, required=True)
@click.argument("label_name")
@click.option(
    "--output",
    type=click.Choice(["unix", "json", "llm"]),
    default="unix",
    help="Output format",
)
def batch_add_label_cmd(message_ids, label_name: str, output: str):
    """Add a label to multiple messages.

    Examples:
        gwc-email batch-add-label msg1 msg2 msg3 "Project X"
    """
    try:
        message_ids_list = tuple(message_ids) if message_ids else []
        result = batch_add_label(message_ids_list, label_name)
        click.echo(format_output([result], output))
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort()
    except Exception as e:
        click.echo(f"Error in batch operation: {e}", err=True)
        raise click.Abort()


@main.command()
@click.argument("message_ids", nargs=-1, required=True)
@click.argument("label_name")
@click.option(
    "--output",
    type=click.Choice(["unix", "json", "llm"]),
    default="unix",
    help="Output format",
)
def batch_remove_label_cmd(message_ids, label_name: str, output: str):
    """Remove a label from multiple messages.

    Examples:
        gwc-email batch-remove-label msg1 msg2 msg3 "Project X"
    """
    try:
        message_ids_list = tuple(message_ids) if message_ids else []
        result = batch_remove_label(message_ids_list, label_name)
        click.echo(format_output([result], output))
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort()
    except Exception as e:
        click.echo(f"Error in batch operation: {e}", err=True)
        raise click.Abort()


@main.command()
@click.argument("message_ids", nargs=-1, required=True)
@click.option(
    "--output",
    type=click.Choice(["unix", "json", "llm"]),
    default="unix",
    help="Output format",
)
def batch_mark_read(message_ids, output: str):
    """Mark multiple messages as read.

    Examples:
        gwc-email batch-mark-read msg1 msg2 msg3
    """
    try:
        message_ids_list = tuple(message_ids) if message_ids else []
        result = batch_set_read(message_ids_list)
        click.echo(format_output([result], output))
    except Exception as e:
        click.echo(f"Error in batch operation: {e}", err=True)
        raise click.Abort()


@main.command()
@click.argument("message_ids", nargs=-1, required=True)
@click.option(
    "--output",
    type=click.Choice(["unix", "json", "llm"]),
    default="unix",
    help="Output format",
)
def batch_mark_unread(message_ids, output: str):
    """Mark multiple messages as unread.

    Examples:
        gwc-email batch-mark-unread msg1 msg2 msg3
    """
    try:
        message_ids_list = tuple(message_ids) if message_ids else []
        result = batch_set_unread(message_ids_list)
        click.echo(format_output([result], output))
    except Exception as e:
        click.echo(f"Error in batch operation: {e}", err=True)
        raise click.Abort()


@main.command()
@click.argument("message_ids", nargs=-1, required=True)
@click.option(
    "--output",
    type=click.Choice(["unix", "json", "llm"]),
    default="unix",
    help="Output format",
)
def batch_archive_cmd(message_ids, output: str):
    """Archive multiple messages.

    Examples:
        gwc-email batch-archive msg1 msg2 msg3
    """
    try:
        message_ids_list = tuple(message_ids) if message_ids else []
        result = batch_archive(message_ids_list)
        click.echo(format_output([result], output))
    except Exception as e:
        click.echo(f"Error in batch operation: {e}", err=True)
        raise click.Abort()


@main.command()
@click.argument("message_ids", nargs=-1, required=True)
@click.option("--confirm", is_flag=True, help="Confirm deletion without prompting")
@click.option(
    "--output",
    type=click.Choice(["unix", "json", "llm"]),
    default="unix",
    help="Output format",
)
def batch_delete_cmd(message_ids, confirm: bool, output: str):
    """Permanently delete multiple messages.

    Examples:
        gwc-email batch-delete msg1 msg2 msg3 --confirm
    """
    try:
        if not confirm:
            if not click.confirm(f"Permanently delete {len(message_ids)} messages?"):
                click.echo("Cancelled.")
                return
        message_ids_list = tuple(message_ids) if message_ids else []
        result = batch_delete(message_ids_list)
        click.echo(format_output([result], output))
    except Exception as e:
        click.echo(f"Error in batch operation: {e}", err=True)
        raise click.Abort()


# ============================================================================
# Phase 4: Advanced Features
# ============================================================================


# Filters
@filters.command("create")
@click.argument("name")
@click.option(
    "--from",
    "from_addr",
    help="Match messages from this address",
)
@click.option(
    "--to",
    "to_addr",
    help="Match messages to this address",
)
@click.option(
    "--subject",
    help="Match messages with this subject",
)
@click.option(
    "--has-attachment",
    is_flag=True,
    help="Match messages with attachments",
)
@click.option(
    "--action",
    type=click.Choice(["archive", "delete", "mark-read", "add-label", "skip-inbox"]),
    required=True,
    help="Action to apply to matching messages",
)
@click.option(
    "--label",
    help="Label to add (required if action is 'add-label')",
)
@click.option(
    "--output",
    type=click.Choice(["unix", "json", "llm"]),
    default="unix",
    help="Output format",
)
def create_filter_cmd(name, from_addr, to_addr, subject, has_attachment, action, label, output):
    """Create a message filter/rule.

    Examples:
        gwc-email filters create "Archive old" --from "spam@example.com" --action archive
        gwc-email filters create "Work label" --to "work@example.com" --action add-label --label Work
    """
    try:
        criteria = {}
        if from_addr:
            criteria["from"] = from_addr
        if to_addr:
            criteria["to"] = to_addr
        if subject:
            criteria["subject"] = subject
        if has_attachment:
            criteria["hasAttachment"] = True

        action_obj = {}
        if action == "archive":
            action_obj["skip"] = True
        elif action == "delete":
            action_obj["deletePermanently"] = True
        elif action == "mark-read":
            action_obj["markAsRead"] = True
        elif action == "skip-inbox":
            action_obj["skipInbox"] = True
        elif action == "add-label":
            if not label:
                click.echo("Error: --label required for add-label action", err=True)
                raise click.Abort()
            action_obj["addLabelIds"] = [label]

        filter_id = create_filter(criteria, action_obj)
        result = {"id": filter_id, "name": name}
        click.echo(format_output([result], output))
    except Exception as e:
        click.echo(f"Error creating filter: {e}", err=True)
        raise click.Abort()


@filters.command("list")
@click.option(
    "--output",
    type=click.Choice(["unix", "json", "llm"]),
    default="unix",
    help="Output format",
)
def list_filters_cmd(output):
    """List all message filters.

    Examples:
        gwc-email filters list --output llm
    """
    try:
        filters_list = list_filters()
        click.echo(format_output(filters_list, output))
    except Exception as e:
        click.echo(f"Error listing filters: {e}", err=True)
        raise click.Abort()


@filters.command("get")
@click.argument("filter_id")
@click.option(
    "--output",
    type=click.Choice(["unix", "json", "llm"]),
    default="unix",
    help="Output format",
)
def get_filter_cmd(filter_id, output):
    """Get filter details.

    Examples:
        gwc-email filters get filter123 --output json
    """
    try:
        filter_obj = get_filter(filter_id)
        click.echo(format_output([filter_obj], output))
    except Exception as e:
        click.echo(f"Error getting filter: {e}", err=True)
        raise click.Abort()


@filters.command("delete")
@click.argument("filter_id")
def delete_filter_cmd(filter_id):
    """Delete a filter.

    Examples:
        gwc-email filters delete filter123
    """
    try:
        delete_filter(filter_id)
        click.echo(f"Filter {filter_id} deleted.")
    except Exception as e:
        click.echo(f"Error deleting filter: {e}", err=True)
        raise click.Abort()


# Signatures
@signatures.command("list")
@click.option(
    "--output",
    type=click.Choice(["unix", "json", "llm"]),
    default="unix",
    help="Output format",
)
def list_signatures_cmd(output):
    """List all email signatures.

    Examples:
        gwc-email signatures list --output llm
    """
    try:
        sigs = list_signatures()
        click.echo(format_output(sigs, output))
    except Exception as e:
        click.echo(f"Error listing signatures: {e}", err=True)
        raise click.Abort()


@signatures.command("get")
@click.argument("send_as_email")
@click.option(
    "--output",
    type=click.Choice(["unix", "json", "llm"]),
    default="unix",
    help="Output format",
)
def get_signature_cmd(send_as_email, output):
    """Get signature for a send-as address.

    Examples:
        gwc-email signatures get user@example.com --output json
    """
    try:
        sig = get_signature(send_as_email)
        click.echo(format_output([sig], output))
    except Exception as e:
        click.echo(f"Error getting signature: {e}", err=True)
        raise click.Abort()


@signatures.command("update")
@click.argument("send_as_email")
@click.argument("signature_html")
def update_signature_cmd(send_as_email, signature_html):
    """Update signature for a send-as address.

    Examples:
        gwc-email signatures update user@example.com "<p>Best regards,<br/>John</p>"
    """
    try:
        result = update_signature(send_as_email, signature_html)
        click.echo(f"Signature updated for {send_as_email}")
    except Exception as e:
        click.echo(f"Error updating signature: {e}", err=True)
        raise click.Abort()


# Auto-responders
@auto_responder.command("create")
@click.option(
    "--subject",
    required=True,
    help="Subject of auto-responder message",
)
@click.option(
    "--message",
    required=True,
    help="Body of auto-responder message",
)
@click.option(
    "--start-date",
    help="Start date (YYYY-MM-DD). Default: now",
)
@click.option(
    "--end-date",
    help="End date (YYYY-MM-DD). If not set, responder stays active",
)
def create_auto_responder_cmd(subject, message, start_date, end_date):
    """Enable auto-responder (vacation message).

    Examples:
        gwc-email auto-responder create --subject "Out of Office" --message "I'm on vacation."
        gwc-email auto-responder create --subject "OOO" --message "Back soon" --start-date 2025-12-01 --end-date 2025-12-15
    """
    try:
        result = create_auto_responder(subject, message, start_date, end_date)
        click.echo("Auto-responder enabled.")
    except Exception as e:
        click.echo(f"Error creating auto-responder: {e}", err=True)
        raise click.Abort()


@auto_responder.command("get")
@click.option(
    "--output",
    type=click.Choice(["unix", "json", "llm"]),
    default="unix",
    help="Output format",
)
def get_auto_responder_cmd(output):
    """Get current auto-responder settings.

    Examples:
        gwc-email auto-responder get --output json
    """
    try:
        settings = get_auto_responder()
        click.echo(format_output([settings], output))
    except Exception as e:
        click.echo(f"Error getting auto-responder: {e}", err=True)
        raise click.Abort()


@auto_responder.command("disable")
def disable_auto_responder_cmd():
    """Disable auto-responder.

    Examples:
        gwc-email auto-responder disable
    """
    try:
        disable_auto_responder()
        click.echo("Auto-responder disabled.")
    except Exception as e:
        click.echo(f"Error disabling auto-responder: {e}", err=True)
        raise click.Abort()


# Templates
@templates.command("create")
@click.argument("name")
@click.option(
    "--subject",
    required=True,
    help="Template subject line",
)
@click.option(
    "--body",
    required=True,
    help="Template body (HTML supported)",
)
@click.option(
    "--output",
    type=click.Choice(["unix", "json", "llm"]),
    default="unix",
    help="Output format",
)
def create_template_cmd(name, subject, body, output):
    """Create a message template.

    Examples:
        gwc-email templates create "Weekly Report" --subject "Weekly Update" --body "..."
    """
    try:
        template_id = create_template(name, body, subject)
        result = {"id": template_id, "name": name}
        click.echo(format_output([result], output))
    except Exception as e:
        click.echo(f"Error creating template: {e}", err=True)
        raise click.Abort()


@templates.command("list")
@click.option(
    "--output",
    type=click.Choice(["unix", "json", "llm"]),
    default="unix",
    help="Output format",
)
def list_templates_cmd(output):
    """List all templates.

    Examples:
        gwc-email templates list --output llm
    """
    try:
        tmpl_list = list_templates()
        click.echo(format_output(tmpl_list, output))
    except Exception as e:
        click.echo(f"Error listing templates: {e}", err=True)
        raise click.Abort()


@templates.command("get")
@click.argument("template_id")
@click.option(
    "--output",
    type=click.Choice(["unix", "json", "llm"]),
    default="unix",
    help="Output format",
)
def get_template_cmd(template_id, output):
    """Get template details.

    Examples:
        gwc-email templates get template123 --output json
    """
    try:
        tmpl = get_template(template_id)
        click.echo(format_output([tmpl], output))
    except Exception as e:
        click.echo(f"Error getting template: {e}", err=True)
        raise click.Abort()


@templates.command("delete")
@click.argument("template_id")
def delete_template_cmd(template_id):
    """Delete a template.

    Examples:
        gwc-email templates delete template123
    """
    try:
        delete_template(template_id)
        click.echo(f"Template {template_id} deleted.")
    except Exception as e:
        click.echo(f"Error deleting template: {e}", err=True)
        raise click.Abort()


@templates.command("use")
@click.argument("template_id")
@click.option(
    "--to",
    required=True,
    help="Recipient email address",
)
@click.option(
    "--cc",
    help="CC recipients (comma-separated)",
)
@click.option(
    "--bcc",
    help="BCC recipients (comma-separated)",
)
@click.option(
    "--output",
    type=click.Choice(["unix", "json", "llm"]),
    default="unix",
    help="Output format",
)
def use_template_cmd(template_id, to, cc, bcc, output):
    """Create a draft from a template.

    Examples:
        gwc-email templates use template123 --to alice@example.com
        gwc-email templates use template123 --to alice@example.com --cc bob@example.com
    """
    try:
        cc_list = [x.strip() for x in cc.split(",")] if cc else []
        bcc_list = [x.strip() for x in bcc.split(",")] if bcc else []
        draft_id = use_template(template_id, to, cc_list, bcc_list)
        result = {"draft_id": draft_id, "template_id": template_id}
        click.echo(format_output([result], output))
    except Exception as e:
        click.echo(f"Error using template: {e}", err=True)
        raise click.Abort()


if __name__ == "__main__":
    main()
