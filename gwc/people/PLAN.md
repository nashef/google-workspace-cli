# gwc-people Implementation Plan

## Overview

This document outlines the 4-iteration plan for implementing the `gwc-people` CLI tool for managing Google Contacts. The tool will enable contact lookup, management, and integration with Calendar and Email tools.

---

## Iteration 1: Essential Features - Contact Discovery & Lookup

**Estimated Duration**: 5-7 days
**Focus**: Core contact lookup functionality needed by Calendar and Email tools

### Success Criteria

- ✅ OAuth2 authentication working with People API scopes
- ✅ Contact search by name/email working and tested
- ✅ Get individual contact details working
- ✅ List contacts with pagination working
- ✅ Output formatting supports unix/json/llm formats
- ✅ All commands tested with real Google Contacts
- ✅ Error handling for common cases (not found, auth failure, rate limits)

### Tasks

#### Authentication Setup (Day 1)
- [ ] Add `gwc.people` package structure with `__init__.py`, `__main__.py`, `operations.py`
- [ ] Add People API scopes to `shared/auth.py` constant
- [ ] Add `build_people_service()` function to operations.py
- [ ] Update pyproject.toml entry point: `gwc-people = "gwc.people:main"`
- [ ] Test OAuth flow works with People API scopes

#### Search & Lookup Operations (Days 2-3)
- [ ] Implement `search_contacts(query, page_size)` in operations.py
  - Validates query is not empty
  - Calls `people.searchContacts` endpoint
  - Returns list of matching contacts with names and emails
  - Handles pagination
- [ ] Implement `get_contact(resource_name_or_email)` in operations.py
  - Accepts resource name (e.g., "people/c123...") or email
  - Handles email lookup via search if needed
  - Returns full contact object
  - Handles etag for future updates
- [ ] Implement `list_contacts(page_size, sort_order, page_token)` in operations.py
  - Lists authenticated user's connections
  - Supports pagination
  - Supports sorting (LAST_MODIFIED, FIRST_NAME, LAST_NAME)
  - Returns contact summary list

#### CLI Implementation (Days 3-4)
- [ ] Create CLI group with auth, search, get, list commands
- [ ] Implement `auth` command (leverages existing auth infrastructure)
- [ ] Implement `search <query>` command
  - Option: `--format` (default: names,emails)
  - Option: `--limit` (default: 10, max: 30)
  - Option: `--output` (unix/json/llm)
- [ ] Implement `get <email-or-id>` command
  - Option: `--output` (unix/json/llm)
  - Option: `--fields` (default: minimal set)
- [ ] Implement `list` command
  - Option: `--limit` (default: 100)
  - Option: `--sort` (LAST_MODIFIED, FIRST_NAME, LAST_NAME)
  - Option: `--output` (unix/json/llm)
  - Handles pagination with prompt or auto-fetch

#### Output Formatting (Days 4-5)
- [ ] Add contact-specific field formatting to output.py
  - Contact card format (name, email, phone, organization)
  - Minimal format (name, email only)
  - Full format (all available fields)
- [ ] Test all three output formats (unix, json, llm)
- [ ] Verify output is properly formatted for shell piping

#### Error Handling & Testing (Days 5-7)
- [ ] Implement error handling for:
  - Authentication failures
  - Rate limiting (429)
  - Contact not found (404)
  - Workspace directory access denied
  - Invalid query format
- [ ] Add helpful error messages
- [ ] Manual testing:
  - Search for existing contacts
  - Get contact by email
  - List contacts with pagination
  - Test all output formats
  - Test error conditions
- [ ] Create test contacts for verification

### Deliverables

```
gwc-people search "john"
gwc-people search "john@example.com" --limit 5
gwc-people get "john@example.com"
gwc-people list --limit 50 --sort FIRST_NAME --output json
```

### Documentation

- [ ] Update README.md with gwc-people basics
- [ ] Add search and lookup examples
- [ ] Document required scopes

---

## Iteration 2: Core CRUD Operations - Full Contact Management

**Estimated Duration**: 5-7 days
**Focus**: Create, update, delete contacts with proper version control

### Success Criteria

- ✅ Create contacts with minimal and full field sets working
- ✅ Update contacts with etag conflict detection working
- ✅ Delete contacts working
- ✅ Local sync cache implementation working
- ✅ Incremental sync with tokens working
- ✅ All operations tested with real Google Contacts
- ✅ Transaction safety (no accidental overwrites)

### Tasks

#### Create Operations (Days 1-2)
- [ ] Implement `create_contact(name, email, phone, organization, address)` in operations.py
  - Handles singleton field constraints (only one name, birthday, etc.)
  - Validates required fields (at least name or email)
  - Returns created contact with resource name
  - Handles field mask properly
