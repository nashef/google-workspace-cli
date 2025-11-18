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
)
from gwc.shared.output import format_output


@click.group()
def main():
    """Gmail CLI (gwc-email)."""
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


if __name__ == "__main__":
    main()
