"""Google Slides CLI commands."""

import click
import json
from typing import Optional
from gwc.slides.operations import (
    create_presentation,
    get_presentation,
    get_presentation_title,
    list_slides,
    get_presentation_stats,
    add_slide,
    delete_slide,
    duplicate_slide,
    insert_text,
    insert_image,
    insert_shape,
    batch_update,
    batch_update_from_file,
    update_slide_properties,
)
from gwc.shared.output import format_output, OutputFormat


@click.group()
def main():
    """Google Slides CLI (gwc-slides)."""
    pass


# ============================================================================
# Phase 1: Core Presentation Operations
# ============================================================================


@main.command()
@click.option("--title", default="Untitled Presentation", help="Presentation title")
@click.option(
    "--output",
    type=click.Choice(["unix", "json", "llm"]),
    default="unix",
    help="Output format",
)
def create_cmd(title, output):
    """Create a new blank presentation.

    Examples:
        gwc-slides create --title "My Presentation"
        gwc-slides create --title "Sales Pitch" --output json
    """
    try:
        presentation_id = create_presentation(title=title)
        result = {"id": presentation_id, "title": title}
        click.echo(format_output([result], output))
    except Exception as e:
        click.echo(f"Error creating presentation: {e}", err=True)
        raise click.Abort()


@main.command()
@click.argument("presentation_id")
@click.option(
    "--output",
    type=click.Choice(["unix", "json", "llm"]),
    default="unix",
    help="Output format",
)
def get_cmd(presentation_id, output):
    """Get presentation metadata and stats.

    Examples:
        gwc-slides get presentation_id
        gwc-slides get presentation_id --output json
    """
    try:
        stats = get_presentation_stats(presentation_id)
        click.echo(format_output([stats], output))
    except Exception as e:
        click.echo(f"Error getting presentation: {e}", err=True)
        raise click.Abort()


@main.command()
@click.argument("presentation_id")
@click.option(
    "--output",
    type=click.Choice(["unix", "json", "llm"]),
    default="unix",
    help="Output format",
)
def list_slides_cmd(presentation_id, output):
    """List all slides in presentation.

    Examples:
        gwc-slides list-slides presentation_id
        gwc-slides list-slides presentation_id --output json
    """
    try:
        slides = list_slides(presentation_id)
        click.echo(format_output(slides, output))
    except Exception as e:
        click.echo(f"Error listing slides: {e}", err=True)
        raise click.Abort()


# ============================================================================
# Phase 2: Slide Management
# ============================================================================


@main.command()
@click.argument("presentation_id")
@click.option("--index", type=int, help="Position to insert slide")
@click.option(
    "--output",
    type=click.Choice(["unix", "json", "llm"]),
    default="unix",
    help="Output format",
)
def add_slide_cmd(presentation_id, index, output):
    """Add a new slide to presentation.

    Examples:
        gwc-slides add-slide presentation_id
        gwc-slides add-slide presentation_id --index 2
    """
    try:
        result = add_slide(presentation_id, slide_index=index)
        result_data = {
            "presentation_id": presentation_id,
            "slides_updated": 1,
            "success": True,
        }
        click.echo(format_output([result_data], output))
    except Exception as e:
        click.echo(f"Error adding slide: {e}", err=True)
        raise click.Abort()


@main.command()
@click.argument("presentation_id")
@click.argument("slide_id")
@click.option(
    "--output",
    type=click.Choice(["unix", "json", "llm"]),
    default="unix",
    help="Output format",
)
def delete_slide_cmd(presentation_id, slide_id, output):
    """Delete a slide from presentation.

    Examples:
        gwc-slides delete-slide presentation_id slide_id
    """
    try:
        result = delete_slide(presentation_id, slide_id)
        result_data = {"deleted_slide_id": slide_id, "success": True}
        click.echo(format_output([result_data], output))
    except Exception as e:
        click.echo(f"Error deleting slide: {e}", err=True)
        raise click.Abort()


@main.command()
@click.argument("presentation_id")
@click.argument("slide_id")
@click.option(
    "--after",
    is_flag=True,
    default=True,
    help="Insert after original (default) or before",
)
@click.option(
    "--output",
    type=click.Choice(["unix", "json", "llm"]),
    default="unix",
    help="Output format",
)
def duplicate_slide_cmd(presentation_id, slide_id, after, output):
    """Duplicate a slide.

    Examples:
        gwc-slides duplicate-slide presentation_id slide_id
        gwc-slides duplicate-slide presentation_id slide_id --no-after
    """
    try:
        result = duplicate_slide(presentation_id, slide_id, insert_after=after)
        result_data = {"duplicated_slide_id": slide_id, "success": True}
        click.echo(format_output([result_data], output))
    except Exception as e:
        click.echo(f"Error duplicating slide: {e}", err=True)
        raise click.Abort()


# ============================================================================
# Phase 3: Content Operations
# ============================================================================


