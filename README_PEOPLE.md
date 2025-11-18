# Google Workspace People API CLI (`gwc-people`)

Complete command-line interface for managing Google Contacts and accessing Google Workspace directory information.

## Features

- **Contact Management**: Full CRUD operations on contacts (create, read, update, delete)
- **Search**: Prefix-based search across names, emails, phone numbers, and organizations
- **Batch Operations**: Create/update/delete up to 1000 contacts in a single request
- **Contact Groups**: Create, manage, and organize contacts into groups
- **Directory Access**: Search Google Workspace domain directory (Workspace accounts only)
- **Local Caching**: SQLite database with incremental sync support for improved performance
- **Import/Export**: CSV and JSON support for backup and data migration
- **Multiple Output Formats**: Unix (TSV), JSON, and human-readable (LLM) output

## Installation & Setup

### Prerequisites

- Python 3.7+
- `poetry` package manager
- Google Workspace account (or personal Google account)

### Initial Setup

1. **Install dependencies:**
   ```bash
   cd ~/Jarvis/sagas/src/google-workspace-cli
   poetry install
   ```

2. **Authenticate with Google:**
   ```bash
   poetry run gwc-people auth
   ```

   This will:
   - Open your browser to Google's OAuth consent screen
   - Ask you to approve access to your contacts
   - Store credentials locally in `~/.config/gwc/`

3. **Verify installation:**
   ```bash
   poetry run gwc-people list --limit 5 --output llm
   ```

## Quick Start

### Most Common Operations

**List all contacts:**
```bash
poetry run gwc-people list --output llm
```

**Search for a contact:**
```bash
poetry run gwc-people search "John" --output llm
```

**Get detailed contact info:**
```bash
poetry run gwc-people get "john@example.com" --output json
```

**Create a new contact:**
```bash
poetry run gwc-people create --name "Jane Doe" --email "jane@example.com"
```

**Update a contact:**
```bash
poetry run gwc-people update "john@example.com" --phone "+1-555-0001"
```

**Delete a contact:**
```bash
poetry run gwc-people delete "john@example.com"
```

**Export contacts:**
```bash
poetry run gwc-people export ~/my_contacts.csv
poetry run gwc-people export ~/my_contacts.json
```

**Import contacts:**
```bash
poetry run gwc-people import ~/my_contacts.csv
poetry run gwc-people import ~/my_contacts.json
```

## Command Reference

### Searching & Listing

#### `gwc-people search`
Search contacts by name, email, phone, or organization.

```bash
poetry run gwc-people search "query" [--limit 10] [--output unix|json|llm]
```

**Examples:**
```bash
# Search by name
poetry run gwc-people search "Alice"

# Search by email
poetry run gwc-people search "alice@company.com"

# Search by organization
poetry run gwc-people search "Acme Corp" --limit 20

# Get JSON output for parsing
poetry run gwc-people search "Bob" --output json | jq '.[0].email'
```

#### `gwc-people get`
Get detailed information about a specific contact.

```bash
poetry run gwc-people get <email_or_id> [--output unix|json|llm]
```

**Arguments:**
- `email_or_id`: Contact's email address or resource name (e.g., `people/c123456789`)

**Examples:**
```bash
# By email
poetry run gwc-people get "alice@company.com"

# By resource name
poetry run gwc-people get "people/c5187881666262445018"

# As JSON (for parsing)
poetry run gwc-people get "alice@company.com" --output json
```

#### `gwc-people list`
List your contacts with optional filtering and sorting.

```bash
poetry run gwc-people list [--limit 100] [--sort SORT_ORDER] [--output unix|json|llm]
```

**Sorting Options:**
- `FIRST_NAME_ASCENDING` - Sort by first name (A-Z)
- `LAST_NAME_ASCENDING` - Sort by last name (A-Z)
- `LAST_MODIFIED_ASCENDING` - Oldest modifications first
- `LAST_MODIFIED_DESCENDING` - Newest modifications first (default)

**Examples:**
```bash
# List first 50 contacts
poetry run gwc-people list --limit 50

# List all contacts sorted by first name
poetry run gwc-people list --limit 1000 --sort FIRST_NAME_ASCENDING --output llm

# List recently modified contacts
poetry run gwc-people list --limit 20 --sort LAST_MODIFIED_DESCENDING
```

### Contact Management

