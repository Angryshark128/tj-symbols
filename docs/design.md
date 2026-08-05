Tianji Symbols 设计文档

1. 项目概述

1.1 项目名称





母品牌：Tianji



子项目：tj-symbols



展示名：Tianji Symbols



Python 包名：tj-symbols



Python 模块名：tj_symbols



CLI 命令：tjsym

1.2 项目定位

tj-symbols 是 Tianji 生态中的证券代码识别、标准化与格式转换工具。

一句话定位：

Tianji Symbols provides market-aware symbol parsing, normalization, and format conversion for Chinese securities.

中文定位：

Tianji Symbols 提供中国证券代码识别、标准化与多格式转换能力。

它解决的问题是：用户和第三方数据源经常使用不同的证券代码格式，例如：

600519
600519.SH
SH600519
sh600519
SSE:600519
600519.XSHG
1.600519
sh.600519

tj-symbols 的目标是自动识别这些常见格式，并转换成用户指定的目标格式。

1.3 在 Tianji 生态中的角色

tj-symbols 是 Tianji 的基础设施模块，依赖 tj-datamodel 中的共享枚举和 Symbol 模型。

后续可被以下项目复用：





tj-data：统一不同数据源的证券代码格式。



tj-factors：对齐因子数据中的证券标识。



tj-backtest：统一标的输入格式。



tj-terminal：统一终端展示和搜索中的证券代码。



tj-research：统一 AI 分析报告中的标的引用。



2. 核心目标与非目标

2.1 核心目标





自动识别常见证券代码格式。



将任意支持格式转换为指定目标格式。



提供 Tianji 生态内部统一标准格式。



支持 Python API 和 CLI。



提供格式注册表，允许用户查询支持的格式、示例和限制。



尽量离线、轻量、无外部数据依赖。



为未来真实证券元数据校验预留扩展空间。

2.2 非目标

MVP 阶段不做：





不联网。



不查询证券名称。



不校验证券是否真实存在。



不查询上市日期、退市日期。



不维护行业分类。



不覆盖港股、美股、期货。



不承诺所有第三方平台所有接口格式都兼容。



不把 AkShare 这种多格式接口简单归为一个固定格式。



3. 核心设计原则

3.1 依赖 tj-datamodel

tj-symbols 应依赖 tj-datamodel，复用其中的公共类型：

Symbol
Exchange
Market
AssetType

这样可以保证 tj-symbols 输出的证券标识对象与 tj-data、tj-factors、tj-backtest 等后续项目一致。

依赖声明示例：

[project]
dependencies = [
  "tj-datamodel>=0.1,<0.2"
]

注意：SymbolFormatInfo 不放入 tj-datamodel，它属于 tj-symbols 自己的格式注册表。

3.2 三层转换模型

tj-symbols 不应只是字符串替换，而应采用三层模型：

输入字符串
  ↓
自动识别 / 显式解析
  ↓
Canonical Symbol 对象
  ↓
输出为指定格式枚举

也就是：

source format auto-detect
        ↓
canonical Symbol
        ↓
target format rendering

示例：

convert("SH600519", to="tushare")
# "600519.SH"
​
convert("600519.SH", to="sina")
# "sh600519"
​
convert("000001.SZ", to="eastmoney")
# "0.000001"
​
convert("SSE:600519", to="prefix")
# "SH600519"

3.3 Tianji 标准格式

Tianji 生态内部统一采用：

<code>.<suffix>

示例：

600519.SH
000001.SZ
430047.BJ
000300.SH
159915.SZ

标准后缀：

SH   上海证券交易所
SZ   深圳证券交易所
BJ   北京证券交易所

内部交易所枚举使用：

SSE   上海证券交易所
SZSE  深圳证券交易所
BSE   北京证券交易所

映射关系：

600519.SH -> exchange = SSE
000001.SZ -> exchange = SZSE
430047.BJ -> exchange = BSE

3.4 normalize 只是快捷转换

normalize(symbol) 不是唯一核心能力，而是：

convert(symbol, to="tianji")

