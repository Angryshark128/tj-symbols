"""Heuristic rules for exchange inference and asset-type inference.

These rules are intentionally simple and rule-based. They infer a plausible
exchange/asset-type from the numeric code prefix, following common Chinese
securities conventions. They do NOT guarantee that a security exists; they
only produce a reasonable default for parsing/formatting.

Reference: design doc section 11.
"""

from __future__ import annotations

from tj_datamodel import AssetType, Exchange

# --- Exchange inference ---------------------------------------------------

_SSE_PREFIXES = ("6", "9", "5")
_SZSE_PREFIXES = ("0", "1", "2", "3")
_BSE_PREFIXES = ("4", "8", "92")

# BSE 920xxx is a strict prefix; "92" is checked before the broad "9" SSE rule.
_BSE_920_PREFIX = "920"


def infer_exchange(code: str) -> Exchange | None:
    """Infer the most likely exchange for a numeric code.

    Returns ``None`` when no rule matches (caller decides how to handle).
    """
    if not code:
        return None
    if code.startswith(_BSE_920_PREFIX):
        return Exchange.BSE
    first = code[0]
    if first in _SSE_PREFIXES:
        return Exchange.SSE
    if first in _SZSE_PREFIXES:
        return Exchange.SZSE
    if first in _BSE_PREFIXES:
        return Exchange.BSE
    return None


def exchange_supports_code(exchange: Exchange, code: str) -> bool:
    """Return whether ``code`` is a plausible code for ``exchange``."""
    return infer_exchange(code) == exchange


def infer_exchange_for_asset_type(code: str, asset_type: AssetType) -> Exchange | None:
    """Infer an exchange from an explicitly requested asset type.

    Used to disambiguate plain codes: ``000001`` with asset_type=index means
    the SSE 上证指数, while asset_type=stock defaults to the SZSE stock.
    """
    if asset_type == AssetType.INDEX and code.startswith("000"):
        return Exchange.SSE
    return infer_exchange(code)


# --- Asset-type inference -------------------------------------------------

# ETF prefix ranges (SSE 510/511/512/513/515/516/588, SZSE 159).
_ETF_PREFIXES = ("510", "511", "512", "513", "515", "516", "517", "518", "588", "159")

# SSE broad-market indices (000xxx on SSE).
_SSE_INDEX_PREFIXES = ("000",)

# SZSE indices (399xxx).
_SZSE_INDEX_PREFIXES = ("399",)


def infer_asset_type(code: str, exchange: Exchange | None = None) -> AssetType:
    """Infer the most likely asset type for a code.

    ``exchange`` may be passed to resolve ambiguous prefixes (e.g. ``000001``
    is a stock on SZSE but an index on SSE).
    """
    if code.startswith(_ETF_PREFIXES):
        return AssetType.ETF
    if code.startswith(_SZSE_INDEX_PREFIXES):
        return AssetType.INDEX
    if code.startswith(_SSE_INDEX_PREFIXES):
        if exchange is Exchange.SSE:
            return AssetType.INDEX
        return AssetType.STOCK
    if _is_fund_like(code):
        return AssetType.FUND
    return AssetType.STOCK


def _is_fund_like(code: str) -> bool:
    """Very coarse fund detection (LOF/off-exchange fund ranges)."""
    if not code.startswith(("1",)):
        return False
    # 160/161/162 are SZSE LOF ranges.
    return code.startswith(("160", "161", "162", "163", "164", "165", "166", "167"))
