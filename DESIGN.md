# Google Workspace CLI Design Document

## Overview

`gwc` (Google Workspace CLI) is a command-line toolkit for interacting with Google Workspace APIs. It provides simple, LLM-friendly interfaces to Calendar, Email, Drive, People, Docs, Sheets, and Slides.

## Architecture

### Project Structure

```
gwc/
  __init__.py
  shared/
    __init__.py
    auth.py           # OAuth2 authentication, token management
    config.py         # Configuration and credential storage
    output.py         # Output formatting (unix, json, llm-pretty)
    exceptions.py     # Custom exception types
  calendar/
    __init__.py
    __main__.py       # Entry point
    operations.py     # Calendar API operations
  email/
    __init__.py
    __main__.py       # Entry point
    operations.py     # Email API operations
  drive/
    __init__.py
    __main__.py
    operations.py
  [people, docs, sheets, slides - same pattern]
```

### Entry Points (pyproject.toml)

```toml
[project.scripts]
gwc-cal = "gwc.calendar:main"
gwc-mail = "gwc.email:main"
gwc-drive = "gwc.drive:main"
gwc-people = "gwc.people:main"
gwc-docs = "gwc.docs:main"
gwc-sheets = "gwc.sheets:main"
gwc-slides = "gwc.slides:main"
```

## Authentication

### Storage

Credentials and tokens stored in `~/.config/gwc/`:
- `credentials.json` - OAuth2 credentials
- `token.json` - Access/refresh tokens
- `config.toml` - User configuration (calendar IDs, email addresses, etc.)

### Workflow

1. **Initial Setup**: `gwc auth`
   - Prints OAuth2 authorization URL
   - User visits URL, grants permissions
   - Returns authorization code (user pastes it back or auto-detected if possible)
   - Stores tokens in `~/.config/gwc/token.json`

2. **Token Refresh**: `gwc auth --refresh`
   - Refreshes expired tokens
   - Stores updated tokens

3. **Error Handling**:
   - If no valid token exists, commands error out with helpful message
   - Never prompt for input (designed for LLM agents)
   - All errors to stderr, exit with non-zero code

## Output Formats

All commands support three output formats via flags:

1. **Unix (default)**: Line-oriented, streamable output. One item per line.
2. **JSON**: `--output json` - Pretty-printed JSON (not newline-delimited)
3. **LLM-Pretty**: `--output llm` - Human-readable format optimized for LLM consumption

## Shared Components

### `gwc.shared.auth`
- OAuth2 setup and token management
- Token refresh logic
- Credential storage/retrieval

### `gwc.shared.config`
- Read/write config files
- Manage stored settings (default calendar ID, email, etc.)

### `gwc.shared.output`
- Format data for unix/json/llm output
- Handle streaming

### `gwc.shared.exceptions`
- `AuthenticationError` - No valid credentials
- `APIError` - Google API errors
- `ConfigError` - Configuration issues

## API Design Principles

1. **Simple by default**: Basic operations should be obvious and minimal
2. **Flags for advanced features**: Complex operations use `--flag` options
3. **Detailed help**: `--help` shows comprehensive examples and descriptions
4. **Non-interactive**: Never prompt for user input; error with clear messages instead
5. **LLM-friendly**: Commands are predictable, unambiguous, and easy to parse

## Calendar API (gwc-cal)

### Commands

#### `gwc-cal list`
List available calendars.

**Output**: Calendar name, ID, description, timezone

#### `gwc-cal create`
Create a new event.

**Required**:
- `--time <ISO8601>` - Event start time
- `--subject <string>` - Event title

**Optional**:
- `--duration <minutes>` - Event duration (default: 60)
- `--attendees <email>,<email>,...` - Comma-separated attendee list
- `--description <string>` - Event description
- `--calendar <id>` - Target calendar (default: primary)
- `--output {unix,json,llm}` - Output format

#### `gwc-cal get <event-id>`
Retrieve event details.

#### `gwc-cal update <event-id>`
Update an existing event.

**Optional flags**: Same as create (--time, --subject, --duration, etc.)

#### `gwc-cal delete <event-id>`
Delete an event.

#### `gwc-cal find`
Search/filter events.

**Optional**:
- `--start <ISO8601>` - Range start (default: today)
- `--end <ISO8601>` - Range end (default: +7 days)
- `--query <string>` - Search query
- `--calendar <id>` - Calendar to search

### Future Iterations
- Recurring events
- Google Meet integration
- Attendee management (People API integration)
- Natural language time parsing

## Email API (gwc-mail)

Design TBD pending API review.

## Drive, People, Docs, Sheets, Slides

Design TBD - will follow same patterns established by Calendar/Email.

## Implementation Roadmap

1. **Phase 1**: Core infrastructure
   - Auth module (OAuth2, token management)
   - Config module
   - Output formatting
   - Click CLI framework setup

2. **Phase 2**: Calendar API
   - Implement `list`, `create`, `get`, `delete`
   - Test against real Google Calendar API

3. **Phase 3**: Email API
   - Design email commands
   - Implement core operations

4. **Phase 4+**: Remaining APIs

## Dependencies

- `google-auth-oauthlib` - OAuth2 authentication
- `google-api-python-client` - Google API client library
- `click` - CLI framework
- `toml` or `tomli` - Configuration file parsing

## Testing

- Test against real credentials (YOLO approach)
- Mock Google API responses for integration tests (future)
- CLI testing with Click's test runner

## Distribution

- Publish to PyPI as `google-workspace-cli`
- Support Python 3.14+ (downgrade if compatibility issues)
