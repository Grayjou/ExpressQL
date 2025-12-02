"""
ExpressQL Exceptions - Custom exception classes.

This module defines custom exception classes used throughout ExpressQL
to indicate specific error conditions related to SQL generation and validation.

Exception Classes:
    ForbiddenCharacterError: Raised when forbidden characters are detected in input

Example:
    >>> from expressql.exceptions import ForbiddenCharacterError
    >>> raise ForbiddenCharacterError(";", "'")
    ForbiddenCharacterError: Forbidden characters: ;, '
"""


class ForbiddenCharacterError(Exception):
    """Exception raised for forbidden characters in a condition."""
    def __init__(self, *forbidden_chars):
        self.forbidden_chars = forbidden_chars
        super().__init__(f"Forbidden characters: {', '.join(forbidden_chars)}")

