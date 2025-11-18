# Command to API Mapping (CMD_API.md)

This document maps `gwc-cal` CLI commands to Google Calendar API v3 REST endpoints and operations.

## Overview

The Google Calendar API v3 provides 8 resource types:
- **Calendars** - Calendar metadata and operations
- **CalendarList** - User's calendar subscriptions
- **Events** - Calendar events
- **Acl** - Access control lists
- **Colors** - Color definitions
- **Freebusy** - Availability/scheduling data
- **Settings** - User settings
- **Channels** - Webhook subscriptions

For Phase 1, we focus on **Calendars** and **Events** resources.

## gwc-cal Commands → API Mapping

### Calendar Management

#### `gwc-cal list`
**Purpose**: List available calendars
**API Call**: `calendarList.list()`
**Endpoint**: `GET /users/me/calendarList`
**Returns**: List of calendars the user has access to
**Output Fields**: id, summary, description, timeZone, primary, backgroundColor

**Example Response**:
```
primary (Primary Calendar)
shared-calendar (Team Meetings)
holidays (US Holidays)
```

---

#### `gwc-cal get <calendar-id>`
**Purpose**: Get calendar details
**API Call**: `calendars.get(calendarId)`
**Endpoint**: `GET /calendars/{calendarId}`
**Returns**: Calendar metadata
**Output Fields**: id, summary, description, timeZone, primary

---

### Event Management

#### `gwc-cal create`
**Purpose**: Create a new event
**API Call**: `events.insert(calendarId, body)`
**Endpoint**: `POST /calendars/{calendarId}/events`

**Required Parameters**:
- `--time <ISO8601>` → `start.dateTime`
- `--subject <string>` → `summary`

**Optional Parameters**:
- `--duration <minutes>` → Calculates `end.dateTime` from start + duration (default: 60)
- `--attendees <email>,<email>,...` → `attendees[].email`
- `--description <string>` → `description`
- `--calendar <id>` → `calendarId` (default: "primary")

**Request Body Structure**:
```json
{
  "summary": "Team Meeting",
  "description": "Quarterly planning",
  "start": {
    "dateTime": "2025-01-15T14:00:00",
    "timeZone": "America/New_York"
  },
  "end": {
    "dateTime": "2025-01-15T15:00:00",
    "timeZone": "America/New_York"
  },
  "attendees": [
    {"email": "user@example.com"},
    {"email": "colleague@example.com"}
  ]
}
```

**Returns**: Created event object with id, start, end, summary, etc.

---

#### `gwc-cal get <event-id>`
**Purpose**: Get event details
**API Call**: `events.get(calendarId, eventId)`
**Endpoint**: `GET /calendars/{calendarId}/events/{eventId}`
**Returns**: Event object with all details

---

#### `gwc-cal update <event-id>`
**Purpose**: Update an existing event
**API Call**: `events.patch(calendarId, eventId, body)` or `events.update(...)`
**Endpoint**: `PATCH /calendars/{calendarId}/events/{eventId}` or `PUT /calendars/{calendarId}/events/{eventId}`

**Optional Parameters**: Same as create (--time, --subject, --duration, --attendees, --description)
**Calendar Flag**: `--calendar <id>` (default: "primary")

