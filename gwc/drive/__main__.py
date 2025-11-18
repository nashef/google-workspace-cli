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
    create_permission,
    get_permission,
    list_permissions,
    update_permission,
    delete_permission,
    create_drive,
    get_drive,
    list_drives,
    update_drive,
    delete_drive,
    hide_drive,
    unhide_drive,
    get_revision,
    list_revisions,
    delete_revision,
    keep_revision,
    restore_revision,
    get_start_page_token,
    list_changes,
    create_comment,
    get_comment,
    list_comments,
    update_comment,
    delete_comment,
    create_reply,
    list_replies,
    generate_ids,
    list_apps,
    get_app,
    create_channel,
    stop_channel,
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


# ============================================================================
# Phase 2: Permissions (Access Control)
# ============================================================================


@main.command()
@click.argument("file_id")
@click.option("--email", required=True, help="User or group email (or domain for domain permission)")
@click.option("--role", default="reader", help="Role: owner, organizer, writer, commenter, reader")
@click.option("--type", "permission_type", default="user", help="Type: user, group, domain, or anyone")
@click.option("--send-notification/--no-send-notification", default=True, help="Send notification email")
@click.option("--transfer-ownership/--no-transfer-ownership", default=False, help="Transfer ownership")
@click.option(
    "--output",
    type=click.Choice(["unix", "json", "llm"]),
    default="unix",
    help="Output format",
)
def create_permission_cmd(file_id, email, role, permission_type, send_notification, transfer_ownership, output):
    """Create a permission (share a file or folder).

    Examples:
        gwc-drive create-permission file_id --email user@example.com --role reader
        gwc-drive create-permission file_id --email user@example.com --role editor
        gwc-drive create-permission file_id --email example.com --type domain --role reader
    """
    try:
        perm_id = create_permission(
            file_id=file_id,
            email_or_domain=email,
            role=role,
            permission_type=permission_type,
            send_notification=send_notification,
            transfer_ownership=transfer_ownership,
        )
        result = {"id": perm_id, "email": email, "role": role, "type": permission_type}
        click.echo(format_output([result], output))
    except Exception as e:
        click.echo(f"Error creating permission: {e}", err=True)
        raise click.Abort()


@main.command()
@click.argument("file_id")
@click.argument("permission_id")
@click.option(
    "--output",
    type=click.Choice(["unix", "json", "llm"]),
    default="unix",
    help="Output format",
)
def get_permission_cmd(file_id, permission_id, output):
    """Get a specific permission.

    Examples:
        gwc-drive get-permission file_id permission_id --output llm
    """
    try:
        perm = get_permission(file_id, permission_id)
        click.echo(format_output([perm], output))
    except Exception as e:
        click.echo(f"Error getting permission: {e}", err=True)
        raise click.Abort()


@main.command()
@click.argument("file_id")
@click.option(
    "--output",
    type=click.Choice(["unix", "json", "llm"]),
    default="unix",
    help="Output format",
)
def list_permissions_cmd(file_id, output):
    """List all permissions on a file or folder.

    Examples:
        gwc-drive list-permissions file_id --output llm
    """
    try:
        perms = list_permissions(file_id)
        click.echo(format_output(perms, output))
    except Exception as e:
        click.echo(f"Error listing permissions: {e}", err=True)
        raise click.Abort()


@main.command()
@click.argument("file_id")
@click.argument("permission_id")
@click.option("--role", help="New role: owner, organizer, writer, commenter, reader")
@click.option(
    "--output",
    type=click.Choice(["unix", "json", "llm"]),
    default="unix",
    help="Output format",
)
def update_permission_cmd(file_id, permission_id, role, output):
    """Update a permission (change role).

    Examples:
        gwc-drive update-permission file_id permission_id --role editor
    """
    try:
        perm = update_permission(file_id, permission_id, role=role)
        click.echo(format_output([perm], output))
    except Exception as e:
        click.echo(f"Error updating permission: {e}", err=True)
        raise click.Abort()


