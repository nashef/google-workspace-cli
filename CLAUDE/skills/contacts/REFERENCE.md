# Google Contacts CLI - Complete Reference

This is the exhaustive reference for all `gwc-people` commands and options. For common tasks, see **SKILL.md** instead.

## Commands Overview

```
gwc-people [OPTIONS] COMMAND [ARGS]...

Commands:
  auth      - Authenticate with Google Workspace
  search    - Search for contacts by name, email, phone, or organization
  get       - Get contact details by email address or resource name
  list      - List your contacts
  create    - Create a new contact
  update    - Update an existing contact
  delete    - Delete a contact
  cache     - Manage local contact cache
  groups    - Manage contact groups
  directory - Search Google Workspace directory (requires Workspace account)
  export    - Export contacts to CSV or JSON
  import    - Import contacts from CSV or JSON
```

---

## `gwc-people search`

Search for contacts by name, email, phone, or organization.

**Usage:**
```bash
gwc-people search QUERY [OPTIONS]
```

**Required Arguments:**
- `QUERY` - Search query (name, email, phone, or organization)

**Optional Options:**
- `--limit INTEGER` - Maximum results to return (default: 10, max: 30)
- `--output [unix|json|llm]` - Output format (default: unix)

**Return Fields:**
Each result includes:
- `displayName` - Contact's display name
- `email` - Primary email address (or N/A if none)
- `phone` - Primary phone number (or N/A if none)
- `resourceName` - Unique contact identifier (e.g., `people/c123456789`)

**Behavior:**
- Search is **prefix-based**, not fuzzy matching
- Searches across names, email addresses, phone numbers, and organization names
- Results limited to max 30 per API constraints
- If no email/phone found for a contact, shows "N/A"

**Examples:**

Search by name:
```bash
poetry run gwc-people search "John"
# Returns all contacts with names starting with "John"
```

Search by email:
```bash
poetry run gwc-people search "john@example.com"
# Finds contact by exact or partial email match
```

Search by organization:
```bash
poetry run gwc-people search "Acme"
# Finds all contacts from "Acme" organization
```

Limit results:
```bash
poetry run gwc-people search "John" --limit 5
```

JSON output for parsing:
```bash
poetry run gwc-people search "John" --output json | jq '.[0].email'
```

Human-readable output:
```bash
poetry run gwc-people search "John" --output llm
```

---

## `gwc-people get`

Get contact details by email address or resource name.

**Usage:**
```bash
gwc-people get EMAIL_OR_ID [OPTIONS]
```

**Required Arguments:**
- `EMAIL_OR_ID` - Contact email address or resource name (e.g., `people/c123456789`)

**Optional Options:**
- `--output [unix|json|llm]` - Output format (default: unix)

**Return Fields:**
When retrieving a contact, you get:
- `names` - Array of name records (includes displayName, givenName, familyName, etc.)
- `emailAddresses` - Array of email records (includes value, type, metadata)
- `phoneNumbers` - Array of phone records (includes value, canonicalForm, type)
- `organizations` - Array of organization records (includes name, title, department)
- `resourceName` - Unique contact identifier

**Email Lookup:**
If you provide an email address:
1. Command searches for contacts matching that email
2. If found, retrieves full contact details using the resource name
3. If not found, returns error "Contact not found"

**Resource Name Lookup:**
If you provide a resource name (e.g., `people/c5187881666262445018`):
1. Directly retrieves contact details for that resource
2. Faster than email-based lookup

**Examples:**

Get by email:
```bash
poetry run gwc-people get "john@example.com"
```

Get by resource name:
```bash
poetry run gwc-people get "people/c5187881666262445018"
```

Get as JSON (for programmatic parsing):
```bash
poetry run gwc-people get "john@example.com" --output json
```

Get in human-readable format:
```bash
poetry run gwc-people get "john@example.com" --output llm
```

Parse specific field from JSON:
```bash
poetry run gwc-people get "john@example.com" --output json | \
  jq '.emailAddresses[] | select(.metadata.primary) | .value'
```

---

## `gwc-people list`

List your contacts with optional filtering and sorting.

**Usage:**
```bash
gwc-people list [OPTIONS]
```