的快捷别名。

3.5 输出大小写可控

格式转换除了目标格式外，还应允许用户控制输出大小写。

建议提供参数：

is_lower: bool | None = None

含义：

None   使用该格式的默认大小写
True   尽可能输出小写
False  尽可能输出大写

例如：

convert("600519.SH", to="prefix")
# "SH600519"

convert("600519.SH", to="prefix", is_lower=True)
# "sh600519"

convert("600519.SH", to="sina")
# "sh600519"

convert("600519.SH", to="sina", is_lower=False)
# "SH600519"

注意：大小写参数只影响字母部分，不影响数字、分隔符或第三方格式的市场编号。

例如：

convert("600519.SH", to="eastmoney", is_lower=True)
# "1.600519"

对于第三方平台格式，默认大小写应尽量遵循平台习惯。例如：

sina      默认小写：sh600519
baostock  默认小写：sh.600519
prefix    默认大写：SH600519
tianji    默认大写后缀：600519.SH
jqdata    默认大写后缀：600519.XSHG

3.6 格式合法不等于证券真实存在

MVP 只判断代码格式和规则，不保证证券真实存在。

例如：

is_valid_symbol("699999.SH")

可能返回格式合法，但不代表真实有这个证券。

需要区分：

is_valid_symbol      格式和规则是否合法
exists_symbol        是否真实存在，未来依赖 metadata

MVP 只做 is_valid_symbol，不做 exists_symbol。

3.7 自动识别不是万能的

纯 6 位代码存在歧义，例如：

000001

可能表示：

000001.SZ  平安银行
000001.SH  上证指数

默认可按股票语境推断为 000001.SZ，但必须允许用户通过 exchange 或 asset_type 显式指定。



4. 市场与资产范围

4.1 MVP 覆盖市场

MVP 覆盖中国内地证券市场：

SSE   上海证券交易所
SZSE  深圳证券交易所
BSE   北京证券交易所

逻辑市场：

CN_A_SHARE  中国 A 股整体市场

4.2 暂不覆盖市场

MVP 暂不覆盖：

HKEX    港交所
NYSE    纽交所
NASDAQ  纳斯达克
CFFEX   中金所
SHFE    上期所
DCE     大商所
CZCE    郑商所
INE     上海国际能源交易中心

原因：





港股、美股、期货的代码规则不同。



过早纳入会显著扩大项目边界。



MVP 应先服务中国内地证券标识的高频场景。

4.3 MVP 资产类型

建议支持资产类型枚举：

stock       股票
etf         ETF
index       指数
fund        场内基金
bond        债券，MVP 可只预留
convertible_bond  可转债，MVP 可只预留
unknown     未知类型

MVP 实际重点支持：

stock
etf
index
fund
unknown

债券、可转债规则较多，可放到后续版本。



5. 支持的输入格式

MVP 应支持自动识别以下常见输入格式。

5.1 纯 6 位代码

600519
000001
300750
688981
430047

根据代码前缀推断交易所：

600519 -> 600519.SH
000001 -> 000001.SZ
300750 -> 300750.SZ
688981 -> 688981.SH
430047 -> 430047.BJ

注意：纯代码可能有歧义。

5.2 Tianji / Tushare 风格

600519.SH
000001.SZ
430047.BJ

大小写不敏感：

600519.sh -> 600519.SH

5.3 前缀格式

SH600519
SZ000001
BJ430047
sh600519
sz000001
bj430047

标准化为：

600519.SH
000001.SZ
430047.BJ

5.4 冒号格式

SSE:600519
SZSE:000001
BSE:430047
SH:600519
SZ:000001
BJ:430047

标准化为：

600519.SH
000001.SZ
430047.BJ

5.5 点分交易所格式

SH.600519
SZ.000001
BJ.430047
SSE.600519
SZSE.000001
BSE.430047

标准化为：

600519.SH
000001.SZ
430047.BJ

5.6 JQData 风格

600519.XSHG
000001.XSHE

标准化为：

600519.SH
000001.SZ

5.7 Eastmoney 风格

