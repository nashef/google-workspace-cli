# Google Drive API Implementation Plan

## Overview

The Google Drive API v3 provides comprehensive file and folder management capabilities for Google Workspace. This document outlines the implementation strategy for `gwc-drive`, the CLI tool for Drive operations.

**API Reference:** https://developers.google.com/workspace/drive/api/reference/rest/v3

## Core Resources

The Drive API consists of 11 primary REST resources:

### 1. **Files** (Core operations - Phase 1)
- **create** - Creates a new file or folder
- **get** - Retrieves file metadata or content
- **list** - Lists files with optional filtering and pagination
- **update** - Updates file metadata or content
- **delete** - Permanently deletes a file
- **copy** - Creates a copy of a file
- **export** - Exports Google Workspace documents to other formats
- **download** - Downloads file content
- **generateIds** - Pre-generates file IDs for batch operations
- **listLabels** - Lists labels on a file
- **modifyLabels** - Adds or removes labels from a file
- **emptyTrash** - Permanently deletes all trashed files
- **watch** - Subscribes to file change notifications

### 2. **Permissions** (Access control - Phase 2)
- **create** - Creates a permission (shares file with user/group/domain/public)
- **get** - Retrieves a specific permission
- **list** - Lists all permissions on a file or shared drive
- **update** - Updates a permission (changes role, restrictions, etc.)
- **delete** - Removes a permission (unshares file)

**Roles:** owner, organizer, fileOrganizer, writer, commenter, reader

### 3. **Drives** (Shared drive management - Phase 2)
- **create** - Creates a new shared drive
- **get** - Retrieves shared drive metadata
- **list** - Lists user's shared drives
- **update** - Updates shared drive metadata
- **delete** - Permanently deletes a shared drive (organizer only)
- **hide** - Hides shared drive from default view
- **unhide** - Restores shared drive to default view

### 4. **Revisions** (Version control - Phase 3)
- **list** - Lists all revisions of a file
- **get** - Retrieves a specific revision's metadata or content
- **update** - Updates revision properties (e.g., keep forever)
- **delete** - Permanently removes a revision

### 5. **Changes** (Change tracking - Phase 3)
- **getStartPageToken** - Gets initial page token for change tracking
- **list** - Lists file system changes
- Supports incremental sync via page tokens

### 6. **Comments** (Collaboration - Phase 3)
- **create** - Creates a comment on a file
- **get** - Retrieves a comment
- **list** - Lists file's comments
- **update** - Updates a comment
- **delete** - Deletes a comment
- **replies.create/get/list/update/delete** - Nested reply operations

### 7. **About** (System info - Phase 1)
- **get** - Retrieves user and system information (storage quota, email, etc.)

### 8. **Additional Resources**

- **Apps** - Lists installed applications
- **Channels** - Manages webhook subscriptions
- **Teamdrives** (Legacy) - Superseded by Drives

## Implementation Phases

### Phase 1: Core File Operations
**Commands:** `gwc-drive create`, `get`, `list`, `update`, `delete`, `copy`, `download`, `export`, `about`

**Features:**
- Create files and folders
- Upload and download files
- List files with filtering (name, mimeType, parents, etc.)
- Get file metadata and download content
- Copy files
- Export Google Workspace docs (Sheets→CSV, Docs→PDF, etc.)
- View storage quota and user info
- Pre-generate file IDs (for batch operations)
- Manage file labels

**Key Parameters:**
- `--name` - File/folder name
- `--parents` - Parent folder IDs
- `--mime-type` - MIME type (application/vnd.google-apps.folder, etc.)
- `--description` - File description
- `--properties` - Custom key-value properties
- `--starred` - Star the file
- `--trashed` - Include trashed files in list

**Query Features:**
- Search by name, type, parent, owner, etc.
- Example: `"name contains 'Report' and trashed = false"`
- Pagination with pageSize and pageToken

### Phase 2: Permissions & Shared Drives
**Commands:** `gwc-drive permissions *`, `drives *`

**Permissions:**
- Share files with users, groups, or domains
- Set permission roles (reader, commenter, writer, organizer, owner)
- Transfer ownership
- Create shareable links
- Revoke access
- Get sharing information

**Shared Drives:**
- Create team shared drives
- Manage shared drive settings
- List and search shared drives
- Hide/unhide shared drives from view
- Delete shared drives (if organizer)

**Key Parameters:**
- `--email` - User/group email
- `--domain` - Domain for domain-wide sharing
- `--role` - Permission level (reader, commenter, writer, organizer, owner)
- `--type` - Permission type (user, group, domain, anyone)
- `--with-link` - Allow access via link sharing
- `--expiration` - Permission expiration time

### Phase 3: Collaboration & Version Control
**Commands:** `gwc-drive revisions *`, `changes *`, `comments *`

**Revisions:**
- View file version history
- Restore previous versions
- Delete old revisions
- Mark versions to keep forever (prevent auto-deletion after 30 days)
- Get revision details (author, timestamp, size)

**Changes:**
- Track file system modifications
- Implement incremental sync
- Monitor what changed since last sync
- Filter changes by file type, user, etc.