#### `gwc-people create`
Create a new contact.

```bash
poetry run gwc-people create \
  [--name TEXT] \
  [--email TEXT] \
  [--phone TEXT] \
  [--organization TEXT] \
  [--output unix|json|llm]
```

**Requirements:**
- At least `--name` or `--email` is required

**Examples:**
```bash
# Create with basic info
poetry run gwc-people create --name "John Smith" --email "john@example.com"

# Create with complete info
poetry run gwc-people create \
  --name "Jane Doe" \
  --email "jane@example.com" \
  --phone "+1-555-0001" \
  --organization "Tech Inc"
```

#### `gwc-people update`
Update an existing contact.

```bash
poetry run gwc-people update <email_or_id> \
  [--name TEXT] \
  [--email TEXT] \
  [--phone TEXT] \
  [--organization TEXT] \
  [--output unix|json|llm]
```

**Examples:**
```bash
# Update phone number
poetry run gwc-people update "john@example.com" --phone "+1-555-0002"

# Update multiple fields
poetry run gwc-people update "jane@example.com" \
  --name "Jane Smith" \
  --organization "New Company"
```

#### `gwc-people delete`
Delete a contact permanently.

```bash
poetry run gwc-people delete <email_or_id>
```

**Examples:**
```bash
# Delete by email
poetry run gwc-people delete "john@example.com"

# Delete by resource name
poetry run gwc-people delete "people/c123456789"
```

### Import/Export

#### `gwc-people export`
Export contacts to a file.

```bash
poetry run gwc-people export <file_path> [--format csv|json]
```

**Format Auto-Detection:**
- `.csv` extension → CSV format
- `.json` extension → JSON format
- `--format` option overrides auto-detection

**Examples:**
```bash
# Export to CSV (auto-detected)
poetry run gwc-people export ~/contacts.csv

# Export to JSON (auto-detected)
poetry run gwc-people export ~/contacts.json

# Export with explicit format
poetry run gwc-people export ~/my_data.txt --format csv
```

**CSV Format:**
```
name,email,phone,organization
John Smith,john@example.com,+1-555-0001,Acme Corp
Jane Doe,jane@example.com,,Tech Inc
```

#### `gwc-people import`
Import contacts from a file.

```bash
poetry run gwc-people import <file_path> [--format csv|json]
```

**Format Auto-Detection:**
- `.csv` extension → CSV format
- `.json` extension → JSON format
- Auto-detection can be overridden with `--format`

**CSV Format Requirements:**
- Header row with columns: `name,email,phone,organization`
- At least `name` or `email` required per row
- `phone` and `organization` are optional

**JSON Format Support:**
- Array of simple contact objects: `[{name, email, phone, organization}, ...]`
- Full Google People API contact objects (from previous exports)

**Examples:**
```bash
# Import from CSV
poetry run gwc-people import ~/contacts.csv

# Import from JSON
poetry run gwc-people import ~/contacts.json

# Import with error handling
# Command shows: Created: 10, Failed: 1, with error details
```

### Contact Groups

#### `gwc-people groups list`
List all contact groups.

```bash
poetry run gwc-people groups list [--output unix|json|llm]
```

#### `gwc-people groups get`
Get details of a specific group.

```bash
poetry run gwc-people groups get <group_name> [--output unix|json|llm]
```

#### `gwc-people groups create`
Create a new contact group.

```bash
poetry run gwc-people groups create <group_name>
```

#### `gwc-people groups update`
Rename a contact group.

```bash
poetry run gwc-people groups update <group_name> --name <new_name>
```

#### `gwc-people groups delete`
Delete a contact group.

```bash
poetry run gwc-people groups delete <group_name>
```

#### `gwc-people groups add-member`
Add a contact to a group.

```bash
poetry run gwc-people groups add-member <group_name> <email_or_id>
```

**Examples:**
```bash
# Add by email
poetry run gwc-people groups add-member "Work" "john@example.com"

# Add by resource name
poetry run gwc-people groups add-member "Work" "people/c123456789"
```

#### `gwc-people groups remove-member`
Remove a contact from a group.

```bash
poetry run gwc-people groups remove-member <group_name> <email_or_id>
```

### Caching

#### `gwc-people cache list`
List cached contacts.

```bash
poetry run gwc-people cache list [--limit 100] [--sort displayName|email|lastModified] [--output unix|json|llm]
```