1.600519
0.000001

映射：

1.xxxxxx -> SSE
0.xxxxxx -> SZSE

BSE 支持情况需谨慎，MVP 可不承诺。

5.8 BaoStock 风格

sh.600519
sz.000001

标准化为：

600519.SH
000001.SZ



6. 支持的输出格式枚举

6.1 MVP 格式枚举

MVP 支持以下格式：

tianji       600519.SH
tushare      600519.SH
prefix       SH600519
sina         sh600519
eastmoney    1.600519 / 0.000001
jqdata       600519.XSHG / 000001.XSHE
baostock     sh.600519 / sz.000001
plain        600519

6.2 暂缓格式

暂缓支持：

akshare      因为不同接口格式不统一
ricequant    可后续加，或作为 jqdata alias
wind         可能涉及更多资产类型
同花顺       规则需要确认
雪球         规则需要确认

6.3 格式说明

tianji

Format: 600519.SH
Examples:
  SSE: 600519.SH
  SZSE: 000001.SZ
  BSE: 430047.BJ

Tianji 生态内部标准格式。

tushare

Format: 600519.SH
Examples:
  SSE: 600519.SH
  SZSE: 000001.SZ
  BSE: 430047.BJ

Tushare 常见 ts_code 风格。MVP 阶段与 Tianji 格式相同，但保留独立枚举，方便未来处理特殊资产类型。

prefix

Format: SH600519
Examples:
  SSE: SH600519
  SZSE: SZ000001
  BSE: BJ430047

大写交易所前缀 + 证券代码。

sina

Format: sh600519
Examples:
  SSE: sh600519
  SZSE: sz000001

新浪财经常见小写前缀格式。BSE 支持不在 MVP 中保证。

eastmoney

Format: 1.600519
Examples:
  SSE: 1.600519
  SZSE: 0.000001

东方财富常见市场编号 + 代码格式。

注意：东方财富不同接口可能存在差异，BSE 支持情况不在 MVP 中保证。

jqdata

Format: 600519.XSHG
Examples:
  SSE: 600519.XSHG
  SZSE: 000001.XSHE

JoinQuant / JQData 常见格式。

BSE 映射可预留，例如 XBSE，但 MVP 不保证。

baostock

Format: sh.600519
Examples:
  SSE: sh.600519
  SZSE: sz.000001

BaoStock 常见格式。BSE 支持不在 MVP 中保证。

plain

Format: 600519
Examples:
  SSE: 600519
  SZSE: 000001
  BSE: 430047

纯 6 位代码。

注意：plain 输出会丢失交易所信息，是有损格式；plain 输入可能需要推断，存在歧义。



7. Format Registry 设计

7.1 为什么需要格式注册表

支持的格式不应只写在 README 里，而应作为可编程接口提供。

原因：





用户可以通过 API 查询支持哪些格式。



CLI 可以复用同一份格式说明。



第三方项目可以动态判断支持能力。



新增格式时只需扩展 registry。



对 plain 等有损或歧义格式可以给出明确提示。

7.2 格式信息结构

建议定义：

from dataclasses import dataclass

@dataclass(frozen=True)
class SymbolFormatInfo:
    name: str
    display_name: str
    example: str
    examples: dict[str, str]
    description: str
    input_supported: bool
    output_supported: bool
    exchanges: tuple[str, ...]
    lossy: bool = False
    ambiguous: bool = False
    notes: tuple[str, ...] = ()

未来可扩展字段：

third_party: str | None
reference_url: str | None
stability: Literal["stable", "endpoint_dependent", "experimental"]

7.3 Python API

from tj_symbols import (
    list_formats,
    list_input_formats,
    list_output_formats,
    get_format_info,
)

list_formats()
list_input_formats()
list_output_formats()
get_format_info("eastmoney")

7.4 示例返回

