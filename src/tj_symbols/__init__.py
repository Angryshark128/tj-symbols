"""Tianji Symbols — Market-aware symbol parsing, normalization, and format conversion for Chinese securities."""

from tj_symbols.api import (
    convert,
    detect_asset_type,
    detect_exchange,
    detect_format,
    format_symbol,
    get_format_info,
    is_valid_symbol,
    list_formats,
    list_input_formats,
    list_output_formats,
    normalize,
    parse_symbol,
)
from tj_symbols.errors import (
    AmbiguousSymbolError,
    InvalidSymbolError,
    SymbolParseError,
    TianjiSymbolsError,
    UnknownFormatError,
    UnsupportedFormatError,
)
from tj_symbols.types import ParseResult, SymbolFormatInfo

__version__ = "0.1.0"

__all__ = [
    "__version__",
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
    "ParseResult",
    "SymbolFormatInfo",
    "TianjiSymbolsError",
    "SymbolParseError",
    "UnknownFormatError",
    "UnsupportedFormatError",
    "AmbiguousSymbolError",
    "InvalidSymbolError",
]
