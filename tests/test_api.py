"""Tests for the top-level API helpers."""

import pytest

from tj_symbols import (
    detect_asset_type,
    detect_exchange,
    detect_format,
    format_symbol,
    is_valid_symbol,
)
from tj_symbols.errors import SymbolParseError, UnknownFormatError


def test_detect_format_tianji() -> None:
    assert detect_format("600519.SH") == "tianji"


def test_detect_format_sina() -> None:
    assert detect_format("sh600519") == "sina"


def test_detect_format_prefix() -> None:
    assert detect_format("SH600519") == "prefix"


def test_detect_format_jqdata() -> None:
    assert detect_format("600519.XSHG") == "jqdata"


def test_detect_format_eastmoney() -> None:
    assert detect_format("1.600519") == "eastmoney"


def test_detect_format_baostock() -> None:
    assert detect_format("sh.600519") == "baostock"


def test_detect_format_plain() -> None:
    assert detect_format("600519") == "plain"


def test_detect_format_garbage_raises() -> None:
    with pytest.raises(SymbolParseError):
        detect_format("abc")


def test_detect_exchange_stock() -> None:
    assert detect_exchange("600519") == "SSE"
    assert detect_exchange("000001") == "SZSE"
    assert detect_exchange("430047") == "BSE"


def test_detect_exchange_from_embedded() -> None:
    assert detect_exchange("600519.SH") == "SSE"
    assert detect_exchange("sz000001") == "SZSE"
    assert detect_exchange("sh.600519") == "SSE"


def test_detect_asset_type_stock() -> None:
    assert detect_asset_type("600519") == "stock"


def test_detect_asset_type_etf() -> None:
    assert detect_asset_type("510300") == "etf"


def test_detect_asset_type_index_sse() -> None:
    assert detect_asset_type("000300.SH") == "index"


def test_detect_asset_type_index_szse() -> None:
    assert detect_asset_type("399001") == "index"


def test_detect_asset_type_000001_default_stock() -> None:
    assert detect_asset_type("000001") == "stock"


def test_detect_asset_type_garbage_raises() -> None:
    with pytest.raises(SymbolParseError):
        detect_asset_type("abc")


def test_format_symbol() -> None:
    assert format_symbol("600519.SH", style="sina") == "sh600519"
    assert format_symbol("600519.SH", style="prefix", is_lower=True) == "sh600519"


def test_is_valid_symbol_true() -> None:
    assert is_valid_symbol("600519.SH") is True
    assert is_valid_symbol("SH600519") is True
    assert is_valid_symbol("000001") is True
    assert is_valid_symbol("430047.BJ") is True


def test_is_valid_symbol_false() -> None:
    assert is_valid_symbol("bad-symbol") is False
    assert is_valid_symbol("") is False
    assert is_valid_symbol("12345") is False


def test_unknown_exchange_in_parse() -> None:
    with pytest.raises(UnknownFormatError):
        format_symbol("600519.SH", style="wind")
