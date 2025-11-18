"""Google Drive API operations for Phase 1."""

import io
import mimetypes
from typing import Any, Dict, List, Optional, Tuple
from functools import lru_cache
from googleapiclient.discovery import build, Resource

from ..shared.auth import get_credentials


# Define Drive API scopes
DRIVE_SCOPES = [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/drive.file",
]


@lru_cache(maxsize=1)
def build_drive_service() -> Resource:
    """Build Drive API service with caching."""
    creds = get_credentials(scopes=DRIVE_SCOPES)
    return build("drive", "v3", credentials=creds)


def get_drive_service():
    """Get authenticated Drive API service."""
    return build_drive_service()


# ============================================================================
# File Operations (Create, Get, Update, Delete, Copy)
# ============================================================================


def create_file(
    name: str,
    mime_type: str = "application/vnd.google-apps.document",
    parents: Optional[List[str]] = None,
    description: str = "",
    properties: Optional[Dict[str, str]] = None,
    starred: bool = False,
    file_content: Optional[bytes] = None,
) -> str:
    """Create a new file or folder.

    Args:
        name: File/folder name
        mime_type: MIME type (default: Google Docs). Use "application/vnd.google-apps.folder" for folders
        parents: List of parent folder IDs
        description: File description
        properties: Custom key-value properties
        starred: Star the file
        file_content: File content (bytes) to upload

    Returns:
        File ID
    """
    service = get_drive_service()

    file_metadata = {
        "name": name,
        "mimeType": mime_type,
        "description": description,
        "starred": starred,
    }

    if parents:
        file_metadata["parents"] = parents
    if properties:
        file_metadata["properties"] = properties

    if file_content:
        media = io.BytesIO(file_content)
        result = service.files().create(
            body=file_metadata,
            media_body=media,
            fields="id, webViewLink"
        ).execute()
    else:
        result = service.files().create(
            body=file_metadata,
            fields="id, webViewLink"
        ).execute()

    return result.get("id", "")


def get_file(file_id: str, download: bool = False) -> Dict[str, Any]:
    """Get file metadata or download content.

    Args:
        file_id: File ID
        download: If True, returns file content as 'content' key in dict

    Returns:
        File metadata dict, optionally with 'content' key
    """
    service = get_drive_service()

    file_metadata = service.files().get(
        fileId=file_id,
        fields="id, name, mimeType, size, createdTime, modifiedTime, owners, parents, webViewLink, description, properties, starred, trashed, permissions"
    ).execute()

    if download:
        content = service.files().get_media(fileId=file_id).execute()
        file_metadata["content"] = content

    return file_metadata


def list_files(
    query: str = "",
    limit: int = 10,
    page_token: Optional[str] = None,
    order_by: str = "modifiedTime desc",
) -> Tuple[List[Dict[str, Any]], Optional[str]]:
    """List files with optional filtering.

    Args:
        query: Drive API query (e.g., "name contains 'budget' and trashed = false")
        limit: Max results (1-1000)
        page_token: For pagination
        order_by: Sort order (e.g., "name", "createdTime", "modifiedTime desc")

    Returns:
        Tuple of (files list, next page token)
    """
    service = get_drive_service()

    if not query:
        query = "trashed = false"

    results = service.files().list(
        q=query,
        pageSize=min(limit, 1000),
        pageToken=page_token,
        orderBy=order_by,
        fields="nextPageToken, files(id, name, mimeType, size, createdTime, modifiedTime, owners, parents, webViewLink, description, trashed)"
    ).execute()

    files = results.get("files", [])
    next_page = results.get("nextPageToken")

    return files, next_page


def update_file(
    file_id: str,
    name: Optional[str] = None,
    description: Optional[str] = None,
    starred: Optional[bool] = None,
    properties: Optional[Dict[str, str]] = None,
    file_content: Optional[bytes] = None,
) -> Dict[str, Any]:
    """Update file metadata or content.

    Args:
        file_id: File ID
        name: New file name
        description: New description
        starred: Star status
        properties: Custom properties to update
        file_content: New file content

    Returns:
        Updated file metadata
    """
    service = get_drive_service()

    file_metadata = {}
    if name is not None:
        file_metadata["name"] = name
    if description is not None:
        file_metadata["description"] = description
    if starred is not None:
        file_metadata["starred"] = starred
    if properties is not None:
        file_metadata["properties"] = properties

    if file_content:
        media = io.BytesIO(file_content)
        result = service.files().update(
            fileId=file_id,
            body=file_metadata,
            media_body=media,
            fields="id, name, modifiedTime, webViewLink"
        ).execute()
    else:
        result = service.files().update(
            fileId=file_id,
            body=file_metadata,
            fields="id, name, modifiedTime, webViewLink"
        ).execute()

    return result


