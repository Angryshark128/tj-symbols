"""Tests for symbol parsing."""

import pytest
from tj_datamodel import AssetType, Exchange, Market

from tj_symbols import parse_symbol
from tj_symbols.errors import SymbolParseError


def test_parse_tianji() -> None:
    result = parse_symbol("600519.SH")
    assert result.source_format == "tianji"
    assert result.symbol.code == "600519"
    assert result.symbol.exchange is Exchange.SSE
    assert result.symbol.suffix == "SH"
    assert result.symbol.market is Market.CN_A_SHARE
    assert result.symbol.asset_type is AssetType.STOCK
    assert result.normalized == "600519.SH"


def test_parse_tianji_lowercase() -> None:
    result = parse_symbol("600519.sh")
    assert result.symbol.exchange is Exchange.SSE
    assert result.normalized == "600519.SH"


def test_parse_tushare() -> None:
    result = parse_symbol("000001.SZ")
    assert result.symbol.exchange is Exchange.SZSE
    assert result.normalized == "000001.SZ"


def test_parse_prefix() -> None:
    result = parse_symbol("SH600519")
    assert result.source_format == "prefix"
    assert result.symbol.exchange is Exchange.SSE
    assert result.normalized == "600519.SH"


def test_parse_prefix_lowercase() -> None:
    result = parse_symbol("sz000001")
    assert result.symbol.exchange is Exchange.SZSE


def test_parse_sina() -> None:
    result = parse_symbol("sh600519")
    assert result.source_format == "sina"
    assert result.symbol.exchange is Exchange.SSE


def test_parse_eastmoney_sse() -> None:
    result = parse_symbol("1.600519")
    assert result.source_format == "eastmoney"
    assert result.symbol.exchange is Exchange.SSE


def test_parse_eastmoney_szse() -> None:
    result = parse_symbol("0.000001")
    assert result.source_format == "eastmoney"
    assert result.symbol.exchange is Exchange.SZSE


def test_parse_jqdata_sse() -> None:
    result = parse_symbol("600519.XSHG")
    assert result.source_format == "jqdata"
    assert result.symbol.exchange is Exchange.SSE


def test_parse_jqdata_szse() -> None:
    result = parse_symbol("000001.XSHE")
    assert result.source_format == "jqdata"
    assert result.symbol.exchange is Exchange.SZSE


def test_parse_baostock_sse() -> None:
    result = parse_symbol("sh.600519")
    assert result.source_format == "baostock"
    assert result.symbol.exchange is Exchange.SSE


def test_parse_baostock_szse() -> None:
    result = parse_symbol("sz.000001")
    assert result.source_format == "baostock"
    assert result.symbol.exchange is Exchange.SZSE


def test_parse_plain_stock() -> None:
    result = parse_symbol("600519")
    assert result.source_format == "plain"
    assert result.symbol.exchange is Exchange.SSE


def test_parse_plain_bse() -> None:
    result = parse_symbol("430047")
    assert result.symbol.exchange is Exchange.BSE


def test_parse_plain_000001_default_szse() -> None:
    result = parse_symbol("000001")
    assert result.symbol.exchange is Exchange.SZSE
    assert result.symbol.asset_type is AssetType.STOCK


def test_parse_plain_000001_exchange_sse() -> None:
    result = parse_symbol("000001", exchange="SSE")
    assert result.symbol.exchange is Exchange.SSE


def test_parse_plain_000001_asset_type_index() -> None:
    result = parse_symbol("000001", asset_type="index")
    assert result.symbol.exchange is Exchange.SSE
    assert result.symbol.asset_type is AssetType.INDEX


def test_parse_plain_399_index() -> None:
    result = parse_symbol("399001")
    assert result.symbol.exchange is Exchange.SZSE
    assert result.symbol.asset_type is AssetType.INDEX


def test_parse_etf_510300() -> None:
    result = parse_symbol("510300")
    assert result.symbol.asset_type is AssetType.ETF


def test_parse_bj_explicit_exchange() -> None:
    result = parse_symbol("920001")
    assert result.symbol.exchange is Exchange.BSE


def test_parse_conflicting_exchange_raises() -> None:
    with pytest.raises(SymbolParseError):
        parse_symbol("600519.SH", exchange="SZSE")


def test_parse_garbage_raises() -> None:
    with pytest.raises(SymbolParseError):
        parse_symbol("abc")


def test_parse_empty_raises() -> None:
    with pytest.raises(SymbolParseError):
        parse_symbol("")


def test_parse_short_code_raises() -> None:
    with pytest.raises(SymbolParseError):
        parse_symbol("60051")


def test_parse_long_code_raises() -> None:
    with pytest.raises(SymbolParseError):
        parse_symbol("6005191")


def test_parse_result_format() -> None:
    result = parse_symbol("SH600519")
    assert result.format("eastmoney") == "1.600519"
    assert result.format("sina") == "sh600519"
    assert result.format("tianji", is_lower=True) == "600519.sh"


def test_parse_result_normalized_property() -> None:
    result = parse_symbol("sz000001")
    assert result.normalized == "000001.SZ"