#### `gwc-people cache sync`
Synchronize local cache with Google Contacts.

```bash
poetry run gwc-people cache sync [--full] [--force]
```

**Options:**
- `--full`: Force full sync (ignores cached sync token)
- `--force`: Sync even if cache is recent

**Behavior:**
- First sync: Downloads all contacts
- Subsequent syncs: Uses sync token for incremental updates
- Sync token stored in SQLite database

#### `gwc-people cache clear`
Clear all cached contacts and reset sync token.

```bash
poetry run gwc-people cache clear
```

### Directory Search (Workspace Only)

#### `gwc-people directory search`
Search Google Workspace directory.

```bash
poetry run gwc-people directory search <query> [--limit 30] [--output unix|json|llm]
```

**Requirements:**
- Google Workspace account
- Admin must enable directory sharing

#### `gwc-people directory list`
List people from Workspace directory.

```bash
poetry run gwc-people directory list [--limit 100] [--output unix|json|llm]
```

### Authentication

#### `gwc-people auth`
Authenticate or re-authenticate with Google.

```bash
poetry run gwc-people auth [--refresh]
```

**Options:**
- `--refresh`: Refresh existing token without re-authenticating

**Examples:**
```bash
# Initial authentication (opens browser)
poetry run gwc-people auth

# Refresh expired token
poetry run gwc-people auth --refresh
```

## Output Formats

### Unix Format (default)
Tab-separated values, one record per line. Best for scripting.

```
John Smith	john@example.com	555-123-4567	Acme Corp
Jane Doe	jane@example.com	N/A	Tech Inc
```

### JSON Format
Complete structured data. Best for programmatic parsing.

```json
[
  {
    "displayName": "John Smith",
    "email": "john@example.com",
    "phone": "555-123-4567",
    "resourceName": "people/c123456789"
  },
  {
    "displayName": "Jane Doe",
    "email": "jane@example.com",
    "phone": "N/A",
    "resourceName": "people/c987654321"
  }
]
```

### LLM Format
Human-readable output. Best for interactive use.

```
displayName: John Smith
email: john@example.com
phone: 555-123-4567
resourceName: people/c123456789
```

## Configuration

### Location
`~/.config/gwc/`

### Files
- `credentials.json` - OAuth2 credentials from Google Cloud Console
- `token.json` - Access/refresh tokens (auto-managed, do not edit)
- `contacts.db` - SQLite cache database (auto-created)

### Reset Authentication
```bash
rm ~/.config/gwc/token.json
poetry run gwc-people auth
```

## Common Workflows

### Find and Review Contact
```bash
# Search for contact
poetry run gwc-people search "Alice" --output llm

# Get full details
poetry run gwc-people get "alice@example.com" --output json
```

### Create Contact Group and Add Members
```bash
# Create group
poetry run gwc-people groups create "Project Team"

# Add members
poetry run gwc-people groups add-member "Project Team" "alice@example.com"
poetry run gwc-people groups add-member "Project Team" "bob@example.com"

# View group
poetry run gwc-people groups get "Project Team" --output llm
```

### Backup and Restore Contacts
```bash
# Backup to CSV
poetry run gwc-people export ~/backup_2024.csv

# Backup to JSON
poetry run gwc-people export ~/backup_2024.json

# Restore (import on new machine)
poetry run gwc-people import ~/backup_2024.csv
```

### Migrate Contacts Between Accounts
```bash
# Export from old account
poetry run gwc-people export ~/contacts_to_migrate.csv

# Switch account / re-authenticate
poetry run gwc-people auth

# Import to new account
poetry run gwc-people import ~/contacts_to_migrate.csv
```

### Filter by Organization
```bash
# List all contacts from a company
poetry run gwc-people search "Acme" --output llm

# Get detailed info
poetry run gwc-people get "john@acme.com" --output json
```

### Sync Cache for Offline Use
```bash
# Initial cache sync
poetry run gwc-people cache sync

# Check cached contacts
poetry run gwc-people cache list --limit 100 --output llm

# Force full resync
poetry run gwc-people cache sync --full

# Clear cache if needed
poetry run gwc-people cache clear
```

## API Limits & Behaviors

### Search
- **Max results:** 30 per search
- **Match type:** Prefix-based (not fuzzy)
- **Fields searched:** Name, email, phone, organization

