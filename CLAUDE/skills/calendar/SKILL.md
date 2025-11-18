---
name: calendar
description: Google Calendar management and event operations
---

# Calendar CLI Quick Reference

Base command: `poetry run gwc-cal <command>`

## Quick Start

```bash
# See today's events
poetry run gwc-cal find --output llm

# Create basic event
poetry run gwc-cal create \
  --time "2025-01-20T14:00:00-07:00" \
  --subject "Team Meeting" \
  --duration 60

# Get event details
poetry run gwc-cal get event_id --output json

# List all calendars
poetry run gwc-cal list --output llm
```

## Timezone Notice

Calendar uses ISO8601 with explicit timezone offsets. Examples:
- Mountain Time: `2025-01-20T14:00:00-07:00`
- Pacific Time: `2025-01-20T14:00:00-08:00`
- Eastern Time: `2025-01-20T14:00:00-05:00`
- UTC: `2025-01-20T21:00:00Z`

**When updating times, always update duration too to keep end time consistent.**

## Event Operations

| Task | Command |
|------|---------|
| Create basic event | `create --time "ISO8601" --subject "..." --duration MINS` |
| Create with location | `create --time "..." --subject "..." --duration MINS --location "Room A"` |
| Add attendees | `create ... --attendees "alice@co.com,bob@co.com"` |
| Add Google Meet | `create ... --meet` |
| Create with description | `create ... --description "Details..."` |
| List events (date range) | `find --start 2025-01-15 --end 2025-01-22 --output llm` |
| Find today | `find --output llm` |
| Search by keyword | `find --query "standup" --output llm` |
| Get event details | `get event_id --output json` |
| Update time | `update event_id --time "ISO8601" --duration MINS` |
| Add attendee | `update event_id --add-attendee "email@co.com" --notify all` |
| Remove attendee | `update event_id --remove-attendee "email@co.com"` |
| Delete event | `delete event_id` |

## Common Options

- `--time TEXT` - Start time (ISO8601 with timezone)
- `--duration INTEGER` - Event duration in minutes
- `--subject TEXT` - Event title
- `--location TEXT` - Physical location or room
- `--attendees "email1,email2"` - Comma-separated emails
- `--description TEXT` - Event details
- `--meet` - Add Google Meet link
- `--notify [all|externalOnly|none]` - Notification level
- `--transparency [opaque|transparent]` - Show as busy/free
- `--output [unix|json|llm]` - Output format

## Calendar Commands

| Command | Purpose |
|---------|---------|
| `list` | Show all calendars |
| `create` | Create new event |
| `update` | Modify existing event |
| `delete` | Remove event |
| `find` | Search/list events in date range |
| `get` | Get event details |
| `config` | Manage settings |
| `auth` | Re-authenticate |

## Output Formats

- `--output unix` - Tab-separated (default, scripting)
- `--output json` - JSON (programmatic parsing)
- `--output llm` - Human-readable (recommended)

## Tips

1. Always use explicit timezones in ISO8601 format
2. When updating event time, always update duration
3. Use `find --output llm` for human-readable event lists
4. Multiple reminders supported (see ADVANCED.md)
5. Use `--add-attendee`/`--remove-attendee` to modify attendee list

## Common Workflows

**Create meeting with team:**
```bash
poetry run gwc-cal create \
  --time "2025-01-20T14:00:00-07:00" \
  --subject "Team Meeting" \
  --duration 30 \
  --attendees "alice@company.com,bob@company.com" \
  --meet \
  --notify all
```

**Add someone to existing event:**
```bash
poetry run gwc-cal update event_id \
  --add-attendee "newperson@company.com" \
  --notify all
```

**Check calendar for date range:**
```bash
poetry run gwc-cal find --start 2025-01-15 --end 2025-01-22 --output llm
```

**Update event time (don't forget duration!):**
```bash
poetry run gwc-cal update event_id \
  --time "2025-01-20T15:00:00-07:00" \
  --duration 60
```

## Advanced Features

For Phase 2-4 features, see **ADVANCED.md**:
- Recurring events (RRULE syntax)
- Multiple reminders
- Attendee management
- Visibility & transparency
- Google Meet integration
- Timezone handling

## Help

Get detailed help for any command:
```bash
poetry run gwc-cal <command> --help
```

## Documentation

- **REFERENCE.md** - Complete command reference, field descriptions, recurrence patterns
- **ADVANCED.md** - Recurring events, reminders, attendee management, timezone handling
