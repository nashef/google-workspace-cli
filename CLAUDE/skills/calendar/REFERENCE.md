# Google Calendar CLI - Complete Reference

This is the exhaustive reference for all `gwc-cal` commands and options. For common tasks, see **SKILL.md** instead.

## Commands Overview

```
gwc-cal [OPTIONS] COMMAND [ARGS]...

Commands:
  auth    - Authenticate with Google Workspace
  config  - Manage configuration settings
  create  - Create a new calendar event
  delete  - Delete a calendar event
  find    - Find events in a calendar
  get     - Get event details
  list    - List available calendars
  update  - Update a calendar event
```

---

## `gwc-cal list`

List all available calendars.

**Usage:**
```bash
gwc-cal list [--output FORMAT]
```

**Options:**
- `--output [unix|json|llm]` - Output format (default: unix)

**Example:**
```bash
poetry run gwc-cal list --output llm
```

---

## `gwc-cal create`

Create a new calendar event.

**Usage:**
```bash
gwc-cal create --time TIME --subject SUBJECT [OPTIONS]
```

**Required Options:**
- `--time TEXT` - Event start time in ISO8601 format (e.g., `2025-01-15T14:00:00-07:00`)
- `--subject TEXT` - Event title/subject

**Optional Options:**
- `--duration INTEGER` - Event duration in minutes (default: 60)
- `--attendees TEXT` - Comma-separated list of attendee email addresses
- `--description TEXT` - Event description
- `--description-file FILENAME` - Read event description from file
- `--meet` - Add a Google Meet conference to the event
- `--location TEXT` - Event location (address or room name)
- `--transparency [opaque|transparent]` - `opaque`=busy (default), `transparent`=free
- `--visibility [default|public|private|confidential]` - Event visibility
- `--notify [all|externalOnly|none]` - Notify guests when creating event
- `--reminder TEXT` - Set reminders (see Reminders section below)
- `--recurrence TEXT` - Recurrence pattern (see Recurrence section below)
- `--calendar TEXT` - Calendar ID (default: primary)
- `--output [unix|json|llm]` - Output format (default: unix)

**Examples:**

Basic event:
```bash
poetry run gwc-cal create \
  --time "2025-01-20T14:00:00-07:00" \
  --subject "Team Meeting" \
  --duration 60
```

Full-featured event:
```bash
poetry run gwc-cal create \
  --time "2025-01-20T14:00:00-07:00" \
  --subject "Quarterly Planning" \
  --duration 120 \
  --attendees "alice@company.com,bob@company.com" \
  --description "Review Q4 goals and plan Q1" \
  --meet \
  --location "Conference Room A" \
  --transparency opaque \
  --notify all \
  --reminder "popup:10,email:60"
```

With description from file:
```bash
poetry run gwc-cal create \
  --time "2025-01-20T14:00:00-07:00" \
  --subject "Project Kickoff" \
  --description-file ~/meeting-agenda.txt \
  --meet
```

Recurring weekly meeting:
```bash
poetry run gwc-cal create \
  --time "2025-01-20T09:00:00-07:00" \
  --subject "Weekly Standup" \
  --duration 15 \
  --recurrence "weekly:MO,WE,FR" \
  --meet
```

---

## `gwc-cal update`

Update an existing calendar event. Only specified fields are updated.

**Usage:**
```bash
gwc-cal update EVENT_ID [OPTIONS]
```

**Required Arguments:**
- `EVENT_ID` - The ID of the event to update

**Optional Options:**
- `--time TEXT` - New event start time in ISO8601 format
- `--subject TEXT` - New event title
- `--duration INTEGER` - New event duration in minutes
- `--attendees TEXT` - Comma-separated list of attendee email addresses (replaces all)
- `--add-attendee TEXT` - Add an attendee (can be used multiple times)
- `--remove-attendee TEXT` - Remove an attendee (can be used multiple times)
- `--description TEXT` - New event description
- `--description-file FILENAME` - Read event description from file
- `--meet` - Add a Google Meet conference to the event
- `--location TEXT` - Event location (address or room name)
- `--transparency [opaque|transparent]` - `opaque`=busy (default), `transparent`=free
- `--visibility [default|public|private|confidential]` - Event visibility
- `--notify [all|externalOnly|none]` - Notify guests when updating event
- `--reminder TEXT` - Set reminders (see Reminders section below)
- `--recurrence TEXT` - Recurrence pattern (see Recurrence section below)
- `--calendar TEXT` - Calendar ID (default: primary)
- `--output [unix|json|llm]` - Output format (default: unix)

