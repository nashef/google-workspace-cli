"""Google Calendar API operations."""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import pytz

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from ..shared.auth import get_credentials, CALENDAR_SCOPES
from ..shared.exceptions import APIError, ValidationError


def build_calendar_service():
    """Build and return Calendar API service object."""
    creds = get_credentials(scopes=CALENDAR_SCOPES)
    return build("calendar", "v3", credentials=creds)


def list_calendars() -> List[Dict[str, Any]]:
    """List all available calendars.

    Returns:
        List of calendar objects with id, summary, timezone, etc.
    """
    service = build_calendar_service()

    try:
        result = service.calendarList().list().execute()
        return result.get('items', [])
    except HttpError as e:
        raise APIError(f"Failed to list calendars: {e}")


def get_calendar(calendar_id: str) -> Dict[str, Any]:
    """Get calendar details.

    Args:
        calendar_id: Calendar ID (e.g., "primary" or email)

    Returns:
        Calendar object
    """
    service = build_calendar_service()

    try:
        result = service.calendars().get(calendarId=calendar_id).execute()
        return result
    except HttpError as e:
        raise APIError(f"Failed to get calendar '{calendar_id}': {e}")


def validate_iso8601(timestamp: str) -> datetime:
    """Validate and parse ISO8601 timestamp.

    Args:
        timestamp: ISO8601 formatted timestamp (with optional timezone)

    Returns:
        datetime object

    Raises:
        ValidationError: If format is invalid
    """
    formats = [
        "%Y-%m-%dT%H:%M:%S%z",      # With timezone
        "%Y-%m-%dT%H:%M:%S",        # Without timezone
        "%Y-%m-%d",                 # Date only
    ]

    for fmt in formats:
        try:
            return datetime.strptime(timestamp, fmt)
        except ValueError:
            continue

    # Try ISO8601 with colon in timezone
    try:
        # Python 3.7+ handles timezone offset with colon
        return datetime.fromisoformat(timestamp)
    except (ValueError, AttributeError):
        pass

    raise ValidationError(
        f"Invalid ISO8601 timestamp: '{timestamp}'\n"
        f"Expected format: 2025-01-15T14:00:00 or 2025-01-15T14:00:00+05:00"
    )


def create_event(
    subject: str,
    start_time: str,
    duration_minutes: int = 60,
    description: Optional[str] = None,
    attendees: Optional[List[str]] = None,
    add_meet: bool = False,
    location: Optional[str] = None,
    transparency: Optional[str] = None,
    visibility: Optional[str] = None,
    send_updates: Optional[str] = None,
    calendar_id: str = "primary"
) -> Dict[str, Any]:
    """Create a calendar event.

    Args:
        subject: Event title
        start_time: Start time in ISO8601 format
        duration_minutes: Duration in minutes (default 60)
        description: Event description
        attendees: List of attendee email addresses
        add_meet: Whether to add a Google Meet conference (default False)
        location: Event location (freeform text or address)
        transparency: "opaque" (busy) or "transparent" (free)
        visibility: "default", "public", "private", or "confidential"
        send_updates: "all", "externalOnly", or "none" - notify guests
        calendar_id: Calendar ID (default "primary")

    Returns:
        Created event object

    Raises:
        ValidationError: If input is invalid
        APIError: If API call fails
    """
    # Validate and parse start time
    start_dt = validate_iso8601(start_time)

    # Add timezone if missing
    if start_dt.tzinfo is None:
        # Use primary calendar's timezone, or UTC if not available
        try:
            calendars = list_calendars()
            primary = next((c for c in calendars if c.get('primary')), None)
            tz_str = primary.get('timeZone', 'UTC') if primary else 'UTC'
            tz = pytz.timezone(tz_str)
        except Exception:
            tz = pytz.UTC

        start_dt = tz.localize(start_dt)

    # Calculate end time
    end_dt = start_dt + timedelta(minutes=duration_minutes)

    # Build event object
    event = {
        'summary': subject,
        'start': {
            'dateTime': start_dt.isoformat(),
            'timeZone': str(start_dt.tzinfo) if start_dt.tzinfo else 'UTC'
        },
        'end': {
            'dateTime': end_dt.isoformat(),
            'timeZone': str(end_dt.tzinfo) if end_dt.tzinfo else 'UTC'
        }
    }

    if description:
        event['description'] = description

    if location:
        event['location'] = location

    if attendees:
        event['attendees'] = [{'email': email.strip()} for email in attendees]

    if transparency:
        if transparency not in ('opaque', 'transparent'):
            raise ValidationError(f"transparency must be 'opaque' or 'transparent', got '{transparency}'")
        event['transparency'] = transparency

    if visibility:
        if visibility not in ('default', 'public', 'private', 'confidential'):
            raise ValidationError(f"visibility must be one of: default, public, private, confidential (got '{visibility}')")
        event['visibility'] = visibility

    if add_meet:
        event['conferenceData'] = {
            'createRequest': {
                'requestId': 'gwc-' + event['start']['dateTime'],
                'conferenceSolutionKey': {
                    'type': 'hangoutsMeet'
                }
            }
        }

    # Create event
    service = build_calendar_service()

    try:
        kwargs = {
            'calendarId': calendar_id,
            'body': event,
            'conferenceDataVersion': 1 if add_meet else 0
        }
        if send_updates:
            kwargs['sendUpdates'] = send_updates

        result = service.events().insert(**kwargs).execute()
        return result
    except HttpError as e:
        raise APIError(f"Failed to create event: {e}")


