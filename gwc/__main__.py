"""Google Workspace CLI main entry point with shared commands."""

import click
from gwc.shared.auth import authenticate_interactive


@click.group()
def main():
    """Google Workspace CLI (gwc)."""
    pass


@main.command()
def auth():
    """Authenticate with Google Workspace APIs.

    This command guides you through OAuth2 authentication and stores your
    access tokens. Run this once to authorize all gwc tools.

    Examples:
        gwc auth
    """
    try:
        creds = authenticate_interactive()
        click.echo("✓ Authentication successful!")
        click.echo(f"✓ Token saved to ~/.config/gwc/token.json")
        click.echo(f"✓ You can now use all gwc tools (gwc-drive, gwc-docs, etc.)")
    except Exception as e:
        click.echo(f"✗ Authentication failed: {e}", err=True)
        raise click.Abort()


if __name__ == "__main__":
    main()
