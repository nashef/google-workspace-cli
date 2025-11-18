# google-workspace-cli

A command line toolkit for interacting with Google Workspace APIs (Calendar, Gmail, Drive, People, Docs, Sheets, Slides). Designed for simplicity and LLM integration.

## Quick Start

### Installation & Setup

1. **Install dependencies** (one time):
   ```bash
   poetry install
   ```

2. **Authenticate** (one time):
   ```bash
   poetry run gwc-cal auth
   ```

   This will print an authorization URL. Visit it in your browser, approve access, and paste the authorization code back when prompted. Your credentials will be saved to `~/.config/gwc/token.json`.

### Basic Usage

All commands use `poetry run gwc-cal <command>`. Here are the most common operations:

#### List your calendars
```bash
poetry run gwc-cal list
```

#### Create an event
```bash
poetry run gwc-cal create \
  --time 2025-01-20T14:00:00 \
  --subject "Team Meeting" \
  --duration 60
```

#### Create an event with attendees
```bash
poetry run gwc-cal create \
  --time 2025-01-20T14:00:00 \
  --subject "Team Meeting" \
  --duration 30 \
  --attendees "alice@company.com,bob@company.com" \
  --description "Quarterly planning"
```

#### Get event details
```bash
poetry run gwc-cal get <event-id>
```

#### Update an event
```bash
poetry run gwc-cal update <event-id> --subject "New Title"
```

#### Delete an event
```bash
poetry run gwc-cal delete <event-id>
```

#### Find events in a date range
```bash
poetry run gwc-cal find --start 2025-01-15 --end 2025-01-22
```

#### Search for events by keyword
```bash
poetry run gwc-cal find --query "standup"
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

To re-authenticate or refresh tokens:
```bash
poetry run gwc-cal auth --refresh
```

## Available Commands

- `auth` - Authenticate with Google Workspace
- `list` - List available calendars
- `create` - Create a new event
- `get` - Get event details
- `update` - Update an event
- `delete` - Delete an event
- `find` - Search/filter events

## Resources

- [Google Calendar API v3 Reference](https://developers.google.com/workspace/calendar/api/v3/reference)
- [Google Calendar API Python Client Library](https://developers.google.com/resources/api-libraries/documentation/calendar/v3/python/latest/)
- [Google Calendar API Python Quickstart](https://developers.google.com/workspace/calendar/api/quickstart/python)
