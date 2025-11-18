# Gmail API CLI Implementation Plan

**Status**: Design & Planning Phase
**Target**: Comprehensive Gmail management via CLI
**Building on**: Calendar API (Phase 1), People API (Iterations 1-4)

## Executive Summary

This document outlines a comprehensive implementation plan for `gwc-email`, a command-line interface to the Gmail API. The plan is designed to be incremental, testable, and production-ready at each phase. We'll implement core message management first, then layer in more sophisticated features.

## API Overview

### Resource Model

Gmail organizes data around four core entities:

1. **Messages** - Individual emails with full headers, body, attachments
2. **Threads** - Conversation chains (groups of related messages)
3. **Labels** - Organization system with system labels (INBOX, SENT, DRAFT, SPAM, TRASH) and user-created labels
4. **Drafts** - Unsent messages that can be edited before sending

### Key Characteristics

- **RESTful**: Standard HTTP methods (GET, POST, PUT, DELETE)
- **Large payloads**: Messages can be large; API supports `fields` parameter for selective retrieval
- **Label-based organization**: Unlike folders, messages can have multiple labels
- **Thread-based conversations**: Messages grouped by conversation ID
- **No direct folder structure**: Everything is labels; inbox is just a label
- **Rate limited**: 250 MB/day quota, 15,000 requests/day per user
- **Pagination**: Results returned with `nextPageToken` for continuation

## Implementation Phases

### Phase 1: Core Message Management (Priority: CRITICAL)

**Goal**: Basic email reading and searching capabilities

**Commands**:
```
gwc-email list           # List messages in a label/folder
gwc-email get <id>       # Get full message details
gwc-email search <query> # Search messages (full Gmail search syntax)
gwc-email labels list    # List available labels
gwc-email labels get     # Get label details
```

**Key Operations**:
- `users.messages().list()` - List messages with pagination
- `users.messages().get()` - Get individual message details
- `users.messages().list(q=query)` - Search using Gmail's search syntax
- `users.labels().list()` - Enumerate all labels
- `users.labels().get()` - Get label properties

**Design Decisions**:

1. **Message Formatting**: Return structured message objects with:
   - `id`: Message ID (required for further operations)
   - `threadId`: Conversation ID
   - `labelIds`: Labels applied
   - `snippet`: Preview text
   - `internalDate`: Message date (milliseconds since epoch)
   - `headers`: Key headers (From, To, Subject, Date)
   - `payload`: Message body with MIME structure

2. **Output Formats**: Support all three output modes
   - `--output unix`: Tab-separated (id, from, to, subject, date)
   - `--output json`: Full message objects
   - `--output llm`: Human-readable formatted display

3. **Search Integration**: Use Gmail's native search syntax
   - Examples: `from:user@example.com`, `subject:urgent`, `before:2025-01-01`, `has:attachment`
   - More powerful than API-level filtering

4. **Label Organization**:
   - Map system labels (INBOX, SENT_MAIL, DRAFT, SPAM, TRASH)
   - Support user-created labels
   - Show label hierarchy in output

**Implementation Details**:

```python
# gwc/email/operations.py
def list_messages(label: str = "INBOX", query: str = "", max_results: int = 10) -> List[Dict[str, Any]]:
    """List messages from a label with optional search query"""

def get_message(message_id: str, format: str = "full") -> Dict[str, Any]:
    """Get full message details with headers and body"""

def search_messages(query: str, max_results: int = 10) -> List[Dict[str, Any]]:
    """Search messages using Gmail search syntax"""

def get_message_headers(message_id: str) -> Dict[str, str]:
    """Extract standard headers (From, To, Subject, Date, Cc, Bcc)"""

def list_labels() -> List[Dict[str, Any]]:
    """List all labels with properties"""

def get_label(label_id: str) -> Dict[str, Any]:
    """Get label details"""
```

**Testing Strategy**:
- Unit tests for message parsing (MIME handling, header extraction)
- Integration tests for label listing
- Search functionality tests with various query types
- Output format validation (unix, json, llm)

