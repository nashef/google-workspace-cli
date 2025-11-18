"""Configuration and credential storage management."""

import json
import os
from pathlib import Path
from typing import Optional, Any, Dict

from .exceptions import ConfigError, AuthenticationError


# Config directory location
CONFIG_DIR = Path.home() / ".config" / "gwc"
CREDENTIALS_FILE = CONFIG_DIR / "credentials.json"
TOKEN_FILE = CONFIG_DIR / "token.json"
CONFIG_FILE = CONFIG_DIR / "config.toml"


def ensure_config_dir() -> None:
    """Ensure config directory exists."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def has_credentials() -> bool:
    """Check if OAuth2 credentials are configured."""
    return CREDENTIALS_FILE.exists()


def has_token() -> bool:
    """Check if a valid token exists."""
    return TOKEN_FILE.exists()


def load_credentials() -> Dict[str, Any]:
    """Load OAuth2 credentials from file.

    Raises:
        AuthenticationError: If credentials file doesn't exist.
    """
    if not CREDENTIALS_FILE.exists():
        raise AuthenticationError(
            "No OAuth2 credentials found.\n"
            "Run 'gwc auth' to authenticate."
        )

    try:
        with open(CREDENTIALS_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        raise ConfigError(f"Failed to load credentials: {e}")


def save_credentials(credentials: Dict[str, Any]) -> None:
    """Save OAuth2 credentials to file."""
    ensure_config_dir()

    try:
        with open(CREDENTIALS_FILE, 'w') as f:
            json.dump(credentials, f, indent=2)
        # Restrict permissions on credentials file
        os.chmod(CREDENTIALS_FILE, 0o600)
    except IOError as e:
        raise ConfigError(f"Failed to save credentials: {e}")


def load_token() -> Dict[str, Any]:
    """Load access token from file.

    Raises:
        AuthenticationError: If token file doesn't exist.
    """
    if not TOKEN_FILE.exists():
        raise AuthenticationError(
            "No valid authentication token found.\n"
            "Run 'gwc auth' to authenticate."
        )

    try:
        with open(TOKEN_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        raise ConfigError(f"Failed to load token: {e}")


def save_token(token: Dict[str, Any]) -> None:
    """Save access token to file."""
    ensure_config_dir()

    try:
        with open(TOKEN_FILE, 'w') as f:
            json.dump(token, f, indent=2)
        # Restrict permissions on token file
        os.chmod(TOKEN_FILE, 0o600)
    except IOError as e:
        raise ConfigError(f"Failed to save token: {e}")


def load_config() -> Dict[str, Any]:
    """Load all configuration values.

    Returns:
        Dictionary of config values, or empty dict if config file doesn't exist.
    """
    if not CONFIG_FILE.exists():
        return {}

    try:
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        raise ConfigError(f"Failed to load config: {e}")


def save_config(config: Dict[str, Any]) -> None:
    """Save configuration values to file."""
    ensure_config_dir()

    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
        os.chmod(CONFIG_FILE, 0o600)
    except IOError as e:
        raise ConfigError(f"Failed to save config: {e}")


def get_config_value(key: str, default: Optional[Any] = None) -> Optional[Any]:
    """Get a configuration value.

    Args:
        key: Configuration key
        default: Default value if key doesn't exist

    Returns:
        Configuration value or default
    """
    try:
        config = load_config()
        return config.get(key, default)
    except ConfigError:
        return default


def set_config_value(key: str, value: Any) -> None:
    """Set a configuration value.

    Args:
        key: Configuration key
        value: Value to set
    """
    try:
        config = load_config()
    except ConfigError:
        config = {}

    config[key] = value
    save_config(config)


def delete_config_value(key: str) -> None:
    """Delete a configuration value.

    Args:
        key: Configuration key to delete
    """
    try:
        config = load_config()
    except ConfigError:
        config = {}

    if key in config:
        del config[key]
        save_config(config)