@main.command()
@click.argument("file_id")
@click.argument("permission_id")
def delete_permission_cmd(file_id, permission_id):
    """Delete a permission (revoke access).

    Examples:
        gwc-drive delete-permission file_id permission_id
    """
    try:
        perm_id = delete_permission(file_id, permission_id)
        click.echo(f"Permission {perm_id} deleted.")
    except Exception as e:
        click.echo(f"Error deleting permission: {e}", err=True)
        raise click.Abort()


# ============================================================================
# Phase 2: Shared Drives
# ============================================================================


@main.command()
@click.option("--name", required=True, help="Shared drive name")
@click.option(
    "--output",
    type=click.Choice(["unix", "json", "llm"]),
    default="unix",
    help="Output format",
)
def create_drive_cmd(name, output):
    """Create a new shared drive.

    Examples:
        gwc-drive create-drive --name "Team Drive"
    """
    try:
        drive_id = create_drive(name=name)
        result = {"id": drive_id, "name": name}
        click.echo(format_output([result], output))
    except Exception as e:
        click.echo(f"Error creating drive: {e}", err=True)
        raise click.Abort()


@main.command()
@click.argument("drive_id")
@click.option(
    "--output",
    type=click.Choice(["unix", "json", "llm"]),
    default="unix",
    help="Output format",
)
def get_drive_cmd(drive_id, output):
    """Get shared drive metadata.

    Examples:
        gwc-drive get-drive drive_id --output llm
    """
    try:
        drive = get_drive(drive_id)
        click.echo(format_output([drive], output))
    except Exception as e:
        click.echo(f"Error getting drive: {e}", err=True)
        raise click.Abort()


@main.command()
@click.option("--limit", default=10, type=int, help="Max results (1-100)")
@click.option(
    "--output",
    type=click.Choice(["unix", "json", "llm"]),
    default="unix",
    help="Output format",
)
def list_drives_cmd(limit, output):
    """List shared drives.

    Examples:
        gwc-drive list-drives --output llm
        gwc-drive list-drives --limit 50 --output json
    """
    try:
        drives = list_drives(limit=limit)
        click.echo(format_output(drives, output))
    except Exception as e:
        click.echo(f"Error listing drives: {e}", err=True)
        raise click.Abort()


@main.command()
@click.argument("drive_id")
@click.option("--name", help="New drive name")
@click.option(
    "--output",
    type=click.Choice(["unix", "json", "llm"]),
    default="unix",
    help="Output format",
)
def update_drive_cmd(drive_id, name, output):
    """Update shared drive metadata.

    Examples:
        gwc-drive update-drive drive_id --name "New Name"
    """
    try:
        drive = update_drive(drive_id, name=name)
        click.echo(format_output([drive], output))
    except Exception as e:
        click.echo(f"Error updating drive: {e}", err=True)
        raise click.Abort()


@main.command()
@click.argument("drive_id")
def delete_drive_cmd(drive_id):
    """Permanently delete a shared drive.

    Examples:
        gwc-drive delete-drive drive_id
    """
    try:
        result_id = delete_drive(drive_id)
        click.echo(f"Drive {result_id} deleted.")
    except Exception as e:
        click.echo(f"Error deleting drive: {e}", err=True)
        raise click.Abort()


@main.command()
@click.argument("drive_id")
@click.option(
    "--output",
    type=click.Choice(["unix", "json", "llm"]),
    default="unix",
    help="Output format",
)
def hide_drive_cmd(drive_id, output):
    """Hide shared drive from default view.

    Examples:
        gwc-drive hide-drive drive_id
    """
    try:
        drive = hide_drive(drive_id)
        click.echo(format_output([drive], output))
    except Exception as e:
        click.echo(f"Error hiding drive: {e}", err=True)
        raise click.Abort()


@main.command()
@click.argument("drive_id")
@click.option(
    "--output",
    type=click.Choice(["unix", "json", "llm"]),
    default="unix",
    help="Output format",
)
def unhide_drive_cmd(drive_id, output):
    """Restore shared drive to default view.

    Examples:
        gwc-drive unhide-drive drive_id
    """
    try:
        drive = unhide_drive(drive_id)
        click.echo(format_output([drive], output))
    except Exception as e:
        click.echo(f"Error unhiding drive: {e}", err=True)
        raise click.Abort()


# ============================================================================
# Phase 3: Revisions (Version History)
# ============================================================================