**CLI Commands** (`gwc/email/__main__.py`):
```python
@main.command()
@click.option('--label', default='INBOX', help='Label to list (default: INBOX)')
@click.option('--limit', default=10, type=int, help='Max results')
@click.option('--query', default='', help='Search query')
@click.option('--output', type=click.Choice(['unix', 'json', 'llm']), default='unix')
def list(label, limit, query, output):
    """List messages from a label"""
```

**Documentation Requirements** (Phase 1 Docs):
- Phase 1 quick start (5 minutes)
- Command reference for list, get, search
- Common search queries guide
- Label organization explanation

---

### Phase 2: Message Composition & Sending (Priority: HIGH)

**Goal**: Create, modify, and send messages programmatically

**Commands**:
```
gwc-email draft create    # Create draft
gwc-email draft send      # Send draft
gwc-email draft list      # List drafts
gwc-email send            # Send message directly (no draft)
gwc-email reply           # Reply to message
gwc-email forward         # Forward message
```

**Key Operations**:
- `users.drafts().create()` - Create new draft
- `users.drafts().send()` - Send existing draft
- `users.messages().send()` - Send message directly
- `users.messages().get(threadId)` - Get thread for reply context

**Design Decisions**:

1. **Message Format**: Support MIME composition
   - Plain text or HTML body
   - Recipients: To, Cc, Bcc
   - Subject and headers
   - Attachments (file paths)

2. **Draft vs Direct Send**:
   - `draft create`: Allows editing before sending
   - `send`: One-shot sending without draft

3. **Reply/Forward Context**:
   - Auto-populate message ID and thread ID
   - Use original subject with "Re:" prefix
   - Quote original message body

**Implementation Details**:

```python
def create_message(to: str, subject: str, body: str, cc: str = "",
                   bcc: str = "", attachments: List[str] = None) -> Dict[str, Any]:
    """Create message object (for drafts or sending)"""

def create_draft(to: str, subject: str, body: str, **kwargs) -> Dict[str, Any]:
    """Create and store draft message"""

def send_message(to: str, subject: str, body: str, **kwargs) -> str:
    """Send message directly (returns message ID)"""

def send_draft(draft_id: str) -> str:
    """Send existing draft (returns message ID)"""

def list_drafts(max_results: int = 10) -> List[Dict[str, Any]]:
    """List all drafts"""

def reply_to_message(message_id: str, body: str, all_recipients: bool = False) -> str:
    """Reply to message in thread (returns message ID)"""

def forward_message(message_id: str, to: str, subject: str = "") -> str:
    """Forward message to new recipient"""
```

**Attachment Handling**:
- Support file path argument
- Base64 encode file content
- MIME type detection
- File size warnings (Gmail has limits)

**Testing Strategy**:
- Mock MIME message construction
- Test draft creation and modification
- Test send with various recipient combinations
- Verify attachments are properly encoded
- Thread context retrieval

**CLI Commands**:
```python
@main.command()
@click.option('--to', required=True, help='Recipient email')
@click.option('--subject', required=True, help='Message subject')
@click.option('--body', required=True, help='Message body')
@click.option('--cc', default='', help='CC recipients')
@click.option('--bcc', default='', help='BCC recipients')
@click.option('--attachments', multiple=True, help='File paths to attach')
def send(to, subject, body, cc, bcc, attachments):
    """Send message directly"""
```

---

### Phase 3: Message Organization & Manipulation (Priority: HIGH)

**Goal**: Modify messages, manage labels, organize mailbox

**Commands**:
```
gwc-email modify        # Add/remove labels
gwc-email delete        # Delete messages
gwc-email mark-read     # Mark as read/unread
gwc-email archive       # Archive messages
gwc-email spam          # Mark/unmark as spam
gwc-email labels create # Create custom label
gwc-email labels update # Update label
gwc-email labels delete # Delete label
```

**Key Operations**:
- `users.messages().modify()` - Add/remove labels
- `users.messages().batchModify()` - Modify multiple messages
- `users.messages().delete()` - Delete message
- `users.messages().batchDelete()` - Delete multiple messages
- `users.messages().trash()` / `untrash()` - Trash/restore
- `users.labels().create()` - Create label
- `users.labels().update()` / `patch()` - Update label

