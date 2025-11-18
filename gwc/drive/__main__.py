"""Google Drive CLI commands."""

import click
import json
from typing import Optional
from gwc.drive.operations import (
    create_file,
    get_file,
    list_files,
    update_file,
    delete_file,
    copy_file,
    export_file,
    download_file,
    list_labels,
    modify_labels,
    trash_file,
    untrash_file,
    empty_trash,
    get_about,
    get_quota,
    format_file_for_display,
    format_quota_for_display,
    guess_mime_type,
    get_mime_types,
    get_export_mime_types,
)
from gwc.shared.output import format_output, OutputFormat


@click.group()
def main():
    """Google Drive CLI (gwc-drive)."""
    pass


# ============================================================================
# File Operations
# ============================================================================


@main.command()
@click.option("--name", required=True, help="File or folder name")
@click.option(
    "--mime-type",
    default="application/vnd.google-apps.document",
    help="MIME type (use 'folder' for application/vnd.google-apps.folder)",
)
@click.option("--parents", multiple=True, help="Parent folder IDs")
@click.option("--description", default="", help="File description")
@click.option("--starred", is_flag=True, help="Star the file")
@click.option("--file", type=click.File("rb"), help="File to upload")
@click.option(
    "--output",
    type=click.Choice(["unix", "json", "llm"]),
    default="unix",
    help="Output format",
)
def create_cmd(name, mime_type, parents, description, starred, file, output):
    """Create a new file or folder.

    Examples:
        gwc-drive create --name "My Document"
        gwc-drive create --name "My Folder" --mime-type folder
        gwc-drive create --name "report.pdf" --file /path/to/report.pdf --parents folder_id
    """
    try:
        # Handle mime-type shortcuts
        if mime_type == "folder":
            mime_type = "application/vnd.google-apps.folder"

        file_content = file.read() if file else None
        file_id = create_file(
            name=name,
            mime_type=mime_type,
            parents=list(parents) if parents else None,
            description=description,
            starred=starred,
            file_content=file_content,
        )

        result = {"id": file_id, "name": name}
        click.echo(format_output([result], output))
    except Exception as e:
        click.echo(f"Error creating file: {e}", err=True)
        raise click.Abort()


@main.command()
@click.argument("file_id")
@click.option(
    "--output",
    type=click.Choice(["unix", "json", "llm"]),
    default="unix",
    help="Output format",
)
def get_cmd(file_id, output):
    """Get file metadata.

    Examples:
        gwc-drive get file_id --output json
        gwc-drive get file_id --output llm
    """
    try:
        file_data = get_file(file_id)
        formatted = format_file_for_display(file_data)
        click.echo(format_output([formatted], output))
    except Exception as e:
        click.echo(f"Error getting file: {e}", err=True)
        raise click.Abort()


@main.command()
@click.option("--query", default="", help="Drive API query (e.g., 'name contains \"budget\"')")
@click.option("--limit", default=10, type=int, help="Max results (1-1000)")
@click.option("--order-by", default="modifiedTime desc", help="Sort order")
@click.option(
    "--output",
    type=click.Choice(["unix", "json", "llm"]),
    default="unix",
    help="Output format",
)
def list_cmd(query, limit, order_by, output):
    """List files.

    Examples:
        gwc-drive list --output llm
        gwc-drive list --query "name contains 'budget'" --output llm
        gwc-drive list --limit 50 --output json
    """
    try:
        files, _ = list_files(query=query, limit=limit, order_by=order_by)
        formatted_files = [format_file_for_display(f) for f in files]
        click.echo(format_output(formatted_files, output))
    except Exception as e:
        click.echo(f"Error listing files: {e}", err=True)
        raise click.Abort()


