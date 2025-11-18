"""Google Calendar CLI (gwc-cal)."""

import sys
import click

from ..shared.exceptions import GwcError, AuthenticationError, ValidationError, ConfigError
from ..shared.output import OutputFormat, format_output
from ..shared.auth import authenticate_interactive, refresh_token
from ..shared import config as config_module
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


@main.group()
def config():
    """Manage configuration settings.

    Store and retrieve configuration like default calendar, timezone, etc.
    """
    pass


@config.command('set')
@click.argument('key')
@click.argument('value')
def config_set(key, value):
    """Set a configuration value.

    Examples:
        gwc-cal config set default-calendar primary
        gwc-cal config set default-calendar "Foster family parenting plan"
    """
    try:
        config_module.set_config_value(key, value)
        click.echo(f"Set {key} = {value}")
    except GwcError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@config.command('get')
@click.argument('key')
def config_get(key):
    """Get a configuration value.

    Example:
        gwc-cal config get default-calendar
    """
    try:
        value = config_module.get_config_value(key)
        if value is None:
            click.echo(f"Configuration key '{key}' not set.")
        else:
            click.echo(value)
    except GwcError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@config.command('list')
def config_list():
    """List all configuration values."""
    try:
        all_config = config_module.load_config()
        if not all_config:
            click.echo("No configuration set.")
            return

        for key, value in sorted(all_config.items()):
            click.echo(f"{key} = {value}")
    except GwcError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@config.command('delete')
@click.argument('key')
def config_delete(key):
    """Delete a configuration value.

    Example:
        gwc-cal config delete default-calendar
    """
    try:
        config_module.delete_config_value(key)
        click.echo(f"Deleted {key}")
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
    '--meet',
    is_flag=True,
    help='Add a Google Meet conference to the event'
)
@click.option(
    '--location',
    help='Event location (address or room name)'
)
@click.option(
    '--transparency',
    type=click.Choice(['opaque', 'transparent']),
    help='opaque=busy (default), transparent=free'
)
@click.option(
    '--visibility',
    type=click.Choice(['default', 'public', 'private', 'confidential']),
    help='Event visibility (default: depends on calendar)'
)
@click.option(
    '--description-file',
    type=click.File('r'),
    help='Read event description from file'
)
@click.option(
    '--notify',
    type=click.Choice(['all', 'externalOnly', 'none']),
    help='Notify guests when creating event'
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
def create(time, subject, duration, attendees, description, meet, location, transparency, visibility, description_file, notify, calendar, output):
    """Create a new calendar event.

    Examples:
        gwc-cal create --time 2025-01-15T14:00:00 --subject "Team Meeting"
        gwc-cal create --time 2025-01-15T14:00:00 --subject "Team Meeting" --meet --location "Conf Room A"
        gwc-cal create --time 2025-01-15T14:00:00 --subject "Standup" --transparency transparent
    """
    try:
        # Parse attendees
        attendee_list = None
        if attendees:
            attendee_list = [a.strip() for a in attendees.split(',')]

        # Get description from file if provided, otherwise use inline
        final_description = description
        if description_file:
            final_description = description_file.read()

        event = operations.create_event(
            subject=subject,
            start_time=time,
            duration_minutes=duration,
            description=final_description,
            attendees=attendee_list,
            add_meet=meet,
            location=location,
            transparency=transparency,
            visibility=visibility,
            send_updates=notify,
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
    '--meet',
    is_flag=True,
    help='Add a Google Meet conference to the event'
)
@click.option(
    '--location',
    help='Event location (address or room name)'
)
@click.option(
    '--transparency',
    type=click.Choice(['opaque', 'transparent']),
    help='opaque=busy (default), transparent=free'
)
@click.option(
    '--visibility',
    type=click.Choice(['default', 'public', 'private', 'confidential']),
    help='Event visibility (default: depends on calendar)'
)
@click.option(
    '--description-file',
    type=click.File('r'),
    help='Read event description from file'
)
@click.option(
    '--notify',
    type=click.Choice(['all', 'externalOnly', 'none']),
    help='Notify guests when updating event'
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
def update(event_id, time, subject, duration, attendees, description, meet, location, transparency, visibility, description_file, notify, calendar, output):
    """Update a calendar event.

    Only specified fields are updated.

    Examples:
        gwc-cal update abc123def456 --subject "New Title"
        gwc-cal update abc123def456 --meet --notify all
        gwc-cal update abc123def456 --location "Room 101" --notify externalOnly
    """
    try:
        # Parse attendees
        attendee_list = None
        if attendees:
            attendee_list = [a.strip() for a in attendees.split(',')]

        # Get description from file if provided, otherwise use inline
        final_description = description
        if description_file:
            final_description = description_file.read()

        event = operations.update_event(
            event_id=event_id,
            subject=subject,
            start_time=time,
            duration_minutes=duration,
            description=final_description,
            attendees=attendee_list,
            add_meet=meet,
            location=location,
            transparency=transparency,
            visibility=visibility,
            send_updates=notify,
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
