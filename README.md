[English](README.en.md) | **中文**

[![PyPI version](https://img.shields.io/pypi/v/tj-symbols?color=4b6ef5&label=pypi)](https://pypi.org/project/tj-symbols/)
[![PyPI - Python](https://img.shields.io/pypi/pyversions/tj-symbols?color=4b6ef5)](https://pypi.org/project/tj-symbols/)
[![CI](https://github.com/Angryshark128/tj-symbols/actions/workflows/ci.yml/badge.svg)](https://github.com/Angryshark128/tj-symbols/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

# Tianji Symbols

面向中国证券的代码识别、标准化与多格式转换工具。

Tianji Symbols 是 [Tianji](https://github.com/tianji-dev/tianji) 开源市场研究工具生态的组成部分。它可以在 Tushare、新浪、东方财富、聚宽、BaoStock 与 Tianji 自身常用的代码格式之间转换。

## 特性

- 自动识别常见的中国证券代码格式
- 转换为指定的目标格式
- Tianji 标准格式：`600519.SH`
- 支持沪深北（SSE、SZSE、BSE）规则
- 可编程查询的格式注册表
- 输出大小写控制（`is_lower`）
- 离线优先，零外部数据依赖

## 安装

```bash
pip install tj-symbols
```

## 快速开始

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

## 支持的格式

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

`plain` 是有损格式：转换成它会丢失交易所信息。将裸 `600519` 转回来时按代码前缀推断交易所，可能存在歧义（见下文）。

## 歧义处理

裸 6 位代码可能存在歧义。`000001` 既可以是 `000001.SZ`（平安银行），也可以是 `000001.SH`（上证指数）。裸代码默认按股票 / 深市解释；传入 `exchange` 或 `asset_type` 可消除歧义。

```python
normalize("000001")
# "000001.SZ"

normalize("000001", exchange="SSE")
# "000001.SH"

normalize("000001", asset_type="index")
# "000001.SH"
```

## CLI 参考

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

## 开发

```bash
uv sync --group dev
uv run ruff check .
uv run ruff format --check .
uv run pyright
uv run pytest -q
```

## Tianji 生态

Tianji 是一套面向市场研究的可组合开源工具生态。每个子项目都可以独立使用，也可以组合成完整的市场研究工作流。

- tj-calendar: 离线优先的交易日历
- tj-symbols: 证券代码标准化与格式转换
- tj-data: 市场数据适配与本地缓存
- tj-factors: 技术指标与因子
- tj-metrics: 绩效指标
- tj-backtest: 轻量回测
- tj-research: AI 辅助研究
- tj-terminal: 综合研究工作台

## Notes / 说明

格式合法不代表证券真实存在。
本包不提供市场数据、投资建议或交易信号。

## Disclaimer / 免责声明

This project is for research and educational purposes only.
It does not provide investment advice, trading signals, or financial recommendations.

本项目仅用于研究和教育目的，不构成投资建议、交易信号或金融建议。