**Examples:**

Change time (remember duration!):
```bash
poetry run gwc-cal update abc123def456 \
  --time "2025-01-20T15:00:00-07:00" \
  --duration 60
```

Add Google Meet:
```bash
poetry run gwc-cal update abc123def456 --meet
```

Add attendees (incremental):
```bash
poetry run gwc-cal update abc123def456 \
  --add-attendee "alice@company.com" \
  --add-attendee "bob@company.com" \
  --notify all
```

Remove an attendee:
```bash
poetry run gwc-cal update abc123def456 \
  --remove-attendee "charlie@company.com" \
  --notify all
```

Replace all attendees:
```bash
poetry run gwc-cal update abc123def456 \
  --attendees "alice@company.com,bob@company.com" \
  --notify all
```

Update multiple fields:
```bash
poetry run gwc-cal update abc123def456 \
  --subject "New Title" \
  --location "Building 2, Room 301" \
  --transparency transparent \
  --notify all
```

---

## `gwc-cal find`

Find events in a calendar within a date range, optionally filtered by search query.

**Usage:**
```bash
gwc-cal find [OPTIONS]
```

**Optional Options:**
- `--start TEXT` - Start date in ISO8601 format (default: today)
- `--end TEXT` - End date in ISO8601 format (default: start + 7 days)
- `--query TEXT` - Search query (searches event title and description)
- `--calendar TEXT` - Calendar ID (default: primary)
- `--output [unix|json|llm]` - Output format (default: unix)

**Examples:**

All events this week (default):
```bash
poetry run gwc-cal find --output llm
```

Specific date range:
```bash
poetry run gwc-cal find \
  --start 2025-01-15 \
  --end 2025-01-22 \
  --output llm
```

Search for events by keyword:
```bash
poetry run gwc-cal find --query "standup" --output llm
```

Today's events:
```bash
poetry run gwc-cal find \
  --start 2025-01-20 \
  --end 2025-01-21 \
  --output llm
```

---

## `gwc-cal get`

Get detailed information about a specific event.

**Usage:**
```bash
gwc-cal get EVENT_ID [OPTIONS]
```

**Required Arguments:**
- `EVENT_ID` - The ID of the event

**Optional Options:**
- `--calendar TEXT` - Calendar ID (default: primary)
- `--output [unix|json|llm]` - Output format (default: unix)

**Example:**
```bash
poetry run gwc-cal get abc123def456 --output llm
```

---

## `gwc-cal delete`

Delete a calendar event.

**Usage:**
```bash
gwc-cal delete EVENT_ID [OPTIONS]
```

**Required Arguments:**
- `EVENT_ID` - The ID of the event to delete

**Optional Options:**
- `--calendar TEXT` - Calendar ID (default: primary)

**Example:**
```bash
poetry run gwc-cal delete abc123def456
```

---

## `gwc-cal config`

Manage configuration settings (default calendar, timezone, etc.).

**Subcommands:**
- `config list` - List all configuration values
- `config get KEY` - Get a configuration value
- `config set KEY VALUE` - Set a configuration value
- `config delete KEY` - Delete a configuration value

**Examples:**

Set default calendar:
```bash
poetry run gwc-cal config set default_calendar "work@company.com"
```

Get default calendar:
```bash
poetry run gwc-cal config get default_calendar
```

List all config:
```bash
poetry run gwc-cal config list
```

---

## `gwc-cal auth`

Authenticate or re-authenticate with Google Workspace.

**Usage:**
```bash
gwc-cal auth [--refresh]
```

**Options:**
- `--refresh` - Force token refresh

**Example:**
```bash
poetry run gwc-cal auth --refresh
```

---

## Recurrence Patterns

The `--recurrence` option accepts several formats:

**Simple patterns:**
- `daily` - Every day
- `weekly` - Every week (same day of week)
- `monthly` - Every month (same date)
- `yearly` - Every year (same date)

