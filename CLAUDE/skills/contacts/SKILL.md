---
name: contacts
description: Google Contacts management and contact discovery.
---

## Quick Start

All commands run from `~/Jarvis/sagas/src/google-workspace-cli` using `poetry run gwc-people <command>`.

### Most Common Tasks

**See all your contacts:**
```bash
poetry run gwc-people list --output llm
```

**Search for a contact by name:**
```bash
poetry run gwc-people search "John" --output llm
```

**Find contact by email:**
```bash
poetry run gwc-people search "john@example.com"
```

**Get full details for a contact:**
```bash
poetry run gwc-people get "john@example.com" --output json
```

**Or by resource name:**
```bash
poetry run gwc-people get "people/c5187881666262445018" --output llm
```

**List contacts with pagination:**
```bash
poetry run gwc-people list --limit 50 --output llm
```

**Sort contacts by name:**
```bash
poetry run gwc-people list --limit 100 --sort FIRST_NAME_ASCENDING --output llm
```

## Output Formats

- `--output unix` - Tab-separated (default, for scripting)
- `--output json` - JSON (for programmatic parsing)
- `--output llm` - Human-readable (use this most of the time!)

## Common Tasks

### Finding Contacts

**Find by name (prefix matching):**
```bash
poetry run gwc-people search "Alice" --output llm
```

**Find by email domain:**
```bash
poetry run gwc-people search "@company.com" --output llm
```

**Get contact by exact email:**
```bash
poetry run gwc-people get "alice@company.com" --output json
```

### Listing Contacts

**See first 10 contacts (default):**
```bash
poetry run gwc-people list --limit 10 --output llm
```

**See all contacts with first name sorting:**
```bash
poetry run gwc-people list --limit 1000 --sort FIRST_NAME_ASCENDING --output llm
```

**Sort by last modification:**
```bash
poetry run gwc-people list --sort LAST_MODIFIED_DESCENDING --output llm
```

### Viewing Contact Details

**Get full contact information as JSON:**
```bash
poetry run gwc-people get "alice@company.com" --output json
```

**Get contact by resource name:**
```bash
poetry run gwc-people get "people/c123456789" --output json
```

## Common Options

Most commands support:
- `--limit INTEGER` - Number of results (search: 1-30, list: 1-1000)
- `--sort [FIRST_NAME_ASCENDING|LAST_NAME_ASCENDING|LAST_MODIFIED_ASCENDING|LAST_MODIFIED_DESCENDING]` - Sort order (list only)
- `--output [unix|json|llm]` - Output format

## For Complex Tasks

See **REFERENCE.md** in this directory for:
- Complete option reference for all commands
- Field descriptions in contact objects
- Sorting options and pagination
- Search limitations and behaviors
- Contact resource names

## Quick Command List

- `search` - Find contacts by name, email, phone, or organization
- `get` - Get full contact details by email or resource name
- `list` - List all contacts with sorting and pagination
- `auth` - Authenticate or refresh token

## Help

Get detailed help for any command:
```bash
poetry run gwc-people <command> --help
```

## Common Workflows

### Morning Contact Review
```bash
# Get list of important contacts
poetry run gwc-people search "@company.com" --limit 20 --output llm
```

### Look Up Meeting Attendee
```bash
# Find contact by email
poetry run gwc-people get "alice@company.com" --output llm
```

### Get Contact for Calendar Event
```bash
# Search and get details for someone you're meeting
poetry run gwc-people search "John" --output json | head -1
# Then get full details
poetry run gwc-people get "john@example.com" --output json
```

### Export Contacts (Integration)
```bash
# Get all contacts in JSON for programmatic use
poetry run gwc-people list --limit 1000 --output json > contacts.json
```

### Search by Organization
```bash
# Find all contacts from a company
poetry run gwc-people search "Acme" --output llm
```

## Tips & Tricks

**1. Use `--output llm` for human-friendly output:**
```bash
poetry run gwc-people search "John" --output llm
```

**2. Search is prefix-based (not fuzzy):**
```bash
# Will find "John Smith", "Johnson", "Johnny"
poetry run gwc-people search "John"

# Won't find "john" (case-insensitive search works)
```

**3. Use email for exact matches:**
```bash
# More reliable than name search
poetry run gwc-people get "john@example.com"
```

**4. Get resource names for integration:**
```bash
# Resource names are useful when integrating with other commands
poetry run gwc-people search "John" --output json | jq '.[0].resourceName'
```

**5. List with large limit for export:**
```bash
# Get many contacts at once
poetry run gwc-people list --limit 1000 --output json > all_contacts.json
```