SymbolFormatInfo(
    name="eastmoney",
    display_name="Eastmoney",
    example="1.600519",
    examples={
        "SSE": "1.600519",
        "SZSE": "0.000001",
    },
    description="Market id plus code format commonly used by Eastmoney APIs.",
    input_supported=True,
    output_supported=True,
    exchanges=("SSE", "SZSE"),
    lossy=False,
    ambiguous=False,
    notes=(
        "BSE support varies by endpoint and is not guaranteed in MVP.",
    ),
)

7.5 MVP 格式注册表内容

tianji
  display: Tianji
  example: 600519.SH
  examples:
    SSE: 600519.SH
    SZSE: 000001.SZ
    BSE: 430047.BJ
  input: yes
  output: yes
  exchanges: SSE, SZSE, BSE
  lossy: no
  ambiguous: no

tushare
  display: Tushare
  example: 600519.SH
  examples:
    SSE: 600519.SH
    SZSE: 000001.SZ
    BSE: 430047.BJ
  input: yes
  output: yes
  exchanges: SSE, SZSE, BSE
  lossy: no
  ambiguous: no
  note: Currently equivalent to Tianji for supported markets.

prefix
  display: Prefix
  example: SH600519
  examples:
    SSE: SH600519
    SZSE: SZ000001
    BSE: BJ430047
  input: yes
  output: yes
  exchanges: SSE, SZSE, BSE
  lossy: no
  ambiguous: no

sina
  display: Sina
  example: sh600519
  examples:
    SSE: sh600519
    SZSE: sz000001
  input: yes
  output: yes
  exchanges: SSE, SZSE
  lossy: no
  ambiguous: no
  note: BSE support is not guaranteed in MVP.

eastmoney
  display: Eastmoney
  example: 1.600519
  examples:
    SSE: 1.600519
    SZSE: 0.000001
  input: yes
  output: yes
  exchanges: SSE, SZSE
  lossy: no
  ambiguous: no
  note: BSE support varies by endpoint and is not guaranteed in MVP.

jqdata
  display: JoinQuant/JQData
  example: 600519.XSHG
  examples:
    SSE: 600519.XSHG
    SZSE: 000001.XSHE
  input: yes
  output: yes
  exchanges: SSE, SZSE
  lossy: no
  ambiguous: no
  note: BSE mapping is reserved but not guaranteed in MVP.

baostock
  display: BaoStock
  example: sh.600519
  examples:
    SSE: sh.600519
    SZSE: sz.000001
  input: yes
  output: yes
  exchanges: SSE, SZSE
  lossy: no
  ambiguous: no
  note: BSE support is not guaranteed in MVP.

plain
  display: Plain Code
  example: 600519
  examples:
    SSE: 600519
    SZSE: 000001
    BSE: 430047
  input: yes
  output: yes
  exchanges: SSE, SZSE, BSE
  lossy: yes
  ambiguous: yes
  note: Plain output drops exchange information. Plain input may require inference.



8. 核心 API 设计

8.1 convert

最核心 API：

from tj_symbols import convert

convert("SH600519", to="tianji")
# "600519.SH"

convert("600519.SH", to="sina")
# "sh600519"

convert("000001.SZ", to="eastmoney")
# "0.000001"

convert("600519.SH", to="jqdata")
# "600519.XSHG"

支持显式指定源格式：

convert("sh600519", from_format="sina", to="tianji")

支持消除歧义：

convert("000001", to="tianji", exchange="SSE")
# "000001.SH"

convert("000001", to="tianji", asset_type="index")
# "000001.SH"

支持输出大小写控制：

convert("600519.SH", to="prefix", is_lower=True)
# "sh600519"

convert("600519.SH", to="tianji", is_lower=True)
# "600519.sh"

convert("600519.SH", to="sina", is_lower=False)
# "SH600519"

建议签名：

def convert(
    symbol: str,
    to: str,
    from_format: str | None = None,
    exchange: str | None = None,
    asset_type: str | None = None,
    is_lower: bool | None = None,
) -> str:
    ...

is_lower 含义：

None   使用目标格式默认大小写
True   尽可能输出小写
False  尽可能输出大写

8.2 normalize

from tj_symbols import normalize

normalize("SH600519")
# "600519.SH"

