"""Tests for symbol conversion."""

import pytest

from tj_symbols import convert, normalize
from tj_symbols.errors import UnsupportedFormatError


def test_prefix_to_tianji() -> None:
    assert convert("SH600519", to="tianji") == "600519.SH"


def test_tianji_to_sina() -> None:
    assert convert("600519.SH", to="sina") == "sh600519"


def test_sz_to_eastmoney() -> None:
    assert convert("000001.SZ", to="eastmoney") == "0.000001"


def test_sh_to_eastmoney() -> None:
    assert convert("600519.SH", to="eastmoney") == "1.600519"


def test_sh_to_jqdata() -> None:
    assert convert("600519.SH", to="jqdata") == "600519.XSHG"


def test_sz_to_jqdata() -> None:
    assert convert("000001.SZ", to="jqdata") == "000001.XSHE"


def test_sh_to_baostock() -> None:
    assert convert("600519.SH", to="baostock") == "sh.600519"


def test_sh_to_plain() -> None:
    assert convert("600519.SH", to="plain") == "600519"


def test_plain_is_lossy_drops_exchange() -> None:
    assert convert("000001.SZ", to="plain") == "000001"


def test_convert_to_prefix() -> None:
    assert convert("600519.SH", to="prefix") == "SH600519"


def test_convert_to_tushare() -> None:
    assert convert("600519.SH", to="tushare") == "600519.SH"


def test_convert_with_explicit_from_format() -> None:
    assert convert("sh600519", from_format="sina", to="tianji") == "600519.SH"


def test_convert_plain_default_szse() -> None:
    assert convert("000001", to="tianji") == "000001.SZ"


def test_convert_plain_with_exchange_sse() -> None:
    assert convert("000001", to="tianji", exchange="SSE") == "000001.SH"


def test_convert_plain_with_asset_type_index() -> None:
    assert convert("000001", to="tianji", asset_type="index") == "000001.SH"


def test_convert_plain_stock_600519() -> None:
    assert convert("600519", to="tianji") == "600519.SH"


def test_convert_plain_bse_430047() -> None:
    assert convert("430047", to="tianji") == "430047.BJ"


def test_prefix_default_upper() -> None:
    assert convert("600519.SH", to="prefix") == "SH600519"


def test_prefix_is_lower() -> None:
    assert convert("600519.SH", to="prefix", is_lower=True) == "sh600519"


def test_tianji_is_lower() -> None:
    assert convert("600519.SH", to="tianji", is_lower=True) == "600519.sh"


def test_tianji_default_upper() -> None:
    assert convert("600519.sh", to="tianji") == "600519.SH"


def test_sina_default_lower() -> None:
    assert convert("600519.SH", to="sina") == "sh600519"


def test_sina_is_lower_false() -> None:
    assert convert("600519.SH", to="sina", is_lower=False) == "SH600519"


def test_eastmoney_case_ignored() -> None:
    assert convert("600519.SH", to="eastmoney", is_lower=True) == "1.600519"


def test_jqdata_default_upper() -> None:
    assert convert("600519.SH", to="jqdata") == "600519.XSHG"


def test_jqdata_is_lower() -> None:
    assert convert("600519.SH", to="jqdata", is_lower=True) == "600519.xshg"


def test_baostock_default_lower() -> None:
    assert convert("600519.SH", to="baostock") == "sh.600519"


def test_baostock_is_lower_false() -> None:
    assert convert("600519.SH", to="baostock", is_lower=False) == "SH.600519"


def test_normalize_alias() -> None:
    assert normalize("SH600519") == "600519.SH"
    assert normalize("600519.sh") == "600519.SH"


def test_bse_to_baostock_raises() -> None:
    with pytest.raises(UnsupportedFormatError) as excinfo:
        convert("430047.BJ", to="baostock")
    message = str(excinfo.value)
    assert "format 'baostock' does not support exchange 'BSE'" in message
    assert "Supported exchanges for baostock: SSE, SZSE" in message
    assert "Run `tjsym format-info baostock` for details" in message


def test_bse_to_eastmoney_raises() -> None:
    with pytest.raises(UnsupportedFormatError):
        convert("430047.BJ", to="eastmoney")


def test_bse_to_jqdata_raises() -> None:
    with pytest.raises(UnsupportedFormatError):
        convert("430047.BJ", to="jqdata")


def test_bse_to_sina_raises() -> None:
    with pytest.raises(UnsupportedFormatError):
        convert("430047.BJ", to="sina")


def test_bse_to_prefix_ok() -> None:
    assert convert("430047.BJ", to="prefix") == "BJ430047"


def test_bse_to_tianji_ok() -> None:
    assert convert("430047.BJ", to="tianji") == "430047.BJ"
