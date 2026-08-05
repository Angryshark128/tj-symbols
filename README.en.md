[English](README.en.md) | [中文](README.md)

# Tianji Symbols

Market-aware symbol parsing, normalization, and format conversion for Chinese securities.

Tianji Symbols is part of the [Tianji](https://github.com/tianji-dev/tianji)
open-source market research toolkit. It converts symbols between the formats
commonly used by Tushare, Sina, Eastmoney, JQData, BaoStock, and Tianji itself.

## Features

- Auto-detect common Chinese security symbol formats
- Convert symbols to a specified target format
- Tianji canonical format: `600519.SH`
- Supports SSE, SZSE, and BSE rules
- Queryable format registry
- Output case control (`is_lower`)
- Offline-first, zero external data dependency

## Install

```bash
pip install tj-symbols
```

## Quickstart

```python
from tj_symbols import convert, normalize, parse_symbol

convert("SH600519", to="tianji")
# "600519.SH"

convert("600519.SH", to="sina")
# "sh600519"

convert("000001.SZ", to="eastmoney")
# "0.000001"

normalize("sh600519")
# "600519.SH"

parse_symbol("600519.SH")
# ParseResult(symbol=Symbol(code='600519', exchange=<Exchange.SSE: 'SSE'>, ...), source_format='tianji')
```

### CLI

```bash
tjsym convert SH600519 --to tianji
# 600519.SH

tjsym convert 600519.SH --to sina
# sh600519

tjsym convert 000001 --to tianji --exchange SSE
# 000001.SH

tjsym parse 600519.SH --json
```

```json
{
  "code": "600519",
  "exchange": "SSE",
  "suffix": "SH",
  "market": "CN_A_SHARE",
  "asset_type": "stock",
  "source_format": "tianji",
  "normalized": "600519.SH"
}
```

## Supported formats

```bash
tjsym formats
```

```
Name       Example       Input  Output  Exchanges       Notes
tianji     600519.SH     yes    yes     SSE,SZSE,BSE
tushare    600519.SH     yes    yes     SSE,SZSE,BSE    Currently equivalent to Tianji for supported markets.
prefix     SH600519      yes    yes     SSE,SZSE,BSE
sina       sh600519      yes    yes     SSE,SZSE        BSE support is not guaranteed in MVP.
eastmoney  1.600519      yes    yes     SSE,SZSE        BSE support varies by endpoint and is not guaranteed in MVP.
jqdata     600519.XSHG   yes    yes     SSE,SZSE        BSE mapping is reserved but not guaranteed in MVP.
baostock   sh.600519     yes    yes     SSE,SZSE        BSE support is not guaranteed in MVP.
plain      600519        yes    yes     SSE,SZSE,BSE    lossy, ambiguous
```

`plain` is lossy: converting to it drops the exchange. Converting a bare
`600519` back infers the exchange by code prefix and may be ambiguous (see below).

## Ambiguity handling

A bare 6-digit code can be ambiguous. `000001` is both `000001.SZ` (Ping An Bank)
and `000001.SH` (Shanghai Composite Index). Bare codes default to a stock / SZSE
interpretation; pass `exchange` or `asset_type` to disambiguate.

```python
normalize("000001")
# "000001.SZ"

normalize("000001", exchange="SSE")
# "000001.SH"

normalize("000001", asset_type="index")
# "000001.SH"
```

## CLI reference

```text
tjsym convert <symbol> --to <format> [--from <fmt>] [--exchange <ex>] [--lower|--upper]
tjsym normalize <symbol>
tjsym parse <symbol> [--json]
tjsym detect-format <symbol>
tjsym detect-exchange <symbol>
tjsym validate <symbol>
tjsym formats [--json]
tjsym format-info <format> [--json]
```

## Development

```bash
uv sync --group dev
uv run ruff check .
uv run ruff format --check .
uv run pyright
uv run pytest -q
```

## Tianji Ecosystem

Tianji is a composable open-source toolkit for market research.
Each package can be used independently or combined into a full workflow.

- tj-calendar: Offline-first trading calendar
- tj-symbols: Symbol normalization and format conversion
- tj-data: Market data adapters and local cache
- tj-factors: Technical indicators and factors
- tj-metrics: Performance metrics
- tj-backtest: Lightweight backtesting
- tj-research: AI-assisted research
- tj-terminal: Integrated research workspace

## Notes

Format validation does not mean the security actually exists.
This package does not provide market data, investment advice, or trading signals.

## Disclaimer

This project is for research and educational purposes only.
It does not provide investment advice, trading signals, or financial recommendations.