等价于：

convert("SH600519", to="tianji")

8.3 parse_symbol

from tj_symbols import parse_symbol

parse_symbol("sh600519")

返回 ParseResult，其中包含 tj_datamodel.Symbol：

ParseResult(
    symbol=Symbol(
        code="600519",
        exchange=Exchange.SSE,
        suffix="SH",
        market=Market.CN_A_SHARE,
        asset_type=AssetType.STOCK,
        normalized="600519.SH",
    ),
    source_format="sina",
)

8.4 format_symbol

from tj_symbols import format_symbol

format_symbol("600519.SH", style="sina")
# "sh600519"

format_symbol("600519.SH", style="prefix", is_lower=True)
# "sh600519"

或者：

result = parse_symbol("SH600519")
result.format("eastmoney")
# "1.600519"

result.format("tianji", is_lower=True)
# "600519.sh"

8.5 detect_format

from tj_symbols import detect_format

detect_format("sh600519")
# "sina"

detect_format("600519.XSHG")
# "jqdata"

对于可能匹配多个格式的输入，可以返回最佳猜测，或提供详细版本：

detect_formats("600519.SH")
# ["tianji", "tushare"]

MVP 可先提供 detect_format，后续再加 detect_formats。

8.6 detect_exchange

from tj_symbols import detect_exchange

detect_exchange("600519")
# "SSE"

detect_exchange("000001")
# "SZSE"

detect_exchange("430047")
# "BSE"

8.7 detect_asset_type

from tj_symbols import detect_asset_type

detect_asset_type("600519")
# "stock"

detect_asset_type("510300")
# "etf"

detect_asset_type("000300.SH")
# "index"

注意：MVP 资产类型识别是规则型识别，不保证完全准确。

8.8 is_valid_symbol

from tj_symbols import is_valid_symbol

is_valid_symbol("600519.SH")
# True

is_valid_symbol("bad-symbol")
# False

需要文档说明：

valid format != listed security exists



9. Symbol 与解析结果设计

9.1 复用 tj-datamodel.Symbol

tj-symbols 不再自行定义 Symbol，而是复用 tj-datamodel 中的不可变模型：

from tj_datamodel import Symbol, Exchange, Market, AssetType

Symbol(
    code="600519",
    exchange=Exchange.SSE,
    suffix="SH",
    market=Market.CN_A_SHARE,
    asset_type=AssetType.STOCK,
    normalized="600519.SH",
)

9.2 ParseResult

由于 source_format 是 tj-symbols 的解析上下文，不属于全生态通用 Symbol 模型，因此建议 parse_symbol 返回一个 ParseResult，其中包含 Symbol 和解析元信息。

from dataclasses import dataclass
from tj_datamodel import Symbol

@dataclass(frozen=True)
class ParseResult:
    symbol: Symbol
    source_format: str | None = None

    @property
    def normalized(self) -> str:
        return self.symbol.normalized

    def format(self, style: str, is_lower: bool | None = None) -> str:
        ...

示例：

ParseResult(
    symbol=Symbol(
        code="600519",
        exchange=Exchange.SSE,
        suffix="SH",
        market=Market.CN_A_SHARE,
        asset_type=AssetType.STOCK,
        normalized="600519.SH",
    ),
    source_format="sina",
)



10. 交易所映射表

核心映射：

SSE:
  suffix: SH
  prefix: SH / sh
  jqdata: XSHG
  eastmoney: 1
  baostock: sh

SZSE:
  suffix: SZ
  prefix: SZ / sz
  jqdata: XSHE
  eastmoney: 0
  baostock: sz

BSE:
  suffix: BJ
  prefix: BJ / bj
  jqdata: XBSE，预留，MVP 不保证
  eastmoney: 待确认，MVP 不保证
  baostock: 待确认，MVP 不保证

对不确定平台格式，MVP 应采取保守策略：





不支持就抛出明确异常。



不要猜测输出。



在格式注册表中说明限制。

例如：

convert("430047.BJ", to="baostock")

如果 BaoStock MVP 不支持 BSE，应抛出：

