"""tj-symbols-specific types: ParseResult and SymbolFormatInfo.

``Symbol`` and the enums come from ``tj_datamodel``; this module only defines
types that belong to tj-symbols itself.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from tj_datamodel import Symbol


@dataclass(frozen=True)
class ParseResult:
    """A parsed symbol plus the format it was recognized from."""

    symbol: Symbol
    source_format: str | None = None

    @property
    def normalized(self) -> str:
        return self.symbol.normalized

    def format(self, style: str, is_lower: bool | None = None) -> str:
        from tj_symbols.formatter import format_symbol as _format_symbol

        return _format_symbol(self.symbol, style, is_lower=is_lower)


@dataclass(frozen=True)
class SymbolFormatInfo:
    """Metadata about a supported symbol format.

    ``exchanges`` uses string names (e.g. ``"SSE"``) for CLI/registry display.
    """

    name: str
    display_name: str
    example: str
    examples: dict[str, str]
    description: str
    input_supported: bool
    output_supported: bool
    exchanges: tuple[str, ...]
    lossy: bool = False
    ambiguous: bool = False
    notes: tuple[str, ...] = field(default=())