**Optional Options:**
- `--limit INTEGER` - Maximum contacts to return per page (default: 100, max: 1000)
- `--sort [FIRST_NAME_ASCENDING|LAST_NAME_ASCENDING|LAST_MODIFIED_ASCENDING|LAST_MODIFIED_DESCENDING]` - Sort order
- `--output [unix|json|llm]` - Output format (default: unix)

**Return Fields:**
Each contact includes:
- `displayName` - Contact's display name
- `email` - Primary email address (or N/A if none)
- `phone` - Primary phone number (or N/A if none)
- `organization` - Primary organization (or N/A if none)
- `resourceName` - Unique contact identifier

**Sorting Options:**
- `FIRST_NAME_ASCENDING` - Sort by first name (A-Z)
- `LAST_NAME_ASCENDING` - Sort by last name (A-Z)
- `LAST_MODIFIED_ASCENDING` - Oldest modifications first
- `LAST_MODIFIED_DESCENDING` - Newest modifications first

**Pagination:**
- Returns up to `--limit` contacts
- If more contacts exist, note will indicate "More results available"
- Currently does not support multi-page iteration in CLI

**Examples:**

List first 10 contacts (default):
```bash
poetry run gwc-people list
```

List first 50 contacts:
```bash
poetry run gwc-people list --limit 50
```

List all contacts (up to 1000) sorted by first name:
```bash
poetry run gwc-people list --limit 1000 --sort FIRST_NAME_ASCENDING
```

List by last name:
```bash
poetry run gwc-people list --limit 100 --sort LAST_NAME_ASCENDING --output llm
```

List by recent modifications:
```bash
poetry run gwc-people list --sort LAST_MODIFIED_DESCENDING --output llm
```

Export all contacts as JSON:
```bash
poetry run gwc-people list --limit 1000 --output json > all_contacts.json
```

Human-readable view:
```bash
poetry run gwc-people list --limit 20 --output llm
```

---

## `gwc-people create`

Create a new contact.

**Usage:**
```bash
gwc-people create [OPTIONS]
```

**Options:**
- `--name TEXT` - Contact's display name
- `--email TEXT` - Contact's email address
- `--phone TEXT` - Contact's phone number
- `--organization TEXT` - Contact's organization/company name
- `--output [unix|json|llm]` - Output format (default: unix)

**Requirements:**
- At least one of `--name` or `--email` is required

**Examples:**

Create contact with name and email:
```bash
poetry run gwc-people create --name "John Smith" --email "john@example.com"
```

Create contact with all details:
```bash
poetry run gwc-people create \
  --name "Jane Doe" \
  --email "jane@example.com" \
  --phone "+1-555-0001" \
  --organization "Acme Corp"
```

Create and view as JSON:
```bash
poetry run gwc-people create --name "Bob Wilson" --email "bob@example.com" --output json
```

---

## `gwc-people update`

Update an existing contact's information.

**Usage:**
```bash
gwc-people update EMAIL_OR_ID [OPTIONS]
```

**Required Arguments:**
- `EMAIL_OR_ID` - Contact email address or resource name

**Options:**
- `--name TEXT` - Update display name
- `--email TEXT` - Update email address
- `--phone TEXT` - Update phone number
- `--organization TEXT` - Update organization
- `--output [unix|json|llm]` - Output format (default: unix)

**Examples:**

Update contact's email:
```bash
poetry run gwc-people update "john@example.com" --email "newemail@example.com"
```

Update by resource name:
```bash
poetry run gwc-people update "people/c123456789" --phone "+1-555-0002"
```

Update multiple fields:
```bash
poetry run gwc-people update "jane@example.com" \
  --name "Jane Smith" \
  --phone "+1-555-0003" \
  --organization "Tech Inc"
```

---

## `gwc-people delete`

Delete a contact permanently.

**Usage:**
```bash
gwc-people delete EMAIL_OR_ID [OPTIONS]
```

**Required Arguments:**
- `EMAIL_OR_ID` - Contact email address or resource name

**Examples:**

Delete by email:
```bash
poetry run gwc-people delete "john@example.com"
```

Delete by resource name:
```bash
poetry run gwc-people delete "people/c123456789"
```

---

## `gwc-people export`

Export contacts to a file (CSV or JSON format).

**Usage:**
```bash
gwc-people export FILE_PATH [OPTIONS]
```