UnsupportedFormatError: format 'baostock' does not support exchange 'BSE'.
Supported exchanges for baostock: SSE, SZSE.
Run `tjsym format-info baostock` for details.



11. 代码推断规则

11.1 SSE 常见规则

600xxx  主板股票
601xxx  主板股票
603xxx  主板股票
605xxx  主板股票
688xxx  科创板股票
510xxx  ETF
511xxx  债券 ETF / 货币基金等
512xxx  ETF
513xxx  跨境 ETF
515xxx  ETF
516xxx  ETF
588xxx  科创 ETF
000xxx  上证指数，注意和深市股票冲突，需要上下文

11.2 SZSE 常见规则

000xxx  主板股票 / 指数冲突
001xxx  主板股票
002xxx  中小板历史代码，现主板
003xxx  主板股票
300xxx  创业板股票
159xxx  ETF
160xxx  LOF / 基金
161xxx  LOF / 基金
162xxx  LOF / 基金
399xxx  深证指数

11.3 BSE 常见规则

4xxxxx  北交所 / 新三板相关
8xxxxx  北交所 / 新三板相关
920xxx  北交所

BSE 规则需要谨慎，很多 4/8 开头证券可能历史上属于新三板或股转系统，不一定都是北交所。

MVP 可以简化推断为 BSE，但文档必须说明规则型识别的局限。



12. 重要歧义处理

12.1 000001 歧义

000001.SZ  平安银行
000001.SH  上证指数

纯代码：

000001

默认按股票语境推断为：

000001.SZ

用户可显式指定：

normalize("000001", exchange="SSE")
# "000001.SH"

normalize("000001", asset_type="index")
# "000001.SH"

12.2 399001 与指数

399001.SZ  深证成指

纯代码 399001 应推断为：

399001.SZ

资产类型为：

index

12.3 plain 格式有损

convert("600519.SH", to="plain")
# "600519"

plain 输出会丢失交易所信息，因此是有损格式。

格式注册表中应标记：

lossy = true
ambiguous = true



13. CLI 设计

13.1 核心命令

tjsym convert <symbol> --to <format>
tjsym normalize <symbol>
tjsym parse <symbol>
tjsym detect-format <symbol>
tjsym detect-exchange <symbol>
tjsym validate <symbol>
tjsym formats
tjsym format-info <format>

13.2 转换示例

tjsym convert SH600519 --to tianji

输出：

600519.SH

tjsym convert 600519.SH --to sina

输出：

sh600519

tjsym convert 000001.SZ --to eastmoney

输出：

0.000001

tjsym convert 600519.SH --to jqdata

输出：

600519.XSHG

支持显式源格式：

tjsym convert sh600519 --from sina --to tianji

支持消除歧义：

tjsym convert 000001 --to tianji --exchange SSE

输出：

000001.SH

支持大小写控制：

tjsym convert 600519.SH --to prefix --lower

输出：

sh600519

tjsym convert sh600519 --to sina --upper

输出：

SH600519

13.3 formats 命令

tjsym formats

输出：

Name        Example       Input  Output  Exchanges        Notes
tianji      600519.SH     yes    yes     SSE,SZSE,BSE     canonical
tushare     600519.SH     yes    yes     SSE,SZSE,BSE     same as Tianji
prefix      SH600519      yes    yes     SSE,SZSE,BSE
sina        sh600519      yes    yes     SSE,SZSE         BSE not guaranteed
eastmoney   1.600519      yes    yes     SSE,SZSE         endpoint-dependent
jqdata      600519.XSHG   yes    yes     SSE,SZSE         BSE not guaranteed
baostock    sh.600519     yes    yes     SSE,SZSE         BSE not guaranteed
plain       600519        yes    yes     SSE,SZSE,BSE     lossy, ambiguous

13.4 format-info 命令

tjsym format-info eastmoney

输出：

Name: eastmoney
Display: Eastmoney
Example: 1.600519
Examples:
  SSE: 1.600519
  SZSE: 0.000001
