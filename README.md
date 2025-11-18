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
