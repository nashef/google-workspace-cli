---
name: calendar-advanced
description: Advanced calendar features (recurring events, reminders, attendee management)
---

# Advanced Calendar Features

For basic tasks, see **SKILL.md**. This document covers recurring events, advanced reminders, and attendee management.

## Recurring Events

Create events that repeat on a schedule using RRULE format.

**Weekly standup (Mon/Wed/Fri for 12 weeks):**
```bash
poetry run gwc-cal create \
  --time "2025-01-20T09:00:00-07:00" \
  --subject "Weekly Standup" \
  --duration 30 \
  --attendees "alice@company.com,bob@company.com" \
  --recurrence "FREQ=WEEKLY;BYDAY=MO,WE,FR;COUNT=12"
```

**Daily sync (weekdays only, 10 occurrences):**
```bash
poetry run gwc-cal create \
  --time "2025-01-20T10:00:00-07:00" \
  --subject "Daily Sync" \
  --duration 15 \
  --recurrence "FREQ=DAILY;BYDAY=MO,TU,WE,TH,FR;COUNT=10"
```

**Monthly on 15th:**
```bash
poetry run gwc-cal create \
  --time "2025-01-15T14:00:00-07:00" \
  --subject "Monthly Review" \
  --duration 60 \
  --recurrence "FREQ=MONTHLY;BYMONTHDAY=15;COUNT=12"
```

**Custom pattern (every 2 weeks until date):**
```bash
poetry run gwc-cal create \
  --time "2025-01-20T09:00:00-07:00" \
  --subject "Bi-weekly Check-in" \
  --duration 30 \
  --recurrence "FREQ=WEEKLY;INTERVAL=2;UNTIL=2025-12-31"
```

**RRULE syntax:**
- `FREQ=DAILY|WEEKLY|MONTHLY|YEARLY`
- `INTERVAL=n` - Every n units
- `BYDAY=MO,TU,WE,TH,FR,SA,SU` - Specific days
- `BYMONTHDAY=15` - Day of month
- `COUNT=n` - Stop after n occurrences
- `UNTIL=2025-12-31` - Stop on date

## Reminders

Set multiple reminders for events.

```bash
poetry run gwc-cal create \
  --time "2025-01-20T14:00:00-07:00" \
  --subject "Important Meeting" \
  --duration 60 \
  --reminder "15 minutes" \
  --reminder "1 day" \
  --reminder "1 hour"
```

**Reminder syntax:**
- `"5 minutes"`
- `"30 minutes"`
- `"1 hour"`
- `"1 day"`
- `"1 week"`

Reminders are sent as notifications to configured methods (email, popup, etc).

## Attendee Management

Add or remove attendees from events.

**Add attendee to existing event:**
```bash
poetry run gwc-cal update event_id \
  --add-attendee "newperson@company.com" \
  --notify all
```

**Remove attendee:**
```bash
poetry run gwc-cal update event_id \
  --remove-attendee "person@company.com"
```

**Add multiple attendees:**
```bash
poetry run gwc-cal update event_id \
  --add-attendee "alice@company.com" \
  --add-attendee "bob@company.com" \
  --add-attendee "charlie@company.com"
```

**Notification options:**
- `--notify all` - Notify all attendees
- `--notify externalOnly` - Notify external attendees only
- `--notify none` - No notifications

## Visibility & Transparency

Control how events appear in your calendar.

```bash
# Show as busy (default)
poetry run gwc-cal create \
  --time "2025-01-20T14:00:00-07:00" \
  --subject "Meeting" \
  --duration 60 \
  --transparency opaque

# Show as free (don't block time)
poetry run gwc-cal create \
  --time "2025-01-20T14:00:00-07:00" \
  --subject "FYI Event" \
  --duration 60 \
  --transparency transparent
```

## Google Meet

Automatically add Google Meet conference link.

```bash
poetry run gwc-cal create \
  --time "2025-01-20T14:00:00-07:00" \
  --subject "Video Meeting" \
  --duration 60 \
  --attendees "alice@company.com" \
  --meet
```

## Timezone Management

Calendar works in ISO8601 with explicit timezone offsets.

**Examples:**
- Mountain Time: `2025-01-20T14:00:00-07:00`
- Pacific Time: `2025-01-20T14:00:00-08:00`
- Eastern Time: `2025-01-20T14:00:00-05:00`
- UTC: `2025-01-20T21:00:00Z`

When updating times, always include duration to maintain end time:
```bash
poetry run gwc-cal update event_id \
  --time "2025-01-20T15:00:00-07:00" \
  --duration 60
```

## Command Reference

| Command | Purpose |
|---------|---------|
| `list` | Show all calendars |
| `create` | Create new event |
| `update` | Modify event |
| `delete` | Remove event |
| `find` | Search/list events in date range |
| `get` | Get event details |

See **REFERENCE.md** for complete option documentation.
