---
name: email-index
description: Navigation guide for Gmail CLI documentation
---

# Gmail CLI - Complete Documentation Index

This directory contains comprehensive documentation for `gwc-email`, the Gmail API CLI tool. Choose the right guide for your needs:

## Quick Navigation

### I Want to...

**Get started immediately** → Read **[QUICK_START.md](QUICK_START.md)**
- Fast 5-minute setup
- Your first commands
- Essential tips

**Find how to do something** → Check **[SKILL.md](SKILL.md)**
- Common tasks with examples
- Quick command reference
- Real-world workflows

**Look up a specific command** → See **[REFERENCE.md](REFERENCE.md)**
- Complete command reference
- All options and parameters
- Output format details
- Field descriptions

**Understand the full project** → See **[../../README_GMAIL.md](../../README_GMAIL.md)**
- Feature overview
- Installation and setup
- Implementation phases
- API limits and quirks
- Troubleshooting guide

## Documentation Structure

```
email/
├── INDEX.md (this file)
│   └─ Navigation guide
├── QUICK_START.md
│   └─ 5-minute intro
├── SKILL.md
│   └─ Common tasks and examples
├── REFERENCE.md
│   └─ Complete command reference
└─ supporting files:
    └── ../../README_GMAIL.md
        └─ Complete implementation plan
```

## Common Tasks by Use Case

### Daily Usage

**See inbox:**
```bash
poetry run gwc-email list --output llm
```

**Search for something:**
```bash
poetry run gwc-email search "from:alice@example.com"
```

**Get full message:**
```bash
poetry run gwc-email get msg_id --output llm
```