**Design Decisions**:

1. **Label Operations**:
   - Support add/remove by label name or ID
   - Special labels: INBOX, SENT_MAIL, DRAFT, SPAM, TRASH
   - Show current labels before modification

2. **Batch Operations**:
   - Support multiple messages in one API call
   - More efficient than individual operations
   - Return modification summary

3. **Read Status**:
   - Read/unread is implemented via UNREAD label
   - Track read/unread status in list output

**Implementation Details**:

```python
def modify_message(message_id: str, add_labels: List[str] = None,
                   remove_labels: List[str] = None) -> Dict[str, Any]:
    """Add/remove labels from message"""

def batch_modify_messages(message_ids: List[str], add_labels: List[str] = None,
                         remove_labels: List[str] = None) -> Dict[str, Any]:
    """Modify multiple messages"""

def mark_read(message_id: str, read: bool = True) -> Dict[str, Any]:
    """Mark message as read or unread"""

def delete_message(message_id: str) -> None:
    """Delete message permanently"""

def batch_delete_messages(message_ids: List[str]) -> Dict[str, int]:
    """Delete multiple messages"""

def archive_message(message_id: str) -> Dict[str, Any]:
    """Remove from INBOX (archive)"""

def create_label(name: str, label_list_visibility: str = "labelShow") -> Dict[str, Any]:
    """Create custom label"""
```

**Testing Strategy**:
- Test label add/remove operations
- Verify batch operations work correctly
- Test read/unread status changes
- Test delete and restore workflows
- Custom label creation and management

---

### Phase 4: Advanced Features (Priority: MEDIUM)

**Goal**: Sophisticated message handling and automation

**Commands**:
```
gwc-email filters list    # List message filters
gwc-email filters create  # Create filter rule
gwc-email settings        # Show email settings
gwc-email signature       # Manage signature
gwc-email forward         # Manage forwarding
gwc-email delegates       # Manage account access
gwc-email threads         # Thread operations
gwc-email watch          # Set up push notifications
```

**Key Operations**:
- `users.settings().getLanguage()`, `getVacation()`, etc. - Settings access
- `users.settings().sendAs()` - Manage send-as aliases
- `users.settings().filters()` - Create/list filters
- `users.threads()` - Thread-level operations
- `users.watch()` - Push notifications

**Design Decisions**:

1. **Filters**: Gmail's server-side filtering
   - Query-based (same search syntax as messages)
   - Actions: apply labels, archive, delete, star, etc.

2. **Settings**: Account-wide configuration
   - Language preference
   - Vacation responder
   - Signature
   - Forwarding addresses

3. **Thread Operations**:
   - List messages in thread
   - Modify entire thread at once
   - Delete conversation

**Implementation Details**:

```python
def list_filters() -> List[Dict[str, Any]]:
    """List message filters"""

def create_filter(criteria: Dict[str, Any], action: Dict[str, Any]) -> Dict[str, Any]:
    """Create message filter with query and action"""

def get_thread(thread_id: str) -> Dict[str, Any]:
    """Get all messages in thread"""

def list_settings() -> Dict[str, Any]:
    """Get email settings"""

def set_vacation_responder(message: str, enabled: bool = True) -> Dict[str, Any]:
    """Enable/disable vacation responder"""
```

---

### Phase 5: Integration & Automation (Priority: MEDIUM)

**Goal**: Connect Gmail with other tools, enable workflows

**Features**:
- Calendar integration: Pull attendees from Gmail → Calendar
- People integration: Extract contacts from emails → Contacts
- Drive integration: Attach files from Drive
- Sheets integration: Export email data to sheets

**Example Workflows**:

1. **Email to Calendar**:
   ```bash
   gwc-email search "from:alice@example.com" --output json | \
   jq '.[] | {from: .headers.from, date: .internalDate}' | \
   gwc-cal create --attendees ...
   ```

