---
name: email
description: Gmail management and email operations
---

## Quick Start

All commands run from `~/Jarvis/sagas/src/google-workspace-cli` using `poetry run gwc-email <command>`.

### Most Common Tasks

**See your inbox:**
```bash
poetry run gwc-email list --output llm
```

**Search for something:**
```bash
poetry run gwc-email search "from:alice@example.com"
```

**Get full message details:**
```bash
poetry run gwc-email get msg_id --output json
```

**See all your labels:**
```bash
poetry run gwc-email labels list --output llm
```

## Output Formats

- `--output unix` - Tab-separated (default, for scripting)
- `--output json` - JSON (for programmatic parsing)
- `--output llm` - Human-readable (use this most of the time!)

## Common Tasks

### Finding Messages

**Find by sender (email address):**
```bash
poetry run gwc-email search "from:alice@example.com" --output llm
```

**Find by subject:**
```bash
poetry run gwc-email search "subject:meeting" --output llm
```

**Find unread messages:**
```bash
poetry run gwc-email search "is:unread" --limit 20 --output llm
```

**Find messages with attachments:**
```bash
poetry run gwc-email search "has:attachment" --output llm
```

**Find messages in date range:**
```bash
poetry run gwc-email search "after:2025-01-01 before:2025-02-01" --output llm
```

**Find large messages:**
```bash
poetry run gwc-email search "larger:1M" --output llm
```

**Find messages with specific filename:**
```bash
poetry run gwc-email search "filename:pdf" --output llm
```

### Listing Messages

**See first 10 messages (default):**
```bash
poetry run gwc-email list --output llm
```

**Get more messages:**
```bash
poetry run gwc-email list --limit 50 --output llm
```

**List from specific label:**
```bash
poetry run gwc-email list --label Important --output llm
```

**Combine label and search:**
```bash
poetry run gwc-email list --label Important --query "from:alice@example.com" --output llm
```

### Viewing Message Details

**Get full message as JSON:**
```bash
poetry run gwc-email get msg_id --output json
```

**Get message as human-readable:**
```bash
poetry run gwc-email get msg_id --output llm
```

### Working with Labels

**List all labels:**
```bash
poetry run gwc-email labels list --output llm
```

**Get label details:**
```bash
poetry run gwc-email labels get "Important" --output llm
```

**See label name→ID mapping:**
```bash
poetry run gwc-email labels map
```

(Useful if you need label IDs for automation)

### Working with Threads

**Get all messages in a conversation:**
```bash
poetry run gwc-email thread thread_id --output llm
```

(Thread ID comes from list/search results)

## Common Options

Most commands support:
- `--limit INTEGER` - Number of results (1-100)
- `--output [unix|json|llm]` - Output format
- `--query SEARCH` - Gmail search query

## Help

Get detailed help for any command:
```bash
poetry run gwc-email <command> --help
```

Examples:
```bash
poetry run gwc-email search --help
poetry run gwc-email list --help
poetry run gwc-email labels --help
```

## All Available Commands

**Core Operations:**
- `list` - List messages from a label
- `get` - Get full message details
- `search` - Search messages using Gmail syntax
- `thread` - Get all messages in a thread

**Labels:**
- `labels list` - List all labels
- `labels get` - Get label details
- `labels map` - Show name→ID mapping

**Help:**
- `search-help` - Show search query examples

## Common Workflows

### Morning Email Review
```bash
# Check unread in important folder
poetry run gwc-email list --label Important --query "is:unread" --output llm
```

### Find Email from Someone
```bash
# Search by sender
poetry run gwc-email search "from:alice@example.com" --output llm

# Get first result details
poetry run gwc-email search "from:alice@example.com" --output json | jq '.[0].id'
```

### Track Project Communications
```bash
# Find all messages about ProjectX
poetry run gwc-email search "subject:ProjectX" --limit 50 --output json

# Export to file for analysis
poetry run gwc-email search "subject:ProjectX" --output json > project_emails.json
```

### Find Old Messages
```bash
# Messages from last year
poetry run gwc-email search "before:2024-01-01" --output llm

# Messages from specific period
poetry run gwc-email search "after:2024-06-01 before:2024-12-31" --output llm
```

### Organize by Label
```bash
# See important messages
poetry run gwc-email list --label Important --output llm

# See starred messages
poetry run gwc-email list --label Starred --output llm

# See drafts
poetry run gwc-email list --label DRAFT --output llm
```

## Tips & Tricks

**1. Use `--output llm` for reading:**
```bash
poetry run gwc-email search "urgent" --output llm
```

**2. Gmail search is powerful:**
```bash
# Combine multiple conditions
poetry run gwc-email search "from:alice@example.com subject:urgent has:attachment is:unread"
```

**3. Use email for exact matches:**
```bash
# More reliable than name
poetry run gwc-email search "from:alice@example.com"
```

**4. Get JSON for programmatic use:**
```bash
# Parse with jq
poetry run gwc-email list --output json | jq '.[].from'
```

**5. Use limits wisely:**
```bash
# Gmail API paginates at 100, so requesting 100 is efficient
poetry run gwc-email list --limit 100 --output json > all_inbox.json
```

**6. Save searches for later:**
```bash
# Export search results
poetry run gwc-email search "from:@company.com" --output json > company_emails.json

# Analyze later
cat company_emails.json | jq 'length'
```

**7. Chain with Unix tools:**
```bash
# Count messages from a domain
poetry run gwc-email search "from:@company.com" --output unix | wc -l

# Get just the IDs
poetry run gwc-email list --output json | jq -r '.[].id'
```

**8. Combine labels and search:**
```bash
# Search within a label
poetry run gwc-email list --label Important --query "from:alice@example.com" --output llm
```

**9. Archive analysis:**
```bash
# See how many old messages you have
poetry run gwc-email search "before:2020-01-01" --output unix | wc -l
```

**10. Date-based organization:**
```bash
# Messages from this month
poetry run gwc-email search "after:2025-11-01" --output json

# Messages from last 7 days
poetry run gwc-email search "after:2025-11-11" --output json
```

## For Complex Tasks

See **REFERENCE.md** in this directory for:
- Complete option reference for all commands
- Field descriptions in message objects
- Search query syntax details
- Message pagination
- Thread operations

## Integration Examples

### With Calendar
```bash
# Get email addresses from message senders for calendar event
poetry run gwc-email search "from:alice@example.com" --output json | jq -r '.[0].from'
```

### With Spreadsheets
```bash
# Export emails for analysis
poetry run gwc-email list --limit 100 --output json > emails.json
# Then import into Google Sheets via manual process
```

### With Shell Scripts
```bash
# Save sender list
poetry run gwc-email search "from:@company.com" --output json | \
  jq -r '.[].from' > senders.txt
```
