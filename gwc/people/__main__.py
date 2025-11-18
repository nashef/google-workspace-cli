"""Google People/Contacts CLI (gwc-people)."""

import sys
import click

from ..shared.exceptions import GwcError, AuthenticationError, ValidationError
from ..shared.output import OutputFormat, format_output
from ..shared.auth import authenticate_interactive, refresh_token
from . import operations


@click.group()
@click.version_option()
def main():
    """Google People CLI - Manage Google Contacts from the command line."""
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
@click.argument('query')
@click.option(
    '--limit',
    type=int,
    default=10,
    help='Maximum results to return (default: 10, max: 30)'
)
@click.option(
    '--output',
    type=click.Choice(['unix', 'json', 'llm']),
    default='unix',
    help='Output format (default: unix)'
)
def search(query, limit, output):
    """Search for contacts by name, email, phone, or organization.

    Examples:
        gwc-people search "john smith"
        gwc-people search "john@example.com" --limit 5
        gwc-people search "acme" --output json
    """
    try:
        if limit < 1 or limit > 30:
            click.echo("Error: Limit must be between 1 and 30", err=True)
            sys.exit(1)

        results = operations.search_contacts(query, page_size=limit)

        if not results:
            click.echo("No contacts found.")
            return

        # Extract contact list from results
        contacts = []
        for result in results:
            person = result.get('person', {})
            contacts.append({
                'resourceName': person.get('resourceName'),
                'displayName': person.get('names', [{}])[0].get('displayName', 'N/A'),
                'email': person.get('emailAddresses', [{}])[0].get('value', 'N/A'),
                'phone': person.get('phoneNumbers', [{}])[0].get('value', 'N/A') if person.get('phoneNumbers') else 'N/A',
            })

        format_type = OutputFormat(output)
        fields = ['displayName', 'email', 'phone', 'resourceName']
        headers = ['Name', 'Email', 'Phone', 'Resource Name']
        output_str = format_output(contacts, format_type, fields, headers)
        click.echo(output_str)

    except ValidationError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except GwcError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.argument('email_or_id')