2. **Extract Email Signatures**:
   ```bash
   gwc-email get <message_id> --output json | \
   jq '.payload.body.data' | base64 -d | grep -i "signature"
   ```

3. **Backup to Sheets**:
   ```bash
   gwc-email list --limit 1000 --output json > emails.json
   gwc-sheets import --file emails.json --sheet backup
   ```

---

## Implementation Roadmap

### Timeline

**Week 1-2: Phase 1 (Core Message Management)**
- Implement message listing, get, search
- Label enumeration
- Output formatting
- Basic tests and documentation
- **Deliverable**: `gwc-email list`, `get`, `search`, `labels`

**Week 3-4: Phase 2 (Message Composition)**
- Draft creation and management
- Message sending
- Reply and forward
- Attachment handling
- **Deliverable**: `gwc-email send`, `draft` commands

**Week 5-6: Phase 3 (Organization)**
- Label modification (add/remove)
- Batch operations
- Read/unread status
- Custom label creation
- **Deliverable**: `gwc-email modify`, `delete`, `labels create`

**Week 7+: Phase 4-5 (Advanced)**
- Filters and settings
- Thread operations
- Integration helpers
- Automation workflows

### Git Workflow

Each phase gets:
1. **Feature branch**: `feature/email-phase-1` etc.
2. **Implementation commit**: All code changes
3. **Test commit**: Test suite and coverage
4. **Documentation commit**: README updates, guides, examples
5. **PR**: Code review and merge to main

### Testing Strategy

**Unit Tests** (`tests/email/`):
- Message parsing and formatting
- Label operations
- MIME message construction
- Header extraction

**Integration Tests**:
- Real API calls to Gmail sandbox
- Message listing and searching
- Create and send workflows
- Label management

**End-to-End Tests**:
- Full workflows (search → modify → archive)
- Multi-step operations
- Error handling

### Documentation Structure

```
README_GMAIL.md (this file)
├── Gmail API Overview
├── Implementation Phases
├── Installation & Auth
├── Quick Start
├── Command Reference
├── Output Formats
├── Common Workflows
├── API Limits & Best Practices
└── Troubleshooting

CLAUDE/skills/email/
├── QUICK_START.md - 5-minute intro
├── SKILL.md - Common tasks
├── REFERENCE.md - Complete API reference
├── INDEX.md - Navigation guide
└── TROUBLESHOOTING.md - Problem solving
```

---

## Key Design Principles

1. **Unix Philosophy**: Each command does one thing well
2. **LLM-Friendly**: Simple syntax, clear options, consistent behavior
3. **Non-Interactive**: Never prompt; errors inform
4. **Composable**: Output feeds into other tools
5. **Efficient**: Batch operations, selective field retrieval
6. **Safe**: Read-only by default, explicit delete/modify
7. **Documented**: Every command has clear help

---

## Gmail API Quirks & Solutions

### Problem 1: Message ID Format
- **Issue**: Message IDs are base16 integers, inconsistent encoding
- **Solution**: Always use `messageId` field from API, never construct IDs

### Problem 2: MIME Payload Encoding
- **Issue**: Body can be base64url-encoded or plain text depending on format
- **Solution**: Use `format: "full"` and decode payload.body.data with base64url
- **Code**:
  ```python
  import base64
  payload = message['payload']
  if 'body' in payload and 'data' in payload['body']:
      body = base64.urlsafe_b64decode(payload['body']['data'])
  ```

### Problem 3: Large Messages
- **Issue**: Full message format can be huge (MB+)
- **Solution**: Use `fields` parameter to request only needed fields
- **Code**:
  ```python
  fields = "payload(headers,mimeType),id,threadId,labelIds"
  messages = service.users().messages().list(userId='me', fields=fields).execute()
  ```

### Problem 4: Pagination
- **Issue**: Results limited to 100 by default, use nextPageToken for more
- **Solution**: Implement helper that yields all results
- **Code**:
  ```python
  def list_all_messages(label: str = "INBOX", max_results: int = 10):
      page_token = None
      for _ in range(max_results):  # Iterate pages
          results = service.users().messages().list(
              userId='me', labelIds=[label], pageToken=page_token
          ).execute()
          messages = results.get('messages', [])
          yield from messages
          page_token = results.get('nextPageToken')
          if not page_token:
              break
  ```

