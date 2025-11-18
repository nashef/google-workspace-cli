# Google Workspace CLI (gwc)

Command-line toolkit for interacting with Google Workspace APIs. Designed for simplicity and LLM-friendliness.

## Project Vision

A lightweight, Unix-philosophy CLI that exposes Google Workspace functionality through simple, predictable commands. Each API has its own tool (`gwc-cal`, `gwc-mail`, etc.) sharing common authentication and configuration infrastructure.

## Requirements Met

- ✅ OAuth2 authentication with token refresh
- ✅ Python 3.14 + Poetry
- ✅ Separate command per API (`gwc-cal`, `gwc-mail`, etc.)
- ✅ LLM-friendly: Simple syntax for basic operations, flags for advanced
- ✅ Non-interactive: Errors inform, never prompts
- ✅ Multiple output formats: unix (default), json, llm-pretty
- ✅ Single shared codebase with multiple entry points

## Gmail API Completion Status

- ✅ **Phase 1**: Message reading, searching, and label management
- ✅ **Phase 2**: Message composition, drafts, send, reply, forward with attachments
- ✅ **Phase 3**: Message organization (read/unread, archive, labels) and batch operations
- ✅ **Phase 4**: Advanced features (filters, signatures, auto-responders, templates)

## Implementation Plan

### Phase 1: Core Infrastructure + Calendar
1. Set up Poetry project structure
2. Implement `gwc.shared.auth` (OAuth2, token management)
3. Implement `gwc.shared.config` (credential/config storage at `~/.config/gwc/`)
4. Implement `gwc.shared.output` (format conversion)
5. Implement `gwc.shared.exceptions` (error handling)
6. Implement `gwc-cal`:
   - `list` - List available calendars
   - `create` - Create event (ISO8601 time, subject, duration, attendees, description)
   - `get` - Get event details
   - `update` - Update event
   - `delete` - Delete event
   - `find` - Search events by date range and query

### Phase 2: Email API
Design TBD after Calendar v1 is complete.

### Phase 3+: Drive, People, Docs, Sheets, Slides

## Design Documents

- **DESIGN.md** - Architecture, project structure, API design principles
- **CMD_API.md** - CLI command → REST API mapping, detailed parameter specs, output formats
- **README.md** - User-facing documentation with API links

## API Details

**Calendar API v3**: https://developers.google.com/workspace/calendar/api/v3/reference
**Python Quickstart**: https://developers.google.com/workspace/calendar/api/quickstart/python

Key resources for Phase 1:
- CalendarList (list user's calendars)
- Events (create, get, update, delete, list/find)

## Configuration

**Credentials**: `~/.config/gwc/`
- `credentials.json` - OAuth2 credentials
- `token.json` - Access/refresh tokens
- `config.toml` - User settings

**Auth Workflow**:
- `gwc auth` - Initial OAuth2 setup (prints URL, user visits, returns code)
- `gwc auth --refresh` - Refresh expired tokens
- All commands error if no valid token exists (no prompts)