**Required Arguments:**
- `FILE_PATH` - Path where to save the exported file

**Options:**
- `--format [csv|json]` - Export format (default: csv, auto-detected from file extension)

**CSV Format:**
Simple tabular format with columns: `name,email,phone,organization`

**JSON Format:**
Full contact objects with all available fields and metadata.

**Examples:**

Export all contacts to CSV:
```bash
poetry run gwc-people export ~/contacts.csv
```

Export to JSON:
```bash
poetry run gwc-people export ~/contacts.json --format json
```

Auto-detect format from filename:
```bash
poetry run gwc-people export ~/my_contacts.csv  # Exports as CSV
poetry run gwc-people export ~/my_contacts.json # Exports as JSON
```

View exported file:
```bash
head ~/contacts.csv
cat ~/contacts.json | jq '.[0]'
```

---

## `gwc-people import`

Import contacts from a file (CSV or JSON format).

**Usage:**
```bash
poetry run gwc-people import FILE_PATH [OPTIONS]
```

**Required Arguments:**
- `FILE_PATH` - Path to the import file

**Options:**
- `--format [csv|json]` - Import format (default: auto-detect from file extension)

**CSV Format:**
Expected columns: `name,email,phone,organization`
- Header row is required
- Minimum: either name or email required per row
- Phone and organization are optional

**JSON Format:**
Accepts either:
- Array of simple contact objects: `[{name, email, phone, organization}, ...]`
- Array of full Google People API contact objects (from export)

**Error Handling:**
- Reports total created/failed counts
- Lists specific errors with row numbers
- Continues importing even if some rows fail
- Requires at least name or email per contact

**Examples:**

Import from CSV:
```bash
poetry run gwc-people import ~/contacts.csv
```

Import from JSON:
```bash
poetry run gwc-people import ~/contacts.json
```

Import with auto-format detection:
```bash
poetry run gwc-people import ~/my_contacts.csv  # Auto-detected as CSV
poetry run gwc-people import ~/my_contacts.json # Auto-detected as JSON
```

View import results:
```bash
# Command output shows:
# Import completed:
#   Created: 10
#   Failed: 1
#
# Errors:
#   Row 3: Failed to create contact: <error message>
```

---

## `gwc-people cache`

Manage the local contact cache.

**Usage:**
```bash
gwc-people cache SUBCOMMAND [OPTIONS]
```

**Subcommands:**

### `cache list`

List cached contacts.

**Usage:**
```bash
gwc-people cache list [OPTIONS]
```

**Options:**
- `--limit INTEGER` - Maximum contacts to display (default: 100)
- `--sort [displayName|email|lastModified]` - Sort order (default: displayName)
- `--output [unix|json|llm]` - Output format (default: unix)

**Examples:**

List cached contacts:
```bash
poetry run gwc-people cache list
```

List most recently modified:
```bash
poetry run gwc-people cache list --sort lastModified --limit 20
```

### `cache sync`

Synchronize cache with Google Contacts (incremental or full).

**Usage:**
```bash
gwc-people cache sync [OPTIONS]
```

**Options:**
- `--full` - Force full sync (ignores cached sync token)
- `--force` - Sync even if cache is recent

**Behavior:**
- On first sync: Performs full sync and stores sync token
- On subsequent syncs: Uses sync token for incremental updates
- Caches changes since last sync for better performance

**Examples:**

Perform incremental sync (uses cached token):
```bash
poetry run gwc-people cache sync
```

Force full resync:
```bash
poetry run gwc-people cache sync --full
```

Sync regardless of age:
```bash
poetry run gwc-people cache sync --force
```

### `cache clear`

Clear all cached contacts and reset sync token.

**Usage:**
```bash
poetry run gwc-people cache clear
```

**Behavior:**
- Deletes all cached contacts from local database
- Resets sync token
- Next sync will be a full sync

**Examples:**

Clear the cache:
```bash
poetry run gwc-people cache clear
```

---

## `gwc-people groups`

Manage contact groups.

**Usage:**
```bash
gwc-people groups SUBCOMMAND [OPTIONS]
```

**Subcommands:**

### `groups list`

List all contact groups.

**Usage:**
```bash
gwc-people groups list [OPTIONS]
```

**Options:**
- `--output [unix|json|llm]` - Output format (default: unix)

**Examples:**

