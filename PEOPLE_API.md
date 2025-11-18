# Google People API - Comprehensive Feature Inventory

## Executive Summary

The Google People API provides programmatic access to Google Contacts and directory information. It enables reading, creating, updating, and deleting contacts, managing contact groups, searching contacts and directories, and accessing profile information. The API consolidates data from multiple sources including public profiles, private profiles, contacts, and Google Workspace domain directories.

**Base URL**: `https://people.googleapis.com`

---

## 1. API Overview

### Core Capabilities

- **Contact Management**: Full CRUD operations on contacts (create, read, update, delete)
- **Contact Groups**: Organize contacts into user-defined or system groups
- **Directory Access**: Search and list Google Workspace domain profiles (requires admin configuration)
- **Profile Information**: Access authenticated user and connection profiles
- **Other Contacts**: Manage auto-populated contacts not in main contact groups
- **Batch Operations**: Perform up to 1000 operations in a single HTTP request
- **Search**: Prefix-based search across names, emails, phone numbers, and organizations
- **Sync**: Track changes incrementally using sync tokens

### Data Source Merging

The API merges information from multiple sources based on OAuth scopes:
- Public Google profile data (always available)
- Private profile information (requires profile scopes)
- User's contacts (requires contacts scope)
- Workspace domain data (requires directory scope + admin setup)

---

## 2. Authentication & OAuth Scopes

### Required Scopes

| Scope | Access Level | Description |
|-------|-------------|-------------|
| `https://www.googleapis.com/auth/contacts` | Read/Write | Full access: create, read, update, delete contacts |
| `https://www.googleapis.com/auth/contacts.readonly` | Read-only | View contacts only, no modifications |
| `https://www.googleapis.com/auth/userinfo.profile` | Read-only | Access user profile information |
| `https://www.googleapis.com/auth/userinfo.email` | Read-only | Access primary Google Account email |

**Note**: Directory access requires additional admin configuration beyond just OAuth scopes.

### Authentication Flow

- Uses standard OAuth 2.0 flow
- Credentials stored locally in `token.json` for persistent access
- Browser-based authorization on first run
- Desktop application flow for CLI tools

---

## 3. Main API Resources

### 3.1 People Resource (`/v1/people`)

Core contact management operations.

#### Methods

| Method | HTTP | Endpoint | Description |
|--------|------|----------|-------------|
| **get** | GET | `/v1/people/{resourceName}` | Get information about a person |
| **getBatchGet** | GET | `/v1/people:batchGet` | Get information about multiple people |
| **createContact** | POST | `/v1/people:createContact` | Create a new contact |
| **updateContact** | PATCH | `/v1/people/{resourceName}:updateContact` | Update existing contact |
| **deleteContact** | DELETE | `/v1/people/{resourceName}:deleteContact` | Delete a contact |
| **batchCreateContacts** | POST | `/v1/people:batchCreateContacts` | Create multiple contacts at once |
| **batchUpdateContacts** | POST | `/v1/people:batchUpdateContacts` | Update multiple contacts |
| **batchDeleteContacts** | POST | `/v1/people:batchDeleteContacts` | Delete multiple contacts |
| **searchContacts** | GET | `/v1/people:searchContacts` | Search user's contacts |
| **searchDirectoryPeople** | GET | `/v1/people:searchDirectoryPeople` | Search domain directory |
| **listDirectoryPeople** | GET | `/v1/people:listDirectoryPeople` | List domain directory profiles |
| **updateContactPhoto** | PATCH | `/v1/people/{resourceName}:updateContactPhoto` | Update contact's photo |
| **deleteContactPhoto** | DELETE | `/v1/people/{resourceName}:deleteContactPhoto` | Delete contact's photo |

#### Key Parameters

**personFields** (required for most operations): Field mask specifying which fields to return. Available fields:

```
addresses, ageRanges, biographies, birthdays, calendarUrls, clientData,
coverPhotos, emailAddresses, events, externalIds, genders, imClients,
interests, locales, locations, memberships, metadata, miscKeywords,
names, nicknames, occupations, organizations, phoneNumbers, photos,
relations, sipAddresses, skills, urls, userDefined
```

**Singleton Fields** (only one value allowed per contact source):
- biographies
- birthdays
- genders
- names

Attempting to set multiple values for these fields returns a 400 error.

### 3.2 People.Connections Resource (`/v1/people/connections`)

Access the authenticated user's contact network.

#### Methods

| Method | HTTP | Description |
|--------|------|-------------|
| **list** | GET | List authenticated user's contacts |

