# Apologia

This is completely vibe-coded and highly experimental, but it seems to basically work, and appears to be very useful.


Nota Bene: *Think very carefully about your access rules.* These tools try to cover the entire REST API for each of the supported services, which means that they could do extensive damage if your LLM got prompt injected. E.g., by reading a Phishing email that contains a hidden subversive prompt for your AI. One that, for example, causes your own agent to replace your company name with an expletive in every Sheets doc in your entire Google Drive.

I am warning you now to think very carefully about how you use these tools.

That said, I included Claude Skills for all of the tools.

If you try it out, after all that, have your LLM write bug reports. Send them to me. I will fix them.

# google-workspace-cli

A command line toolkit for interacting with Google Workspace APIs (Calendar, Gmail, Drive, People, Docs, Sheets, Slides). Designed for simplicity and LLM integration.

## Quick Start

### Installation & Setup

1. **Install dependencies** (one time):
   ```bash
   poetry install
   ```

2. **Authenticate** (one time):

    Before you authenticate, you must [create credentials in the Google Cloud console](https://developers.google.com/workspace/guides/create-credentials) for a desktop app client. Once you have downloaded the credentials.json and place it here: `~/.config/credential.json`. You can then run the auth flow.

   ```bash
   poetry run gwc auth
   ```

   This will print an authorization URL to your terminal. You must visit this in a browser tab logged into the same account or organization you used to create the credentials above. The URL will take you through the OAuth authorization flow. If the `gwc auth` command is running on the same machine as the browser, then the browser should automatically complete the OAuth flow. If you are running this on a server, your browser may try to visit localhost on a weird port, and get an error. That's ok, just copy that URL over to the server where `gwc auth` is running and curl it. Make sure to put the URL in single quotes as shown:

   ```bash
   curl '<ENTIRE_LONG_URL>'
   ```

   Your oauth token will be saved to `~/.config/gwc/token.json`. It can be refreshed using `gwc auth --refresh` without having to complete the login flow again.

### Available Commands by API

This toolkit provides 190+ commands across 7 Google Workspace APIs:

#### **Calendar** (`poetry run gwc-cal <command>`)
- `list` - List calendars
- `create` - Create event
- `get` - Get event details
- `update` - Update event
- `delete` - Delete event
- `find` - Search/filter events
- `move` - Move event to different calendar
- `watch` - Watch for changes

#### **Contacts** (`poetry run gwc-people <command>`)
- `list` - List contacts
- `get` - Get contact details
- `search` - Search contacts by name/email
- `create` - Create new contact
- `update` - Update contact
- `delete` - Delete contact
- `list-groups` - List contact groups
- `add-to-group` - Add contact to group

#### **Drive** (`poetry run gwc-drive <command>`)
- `list-drives` - List shared drives
- `list` - List files/folders
- `get` - Get file metadata
- `search` - Search files
- `create-folder` - Create folder
- `upload` - Upload file
- `download` - Download file
- `delete` - Delete file
- `share` - Share file with users
- `move` - Move file to folder

#### **Docs** (`poetry run gwc-docs <command>`)
- `create` - Create new document
- `get` - Get document metadata
- `get-content` - Get document text
- `append-text` - Add text to document
- `insert-text` - Insert text at position
- `update-text` - Replace text
- `batch-update` - Complex multi-step updates
- `get-revisions` - Get document history

#### **Sheets** (`poetry run gwc-sheets <command>`)
- `create` - Create new spreadsheet
- `get` - Get spreadsheet metadata
- `list-sheets` - List sheets in spreadsheet
- `read-range` - Read cell values
- `write-range` - Write cell values
- `append-range` - Append rows
- `clear-range` - Clear cells
- `batch-update` - Complex multi-step updates

#### **Email** (`poetry run gwc-mail <command>`)
- `list` - List messages
- `get` - Get message details
- `search` - Search messages
- `send` - Send email
- `delete` - Delete message
- `mark-read` - Mark message as read
- `add-label` - Add label to message
- `list-labels` - List label categories

#### **Slides** (`poetry run gwc-slides <command>`)
- `create` - Create presentation
- `get` - Get presentation metadata
- `list-slides` - List slides
- `add-slide` - Add new slide
- `delete-slide` - Delete slide
- `duplicate-slide` - Copy slide
- `insert-text` - Add text to slide
- `insert-image` - Add image to slide
- `insert-shape` - Add shape to slide
- `batch-update` - Complex multi-step updates

### Basic Workflow Examples

#### Example 1: Create a meeting with a contact
```bash
# 1. Search for contact
poetry run gwc-people search --query "alice" --output json

# 2. Get full contact details (note the contact ID from search)
poetry run gwc-people get <contact-id> --output json

# 3. Create calendar event with contact's email
poetry run gwc-cal create \
  --time 2025-01-20T14:00:00 \
  --subject "Meeting with Alice" \
  --duration 30 \
  --attendees "alice@company.com" \
  --description "Quarterly sync"
```

#### Example 2: Generate a report in Sheets and share it
```bash
# 1. Create spreadsheet
SHEET_ID=$(poetry run gwc-sheets create --title "Monthly Report" --output json | jq -r '.id')

# 2. Add data to spreadsheet
poetry run gwc-sheets write-range \
  --sheet-id $SHEET_ID \
  --range "Sheet1!A1:C3" \
  --values "[['Month','Revenue','Growth'],['Jan','100K','5%'],['Feb','105K','5%']]"

# 3. Share with team member
poetry run gwc-drive share \
  --file-id $SHEET_ID \
  --users "bob@company.com" \
  --role editor

# 4. Send email notification
poetry run gwc-mail send \
  --to "bob@company.com" \
  --subject "Monthly Report Ready" \
  --body "Your report is ready at: https://sheets.google.com/d/$SHEET_ID"
```

#### Example 3: Create presentation from contact list
```bash
# 1. Get all contacts
poetry run gwc-people list --output json > contacts.json

# 2. Create presentation
PRES_ID=$(poetry run gwc-slides create --title "Team Directory" --output json | jq -r '.presentationId')

# 3. Add slide for each contact (using jq to parse)
cat contacts.json | jq -r '.[] | .displayName' | while read name; do
  poetry run gwc-slides add-slide --presentation-id $PRES_ID
  poetry run gwc-slides insert-text --presentation-id $PRES_ID \
    --slide-id slide-1 --text "$name"
done
```

#### Example 4: Archive emails to Drive as document
```bash
# 1. Search for emails from a date range
poetry run gwc-mail search --query "from:alice@company.com" --output json > emails.json

# 2. Create a document to hold archive
DOC_ID=$(poetry run gwc-docs create --title "Email Archive - Alice" --output json | jq -r '.documentId')

# 3. Append email content
poetry run gwc-mail search --query "from:alice@company.com" --output llm | \
  poetry run gwc-docs append-text --document-id $DOC_ID

# 4. Move to specific Drive folder
poetry run gwc-drive move \
  --file-id $DOC_ID \
  --parent-folder "Email Archives"
```

#### Example 5: Create meeting notes template
```bash
# 1. Create document for meeting notes
DOC_ID=$(poetry run gwc-docs create --title "Team Meeting - Jan 20" --output json | jq -r '.documentId')

# 2. Get attendees from calendar event
poetry run gwc-cal get <event-id> --output json | jq -r '.attendees[].email' > attendees.txt

# 3. Append attendee list to document
echo "Attendees:" | poetry run gwc-docs append-text --document-id $DOC_ID
cat attendees.txt | poetry run gwc-docs append-text --document-id $DOC_ID

# 4. Share with meeting attendees
cat attendees.txt | while read email; do
  poetry run gwc-drive share \
    --file-id $DOC_ID \
    --users "$email" \
    --role commenter
done
```

## Output Formats

By default, commands output in unix format (tab-separated values). You can change this with `--output`:

**JSON format** (for programmatic use):
```bash
poetry run gwc-cal list --output json
```

**LLM-pretty format** (human-readable):
```bash
poetry run gwc-cal list --output llm
```

## Time Format

Event times must be in ISO8601 format:
- `2025-01-20T14:00:00` - Without timezone (uses calendar's timezone)
- `2025-01-20T14:00:00-07:00` - With timezone offset

Examples:
- `2025-01-20T09:30:00` - 9:30 AM on Jan 20, 2025
- `2025-01-20T14:00:00+00:00` - 2 PM UTC

## Help & Documentation

Get detailed help for any command:
```bash
poetry run gwc-cal --help
poetry run gwc-cal list --help
poetry run gwc-cal create --help
```

## Configuration

Credentials and tokens are stored in `~/.config/gwc/`:
- `credentials.json` - OAuth2 credentials (from Google Cloud Console)
- `token.json` - Access/refresh tokens (auto-managed)

To refresh your token:
```bash
poetry run gwc auth --refresh
```

## Getting Help

Each command has built-in help. Use `--help` to see all options:

```bash
poetry run gwc auth --help
poetry run gwc-cal create --help
poetry run gwc-sheets write-range --help
```

For detailed documentation on each API, see the docs folder:
- `docs/README_CALENDAR.md` - Calendar API guide
- `docs/README_PEOPLE.md` - Contacts API guide
- `docs/README_DRIVE.md` - Drive API guide
- `docs/README_DOCS.md` - Docs API guide
- `docs/README_SHEETS.md` - Sheets API guide
- `docs/README_GMAIL.md` - Gmail API guide
- `docs/README_SLIDES.md` - Slides API guide