**Notes**:
- Use PATCH to update only specified fields
- Use PUT to replace entire event (we'll use PATCH for partial updates)

---

#### `gwc-cal delete <event-id>`
**Purpose**: Delete an event
**API Call**: `events.delete(calendarId, eventId)`
**Endpoint**: `DELETE /calendars/{calendarId}/events/{eventId}`
**Returns**: 204 No Content (success)

---

#### `gwc-cal find`
**Purpose**: Search/filter events in a calendar or date range
**API Call**: `events.list(calendarId, ...)`
**Endpoint**: `GET /calendars/{calendarId}/events`

**Optional Parameters**:
- `--start <ISO8601>` → `timeMin` (default: today)
- `--end <ISO8601>` → `timeMax` (default: +7 days from start)
- `--query <string>` → `q` (full-text search on summary and description)
- `--calendar <id>` → `calendarId` (default: "primary")

**Query Parameters**:
```
GET /calendars/primary/events?timeMin=2025-01-15T00:00:00&timeMax=2025-01-22T00:00:00&q=meeting
```

**Returns**: List of matching events

---

### Advanced Operations (Phase 2+)

#### `gwc-cal freebusy`
**Purpose**: Check availability across calendars
**API Call**: `freebusy.query(body)`
**Endpoint**: `POST /freeBusy`
**Use Case**: Find available time slots across multiple calendars

---

#### `gwc-cal move <event-id>`
**Purpose**: Move event to another calendar
**API Call**: `events.move(calendarId, eventId, destination)`
**Endpoint**: `POST /calendars/{calendarId}/events/{eventId}/move`
**Parameters**: `--to <calendar-id>`

---

## Output Format Mapping

### Unix Format (Default)
Line-oriented output, one item per line. For lists, suitable for piping.

**Example** (`gwc-cal list`):
```
primary	Primary Calendar	America/New_York
team	Team Calendar	America/New_York
holidays	US Holidays	America/Los_Angeles
```

**Example** (`gwc-cal find`):
```
event1	Team Meeting	2025-01-15T14:00:00	2025-01-15T15:00:00
event2	1:1 Sync	2025-01-16T10:00:00	2025-01-16T10:30:00
```

### JSON Format
Pretty-printed JSON objects, one per item or array.

**Example** (`gwc-cal list`):
```json
[
  {
    "id": "primary",
    "summary": "Primary Calendar",
    "timeZone": "America/New_York",
    "primary": true
  },
  {
    "id": "team",
    "summary": "Team Calendar",
    "timeZone": "America/New_York"
  }
]
```

### LLM-Pretty Format
Human-readable, verbose output optimized for LLM consumption.

**Example** (`gwc-cal list`):
```
Available Calendars:

1. Primary Calendar (primary)
   Timezone: America/New_York
   Type: Primary calendar

2. Team Calendar (team)
   Timezone: America/New_York
   Type: Shared calendar

3. US Holidays (holidays)
   Timezone: America/Los_Angeles
   Type: Holiday calendar
```

---

## Error Handling

### No Authentication
```
Error: No valid Google Workspace credentials found.
Run 'gwc auth' to authenticate.
```

### Calendar Not Found
```
Error: Calendar 'invalid-id' not found.
Available calendars: primary, team, holidays
```

### Invalid Time Format
```
Error: Invalid ISO8601 timestamp: 'tomorrow at 2pm'
Expected format: 2025-01-15T14:00:00 or 2025-01-15T14:00:00+05:00
```

### API Error
```
Error: Google Calendar API error: Permission denied
(Ensure you have access to this calendar)
```

---

## Implementation Notes

1. **Timezone Handling**:
   - Always use ISO8601 with timezone information
   - Default to user's primary calendar timezone if not specified
   - Store timezone info in event objects for proper handling

2. **Calendar ID**:
   - Special ID "primary" refers to user's primary calendar
   - Calendar IDs are email addresses for shared calendars
   - Always accept both special ID and full email

3. **Attendee Handling (Phase 1)**:
   - Accept email list, no validation against People API yet
   - Future: Integrate with People API to search by name

4. **Recurring Events (Phase 2)**:
   - Support `--recurrence` flag with RRULE format
   - Map to `recurrence` field in event body
   - Handle `--instances` to fetch occurrences

5. **Google Meet Integration (Phase 2+)**:
   - Support `--meet` flag to auto-add Meet link
   - Use `conferenceData` field with `generateConferenceRequest`

6. **Pagination (Phase 2)**:
   - Implement `--limit` and `--page` for large result sets
   - Use `pageToken` for efficient pagination