List all groups:
```bash
poetry run gwc-people groups list
```

List as JSON:
```bash
poetry run gwc-people groups list --output json | jq '.[] | .name'
```

### `groups get`

Get details of a specific group.

**Usage:**
```bash
gwc-people groups get GROUP_NAME [OPTIONS]
```

**Options:**
- `--output [unix|json|llm]` - Output format (default: unix)

**Examples:**

Get group details:
```bash
poetry run gwc-people groups get "Work"
```

### `groups create`

Create a new contact group.

**Usage:**
```bash
gwc-people groups create GROUP_NAME
```

**Requirements:**
- Group names must be unique

**Examples:**

Create new group:
```bash
poetry run gwc-people groups create "Project Team"
```

### `groups update`

Rename a contact group.

**Usage:**
```bash
gwc-people groups update GROUP_NAME --name NEW_NAME
```

**Examples:**

Rename group:
```bash
poetry run gwc-people groups update "Team A" --name "Team Alpha"
```

### `groups delete`

Delete a contact group.

**Usage:**
```bash
gwc-people groups delete GROUP_NAME
```

**Examples:**

Delete group:
```bash
poetry run gwc-people groups delete "Temporary Group"
```

### `groups add-member`

Add a contact to a group.

**Usage:**
```bash
gwc-people groups add-member GROUP_NAME EMAIL_OR_ID
```

**Arguments:**
- `GROUP_NAME` - Name of the group
- `EMAIL_OR_ID` - Contact email or resource name

**Examples:**

Add contact to group by email:
```bash
poetry run gwc-people groups add-member "Work" "john@example.com"
```

Add contact by resource name:
```bash
poetry run gwc-people groups add-member "Work" "people/c123456789"
```

### `groups remove-member`

Remove a contact from a group.

**Usage:**
```bash
gwc-people groups remove-member GROUP_NAME EMAIL_OR_ID
```

**Examples:**

Remove contact from group:
```bash
poetry run gwc-people groups remove-member "Work" "john@example.com"
```

---

## `gwc-people directory`

Search Google Workspace directory (Workspace accounts only).

**Usage:**
```bash
gwc-people directory SUBCOMMAND [OPTIONS]
```

**Requirements:**
- Google Workspace account
- Admin must have enabled directory sharing

**Subcommands:**

### `directory search`

Search the Workspace directory.

**Usage:**
```bash
gwc-people directory search QUERY [OPTIONS]
```

**Options:**
- `--limit INTEGER` - Maximum results (default: 10, max: 30)
- `--output [unix|json|llm]` - Output format (default: unix)

**Examples:**

Search directory by name:
```bash
poetry run gwc-people directory search "John"
```

Search with limit:
```bash
poetry run gwc-people directory search "John" --limit 20
```

### `directory list`

List people from the Workspace directory.

**Usage:**
```bash
gwc-people directory list [OPTIONS]
```

**Options:**
- `--limit INTEGER` - Maximum results (default: 100, max: 1000)
- `--output [unix|json|llm]` - Output format (default: unix)

**Examples:**

List directory people:
```bash
poetry run gwc-people directory list --limit 50
```

---

## `gwc-people auth`

Authenticate or re-authenticate with Google Workspace.

**Usage:**
```bash
gwc-people auth [--refresh]
```

**Options:**
- `--refresh` - Refresh an existing token instead of performing initial authentication

**Initial Authentication:**
Without `--refresh`, performs initial OAuth2 setup:
1. Prints authorization URL
2. Guides you through authentication flow
3. Saves access and refresh tokens

**Example:**
```bash
poetry run gwc-people auth
```

**Token Refresh:**
With `--refresh`, refreshes existing token:
- Does not require re-authentication
- Obtains new access token using refresh token
- Saves updated token

**Example:**
```bash
poetry run gwc-people auth --refresh
```

**When to Use:**
- Initial auth: First time using gwc-people, or need to re-authenticate
- Refresh: Token has expired, or need to re-grant permissions

---

## Contact Object Structure

### Contact Response (from `get` command)

A complete contact object contains:

