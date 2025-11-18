# Google Calendar API Implementation Plan

## Overview

The Google Calendar API v3 provides programmatic access to Google Calendar for managing calendars, events, and scheduling operations. The calendar API is designed for creating, reading, updating, and deleting calendar events with full support for attendees, reminders, and recurring events.

**API Reference:** https://developers.google.com/workspace/calendar/api/v3/reference

## Core Resources

The Google Calendar API consists of two primary REST resources:

### 1. **CalendarList** (Calendar Management)
- **list** - Lists user's calendars
- **get** - Retrieves specific calendar
- **insert** - Creates new calendar
- **update** - Modifies calendar
- **delete** - Removes calendar

### 2. **Events** (Event Management)
- **create** - Creates new event
- **get** - Retrieves event details
- **update** - Modifies event
- **delete** - Removes event
- **list** - Lists events
- **quickAdd** - Creates event from text
- **import** - Imports external events

## Calendar Structure

### Calendar Properties
- **Title** - Calendar display name
- **Description** - Calendar information
- **TimeZone** - Calendar timezone
- **Visibility** - Public/Private
- **Color** - Display color
- **Location** - Calendar location (optional)

### Event Properties
- **Title/Summary** - Event name
- **Description** - Event details
- **Start/End Time** - ISO8601 format with timezone
- **Attendees** - List of participants
- **Organizer** - Event creator
- **Location** - Event location
- **Recurrence** - Recurring patterns (RRULE)
- **Reminders** - Notification settings
- **Status** - Confirmed/Tentative/Cancelled
- **Visibility** - Public/Private/Confidential
- **Calendar ID** - Which calendar contains event

## Implementation Phases

### Phase 1: Core Event Operations ✅
**Commands:** `gwc-cal create`, `get`, `find`, `list`

**Features:**
- Create events with basic properties
- Get event details
- Find events by date range
- List available calendars
- Support for timezones
- ISO8601 time format

**Key Parameters:**
- `--time TEXT` - Event start time (ISO8601)
- `--subject TEXT` - Event title
- `--duration INTEGER` - Duration in minutes
- `--attendees TEXT` - Comma-separated emails
- `--description TEXT` - Event details
- `--calendar TEXT` - Calendar ID (defaults to primary)

**Use Cases:**
- Schedule meetings programmatically
- Create calendar entries from external data
- Query upcoming events
- Integration with scheduling systems

### Phase 2: Event Modification & Management ✅
**Commands:** `gwc-cal update`, `delete`, `modify-recurrence`

**Features:**
- Update event properties
- Delete events
- Manage recurring events
- Handle attendee responses
- Update reminders
- Modify visibility/status

**Key Parameters:**
- `--event-id TEXT` - Event identifier
- `--start-time TEXT` - New start time
- `--end-time TEXT` - New end time
- `--add-attendee EMAIL` - Add participant
- `--remove-attendee EMAIL` - Remove participant
- `--set-reminder MINUTES` - Notification timing

**Use Cases:**
- Update event details
- Reschedule meetings
- Manage attendees
- Change event visibility
- Cancel events

## Event Time Format

The API uses ISO8601 format with explicit timezone offset:

```
2025-01-20T14:00:00-07:00
```

**Components:**
- `2025-01-20` - Date (YYYY-MM-DD)
- `T` - Date/time separator
- `14:00:00` - Time (HH:MM:SS)
- `-07:00` - Timezone offset (±HH:MM)

**Common Timezone Offsets:**
- Mountain Time: `-07:00` (or `-06:00` during DST)
- Pacific Time: `-08:00` (or `-07:00` during DST)
- Eastern Time: `-05:00` (or `-04:00` during DST)
- Central Time: `-06:00` (or `-05:00` during DST)
- UTC: `Z`

## Recurrence Rules

Recurring events use iCalendar RRULE format:

```
RRULE:FREQ=WEEKLY;BYDAY=MO,WE,FR;COUNT=10
RRULE:FREQ=DAILY;INTERVAL=2;UNTIL=20250630
RRULE:FREQ=MONTHLY;BYMONTHDAY=15
```

**Frequency Options:**
- `DAILY` - Every day
- `WEEKLY` - Every week
- `MONTHLY` - Every month
- `YEARLY` - Every year
- `HOURLY` - Every hour

## Comparison with Other APIs

| Feature | Calendar | Sheets | Docs |
|---------|----------|--------|------|
| **Time-based** | Native | No | No |
| **Recurrence** | Native | No | No |
| **Attendees** | Native | No | No |
| **Reminders** | Native | No | No |
| **Collaborative** | Native | Via Drive | Native |
| **Data format** | Events | Tabular | Documents |

## Output Formats

All commands support:
- `--output unix` - Tab-separated (default, for scripting)
- `--output json` - JSON (for programmatic parsing)
- `--output llm` - Human-readable (recommended for humans)

## Common Use Cases

### 1. Schedule Meeting
```bash
gwc-cal create \
  --subject "Team Standup" \
  --time "2025-01-20T09:00:00-07:00" \
  --duration 15 \
  --attendees "alice@example.com,bob@example.com"
```

### 2. Find Next Week's Events
```bash
gwc-cal find \
  --start-date "2025-01-20" \
  --end-date "2025-01-27" \
  --output llm
```

### 3. Create Recurring Meeting
```bash
# Create base event, then set recurrence
gwc-cal create --subject "Weekly Sync" --time "2025-01-20T10:00:00Z" --duration 60
# Use update to add: --recurrence "RRULE:FREQ=WEEKLY;BYDAY=MO"
```

### 4. Reschedule Event
```bash
gwc-cal update event_id \
  --start-time "2025-01-21T14:00:00-07:00" \
  --end-time "2025-01-21T15:00:00-07:00"
```

## API Limits & Considerations

1. **Rate Limits:**
   - 1,000,000 queries per day per user
   - 1,000 qps (queries per second) per user

2. **Event Properties:**
   - Maximum 256 attendees per event
   - Description limited to 8,192 characters
   - Title limited to 255 characters

3. **Time Zones:**
   - Must use valid timezone identifiers (IANA format)
   - Or explicit offsets (±HH:MM)

4. **Recurrence:**
   - Limited to 2,000 instances
   - Some RRULE combinations may be rejected

5. **Attendees:**
   - Supports internal and external attendees
   - Organizer automatically included
   - Status can be: accepted, tentative, declined, needsAction

## Unique Aspects

**Strengths:**
1. Native time/date handling
2. Recurrence rule support
3. Attendee management
4. Timezone awareness
5. Multiple reminder options
6. Event visibility control

**Limitations:**
1. No custom fields
2. No repeating tasks (only recurring events)
3. Event color limited to predefined set
4. No event dependencies
5. Attendee response tracking limited

## MIME Types

- Calendar: `application/vnd.google-apps.calendar` (not applicable - GCal is service, not file)
- Events: Stored in Calendar service

## Next Steps

1. **Phase 1**: Core event operations ✅
2. **Phase 2**: Event modification and management ✅
3. **Consider Phase 3**: Advanced features
   - Event resources/equipment
   - Availability checking
   - Scheduling hints
   - Organizer/attendee analytics