### Listing
- **Max results:** 1000 per page
- **Sorting:** By name or modification time only
- **Filtering:** None (returns all contacts)

### Batch Operations
- **Max per batch:** 1000 contacts
- **Operations:** Create, update, delete
- **Quota:** Each operation counts separately

### Sync Tokens
- **Expiration:** Can expire, requiring full resync
- **Storage:** SQLite database in cache
- **Propagation:** Changes can take minutes to appear

## Troubleshooting

### "No valid authentication token found"
```bash
poetry run gwc-people auth
```

### "Request had insufficient authentication scopes"
Your token doesn't have the necessary permissions.
```bash
# Re-authenticate to grant new permissions
poetry run gwc-people auth
```

### "Contact not found"
Search is prefix-based, not exact match.
```bash
# Try searching instead
poetry run gwc-people search "john@example.com"
```

### Slow search performance
First search on large contact lists can be slow.
```bash
# Use caching to improve performance
poetry run gwc-people cache sync
poetry run gwc-people cache list
```

### Cache out of sync
```bash
# Force full resync
poetry run gwc-people cache sync --full

# Or clear and resync
poetry run gwc-people cache clear
poetry run gwc-people cache sync
```

## Integration with Other Tools

### Calendar Integration
Get contact email for meeting attendees:
```bash
poetry run gwc-people search "Alice" --output json | jq -r '.[0].email'
```

### Email Integration
Find contact by email:
```bash
poetry run gwc-people get "alice@example.com" --output json
```

### Data Export
Export for use with other tools:
```bash
# CSV for spreadsheet
poetry run gwc-people export ~/contacts.csv

# JSON for programmatic use
poetry run gwc-people export ~/contacts.json
```

## Performance Tips

1. **Use caching for frequent access:**
   ```bash
   poetry run gwc-people cache sync
   poetry run gwc-people cache list
   ```

2. **Use resource names for reliable lookups:**
   ```bash
   # Store resource name
   poetry run gwc-people search "John" --output json | jq -r '.[0].resourceName'

   # Use for future lookups
   poetry run gwc-people get "people/c123456789"
   ```

3. **Search is prefix-based:**
   ```bash
   # These work:
   poetry run gwc-people search "John"      # Finds John*, Johnny, etc.
   poetry run gwc-people search "john@"     # Finds john@*

   # These don't:
   poetry run gwc-people search "ohn"       # Won't find John
   ```

4. **Use email for exact matches:**
   ```bash
   # More reliable than name search
   poetry run gwc-people get "john@example.com"
   ```

5. **Batch operations for large datasets:**
   ```bash
   # Import many contacts at once
   poetry run gwc-people import ~/large_contact_list.csv
   ```

## Help & Documentation

### Get help for any command:
```bash
poetry run gwc-people <command> --help
```

### Full reference documentation:
See `CLAUDE/skills/contacts/REFERENCE.md`

### Quick tips and tricks:
See `CLAUDE/skills/contacts/SKILL.md`

### API documentation:
See `PEOPLE_API.md` for comprehensive Google People API reference

## Authentication Details

### Scopes Used
- `https://www.googleapis.com/auth/contacts` - Read/write contacts
- `https://www.googleapis.com/auth/contacts.readonly` - Read-only alternative
- `https://www.googleapis.com/auth/userinfo.profile` - Profile information
- `https://www.googleapis.com/auth/userinfo.email` - Email address

### Token Storage
- **Location:** `~/.config/gwc/token.json`
- **Security:** Contains refresh token (keep private!)
- **Expiration:** Access tokens auto-refresh as needed
- **Management:** Completely automatic (don't edit manually)

### OAuth Flow
1. First run: Browser opens for OAuth consent
2. You approve access to your Google account
3. Tokens saved locally
4. Subsequent runs: Automatic token refresh

## Limitations & Known Issues

### Search
- Prefix-based, not fuzzy matching
- Max 30 results per query
- Single-term search only

### Sync
- Tokens can expire (force full resync if needed)
- Propagation delay of several minutes
- Not intended for read-after-write scenarios

### Directory
- Requires Workspace account
- Admin must enable sharing
- Propagation delays

## Contributing & Feedback

For issues or feature requests, see the main project repository.

## License

Part of the Google Workspace CLI tool.