**Weekly with specific days:**
- `weekly:MO,WE,FR` - Every Monday, Wednesday, Friday
- `weekly:TU,TH` - Every Tuesday, Thursday

**Raw RRULE (for complex patterns):**
- `RRULE:FREQ=DAILY;COUNT=10` - Daily for 10 occurrences
- `RRULE:FREQ=WEEKLY;BYDAY=MO,WE,FR;UNTIL=20251231T000000Z` - Every Mon/Wed/Fri until Dec 31, 2025

**Day abbreviations:** `MO`, `TU`, `WE`, `TH`, `FR`, `SA`, `SU`

**Examples:**
```bash
# Daily standup for 2 weeks
poetry run gwc-cal create \
  --time "2025-01-20T09:00:00-07:00" \
  --subject "Daily Standup" \
  --duration 15 \
  --recurrence "daily" \
  --meet

# Weekly team meeting every Monday
poetry run gwc-cal create \
  --time "2025-01-20T14:00:00-07:00" \
  --subject "Weekly Team Sync" \
  --duration 60 \
  --recurrence "weekly" \
  --meet

# Mon/Wed/Fri office hours
poetry run gwc-cal create \
  --time "2025-01-20T10:00:00-07:00" \
  --subject "Office Hours" \
  --duration 60 \
  --recurrence "weekly:MO,WE,FR" \
  --transparency transparent
```

---

## Reminders

The `--reminder` option sets custom reminders for an event.

**Format:** `method:minutes` (comma-separated for multiple)

**Methods:**
- `popup` - Pop-up notification
- `email` - Email reminder

**Special value:**
- `default` - Use calendar's default reminders

**Examples:**

10-minute popup before event:
```bash
--reminder "popup:10"
```

Multiple reminders:
```bash
--reminder "popup:10,email:60,email:1440"
```
(Pop-up 10 min before, email 1 hour before, email 1 day before)

Use calendar defaults:
```bash
--reminder "default"
```

**Complete example:**
```bash
poetry run gwc-cal create \
  --time "2025-01-20T14:00:00-07:00" \
  --subject "Important Meeting" \
  --duration 60 \
  --reminder "popup:10,email:60,email:1440"
```

---

## Transparency

Controls whether an event shows as "busy" or "free" in calendar.

**Values:**
- `opaque` - Shows as busy (default)
- `transparent` - Shows as free (available during this time)

**Use cases:**
- `transparent` for "hold" events, optional meetings, personal time
- `opaque` for actual commitments

**Example:**
```bash
poetry run gwc-cal create \
  --time "2025-01-20T14:00:00-07:00" \
  --subject "Hold for possible client call" \
  --duration 60 \
  --transparency transparent
```

---

## Visibility

Controls who can see event details.

**Values:**
- `default` - Use calendar's default visibility
- `public` - Anyone can see full event details
- `private` - Only you can see event details
- `confidential` - Others see time blocked but no details

**Example:**
```bash
poetry run gwc-cal create \
  --time "2025-01-20T14:00:00-07:00" \
  --subject "Personal Appointment" \
  --duration 60 \
  --visibility private
```

---

## Guest Notifications

Control whether attendees receive email notifications.

**Values:**
- `all` - Notify all guests (default for new events)
- `externalOnly` - Only notify external guests (outside your domain)
- `none` - Don't send notifications

**Example:**
```bash
poetry run gwc-cal update abc123def456 \
  --add-attendee "alice@company.com" \
  --notify all
```

---

## Working with Multiple Calendars

By default, all commands operate on your primary calendar. To use a different calendar:

1. **List all calendars:**
   ```bash
   poetry run gwc-cal list --output llm
   ```

2. **Use specific calendar:**
   ```bash
   poetry run gwc-cal create \
     --time "2025-01-20T14:00:00-07:00" \
     --subject "Team Event" \
     --calendar "team@company.com"
   ```

3. **Set default calendar:**
   ```bash
   poetry run gwc-cal config set default_calendar "work@company.com"
   ```

---

## Date/Time Format

**ISO8601 format:** `YYYY-MM-DDTHH:MM:SS[TIMEZONE]`

