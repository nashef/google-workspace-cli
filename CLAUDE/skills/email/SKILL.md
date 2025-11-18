---
name: email
description: Gmail management and email operations (Phases 1-3 complete)
---

## Status

✅ **Phase 1**: Message reading, searching, and label management
✅ **Phase 2**: Message composition, drafts, send, reply, forward with attachments
✅ **Phase 3**: Message organization (read/unread, archive, labels) and batch operations

All core email functionality is fully implemented and tested.

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

**Reading & Searching (Phase 1):**
- `list` - List messages from a label
- `get` - Get full message details
- `search` - Search messages using Gmail syntax
- `thread` - Get all messages in a thread

**Composing & Sending (Phase 2):**
- `send` - Send message directly (no draft)
- `draft create` - Create draft message (unsent)
- `draft list` - List all drafts
- `draft get` - Get draft details
- `draft send` - Send existing draft
- `draft delete` - Delete draft
- `reply` - Reply to a message
- `forward` - Forward message to recipient

**Labels & Organization (Phase 1):**
- `labels list` - List all labels
- `labels get` - Get label details
- `labels map` - Show name→ID mapping

**Message Organization & Batch Operations (Phase 3):**
- `create-label` - Create new label
- `add-label` - Add label to message
- `remove-label` - Remove label from message
- `mark-read` - Mark message as read
- `mark-unread` - Mark message as unread
- `archive` - Archive message (remove from INBOX)
- `unarchive` - Restore message to INBOX
- `spam` - Mark message as spam
- `delete` - Permanently delete message
- `batch-add-label` - Add label to multiple messages
- `batch-remove-label` - Remove label from multiple messages
- `batch-mark-read` - Mark multiple messages as read
- `batch-mark-unread` - Mark multiple messages as unread
- `batch-archive` - Archive multiple messages
- `batch-delete` - Permanently delete multiple messages

**Help & Reference:**
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

### Send a Simple Email
```bash
# Send directly
poetry run gwc-email send --to alice@example.com --subject "Hello" --body "Hi there!"
```

### Create and Send Draft
```bash
# Create draft
poetry run gwc-email draft create --to alice@example.com --subject "Meeting" --body "Can we meet tomorrow?"

# List drafts
poetry run gwc-email draft list --output llm

# Send the draft
poetry run gwc-email draft send draft_id_here
```

### Send with Attachments
```bash
# Single attachment
poetry run gwc-email send --to alice@example.com --subject "Report" --body "See attached" \
  --attachments /path/to/report.pdf

# Multiple attachments
poetry run gwc-email send --to alice@example.com --subject "Files" --body "Here are the files" \
  --attachments /path/to/file1.pdf --attachments /path/to/file2.xlsx
```

### Send with CC and BCC
```bash
# CC someone
poetry run gwc-email send --to alice@example.com --cc bob@example.com \
  --subject "Update" --body "Copying Bob on this"

# Add BCC
poetry run gwc-email send --to alice@example.com --bcc manager@example.com \
  --subject "Report" --body "For your records"
```

### Reply to Message
```bash
# Reply to sender only
poetry run gwc-email reply msg123 --body "Thanks for your message!"

# Reply to all (including CC)
poetry run gwc-email reply msg123 --reply-all --body "Everyone, please see my response below"
```

### Forward Message
```bash
# Forward to someone
poetry run gwc-email forward msg123 --to alice@example.com

# Forward with additional text
poetry run gwc-email forward msg123 --to alice@example.com --body "This is important, thought you should see it"

# Forward with custom subject
poetry run gwc-email forward msg123 --to alice@example.com --subject "FYI: Project Update"
```

## Message Organization (Phase 3)

### Create and Manage Labels
```bash
# Create a new label
poetry run gwc-email create-label "Project X"

# Create hidden label
poetry run gwc-email create-label "To Review" --visibility hide

# Add label to message
poetry run gwc-email add-label msg123 "Project X"

# Remove label from message
poetry run gwc-email remove-label msg123 "Project X"
```

### Mark Messages as Read/Unread
```bash
# Mark single message as read
poetry run gwc-email mark-read msg123

# Mark single message as unread
poetry run gwc-email mark-unread msg123

# Mark multiple messages as read
poetry run gwc-email batch-mark-read msg1 msg2 msg3

# Mark multiple messages as unread
poetry run gwc-email batch-mark-unread msg1 msg2 msg3
```

### Archive and Delete Messages
```bash
# Archive a message (remove from INBOX)
poetry run gwc-email archive msg123

# Restore archived message to INBOX
poetry run gwc-email unarchive msg123

# Mark message as spam
poetry run gwc-email spam msg123

# Permanently delete a message
poetry run gwc-email delete msg123 --confirm

# Archive multiple messages
poetry run gwc-email batch-archive msg1 msg2 msg3

# Permanently delete multiple messages
poetry run gwc-email batch-delete msg1 msg2 msg3 --confirm
```

### Batch Label Operations
```bash
# Add label to multiple messages
poetry run gwc-email batch-add-label msg1 msg2 msg3 "Project X"

# Remove label from multiple messages
poetry run gwc-email batch-remove-label msg1 msg2 msg3 "Project X"
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
