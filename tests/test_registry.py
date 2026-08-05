"""Tests for the format registry."""

import pytest

from tj_symbols import get_format_info, list_formats, list_input_formats, list_output_formats
from tj_symbols.errors import UnknownFormatError

MVP_FORMATS = ["tianji", "tushare", "prefix", "sina", "eastmoney", "jqdata", "baostock", "plain"]


def test_list_formats() -> None:
    assert list_formats() == MVP_FORMATS


def test_list_input_formats() -> None:
    assert set(list_input_formats()) == set(MVP_FORMATS)


def test_list_output_formats() -> None:
    assert set(list_output_formats()) == set(MVP_FORMATS)


def test_get_format_info_eastmoney() -> None:
    info = get_format_info("eastmoney")
    assert info.name == "eastmoney"
    assert info.display_name == "Eastmoney"
    assert info.example == "1.600519"
    assert info.examples == {"SSE": "1.600519", "SZSE": "0.000001"}
    assert info.input_supported is True
    assert info.output_supported is True
    assert info.exchanges == ("SSE", "SZSE")
    assert info.lossy is False
    assert info.ambiguous is False
    assert info.notes


def test_get_format_info_plain_flags() -> None:
    info = get_format_info("plain")
    assert info.lossy is True
    assert info.ambiguous is True


def test_get_format_info_tianji() -> None:
    info = get_format_info("tianji")
    assert info.exchanges == ("SSE", "SZSE", "BSE")
    assert info.examples == {"SSE": "600519.SH", "SZSE": "000001.SZ", "BSE": "430047.BJ"}


def test_get_format_info_unknown_raises() -> None:
    with pytest.raises(UnknownFormatError) as excinfo:
        get_format_info("wind")
    assert "unknown target format 'wind'" in str(excinfo.value)
    assert "Run `tjsym formats` to list supported formats" in str(excinfo.value)


def test_sina_exchanges() -> None:
    info = get_format_info("sina")
    assert info.exchanges == ("SSE", "SZSE")


def test_baostock_exchanges() -> None:
    info = get_format_info("baostock")
    assert info.exchanges == ("SSE", "SZSE")


def test_jqdata_exchanges() -> None:
    info = get_format_info("jqdata")
    assert info.exchanges == ("SSE", "SZSE")
