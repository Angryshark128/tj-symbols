"""Render a Symbol to a target format.

Exchange mapping reference: design doc section 10.
"""

from __future__ import annotations

from tj_datamodel import Exchange, Symbol

from tj_symbols.errors import UnknownFormatError, UnsupportedFormatError
from tj_symbols.registry import get_format_info

# Canonical Tianji suffix per exchange.
_SUFFIX: dict[Exchange, str] = {
    Exchange.SSE: "SH",
    Exchange.SZSE: "SZ",
    Exchange.BSE: "BJ",
}

# jqdata suffix per exchange.
_JQDATA_SUFFIX: dict[Exchange, str] = {
    Exchange.SSE: "XSHG",
    Exchange.SZSE: "XSHE",
}

# eastmoney market id per exchange.
_EASTMONEY_ID: dict[Exchange, str] = {
    Exchange.SSE: "1",
    Exchange.SZSE: "0",
}

# baostock prefix per exchange.
_BAOSTOCK_PREFIX: dict[Exchange, str] = {
    Exchange.SSE: "sh",
    Exchange.SZSE: "sz",
}

# prefix (and sina) exchange letter group per exchange.
_PREFIX_CODE: dict[Exchange, str] = {
    Exchange.SSE: "SH",
    Exchange.SZSE: "SZ",
    Exchange.BSE: "BJ",
}


def _check_supported(target: str, exchange: Exchange) -> None:
    info = get_format_info(target)
    if not info.output_supported:
        raise UnknownFormatError(f"unknown target format {target!r}. Run `tjsym formats` to list supported formats.")
    if exchange.value not in info.exchanges:
        supported = ", ".join(info.exchanges)
        raise UnsupportedFormatError(
            f"format {target!r} does not support exchange {exchange.value!r}. "
            f"Supported exchanges for {target}: {supported}. "
            f"Run `tjsym format-info {target}` for details."
        )


def _case(text: str, is_lower: bool | None, default_lower: bool) -> str:
    if is_lower is None:
        return text.lower() if default_lower else text.upper()
    return text.lower() if is_lower else text.upper()


def format_symbol(
    symbol: Symbol,
    style: str,
    is_lower: bool | None = None,
) -> str:
    """Render a canonical Symbol into ``style``.

    ``is_lower`` controls letter case only: None = format default,
    True = lowercase, False = uppercase. Digits and eastmoney market ids are
    never affected.
    """
    code = symbol.code
    exchange = symbol.exchange
    suffix = _SUFFIX[exchange]

    if style in ("tianji", "tushare"):
        return f"{code}.{_case(suffix, is_lower, default_lower=False)}"

    if style == "prefix":
        prefix = _PREFIX_CODE[exchange]
        return f"{_case(prefix, is_lower, default_lower=False)}{code}"

    if style == "sina":
        _check_supported(style, exchange)
        prefix = _PREFIX_CODE[exchange]
        return f"{_case(prefix, is_lower, default_lower=True)}{code}"

    if style == "eastmoney":
        _check_supported(style, exchange)
        market_id = _EASTMONEY_ID[exchange]
        return f"{market_id}.{code}"

    if style == "jqdata":
        _check_supported(style, exchange)
        jq = _JQDATA_SUFFIX[exchange]
        return f"{code}.{_case(jq, is_lower, default_lower=False)}"

    if style == "baostock":
        _check_supported(style, exchange)
        prefix = _BAOSTOCK_PREFIX[exchange]
        return f"{_case(prefix, is_lower, default_lower=True)}.{code}"

    if style == "plain":
        return code

    raise UnknownFormatError(f"unknown target format {style!r}. Run `tjsym formats` to list supported formats.")
