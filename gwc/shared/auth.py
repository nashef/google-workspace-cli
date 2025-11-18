"""OAuth2 authentication and token management."""

import os
import json
from typing import Optional, Dict, Any

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

from .exceptions import AuthenticationError
from . import config


# Google Calendar API scopes
CALENDAR_SCOPES = [
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/calendar.readonly"
]

# Gmail scopes (for future use)
GMAIL_SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.compose",
    "https://www.googleapis.com/auth/gmail.send"
]

# Google People API scopes
PEOPLE_SCOPES = [
    "https://www.googleapis.com/auth/contacts",
    "https://www.googleapis.com/auth/contacts.readonly"
]

# Union of all scopes we might need
ALL_SCOPES = list(set(CALENDAR_SCOPES + GMAIL_SCOPES + PEOPLE_SCOPES))


def authenticate_interactive(scopes: Optional[list] = None) -> Credentials:
    """Perform interactive OAuth2 authentication.

    This is used by 'gwc auth' command. Prints URL for user to visit,
    then exchanges the authorization code for tokens.

    Args:
        scopes: List of OAuth2 scopes to request

    Returns:
        Authenticated Credentials object
    """
    if scopes is None:
        scopes = ALL_SCOPES

    if not config.has_credentials():
        raise AuthenticationError(
            "No credentials.json file found in ~/.config/gwc/\n"
            "Please download OAuth2 credentials from Google Cloud Console\n"
            "and save as ~/.config/gwc/credentials.json"
        )

    credentials_file = str(config.CREDENTIALS_FILE)

    try:
        flow = InstalledAppFlow.from_client_secrets_file(
            credentials_file,
            scopes=scopes
        )

        # Try to run local server for callback
        try:
            creds = flow.run_local_server(port=0, open_browser=False)
        except Exception as local_server_error:
            # Fallback to manual code entry
            import sys
            print("\n" + "="*70, file=sys.stderr)
            print("Browser-based authentication failed. Using manual code entry.", file=sys.stderr)
            print("="*70 + "\n", file=sys.stderr)

            auth_url, _ = flow.authorization_url(prompt='consent')
            print(f"Please visit this URL to authorize:\n\n{auth_url}\n", file=sys.stderr)
            print("After authorizing, you'll be redirected. Copy the authorization code from the URL.", file=sys.stderr)
            print("(It will be in the 'code' parameter)\n", file=sys.stderr)

            code = input("Enter the authorization code: ").strip()
            if not code:
                raise AuthenticationError("No authorization code provided")

            try:
                creds = flow.fetch_token(code=code)
            except Exception as e:
                raise AuthenticationError(f"Failed to exchange code for token: {e}")

        # Save the token - handle both Credentials objects and dicts
        token_data = {
            'token': getattr(creds, 'token', None),
            'refresh_token': getattr(creds, 'refresh_token', None),
            'token_uri': getattr(creds, 'token_uri', None),
            'client_id': getattr(creds, 'client_id', None),
            'client_secret': getattr(creds, 'client_secret', None),
            'scopes': scopes
        }
        config.save_token(token_data)

        return creds

    except AuthenticationError:
        raise
    except Exception as e:
        raise AuthenticationError(f"OAuth2 authentication failed: {e}")


def get_credentials(scopes: Optional[list] = None) -> Credentials:
    """Get valid credentials, refreshing if necessary.

    Args:
        scopes: List of OAuth2 scopes required

    Returns:
        Valid Credentials object

    Raises:
        AuthenticationError: If no valid credentials exist
    """
    if scopes is None:
        scopes = ALL_SCOPES

    if not config.has_token():
        raise AuthenticationError(
            "No valid authentication token found.\n"
            "Run 'gwc auth' to authenticate."
        )

    try:
        token_data = config.load_token()

        # Reconstruct credentials from saved token
        creds = Credentials(
            token=token_data.get('token'),
            refresh_token=token_data.get('refresh_token'),
            token_uri=token_data.get('token_uri'),
            client_id=token_data.get('client_id'),
            client_secret=token_data.get('client_secret'),
            scopes=token_data.get('scopes', scopes)
        )

        # Refresh if expired
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            # Save updated token
            config.save_token({
                'token': creds.token,
                'refresh_token': creds.refresh_token,
                'token_uri': creds.token_uri,
                'client_id': creds.client_id,
                'client_secret': creds.client_secret,
                'scopes': creds.scopes
            })

        return creds

    except Exception as e:
        raise AuthenticationError(f"Failed to load credentials: {e}")


def refresh_token() -> None:
    """Refresh the stored authentication token.

    Raises:
        AuthenticationError: If refresh fails
    """
    if not config.has_token():
        raise AuthenticationError(
            "No valid authentication token found.\n"
            "Run 'gwc auth' to authenticate."
        )

    try:
        token_data = config.load_token()

        creds = Credentials(
            token=token_data.get('token'),
            refresh_token=token_data.get('refresh_token'),
            token_uri=token_data.get('token_uri'),
            client_id=token_data.get('client_id'),
            client_secret=token_data.get('client_secret'),
            scopes=token_data.get('scopes')
        )

        if not creds.refresh_token:
            raise AuthenticationError(
                "Cannot refresh token - no refresh_token available.\n"
                "Run 'gwc auth' to re-authenticate."
            )

        creds.refresh(Request())

        # Save updated token
        config.save_token({
            'token': creds.token,
            'refresh_token': creds.refresh_token,
            'token_uri': creds.token_uri,
            'client_id': creds.client_id,
            'client_secret': creds.client_secret,
            'scopes': creds.scopes
        })

        print("Token refreshed successfully.")

    except Exception as e:
        raise AuthenticationError(f"Token refresh failed: {e}")