Input supported: yes
Output supported: yes
Exchanges: SSE, SZSE
Lossy: no
Ambiguous: no
Notes:
  - BSE support varies by endpoint and is not guaranteed in MVP.

13.5 JSON 输出

CLI 应支持 JSON 输出，方便脚本和其他工具消费：

tjsym parse 600519.SH --json
tjsym formats --json
tjsym format-info eastmoney --json

示例：

tjsym parse 600519.SH --json

输出：

{
  "code": "600519",
  "exchange": "SSE",
  "suffix": "SH",
  "market": "CN_A_SHARE",
  "asset_type": "stock",
  "source_format": "tianji",
  "normalized": "600519.SH"
}



14. 异常设计

建议定义异常：

class TianjiSymbolsError(Exception):
    pass

class SymbolParseError(TianjiSymbolsError):
    pass

class UnknownFormatError(TianjiSymbolsError):
    pass

class UnsupportedFormatError(TianjiSymbolsError):
    pass

class AmbiguousSymbolError(TianjiSymbolsError):
    pass

class InvalidSymbolError(TianjiSymbolsError):
    pass

14.1 解析失败

SymbolParseError: unable to parse symbol 'abc'.

14.2 未知格式

UnknownFormatError: unknown target format 'wind'. Run `tjsym formats` to list supported formats.

14.3 格式不支持交易所

UnsupportedFormatError: format 'baostock' does not support exchange 'BSE'.
Supported exchanges for baostock: SSE, SZSE.
Run `tjsym format-info baostock` for details.

14.4 歧义代码

MVP 默认可以进行合理推断，不一定抛出歧义异常。

但对严格模式可设计：

convert("000001", to="tianji", strict=True)

如果存在歧义则抛出：

AmbiguousSymbolError: plain code '000001' can refer to 000001.SZ or 000001.SH. Specify exchange or asset_type.

严格模式可放到后续版本。



15. 数据依赖策略

15.1 MVP 无外部数据依赖

MVP 使用规则实现：





代码格式解析。



源格式识别。



交易所推断。



资产类型粗略识别。



格式转换。



格式注册表查询。

不依赖外部数据文件，不联网。

15.2 未来 metadata 扩展

后续可以增加可选 metadata：

证券名称
上市日期
退市日期
市场板块
真实存在校验
行业分类

这部分可以独立为：

tj-symbols-data

或者由：

tj-data

提供。

但不应让 MVP 依赖 metadata。



16. 项目结构建议

tj-symbols/
  README.md
  pyproject.toml
  LICENSE
  src/
    tj_symbols/
      __init__.py
      api.py
      parser.py
      formatter.py
      registry.py
      rules.py
      types.py
      errors.py
      cli.py
  tests/
    test_convert.py
    test_parse.py
    test_format.py
    test_registry.py
    test_rules.py
    test_cli.py
  docs/
    formats.md
    ambiguity.md

模块职责：

api.py        顶层 API，例如 convert / normalize / parse_symbol
parser.py     输入格式识别与解析
formatter.py  Symbol 对象到目标格式的渲染
registry.py   格式注册表与格式说明接口
rules.py      交易所推断和资产类型规则
types.py      ParseResult、SymbolFormatInfo 等 tj-symbols 专属类型；Symbol 来自 tj-datamodel
errors.py     异常定义
cli.py        命令行入口



17. 测试策略

17.1 转换测试

覆盖：





SH600519 -> 600519.SH



600519.SH -> sh600519



000001.SZ -> 0.000001



600519.SH -> 600519.XSHG



600519.SH -> sh.600519



600519.SH -> 600519

17.2 解析测试

覆盖：





Tianji / Tushare 风格。



Prefix 风格。



Sina 风格。



Eastmoney 风格。



JQData 风格。



BaoStock 风格。



Plain 风格。

17.3 歧义测试

覆盖：





000001 默认推断。



000001 指定 exchange="SSE"。



000001 指定 asset_type="index"。



plain 输出有损标记。

17.4 格式注册表测试

覆盖：





list_formats() 返回所有 MVP 格式。