@main.command()
@click.argument("file_id")
@click.argument("revision_id")
@click.option(
    "--output",
    type=click.Choice(["unix", "json", "llm"]),
    default="unix",
    help="Output format",
)
def get_revision_cmd(file_id, revision_id, output):
    """Get a specific file revision.

    Examples:
        gwc-drive get-revision file_id revision_id --output llm
    """
    try:
        revision = get_revision(file_id, revision_id)
        click.echo(format_output([revision], output))
    except Exception as e:
        click.echo(f"Error getting revision: {e}", err=True)
        raise click.Abort()


@main.command()
@click.argument("file_id")
@click.option("--limit", default=10, type=int, help="Max results (1-1000)")
@click.option(
    "--output",
    type=click.Choice(["unix", "json", "llm"]),
    default="unix",
    help="Output format",
)
def list_revisions_cmd(file_id, limit, output):
    """List file revisions (version history).

    Examples:
        gwc-drive list-revisions file_id --output llm
        gwc-drive list-revisions file_id --limit 50 --output json
    """
    try:
        revisions = list_revisions(file_id, limit=limit)
        click.echo(format_output(revisions, output))
    except Exception as e:
        click.echo(f"Error listing revisions: {e}", err=True)
        raise click.Abort()


@main.command()
@click.argument("file_id")
@click.argument("revision_id")
def delete_revision_cmd(file_id, revision_id):
    """Delete a file revision permanently.

    Examples:
        gwc-drive delete-revision file_id revision_id
    """
    try:
        result_id = delete_revision(file_id, revision_id)
        click.echo(f"Revision {result_id} deleted.")
    except Exception as e:
        click.echo(f"Error deleting revision: {e}", err=True)
        raise click.Abort()


@main.command()
@click.argument("file_id")
@click.argument("revision_id")
@click.option("--forever/--not-forever", default=True, help="Keep revision forever")
@click.option(
    "--output",
    type=click.Choice(["unix", "json", "llm"]),
    default="unix",
    help="Output format",
)
def keep_revision_cmd(file_id, revision_id, forever, output):
    """Mark revision to keep forever (prevent auto-deletion after 30 days).

    Examples:
        gwc-drive keep-revision file_id revision_id
        gwc-drive keep-revision file_id revision_id --not-forever
    """
    try:
        revision = keep_revision(file_id, revision_id, keep_forever=forever)
        click.echo(format_output([revision], output))
    except Exception as e:
        click.echo(f"Error keeping revision: {e}", err=True)
        raise click.Abort()


@main.command()
@click.argument("file_id")
@click.argument("revision_id")
@click.option(
    "--output",
    type=click.Choice(["unix", "json", "llm"]),
    default="unix",
    help="Output format",
)
def restore_revision_cmd(file_id, revision_id, output):
    """Restore a file to a previous revision.

    Examples:
        gwc-drive restore-revision file_id revision_id --output llm
    """
    try:
        result = restore_revision(file_id, revision_id)
        click.echo(format_output([result], output))
    except Exception as e:
        click.echo(f"Error restoring revision: {e}", err=True)
        raise click.Abort()


# ============================================================================
# Phase 3: Changes (Sync Tracking)
# ============================================================================


@main.command()
def get_start_page_token_cmd():
    """Get starting pageToken for change tracking.

    Save this token and use it with list-changes to track modifications
    since this point. Useful for incremental sync.

    Examples:
        gwc-drive get-start-page-token
    """
    try:
        token = get_start_page_token()
        click.echo(token)
    except Exception as e:
        click.echo(f"Error getting start page token: {e}", err=True)
        raise click.Abort()


@main.command()
@click.argument("page_token")
@click.option("--limit", default=100, type=int, help="Max results (1-1000)")
@click.option(
    "--output",
    type=click.Choice(["unix", "json", "llm"]),
    default="unix",
    help="Output format",
)
def list_changes_cmd(page_token, limit, output):
    """List changes to files since a given pageToken.

    Use get-start-page-token to get initial token, then use this command
    to find what changed since that point.

    Examples:
        gwc-drive list-changes PAGE_TOKEN --output llm
        gwc-drive list-changes PAGE_TOKEN --limit 50 --output json
    """
    try:
        changes, next_token = list_changes(page_token, limit=limit)
        result = {"changes": changes, "nextPageToken": next_token}
        click.echo(format_output([result], output))
    except Exception as e:
        click.echo(f"Error listing changes: {e}", err=True)
        raise click.Abort()


