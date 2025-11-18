---
name: email
description: Gmail management and email operations
---

# Gmail CLI Quick Reference

Base command: `poetry run gwc-email <command>`

## Quick Start

```bash
# See inbox
poetry run gwc-email list --output llm

# Search
poetry run gwc-email search "from:alice@example.com"

# Get message details
poetry run gwc-email get msg_id --output json

# List labels
poetry run gwc-email labels list --output llm
```

## Output Formats

- `--output unix` - Tab-separated (default, scripting)
- `--output json` - JSON (programmatic parsing)
- `--output llm` - Human-readable (recommended)

## Finding Messages

| Task | Command |
|------|---------|
| By sender | `search "from:alice@example.com"` |
| By subject | `search "subject:meeting"` |
| Unread | `search "is:unread" --limit 20` |
| With attachments | `search "has:attachment"` |
| Date range | `search "after:2025-01-01 before:2025-02-01"` |
| Large files | `search "larger:1M"` |
| Specific filename | `search "filename:pdf"` |

## Message Operations

| Task | Command |
|------|---------|
| List (10 default) | `list --output llm` |
| Get more results | `list --limit 50` |
| From label | `list --label Important` |
| Label + search | `list --label Important --query "from:alice@example.com"` |
| Get details | `get msg_id --output llm` |
| Thread | `thread thread_id --output llm` |

## Composition

| Task | Command |
|------|---------|
| Send directly | `send --to alice@example.com --subject "..." --body "..."` |
| With attachments | `send ... --attachments /path/to/file` |
| With CC/BCC | `send ... --cc bob@example.com --bcc mgr@example.com` |
| Draft | `draft create --to alice@example.com --subject "..." --body "..."` |
| Send draft | `draft send draft_id` |
| List drafts | `draft list --output llm` |
| Reply | `reply msg_id --body "response"` |
| Reply-all | `reply msg_id --reply-all --body "..."` |
| Forward | `forward msg_id --to alice@example.com` |

## Organization

| Task | Command |
|------|---------|
| Create label | `create-label "Project X"` |
| List labels | `labels list --output llm` |
| Get label | `labels get "Important"` |
| Label mapping | `labels map` |
| Add label | `add-label msg_id "Label"` |
| Remove label | `remove-label msg_id "Label"` |
| Mark read | `mark-read msg_id` |
| Mark unread | `mark-unread msg_id` |
| Archive | `archive msg_id` |
| Unarchive | `unarchive msg_id` |
| Spam | `spam msg_id` |
| Delete | `delete msg_id --confirm` |

## Batch Operations

| Task | Command |
|------|---------|
| Add label | `batch-add-label msg1 msg2 msg3 "Label"` |
| Remove label | `batch-remove-label msg1 msg2 msg3 "Label"` |
| Mark read | `batch-mark-read msg1 msg2 msg3` |
| Mark unread | `batch-mark-unread msg1 msg2 msg3` |
| Archive | `batch-archive msg1 msg2 msg3` |
| Delete | `batch-delete msg1 msg2 msg3 --confirm` |

## Advanced Features

For Phase 4 features (filters, signatures, auto-responders, templates), see **ADVANCED.md**

- `filters create/list/get/delete`
- `signatures list/get/update`
- `auto-responder create/get/disable`
- `templates create/list/get/delete/use`

## Common Options

- `--limit INTEGER` - Results limit (1-100)
- `--output [unix|json|llm]` - Output format
- `--query SEARCH` - Gmail search syntax
- `--help` - Command help

## Search Syntax

Combine any of: `from:`, `to:`, `subject:`, `is:unread`, `is:read`, `has:attachment`, `before:`, `after:`, `larger:`, `filename:`, etc.

Example: `search "from:alice@example.com subject:urgent has:attachment is:unread"`

## Help

Get detailed help for any command:
```bash
poetry run gwc-email <command> --help
```

## Tips

1. Use `--output llm` for reading by humans
2. Gmail search is powerful - combine multiple conditions
3. Use email addresses, not names, for reliable matching
4. Use `jq` to parse JSON: `list --output json | jq '.[].from'`
5. Batch operations more efficient than single operations
6. `batch-delete` and `delete` require `--confirm` flag

## Common Workflows

**Morning review:** `list --label Important --query "is:unread" --output llm`

**Find email:** `search "from:alice@example.com" --output llm`

**Export messages:** `search "subject:ProjectX" --output json > project_emails.json`

**Archive old:** `search "before:2020-01-01" --output unix | wc -l`

**See drafts:** `list --label DRAFT --output llm`

**Send simple:** `send --to alice@example.com --subject "Hello" --body "Hi there!"`

## Documentation

- **REFERENCE.md** - Complete command reference, field descriptions, pagination
- **ADVANCED.md** - Phase 4 features (filters, signatures, auto-responders, templates)
