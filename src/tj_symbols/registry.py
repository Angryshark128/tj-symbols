"""Symbol format registry: the 8 MVP formats and query helpers.

Reference: design doc section 7.
"""

from __future__ import annotations

from tj_symbols.errors import UnknownFormatError
from tj_symbols.types import SymbolFormatInfo

_FORMATS: dict[str, SymbolFormatInfo] = {
    "tianji": SymbolFormatInfo(
        name="tianji",
        display_name="Tianji",
        example="600519.SH",
        examples={
            "SSE": "600519.SH",
            "SZSE": "000001.SZ",
            "BSE": "430047.BJ",
        },
        description="Tianji ecosystem canonical format.",
        input_supported=True,
        output_supported=True,
        exchanges=("SSE", "SZSE", "BSE"),
        lossy=False,
        ambiguous=False,
    ),
    "tushare": SymbolFormatInfo(
        name="tushare",
        display_name="Tushare",
        example="600519.SH",
        examples={
            "SSE": "600519.SH",
            "SZSE": "000001.SZ",
            "BSE": "430047.BJ",
        },
        description="Tushare ts_code style. Currently equivalent to Tianji for supported markets.",
        input_supported=True,
        output_supported=True,
        exchanges=("SSE", "SZSE", "BSE"),
        lossy=False,
        ambiguous=False,
        notes=("Currently equivalent to Tianji for supported markets.",),
    ),
    "prefix": SymbolFormatInfo(
        name="prefix",
        display_name="Prefix",
        example="SH600519",
        examples={
            "SSE": "SH600519",
            "SZSE": "SZ000001",
            "BSE": "BJ430047",
        },
        description="Exchange prefix plus code, e.g. SH600519.",
        input_supported=True,
        output_supported=True,
        exchanges=("SSE", "SZSE", "BSE"),
        lossy=False,
        ambiguous=False,
    ),
    "sina": SymbolFormatInfo(
        name="sina",
        display_name="Sina",
        example="sh600519",
        examples={
            "SSE": "sh600519",
            "SZSE": "sz000001",
        },
        description="Lowercase exchange prefix plus code used by Sina Finance.",
        input_supported=True,
        output_supported=True,
        exchanges=("SSE", "SZSE"),
        lossy=False,
        ambiguous=False,
        notes=("BSE support is not guaranteed in MVP.",),
    ),
    "eastmoney": SymbolFormatInfo(
        name="eastmoney",
        display_name="Eastmoney",
        example="1.600519",
        examples={
            "SSE": "1.600519",
            "SZSE": "0.000001",
        },
        description="Market id plus code format commonly used by Eastmoney APIs.",
        input_supported=True,
        output_supported=True,
        exchanges=("SSE", "SZSE"),
        lossy=False,
        ambiguous=False,
        notes=("BSE support varies by endpoint and is not guaranteed in MVP.",),
    ),
    "jqdata": SymbolFormatInfo(
        name="jqdata",
        display_name="JoinQuant/JQData",
        example="600519.XSHG",
        examples={
            "SSE": "600519.XSHG",
            "SZSE": "000001.XSHE",
        },
        description="JQData code.suffix format.",
        input_supported=True,
        output_supported=True,
        exchanges=("SSE", "SZSE"),
        lossy=False,
        ambiguous=False,
        notes=("BSE mapping is reserved but not guaranteed in MVP.",),
    ),
    "baostock": SymbolFormatInfo(
        name="baostock",
        display_name="BaoStock",
        example="sh.600519",
        examples={
            "SSE": "sh.600519",
            "SZSE": "sz.000001",
        },
        description="Lowercase exchange prefix dot code format used by BaoStock.",
        input_supported=True,
        output_supported=True,
        exchanges=("SSE", "SZSE"),
        lossy=False,
        ambiguous=False,
        notes=("BSE support is not guaranteed in MVP.",),
    ),
    "plain": SymbolFormatInfo(
        name="plain",
        display_name="Plain Code",
        example="600519",
        examples={
            "SSE": "600519",
            "SZSE": "000001",
            "BSE": "430047",
        },
        description="Bare 6-digit code.",
        input_supported=True,
        output_supported=True,
        exchanges=("SSE", "SZSE", "BSE"),
        lossy=True,
        ambiguous=True,
        notes=("Plain output drops exchange information. Plain input may require inference.",),
    ),
}

# Aliases that map to a canonical registry entry.
_ALIASES: dict[str, str] = {}


def list_formats() -> list[str]:
    """Return the names of all registered formats."""
    return list(_FORMATS)


def list_input_formats() -> list[str]:
    """Return formats that support input parsing."""
    return [name for name, info in _FORMATS.items() if info.input_supported]


def list_output_formats() -> list[str]:
    """Return formats that support output rendering."""
    return [name for name, info in _FORMATS.items() if info.output_supported]


def get_format_info(name: str) -> SymbolFormatInfo:
    """Return the SymbolFormatInfo for a format name."""
    real = _ALIASES.get(name, name)
    info = _FORMATS.get(real)
    if info is None:
        raise UnknownFormatError(f"unknown target format {name!r}. Run `tjsym formats` to list supported formats.")
    return info


def is_known_format(name: str) -> bool:
    """Return whether ``name`` is a known format (including aliases)."""
    return name in _ALIASES or name in _FORMATS