```json
{
  "resourceName": "people/c5187881666262445018",
  "etag": "%EgoBAgkLDC47PT4/GgQBAgUHIgxSNEFUakVNMTFzRT0=",
  "names": [
    {
      "metadata": {
        "primary": true,
        "source": {
          "type": "CONTACT",
          "id": "47ff0ee38e55abda"
        },
        "sourcePrimary": true
      },
      "displayName": "Scott Anderson",
      "familyName": "Anderson",
      "givenName": "Scott",
      "displayNameLastFirst": "Anderson, Scott",
      "unstructuredName": "Scott Anderson"
    }
  ],
  "emailAddresses": [
    {
      "metadata": {
        "primary": true,
        "source": {
          "type": "CONTACT",
          "id": "47ff0ee38e55abda"
        },
        "sourcePrimary": true
      },
      "value": "scott@example.com",
      "type": "work",
      "formattedType": "Work"
    }
  ],
  "phoneNumbers": [
    {
      "metadata": {
        "primary": true,
        "source": {
          "type": "CONTACT",
          "id": "47ff0ee38e55abda"
        }
      },
      "value": "555-123-4567",
      "canonicalForm": "+15551234567",
      "type": "work",
      "formattedType": "Work"
    }
  ],
  "organizations": [
    {
      "metadata": {
        "primary": true,
        "source": {
          "type": "CONTACT",
          "id": "47ff0ee38e55abda"
        }
      },
      "name": "Acme Corp",
      "title": "Senior Engineer",
      "department": "Engineering"
    }
  ]
}
```

### Search Result Object

A search result is a simplified contact with:

```json
{
  "resourceName": "people/c5187881666262445018",
  "displayName": "Scott Anderson",
  "email": "scott@example.com",
  "phone": "555-123-4567"
}
```

### List Result Object

A list result is a simplified contact with:

```json
{
  "displayName": "Scott Anderson",
  "email": "scott@example.com",
  "phone": "555-123-4567",
  "organization": "Acme Corp",
  "resourceName": "people/c5187881666262445018"
}
```

## Resource Names

Each contact has a unique `resourceName` in the format:
```
people/c<NUMERIC_ID>
```

Example: `people/c5187881666262445018`

**Use Cases:**
- Uniquely identify a contact
- Reference contact in integration with other tools
- Faster lookups than email-based searches

**Get Resource Name:**
```bash
# From search results
poetry run gwc-people search "John" --output json | jq '.[0].resourceName'

# From list results
poetry run gwc-people list --output json | jq '.[0].resourceName'

# From get command
poetry run gwc-people get "john@example.com" --output json | jq '.resourceName'
```

---

## Output Formats

### Unix Format (default)

Tab-separated values, one record per line. Good for scripting.

**Search example:**
```
John Smith	john@example.com	555-123-4567	people/c123456789
Jane Doe	jane@example.com	N/A	people/c987654321
```

**List example:**
```
Scott Anderson	scanderson@wcsr.com	704.331.4978	Womble, &c.
TCB	tcb@protonmail.com	N/A	N/A
```

**Get example (raw field data):**
```
[{...name objects...}]	[{...email objects...}]	[{...phone objects...}]	[{...org objects...}]	people/c123456789
```

### JSON Format

Complete structured data in JSON. Good for programmatic parsing.

**Search example:**
```json
[
  {
    "resourceName": "people/c123456789",
    "displayName": "John Smith",
    "email": "john@example.com",
    "phone": "555-123-4567"
  },
  {
    "resourceName": "people/c987654321",
    "displayName": "Jane Doe",
    "email": "jane@example.com",
    "phone": "N/A"
  }
]
```

**List example:**
```json
[
  {
    "displayName": "Scott Anderson",
    "email": "scanderson@wcsr.com",
    "phone": "704.331.4978",
    "organization": "Womble, &c.",
    "resourceName": "people/c5187881666262445018"
  }
]
```

**Get example (all contact details):**
```json
{
  "resourceName": "people/c5187881666262445018",
  "names": [...],
  "emailAddresses": [...],
  "phoneNumbers": [...],
  "organizations": [...]
}
```

### LLM Format

Human-readable, well-formatted output. Best for interactive use.

**Search example:**
```
displayName: John Smith
email: john@example.com
phone: 555-123-4567
resourceName: people/c123456789
```

**List example:**
```
displayName: Scott Anderson
email: scanderson@wcsr.com
phone: 704.331.4978
organization: Womble, &c.
resourceName: people/c5187881666262445018
```

