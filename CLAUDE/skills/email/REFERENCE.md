---
name: email-reference
description: Complete Gmail CLI command reference
---

# Gmail CLI - Command Reference

Complete reference for all `gwc-email` commands and options.

## Command Overview

```
gwc-email                  # Main entry point
├── list                   # List messages from a label
├── get                    # Get full message details
├── search                 # Search messages
├── search-help            # Show search examples
├── thread                 # Get messages in thread
└── labels                 # Label management
    ├── list              # List all labels
    ├── get               # Get label details
    └── map               # Show label name→ID mapping
```

---

## Message Commands

### gwc-email list

List messages from a label with optional filtering.

**Syntax:**
```bash
poetry run gwc-email list [OPTIONS]
```

**Options:**

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--label TEXT` | string | `INBOX` | Label to list (e.g., `Important`, `DRAFT`, `SENT_MAIL`) |
| `--limit INTEGER` | int | `10` | Max messages to return (1-100) |
| `--query TEXT` | string | `` | Gmail search query to filter results |
| `--output [unix\|json\|llm]` | enum | `unix` | Output format |
| `--page-token TEXT` | string | `` | Token for pagination (from previous results) |

**Examples:**

```bash
# List 10 inbox messages
poetry run gwc-email list

# List 50 messages in human-readable format
poetry run gwc-email list --limit 50 --output llm

# List important messages
poetry run gwc-email list --label Important --output llm

# List unread inbox messages
poetry run gwc-email list --query "is:unread" --output llm

# Get more results (use token from previous output)
poetry run gwc-email list --page-token "NEXT_TOKEN_HERE"
```

**Output (--output unix):**
```
id              threadId        snippet                 date
msg123          thread456       Hello, how are you      1700000000000
msg124          thread789       Meeting notes           1700000001000
```

**Output (--output json):**
```json
[
  {
    "id": "msg123",
    "threadId": "thread456",
    "snippet": "Hello, how are you doing?",
    "date": "1700000000000"
  }
]
```

**Output (--output llm):**
```
id:    msg123
thread: thread456
snippet: Hello, how are you doing?
date:  1700000000000

id:    msg124
thread: thread789
snippet: Meeting notes for today
date:  1700000001000
```

**Notes:**

- Default label is INBOX
- Use `--label ALL_MAIL` to list all messages
- System labels: `INBOX`, `SENT_MAIL`, `DRAFT`, `SPAM`, `TRASH`, `UNREAD`, `STARRED`
- Page size limited to 100 by API; use `--page-token` for more results
- Combine `--query` with `--label` to search within a label

---

### gwc-email get

Get full message details including headers, body, and attachments.

**Syntax:**
```bash
poetry run gwc-email get MESSAGE_ID [OPTIONS]
```

**Arguments:**

| Argument | Type | Description |
|----------|------|-------------|
| `MESSAGE_ID` | string | Message ID (required) |

**Options:**

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--output [unix\|json\|llm]` | enum | `unix` | Output format |

**Examples:**

```bash
# Get message details
poetry run gwc-email get msg123

# Get as JSON
poetry run gwc-email get msg123 --output json

# Get human-readable
poetry run gwc-email get msg123 --output llm
```

**Output (--output llm):**
```
id:        msg123
threadId:  thread456
from:      alice@example.com
to:        bob@example.com
subject:   Meeting Tomorrow
date:      Wed, 15 Nov 2025 14:30:00 +0000
body:      Sure, let's meet at 2pm tomorrow. Will send calendar invite...
```

**Output (--output json):**
```json
{
  "id": "msg123",
  "threadId": "thread456",
  "from": "alice@example.com",
  "to": "bob@example.com",
  "subject": "Meeting Tomorrow",
  "date": "Wed, 15 Nov 2025 14:30:00 +0000",
  "body": "Sure, let's meet at 2pm tomorrow...",
  "labelIds": ["INBOX"]
}
```

**Notes:**

- Message IDs come from `list` or `search` commands
- Body is truncated to first 500 characters (use API directly for full body)
- Headers (From, To, Subject, Date, Cc, Bcc) are always extracted
- JSON output includes full labelIds array

---

### gwc-email search

Search messages using Gmail's powerful search syntax.

**Syntax:**
```bash
poetry run gwc-email search QUERY [OPTIONS]
```

**Arguments:**

| Argument | Type | Description |
|----------|------|-------------|
| `QUERY` | string | Gmail search query (required) |

**Options:**

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--limit INTEGER` | int | `10` | Max results to return (1-100) |
| `--output [unix\|json\|llm]` | enum | `unix` | Output format |

**Examples:**

```bash
# Search by sender
poetry run gwc-email search "from:alice@example.com"

# Search by subject
poetry run gwc-email search "subject:meeting"

