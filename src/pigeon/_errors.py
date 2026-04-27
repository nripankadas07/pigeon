"""Exception classes for pigeon."""

from __future__ import annotations


class PluralFormError(Exception):
    """Base class for all pigeon errors."""


class ParseError(PluralFormError):
    """Raised when a plural-form string fails to parse.

    The ``position`` attribute holds the column (0-indexed) where the error
    was first detected, when known.
    """

    def __init__(self, message: str, position: int | None = None) -> None:
        super().__init__(message)
        self.position = position


class EvaluationError(PluralFormError):
    """Raised at evaluation time (e.g., division/modulo by zero)."""


class UnknownLocaleError(PluralFormError):
    """Raised when ``forms_for(locale)`` does not recognise the locale."""