@main.command()
@click.argument("presentation_id")
@click.argument("slide_id")
@click.option("--text", required=True, help="Text content")
@click.option("--x", type=int, default=100000, help="X position in EMU")
@click.option("--y", type=int, default=100000, help="Y position in EMU")
@click.option("--width", type=int, default=3000000, help="Width in EMU")
@click.option("--height", type=int, default=500000, help="Height in EMU")
@click.option(
    "--output",
    type=click.Choice(["unix", "json", "llm"]),
    default="unix",
    help="Output format",
)
def insert_text_cmd(presentation_id, slide_id, text, x, y, width, height, output):
    """Insert text box into slide.

    Examples:
        gwc-slides insert-text presentation_id slide_id --text "Hello World"
        gwc-slides insert-text presentation_id slide_id --text "Title" --y 500000
    """
    try:
        result = insert_text(presentation_id, slide_id, text, x, y, width, height)
        result_data = {"slide_id": slide_id, "text_inserted": True}
        click.echo(format_output([result_data], output))
    except Exception as e:
        click.echo(f"Error inserting text: {e}", err=True)
        raise click.Abort()


@main.command()
@click.argument("presentation_id")
@click.argument("slide_id")
@click.option("--url", required=True, help="Image URL")
@click.option("--x", type=int, default=100000, help="X position in EMU")
@click.option("--y", type=int, default=100000, help="Y position in EMU")
@click.option("--width", type=int, default=2000000, help="Width in EMU")
@click.option("--height", type=int, default=2000000, help="Height in EMU")
@click.option(
    "--output",
    type=click.Choice(["unix", "json", "llm"]),
    default="unix",
    help="Output format",
)
def insert_image_cmd(presentation_id, slide_id, url, x, y, width, height, output):
    """Insert image into slide from URL.

    Examples:
        gwc-slides insert-image presentation_id slide_id --url "https://example.com/image.png"
        gwc-slides insert-image presentation_id slide_id --url "https://..." --width 1000000
    """
    try:
        result = insert_image(presentation_id, slide_id, url, x, y, width, height)
        result_data = {"slide_id": slide_id, "image_inserted": True}
        click.echo(format_output([result_data], output))
    except Exception as e:
        click.echo(f"Error inserting image: {e}", err=True)
        raise click.Abort()


@main.command()
@click.argument("presentation_id")
@click.argument("slide_id")
@click.option(
    "--shape",
    required=True,
    type=click.Choice(
        ["RECTANGLE", "ELLIPSE", "TRIANGLE", "PARALLELOGRAM", "STAR", "HEART"]
    ),
    help="Shape type",
)
@click.option("--x", type=int, default=100000, help="X position in EMU")
@click.option("--y", type=int, default=100000, help="Y position in EMU")
@click.option("--width", type=int, default=1000000, help="Width in EMU")
@click.option("--height", type=int, default=1000000, help="Height in EMU")
@click.option(
    "--output",
    type=click.Choice(["unix", "json", "llm"]),
    default="unix",
    help="Output format",
)
def insert_shape_cmd(presentation_id, slide_id, shape, x, y, width, height, output):
    """Insert shape into slide.

    Examples:
        gwc-slides insert-shape presentation_id slide_id --shape RECTANGLE
        gwc-slides insert-shape presentation_id slide_id --shape ELLIPSE --width 500000
    """
    try:
        result = insert_shape(presentation_id, slide_id, shape, x, y, width, height)
        result_data = {"slide_id": slide_id, "shape_inserted": True, "type": shape}
        click.echo(format_output([result_data], output))
    except Exception as e:
        click.echo(f"Error inserting shape: {e}", err=True)
        raise click.Abort()


# ============================================================================
# Phase 4: Advanced Operations
# ============================================================================


@main.command()
@click.argument("presentation_id")
@click.option(
    "--batch-file",
    required=True,
    type=click.Path(exists=True),
    help="JSON file with batch requests",
)
@click.option(
    "--output",
    type=click.Choice(["unix", "json", "llm"]),
    default="json",
    help="Output format",
)
def batch_update_cmd(presentation_id, batch_file, output):
    """Execute batch update from JSON file.

    Batch file format:
        {
          "requests": [
            {"addSlide": {...}},
            {"insertText": {...}},
            ...
          ]
        }

    Examples:
        gwc-slides batch-update presentation_id --batch-file updates.json
        gwc-slides batch-update presentation_id --batch-file requests.json --output llm
    """
    try:
        result = batch_update_from_file(presentation_id, batch_file)
        click.echo(format_output([result], output))
    except Exception as e:
        click.echo(f"Error executing batch update: {e}", err=True)
        raise click.Abort()


@main.command()
@click.argument("presentation_id")
@click.argument("slide_id")
@click.option("--name", help="New slide name")
@click.option(
    "--output",
    type=click.Choice(["unix", "json", "llm"]),
    default="unix",
    help="Output format",
)
def update_slide_cmd(presentation_id, slide_id, name, output):
    """Update slide properties.

    Examples:
        gwc-slides update-slide presentation_id slide_id --name "Title Slide"
    """
    try:
        result = update_slide_properties(presentation_id, slide_id, name=name)
        result_data = {"slide_id": slide_id, "updated": True}
        click.echo(format_output([result_data], output))
    except Exception as e:
        click.echo(f"Error updating slide: {e}", err=True)
        raise click.Abort()


if __name__ == "__main__":
    main()
