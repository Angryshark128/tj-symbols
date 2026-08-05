"""Input format detection and symbol parsing.

Reference: design doc sections 5, 11, 12.
"""

from __future__ import annotations

import re

from tj_datamodel import AssetType, Exchange, Market, Symbol

from tj_symbols.errors import SymbolParseError, UnknownFormatError
from tj_symbols.registry import is_known_format
from tj_symbols.rules import infer_asset_type, infer_exchange, infer_exchange_for_asset_type
from tj_symbols.types import ParseResult

_CODE_RE = re.compile(r"^\d{6}$")

# source-format handlers. Each returns (code, Exchange | None, format) or None.
_PLAIN_RE = re.compile(r"^\d{6}$")
_TIANJI_RE = re.compile(r"^(?P<code>\d{6})\.(?P<suffix>sh|sz|bj)$", re.IGNORECASE)
# Prefix format uses an UPPERCASE exchange group (SH600519). Lowercase prefixes
# (sh600519) are treated as the Sina format per design section 8.5.
_PREFIX_RE = re.compile(r"^(?P<ex>(?:SH|SZ|BJ))(?P<code>\d{6})$")
_SINA_RE = re.compile(r"^(?P<ex>(?:sh|sz|bj))(?P<code>\d{6})$")
_COLON_RE = re.compile(r"^(?P<ex>[a-z]{2,4}):(?P<code>\d{6})$", re.IGNORECASE)
# BaoStock is the lowercase sh./sz. form; it must be checked before the
# general dot-exchange form so that sh.600519 is detected as baostock.
_BAOSTOCK_RE = re.compile(r"^(?P<ex>sh|sz)\.(?P<code>\d{6})$")
_DOT_EX_RE = re.compile(r"^(?P<ex>[a-z]{2,4})\.(?P<code>\d{6})$", re.IGNORECASE)
_JQDATA_RE = re.compile(r"^(?P<code>\d{6})\.(?P<suffix>xshg|xshe)$", re.IGNORECASE)
_EASTMONEY_RE = re.compile(r"^(?P<market>[01])\.(?P<code>\d{6})$")

_SUFFIX_TO_EXCHANGE = {
    "SH": Exchange.SSE,
    "SZ": Exchange.SZSE,
    "BJ": Exchange.BSE,
}

_EXCHANGE_NAME_TO_ENUM = {
    "SH": Exchange.SSE,
    "SZ": Exchange.SZSE,
    "BJ": Exchange.BSE,
    "SSE": Exchange.SSE,
    "SZSE": Exchange.SZSE,
    "BSE": Exchange.BSE,
}

# Canonical Tianji suffix per exchange.
_SUFFIX: dict[Exchange, str] = {
    Exchange.SSE: "SH",
    Exchange.SZSE: "SZ",
    Exchange.BSE: "BJ",
}


def _coerce_exchange(value: str | Exchange | None) -> Exchange | None:
    if value is None:
        return None
    if isinstance(value, Exchange):
        return value
    up = value.upper()
    ex = _EXCHANGE_NAME_TO_ENUM.get(up)
    if ex is None:
        raise UnknownFormatError(f"unknown exchange {value!r}.")
    return ex


def _coerce_asset_type(value: str | AssetType | None) -> AssetType | None:
    if value is None:
        return None
    if isinstance(value, AssetType):
        return value
    try:
        return AssetType(value.lower())
    except ValueError:
        raise UnknownFormatError(f"unknown asset type {value!r}.") from None


def detect_format(text: str) -> str:
    """Return the source format name for ``text`` (best single guess).

    Raises SymbolParseError when nothing matches.
    """
    parsed = _parse(text)
    if parsed is not None:
        return parsed[2]
    raise SymbolParseError(f"unable to parse symbol {text!r}.")