# ============================================================================
# Phase 3: Comments
# ============================================================================


@main.command()
@click.argument("file_id")
@click.option("--content", required=True, help="Comment text")
@click.option(
    "--output",
    type=click.Choice(["unix", "json", "llm"]),
    default="unix",
    help="Output format",
)
def create_comment_cmd(file_id, content, output):
    """Create a comment on a file.

    Examples:
        gwc-drive create-comment file_id --content "Great work!"
    """
    try:
        comment_id = create_comment(file_id, content)
        result = {"id": comment_id, "content": content}
        click.echo(format_output([result], output))
    except Exception as e:
        click.echo(f"Error creating comment: {e}", err=True)
        raise click.Abort()


@main.command()
@click.argument("file_id")
@click.argument("comment_id")
@click.option(
    "--output",
    type=click.Choice(["unix", "json", "llm"]),
    default="unix",
    help="Output format",
)
def get_comment_cmd(file_id, comment_id, output):
    """Get a specific comment.

    Examples:
        gwc-drive get-comment file_id comment_id --output llm
    """
    try:
        comment = get_comment(file_id, comment_id)
        click.echo(format_output([comment], output))
    except Exception as e:
        click.echo(f"Error getting comment: {e}", err=True)
        raise click.Abort()


@main.command()
@click.argument("file_id")
@click.option("--limit", default=20, type=int, help="Max results (1-100)")
@click.option("--include-deleted/--no-include-deleted", default=False, help="Include deleted comments")
@click.option(
    "--output",
    type=click.Choice(["unix", "json", "llm"]),
    default="unix",
    help="Output format",
)
def list_comments_cmd(file_id, limit, include_deleted, output):
    """List comments on a file.

    Examples:
        gwc-drive list-comments file_id --output llm
        gwc-drive list-comments file_id --limit 50 --output json
    """
    try:
        comments = list_comments(file_id, limit=limit, include_deleted=include_deleted)
        click.echo(format_output(comments, output))
    except Exception as e:
        click.echo(f"Error listing comments: {e}", err=True)
        raise click.Abort()


@main.command()
@click.argument("file_id")
@click.argument("comment_id")
@click.option("--content", help="New comment text")
@click.option("--resolved", type=bool, help="Mark as resolved/unresolved")
@click.option(
    "--output",
    type=click.Choice(["unix", "json", "llm"]),
    default="unix",
    help="Output format",
)
def update_comment_cmd(file_id, comment_id, content, resolved, output):
    """Update a comment.

    Examples:
        gwc-drive update-comment file_id comment_id --content "Updated text"
        gwc-drive update-comment file_id comment_id --resolved true
    """
    try:
        comment = update_comment(file_id, comment_id, content=content, resolved=resolved)
        click.echo(format_output([comment], output))
    except Exception as e:
        click.echo(f"Error updating comment: {e}", err=True)
        raise click.Abort()


@main.command()
@click.argument("file_id")
@click.argument("comment_id")
def delete_comment_cmd(file_id, comment_id):
    """Delete a comment.

    Examples:
        gwc-drive delete-comment file_id comment_id
    """
    try:
        result_id = delete_comment(file_id, comment_id)
        click.echo(f"Comment {result_id} deleted.")
    except Exception as e:
        click.echo(f"Error deleting comment: {e}", err=True)
        raise click.Abort()


@main.command()
@click.argument("file_id")
@click.argument("comment_id")
@click.option("--content", required=True, help="Reply text")
@click.option(
    "--output",
    type=click.Choice(["unix", "json", "llm"]),
    default="unix",
    help="Output format",
)
def create_reply_cmd(file_id, comment_id, content, output):
    """Create a reply to a comment.

    Examples:
        gwc-drive create-reply file_id comment_id --content "I agree!"
    """
    try:
        reply_id = create_reply(file_id, comment_id, content)
        result = {"id": reply_id, "content": content}
        click.echo(format_output([result], output))
    except Exception as e:
        click.echo(f"Error creating reply: {e}", err=True)
        raise click.Abort()


