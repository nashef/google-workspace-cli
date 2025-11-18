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
    find_text_position,
    insert_text,
    delete_text,
    replace_text,
    format_text,
    format_paragraph,
    insert_table,
    insert_image,
    insert_page_break,
    insert_footnote,
    create_header,
    create_footer,
    delete_header,
    delete_footer,
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


# ============================================================================
# Phase 2: Text Manipulation & Formatting
# ============================================================================


@main.command()
@click.argument("document_id")
@click.option("--text", required=True, help="Text to insert")
@click.option("--index", type=int, required=True, help="Position to insert at")
def insert_text_cmd(document_id, text, index):
    """Insert text at a specific position.

    Examples:
        gwc-docs insert-text doc_id --text "Hello" --index 0
        gwc-docs insert-text doc_id --text " World" --index 5
    """
    try:
        result = insert_text(document_id, text, index)
        click.echo(f"Text inserted at index {index}")
    except Exception as e:
        click.echo(f"Error inserting text: {e}", err=True)
        raise click.Abort()


@main.command()
@click.argument("document_id")
@click.option("--start-index", type=int, required=True, help="Start position")
@click.option("--end-index", type=int, required=True, help="End position")
def delete_cmd(document_id, start_index, end_index):
    """Delete text from a range.

    Examples:
        gwc-docs delete doc_id --start-index 0 --end-index 5
        gwc-docs delete doc_id --start-index 10 --end-index 20
    """
    try:
        result = delete_text(document_id, start_index, end_index)
        click.echo(f"Text deleted from index {start_index} to {end_index}")
    except Exception as e:
        click.echo(f"Error deleting text: {e}", err=True)
        raise click.Abort()


@main.command()
@click.argument("document_id")
@click.option("--find", required=True, help="Text to find")
@click.option("--replace", required=True, help="Text to replace with")
@click.option("--replace-all", is_flag=True, default=True, help="Replace all occurrences")
@click.option("--case-sensitive", is_flag=True, default=True, help="Case sensitive search")
def replace_cmd(document_id, find, replace, replace_all, case_sensitive):
    """Replace text in document.

    Examples:
        gwc-docs replace doc_id --find "old" --replace "new"
        gwc-docs replace doc_id --find "{{name}}" --replace "John"
    """
    try:
        result = replace_text(document_id, find, replace, replace_all, case_sensitive)
        click.echo(f"Text replaced: '{find}' -> '{replace}'")
    except Exception as e:
        click.echo(f"Error replacing text: {e}", err=True)
        raise click.Abort()


@main.command()
@click.argument("document_id")
@click.option("--start-index", type=int, required=True, help="Start position")
@click.option("--end-index", type=int, required=True, help="End position")
@click.option("--bold", is_flag=True, help="Make bold")
@click.option("--italic", is_flag=True, help="Make italic")
@click.option("--underline", is_flag=True, help="Make underlined")
@click.option("--strikethrough", is_flag=True, help="Apply strikethrough")
@click.option("--font", help="Font name (e.g., Arial, Courier New)")
@click.option("--size", type=int, help="Font size in points")
@click.option("--color", help="Color as hex (e.g., ff0000 for red)")
def format_text_cmd(
    document_id, start_index, end_index, bold, italic, underline, strikethrough, font, size, color
):
    """Apply character formatting to text range.

    Examples:
        gwc-docs format-text doc_id --start-index 0 --end-index 5 --bold
        gwc-docs format-text doc_id --start-index 10 --end-index 15 --italic --color ff0000
        gwc-docs format-text doc_id --start-index 20 --end-index 30 --font "Arial" --size 14
    """
    try:
        result = format_text(
            document_id,
            start_index,
            end_index,
            bold=bold,
            italic=italic,
            underline=underline,
            strikethrough=strikethrough,
            font=font,
            size=size,
            color=color,
        )
        click.echo(f"Text formatted from index {start_index} to {end_index}")
    except Exception as e:
        click.echo(f"Error formatting text: {e}", err=True)
        raise click.Abort()


@main.command()
@click.argument("document_id")
@click.option("--start-index", type=int, required=True, help="Start position")
@click.option("--end-index", type=int, required=True, help="End position")
@click.option("--align", type=click.Choice(["left", "center", "right", "justify"]), help="Alignment")
@click.option("--indent", type=int, help="Indentation in points")
@click.option("--spacing-before", type=int, help="Space before paragraph in points")
@click.option("--spacing-after", type=int, help="Space after paragraph in points")
@click.option("--line-spacing", type=float, help="Line spacing multiplier (1.0, 1.5, 2.0)")
@click.option(
    "--heading",
    type=click.Choice(["HEADING_1", "HEADING_2", "HEADING_3", "HEADING_4", "HEADING_5", "HEADING_6", "NORMAL_TEXT"]),
    help="Heading style",
)
def format_paragraph_cmd(
    document_id, start_index, end_index, align, indent, spacing_before, spacing_after, line_spacing, heading
):
    """Apply paragraph formatting.

    Examples:
        gwc-docs format-paragraph doc_id --start-index 0 --end-index 10 --align center
        gwc-docs format-paragraph doc_id --start-index 20 --end-index 30 --heading HEADING_1
        gwc-docs format-paragraph doc_id --start-index 40 --end-index 50 --spacing-after 12 --line-spacing 1.5
    """
    try:
        result = format_paragraph(
            document_id,
            start_index,
            end_index,
            alignment=align,
            indent=indent,
            spacing_before=spacing_before,
            spacing_after=spacing_after,
            line_spacing=line_spacing,
            heading_style=heading,
        )
        click.echo(f"Paragraph formatted from index {start_index} to {end_index}")
    except Exception as e:
        click.echo(f"Error formatting paragraph: {e}", err=True)
        raise click.Abort()


