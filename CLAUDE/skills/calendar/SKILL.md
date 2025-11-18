---
name: calendar
description: Comprehensive google calendar management.
---

## IMPORTANT: Timezone & Date Handling

**Abby runs in UTC. Leaf is in Mountain Time (UTC-07:00).**

When working with dates and times:
1. **Always use explicit timezone offsets** in ISO8601 format (e.g., `2025-01-20T14:00:00-07:00`)
2. **Be careful with "today" vs "tomorrow"** - if it's 1 AM UTC, it's still the previous day in Mountain time
3. **When updating event times, ALWAYS update duration too** to keep the end time consistent

**Pro tip**: Use `date` command to check current time in different zones.

## Quick Start

All commands run from `~/Jarvis/sagas/src/google-workspace-cli` using `poetry run gwc-cal <command>`.

### Most Common Tasks

**See today's events:**
```bash
poetry run gwc-cal find --output llm
```

**Create a basic meeting:**
```bash
poetry run gwc-cal create \
  --time "2025-01-20T14:00:00-07:00" \
  --subject "Team Meeting" \
  --duration 60
```

**Create meeting with Google Meet and attendees:**
```bash
poetry run gwc-cal create \
  --time "2025-01-20T14:00:00-07:00" \
  --subject "Team Meeting" \
  --duration 30 \
  --attendees "alice@company.com,bob@company.com" \
  --meet \
  --location "Conference Room A"
```

**Update an event (remember duration!):**
```bash
poetry run gwc-cal update <event-id> \
  --time "2025-01-20T15:00:00-07:00" \
  --duration 60
```

**Add attendees to existing event:**
```bash
poetry run gwc-cal update <event-id> \
  --add-attendee "newperson@company.com" \
  --notify all
```

**Delete an event:**
```bash
poetry run gwc-cal delete <event-id>
```

### Finding Events

**This week:**
```bash
poetry run gwc-cal find --output llm
```

**Specific date range:**
```bash
poetry run gwc-cal find --start 2025-01-15 --end 2025-01-22 --output llm
```

**Search by keyword:**
```bash
poetry run gwc-cal find --query "standup" --output llm
```

## Output Formats

- `--output unix` - Tab-separated (default, for scripting)
- `--output json` - JSON (for programmatic parsing)
- `--output llm` - Human-readable (use this most of the time!)

## Common Options

Most create/update commands support:
- `--meet` - Add Google Meet link
- `--location TEXT` - Physical location or room
- `--attendees "email1,email2"` - Invite people
- `--description TEXT` - Event details
- `--notify [all|externalOnly|none]` - Email notifications
- `--transparency [opaque|transparent]` - Show as busy/free
- `--recurrence TEXT` - Recurring events (see REFERENCE.md)
- `--reminder TEXT` - Custom reminders (see REFERENCE.md)

## For Complex Tasks

See **REFERENCE.md** in this directory for:
- Complete option reference for all commands
- Recurring event patterns
- Custom reminder syntax
- Visibility and transparency settings
- Adding/removing individual attendees
- Reading descriptions from files
- Config management

## Quick Command List

- `list` - Show all calendars
- `create` - Create new event
- `update` - Modify event
- `delete` - Remove event
- `find` - Search/list events
- `get` - Get event details
- `config` - Manage settings
- `auth` - Re-authenticate

## Help

Get detailed help for any command:
```bash
poetry run gwc-cal <command> --help
```