- [ ] Implement `create_contact_batch(contacts)` in operations.py
  - Accepts list of contact dicts
  - Creates up to 1000 in single request
  - Returns list of created contacts
- [ ] Implement CLI `create` command
  - Options: `--name`, `--email`, `--phone`, `--organization`, `--address`
  - Option: `--output` (unix/json/llm)
  - Validates at least name or email provided
- [ ] Test creating simple and complex contacts

#### Update Operations (Days 2-4)
- [ ] Implement `update_contact(resource_name, fields_to_update)` in operations.py
  - Fetches current etag
  - Updates specified fields
  - Handles etag mismatch errors gracefully (retry with fresh data)
  - Returns updated contact
  - Validates field updates for singleton constraints
- [ ] Implement `update_contact_batch(updates)` in operations.py
  - Updates up to 1000 contacts in single request
  - Returns success/failure for each
- [ ] Implement CLI `update <email-or-id>` command
  - Options: `--email`, `--phone`, `--organization`, `--address`, etc.
  - Option: `--output` (unix/json/llm)
  - Handles etag mismatch with user-friendly retry
- [ ] Test updating different field types
- [ ] Test conflict resolution on concurrent updates

#### Delete Operations (Days 3-4)
- [ ] Implement `delete_contact(resource_name)` in operations.py
  - Validates contact exists before delete (optional confirmation)
  - Handles 404 gracefully
- [ ] Implement `delete_contact_batch(resource_names)` in operations.py
  - Deletes up to 1000 contacts
- [ ] Implement CLI `delete <email-or-id>` command
  - Option: `--confirm` (require confirmation by default)
  - Provides clear deletion message
- [ ] Test deleting single and batch contacts

#### Local Caching with Sync (Days 4-7)
- [ ] Design SQLite schema for contact cache
  - Contacts table: resourceName, name, email, phone, organization, fullJson, lastModified
  - SyncToken table: lastSyncToken, lastSyncTime
  - Metadata table: schema version, last full sync
- [ ] Implement `ContactCache` class in operations.py
  - `init_cache()`: Create database if not exists
  - `get_from_cache(resource_name)`: Return cached contact or None
  - `cache_contact(contact)`: Store/update contact in cache
  - `cache_contacts(contacts)`: Batch cache
  - `clear_cache()`: Reset cache
  - `get_sync_token()`: Retrieve last sync token
  - `set_sync_token(token)`: Store sync token
- [ ] Implement incremental sync via sync tokens
  - `sync_contacts()`: Fetch only changed contacts since last sync
  - Updates cache incrementally
  - Handles sync token expiration (falls back to full list)
  - Runs on CLI startup if cache is older than 24 hours
- [ ] Implement CLI `cache` subcommand
  - `cache list`: Show cache stats
  - `cache clear`: Clear cache
  - `cache sync`: Force sync from server
- [ ] Add background sync option (can be deferred to iteration 4)

#### Manual Testing (Days 5-7)
- [ ] Create new contact via CLI
- [ ] Update contact with various fields
- [ ] Attempt concurrent updates (verify etag handling)
- [ ] Delete contact with confirmation
- [ ] Verify cache is populated and synced
- [ ] Test sync token refresh
- [ ] Verify batch operations work correctly

### Deliverables

```
gwc-people create --name "Jane Doe" --email "jane@example.com" --phone "+1234567890"
gwc-people update "jane@example.com" --phone "+0987654321"
gwc-people delete "jane@example.com" --confirm
gwc-people cache list
gwc-people cache sync
```

### Documentation

- [ ] Update README with create/update/delete examples
- [ ] Document etag handling and conflict resolution
- [ ] Document cache behavior and sync tokens
- [ ] Add troubleshooting section for sync issues

---

## Iteration 3: Advanced Features - Groups & Directory

**Estimated Duration**: 4-6 days
**Focus**: Contact groups and workspace directory search

### Success Criteria

- ✅ Contact groups list, get, create, update, delete working
- ✅ Add/remove members from groups working
- ✅ Directory search working (for Workspace users)
- ✅ Batch group operations working
- ✅ All tested with real data

### Tasks

#### Contact Groups Operations (Days 1-3)
- [ ] Implement `list_contact_groups()` in operations.py
  - Returns all contact groups (user and system)
  - Includes member count
- [ ] Implement `get_contact_group(group_id)` in operations.py
  - Returns single group with member list
- [ ] Implement `create_contact_group(name)` in operations.py
  - Validates unique group name
  - Handles 409 duplicate name error gracefully