# ============================================================================
# Phase 3: Tables, Images & Advanced Structures
# ============================================================================


@main.command()
@click.argument("document_id")
@click.option("--rows", type=int, required=True, help="Number of rows")
@click.option("--columns", type=int, required=True, help="Number of columns")
@click.option("--index", type=int, required=True, help="Position to insert at")
def insert_table_cmd(document_id, rows, columns, index):
    """Insert a table at a specific position.

    Examples:
        gwc-docs insert-table doc_id --rows 3 --columns 2 --index 0
        gwc-docs insert-table doc_id --rows 5 --columns 4 --index 100
    """
    try:
        table_id = insert_table(document_id, rows, columns, index)
        click.echo(f"Table inserted at index {index} with ID: {table_id}")
    except Exception as e:
        click.echo(f"Error inserting table: {e}", err=True)
        raise click.Abort()


@main.command()
@click.argument("document_id")
@click.option("--image-url", required=True, help="URL of the image to insert")
@click.option("--index", type=int, required=True, help="Position to insert at")
def insert_image_cmd(document_id, image_url, index):
    """Insert an image from a URL.

    Examples:
        gwc-docs insert-image doc_id --image-url "https://example.com/logo.png" --index 0
        gwc-docs insert-image doc_id --image-url "https://example.com/image.jpg" --index 50
    """
    try:
        object_id = insert_image(document_id, image_url, index)
        click.echo(f"Image inserted at index {index} with ID: {object_id}")
    except Exception as e:
        click.echo(f"Error inserting image: {e}", err=True)
        raise click.Abort()


@main.command()
@click.argument("document_id")
@click.option("--index", type=int, required=True, help="Position to insert at")
def insert_page_break_cmd(document_id, index):
    """Insert a page break at a specific position.

    Examples:
        gwc-docs insert-page-break doc_id --index 50
        gwc-docs insert-page-break doc_id --index 100
    """
    try:
        insert_page_break(document_id, index)
        click.echo(f"Page break inserted at index {index}")
    except Exception as e:
        click.echo(f"Error inserting page break: {e}", err=True)
        raise click.Abort()


@main.command()
@click.argument("document_id")
@click.option("--text", required=True, help="Footnote text")
@click.option("--index", type=int, required=True, help="Position to insert at")
def insert_footnote_cmd(document_id, text, index):
    """Insert a footnote at a specific position.

    Examples:
        gwc-docs insert-footnote doc_id --text "See appendix A" --index 50
        gwc-docs insert-footnote doc_id --text "Citation here" --index 100
    """
    try:
        insert_footnote(document_id, index, text)
        click.echo(f"Footnote inserted at index {index}")
    except Exception as e:
        click.echo(f"Error inserting footnote: {e}", err=True)
        raise click.Abort()


@main.command()
@click.argument("document_id")
@click.option("--section-id", type=int, default=0, help="Section ID (default: 0)")
def create_header_cmd(document_id, section_id):
    """Create a header for a section.

    Examples:
        gwc-docs create-header doc_id
        gwc-docs create-header doc_id --section-id 1
    """
    try:
        header_id = create_header(document_id, section_id)
        click.echo(f"Header created for section {section_id} with ID: {header_id}")
    except Exception as e:
        click.echo(f"Error creating header: {e}", err=True)
        raise click.Abort()


@main.command()
@click.argument("document_id")
@click.option("--section-id", type=int, default=0, help="Section ID (default: 0)")
def create_footer_cmd(document_id, section_id):
    """Create a footer for a section.

    Examples:
        gwc-docs create-footer doc_id
        gwc-docs create-footer doc_id --section-id 1
    """
    try:
        footer_id = create_footer(document_id, section_id)
        click.echo(f"Footer created for section {section_id} with ID: {footer_id}")
    except Exception as e:
        click.echo(f"Error creating footer: {e}", err=True)
        raise click.Abort()


@main.command()
@click.argument("document_id")
@click.argument("header_id")
def delete_header_cmd(document_id, header_id):
    """Delete a header from a section.

    Examples:
        gwc-docs delete-header doc_id header_id_here
    """
    try:
        delete_header(document_id, header_id)
        click.echo(f"Header {header_id} deleted")
    except Exception as e:
        click.echo(f"Error deleting header: {e}", err=True)
        raise click.Abort()


@main.command()
@click.argument("document_id")
@click.argument("footer_id")
def delete_footer_cmd(document_id, footer_id):
    """Delete a footer from a section.

    Examples:
        gwc-docs delete-footer doc_id footer_id_here
    """
    try:
        delete_footer(document_id, footer_id)
        click.echo(f"Footer {footer_id} deleted")
    except Exception as e:
        click.echo(f"Error deleting footer: {e}", err=True)
        raise click.Abort()


if __name__ == "__main__":
    main()
