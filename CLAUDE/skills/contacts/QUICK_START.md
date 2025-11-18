---
name: contacts-quick-start
description: Get started with Google Contacts CLI in 5 minutes
---

# Google Contacts CLI - Quick Start (5 Minutes)

Get up and running with `gwc-people` in just a few minutes.

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
poetry run gwc-people auth
```

This will:
- Open your browser to Google's sign-in page
- Ask you to approve access to your contacts
- Save your credentials for future use

**Done!** You're authenticated and ready to use `gwc-people`.

## Your First Commands (2 Minutes)

### See all your contacts

```bash
poetry run gwc-people list --output llm
```

Output will look like:
```
displayName: John Smith
email: john@example.com
phone: 555-123-4567
resourceName: people/c123456789
```

### Search for someone

```bash
poetry run gwc-people search "Alice" --output llm
```

### Get details about a contact

```bash
poetry run gwc-people get "alice@example.com" --output llm
```

### Create a new contact

```bash
poetry run gwc-people create --name "Jane Doe" --email "jane@example.com"
```

### Create a contact group

```bash
poetry run gwc-people groups create "My Team"
```

### Add someone to a group

```bash
poetry run gwc-people groups add-member "My Team" "alice@example.com"
```

### Backup your contacts

```bash
poetry run gwc-people export ~/contacts.csv
```

### Restore from backup

```bash
poetry run gwc-people import ~/contacts.csv
```

## Three Essential Tips

### Tip 1: Use `--output llm` for readability

The default output is tab-separated (good for scripting). Use `--output llm` to see nice, readable output:

```bash
# Hard to read
poetry run gwc-people search "John"

# Easy to read
poetry run gwc-people search "John" --output llm
```

### Tip 2: Get help for any command

Forgotten the exact syntax? Just ask:

```bash
poetry run gwc-people search --help
poetry run gwc-people create --help
poetry run gwc-people groups --help
```

### Tip 3: Use email for exact matches

Search is prefix-based. If you want to find someone exactly, use their email:

```bash
# Might return multiple results
poetry run gwc-people search "John"

# Returns exactly one person
poetry run gwc-people get "john@example.com" --output llm
```

## Common Workflows

### I want to find someone

```bash
poetry run gwc-people search "Alice" --output llm
```

### I want to get their email for a calendar event

```bash
poetry run gwc-people search "Bob" --output json | jq -r '.[0].email'
```

### I want to create a team group and add people

```bash
# Create group
poetry run gwc-people groups create "Engineering Team"

# Add people
poetry run gwc-people groups add-member "Engineering Team" "alice@example.com"
poetry run gwc-people groups add-member "Engineering Team" "bob@example.com"

# See the group
poetry run gwc-people groups get "Engineering Team" --output llm
```

### I want to backup my contacts before doing something risky

```bash
poetry run gwc-people export ~/backup_$(date +%Y%m%d).csv
```

### I want to import contacts from a CSV file

```bash
poetry run gwc-people import ~/my_contacts.csv
```

## Next Steps

Now you know the basics! Here's what to explore:

1. **Learn more commands** - See [SKILL.md](SKILL.md) for common tasks
2. **Look up syntax** - Check [REFERENCE.md](REFERENCE.md) for complete reference
3. **Understand features** - Read [INDEX.md](INDEX.md) for navigation
4. **Get details** - Study [../../README_PEOPLE.md](../../README_PEOPLE.md) for comprehensive guide

## Keyboard Shortcuts & Pro Tips

### Get command help quickly

Instead of searching docs, just add `--help`:

```bash
poetry run gwc-people export --help
```

### Use output formats for different needs

```bash
# For humans (most readable)
poetry run gwc-people list --output llm

# For programs/scripts
poetry run gwc-people list --output json

# For importing into other tools
poetry run gwc-people list --output unix
```

### Chain commands together

Get all emails from your Engineering Team:

```bash
poetry run gwc-people groups get "Engineering Team" --output json | jq -r '.[].email'
```

### Export for different purposes

```bash
# For Excel/Google Sheets
poetry run gwc-people export ~/contacts.csv

# For backup/archival
poetry run gwc-people export ~/backup.json
```

## Troubleshooting

### "No valid authentication token found"

You haven't authenticated yet. Run:

```bash
poetry run gwc-people auth
```

### "Contact not found"

Remember: search is prefix-based. Try a different term:

```bash
# Instead of this (looking for "John.Smith@company.com")
poetry run gwc-people search "John.Smith"

# Try this
poetry run gwc-people get "john.smith@company.com"
```

### Command not recognized

Make sure you're in the right directory:

```bash
cd ~/Jarvis/sagas/src/google-workspace-cli
```

### Still stuck?

Check the full documentation:

```bash
poetry run gwc-people <command> --help
```

Or read [REFERENCE.md](REFERENCE.md) for detailed command documentation.

## Command Cheat Sheet

```bash
# Search & Browse
poetry run gwc-people search "NAME" --output llm
poetry run gwc-people list --output llm
poetry run gwc-people get "EMAIL" --output llm

# Create & Modify
poetry run gwc-people create --name "NAME" --email "EMAIL"
poetry run gwc-people update "EMAIL" --phone "+1-555-0001"
poetry run gwc-people delete "EMAIL"

# Groups
poetry run gwc-people groups list
poetry run gwc-people groups create "GROUP_NAME"
poetry run gwc-people groups add-member "GROUP_NAME" "EMAIL"
poetry run gwc-people groups remove-member "GROUP_NAME" "EMAIL"

# Import/Export
poetry run gwc-people export ~/contacts.csv
poetry run gwc-people import ~/contacts.csv

# Cache & Maintenance
poetry run gwc-people cache sync
poetry run gwc-people cache list
poetry run gwc-people auth --refresh
```

## What to Do Next

✓ **Authentication done?** → Explore [SKILL.md](SKILL.md)
✓ **Know the basics?** → Check [REFERENCE.md](REFERENCE.md) for advanced usage
✓ **Want integration?** → See [../../README_PEOPLE.md](../../README_PEOPLE.md#integration-with-other-tools)

---

**Congratulations!** You're now ready to use `gwc-people`. Enjoy managing your contacts!

For detailed documentation, see [INDEX.md](INDEX.md).
