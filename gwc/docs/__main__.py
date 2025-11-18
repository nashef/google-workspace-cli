"""Google Docs CLI commands."""

import click
from typing import Optional
from gwc.docs.operations import (
    create_document,
    get_document,
    get_document_title,
    extract_text,
    get_document_stats,
    get_document_structure,
    export_document_as_text,
    export_document_as_json,
    export_document_as_markdown,
    format_document_for_display,
)
from gwc.shared.output import format_output, OutputFormat


@click.group()
def main():
    """Google Docs CLI (gwc-docs)."""
    pass


# ============================================================================
# Phase 1: Core Document Operations
# ============================================================================


@main.command()
@click.option("--title", default="Untitled Document", help="Document title")
@click.option(
    "--output",
    type=click.Choice(["unix", "json", "llm"]),
    default="unix",
    help="Output format",
)
def create_cmd(title, output):
    """Create a new blank document.

    Examples:
        gwc-docs create --title "My Document"
        gwc-docs create --title "Report" --output json
    """
    try:
        doc_id = create_document(title=title)
        result = {"id": doc_id, "title": title}
        click.echo(format_output([result], output))
    except Exception as e:
        click.echo(f"Error creating document: {e}", err=True)
        raise click.Abort()


@main.command()
@click.argument("document_id")
@click.option(
    "--output",
    type=click.Choice(["unix", "json", "llm"]),
    default="unix",
    help="Output format",
)
def get_cmd(document_id, output):
    """Get document metadata.

    Examples:
        gwc-docs get document_id --output json
        gwc-docs get document_id --output llm
    """
    try:
        doc = get_document(document_id)
        formatted = format_document_for_display(doc)
        click.echo(format_output([formatted], output))
    except Exception as e:
        click.echo(f"Error getting document: {e}", err=True)
        raise click.Abort()


@main.command()
@click.argument("document_id")
def title_cmd(document_id):
    """Get document title.

    Examples:
        gwc-docs title document_id
    """
    try:
        title = get_document_title(document_id)
        click.echo(title)
    except Exception as e:
        click.echo(f"Error getting title: {e}", err=True)
        raise click.Abort()


@main.command()
@click.argument("document_id")
def read_cmd(document_id):
    """Read and display document text content.

    Examples:
        gwc-docs read document_id
    """
    try:
        text = extract_text(document_id)
        click.echo(text)
    except Exception as e:
        click.echo(f"Error reading document: {e}", err=True)
        raise click.Abort()


@main.command()
@click.argument("document_id")
@click.option(
    "--output",
    type=click.Choice(["unix", "json", "llm"]),
    default="llm",
    help="Output format",
)
def stats_cmd(document_id, output):
    """Get document statistics.

    Examples:
        gwc-docs stats document_id --output llm
        gwc-docs stats document_id --output json
    """
    try:
        stats = get_document_stats(document_id)
        click.echo(format_output([stats], output))
    except Exception as e:
        click.echo(f"Error getting stats: {e}", err=True)
        raise click.Abort()


@main.command()
@click.argument("document_id")
@click.option(
    "--output",
    type=click.Choice(["unix", "json", "llm"]),
    default="json",
    help="Output format",
)
def structure_cmd(document_id, output):
    """Get document structure.

    Shows the document structure with element types and hierarchy.

    Examples:
        gwc-docs structure document_id --output llm
        gwc-docs structure document_id --output json
    """
    try:
        structure = get_document_structure(document_id)
        click.echo(format_output([structure], output))
    except Exception as e:
        click.echo(f"Error getting structure: {e}", err=True)
        raise click.Abort()


@main.command()
@click.argument("document_id")
@click.option(
    "--output-file",
    type=click.Path(),
    help="Save to file instead of stdout",
)
def export_text_cmd(document_id, output_file):
    """Export document as plain text.

    Examples:
        gwc-docs export-text document_id
        gwc-docs export-text document_id --output-file output.txt
    """
    try:
        text = export_document_as_text(document_id)
        if output_file:
            with open(output_file, "w") as f:
                f.write(text)
            click.echo(f"Document exported to {output_file}")
        else:
            click.echo(text)
    except Exception as e:
        click.echo(f"Error exporting document: {e}", err=True)
        raise click.Abort()


@main.command()
@click.argument("document_id")
@click.option(
    "--output-file",
    type=click.Path(),
    help="Save to file instead of stdout",
)
def export_json_cmd(document_id, output_file):
    """Export document as JSON.

    Exports the full document structure and content as JSON.

    Examples:
        gwc-docs export-json document_id
        gwc-docs export-json document_id --output-file output.json
    """
    try:
        json_str = export_document_as_json(document_id)
        if output_file:
            with open(output_file, "w") as f:
                f.write(json_str)
            click.echo(f"Document exported to {output_file}")
        else:
            click.echo(json_str)
    except Exception as e:
        click.echo(f"Error exporting document: {e}", err=True)
        raise click.Abort()


@main.command()
@click.argument("document_id")
@click.option(
    "--output-file",
    type=click.Path(),
    help="Save to file instead of stdout",
)
def export_markdown_cmd(document_id, output_file):
    """Export document as Markdown.

    Converts document to Markdown format preserving headings and tables.

    Examples:
        gwc-docs export-markdown document_id
        gwc-docs export-markdown document_id --output-file output.md
    """
    try:
        markdown = export_document_as_markdown(document_id)
        if output_file:
            with open(output_file, "w") as f:
                f.write(markdown)
            click.echo(f"Document exported to {output_file}")
        else:
            click.echo(markdown)
    except Exception as e:
        click.echo(f"Error exporting document: {e}", err=True)
        raise click.Abort()


if __name__ == "__main__":
    main()
