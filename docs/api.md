# tj-symbols API

> 中国证券代码的解析、标准化与格式转换。核心模型复用 tj-datamodel，支持 8 种格式。

## 目录

- [安装](#安装)
- [快速开始](#快速开始)
- [核心函数](#核心函数)
  - [convert](#convert)
  - [normalize](#normalize)
  - [parse_symbol](#parse_symbol)
  - [format_symbol](#format_symbol)
- [检测函数](#检测函数)
  - [detect_format](#detect_format)
  - [detect_exchange](#detect_exchange)
  - [detect_asset_type](#detect_asset_type)
  - [is_valid_symbol](#is_valid_symbol)
- [格式注册表](#格式注册表)
- [支持的格式](#支持的格式)
- [数据类型](#数据类型)
  - [ParseResult](#parseresult)
  - [SymbolFormatInfo](#symbolformatinfo)
- [异常](#异常)
- [CLI：tjsym](#cli-tjsym)

## 安装

```bash
pip install tj-symbols
```

## 快速开始

```python
from tj_symbols import convert, normalize, parse_symbol

convert("SH600519", to="tianji")  # "600519.SH"
convert("600519.SH", to="sina")  # "sh600519"
convert("000001.SZ", to="eastmoney")  # "0.000001"

normalize("sh600519")  # "600519.SH"
normalize("000001", exchange="SSE")  # "000001.SH"（裸码消歧）

result = parse_symbol("600519.SH")
result.normalized  # "600519.SH"
result.source_format  # "tianji"
```

## 核心函数

### convert

```python
def convert(
    symbol: str,
    to: str,
    from_format: str | None = None,
    exchange: str | Exchange | None = None,
    asset_type: str | AssetType | None = None,
    is_lower: bool | None = None,
) -> str
```

将 `symbol` 转换到目标格式 `to`。

- `from_format`：显式指定源格式，跳过自动检测。
- `exchange` / `asset_type`：裸 6 位代码存在歧义时用于消歧（`000001` 既可是深市股票也可是上证指数）。
- `is_lower`：控制输出字母大小写；`None` 使用格式默认（sina/baostock 默认小写，其余大写）。只影响字母，数字不受影响。

```python
convert("600519", to="tianji")  # 默认深市推断 → "600519.SH"
convert("600519", to="tianji", exchange="SSE")  # "600519.SH"
convert("000001", to="tianji", exchange="SSE")  # "000001.SH"
convert("000001", to="tianji", asset_type="index")  # "000001.SH"（上证指数）
convert("600519.SH", to="sina", is_lower=False)  # "SH600519"
```

### normalize

```python
def normalize(symbol: str, exchange=None, asset_type=None) -> str
```

将 `symbol` 标准化为 Tianji 标准格式 `<code>.<suffix>`。等价于 `convert(symbol, to="tianji")`。

```python
normalize("SH600519")  # "600519.SH"
normalize("000001.SZ")  # "000001.SZ"
```

### parse_symbol

```python
def parse_symbol(
    text: str,
    exchange: str | Exchange | None = None,
    asset_type: str | AssetType | None = None,
    from_format: str | None = None,
) -> ParseResult
```

解析 `text` 为 [`ParseResult`](#parseresult)，内含完整 [`Symbol`](https://github.com/Angryshark128/tj-datamodel/blob/main/docs/api.md#symbol) 及源格式。

- 显式 `exchange` 与字符串内嵌交易所冲突时抛 [`SymbolParseError`](#异常)。
- `exchange` 和 `asset_type` 同时给出时必须一致。

```python
from tj_symbols import parse_symbol

r = parse_symbol("SH600519")
r.symbol.code  # "600519"
r.symbol.exchange.value  # "SSE"
r.symbol.asset_type  # AssetType.STOCK
r.source_format  # "prefix"
```

### format_symbol

```python
def format_symbol(symbol: str, style: str, is_lower: bool | None = None) -> str
```

解析 `symbol` 并按 `style` 渲染。等价于 `convert(symbol, to=style)`。

```python
from tj_symbols import format_symbol

format_symbol("600519.SH", "baostock")  # "sh.600519"
```

## 检测函数

### detect_format

```python
def detect_format(text: str) -> str
```

返回字符串最可能的源格式名。无匹配抛 [`SymbolParseError`](#异常)。

```python
from tj_symbols import detect_format

detect_format("SH600519")  # "prefix"
detect_format("sh.600519")  # "baostock"
detect_format("600519.XSHG")  # "jqdata"
```

### detect_exchange

```python
def detect_exchange(text: str) -> str
```

返回交易所名（`"SSE"` / `"SZSE"` / `"BSE"`）。裸码按前缀推断，无解抛 [`SymbolParseError`](#异常)。

```python
from tj_symbols import detect_exchange

detect_exchange("600519.SH")  # "SSE"
detect_exchange("000001")  # "SZSE"
```

### detect_asset_type

```python
def detect_asset_type(text: str) -> str
```

返回资产类型名（`"stock"` / `"etf"` / `"index"` / …）。

```python
from tj_symbols import detect_asset_type

detect_asset_type("510300.SH")  # "etf"
detect_asset_type("000001.SZ")  # "stock"
detect_asset_type("000001", exchange="SSE")  # 作为上证指数
```

### is_valid_symbol

```python
def is_valid_symbol(text: str) -> bool
```

返回字符串是否能解析为合法符号。**格式合法 ≠ 证券真实存在**，本包不做存在性校验。

```python
from tj_symbols import is_valid_symbol

is_valid_symbol("600519.SH")  # True
is_valid_symbol("not-a-sym")  # False
```

## 格式注册表

| 函数 | 说明 |
| --- | --- |
| `list_formats()` | 全部已注册格式名列表 |
| `list_input_formats()` | 支持输入解析的格式名 |
| `list_output_formats()` | 支持输出渲染的格式名 |
| `get_format_info(name)` | 返回格式的 [`SymbolFormatInfo`](#symbolformatinfo)，未知格式抛 [`UnknownFormatError`](#异常) |

```python
from tj_symbols import get_format_info, list_formats

list_formats()
# ["tianji", "tushare", "prefix", "sina", "eastmoney", "jqdata", "baostock", "plain"]

info = get_format_info("eastmoney")
info.exchanges  # ("SSE", "SZSE")
info.lossy  # False
info.example  # "1.600519"
```

## 支持的格式

| 格式 | 示例 | 输入 | 输出 | 交易所 | 备注 |
| --- | --- | --- | --- | --- | --- |
| `tianji` | `600519.SH` | ✅ | ✅ | SSE/SZSE/BSE | 生态标准格式 |
| `tushare` | `600519.SH` | ✅ | ✅ | SSE/SZSE/BSE | 目前与 tianji 等价 |
| `prefix` | `SH600519` | ✅ | ✅ | SSE/SZSE/BSE | 大写前缀 + 代码 |
| `sina` | `sh600519` | ✅ | ✅ | SSE/SZSE | 默认小写，MVP 不含 BSE |
| `eastmoney` | `1.600519` | ✅ | ✅ | SSE/SZSE | 市场 id + 代码 |
| `jqdata` | `600519.XSHG` | ✅ | ✅ | SSE/SZSE | BSE 映射预留 |
| `baostock` | `sh.600519` | ✅ | ✅ | SSE/SZSE | 默认小写 |
| `plain` | `600519` | ✅ | ✅ | SSE/SZSE/BSE | **有损**：丢失交易所信息 |

> `plain` 是有损格式：转换会丢失交易所信息。裸码转回时按前缀推断，可能有歧义。

## 数据类型

### ParseResult

`parse_symbol` 的返回值，`frozen=True`。

| 属性 | 类型 | 说明 |
| --- | --- | --- |
| `symbol` | [`Symbol`](https://github.com/Angryshark128/tj-datamodel/blob/main/docs/api.md#symbol) | 规范化的完整 Symbol |
| `source_format` | `str \| None` | 识别出的源格式名 |
| `normalized` | `str` | 快捷属性，即 `symbol.normalized` |

方法：`format(style, is_lower=None)`，等价于对内部 Symbol 做 [`format_symbol`](#format_symbol)。

```python
from tj_symbols import parse_symbol

r = parse_symbol("sh600519")
r.source_format  # "sina"
r.format("tianji")  # "600519.SH"
r.format("baostock")  # "sh.600519"
```

### SymbolFormatInfo

格式注册表条目，`frozen=True`。常用字段：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `name` | `str` | 格式名（`"tianji"` 等） |
| `display_name` | `str` | 展示名（`"Eastmoney"` 等） |
| `example` | `str` | 通用示例 |
| `examples` | `dict[str, str]` | 按交易所的示例，键为 `"SSE"` / `"SZSE"` / `"BSE"` |
| `description` | `str` | 格式说明 |
| `input_supported` / `output_supported` | `bool` | 是否支持输入/输出 |
| `exchanges` | `tuple[str, ...]` | 支持的交易所 |
| `lossy` / `ambiguous` | `bool` | 是否信息有损 / 是否歧义 |
| `notes` | `tuple[str, ...]` | 附加说明 |

## 异常

| 异常 | 父类 | 触发条件 |
| --- | --- | --- |
| `TianjiSymbolsError` | `Exception` | 本包异常基类 |
| `SymbolParseError` | `TianjiSymbolsError` | 符号无法解析；显式 exchange 与内嵌冲突 |
| `UnknownFormatError` | `TianjiSymbolsError` | 格式名不在注册表中；未知交易所 |
| `UnsupportedFormatError` | `TianjiSymbolsError` | 格式不支持某交易所（如 `eastmoney` + BSE） |
| `AmbiguousSymbolError` | `TianjiSymbolsError` | 严格模式预留，MVP 未使用 |
| `InvalidSymbolError` | `TianjiSymbolsError` | 预留，MVP 未使用 |

## CLI：tjsym

安装包后提供 `tjsym` 命令。所有子命令支持 `--json`（部分）。

```bash
# 转换
tjsym convert SH600519 --to tianji            # 600519.SH
tjsym convert 000001 --to tianji --exchange SSE  # 000001.SH

# 标准化
tjsym normalize sh600519                      # 600519.SH

# 解析
tjsym parse 600519.SH --json

# 检测
tjsym detect-format sh.600519                 # baostock
tjsym detect-exchange 000001                  # SZSE
tjsym detect-asset-type 510300.SH             # etf

# 校验
tjsym validate 600519.SH; echo $?             # valid, exit 0
tjsym validate nope; echo $?                  # invalid, exit 1

# 注册表
tjsym formats --json
tjsym format-info sina

# 大小写控制（convert）
tjsym convert 600519.SH --to sina --upper     # SH600519
```

CLI 遇到本包异常时输出 `error: <message>` 到 stderr 并返回 1。