- [ ] Implement `update_contact_group(group_id, name)` in operations.py
  - Updates group name
  - Validates new name is unique
- [ ] Implement `delete_contact_group(group_id)` in operations.py
  - Handles system group deletion (not allowed)
- [ ] Implement `add_group_member(group_id, resource_name)` in operations.py
  - Adds single member to group
  - Handles already-member case
- [ ] Implement `add_group_members(group_id, resource_names)` in operations.py
  - Adds multiple members in single request
- [ ] Implement `remove_group_member(group_id, resource_name)` in operations.py
  - Removes member from group

#### Groups CLI (Days 2-3)
- [ ] Implement CLI `groups` subcommand
  - `groups list`: List all groups
  - `groups get <group-id>`: Get group details
  - `groups create --name <name>`: Create group
  - `groups update <group-id> --name <new-name>`: Rename group
  - `groups delete <group-id>`: Delete group
  - `groups add-member <group-id> <email>`: Add member
  - `groups remove-member <group-id> <email>`: Remove member
- [ ] Add `--output` option to all read commands
- [ ] Add `--confirm` to delete command

#### Directory Search (Days 3-4)
- [ ] Implement `search_directory(query, page_size)` in operations.py
  - Note: Requires Workspace and admin setup
  - Searches domain directory
  - Returns names, emails, jobTitle, department
- [ ] Implement `list_directory(page_size)` in operations.py
  - Lists all domain profiles
- [ ] Implement CLI `directory` subcommand
  - `directory search <query>`: Search domain
  - `directory list`: List all profiles
  - Add `--output` option
  - Handle Workspace-only feature gracefully

#### Batch Group Operations (Days 4-5)
- [ ] Implement `batch_add_to_group(group_id, email_list)` in operations.py
  - Adds multiple members efficiently
- [ ] Implement `batch_remove_from_group(group_id, email_list)` in operations.py
  - Removes multiple members efficiently

#### Testing (Days 5-6)
- [ ] Create test groups
- [ ] Add/remove members
- [ ] Test batch operations
- [ ] Test directory search (if Workspace available)
- [ ] Test error cases (duplicate name, system group delete, etc.)

### Deliverables

```
gwc-people groups list
gwc-people groups create --name "Team"
gwc-people groups add-member "Team" "john@example.com"
gwc-people directory search "john"
```

### Documentation

- [ ] Add groups management examples
- [ ] Document directory search requirements
- [ ] Note Workspace-only features

---

## Iteration 4: Integration & Polish - Calendar & Email Integration

**Estimated Duration**: 5-7 days
**Focus**: Seamless integration with Calendar and Email CLIs

### Success Criteria

- ✅ Calendar CLI can use People API for attendee lookup and autocomplete
- ✅ Email CLI can use People API for recipient lookup
- ✅ Contact import/export working
- ✅ Advanced search filters working
- ✅ Performance optimizations (warmup, caching) working
- ✅ Documentation complete
- ✅ All four CLI tools working together seamlessly

### Tasks

#### Calendar Integration (Days 1-2)
- [ ] Create `get_contact_email_by_name(name)` helper in operations.py
  - Searches for contact, returns email
  - Returns None if not found
- [ ] Create `get_contact_emails_by_group(group_name)` helper
  - Returns all email addresses in group
  - Useful for bulk invitations
- [ ] Update Calendar CLI to use People API
  - `gwc-cal create --attendee <name>` searches People API
  - `gwc-cal create --attendee-group <group-name>` adds group members
  - Validates emails found before creating event
- [ ] Test Calendar + People API integration

#### Email Integration (Days 2-3)
- [ ] Create `get_contact_by_email(email)` helper in operations.py
- [ ] Update Email CLI to use People API (when implemented)
  - `gwc-mail send --to <name>` searches People API
  - Shows email options if multiple matches
  - Autocomplete for recipient field
- [ ] Test Email + People API integration

#### Import/Export (Days 3-4)
- [ ] Implement `export_contacts(format)` in operations.py
  - Supports CSV format: name,email,phone,organization
  - Supports JSON format: full contact objects
  - Supports vCard format (if time permits)
- [ ] Implement `import_contacts(file_path, format)` in operations.py
  - Parses CSV/JSON/vCard
  - Creates contacts via batch operation
  - Reports success/failure
- [ ] Implement CLI `import` and `export` commands
  - `import <file>`: Import from file (auto-detect format)
  - `import <file> --format csv/json/vcard`: Explicit format
  - `export [--file <path>] [--format csv/json]`: Export contacts

#### Advanced Search (Days 4-5)
- [ ] Implement filtered search:
  - `search --name <pattern>`: Name only
  - `search --email <pattern>`: Email only
  - `search --phone <pattern>`: Phone only
  - `search --org <pattern>`: Organization only
