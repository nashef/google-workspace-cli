---
name: contacts-index
description: Navigation guide for Google Contacts CLI documentation
---

# Google Contacts CLI - Complete Documentation Index

This directory contains comprehensive documentation for `gwc-people`, the Google Workspace People API CLI tool. Choose the right guide for your needs:

## Quick Navigation

### I Want to...

**Get started immediately** → Read **[SKILL.md](SKILL.md)**
- Quick start guide
- Most common tasks with examples
- Essential commands overview
- Tips & tricks

**Look up a specific command** → Check **[REFERENCE.md](REFERENCE.md)**
- Complete command reference
- All options and parameters
- Output formats
- Full examples for each command
- API limitations and behaviors

**Understand the full project** → See **[../../../README_PEOPLE.md](../../../README_PEOPLE.md)**
- Feature overview
- Installation and authentication
- Integration with Calendar/Email
- Performance recommendations
- Troubleshooting guide

**Learn the Google People API** → Study **[../../../PEOPLE_API.md](../../../PEOPLE_API.md)**
- API architecture and design
- All available endpoints
- OAuth scopes and authentication
- Batch operations
- Quota and limits

## Documentation Structure

```
contacts/
├── INDEX.md (this file)
│   └─ Navigation guide
├── SKILL.md
│   └─ Common tasks and quick examples
├── REFERENCE.md
│   └─ Complete command reference
└─ supporting files:
    ├── ../../README_PEOPLE.md
    │   └─ Complete user guide
    └── ../../PEOPLE_API.md
        └─ Technical API reference
```

## Common Tasks by Use Case

### Daily Usage

**Search and review contacts:**
```bash
# See all contacts
poetry run gwc-people list --output llm

# Find someone specific
poetry run gwc-people search "Alice" --output llm

# Get full details
poetry run gwc-people get "alice@example.com" --output json
```

