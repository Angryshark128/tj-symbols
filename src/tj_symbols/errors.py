"""Exceptions raised by tj-symbols."""

from __future__ import annotations


class TianjiSymbolsError(Exception):
    """Base error for tj-symbols."""


class SymbolParseError(TianjiSymbolsError):
    """Raised when a symbol string cannot be parsed."""


class UnknownFormatError(TianjiSymbolsError):
    """Raised when a format name is not in the registry."""


class UnsupportedFormatError(TianjiSymbolsError):
    """Raised when a format does not support a requested exchange."""


class AmbiguousSymbolError(TianjiSymbolsError):
    """Raised when a symbol cannot be disambiguated (reserved for strict mode)."""


class InvalidSymbolError(TianjiSymbolsError):
    """Raised when a symbol string is not a valid security identifier."""