def delete_file(file_id: str) -> str:
    """Permanently delete a file.

    Args:
        file_id: File ID

    Returns:
        File ID
    """
    service = get_drive_service()
    service.files().delete(fileId=file_id).execute()
    return file_id


def copy_file(
    file_id: str,
    name: str,
    parents: Optional[List[str]] = None,
) -> str:
    """Create a copy of a file.

    Args:
        file_id: File ID to copy
        name: Name for copied file
        parents: Parent folder IDs for copy

    Returns:
        New file ID
    """
    service = get_drive_service()

    copy_metadata = {"name": name}
    if parents:
        copy_metadata["parents"] = parents

    result = service.files().copy(
        fileId=file_id,
        body=copy_metadata,
        fields="id, webViewLink"
    ).execute()

    return result.get("id", "")


# ============================================================================
# Export and Download
# ============================================================================


def export_file(
    file_id: str,
    mime_type: str = "application/pdf",
) -> bytes:
    """Export a Google Workspace document to another format.

    Args:
        file_id: File ID (must be Google Workspace document)
        mime_type: Export MIME type (e.g., 'application/pdf', 'text/csv', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')

    Returns:
        File content as bytes
    """
    service = get_drive_service()
    return service.files().export(fileId=file_id, mimeType=mime_type).execute()


def download_file(file_id: str) -> bytes:
    """Download file content.

    Args:
        file_id: File ID

    Returns:
        File content as bytes
    """
    service = get_drive_service()
    return service.files().get_media(fileId=file_id).execute()


# ============================================================================
# Labels
# ============================================================================


def list_labels(file_id: str) -> List[Dict[str, Any]]:
    """List labels on a file.

    Args:
        file_id: File ID

    Returns:
        List of label dicts
    """
    service = get_drive_service()

    result = service.files().listLabels(fileId=file_id).execute()
    return result.get("labels", [])


def modify_labels(
    file_id: str,
    add_label_ids: Optional[List[str]] = None,
    remove_label_ids: Optional[List[str]] = None,
) -> List[Dict[str, Any]]:
    """Modify labels on a file.

    Args:
        file_id: File ID
        add_label_ids: Label IDs to add
        remove_label_ids: Label IDs to remove

    Returns:
        Updated labels list
    """
    service = get_drive_service()

    body = {}
    if add_label_ids:
        body["labelIds"] = {"addIds": add_label_ids}
    if remove_label_ids:
        if "labelIds" not in body:
            body["labelIds"] = {}
        body["labelIds"]["removeIds"] = remove_label_ids

    result = service.files().modifyLabels(
        fileId=file_id,
        body=body
    ).execute()

    return result.get("labels", [])


# ============================================================================
# Trash and Cleanup
# ============================================================================


def trash_file(file_id: str) -> Dict[str, Any]:
    """Move file to trash (soft delete).

    Args:
        file_id: File ID

    Returns:
        File metadata
    """
    service = get_drive_service()

    result = service.files().update(
        fileId=file_id,
        body={"trashed": True},
        fields="id, name, trashed"
    ).execute()

    return result


def untrash_file(file_id: str) -> Dict[str, Any]:
    """Restore file from trash.

    Args:
        file_id: File ID

    Returns:
        File metadata
    """
    service = get_drive_service()

    result = service.files().update(
        fileId=file_id,
        body={"trashed": False},
        fields="id, name, trashed"
    ).execute()

    return result


def empty_trash() -> str:
    """Permanently delete all trashed files.

    Returns:
        Confirmation message
    """
    service = get_drive_service()
    service.files().emptyTrash().execute()
    return "Trash emptied successfully"


# ============================================================================
# About (User Info and Quota)
# ============================================================================


def get_about() -> Dict[str, Any]:
    """Get user information and storage quota.

    Returns:
        About dict with user and quota information
    """
    service = get_drive_service()

    result = service.about().get(
        fields="user, storageQuota, appInstalled, canCreateDrives, canCreateTeamDrives"
    ).execute()

    return result