def _parse(text: str) -> tuple[str, Exchange | None, str] | None:
    """Return (code, exchange, format) for ``text`` or None.

    Plain codes return ``None`` as the exchange: the caller resolves it via
    inference so that ``exchange=`` / ``asset_type=`` can disambiguate.
    """
    s = text.strip()
    if not s:
        return None

    m = _PLAIN_RE.match(s)
    if m:
        return (s, None, "plain")

    m = _TIANJI_RE.match(s)
    if m:
        code = m.group("code")
        exchange = _SUFFIX_TO_EXCHANGE[m.group("suffix").upper()]
        return (code, exchange, "tianji")

    m = _PREFIX_RE.match(s)
    if m:
        code = m.group("code")
        ex_key = m.group("ex").upper()
        exchange = _EXCHANGE_NAME_TO_ENUM[ex_key]
        return (code, exchange, "prefix")

    m = _SINA_RE.match(s)
    if m:
        code = m.group("code")
        ex_key = m.group("ex").upper()
        exchange = _EXCHANGE_NAME_TO_ENUM[ex_key]
        return (code, exchange, "sina")

    m = _COLON_RE.match(s)
    if m:
        code = m.group("code")
        exchange = _coerce_exchange(m.group("ex"))
        if exchange is None:
            return None
        return (code, exchange, "prefix")

    # BaoStock (sh.600519 / sz.000001) must be checked before the general
    # dot-exchange form so it is detected as baostock.
    m = _BAOSTOCK_RE.match(s)
    if m:
        code = m.group("code")
        exchange = Exchange.SSE if m.group("ex").lower() == "sh" else Exchange.SZSE
        return (code, exchange, "baostock")

    m = _DOT_EX_RE.match(s)
    if m:
        code = m.group("code")
        exchange = _coerce_exchange(m.group("ex"))
        if exchange is None:
            return None
        return (code, exchange, "prefix")

    m = _JQDATA_RE.match(s)
    if m:
        code = m.group("code")
        suffix = m.group("suffix").upper()
        exchange = Exchange.SSE if suffix == "XSHG" else Exchange.SZSE
        return (code, exchange, "jqdata")

    m = _EASTMONEY_RE.match(s)
    if m:
        code = m.group("code")
        exchange = Exchange.SSE if m.group("market") == "1" else Exchange.SZSE
        return (code, exchange, "eastmoney")

    return None


def parse_symbol(
    text: str,
    exchange: str | Exchange | None = None,
    asset_type: str | AssetType | None = None,
    from_format: str | None = None,
) -> ParseResult:
    """Parse ``text`` into a ParseResult containing a canonical Symbol.

    ``exchange`` and ``asset_type`` disambiguate plain codes; when both are
    given they must be consistent with any exchange embedded in ``text``.
    ``from_format`` optionally pins the source format.
    """
    src_ex = _coerce_exchange(exchange)
    src_at = _coerce_asset_type(asset_type)

    raw = text.strip() if text else ""
    parsed = _parse(raw) if raw else None

    if parsed is None:
        raise SymbolParseError(f"unable to parse symbol {text!r}.")

    code, ex_from_text, fmt = parsed
    if from_format is not None and not is_known_format(from_format):
        raise UnknownFormatError(
            f"unknown target format {from_format!r}. Run `tjsym formats` to list supported formats."
        )

    if src_ex is not None and ex_from_text is not None and src_ex != ex_from_text:
        raise SymbolParseError(
            f"symbol {text!r} conflicts with exchange {src_ex.value!r}: it already encodes {ex_from_text.value!r}."
        )

    # Resolve exchange: explicit param > exchange embedded in text > inference.
    if src_ex is not None:
        exchange_resolved = src_ex
    elif ex_from_text is not None:
        exchange_resolved = ex_from_text
    elif src_at is not None:
        exchange_resolved = infer_exchange_for_asset_type(code, src_at) or Exchange.SZSE
    else:
        exchange_resolved = infer_exchange(code) or Exchange.SZSE

    asset_resolved = src_at or infer_asset_type(code, exchange_resolved)

    suffix = _SUFFIX[exchange_resolved]
    normalized = f"{code}.{suffix}"

    symbol = Symbol(
        code=code,
        exchange=exchange_resolved,
        suffix=suffix,
        market=Market.CN_A_SHARE,
        asset_type=asset_resolved,
        normalized=normalized,
    )
    return ParseResult(symbol=symbol, source_format=fmt)


def detect_exchange(text: str) -> str:
    """Return the exchange name for ``text`` (e.g. ``"SSE"``)."""
    s = text.strip()
    if s:
        parsed = _parse(s)
        if parsed is not None:
            code, exchange, _ = parsed
            if exchange is not None:
                return exchange.value
            inferred = infer_exchange(code)
            if inferred is not None:
                return inferred.value
            raise SymbolParseError(f"unable to detect exchange for symbol {text!r}.")
        if _CODE_RE.match(s):
            inferred = infer_exchange(s)
            if inferred is not None:
                return inferred.value
    raise SymbolParseError(f"unable to detect exchange for symbol {text!r}.")


def detect_asset_type(text: str) -> str:
    """Return the asset type for ``text`` (e.g. ``"stock"``)."""
    s = text.strip()
    if not s:
        raise SymbolParseError(f"unable to detect asset type for symbol {text!r}.")
    parsed = _parse(s)
    if parsed is not None:
        code, exchange, _ = parsed
        exchange = exchange or infer_exchange(code) or Exchange.SZSE
    elif _CODE_RE.match(s):
        code = s
        exchange = infer_exchange(s) or Exchange.SZSE
    else:
        raise SymbolParseError(f"unable to detect asset type for symbol {text!r}.")
    return infer_asset_type(code, exchange).value


def is_valid_symbol(text: str) -> bool:
    """Return whether ``text`` parses as a valid symbol.

    Note: a valid format does NOT mean the security exists.
    """
    try:
        parse_symbol(text)
        return True
    except SymbolParseError:
        return False