- [ ] Implement sorting options:
  - `--sort name/modified/email`
- [ ] Add filter chaining examples

#### Performance Optimizations (Days 5-6)
- [ ] Implement warmup search on first use
  - Calls search with empty query to warm cache
  - Only on first search per session
- [ ] Implement contact photo caching
  - Download and cache profile photos (optional)
- [ ] Profile CLI performance
  - Ensure search is < 1 second
  - Ensure list is < 2 seconds

#### Comprehensive Testing (Days 6-7)
- [ ] Test Calendar + People integration
- [ ] Test Email + People integration (when available)
- [ ] Test import/export roundtrip
- [ ] Test all search variants
- [ ] Test performance (search speed, cache behavior)
- [ ] Test error cases and edge cases

#### Documentation & Polish (Days 7)
- [ ] Write comprehensive README for gwc-people
  - Overview
  - Installation
  - Quick start
  - Integration with Calendar/Email
  - Advanced features
  - API reference
- [ ] Add examples for all major commands
- [ ] Create troubleshooting guide
- [ ] Document cache behavior
- [ ] Add performance tuning tips

### Deliverables

```
# Calendar integration
gwc-cal create --time "2pm tomorrow" --subject "Team Meeting" \
  --attendee "john"  # Searches People API

# Email integration
gwc-mail send --to "jane" --subject "Hello" --body "Message"

# Import/Export
gwc-people import contacts.csv
gwc-people export --file backup.json --format json

# Advanced search
gwc-people search --email "@company.com" --sort name
```

### Final Documentation

- [ ] Complete README.md
- [ ] API reference for all commands
- [ ] Troubleshooting guide
- [ ] Performance tuning guide
- [ ] Integration guide for Calendar/Email

---

## Cross-Cutting Concerns

### Error Handling Strategy

Throughout all iterations, consistent error handling:

```python
try:
    # API call
except HttpError as e:
    if e.resp.status == 404:
        raise ValidationError(f"Contact not found: {email}")
    elif e.resp.status == 409:
        raise ValidationError(f"Duplicate group name: {name}")
    elif e.resp.status == 429:
        raise APIError("Rate limited. Please try again in a moment.")
    else:
        raise APIError(f"People API error: {e}")
except AuthenticationError:
    raise  # User needs to re-authenticate
```

### Testing Strategy

- Unit tests for operations.py functions
- Integration tests with real Google Contacts (sandbox account)
- CLI tests for each command
- Manual testing with user's actual contacts

### Documentation Strategy

- Inline code comments for complex logic
- Docstrings for all public functions
- README with examples
- PEOPLE_API.md for API reference
- PLAN.md (this file) for development roadmap

### Performance Targets

- Search: < 1 second response
- List: < 2 seconds for first 100 contacts
- Create: < 1 second
- Update: < 1 second
- Delete: < 1 second
- Cache sync: < 5 seconds

---

## Success Metrics

### Iteration 1 Success
- All search/lookup commands working
- All output formats functional
- Zero unhandled exceptions in typical usage

### Iteration 2 Success
- Create/update/delete operations working
- Cache syncing reliably
- No data loss or corruption

### Iteration 3 Success
- Groups management complete
- Directory search working (Workspace users)
- All edge cases handled

### Iteration 4 Success
- Calendar + People integration working seamlessly
- Email + People integration ready
- Import/export tested with real data
- Performance targets met
- Comprehensive documentation complete

---

## Timeline

```
Week 1: Iteration 1 (Essential Features)
Week 2: Iteration 2 (CRUD Operations)
Week 3: Iteration 3 (Groups & Directory)
Week 4: Iteration 4 (Integration & Polish)
```

Total estimated effort: **3-4 weeks**

## Dependency Order

1. Iteration 1 must complete before Iteration 2 (need working API calls)
2. Iteration 2 must complete before Iteration 4 (need full CRUD for integration)
3. Iteration 3 can run in parallel with Iteration 2 (independent features)
4. Iteration 4 requires Iterations 1-3 complete

## Decision Points

### Should we implement sync tokens immediately?
**Decision**: Defer to Iteration 2. Iteration 1 focuses on core functionality; caching is optimization.

### Should we support vCard import/export?
**Decision**: Start with CSV/JSON in Iteration 4. Add vCard support in follow-up if needed.

### Should we implement directory features even without Workspace?
**Decision**: Yes, with clear error message explaining Workspace requirement.

### Should we optimize for large contact lists (10k+ contacts)?
**Decision**: Yes, via caching and pagination, built into Iterations 1-2.