@main.command()
@click.argument("file_id")
@click.option("--name", help="New file name")
@click.option("--description", help="New description")
@click.option("--starred", type=bool, help="Star status")
@click.option(
    "--output",
    type=click.Choice(["unix", "json", "llm"]),
    default="unix",
    help="Output format",
)
def update_cmd(file_id, name, description, starred, output):
    """Update file metadata.

    Examples:
        gwc-drive update file_id --name "New Name"
        gwc-drive update file_id --description "Updated description"
        gwc-drive update file_id --starred true
    """
    try:
        result = update_file(
            file_id=file_id,
            name=name,
            description=description,
            starred=starred,
        )
        formatted = format_file_for_display(result)
        click.echo(format_output([formatted], output))
    except Exception as e:
        click.echo(f"Error updating file: {e}", err=True)
        raise click.Abort()


@main.command()
@click.argument("file_id")
def delete_cmd(file_id):
    """Permanently delete a file.

    Examples:
        gwc-drive delete file_id
    """
    try:
        delete_file(file_id)
        click.echo(f"File {file_id} deleted.")
    except Exception as e:
        click.echo(f"Error deleting file: {e}", err=True)
        raise click.Abort()


@main.command()
@click.argument("file_id")
@click.option("--name", required=True, help="Name for copied file")
@click.option("--parents", multiple=True, help="Parent folder IDs for copy")
@click.option(
    "--output",
    type=click.Choice(["unix", "json", "llm"]),
    default="unix",
    help="Output format",
)
def copy_cmd(file_id, name, parents, output):
    """Create a copy of a file.

    Examples:
        gwc-drive copy file_id --name "Copy of Document"
        gwc-drive copy file_id --name "Copy" --parents folder_id
    """
    try:
        new_file_id = copy_file(
            file_id=file_id,
            name=name,
            parents=list(parents) if parents else None,
        )
        result = {"id": new_file_id, "name": name}
        click.echo(format_output([result], output))
    except Exception as e:
        click.echo(f"Error copying file: {e}", err=True)
        raise click.Abort()


# ============================================================================
# Export and Download
# ============================================================================


@main.command()
@click.argument("file_id")
@click.option("--mime-type", default="application/pdf", help="Export MIME type")
@click.option("--output-file", required=True, help="Output file path")
def export_cmd(file_id, mime_type, output_file):
    """Export a Google Workspace document.

    Examples:
        gwc-drive export sheet_id --mime-type text/csv --output-file budget.csv
        gwc-drive export doc_id --mime-type application/pdf --output-file report.pdf
    """
    try:
        content = export_file(file_id, mime_type)
        with open(output_file, "wb") as f:
            f.write(content)
        click.echo(f"File exported to {output_file}")
    except Exception as e:
        click.echo(f"Error exporting file: {e}", err=True)
        raise click.Abort()


@main.command()
@click.argument("file_id")
@click.option("--output-file", required=True, help="Output file path")
def download_cmd(file_id, output_file):
    """Download file content.

    Examples:
        gwc-drive download file_id --output-file /path/to/save
    """
    try:
        content = download_file(file_id)
        with open(output_file, "wb") as f:
            f.write(content)
        click.echo(f"File downloaded to {output_file}")
    except Exception as e:
        click.echo(f"Error downloading file: {e}", err=True)
        raise click.Abort()


# ============================================================================
# Labels
# ============================================================================


@main.command()
@click.argument("file_id")
@click.option(
    "--output",
    type=click.Choice(["unix", "json", "llm"]),
    default="unix",
    help="Output format",
)
def labels_cmd(file_id, output):
    """List labels on a file.

    Examples:
        gwc-drive labels file_id --output llm
    """
    try:
        labels = list_labels(file_id)
        click.echo(format_output(labels, output))
    except Exception as e:
        click.echo(f"Error listing labels: {e}", err=True)
        raise click.Abort()


