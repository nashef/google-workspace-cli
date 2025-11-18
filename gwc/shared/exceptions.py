"""Custom exception types for gwc."""


class GwcError(Exception):
    """Base exception for gwc errors."""
    pass


class AuthenticationError(GwcError):
    """Raised when authentication fails or credentials are missing."""
    pass


class ConfigError(GwcError):
    """Raised when configuration is invalid or missing."""
    pass


class APIError(GwcError):
    """Raised when Google API calls fail."""
    pass


class ValidationError(GwcError):
    """Raised when user input validation fails."""
    pass
