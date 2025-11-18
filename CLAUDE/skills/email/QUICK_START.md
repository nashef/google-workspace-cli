---
name: email-quick-start
description: Get started with Gmail CLI in 5 minutes
---

# Gmail CLI - Quick Start (5 Minutes)

Get up and running with `gwc-email` in just a few minutes.

## Installation & Authentication

### 1. Navigate to the project directory

```bash
cd ~/Jarvis/sagas/src/google-workspace-cli
```

### 2. Install dependencies (if not already done)

```bash
poetry install
```

### 3. Authenticate with Google

```bash
poetry run gwc auth
```

This will:
- Open your browser to Google's sign-in page
- Ask you to approve access to your Gmail
- Save your credentials for future use

**Done!** You're authenticated and ready to use `gwc-email`.

## Your First Commands (2 Minutes)

### See your inbox

```bash
poetry run gwc-email list --output llm
```

Output will look like:
```
id          thread...     snippet                    date
msg123      thread456     Hello, how are you doing?  1700000000000
msg124      thread789     Meeting notes for today    1700000001000
```

### Search for something

```bash
poetry run gwc-email search "from:alice@example.com" --output llm
```

### Get full details about a message

```bash
poetry run gwc-email get msg123 --output llm
```

### See all your labels

```bash
poetry run gwc-email labels list --output llm
```

### Get messages from a specific label

```bash
poetry run gwc-email list --label Important --output llm
```

### Get help with search queries

```bash
poetry run gwc-email search-help
```

Shows:
```
Common Gmail Search Queries:
  from_email           from:user@example.com
  to_email             to:alice@example.com
  subject              subject:urgent
  has_attachment       has:attachment
  is_unread            is:unread
```

## Three Essential Tips

### Tip 1: Use `--output llm` for readability

The default output is tab-separated (good for scripting). Use `--output llm` to see nice, readable output:

```bash
# Hard to read
poetry run gwc-email list

# Easy to read
poetry run gwc-email list --output llm
```

### Tip 2: Search with Gmail syntax

Gmail has powerful built-in search. Combine queries:

```bash
# Multiple conditions
poetry run gwc-email search "from:alice@example.com subject:urgent has:attachment"

# Date ranges
poetry run gwc-email search "after:2025-01-01 before:2025-02-01"

# Unread messages from a domain
poetry run gwc-email search "is:unread from:@company.com"
```

### Tip 3: Use email for exact matches

Search returns the first matching result. Use email to narrow down:

```bash
# Might return multiple matches
poetry run gwc-email search "Alice"

# More precise
poetry run gwc-email search "from:alice@example.com"
```

## Common Workflows

### I want to find an email from someone

```bash
poetry run gwc-email search "from:alice@example.com"
```

### I want to see unread messages

```bash
poetry run gwc-email search "is:unread" --output llm
```

### I want to find messages with attachments

```bash
poetry run gwc-email search "has:attachment" --limit 20 --output llm
```

### I want to see my important messages

```bash
poetry run gwc-email list --label Important --output llm
```

### I want to find old messages

```bash
poetry run gwc-email search "before:2024-01-01" --output llm
```

### I want to get all messages from a project

```bash
poetry run gwc-email search "subject:ProjectX" --output json
```

## Next Steps

Now you know the basics! Here's what to explore:

1. **Learn more commands** - See [SKILL.md](SKILL.md) for common tasks
2. **Look up syntax** - Check [REFERENCE.md](REFERENCE.md) for complete reference
3. **Understand features** - Read [INDEX.md](INDEX.md) for navigation
4. **Get help** - Run `gwc-email <command> --help`

## Keyboard Shortcuts & Pro Tips

### Get command help quickly

Instead of searching docs, just add `--help`:

```bash
poetry run gwc-email search --help
poetry run gwc-email labels --help
```

### Use output formats for different needs

```bash
# For humans (most readable)
poetry run gwc-email list --output llm

# For programs/scripts
poetry run gwc-email list --output json

# For Unix tools
poetry run gwc-email list --output unix
```

### Chain commands together

Get message IDs from search, then get full details:

```bash
poetry run gwc-email search "from:alice@example.com" --output json | \
  jq -r '.[0].id' | \
  xargs -I {} poetry run gwc-email get {}
```

## Troubleshooting

### "No valid authentication token found"

You haven't authenticated yet. Run:

```bash
poetry run gwc auth
```

### "No messages found"

Try a different search query, or use the full search syntax:

```bash
# Try with date
poetry run gwc-email search "after:2025-01-01"

# Try with label
poetry run gwc-email list --label INBOX
```

### Command not recognized

Make sure you're in the right directory:

```bash
cd ~/Jarvis/sagas/src/google-workspace-cli
```

### Still stuck?

Check the full documentation:

```bash
poetry run gwc-email <command> --help
```

Or read [REFERENCE.md](REFERENCE.md) for detailed command documentation.

## Command Cheat Sheet

```bash
# Search & Browse
poetry run gwc-email list --output llm
poetry run gwc-email search "QUERY" --output llm
poetry run gwc-email get MESSAGE_ID --output llm
poetry run gwc-email thread THREAD_ID --output llm

# Labels
poetry run gwc-email labels list
poetry run gwc-email labels get "LABEL_NAME"
poetry run gwc-email labels map

# Help & Examples
poetry run gwc-email search-help
poetry run gwc-email <command> --help
```

## What to Do Next

✓ **Authentication done?** → Explore [SKILL.md](SKILL.md)
✓ **Know the basics?** → Check [REFERENCE.md](REFERENCE.md) for advanced usage
✓ **Want integration?** → See [../../README_GMAIL.md](../../README_GMAIL.md#integration--automation)

---

**Congratulations!** You're now ready to use `gwc-email`. Enjoy managing your emails!

For detailed documentation, see [INDEX.md](INDEX.md).
