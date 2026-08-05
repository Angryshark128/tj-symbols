"""Top-level public API for tj-symbols."""

from __future__ import annotations

from tj_datamodel import AssetType, Exchange

from tj_symbols.parser import (
    detect_asset_type,
    detect_exchange,
    detect_format,
    is_valid_symbol,
    parse_symbol,
)
from tj_symbols.registry import get_format_info


def convert(
    symbol: str,
    to: str,
    from_format: str | None = None,
    exchange: str | Exchange | None = None,
    asset_type: str | AssetType | None = None,
    is_lower: bool | None = None,
) -> str:
    """Convert ``symbol`` to the target format ``to``.

    ``from_format`` optionally pins the source format. ``exchange`` and
    ``asset_type`` disambiguate plain codes. ``is_lower`` controls letter
    case (None = format default).
    """
    result = parse_symbol(symbol, exchange=exchange, asset_type=asset_type, from_format=from_format)
    return result.format(to, is_lower=is_lower)


def normalize(
    symbol: str,
    exchange: str | Exchange | None = None,
    asset_type: str | AssetType | None = None,
) -> str:
    """Normalize ``symbol`` to the Tianji canonical format (600519.SH)."""
    return convert(symbol, to="tianji", exchange=exchange, asset_type=asset_type)


def format_symbol(symbol: str, style: str, is_lower: bool | None = None) -> str:
    """Parse ``symbol`` and render it in ``style``."""
    return convert(symbol, to=style, is_lower=is_lower)


__all__ = [
    "convert",
    "normalize",
    "parse_symbol",
    "format_symbol",
    "detect_format",
    "detect_exchange",
    "detect_asset_type",
    "is_valid_symbol",
    "list_formats",
    "list_input_formats",
    "list_output_formats",
    "get_format_info",
]


def list_formats() -> list[str]:
    """Return names of all registered formats."""
    from tj_symbols.registry import list_formats as _list

    return _list()


def list_input_formats() -> list[str]:
    """Return names of formats that support input."""
    from tj_symbols.registry import list_input_formats as _list

    return _list()


def list_output_formats() -> list[str]:
    """Return names of formats that support output."""
    from tj_symbols.registry import list_output_formats as _list

    return _list()