See **[SKILL.md - Common Workflows](SKILL.md#common-workflows)**

### Contact Management

**Create, organize, and maintain contacts:**
```bash
# Create new contact
poetry run gwc-people create --name "Jane Doe" --email "jane@example.com"

# Create groups
poetry run gwc-people groups create "Engineering Team"

# Add to group
poetry run gwc-people groups add-member "Engineering Team" "jane@example.com"

# Update contact
poetry run gwc-people update "jane@example.com" --phone "+1-555-0001"
```

See **[SKILL.md - Create, Update, Delete](SKILL.md#create-update-delete)** and **[SKILL.md - Contact Groups](SKILL.md#contact-groups)**

### Backup & Migration

**Export and import contacts:**
```bash
# Backup to CSV
poetry run gwc-people export ~/backup_20241118.csv

# Restore from CSV
poetry run gwc-people import ~/backup_20241118.csv

# Export to JSON
poetry run gwc-people export ~/contacts.json
```

See **[SKILL.md - Import & Export](SKILL.md#import--export)**

### Performance & Caching

**Optimize for speed:**
```bash
# Warmup cache
poetry run gwc-people cache sync

# Check cache
poetry run gwc-people cache list

# Clear if needed
poetry run gwc-people cache clear
```

See **[SKILL.md - Cache Management](SKILL.md#cache-management)**

### Enterprise/Workspace Features

**Search company directory:**
```bash
# Find in Workspace directory
poetry run gwc-people directory search "Alice"
```

See **[SKILL.md - Workspace Directory](SKILL.md#workspace-directory-enterprise)**

## Command Categories

### Core Contact Operations

| Command | Purpose | Doc Link |
|---------|---------|----------|
| `search` | Find contacts | [REFERENCE](REFERENCE.md#gwc-people-search) |
| `get` | Get details | [REFERENCE](REFERENCE.md#gwc-people-get) |
| `list` | List all | [REFERENCE](REFERENCE.md#gwc-people-list) |
| `create` | Create new | [REFERENCE](REFERENCE.md#gwc-people-create) |
| `update` | Modify | [REFERENCE](REFERENCE.md#gwc-people-update) |
| `delete` | Remove | [REFERENCE](REFERENCE.md#gwc-people-delete) |

See **[SKILL.md - All Available Commands](SKILL.md#all-available-commands)**

### Import/Export

| Command | Purpose | Doc Link |
|---------|---------|----------|
| `export` | Save to file | [REFERENCE](REFERENCE.md#gwc-people-export) |
| `import` | Load from file | [REFERENCE](REFERENCE.md#gwc-people-import) |

See **[SKILL.md - Import & Export](SKILL.md#import--export)**

### Organization

| Command | Purpose | Doc Link |
|---------|---------|----------|
| `groups` | Manage groups | [REFERENCE](REFERENCE.md#gwc-people-groups) |
| `directory` | Workspace search | [REFERENCE](REFERENCE.md#gwc-people-directory) |

See **[SKILL.md - Contact Groups](SKILL.md#contact-groups)** and **[SKILL.md - Workspace Directory](SKILL.md#workspace-directory-enterprise)**

### Maintenance

| Command | Purpose | Doc Link |
|---------|---------|----------|
| `cache` | Cache management | [REFERENCE](REFERENCE.md#gwc-people-cache) |
| `auth` | Authentication | [REFERENCE](REFERENCE.md#gwc-people-auth) |

See **[SKILL.md - Cache Management](SKILL.md#cache-management)**

## Feature Highlights

### Iteration 4 Additions (Latest)

✨ **New in Iteration 4:**

- **Import/Export** - CSV and JSON support with auto-detection
- **Advanced Filters** - Organization, domain, phone, and name-based filtering
- **Performance** - Batch operations, caching, and optimization functions
- **Groups** - Full contact group management
- **Directory** - Workspace directory search (enterprise)
- **Cache** - Local SQLite cache with sync tokens

See **[README_PEOPLE.md](../../../README_PEOPLE.md)** for complete feature list

### Output Formats

Choose the right format for your use:

- **`--output unix`** - Tab-separated for scripting
- **`--output json`** - Full JSON for programmatic use
- **`--output llm`** - Human-readable (recommended for interactive use)

See **[SKILL.md - Output Formats](SKILL.md#output-formats)** and **[REFERENCE.md - Output Formats](REFERENCE.md#output-formats)**

## Getting Help

### For Command Help

```bash
# Get help for any command
poetry run gwc-people <command> --help

# Examples:
poetry run gwc-people search --help
poetry run gwc-people export --help
poetry run gwc-people groups --help
```

### For This Documentation

1. **Quick question?** → [SKILL.md](SKILL.md)
2. **Need exact syntax?** → [REFERENCE.md](REFERENCE.md)
3. **Want detailed guide?** → [README_PEOPLE.md](../../../README_PEOPLE.md)
4. **Understanding API?** → [PEOPLE_API.md](../../../PEOPLE_API.md)

## Key Concepts

### Search Behavior

- **Prefix-based**: Matches beginning of words only
- **Case-insensitive**: "John" finds "john", "JOHN"
- **Cross-field**: Searches names, emails, phones, organizations
- **Max results**: 30 per search

See **[REFERENCE.md - Search Limitations](REFERENCE.md#search-limitations)**

### Resource Names

Unique contact identifiers in format: `people/c<numeric_id>`

Example: `people/c5187881666262445018`

Use for reliable lookups and integration.

See **[REFERENCE.md - Resource Names](REFERENCE.md#resource-names)**

### Sync Tokens

Local cache uses sync tokens for incremental updates:
- First sync: Downloads all contacts
- Subsequent syncs: Only changes

Stored in SQLite: `~/.config/gwc/contacts.db`

See **[SKILL.md - Cache Management](SKILL.md#cache-management)**

## Tips for Success

1. **Use `--output llm` for interactive use** - Most readable format
2. **Cache for performance** - Run `cache sync` once for speed boost
3. **Backup regularly** - Use `export` for safety
4. **Search by email** - More reliable than name search
5. **Use groups** - Organize related contacts
6. **Check help** - `<command> --help` for options

See **[SKILL.md - Tips & Tricks](SKILL.md#tips--tricks)**

## Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| "No valid authentication token" | Run `poetry run gwc-people auth` |
| "Contact not found" | Search is prefix-based; try `search` instead of exact name |
| Slow search | Run `cache sync` to warmup local cache |
| Cache out of sync | Run `cache sync --full` to force resync |

See **[README_PEOPLE.md - Troubleshooting](../../../README_PEOPLE.md#troubleshooting)** for more

## Integration

### With Calendar

Get contact email for meeting attendees:
```bash
poetry run gwc-people search "Alice" --output json | jq -r '.[0].email'
```

### With Shell Scripts

Export emails to a file:
```bash
poetry run gwc-people search "Engineering" --output json | jq -r '.[].email' > team.txt
```

### With Spreadsheets

Export to CSV for Excel/Google Sheets:
```bash
poetry run gwc-people export ~/contacts.csv
```

See **[README_PEOPLE.md - Integration](../../../README_PEOPLE.md#integration-with-other-tools)**

## Performance Metrics

Based on actual testing:

| Operation | Time | Notes |
|-----------|------|-------|
| Search | ~100ms | First search slower on large lists |
| Batch get (10 contacts) | ~95ms | More efficient than individual gets |
| Cache warmup (19 contacts) | 170ms | One-time operation |
| CSV export | 110ms | Fast for small/medium lists |

Cache improves search performance significantly after initial warmup.

See **[README_PEOPLE.md - Performance Tips](../../../README_PEOPLE.md#performance-tips)**

## What's Included

**✓ Complete** - All People API operations
**✓ Tested** - 14+ integration tests passed
**✓ Documented** - Comprehensive guides and examples
**✓ Optimized** - Performance tuned with caching
**✓ Enterprise-Ready** - Workspace directory support

**Pending** - Calendar CLI integration (next iteration)

## Contributing & Feedback

For issues, improvements, or questions:
- Check existing documentation
- Review example commands
- Try `<command> --help` for quick help
- Consult the main README for setup issues

---

**Last Updated:** Iteration 4
**Status:** Complete and tested
**Version:** 4.0.0