### Problem 5: Label IDs vs Names
- **Issue**: Some operations require label ID (hex), others accept names
- **Solution**: Maintain mapping of label name → ID, resolve names to IDs
- **Code**:
  ```python
  label_map = {}
  for label in service.users().labels().list(userId='me').execute()['labels']:
      label_map[label['name']] = label['id']

  # Always use IDs in API calls
  service.users().messages().modify(
      userId='me', id=msg_id,
      body={'addLabelIds': [label_map['Important']]}
  )
  ```

### Problem 6: Rate Limiting
- **Issue**: 15,000 requests/day per user, 250MB/day quota
- **Solution**: Batch operations, cache results, implement backoff
- **Example**: Use `batchModify` instead of individual `modify` calls

---

## Success Metrics

**Phase 1 Success**:
- ✅ List 100+ messages with pagination
- ✅ Search with 5+ different query types
- ✅ Get full message details (headers, body, attachments)
- ✅ All output formats working (unix, json, llm)
- ✅ 10+ tests passing
- ✅ Documentation for all commands

**Phase 2 Success**:
- ✅ Create and send messages
- ✅ Reply and forward
- ✅ Attachments working
- ✅ Draft management
- ✅ Integration tests passing

**Phase 3 Success**:
- ✅ Batch modify operations
- ✅ Read/unread tracking
- ✅ Custom label creation and management
- ✅ Archive and delete workflows

---

## Questions for Leaf

1. **Priority on features**: Are we focusing on read-first operations initially, or do you need send capability right away?

2. **Attachment handling**: Should we support large files? There are Gmail API quotas to consider.

3. **Integration timeline**: When do you need Calendar integration? Can it wait for Phase 4?

4. **Testing approach**: Should we use a sandbox Gmail account for integration tests, or mock the API?

5. **Documentation depth**: How detailed should command examples be? (We have the People API docs as a reference)

---

## Appendix: Gmail API Quota & Limits

| Limit | Value | Notes |
|-------|-------|-------|
| Daily Quota | 250 MB | Total data transfer per user |
| Requests/Day | 15,000 | Total API calls per user |
| Batch Size | 100 messages | Max per batchModify/batchDelete |
| Message Size | 25 MB | Max message with attachments |
| Label Limit | 500+ | Max labels per account |
| Attachment Size | 25 MB | Per file |
| List Page Size | 100 | Messages per page |

**Best Practices**:
1. Use batch operations for multiple modifications
2. Specify `fields` parameter to request only needed data
3. Implement exponential backoff for rate limit errors (429)
4. Cache label name→ID mappings
5. Use incremental sync for large mailboxes
6. Prefer `modify` over `delete` when possible

---

## Appendix: Sample API Calls

### List Messages
```python
messages = service.users().messages().list(
    userId='me',
    labelIds=['INBOX'],
    q='before:2025-01-01',
    maxResults=10,
    fields='messages(id,threadId,labelIds,snippet,internalDate),nextPageToken'
).execute()
```

### Get Full Message
```python
message = service.users().messages().get(
    userId='me',
    id=message_id,
    format='full'
).execute()

# Extract headers
headers = {h['name']: h['value'] for h in message['payload']['headers']}
```

### Send Message
```python
message = {
    'raw': base64.urlsafe_b64encode(
        email_message.as_bytes()
    ).decode()
}

sent = service.users().messages().send(
    userId='me',
    body=message
).execute()
```

### Batch Modify
```python
service.users().messages().batchModify(
    userId='me',
    body={
        'ids': ['msg_id_1', 'msg_id_2', 'msg_id_3'],
        'addLabelIds': ['IMPORTANT'],
        'removeLabelIds': ['INBOX']
    }
).execute()
```

---

**Document Version**: 1.0
**Last Updated**: November 18, 2025
**Status**: Ready for Implementation