See **[SKILL.md - Finding Messages](SKILL.md#finding-messages)**

### Email Discovery

**Find by sender:**
```bash
poetry run gwc-email search "from:alice@example.com" --output llm
```

**Find by subject:**
```bash
poetry run gwc-email search "subject:meeting" --output llm
```

**Find unread:**
```bash
poetry run gwc-email search "is:unread" --limit 20 --output llm
```

**Find with attachments:**
```bash
poetry run gwc-email search "has:attachment" --output llm
```

See **[REFERENCE.md - Search Syntax](REFERENCE.md#gmail-search-syntax)**

### Organization & Labels

**List labels:**
```bash
poetry run gwc-email labels list --output llm
```

**See important messages:**
```bash
poetry run gwc-email list --label Important --output llm
```

**Get label details:**
```bash
poetry run gwc-email labels get "Important" --output llm
```

See **[SKILL.md - Working with Labels](SKILL.md#working-with-labels)**

### Archive & Cleanup

**Find old messages:**
```bash
poetry run gwc-email search "before:2024-01-01" --output llm
```

**Find by date range:**
```bash
poetry run gwc-email search "after:2025-01-01 before:2025-02-01" --output llm
```

**Find large messages:**
```bash
poetry run gwc-email search "larger:1M" --output llm
```

See **[SKILL.md - Common Workflows](SKILL.md#common-workflows)**

## Command Categories

### Core Message Operations

| Command | Purpose | Doc Link |
|---------|---------|----------|
| `list` | List messages from label | [REFERENCE](REFERENCE.md#gwc-email-list) |
| `get` | Get message details | [REFERENCE](REFERENCE.md#gwc-email-get) |
| `search` | Search messages | [REFERENCE](REFERENCE.md#gwc-email-search) |
| `thread` | Get thread messages | [REFERENCE](REFERENCE.md#gwc-email-thread) |

See **[SKILL.md - All Available Commands](SKILL.md#all-available-commands)**

### Label Management

| Command | Purpose | Doc Link |
|---------|---------|----------|
| `labels list` | List all labels | [REFERENCE](REFERENCE.md#gwc-email-labels-list) |
| `labels get` | Get label details | [REFERENCE](REFERENCE.md#gwc-email-labels-get) |
| `labels map` | Show name→ID mapping | [REFERENCE](REFERENCE.md#gwc-email-labels-map) |

See **[SKILL.md - Working with Labels](SKILL.md#working-with-labels)**

### Help & Reference

| Command | Purpose | Doc Link |
|---------|---------|----------|
| `search-help` | Show search examples | [REFERENCE](REFERENCE.md#gwc-email-search-help) |
| `<command> --help` | Command help | [QUICK_START](QUICK_START.md#keyboard-shortcuts--pro-tips) |

## Feature Highlights

### Phase 1 Features (Complete)

✨ **Core Message Reading:**
- List messages with pagination
- Search with full Gmail syntax
- Get full message details
- Thread conversation viewing

✨ **Label Management:**
- List all labels
- View label details
- Label name→ID mapping

✨ **Flexible Output:**
- Unix (tab-separated) format
- JSON for programmatic use
- LLM format for humans

✨ **Search Capabilities:**
- Search by sender/recipient
- Search by subject
- Date-based queries
- Attachment detection
- Large message filtering
- Unread/starred filtering
- Custom label filtering

## Output Formats

Choose the right format for your use:

### Unix Format (Default)
```bash
poetry run gwc-email list
```
- Tab-separated
- Easy to pipe to other tools
- Good for scripting

### JSON Format
```bash
poetry run gwc-email list --output json
```
- Full structured data
- Parse with jq
- Programmatic access

### LLM Format
```bash
poetry run gwc-email list --output llm
```
- Human-readable
- Clear field labels
- Best for interactive exploration

See **[REFERENCE.md - Output Formats](REFERENCE.md#output-formats)**

## Getting Help

### For Command Help

```bash
# Get help for specific command
poetry run gwc-email <command> --help

# Examples:
poetry run gwc-email search --help
poetry run gwc-email labels --help
```

### For This Documentation

1. **Quick question?** → [QUICK_START.md](QUICK_START.md)
2. **How do I do X?** → [SKILL.md](SKILL.md)
3. **Need exact syntax?** → [REFERENCE.md](REFERENCE.md)
4. **Understanding API?** → [../../README_GMAIL.md](../../README_GMAIL.md)

## Key Concepts

### Message ID

Unique identifier for each email. Examples:
- Format: `msg123abc...`
- Use for: `gwc-email get <message_id>`
- Get from: `list` or `search` results

### Thread ID

Unique identifier for a conversation. Examples:
- Format: `thread456xyz...`
- Use for: `gwc-email thread <thread_id>`
- Get from: `list` or `search` results

### Labels

Gmail's organization system:
- **System labels**: INBOX, SENT_MAIL, DRAFT, SPAM, TRASH
- **User labels**: Custom labels created in Gmail
- **Label ID**: Internal identifier (e.g., `important_123`)
- **Label name**: Human-readable name (e.g., `Important`)

### Search Syntax

Gmail's powerful search language:
- `from:email` - By sender
- `to:email` - By recipient
- `subject:text` - By subject
- `after:date` - After date
- `before:date` - Before date
- `has:attachment` - Has files
- `is:unread` - Unread status
- `larger:size` - File size filtering

See **[REFERENCE.md - Gmail Search Syntax](REFERENCE.md#gmail-search-syntax)**

## Tips for Success

1. **Use `--output llm` for interactive use** - Most readable format
2. **Use `--output json` for scripts** - Full data available
3. **Combine label and search** - Filter by label + search query
4. **Use search-help when unsure** - Shows all search options
5. **Save JSON results** - Export for later analysis
6. **Start with small limits** - Test before running large queries

See **[SKILL.md - Tips & Tricks](SKILL.md#tips--tricks)**

## Common Patterns

### Find and Inspect
```bash
# Find messages
poetry run gwc-email search "from:alice@example.com" --output json

# Get message ID
poetry run gwc-email search "from:alice@example.com" --output json | jq '.[0].id'

# Get full details
poetry run gwc-email search "from:alice@example.com" --output json | \
  jq -r '.[0].id' | \
  xargs -I {} poetry run gwc-email get {}
```

### Export for Analysis
```bash
# Export all messages
poetry run gwc-email list --limit 100 --output json > all_inbox.json

# Analyze
cat all_inbox.json | jq 'length'  # Count
cat all_inbox.json | jq '.[].from' | sort | uniq  # Unique senders
```

### Date-Based Organization
```bash
# This month
poetry run gwc-email search "after:2025-11-01" --output llm

# Last 7 days
poetry run gwc-email search "after:2025-11-11" --output llm

# Specific range
poetry run gwc-email search "after:2025-01-01 before:2025-02-01" --output llm
```

## Integration

### With Calendar
```bash
# Get contact email for calendar event
poetry run gwc-email search "from:alice@example.com" --output json | jq -r '.[0].from'
```

### With Spreadsheets
```bash
# Export emails for analysis (then import to Google Sheets)
poetry run gwc-email list --limit 100 --output json > emails.json
```

### With Shell Scripts
```bash
# Extract emails for a group
poetry run gwc-email search "from:@company.com" --output json | \
  jq -r '.[].from' > company_emails.txt
```

See **[SKILL.md - Integration Examples](SKILL.md#integration-examples)**

## What's Included

**✓ Complete** - All Phase 1 features (message reading, searching, labels)
**✓ Tested** - 32+ tests passing
**✓ Documented** - Comprehensive guides and examples
**✓ Composable** - Works with Unix pipes and jq
**✓ Production-Ready** - Error handling and validation

**Coming Later (Phases 2-5):**
- Message composition and sending
- Draft management
- Label modification
- Message deletion
- Filters and rules
- Integration helpers

## Contributing & Feedback

For issues, improvements, or questions:
- Check existing documentation
- Review example commands
- Try `<command> --help` for quick help
- Consult README_GMAIL.md for setup issues

---

**Last Updated:** November 18, 2025
**Phase:** 1 (Core Message Management)
**Status:** Complete and tested
**Version:** 1.0.0
