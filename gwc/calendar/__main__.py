"""Google Calendar CLI (gwc-cal)."""

import sys
import click

from ..shared.exceptions import GwcError, AuthenticationError, ValidationError
from ..shared.output import OutputFormat, format_output
from ..shared.auth import authenticate_interactive, refresh_token
from . import operations


@click.group()
@click.version_option()
def main():
    """Google Calendar CLI - Manage Google Calendar from the command line."""
    pass


@main.command()
@click.option(
    '--refresh',
    is_flag=True,
    help='Refresh an existing token instead of performing initial authentication.'
)
def auth(refresh):
    """Authenticate with Google Workspace.

    Without --refresh: Performs initial OAuth2 setup. Prints authorization URL
    and guides you through the authentication flow.

    With --refresh: Refreshes an existing token.
    """
    try:
        if refresh:
            refresh_token()
        else:
            authenticate_interactive()
            click.echo("Authentication successful! Token saved.")
    except GwcError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.option(
    '--output',
    type=click.Choice(['unix', 'json', 'llm']),
    default='unix',
    help='Output format (default: unix)'
)
def list(output):
    """List available calendars.

    Shows all calendars you have access to with their IDs, names, and timezones.
    """
    try:
        calendars = operations.list_calendars()

        if not calendars:
            click.echo("No calendars found.")
            return

        format_type = OutputFormat(output)

        # Define fields to display
        fields = ['id', 'summary', 'timeZone', 'primary']
        headers = ['ID', 'Name', 'Timezone', 'Primary']

        # Filter to only requested fields
        filtered = []
        for cal in calendars:
            filtered_cal = {f: cal.get(f, '') for f in fields}
            filtered.append(filtered_cal)

        output_str = format_output(filtered, format_type, fields, headers)
        click.echo(output_str)

    except GwcError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.option(
    '--time',
    required=True,
    help='Event start time in ISO8601 format (e.g., 2025-01-15T14:00:00)'
)
@click.option(
    '--subject',
    required=True,
    help='Event title/subject'
)
@click.option(
    '--duration',
    type=int,
    default=60,
    help='Event duration in minutes (default: 60)'
)
@click.option(
    '--attendees',
    help='Comma-separated list of attendee email addresses'
)
@click.option(
    '--description',
    help='Event description'
)
@click.option(
    '--calendar',
    default='primary',
    help='Calendar ID (default: primary)'
)
@click.option(
    '--output',
    type=click.Choice(['unix', 'json', 'llm']),
    default='unix',
    help='Output format (default: unix)'
)
def create(time, subject, duration, attendees, description, calendar, output):
    """Create a new calendar event.

    Example:
        gwc-cal create --time 2025-01-15T14:00:00 --subject "Team Meeting"
    """
    try:
        # Parse attendees
        attendee_list = None
        if attendees:
            attendee_list = [a.strip() for a in attendees.split(',')]

        event = operations.create_event(
            subject=subject,
            start_time=time,
            duration_minutes=duration,
            description=description,
            attendees=attendee_list,
            calendar_id=calendar
        )

        format_type = OutputFormat(output)
        fields = ['id', 'summary', 'start', 'end', 'organizer', 'status']
        output_str = format_output(event, format_type, fields)
        click.echo(output_str)

    except (ValidationError, AuthenticationError) as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except GwcError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.argument('event_id')
@click.option(
    '--calendar',
    default='primary',
    help='Calendar ID (default: primary)'
)
@click.option(
    '--output',
    type=click.Choice(['unix', 'json', 'llm']),
    default='unix',
    help='Output format (default: unix)'
)
def get(event_id, calendar, output):
    """Get event details.

    Example:
        gwc-cal get abc123def456
    """
    try:
        event = operations.get_event(event_id, calendar_id=calendar)

        format_type = OutputFormat(output)
        fields = ['id', 'summary', 'start', 'end', 'description', 'attendees', 'status']
        output_str = format_output(event, format_type, fields)
        click.echo(output_str)

    except GwcError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.argument('event_id')
@click.option(
    '--time',
    help='New event start time in ISO8601 format'
)
@click.option(
    '--subject',
    help='New event title'
)
@click.option(
    '--duration',
    type=int,
    help='New event duration in minutes'
)
@click.option(
    '--attendees',
    help='Comma-separated list of attendee email addresses'
)
@click.option(
    '--description',
    help='New event description'
)
@click.option(
    '--calendar',
    default='primary',
    help='Calendar ID (default: primary)'
)
@click.option(
    '--output',
    type=click.Choice(['unix', 'json', 'llm']),
    default='unix',
    help='Output format (default: unix)'
)
def update(event_id, time, subject, duration, attendees, description, calendar, output):
    """Update a calendar event.

    Only specified fields are updated.

    Example:
        gwc-cal update abc123def456 --subject "New Title"
    """
    try:
        # Parse attendees
        attendee_list = None
        if attendees:
            attendee_list = [a.strip() for a in attendees.split(',')]

        event = operations.update_event(
            event_id=event_id,
            subject=subject,
            start_time=time,
            duration_minutes=duration,
            description=description,
            attendees=attendee_list,
            calendar_id=calendar
        )

        format_type = OutputFormat(output)
        fields = ['id', 'summary', 'start', 'end', 'status']
        output_str = format_output(event, format_type, fields)
        click.echo(output_str)

    except (ValidationError, AuthenticationError) as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except GwcError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.argument('event_id')
@click.option(
    '--calendar',
    default='primary',
    help='Calendar ID (default: primary)'
)
def delete(event_id, calendar):
    """Delete a calendar event.

    Example:
        gwc-cal delete abc123def456
    """
    try:
        operations.delete_event(event_id, calendar_id=calendar)
        click.echo(f"Event '{event_id}' deleted.")

    except GwcError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.option(
    '--start',
    help='Start date in ISO8601 format (default: today)'
)
@click.option(
    '--end',
    help='End date in ISO8601 format (default: start + 7 days)'
)
@click.option(
    '--query',
    help='Search query (searches event title and description)'
)
@click.option(
    '--calendar',
    default='primary',
    help='Calendar ID (default: primary)'
)
@click.option(
    '--output',
    type=click.Choice(['unix', 'json', 'llm']),
    default='unix',
    help='Output format (default: unix)'
)
def find(start, end, query, calendar, output):
    """Find events in a calendar.

    Lists events within a date range, optionally filtered by search query.

    Examples:
        gwc-cal find
        gwc-cal find --start 2025-01-15 --end 2025-01-22
        gwc-cal find --query "standup"
    """
    try:
        events = operations.find_events(
            start_date=start,
            end_date=end,
            query=query,
            calendar_id=calendar
        )

        if not events:
            click.echo("No events found.")
            return

        format_type = OutputFormat(output)
        fields = ['id', 'summary', 'start', 'end', 'organizer']
        output_str = format_output(events, format_type, fields)
        click.echo(output_str)

    except GwcError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
