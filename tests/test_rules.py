"""Tests for the exchange and asset-type inference rules."""

from tj_datamodel import AssetType, Exchange

from tj_symbols.rules import infer_asset_type, infer_exchange


def test_infer_exchange_sse() -> None:
    assert infer_exchange("600519") is Exchange.SSE
    assert infer_exchange("601318") is Exchange.SSE
    assert infer_exchange("603259") is Exchange.SSE
    assert infer_exchange("688981") is Exchange.SSE
    assert infer_exchange("510300") is Exchange.SSE


def test_infer_exchange_szse() -> None:
    assert infer_exchange("000001") is Exchange.SZSE
    assert infer_exchange("001979") is Exchange.SZSE
    assert infer_exchange("002594") is Exchange.SZSE
    assert infer_exchange("300750") is Exchange.SZSE
    assert infer_exchange("159915") is Exchange.SZSE


def test_infer_exchange_bse() -> None:
    assert infer_exchange("430047") is Exchange.BSE
    assert infer_exchange("830799") is Exchange.BSE
    assert infer_exchange("920001") is Exchange.BSE


def test_infer_exchange_unknown() -> None:
    assert infer_exchange("") is None


def test_infer_asset_type_stock() -> None:
    assert infer_asset_type("600519") is AssetType.STOCK
    assert infer_asset_type("300750") is AssetType.STOCK


def test_infer_asset_type_etf() -> None:
    assert infer_asset_type("510300") is AssetType.ETF
    assert infer_asset_type("159915") is AssetType.ETF
    assert infer_asset_type("512880") is AssetType.ETF
    assert infer_asset_type("588000") is AssetType.ETF


def test_infer_asset_type_index() -> None:
    assert infer_asset_type("399001") is AssetType.INDEX
    assert infer_asset_type("000300", Exchange.SSE) is AssetType.INDEX


def test_infer_asset_type_000001_context() -> None:
    # 000xxx is an index on SSE but a stock on SZSE.
    assert infer_asset_type("000001", Exchange.SZSE) is AssetType.STOCK
    assert infer_asset_type("000001", Exchange.SSE) is AssetType.INDEX
    assert infer_asset_type("000001") is AssetType.STOCK


def test_infer_asset_type_fund() -> None:
    assert infer_asset_type("161725") is AssetType.FUND