def get_quota() -> Dict[str, Any]:
    """Get storage quota information.

    Returns:
        Dict with quota info (limit, usage, etc.)
    """
    about = get_about()
    return about.get("storageQuota", {})


# ============================================================================
# Phase 2: Permissions (Access Control)
# ============================================================================


def create_permission(
    file_id: str,
    email_or_domain: str,
    role: str = "reader",
    permission_type: str = "user",
    send_notification: bool = True,
    transfer_ownership: bool = False,
) -> str:
    """Create a permission (share a file).

    Args:
        file_id: File or shared drive ID
        email_or_domain: User email, group email, or domain (for type=domain)
        role: Permission role (owner, organizer, fileOrganizer, writer, commenter, reader)
        permission_type: user, group, domain, or anyone
        send_notification: Send notification email to recipient
        transfer_ownership: Transfer ownership (only with role=owner, type=user)

    Returns:
        Permission ID
    """
    service = get_drive_service()

    permission_body = {
        "role": role,
        "type": permission_type,
    }

    if permission_type in ("user", "group"):
        permission_body["emailAddress"] = email_or_domain
    elif permission_type == "domain":
        permission_body["domain"] = email_or_domain

    result = service.permissions().create(
        fileId=file_id,
        body=permission_body,
        sendNotificationEmail=send_notification,
        transferOwnership=transfer_ownership,
        fields="id, emailAddress, displayName, role, type, domain"
    ).execute()

    return result.get("id", "")


def get_permission(file_id: str, permission_id: str) -> Dict[str, Any]:
    """Get a specific permission.

    Args:
        file_id: File or shared drive ID
        permission_id: Permission ID

    Returns:
        Permission dict
    """
    service = get_drive_service()

    result = service.permissions().get(
        fileId=file_id,
        permissionId=permission_id,
        fields="id, emailAddress, displayName, role, type, domain, deleted"
    ).execute()

    return result


def list_permissions(file_id: str) -> List[Dict[str, Any]]:
    """List all permissions on a file or shared drive.

    Args:
        file_id: File or shared drive ID

    Returns:
        List of permission dicts
    """
    service = get_drive_service()

    results = service.permissions().list(
        fileId=file_id,
        fields="permissions(id, emailAddress, displayName, role, type, domain, deleted)",
        pageSize=100
    ).execute()

    return results.get("permissions", [])


def update_permission(
    file_id: str,
    permission_id: str,
    role: Optional[str] = None,
) -> Dict[str, Any]:
    """Update a permission (change role).

    Args:
        file_id: File or shared drive ID
        permission_id: Permission ID
        role: New role (owner, organizer, fileOrganizer, writer, commenter, reader)

    Returns:
        Updated permission dict
    """
    service = get_drive_service()

    body = {}
    if role:
        body["role"] = role

    result = service.permissions().update(
        fileId=file_id,
        permissionId=permission_id,
        body=body,
        fields="id, emailAddress, displayName, role, type, domain"
    ).execute()

    return result


def delete_permission(file_id: str, permission_id: str) -> str:
    """Delete a permission (revoke access).

    Args:
        file_id: File or shared drive ID
        permission_id: Permission ID

    Returns:
        Permission ID
    """
    service = get_drive_service()
    service.permissions().delete(
        fileId=file_id,
        permissionId=permission_id
    ).execute()
    return permission_id


# ============================================================================
# Phase 2: Shared Drives
# ============================================================================


def create_drive(
    name: str,
    request_id: Optional[str] = None,
) -> str:
    """Create a new shared drive.

    Args:
        name: Shared drive name
        request_id: Unique request ID (for idempotency)

    Returns:
        Shared drive ID
    """
    service = get_drive_service()

    drive_body = {"name": name}

    result = service.drives().create(
        body=drive_body,
        requestId=request_id or f"drive_{name}_{int(__import__('time').time())}",
        fields="id, name, createdTime"
    ).execute()

    return result.get("id", "")


def get_drive(drive_id: str) -> Dict[str, Any]:
    """Get shared drive metadata.

    Args:
        drive_id: Shared drive ID

    Returns:
        Shared drive dict
    """
    service = get_drive_service()

    result = service.drives().get(
        driveId=drive_id,
        fields="id, name, createdTime, restrictions, capabilities, hidden"
    ).execute()

    return result