def get_event(event_id: str, calendar_id: str = "primary") -> Dict[str, Any]:
    """Get event details.

    Args:
        event_id: Event ID
        calendar_id: Calendar ID (default "primary")

    Returns:
        Event object
    """
    service = build_calendar_service()

    try:
        result = service.events().get(
            calendarId=calendar_id,
            eventId=event_id
        ).execute()
        return result
    except HttpError as e:
        raise APIError(f"Failed to get event '{event_id}': {e}")


def add_attendees(
    event_id: str,
    attendee_emails: List[str],
    calendar_id: str = "primary",
    send_updates: Optional[str] = None
) -> Dict[str, Any]:
    """Add attendees to an existing event.

    Args:
        event_id: Event ID
        attendee_emails: List of email addresses to add
        calendar_id: Calendar ID (default "primary")
        send_updates: "all", "externalOnly", or "none" - notify existing guests

    Returns:
        Updated event object
    """
    # Get existing event
    event = get_event(event_id, calendar_id)

    # Get existing attendees
    existing_emails = set()
    if 'attendees' in event:
        existing_emails = {att['email'] for att in event['attendees']}

    # Add new attendees (avoiding duplicates)
    new_emails = set(att.strip() for att in attendee_emails)
    all_emails = existing_emails | new_emails

    # Update event with full attendee list
    service = build_calendar_service()
    event['attendees'] = [{'email': email} for email in sorted(all_emails)]

    try:
        kwargs = {
            'calendarId': calendar_id,
            'eventId': event_id,
            'body': event
        }
        if send_updates:
            kwargs['sendUpdates'] = send_updates

        result = service.events().patch(**kwargs).execute()
        return result
    except HttpError as e:
        raise APIError(f"Failed to add attendees: {e}")


def remove_attendees(
    event_id: str,
    attendee_emails: List[str],
    calendar_id: str = "primary",
    send_updates: Optional[str] = None
) -> Dict[str, Any]:
    """Remove attendees from an existing event.

    Args:
        event_id: Event ID
        attendee_emails: List of email addresses to remove
        calendar_id: Calendar ID (default "primary")
        send_updates: "all", "externalOnly", or "none" - notify remaining guests

    Returns:
        Updated event object
    """
    # Get existing event
    event = get_event(event_id, calendar_id)

    # Get existing attendees
    if 'attendees' not in event:
        raise APIError("Event has no attendees to remove")

    existing_emails = {att['email'] for att in event['attendees']}

    # Remove specified attendees
    remove_set = set(att.strip() for att in attendee_emails)
    remaining_emails = existing_emails - remove_set

    if not remaining_emails:
        raise ValidationError("Cannot remove all attendees from event")

    # Update event with filtered attendee list
    service = build_calendar_service()
    event['attendees'] = [{'email': email} for email in sorted(remaining_emails)]

    try:
        kwargs = {
            'calendarId': calendar_id,
            'eventId': event_id,
            'body': event
        }
        if send_updates:
            kwargs['sendUpdates'] = send_updates

        result = service.events().patch(**kwargs).execute()
        return result
    except HttpError as e:
        raise APIError(f"Failed to remove attendees: {e}")