#### List Parameters

- `pageSize`: 1-1000 (default: 100)
- `pageToken`: For pagination
- `sortOrder`: LAST_MODIFIED_ASCENDING/DESCENDING, FIRST_NAME_ASCENDING, LAST_NAME_ASCENDING
- `syncToken`: For incremental sync
- `requestSyncToken`: Request sync token in response
- `personFields`: Required field mask
- `sources[]`: Filter by source type

**Important**: When paginating, all parameters must match the first call that provided the page token. Sorting is unavailable when using sync requests.

### 3.3 ContactGroups Resource (`/v1/contactGroups`)

Manage contact groups.

#### Methods

| Method | HTTP | Description |
|--------|------|-------------|
| **list** | GET | List all contact groups |
| **get** | GET | Get specific contact group |
| **batchGet** | GET | Get multiple contact groups |
| **create** | POST | Create new contact group |
| **update** | PUT | Update contact group name |
| **delete** | DELETE | Delete contact group |

#### Group Types

- **USER_CONTACT_GROUP**: User-defined groups
- **SYSTEM_CONTACT_GROUP**: System-defined groups (translated to user's locale)

**Constraint**: Group names must be unique. Duplicate names return HTTP 409 error.

### 3.4 ContactGroups.Members Resource

Manage contact group membership.

#### Methods

| Method | HTTP | Description |
|--------|------|-------------|
| **modify** | POST | Add/remove members from contact group |

#### Fields

- `memberResourceNames[]`: Current members (limited by maxMembers parameter)
- `memberCount`: Total member count

### 3.5 OtherContacts Resource (`/v1/otherContacts`)

Manage auto-populated contacts not in contact groups.

#### Methods

| Method | HTTP | Description |
|--------|------|-------------|
| **list** | GET | List all other contacts |
| **search** | GET | Search other contacts |
| **copyOtherContactToMyContactsGroup** | POST | Copy to main contacts |

**Other Contacts** are contacts that exist outside traditional contact groups (possibly from email interactions). They can be promoted to regular contacts using the copy operation.

---

## 4. Search Capabilities

### 4.1 Contact Search

**Endpoint**: `people.searchContacts`

**Search Scope**: Searches the following fields in contacts:
- names
- nicknames
- emailAddresses
- phoneNumbers
- organizations

**Query Mechanism**: Prefix phrase matching
- Matches beginning of words only
- Example: "foo name" matches "f", "fo", "foo", "foo n", "nam"
- Does NOT match: "oo n" (substring not at beginning)

**Parameters**:
- `query` (required): Plain-text search term
- `pageSize` (optional): Default 10, max 30
- `readMask` (required): Fields to return
- `sources` (optional): Filter by source type

**Important**: Send a warmup request with empty query first to update cache for optimal performance.

### 4.2 Directory Search

**Endpoint**: `people.searchDirectoryPeople`

Searches Google Workspace domain profiles and contacts.

**Requirements**:
- Admin must enable external contact/profile sharing
- Appropriate directory scope
- Google Workspace account

**Limitations**:
- Propagation delay of several minutes for changes
- Not intended for read-after-write scenarios
- Sync tokens can expire requiring full resync

---

## 5. Batch Operations

### Capabilities

Combine up to **1000 API calls** into a single HTTP request using `multipart/mixed` content type.

### Supported Operations

- Batch create contacts
- Batch update contacts
- Batch delete contacts
- Batch get contact groups
- Any combination of GET requests

### Key Limitations

1. **No guaranteed order**: Server may execute calls in any order
2. **Quota counting**: Each call in batch counts separately (n requests = n quota usage)
3. **Sequential dependencies**: If order matters, send separate requests
4. **Header inheritance**: Outer headers apply to all inner calls unless overridden

### Best Practices

- Use for initial data uploads with large datasets
- Use for syncing offline changes
- Include `Content-ID` headers for tracking
- Send sequential requests separately if order matters

---

## 6. Create/Update Operations

### Creating Contacts

**Endpoint**: `POST /v1/people:createContact`

**Required Parameters**:
- `personFields`: Field mask for response

**Request Body**: Person object with desired fields

**Best Practices**:
- Send mutate requests sequentially for same user to avoid latency
- Respect singleton field constraints (one value only for biographies, birthdays, genders, names)

### Updating Contacts

**Endpoint**: `PATCH /v1/people/{resourceName}:updateContact`

**Required Parameters**:
- `updatePersonFields`: Field mask specifying which fields to update
- `person.metadata.sources.etag`: Version control

**Update Mechanism**: Wholesale replacement (not incremental)
- All specified fields are completely replaced
- Must include current etag to prevent conflicts
- Returns 400 error with `failedPrecondition` if etag doesn't match

**Best Practices**:
- Use etag from previous response for sequential updates
- Send mutate requests sequentially

---

## 7. Integration Recommendations for Calendar & Email CLI

### Most Useful Features for Integration

#### Priority 1: Core Contact Lookup
Essential for calendar meeting attendees and email recipients.

**Implement First**:
1. **Search contacts by name/email** (`searchContacts`)
   - For autocomplete when adding meeting attendees
   - For email address lookup when composing
   - Returns: names, emailAddresses, phoneNumbers

2. **Get contact details** (`people.get`)
   - Retrieve full contact information
   - Field mask: names, emailAddresses, phoneNumbers, organizations

3. **List connections** (`people.connections.list`)
   - Show all contacts for selection
   - Pagination support for large contact lists
   - Sort by name for user-friendly display

#### Priority 2: Contact Management
For maintaining contacts while using calendar/email.

4. **Create contact** (`createContact`)
   - Add new contacts encountered in meetings/emails
   - Minimal fields: name, email

5. **Update contact** (`updateContact`)
   - Update contact info after meetings
   - Add phone numbers from email signatures

#### Priority 3: Advanced Features
Nice-to-have for power users.

6. **Contact groups** (`contactGroups`)
   - Filter attendees by group (e.g., "Team", "Clients")
   - Bulk-add group members to meetings

7. **Directory search** (`searchDirectoryPeople`)
   - For Google Workspace users
   - Search company directory for meeting attendees
   - Returns: names, emailAddresses, jobTitle, department

### Recommended CLI Design

#### gwc-people Basic Commands

```bash
# Search contacts
gwc-people search "john smith"
gwc-people search --email "john@example.com"

# Get contact details
gwc-people get <resource-name>
gwc-people get --email "john@example.com"

# List contacts
gwc-people list [--limit 100] [--sort name]

# Create contact
gwc-people create --name "John Smith" --email "john@example.com" --phone "+1234567890"

# Update contact
gwc-people update <resource-name> --email "newemail@example.com"

# Delete contact
gwc-people delete <resource-name>

# Contact groups
gwc-people groups list
gwc-people groups create --name "Team"
gwc-people groups add-member <group-id> <contact-resource-name>

# Directory search (Workspace only)
gwc-people directory search "john"
```

#### Integration with Calendar

```bash
# Use contact search in calendar
gwc-cal create --time "2pm tomorrow" --subject "Team Meeting" \
  --attendee $(gwc-people search --email "john@example.com" --format email)

# Or with autocomplete
gwc-cal create --time "2pm tomorrow" --subject "Team Meeting" \
  --attendee john@  # triggers contact search autocomplete
```

#### Integration with Email

```bash
# Use contact search in email
gwc-mail send --to $(gwc-people search "john smith" --format email) \
  --subject "Hello" --body "Message"

# Add contact from email
gwc-mail show <message-id> | gwc-people create-from-email
```

### Data Caching Strategy

For CLI performance:

1. **Cache contact list locally** (refresh daily or on-demand)
   - Use sync tokens for incremental updates
   - Store in SQLite database: `~/.config/gwc/contacts.db`

2. **Warmup cache on first search**
   - Send empty query to searchContacts endpoint
   - Improves subsequent search performance

3. **Cache contact groups**
   - Infrequently changed
   - Refresh on create/update/delete

### Error Handling

Key errors to handle:

1. **400 - Duplicate singleton fields**
   - Multiple values for name, birthday, etc.
   - Show clear error message about which field

2. **400 - Failed precondition (etag mismatch)**
   - Contact changed since last read
   - Re-fetch and retry update

3. **404 - Resource not found**
   - Contact deleted
   - Clear from cache

4. **409 - Duplicate group name**
   - Group name already exists
   - Suggest alternative or show existing group

5. **429 - Rate limit**
   - Implement exponential backoff
   - Consider batch operations for bulk actions

---

## 8. Field Reference

### Complete Field List

All available person fields that can be requested via `personFields` parameter:

| Field | Type | Description |
|-------|------|-------------|
| addresses | Multiple | Physical addresses |
| ageRanges | Multiple | Age range (e.g., 18-20, 21-24) |
| biographies | Singleton | About/bio text |
| birthdays | Singleton | Birthday dates |
| calendarUrls | Multiple | Calendar URLs |
| clientData | Multiple | Client-specific data |
| coverPhotos | Multiple | Cover photos |
| emailAddresses | Multiple | Email addresses |
| events | Multiple | Important dates/events |
| externalIds | Multiple | External identifiers |
| genders | Singleton | Gender |
| imClients | Multiple | IM handles |
| interests | Multiple | Interests/hobbies |
| locales | Multiple | Locale preferences |
| locations | Multiple | Location |
| memberships | Multiple | Group memberships |
| metadata | - | Resource metadata |
| miscKeywords | Multiple | Miscellaneous keywords |
| names | Singleton | Name (given, family, display) |
| nicknames | Multiple | Nicknames |
| occupations | Multiple | Job titles/occupations |
| organizations | Multiple | Organizations/employers |
| phoneNumbers | Multiple | Phone numbers |
| photos | Multiple | Photos |
| relations | Multiple | Relationships |
| sipAddresses | Multiple | SIP addresses |
| skills | Multiple | Skills |
| urls | Multiple | URLs |
| userDefined | Multiple | Custom fields |

### Common Field Combinations

**Minimal contact info**:
```
names,emailAddresses
```

**Contact card**:
```
names,emailAddresses,phoneNumbers,organizations,photos
```

**Full contact**:
```
addresses,biographies,birthdays,emailAddresses,events,genders,names,
nicknames,occupations,organizations,phoneNumbers,photos,urls
```

**Calendar integration**:
```
names,emailAddresses,phoneNumbers,organizations
```

---

## 9. Quotas & Limits

Based on documentation references:

- **Batch operations**: Maximum 1000 calls per request
- **Search results**: Default 10, maximum 30 per page
- **Connections list**: Default 100, maximum 1000 per page
- **Sequential mutations**: Required for same user to avoid latency
- **Sync token expiration**: Tokens can expire, requiring full resync
- **Directory propagation**: Several minutes delay for changes

**Note**: Specific quota limits (requests per day, per minute) are not detailed in the documentation reviewed but follow standard Google API quotas.

---

## 10. Python Implementation Notes

### Minimal Working Example

From the Python quickstart:

```python
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import os.path

SCOPES = ['https://www.googleapis.com/auth/contacts.readonly']

def get_credentials():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return creds

def list_contacts():
    creds = get_credentials()
    service = build('people', 'v1', credentials=creds)

    results = service.people().connections().list(
        resourceName='people/me',
        pageSize=10,
        personFields='names,emailAddresses'
    ).execute()

    connections = results.get('connections', [])
    for person in connections:
        names = person.get('names', [])
        emails = person.get('emailAddresses', [])
        if names:
            name = names[0].get('displayName')
            email = emails[0].get('value') if emails else 'No email'
            print(f"{name}: {email}")
```

### Library Requirements

```toml
[tool.poetry.dependencies]
google-auth = "^2.0.0"
google-auth-oauthlib = "^1.0.0"
google-auth-httplib2 = "^0.1.0"
google-api-python-client = "^2.0.0"
```

---

## 11. Summary & Recommendations

### API Strengths

✅ Comprehensive contact data access
✅ Powerful search with prefix matching
✅ Batch operations for efficiency
✅ Incremental sync capabilities
✅ Directory integration for Workspace
✅ Well-structured REST API
✅ Good Python library support

### API Limitations

⚠️ Warmup required for optimal search performance
⚠️ Directory features require admin configuration
⚠️ Sequential mutations required to avoid latency
⚠️ Etag management needed for updates
⚠️ Limited search (prefix only, no fuzzy matching)
⚠️ Sync tokens can expire

### Implementation Priority for gwc-people

**Phase 1 - Essential (Week 1)**:
1. OAuth authentication setup
2. Search contacts by name/email
3. Get contact details
4. List contacts with pagination

**Phase 2 - Core Features (Week 2)**:
5. Create contact
6. Update contact
7. Delete contact
8. Local caching with sync tokens

**Phase 3 - Advanced (Week 3)**:
9. Contact groups management
10. Batch operations
11. Directory search (Workspace)
12. Photo management

**Phase 4 - Integration (Week 4)**:
13. Calendar integration helpers
14. Email integration helpers
15. Contact import/export
16. Advanced search filters

### Key Integration Points

**For gwc-cal**:
- Contact search for meeting attendees
- Email validation and autocomplete
- Contact groups for bulk invitations

**For gwc-mail**:
- Email address lookup
- Contact autocomplete in compose
- Add contacts from received emails

**Shared Infrastructure**:
- Common contact cache database
- Unified search interface
- Shared OAuth credentials
