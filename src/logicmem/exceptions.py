"""
LogicMem Exceptions
==================
Custom exception hierarchy for the LogicMem SDK.
"""


class LogicMemError(Exception):
    """Base exception for all LogicMem errors."""

    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class AuthenticationError(LogicMemError):
    """Raised when the API key is invalid or missing."""

    pass


class MemoryNotFoundError(LogicMemError):
    """Raised when a requested memory entry does not exist."""

    pass


class RateLimitError(LogicMemError):
    """Raised when the API rate limit has been exceeded."""

    pass


class ServerError(LogicMemError):
    """Raised when the LogicMem server returns a 5xx error."""

    pass


class ValidationError(LogicMemError):
    """Raised when request parameters fail validation."""

    pass


class NetworkError(LogicMemError):
    """Raised when a network-level error occurs (timeout, DNS, etc.)."""

    pass