---

## Configuration Files

**Location:** `~/.config/gwc/`

**Files:**
- `credentials.json` - OAuth2 credentials from Google Cloud Console
- `token.json` - Access/refresh tokens (auto-managed)

**To reset authentication:**
```bash
rm ~/.config/gwc/token.json
poetry run gwc-people auth
```

---

## API Limitations & Behavior

### Search Limitations
- **Max results:** 30 per search
- **Matching:** Prefix-based (not fuzzy)
- **Fields searched:** Name, email, phone, organization
- **Time:** API may be slow for large contact lists

### List Limitations
- **Max results:** 1000 per page
- **Sorting:** Only by name or modification time
- **No filtering:** Returns all contacts (can't filter by organization, etc.)

### Email Lookup
- When using `get <email>`, the tool searches first
- Search is prefix-based, not exact match
- If exact email not found, may return other matches
- For exact matching, use resource name instead

---

## Error Handling

### Common Errors

**Error: "Search query cannot be empty"**
- You passed an empty search query
- Solution: Provide a non-empty query string

**Error: "Contact not found"**
- `get` command couldn't find contact by email
- Solution: Use `search` to find the contact first, then `get` with the email

**Error: "No contacts found"**
- `search` command returned no results
- Solution: Try a different search term or use `list` to browse all contacts

**Error: "Request had insufficient authentication scopes"**
- Token doesn't have People API permissions
- Solution: Run `poetry run gwc-people auth` to re-authenticate

**Error: "No valid authentication token found"**
- No OAuth2 token exists
- Solution: Run `poetry run gwc-people auth` for initial authentication

---

## Tips & Tricks

**1. Always use `--output llm` for human review:**
```bash
poetry run gwc-people search "John" --output llm
```

**2. Use resource names for reliable lookups:**
```bash
# Store resource name from search
poetry run gwc-people search "John" --output json | jq -r '.[0].resourceName' > john_id.txt

# Use it later for exact lookups
poetry run gwc-people get "$(cat john_id.txt)" --output llm
```

**3. Search is prefix-based:**
```bash
# These work:
poetry run gwc-people search "John"      # Finds "John", "Johnny", etc.
poetry run gwc-people search "john@"     # Finds emails starting with john@

# This probably won't find anything:
poetry run gwc-people search "ohn"       # Won't find "John"
```

**4. Use email for more predictable results:**
```bash
# Name search may return multiple results
poetry run gwc-people search "John"

# Email search is more specific
poetry run gwc-people get "john@example.com"
```

**5. Export contacts for backup or integration:**
```bash
# Save all contacts as JSON
poetry run gwc-people list --limit 1000 --output json > my_contacts_backup.json

# Parse with jq
cat my_contacts_backup.json | jq '.[] | .email'
```

**6. Find contacts from specific organization:**
```bash
# Search by company name
poetry run gwc-people search "Acme" --output llm
```

**7. Integrate with calendar for finding attendees:**
```bash
# Search for contact to get email
poetry run gwc-people search "Alice" --output json | jq -r '.[0].email'

# Use email with gwc-cal to add to event
poetry run gwc-cal update <event-id> \
  --add-attendee "$(poetry run gwc-people search 'Alice' --output json | jq -r '.[0].email')"
```

---

## Common Workflows

### Find Someone's Contact Info
```bash
# Search by name
poetry run gwc-people search "John" --output llm

# Or by email
poetry run gwc-people get "john@example.com" --output llm
```

### Get Email for Calendar Integration
```bash
# Find contact
poetry run gwc-people search "Alice" --output json

# Get email address
poetry run gwc-people search "Alice" --output json | jq -r '.[0].email'
```

### Browse All Contacts
```bash
# Show first 50 sorted by name
poetry run gwc-people list --limit 50 --sort FIRST_NAME_ASCENDING --output llm

# Show next batch
poetry run gwc-people list --limit 50 --sort FIRST_NAME_ASCENDING --output llm
```

### Backup Contacts
```bash
# Export all contacts
poetry run gwc-people list --limit 1000 --output json > contacts_backup.json
```

### Find Recently Modified Contacts
```bash
# Show most recently updated contacts
poetry run gwc-people list --limit 20 --sort LAST_MODIFIED_DESCENDING --output llm
```

---