@main.command()
@click.argument("file_id")
@click.option("--add", multiple=True, help="Label IDs to add")
@click.option("--remove", multiple=True, help="Label IDs to remove")
@click.option(
    "--output",
    type=click.Choice(["unix", "json", "llm"]),
    default="unix",
    help="Output format",
)
def modify_labels_cmd(file_id, add, remove, output):
    """Modify labels on a file.

    Examples:
        gwc-drive modify-labels file_id --add label_id1 --add label_id2
        gwc-drive modify-labels file_id --remove label_id
    """
    try:
        labels = modify_labels(
            file_id=file_id,
            add_label_ids=list(add) if add else None,
            remove_label_ids=list(remove) if remove else None,
        )
        click.echo(format_output(labels, output))
    except Exception as e:
        click.echo(f"Error modifying labels: {e}", err=True)
        raise click.Abort()


# ============================================================================
# Trash
# ============================================================================


@main.command()
@click.argument("file_id")
@click.option(
    "--output",
    type=click.Choice(["unix", "json", "llm"]),
    default="unix",
    help="Output format",
)
def trash_cmd(file_id, output):
    """Move file to trash.

    Examples:
        gwc-drive trash file_id
    """
    try:
        result = trash_file(file_id)
        formatted = format_file_for_display(result)
        click.echo(format_output([formatted], output))
    except Exception as e:
        click.echo(f"Error trashing file: {e}", err=True)
        raise click.Abort()


@main.command()
@click.argument("file_id")
@click.option(
    "--output",
    type=click.Choice(["unix", "json", "llm"]),
    default="unix",
    help="Output format",
)
def untrash_cmd(file_id, output):
    """Restore file from trash.

    Examples:
        gwc-drive untrash file_id
    """
    try:
        result = untrash_file(file_id)
        formatted = format_file_for_display(result)
        click.echo(format_output([formatted], output))
    except Exception as e:
        click.echo(f"Error untrashing file: {e}", err=True)
        raise click.Abort()


@main.command()
def empty_trash_cmd():
    """Empty trash permanently.

    Examples:
        gwc-drive empty-trash
    """
    try:
        message = empty_trash()
        click.echo(message)
    except Exception as e:
        click.echo(f"Error emptying trash: {e}", err=True)
        raise click.Abort()


# ============================================================================
# About and Info
# ============================================================================


@main.command()
@click.option(
    "--output",
    type=click.Choice(["unix", "json", "llm"]),
    default="unix",
    help="Output format",
)
def about_cmd(output):
    """Get user information and storage quota.

    Examples:
        gwc-drive about --output llm
        gwc-drive about --output json
    """
    try:
        about = get_about()
        user = about.get("user", {})
        quota = about.get("storageQuota", {})

        result = {
            "email": user.get("emailAddress", "—"),
            "name": user.get("displayName", "—"),
        }
        result.update(format_quota_for_display(quota))

        click.echo(format_output([result], output))
    except Exception as e:
        click.echo(f"Error getting about info: {e}", err=True)
        raise click.Abort()


@main.command()
@click.option(
    "--output",
    type=click.Choice(["unix", "json", "llm"]),
    default="unix",
    help="Output format",
)
def quota_cmd(output):
    """Get storage quota information.

    Examples:
        gwc-drive quota --output llm
    """
    try:
        quota = get_quota()
        formatted = format_quota_for_display(quota)
        click.echo(format_output([formatted], output))
    except Exception as e:
        click.echo(f"Error getting quota: {e}", err=True)
        raise click.Abort()


# ============================================================================
# Help and Reference
# ============================================================================


@main.command()
def mime_types_cmd():
    """Show common MIME types.

    Examples:
        gwc-drive mime-types
    """
    types = get_mime_types()
    for name, mime_type in types.items():
        click.echo(f"{name:15} {mime_type}")


@main.command()
def export_formats_cmd():
    """Show available export formats.

    Examples:
        gwc-drive export-formats
    """
    formats = get_export_mime_types()
    for doc_type, export_formats in formats.items():
        click.echo(f"\n{doc_type.upper()}:")
        for format_name, mime_type in export_formats.items():
            click.echo(f"  {format_name:15} {mime_type}")


if __name__ == "__main__":
    main()