# Search with multiple conditions
poetry run gwc-email search "from:alice@example.com subject:urgent has:attachment"

# Search by date
poetry run gwc-email search "after:2025-01-01"

# Search for unread
poetry run gwc-email search "is:unread" --limit 20
```

**Gmail Search Syntax:**

| Query | Meaning |
|-------|---------|
| `from:alice@example.com` | From specific sender |
| `to:bob@example.com` | To specific recipient |
| `subject:urgent` | Subject contains word |
| `after:2025-01-01` | After date |
| `before:2025-02-01` | Before date |
| `has:attachment` | Has attachments |
| `is:unread` | Unread messages |
| `is:starred` | Starred messages |
| `larger:1M` | Larger than 1 MB |
| `filename:pdf` | Attachment filename contains |
| `label:Important` | In specific label |

**Combinations:**
```bash
# Multiple conditions (AND)
poetry run gwc-email search "from:alice@example.com subject:urgent"

# Date range
poetry run gwc-email search "after:2025-01-01 before:2025-02-01"

# Complex query
poetry run gwc-email search "from:@company.com has:attachment is:unread"
```

**Notes:**

- Search is case-insensitive
- Enclose multi-word queries in quotes
- Use `gwc-email search-help` to see all examples
- Max results: 100 per query
- Gmail search is more powerful than API filtering

---

### gwc-email search-help

Show examples of common Gmail search queries.

**Syntax:**
```bash
poetry run gwc-email search-help
```

**Output:**
```
Common Gmail Search Queries:
  from_email           from:user@example.com
  to_email             to:alice@example.com
  subject              subject:urgent
  has_attachment       has:attachment
  is_unread            is:unread
  before_date          before:2025-01-01
  after_date           after:2025-01-01
  larger_than          larger:1M
  filename             filename:pdf
  in_label             label:Important

Combine multiple queries:
  gwc-email search 'from:alice@example.com subject:urgent has:attachment'
```

**Notes:**

- No options for this command
- Purely informational

---

### gwc-email thread

Get all messages in a conversation thread.

**Syntax:**
```bash
poetry run gwc-email thread THREAD_ID [OPTIONS]
```

**Arguments:**

| Argument | Type | Description |
|----------|------|-------------|
| `THREAD_ID` | string | Thread ID (required) |

**Options:**

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--output [unix\|json\|llm]` | enum | `unix` | Output format |

**Examples:**

```bash
# Get thread messages
poetry run gwc-email thread thread456

# Get as JSON
poetry run gwc-email thread thread456 --output json

# Get human-readable
poetry run gwc-email thread thread456 --output llm
```

**Output (--output llm):**
```
id:    msg123
from:  alice@example.com
subject: Re: Meeting Tomorrow
date:  Wed, 15 Nov 2025 14:30:00 +0000

id:    msg124
from:  bob@example.com
subject: Re: Meeting Tomorrow
date:  Wed, 15 Nov 2025 15:00:00 +0000
```

**Notes:**

- Thread IDs come from `list` or `search` results
- Returns all messages in conversation chronologically
- Use to view full email thread

---

## Label Commands

### gwc-email labels list

List all labels in your account.

**Syntax:**
```bash
poetry run gwc-email labels list [OPTIONS]
```

**Options:**

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--output [unix\|json\|llm]` | enum | `unix` | Output format |

**Examples:**

```bash
# List labels
poetry run gwc-email labels list

# List as JSON
poetry run gwc-email labels list --output json

# List human-readable
poetry run gwc-email labels list --output llm
```

**Output (--output llm):**
```
id:    INBOX
name:  INBOX
type:  system
total: 150
unread: 5

id:    important
name:  Important
type:  user
total: 25
unread: 2
```

**Notes:**

- Includes system labels (INBOX, SENT_MAIL, DRAFT, etc.)
- Also shows user-created labels
- `messagesTotal` is total messages with that label
- `messagesUnread` is unread count

---

### gwc-email labels get

Get details about a specific label.

**Syntax:**
```bash
poetry run gwc-email labels get LABEL_NAME [OPTIONS]
```

**Arguments:**

| Argument | Type | Description |
|----------|------|-------------|
| `LABEL_NAME` | string | Label name (required) |

**Options:**

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--output [unix\|json\|llm]` | enum | `unix` | Output format |

**Examples:**

```bash
# Get label details
poetry run gwc-email labels get "Important"

# Get as JSON
poetry run gwc-email labels get "Important" --output json

# Case sensitive
poetry run gwc-email labels get "INBOX"
```

**Output (--output llm):**
```
id:    important
name:  Important
type:  user
total: 25
unread: 2
visibility: labelShow
```

**Notes:**

- Label names are case-sensitive
- Use exact names from `labels list`
- Returns full label properties including visibility settings

---

### gwc-email labels map

