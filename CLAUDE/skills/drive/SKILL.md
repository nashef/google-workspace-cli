---
name: drive
description: Google Drive file and folder management
---

# Drive CLI Quick Reference

Base command: `poetry run gwc-drive <command>`

## Quick Start

```bash
# List your files
poetry run gwc-drive list --output llm

# Create a folder
poetry run gwc-drive create --name "My Folder" --mime-type folder

# Get file details
poetry run gwc-drive get file_id --output json

# Check storage quota
poetry run gwc-drive quota --output llm
```

## File Operations

| Task | Command |
|------|---------|
| List files | `list --output llm` |
| Search files | `list --query "name contains 'budget'" --output llm` |
| Get more results | `list --limit 50 --output json` |
| Get file details | `get file_id --output llm` |
| Create file | `create --name "Document" --mime-type docs` |
| Create folder | `create --name "Folder" --mime-type folder` |
| Upload file | `create --name "file.pdf" --file /path/to/file.pdf` |
| Update file | `update file_id --name "New Name"` |
| Copy file | `copy file_id --name "Copy of Document"` |
| Delete file | `delete file_id` |
| Move to trash | `trash file_id` |
| Restore from trash | `untrash file_id` |
| Empty trash | `empty-trash` |

## Export & Download

| Task | Command |
|------|---------|
| Export to PDF | `export file_id --mime-type application/pdf --output-file report.pdf` |
| Export to CSV | `export sheet_id --mime-type text/csv --output-file data.csv` |
| Export to DOCX | `export doc_id --mime-type application/vnd.openxmlformats-officedocument.wordprocessingml.document --output-file doc.docx` |
| Download file | `download file_id --output-file /path/to/save` |
| View export formats | `export-formats` |

## Labels

| Task | Command |
|------|---------|
| List file labels | `labels file_id --output llm` |
| Add label | `modify-labels file_id --add label_id` |
| Remove label | `modify-labels file_id --remove label_id` |
| Add multiple | `modify-labels file_id --add id1 --add id2` |

## Permissions (Phase 2)

| Task | Command |
|------|---------|
| Share with user | `create-permission file_id --email user@example.com --role reader` |
| Share with group | `create-permission file_id --email group@example.com --type group --role editor` |
| Share with domain | `create-permission file_id --email example.com --type domain --role reader` |
| Get permission details | `get-permission file_id permission_id --output llm` |
| List all permissions | `list-permissions file_id --output llm` |
| Change role | `update-permission file_id permission_id --role editor` |
| Revoke access | `delete-permission file_id permission_id` |
| Transfer ownership | `create-permission file_id --email user@example.com --role owner --transfer-ownership` |

## Shared Drives (Phase 2)

| Task | Command |
|------|---------|
| Create drive | `create-drive --name "Team Drive"` |
| Get drive info | `get-drive drive_id --output llm` |
| List drives | `list-drives --output llm` |
| List more drives | `list-drives --limit 50 --output json` |
| Rename drive | `update-drive drive_id --name "New Name"` |
| Hide drive | `hide-drive drive_id` |
| Show hidden drive | `unhide-drive drive_id` |
| Delete drive | `delete-drive drive_id` |

## Revisions (Phase 3)

| Task | Command |
|------|---------|
| View revision history | `list-revisions file_id --output llm` |
| See more versions | `list-revisions file_id --limit 50 --output json` |
| Get revision details | `get-revision file_id revision_id --output llm` |
| Mark to keep forever | `keep-revision file_id revision_id` |
| Delete old revision | `delete-revision file_id revision_id` |
| Restore from version | `restore-revision file_id revision_id` |

## Change Tracking (Phase 3)

| Task | Command |
|------|---------|
| Get sync starting point | `get-start-page-token` |
| Check what changed | `list-changes PAGE_TOKEN --output llm` |
| Track more changes | `list-changes PAGE_TOKEN --limit 500 --output json` |

## Comments & Collaboration (Phase 3)

| Task | Command |
|------|---------|
| Add comment | `create-comment file_id --content "Great work!"` |
| View all comments | `list-comments file_id --output llm` |
| Get comment details | `get-comment file_id comment_id --output llm` |
| Update comment | `update-comment file_id comment_id --content "Updated"` |
| Mark comment resolved | `update-comment file_id comment_id --resolved true` |
| Reply to comment | `create-reply file_id comment_id --content "I agree!"` |
| See replies | `list-replies file_id comment_id --output llm` |
| Delete comment | `delete-comment file_id comment_id` |

## User Information

| Task | Command |
|------|---------|
| Storage quota | `quota --output llm` |
| Account info | `about --output llm` |
| MIME type list | `mime-types` |

## Common Options

- `--output [unix|json|llm]` - Output format
- `--limit INTEGER` - Results limit (1-1000, default 10)
- `--query TEXT` - Drive API query (see below)
- `--mime-type TEXT` - MIME type for file creation
- `--name TEXT` - File/folder name
- `--description TEXT` - File description
- `--starred` - Star the file
- `--parents ID` - Parent folder IDs (can repeat)

## Query Syntax

Use Drive API query syntax with `list --query`:

```bash
# By name
gwc-drive list --query "name contains 'report'"

# Exact match
gwc-drive list --query "name = 'document.pdf'"

# By type
gwc-drive list --query "mimeType = 'application/vnd.google-apps.folder'"

# Multiple conditions
gwc-drive list --query "name contains 'budget' and trashed = false"

# By owner
gwc-drive list --query "owners any in ('user@example.com')"
```

## MIME Types

**Google Workspace:**
- `docs` → Google Docs
- `sheets` → Google Sheets
- `slides` → Google Slides
- `folder` → Folder
- `forms` → Google Forms

**Files:** Use regular MIME types (application/pdf, text/csv, etc.)

View shortcuts: `gwc-drive mime-types`

## Export Formats

See available formats for each document type:
```bash
gwc-drive export-formats
```

Examples:
- Docs → PDF, DOCX, ODT, RTFD, TXT, EPUB, ZIP
- Sheets → CSV, XLSX, ODS, PDF, TSV, ZIP
- Slides → PDF, PPTX, ODP, PNG, JPG, SVG, ZIP

## Tips

1. Use `--output llm` for human-readable output
2. Combine `--query` with `list` for powerful searching
3. Export before deleting important files
4. Use `--limit 50` to get more results at once
5. Query syntax: logical operators (and, or, not) work as expected
6. Check quota before uploading large files

## Common Workflows

**Find old budget files:**
```bash
gwc-drive list --query "name contains 'budget' and trashed = false" --output llm
```

**Backup file:**
```bash
gwc-drive export file_id --mime-type application/pdf --output-file backup.pdf
```

**Clean up trash:**
```bash
gwc-drive list --query "trashed = true" --output llm
gwc-drive empty-trash
```

**Find all spreadsheets:**
```bash
gwc-drive list --query "mimeType = 'application/vnd.google-apps.spreadsheet'" --output llm
```

**Copy file to folder:**
```bash
gwc-drive copy original_id --name "Copy" --parents folder_id
```

## Documentation

- **REFERENCE.md** - Complete command reference and field descriptions
- **ADVANCED.md** - Phase 2-3 features (permissions, shared drives, revisions, comments)