get_format_info("eastmoney") 返回正确示例。



list_input_formats() 只返回输入支持格式。



list_output_formats() 只返回输出支持格式。



plain 标记 lossy=True 和 ambiguous=True。

17.5 异常测试

覆盖：





无法解析的字符串。



未知目标格式。



不支持的交易所格式转换。



BSE 转换到不保证支持的平台格式。

17.6 CLI 测试

覆盖：





tjsym convert



tjsym normalize



tjsym parse



tjsym formats



tjsym format-info



--json 输出



18. README 建议

README 首屏：

# Tianji Symbols

Market-aware symbol parsing, normalization, and format conversion for Chinese securities.

Tianji Symbols is part of the Tianji open-source market research toolkit.
It helps convert symbols between common formats used by Tushare, Sina, Eastmoney, JQData, BaoStock, and Tianji.

核心卖点：

## Features

- Auto-detect common Chinese security symbol formats
- Convert symbols to a specified target format
- Tianji canonical format: 600519.SH
- Supports SSE, SZSE, and BSE-oriented rules
- Supports Python API and CLI
- Provides a queryable format registry
- Offline-first and no external data dependency

免责声明：

## Notes

Format validation does not mean the security actually exists.
This package does not provide market data, investment advice, or trading signals.



19. 版本规划

v0.1.0





支持 SSE、SZSE、BSE 基础规则。



支持 Tianji 标准格式 600519.SH。



支持格式枚举：





tianji



tushare



prefix



sina



eastmoney



jqdata



baostock



plain



支持核心 API：





convert



normalize



parse_symbol



format_symbol



detect_format



detect_exchange



detect_asset_type



is_valid_symbol



支持输出大小写控制参数 is_lower。



支持格式注册表 API：





list_formats



list_input_formats



list_output_formats



get_format_info



支持 CLI：





tjsym convert



tjsym normalize



tjsym parse



tjsym formats



tjsym format-info

v0.2.0





增强歧义处理。



增加 strict 模式。



增加更多资产类型规则。



改进 BSE 支持说明。



增加更多 CLI JSON 输出。

v0.3.0





可选支持 RiceQuant 格式。



可选支持 Wind 格式。



明确 AkShare 不同接口的多个格式枚举。



增加批量转换 API。

v1.0.0





API 稳定。



格式注册表稳定。



核心格式转换行为稳定。



被 Tianji 其他子项目复用。



20. 最终决策摘要





tj-symbols 是 Tianji 生态的证券代码识别、标准化与格式转换基础模块。



tj-symbols 应依赖 tj-datamodel，复用 Symbol、Exchange、Market、AssetType。



它不只是多格式输入转标准格式，而是支持自动识别源格式并转换为指定目标格式枚举。



Tianji 内部标准格式为 600519.SH。



normalize(symbol) 等价于 convert(symbol, to="tianji")。



convert 和 format_symbol 应支持 is_lower: bool | None，用于控制输出中字母部分的大小写。



MVP 覆盖 SSE、SZSE、BSE。



MVP 重点支持股票、ETF、指数、场内基金和 unknown 类型。



MVP 不校验证券是否真实存在，不查询证券名称，不联网。



MVP 支持格式：tianji、tushare、prefix、sina、eastmoney、jqdata、baostock、plain。



parse_symbol 建议返回 ParseResult，其中包含 tj_datamodel.Symbol 和 source_format 等解析上下文。



plain 是有损且可能歧义的格式，必须在格式注册表中明确标记。



第三方平台中 BSE 支持不确定的格式应保守处理，不应猜测输出。



必须提供格式注册表 API，让用户查询支持格式、示例、说明、支持交易所和限制。



CLI 必须支持 tjsym formats 和 tjsym format-info <format>。



CLI 转换命令应支持 --lower 和 --upper，分别对应 is_lower=True 与 is_lower=False。



格式合法不等于证券真实存在，文档和 API 行为需要明确区分。



项目应保持轻量、离线、规则驱动，为未来 metadata 扩展预留空间。