def list_drives(limit: int = 10) -> List[Dict[str, Any]]:
    """List shared drives.

    Args:
        limit: Max results (1-100)

    Returns:
        List of shared drive dicts
    """
    service = get_drive_service()

    results = service.drives().list(
        pageSize=min(limit, 100),
        fields="drives(id, name, createdTime, hidden, capabilities)",
        useDomainAdminAccess=False
    ).execute()

    return results.get("drives", [])


def update_drive(
    drive_id: str,
    name: Optional[str] = None,
) -> Dict[str, Any]:
    """Update shared drive metadata.

    Args:
        drive_id: Shared drive ID
        name: New drive name

    Returns:
        Updated shared drive dict
    """
    service = get_drive_service()

    body = {}
    if name:
        body["name"] = name

    result = service.drives().update(
        driveId=drive_id,
        body=body,
        fields="id, name, createdTime"
    ).execute()

    return result


def delete_drive(drive_id: str) -> str:
    """Permanently delete a shared drive.

    Args:
        drive_id: Shared drive ID (must be organizer)

    Returns:
        Shared drive ID
    """
    service = get_drive_service()
    service.drives().delete(driveId=drive_id).execute()
    return drive_id


def hide_drive(drive_id: str) -> Dict[str, Any]:
    """Hide shared drive from default view.

    Args:
        drive_id: Shared drive ID

    Returns:
        Updated shared drive dict
    """
    service = get_drive_service()

    result = service.drives().hide(
        driveId=drive_id,
        fields="id, name, hidden"
    ).execute()

    return result


def unhide_drive(drive_id: str) -> Dict[str, Any]:
    """Restore shared drive to default view.

    Args:
        drive_id: Shared drive ID

    Returns:
        Updated shared drive dict
    """
    service = get_drive_service()

    result = service.drives().unhide(
        driveId=drive_id,
        fields="id, name, hidden"
    ).execute()

    return result


# ============================================================================
# Helper Functions
# ============================================================================