**Comments:**
- Read comments on files
- Add comments
- Reply to comments
- Resolve/unresolve comments
- Mention other users
- Assign comments to users

## Output Formats

All commands support:
- `--output unix` - Tab-separated (default, for scripting)
- `--output json` - JSON (for programmatic parsing)
- `--output llm` - Human-readable (recommended for humans)

## Common Use Cases

### File Management
```bash
# Create a folder
gwc-drive create --name "My Folder" --mime-type "application/vnd.google-apps.folder"

# Upload a file
gwc-drive create --name "report.pdf" --file /path/to/report.pdf --parents "folder_id"

# List files in folder
gwc-drive list --query "parents = 'folder_id'" --output llm

# Download file
gwc-drive get file_id --download /path/to/save

# Search files
gwc-drive list --query "name contains 'budget' and trashed = false" --output llm

# Export Google Sheet to CSV
gwc-drive export sheet_id --mime-type "text/csv" --output-file budget.csv
```

### Sharing & Permissions
```bash
# Share file with user
gwc-drive permissions create file_id --email user@example.com --role writer

# Share file with domain
gwc-drive permissions create file_id --domain company.com --role reader

# Create public link
gwc-drive permissions create file_id --type anyone --role reader --with-link

# Revoke access
gwc-drive permissions delete file_id permission_id

# List who has access
gwc-drive permissions list file_id --output llm
```

### Shared Drives
```bash
# Create shared drive
gwc-drive drives create --name "Engineering Team"

# Add team members
gwc-drive permissions create drive_id --email alice@company.com --role fileOrganizer

# List shared drives
gwc-drive drives list --output llm
```

### Version Control
```bash
# View revision history
gwc-drive revisions list file_id --output llm

# Restore previous version
gwc-drive revisions update file_id revision_id --keep-forever

# View specific revision
gwc-drive revisions get file_id revision_id --output json
```

### Collaboration
```bash
# Read comments
gwc-drive comments list file_id --output llm

# Add comment
gwc-drive comments create file_id --body "Please review this section"

# Reply to comment
gwc-drive comments replies create file_id comment_id --body "Approved"

# Resolve comment
gwc-drive comments update file_id comment_id --resolved
```

## API Limits & Considerations

1. **Rate Limits:**
   - 1,000 requests per 100 seconds per user
   - Batch operations more efficient than individual requests

2. **File Size:**
   - Max upload size: 5TB
   - Resumable upload for large files

3. **Query Filtering:**
   - Complex search queries require proper escaping
   - Case-sensitive field names
   - Supports boolean operators (and, or, not)

4. **Change Tracking:**
   - Use `changes.getStartPageToken` to get initial sync token
   - Tracks changes within 24 hours by default
   - Requires pageToken for continuation

5. **Permissions:**
   - Sharing with "anyone" requires `withLink=true` and role restrictions
   - Domain-wide sharing requires domain admin or drive organizer
   - Cannot share with owner's own user account

6. **Storage:**
   - Check quota via `about.get`
   - Different quota for Drive and Shared Drives
   - Trash files don't count towards quota

## MIME Types

Common MIME types for Google Workspace documents:
- `application/vnd.google-apps.document` - Google Docs
- `application/vnd.google-apps.spreadsheet` - Google Sheets
- `application/vnd.google-apps.presentation` - Google Slides
- `application/vnd.google-apps.folder` - Folder
- `application/vnd.google-apps.form` - Google Forms
- `application/vnd.google-apps.site` - Google Sites

Export MIME types for Google Workspace documents:
- Google Docs → PDF, DOCX, ODT, RTFD, TXT, EPUB, ZIP
- Google Sheets → CSV, XLSX, ODS, PDF, TSV, OOXML, ZIP
- Google Slides → PDF, PPTX, ODP, PNG, JPG

## Error Handling

Common error scenarios:
- `403 Forbidden` - No permission to access file
- `404 Not Found` - File doesn't exist
- `400 Bad Request` - Invalid query or parameters
- `429 Too Many Requests` - Rate limit exceeded
- `500 Server Error` - Temporary Drive API issue

## Implementation Strategy

1. **Shared Infrastructure** (reuse from other CLIs):
   - OAuth2 authentication
   - Configuration management
   - Output formatting
   - Error handling

2. **Phase 1 Focus:**
   - File listing and search
   - File metadata operations
   - Download/upload
   - Export functionality
   - User quota information

3. **Phase 2 Extension:**
   - Sharing and permissions
   - Shared drive creation and management
   - Bulk permission operations

4. **Phase 3 Polish:**
   - Change tracking and sync
   - Version history and restoration
   - Comments and collaboration features

## Testing Strategy

- Unit tests for operations.py functions
- Integration tests for CLI command structure
- Mock API responses for offline testing
- Real API testing with test Drive account

## Related Documentation

- **Gmail CLI:** Similar implementation with email-specific operations
- **Calendar CLI:** Event management patterns
- **Shared Infrastructure:** Authentication, output formatting, error handling