@main.command()
@click.argument("file_id")
@click.argument("comment_id")
@click.option(
    "--output",
    type=click.Choice(["unix", "json", "llm"]),
    default="unix",
    help="Output format",
)
def list_replies_cmd(file_id, comment_id, output):
    """List replies to a comment.

    Examples:
        gwc-drive list-replies file_id comment_id --output llm
    """
    try:
        replies = list_replies(file_id, comment_id)
        click.echo(format_output(replies, output))
    except Exception as e:
        click.echo(f"Error listing replies: {e}", err=True)
        raise click.Abort()


# ============================================================================
# Phase 3.5: Bonus Features
# ============================================================================


@main.command()
@click.option("--count", default=1, type=int, help="Number of IDs to generate (1-1000)")
@click.option("--space", default="drive", help="Scope: 'drive' or 'appDataFolder'")
def generate_ids_cmd(count, space):
    """Pre-generate file IDs for batch operations.

    Useful for batch file creation workflows where you want to reserve
    IDs before actually creating the files.

    Examples:
        gwc-drive generate-ids --count 5
        gwc-drive generate-ids --count 100 --space appDataFolder
    """
    try:
        ids = generate_ids(count=count, space=space)
        for file_id in ids:
            click.echo(file_id)
    except Exception as e:
        click.echo(f"Error generating IDs: {e}", err=True)
        raise click.Abort()


@main.command()
@click.option(
    "--output",
    type=click.Choice(["unix", "json", "llm"]),
    default="unix",
    help="Output format",
)
def list_apps_cmd(output):
    """List installed applications on your Drive.

    Examples:
        gwc-drive list-apps --output llm
        gwc-drive list-apps --output json
    """
    try:
        apps = list_apps()
        click.echo(format_output(apps, output))
    except Exception as e:
        click.echo(f"Error listing apps: {e}", err=True)
        raise click.Abort()


@main.command()
@click.argument("app_id")
@click.option(
    "--output",
    type=click.Choice(["unix", "json", "llm"]),
    default="unix",
    help="Output format",
)
def get_app_cmd(app_id, output):
    """Get details about an installed application.

    Examples:
        gwc-drive get-app app_id --output llm
    """
    try:
        app = get_app(app_id)
        click.echo(format_output([app], output))
    except Exception as e:
        click.echo(f"Error getting app: {e}", err=True)
        raise click.Abort()


@main.command()
@click.argument("file_id")
@click.option("--address", help="HTTPS webhook URL for notifications")
@click.option("--channel-id", help="Unique channel ID (auto-generated if not provided)")
@click.option("--expiration-ms", type=int, help="Expiration in milliseconds (max 86400000 for 24 hours)")
@click.option(
    "--output",
    type=click.Choice(["unix", "json", "llm"]),
    default="unix",
    help="Output format",
)
def create_channel_cmd(file_id, address, channel_id, expiration_ms, output):
    """Create a push notification channel for a file.

    Requires an HTTPS webhook URL. Google Drive will send notifications
    when the file changes.

    Examples:
        gwc-drive create-channel file_id --address https://myserver.com/webhook
        gwc-drive create-channel file_id --address https://myserver.com/webhook --expiration-ms 86400000
    """
    try:
        channel = create_channel(
            file_id=file_id,
            channel_address=address,
            channel_id=channel_id,
            expiration_ms=expiration_ms,
        )
        click.echo(format_output([channel], output))
    except Exception as e:
        click.echo(f"Error creating channel: {e}", err=True)
        raise click.Abort()


@main.command()
@click.argument("channel_id")
@click.argument("resource_id")
def stop_channel_cmd(channel_id, resource_id):
    """Stop receiving notifications on a channel.

    Examples:
        gwc-drive stop-channel channel_id resource_id
    """
    try:
        message = stop_channel(channel_id, resource_id)
        click.echo(message)
    except Exception as e:
        click.echo(f"Error stopping channel: {e}", err=True)
        raise click.Abort()


if __name__ == "__main__":
    main()
