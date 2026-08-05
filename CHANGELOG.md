# Changelog

本项目遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/) 与 [语义化版本](https://semver.org/lang/zh-CN/)。

## [Unreleased]

### Added
- 首个 MVP 版本：中国证券代码识别、标准化与格式转换。

## [0.1.0] - 2026-08-04

### Added
- 支持格式：`tianji` / `tushare` / `prefix` / `sina` / `eastmoney` / `jqdata` / `baostock` / `plain`。
- Python API：`convert` / `normalize` / `parse_symbol` / `format_symbol` / `detect_format` / `detect_exchange` / `detect_asset_type` / `is_valid_symbol`。
- 格式注册表 API：`list_formats` / `list_input_formats` / `list_output_formats` / `get_format_info`。
- CLI `tjsym`：`convert` / `normalize` / `parse` / `detect-format` / `detect-exchange` / `validate` / `formats` / `format-info`，支持 `--json` / `--lower` / `--upper`。
- 覆盖 SSE / SZSE / BSE 规则。
- 歧义处理：裸代码默认推断，支持 `exchange` / `asset_type` 消歧。
- 复用 `tj-datamodel` 的 `Symbol` / `Exchange` / `Market` / `AssetType`。
- 离线优先，零外部数据依赖。

[Unreleased]: https://github.com/tianji-dev/tj-symbols/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/tianji-dev/tj-symbols/releases/tag/v0.1.0