Show mapping of label names to IDs (useful for automation).

**Syntax:**
```bash
poetry run gwc-email labels map [OPTIONS]
```

**Options:**

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--output [unix\|json\|llm]` | enum | `unix` | Output format |

**Examples:**

```bash
# Show label mapping
poetry run gwc-email labels map

# As JSON
poetry run gwc-email labels map --output json
```

**Output (--output unix):**
```
name              id
INBOX             INBOX
DRAFT             DRAFT
SENT_MAIL         SENT_MAIL
SPAM              SPAM
TRASH             TRASH
Important         important_id_123
Personal          personal_id_456
Work              work_id_789
```

**Notes:**

- Sorted alphabetically by name
- IDs are unique identifiers used by Gmail API
- Useful if you're writing scripts that need label IDs

---

## Output Formats

### Unix Format (Default)

Tab-separated output optimized for scripting.

```
id              threadId        snippet                 date
msg123          thread456       Hello, how are you      1700000000000
msg124          thread789       Meeting notes           1700000001000
```

**Advantages:**
- Works with `cut`, `grep`, `awk`, `sort`
- Easy to process in scripts
- Compact output

**Use when:** Piping to other Unix tools or processing in scripts

---

### JSON Format

Structured JSON output for programmatic parsing.

```json
[
  {
    "id": "msg123",
    "threadId": "thread456",
    "snippet": "Hello, how are you doing?",
    "date": "1700000000000"
  }
]
```

**Advantages:**
- Full data available
- Easy to parse with jq
- Works with any programming language

**Use when:** Processing data programmatically or exporting for analysis

---

### LLM Format

Human-readable format optimized for interactive use.

```
id:       msg123
threadId: thread456
snippet:  Hello, how are you doing?
date:     1700000000000

id:       msg124
threadId: thread789
snippet:  Meeting notes for today
date:     1700000001000
```

**Advantages:**
- Easy to read and understand
- Good for exploring data
- Clear field labels

**Use when:** Reading results interactively in terminal

---

## Pagination

Gmail API returns results in pages (max 100 per page).

**Example:**

```bash
# Get first 100
poetry run gwc-email list --limit 100 --output json

# If more exist, use nextPageToken from output
poetry run gwc-email list --limit 100 --page-token "NEXT_TOKEN_HERE"
```

**Notes:**

- Pagination token appears in stderr (error output)
- Look for: `[More results available. Use --page-token ...]`
- Each API call returns fresh data (not cached)

---

## Message Object Fields

**Standard fields in message objects:**

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Message ID (use for `get` command) |
| `threadId` | string | Thread ID (use for `thread` command) |
| `from` | string | Sender email address |
| `to` | string | Primary recipient |
| `cc` | string | CC recipients (if any) |
| `subject` | string | Email subject |
| `date` | string | RFC 2822 date string |
| `internalDate` | string | Unix timestamp in milliseconds |
| `snippet` | string | Preview text (first ~150 chars) |
| `labelIds` | array | List of label IDs applied |
| `body` | string | Message body (truncated to 500 chars) |

---

## Label Names

**System Labels:**

| Name | ID | Purpose |
|------|----|---------|
| `INBOX` | INBOX | Inbox |
| `SENT_MAIL` | SENT_MAIL | Sent messages |
| `DRAFT` | DRAFT | Draft messages |
| `SPAM` | SPAM | Spam folder |
| `TRASH` | TRASH | Deleted messages |
| `UNREAD` | UNREAD | Unread status |
| `STARRED` | STARRED | Starred messages |
| `ALL_MAIL` | ALL_MAIL | All messages |

**User Labels:**

Create custom labels in Gmail interface. Use exact names:
- `Important`
- `Work`
- `Personal`
- etc.

---

## Error Handling

**Common errors:**

| Error | Cause | Solution |
|-------|-------|----------|
| `No valid authentication token found` | Not authenticated | Run `poetry run gwc auth` |
| `Label 'X' not found` | Label doesn't exist | Check exact name with `labels list` |
| `[Errno 1] Error` | Authentication expired | Run `poetry run gwc auth --refresh` |
| `No messages found` | Empty search result | Try different search query |

---

## Best Practices

1. **Use `--output llm` for interactive exploration**
2. **Use `--output json` for scripts and integration**
3. **Combine `--label` and `--query` to narrow searches**
4. **Use `search-help` when unsure of query syntax**
5. **Start with small `--limit` when testing queries**
6. **Cache results to file if processing large sets**

```bash
# Example: Save results for later processing
poetry run gwc-email list --limit 100 --output json > inbox.json
cat inbox.json | jq '.[] | .from' | sort | uniq -c
```

---

**Last Updated:** November 18, 2025
**Phase:** 1 (Core Message Management)
**Status:** Complete and tested