def update_event(
    event_id: str,
    subject: Optional[str] = None,
    start_time: Optional[str] = None,
    duration_minutes: Optional[int] = None,
    description: Optional[str] = None,
    attendees: Optional[List[str]] = None,
    add_meet: bool = False,
    location: Optional[str] = None,
    transparency: Optional[str] = None,
    visibility: Optional[str] = None,
    send_updates: Optional[str] = None,
    calendar_id: str = "primary"
) -> Dict[str, Any]:
    """Update a calendar event.

    Args:
        event_id: Event ID
        subject: New event title
        start_time: New start time in ISO8601
        duration_minutes: New duration in minutes
        description: New description
        attendees: New attendee list
        add_meet: Whether to add a Google Meet conference
        location: Event location (freeform text or address)
        transparency: "opaque" (busy) or "transparent" (free)
        visibility: "default", "public", "private", or "confidential"
        send_updates: "all", "externalOnly", or "none" - notify guests
        calendar_id: Calendar ID (default "primary")

    Returns:
        Updated event object
    """
    service = build_calendar_service()

    # Get existing event first
    event = get_event(event_id, calendar_id)

    # Update fields
    if subject:
        event['summary'] = subject

    if start_time:
        start_dt = validate_iso8601(start_time)
        if start_dt.tzinfo is None:
            tz = pytz.UTC
            start_dt = tz.localize(start_dt)
        event['start'] = {
            'dateTime': start_dt.isoformat(),
            'timeZone': str(start_dt.tzinfo) if start_dt.tzinfo else 'UTC'
        }

    if duration_minutes is not None and start_time:
        # Recalculate end time if duration is provided with new start time
        start_dt = validate_iso8601(start_time)
        if start_dt.tzinfo is None:
            tz = pytz.UTC
            start_dt = tz.localize(start_dt)
        end_dt = start_dt + timedelta(minutes=duration_minutes)
        event['end'] = {
            'dateTime': end_dt.isoformat(),
            'timeZone': str(start_dt.tzinfo) if start_dt.tzinfo else 'UTC'
        }

    if description:
        event['description'] = description

    if location:
        event['location'] = location

    if attendees is not None:
        event['attendees'] = [{'email': email.strip()} for email in attendees]

    if transparency:
        if transparency not in ('opaque', 'transparent'):
            raise ValidationError(f"transparency must be 'opaque' or 'transparent', got '{transparency}'")
        event['transparency'] = transparency

    if visibility:
        if visibility not in ('default', 'public', 'private', 'confidential'):
            raise ValidationError(f"visibility must be one of: default, public, private, confidential (got '{visibility}')")
        event['visibility'] = visibility

    if add_meet:
        event['conferenceData'] = {
            'createRequest': {
                'requestId': 'gwc-' + event_id,
                'conferenceSolutionKey': {
                    'type': 'hangoutsMeet'
                }
            }
        }

    # Perform update
    try:
        kwargs = {
            'calendarId': calendar_id,
            'eventId': event_id,
            'body': event,
            'conferenceDataVersion': 1 if add_meet else 0
        }
        if send_updates:
            kwargs['sendUpdates'] = send_updates

        result = service.events().patch(**kwargs).execute()
        return result
    except HttpError as e:
        raise APIError(f"Failed to update event: {e}")


def delete_event(event_id: str, calendar_id: str = "primary") -> None:
    """Delete a calendar event.

    Args:
        event_id: Event ID
        calendar_id: Calendar ID (default "primary")
    """
    service = build_calendar_service()

    try:
        service.events().delete(
            calendarId=calendar_id,
            eventId=event_id
        ).execute()
    except HttpError as e:
        raise APIError(f"Failed to delete event '{event_id}': {e}")


def find_events(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    query: Optional[str] = None,
    calendar_id: str = "primary"
) -> List[Dict[str, Any]]:
    """Find/list events in a calendar.

    Args:
        start_date: Start date in ISO8601 format (default: today)
        end_date: End date in ISO8601 format (default: start_date + 7 days)
        query: Search query (searches summary and description)
        calendar_id: Calendar ID (default "primary")

    Returns:
        List of matching events
    """
    service = build_calendar_service()

    # Default dates
    if start_date is None:
        start_dt = datetime.now(tz=pytz.UTC).replace(hour=0, minute=0, second=0, microsecond=0)
    else:
        start_dt = validate_iso8601(start_date)
        if start_dt.tzinfo is None:
            start_dt = pytz.UTC.localize(start_dt)

    if end_date is None:
        end_dt = start_dt + timedelta(days=7)
    else:
        end_dt = validate_iso8601(end_date)
        if end_dt.tzinfo is None:
            end_dt = pytz.UTC.localize(end_dt)

    # Build query
    kwargs = {
        'calendarId': calendar_id,
        'timeMin': start_dt.isoformat(),
        'timeMax': end_dt.isoformat(),
        'singleEvents': True,
        'orderBy': 'startTime'
    }

    if query:
        kwargs['q'] = query

    try:
        result = service.events().list(**kwargs).execute()
        return result.get('items', [])
    except HttpError as e:
        raise APIError(f"Failed to find events: {e}")