def format_file_for_display(file_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Format file metadata for display.

    Args:
        file_dict: File metadata from API

    Returns:
        Formatted dict
    """
    formatted = {
        "id": file_dict.get("id"),
        "name": file_dict.get("name"),
        "type": "Folder" if file_dict.get("mimeType") == "application/vnd.google-apps.folder" else "File",
        "mime_type": file_dict.get("mimeType"),
        "size": f"{int(file_dict.get('size', 0)) / 1024 / 1024:.1f} MB" if file_dict.get("size") else "—",
        "created": file_dict.get("createdTime", "—"),
        "modified": file_dict.get("modifiedTime", "—"),
        "owner": file_dict.get("owners", [{}])[0].get("displayName", "Unknown") if file_dict.get("owners") else "Unknown",
        "link": file_dict.get("webViewLink", "—"),
        "trashed": file_dict.get("trashed", False),
    }
    return formatted


def format_quota_for_display(quota_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Format quota information for display.

    Args:
        quota_dict: Quota data from API

    Returns:
        Formatted dict
    """
    limit = int(quota_dict.get("limit", 0))
    usage = int(quota_dict.get("usage", 0))
    trash = int(quota_dict.get("trashBytes", 0))

    # Calculate percentages and converted sizes
    percent_used = (usage / limit * 100) if limit > 0 else 0
    limit_gb = limit / 1024 / 1024 / 1024
    usage_gb = usage / 1024 / 1024 / 1024
    trash_gb = trash / 1024 / 1024 / 1024

    return {
        "total_storage": f"{limit_gb:.1f} GB",
        "used_storage": f"{usage_gb:.1f} GB",
        "available_storage": f"{(limit - usage) / 1024 / 1024 / 1024:.1f} GB",
        "trash_storage": f"{trash_gb:.1f} GB",
        "percent_used": f"{percent_used:.1f}%",
    }


def guess_mime_type(filename: str) -> str:
    """Guess MIME type from filename.

    Args:
        filename: File name

    Returns:
        MIME type
    """
    mime_type, _ = mimetypes.guess_type(filename)
    return mime_type or "application/octet-stream"


def get_mime_types() -> Dict[str, str]:
    """Get common Google Workspace MIME types.

    Returns:
        Dict mapping type names to MIME types
    """
    return {
        "docs": "application/vnd.google-apps.document",
        "sheets": "application/vnd.google-apps.spreadsheet",
        "slides": "application/vnd.google-apps.presentation",
        "folder": "application/vnd.google-apps.folder",
        "forms": "application/vnd.google-apps.form",
        "sites": "application/vnd.google-apps.site",
    }


def get_export_mime_types() -> Dict[str, Dict[str, str]]:
    """Get export MIME types for Google Workspace documents.

    Returns:
        Dict mapping document type to export format options
    """
    return {
        "document": {
            "pdf": "application/pdf",
            "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "odt": "application/vnd.oasis.opendocument.text",
            "rtf": "application/rtf",
            "txt": "text/plain",
            "epub": "application/epub+zip",
            "zip": "application/zip",
        },
        "spreadsheet": {
            "csv": "text/csv",
            "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "ods": "application/vnd.oasis.opendocument.spreadsheet",
            "pdf": "application/pdf",
            "tsv": "text/tab-separated-values",
            "ooxml": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "zip": "application/zip",
        },
        "presentation": {
            "pdf": "application/pdf",
            "pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
            "odp": "application/vnd.oasis.opendocument.presentation",
            "png": "image/png",
            "jpg": "image/jpeg",
            "svg": "image/svg+xml",
            "zip": "application/zip",
        },
    }


# ============================================================================
# Phase 3: Revisions (Version History)
# ============================================================================


def get_revision(file_id: str, revision_id: str) -> Dict[str, Any]:
    """Get a specific file revision.

    Args:
        file_id: File ID
        revision_id: Revision ID

    Returns:
        Revision metadata
    """
    service = get_drive_service()

    result = service.revisions().get(
        fileId=file_id,
        revisionId=revision_id,
        fields="id, mimeType, modifiedTime, modifiedByMe, lastModifyingUser, size, originalFilename, keepForever"
    ).execute()

    return result


def list_revisions(file_id: str, limit: int = 10) -> List[Dict[str, Any]]:
    """List file revisions (version history).

    Args:
        file_id: File ID
        limit: Max results (1-1000)

    Returns:
        List of revision dicts
    """
    service = get_drive_service()

    results = service.revisions().list(
        fileId=file_id,
        pageSize=min(limit, 1000),
        fields="revisions(id, modifiedTime, modifiedByMe, lastModifyingUser, size, originalFilename, keepForever)",
    ).execute()

    return results.get("revisions", [])


def delete_revision(file_id: str, revision_id: str) -> str:
    """Delete a file revision permanently.

    Args:
        file_id: File ID
        revision_id: Revision ID to delete

    Returns:
        Revision ID
    """
    service = get_drive_service()

    service.revisions().delete(
        fileId=file_id,
        revisionId=revision_id
    ).execute()

    return revision_id


def keep_revision(file_id: str, revision_id: str, keep_forever: bool = True) -> Dict[str, Any]:
    """Mark revision to keep forever (prevent auto-deletion after 30 days).

    Args:
        file_id: File ID
        revision_id: Revision ID
        keep_forever: Whether to keep revision forever

    Returns:
        Updated revision metadata
    """
    service = get_drive_service()

    result = service.revisions().update(
        fileId=file_id,
        revisionId=revision_id,
        body={"keepForever": keep_forever},
        fields="id, keepForever, modifiedTime"
    ).execute()

    return result


def restore_revision(file_id: str, revision_id: str) -> Dict[str, Any]:
    """Restore a file to a previous revision.

    Args:
        file_id: File ID
        revision_id: Revision ID to restore to

    Returns:
        Updated file metadata
    """
    service = get_drive_service()

    # Copy the revision content to current version
    result = service.revisions().get(
        fileId=file_id,
        revisionId=revision_id,
        fields="*"
    ).execute()

    # Update the file with restored content
    update_result = service.files().update(
        fileId=file_id,
        body={"name": result.get("originalFilename", "Restored")},
        fields="id, name, modifiedTime"
    ).execute()

    return update_result


# ============================================================================
# Phase 3: Changes (Sync Tracking)
# ============================================================================


def get_start_page_token() -> str:
    """Get the starting pageToken for change tracking.

    Use this when initializing incremental sync. Save the token for later
    use to check what changed since this point.

    Returns:
        Starting page token for changes
    """
    service = get_drive_service()

    result = service.changes().getStartPageToken().execute()
    return result.get("startPageToken", "")


def list_changes(page_token: str, limit: int = 100) -> Tuple[List[Dict[str, Any]], str]:
    """List changes to files since a given pageToken.

    Args:
        page_token: Page token from previous call or getStartPageToken()
        limit: Max results (1-1000)

    Returns:
        Tuple of (changes list, next page token)
    """
    service = get_drive_service()

    results = service.changes().list(
        pageToken=page_token,
        pageSize=min(limit, 1000),
        spaces="drive",
        fields="changes(id, type, time, fileId, file(id, name, mimeType, trashed)), nextPageToken",
    ).execute()

    changes = results.get("changes", [])
    next_token = results.get("nextPageToken", "")

    return changes, next_token


# ============================================================================
# Phase 3: Comments
# ============================================================================


def create_comment(
    file_id: str,
    content: str,
    anchor: Optional[str] = None,
) -> str:
    """Create a comment on a file.

    Args:
        file_id: File ID
        content: Comment text
        anchor: Optional anchor (for replies use replyId in parent comment)

    Returns:
        Comment ID
    """
    service = get_drive_service()

    body = {
        "content": content,
    }

    if anchor:
        body["anchor"] = anchor

    result = service.comments().create(
        fileId=file_id,
        body=body,
        fields="id, content, author, createdTime, resolved"
    ).execute()

    return result.get("id", "")


def get_comment(file_id: str, comment_id: str) -> Dict[str, Any]:
    """Get a specific comment.

    Args:
        file_id: File ID
        comment_id: Comment ID

    Returns:
        Comment metadata
    """
    service = get_drive_service()

    result = service.comments().get(
        fileId=file_id,
        commentId=comment_id,
        fields="id, content, author, createdTime, modifiedTime, resolved, replies"
    ).execute()

    return result


def list_comments(file_id: str, limit: int = 20, include_deleted: bool = False) -> List[Dict[str, Any]]:
    """List comments on a file.

    Args:
        file_id: File ID
        limit: Max results (1-100)
        include_deleted: Include deleted comments

    Returns:
        List of comment dicts
    """
    service = get_drive_service()

    results = service.comments().list(
        fileId=file_id,
        pageSize=min(limit, 100),
        includeDeleted=include_deleted,
        fields="comments(id, content, author, createdTime, modifiedTime, resolved, replies)",
    ).execute()

    return results.get("comments", [])


def update_comment(
    file_id: str,
    comment_id: str,
    content: Optional[str] = None,
    resolved: Optional[bool] = None,
) -> Dict[str, Any]:
    """Update a comment.

    Args:
        file_id: File ID
        comment_id: Comment ID
        content: New comment text
        resolved: Mark comment as resolved/unresolved

    Returns:
        Updated comment metadata
    """
    service = get_drive_service()

    body = {}
    if content is not None:
        body["content"] = content
    if resolved is not None:
        body["resolved"] = resolved

    result = service.comments().update(
        fileId=file_id,
        commentId=comment_id,
        body=body,
        fields="id, content, resolved, modifiedTime"
    ).execute()

    return result


def delete_comment(file_id: str, comment_id: str) -> str:
    """Delete a comment.

    Args:
        file_id: File ID
        comment_id: Comment ID

    Returns:
        Comment ID
    """
    service = get_drive_service()

    service.comments().delete(
        fileId=file_id,
        commentId=comment_id
    ).execute()

    return comment_id


def create_reply(
    file_id: str,
    comment_id: str,
    content: str,
) -> str:
    """Create a reply to a comment.

    Args:
        file_id: File ID
        comment_id: Parent comment ID
        content: Reply text

    Returns:
        Reply ID
    """
    service = get_drive_service()

    result = service.replies().create(
        fileId=file_id,
        commentId=comment_id,
        body={"content": content},
        fields="id, content, author, createdTime"
    ).execute()

    return result.get("id", "")


def list_replies(file_id: str, comment_id: str) -> List[Dict[str, Any]]:
    """List replies to a comment.

    Args:
        file_id: File ID
        comment_id: Comment ID

    Returns:
        List of reply dicts
    """
    service = get_drive_service()

    results = service.replies().list(
        fileId=file_id,
        commentId=comment_id,
        fields="replies(id, content, author, createdTime, modifiedTime)",
    ).execute()

    return results.get("replies", [])
