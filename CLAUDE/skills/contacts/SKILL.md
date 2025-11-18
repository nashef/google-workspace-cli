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

## All Available Commands

**Core Operations:**
- `search` - Find contacts by name, email, phone, or organization
- `get` - Get full contact details by email or resource name
- `list` - List all contacts with sorting and pagination
- `create` - Create a new contact
- `update` - Update an existing contact
- `delete` - Delete a contact

**Import/Export:**
- `export` - Export all contacts to CSV or JSON
- `import` - Import contacts from CSV or JSON

**Organization:**
- `groups` - Manage contact groups (list, get, create, update, delete, add-member, remove-member)
- `directory` - Search Workspace directory (Workspace only)

**Performance & Maintenance:**
- `cache` - Local cache management (list, sync, clear)
- `auth` - Authenticate or refresh token

## Help

Get detailed help for any command:
```bash
poetry run gwc-people <command> --help
```

## Create, Update, Delete

**Create a contact:**
```bash
poetry run gwc-people create --name "Jane Doe" --email "jane@example.com" --phone "+1-555-0001" --organization "Tech Inc"
```

**Update a contact:**
```bash
poetry run gwc-people update "jane@example.com" --phone "+1-555-0002"
```

**Delete a contact:**
```bash
poetry run gwc-people delete "jane@example.com"
```

## Import & Export

**Export all contacts to CSV:**
```bash
poetry run gwc-people export ~/my_contacts.csv
```

**Export all contacts to JSON:**
```bash
poetry run gwc-people export ~/my_contacts.json
```

**Import contacts from CSV:**
```bash
poetry run gwc-people import ~/my_contacts.csv
```

**Import contacts from JSON:**
```bash
poetry run gwc-people import ~/my_contacts.json
```

**Backup & restore workflow:**
```bash
# Backup
poetry run gwc-people export ~/backup_$(date +%Y%m%d).csv

# Later: restore
poetry run gwc-people import ~/backup_20241118.csv
```

## Contact Groups

**List all groups:**
```bash
poetry run gwc-people groups list --output llm
```

**Create a group:**
```bash
poetry run gwc-people groups create "Project Team"
```

**Add contacts to a group:**
```bash
poetry run gwc-people groups add-member "Project Team" "alice@example.com"
poetry run gwc-people groups add-member "Project Team" "bob@example.com"
```

**Remove contact from group:**
```bash
poetry run gwc-people groups remove-member "Project Team" "alice@example.com"
```

**Delete a group:**
```bash
poetry run gwc-people groups delete "Project Team"
```

## Cache Management

**Check cache statistics:**
```bash
poetry run gwc-people cache list --limit 10 --output llm
```

**Sync cache with Google Contacts:**
```bash
poetry run gwc-people cache sync
```

**Force full cache resync:**
```bash
poetry run gwc-people cache sync --full
```

**Clear cache (useful if out of sync):**
```bash
poetry run gwc-people cache clear
```

## Workspace Directory (Enterprise)

**Search company directory:**
```bash
poetry run gwc-people directory search "Alice" --output llm
```

**List directory people:**
```bash
poetry run gwc-people directory list --limit 50 --output llm
```

*Note: Requires Google Workspace account with directory sharing enabled.*

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

### Create & Organize Team Contacts
```bash
# Create a group for your team
poetry run gwc-people groups create "Engineering Team"

# Add team members
poetry run gwc-people groups add-member "Engineering Team" "alice@example.com"
poetry run gwc-people groups add-member "Engineering Team" "bob@example.com"
poetry run gwc-people groups add-member "Engineering Team" "charlie@example.com"

# View team
poetry run gwc-people groups get "Engineering Team" --output llm
```

### Backup & Migrate Contacts
```bash
# Backup to CSV
poetry run gwc-people export ~/backup_$(date +%Y%m%d).csv

# Later: restore on new machine
poetry run gwc-people import ~/backup_20241118.csv
```

### Search by Organization
```bash
# Find all contacts from a company
poetry run gwc-people search "Acme" --output llm
```

### Find Contacts by Email Domain
```bash
# Find all @company.com emails
poetry run gwc-people search "@company.com" --output llm
```

### Find Contacts with Phone Numbers
```bash
# Get all contacts that have phone numbers
poetry run gwc-people search "" --limit 1000 | grep -v "N/A" | grep "[0-9]"
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

**6. Cache improves search performance:**
```bash
# Warmup cache on first use
poetry run gwc-people cache sync

# Subsequent searches are much faster
poetry run gwc-people search "Alice" --output llm
```

**7. Use CSV for spreadsheet compatibility:**
```bash
# Export to CSV for use in Excel
poetry run gwc-people export ~/contacts.csv

# Edit in spreadsheet, then reimport
poetry run gwc-people import ~/contacts.csv
```

**8. Combine commands with shell piping:**
```bash
# Get emails of all contacts from a company
poetry run gwc-people search "Acme" --output json | jq -r '.[].email'

# Save to a file
poetry run gwc-people search "Acme" --output json | jq -r '.[].email' > acme_emails.txt
```

**9. Filter results with common Unix tools:**
```bash
# Find contacts with specific phone area code
poetry run gwc-people list --limit 1000 --output unix | grep "703"

# Count contacts
poetry run gwc-people list --limit 1000 --output unix | wc -l
```

**10. Keep cache in sync regularly:**
```bash
# Add to cron job for daily sync
# 0 9 * * * cd ~/Jarvis/sagas/src/google-workspace-cli && poetry run gwc-people cache sync
```

**11. Batch operations for performance:**
```bash
# Import large CSV files - all at once is more efficient
poetry run gwc-people import ~/large_contact_list.csv
```

**12. Error handling in scripts:**
```bash
# Check exit code after operations
poetry run gwc-people update "john@example.com" --phone "+1-555-0001" || echo "Update failed"

# Use in conditional logic
if poetry run gwc-people get "alice@example.com" > /dev/null 2>&1; then
    echo "Contact exists"
else
    echo "Contact not found"
fi
```