@click.option(
    '--output',
    type=click.Choice(['unix', 'json', 'llm']),
    default='unix',
    help='Output format (default: unix)'
)
def get(email_or_id, output):
    """Get contact details by email address or resource name.

    Examples:
        gwc-people get "john@example.com"
        gwc-people get "people/c123456789" --output json
    """
    try:
        contact = operations.get_contact(email_or_id)

        format_type = OutputFormat(output)
        fields = ['names', 'emailAddresses', 'phoneNumbers', 'organizations', 'resourceName']
        output_str = format_output(contact, format_type, fields)
        click.echo(output_str)

    except ValidationError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except GwcError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.option(
    '--limit',
    type=int,
    default=100,
    help='Maximum contacts to return per page (default: 100, max: 1000)'
)
@click.option(
    '--sort',
    type=click.Choice(['LAST_MODIFIED_ASCENDING', 'LAST_MODIFIED_DESCENDING', 'FIRST_NAME_ASCENDING', 'LAST_NAME_ASCENDING']),
    help='Sort order for results'
)
@click.option(
    '--output',
    type=click.Choice(['unix', 'json', 'llm']),
    default='unix',
    help='Output format (default: unix)'
)
def list(limit, sort, output):
    """List your contacts.

    Examples:
        gwc-people list
        gwc-people list --limit 50 --sort FIRST_NAME_ASCENDING
        gwc-people list --output json
    """
    try:
        if limit < 1 or limit > 1000:
            click.echo("Error: Limit must be between 1 and 1000", err=True)
            sys.exit(1)

        result = operations.list_contacts(page_size=limit, sort_order=sort)
        connections = result.get('connections', [])

        if not connections:
            click.echo("No contacts found.")
            return

        # Format contacts for display
        contacts = []
        for person in connections:
            contacts.append({
                'displayName': person.get('names', [{}])[0].get('displayName', 'N/A'),
                'email': person.get('emailAddresses', [{}])[0].get('value', 'N/A') if person.get('emailAddresses') else 'N/A',
                'phone': person.get('phoneNumbers', [{}])[0].get('value', 'N/A') if person.get('phoneNumbers') else 'N/A',
                'organization': person.get('organizations', [{}])[0].get('name', 'N/A') if person.get('organizations') else 'N/A',
                'resourceName': person.get('resourceName'),
            })

        format_type = OutputFormat(output)
        fields = ['displayName', 'email', 'phone', 'organization']
        headers = ['Name', 'Email', 'Phone', 'Organization']
        output_str = format_output(contacts, format_type, fields, headers)
        click.echo(output_str)

        # Show pagination info if available
        next_token = result.get('nextPageToken')
        if next_token:
            click.echo(f"\nMore results available. Use --limit with a larger value or implement pagination.")

    except ValidationError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except GwcError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.option(
    '--name',
    help='Contact display name'
)
@click.option(
    '--email',
    help='Email address'
)
@click.option(
    '--phone',
    help='Phone number'
)
@click.option(
    '--organization',
    help='Organization name'
)
@click.option(
    '--address',
    help='Physical address'
)
@click.option(
    '--output',
    type=click.Choice(['unix', 'json', 'llm']),
    default='unix',
    help='Output format (default: unix)'
)
def create(name, email, phone, organization, address, output):
    """Create a new contact.

    Examples:
        gwc-people create --name "John Smith" --email "john@example.com"
        gwc-people create --name "Jane Doe" --phone "+1234567890" --organization "Acme"
        gwc-people create --email "contact@example.com" --output json
    """
    try:
        contact = operations.create_contact(
            name=name,
            email=email,
            phone=phone,
            organization=organization,
            address=address
        )

        format_type = OutputFormat(output)
        fields = ['names', 'emailAddresses', 'phoneNumbers', 'organizations', 'resourceName']
        output_str = format_output(contact, format_type, fields)
        click.echo(output_str)

    except ValidationError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except GwcError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.argument('email_or_id')
@click.option(
    '--name',
    help='New display name'
)
@click.option(
    '--email',
    help='New email address'
)
@click.option(
    '--phone',
    help='New phone number'
)
@click.option(
    '--organization',
    help='New organization name'
)
@click.option(
    '--address',
    help='New physical address'
)
@click.option(
    '--output',
    type=click.Choice(['unix', 'json', 'llm']),
    default='unix',
    help='Output format (default: unix)'
)
def update(email_or_id, name, email, phone, organization, address, output):
    """Update an existing contact.

    Examples:
        gwc-people update "john@example.com" --phone "+1987654321"
        gwc-people update "jane@example.com" --organization "New Company"
        gwc-people update "people/c123456789" --name "Jonathan Smith" --output json
    """
    try:
        contact = operations.update_contact(
            resource_name_or_email=email_or_id,
            name=name,
            email=email,
            phone=phone,
            organization=organization,
            address=address
        )

        format_type = OutputFormat(output)
        fields = ['names', 'emailAddresses', 'phoneNumbers', 'organizations', 'resourceName']
        output_str = format_output(contact, format_type, fields)
        click.echo(output_str)

    except ValidationError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except GwcError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.argument('email_or_id')
@click.option(
    '--confirm',
    is_flag=True,
    help='Confirm deletion without prompting'
)
def delete(email_or_id, confirm):
    """Delete a contact.

    Examples:
        gwc-people delete "john@example.com"
        gwc-people delete "people/c123456789" --confirm
    """
    try:
        if not confirm:
            click.echo(f"About to delete contact: {email_or_id}")
            if not click.confirm("Are you sure?"):
                click.echo("Deletion cancelled.")
                return

        operations.delete_contact(email_or_id)
        click.echo(f"Contact deleted successfully.")

    except ValidationError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except GwcError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
