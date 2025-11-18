"""Google Workspace CLI main entry point with shared commands."""

import click
from gwc.shared.auth import authenticate_interactive, refresh_token


@click.group()
def main():
    """Google Workspace CLI (gwc)."""
    pass


@main.command()
@click.option(
    '--refresh',
    is_flag=True,
    help='Refresh an existing token instead of performing initial authentication.'
)
def auth(refresh):
    """Authenticate with Google Workspace APIs.

    Without --refresh: Performs initial OAuth2 setup. Guides you through the
    OAuth2 authentication flow and stores your tokens.

    With --refresh: Refreshes an existing token.

    Examples:
        gwc auth
        gwc auth --refresh
    """
    try:
        if refresh:
            refresh_token()
            click.echo("✓ Token refreshed successfully!")
        else:
            creds = authenticate_interactive()
            click.echo("✓ Authentication successful!")
            click.echo(f"✓ Token saved to ~/.config/gwc/token.json")
            click.echo(f"✓ You can now use all gwc tools (gwc-drive, gwc-docs, etc.)")
    except Exception as e:
        click.echo(f"✗ {'Refresh' if refresh else 'Authentication'} failed: {e}", err=True)
        raise click.Abort()


if __name__ == "__main__":
    main()