**Examples:**
- `2025-01-20T14:00:00-07:00` - 2:00 PM Mountain Time
- `2025-01-20T14:00:00` - 2:00 PM (uses calendar's timezone)
- `2025-01-20T14:00:00+00:00` - 2:00 PM UTC
- `2025-01-20T14:00:00Z` - 2:00 PM UTC (Z = Zulu time)

**Date-only** (for `find --start/--end`):
- `2025-01-20` - Midnight on Jan 20, 2025

**IMPORTANT:** Always include timezone offset (`-07:00`) to avoid confusion!

---

## Output Formats

**Unix format** (default):
- Tab-separated values
- Good for scripting with `awk`, `cut`, etc.

**JSON format:**
- Complete event data in JSON
- Good for parsing with `jq` or Python

**LLM format:**
- Human-readable, well-formatted
- Best for interactive use and reviewing events

**Example:**
```bash
# Human-readable
poetry run gwc-cal find --output llm

# Parse with jq
poetry run gwc-cal find --output json | jq '.[] | .summary'
```

---

## Configuration Files

**Location:** `~/.config/gwc/`

**Files:**
- `credentials.json` - OAuth2 credentials from Google Cloud Console
- `token.json` - Access/refresh tokens (auto-managed)
- `config.json` - User configuration (default calendar, etc.)

**To reset authentication:**
```bash
rm ~/.config/gwc/token.json
poetry run gwc-cal auth
```

---

## Tips & Tricks

**1. Always use `--output llm` when reviewing events:**
```bash
poetry run gwc-cal find --output llm
```

**2. When updating times, update duration too:**
```bash
# BAD - changes start but not end
poetry run gwc-cal update abc123 --time "2025-01-20T15:00:00-07:00"

# GOOD - keeps duration consistent
poetry run gwc-cal update abc123 --time "2025-01-20T15:00:00-07:00" --duration 60
```

**3. Use `--notify all` when adding/removing attendees:**
```bash
poetry run gwc-cal update abc123 --add-attendee "alice@company.com" --notify all
```

**4. Create "hold" events with transparent:**
```bash
poetry run gwc-cal create \
  --time "2025-01-20T14:00:00-07:00" \
  --subject "Hold for potential meeting" \
  --duration 60 \
  --transparency transparent
```

**5. Search for recurring meetings:**
```bash
poetry run gwc-cal find --query "standup" --output llm
```

**6. Use description files for long agendas:**
```bash
echo "1. Review last week\n2. Plan this week\n3. Blockers" > /tmp/agenda.txt
poetry run gwc-cal create \
  --time "2025-01-20T09:00:00-07:00" \
  --subject "Team Sync" \
  --description-file /tmp/agenda.txt
```

---

## Common Workflows

### Morning Briefing - Get Today's Events
```bash
TODAY=$(date +%Y-%m-%d)
TOMORROW=$(date -d "+1 day" +%Y-%m-%d)
poetry run gwc-cal find --start "$TODAY" --end "$TOMORROW" --output llm
```

### Schedule Coffee Meeting
```bash
poetry run gwc-cal create \
  --time "2025-01-20T14:30:00-07:00" \
  --subject "Coffee with John" \
  --duration 90 \
  --location "Starbucks on Main St" \
  --attendees "john@company.com" \
  --transparency transparent
```

### Create Recurring Standup
```bash
poetry run gwc-cal create \
  --time "2025-01-20T09:00:00-07:00" \
  --subject "Daily Standup" \
  --duration 15 \
  --recurrence "weekly:MO,TU,WE,TH,FR" \
  --meet \
  --attendees "team@company.com"
```

### Block Focus Time
```bash
poetry run gwc-cal create \
  --time "2025-01-20T09:00:00-07:00" \
  --subject "Deep Work - Do Not Disturb" \
  --duration 180 \
  --transparency opaque \
  --visibility private
```

### Reschedule Meeting
```bash
# Get event ID first
poetry run gwc-cal find --query "Team Meeting" --output llm

# Update time (keep duration!)
poetry run gwc-cal update abc123def456 \
  --time "2025-01-21T14:00:00-07:00" \
  --duration 60 \
  --notify all
```
