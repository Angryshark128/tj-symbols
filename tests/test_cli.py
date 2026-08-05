"""Tests for CLI commands."""

import json

from tj_symbols import cli


def _run(argv: list[str]) -> tuple[int, str]:
    """Run cli.main, capturing stdout and stderr."""
    import io
    import sys
    from contextlib import redirect_stdout

    buf = io.StringIO()
    err_buf = io.StringIO()
    old_stderr = sys.stderr
    sys.stderr = err_buf
    try:
        with redirect_stdout(buf):
            code = cli.main(argv)
    finally:
        sys.stderr = old_stderr
    return code, buf.getvalue() + err_buf.getvalue()


def test_cli_convert() -> None:
    code, out = _run(["convert", "SH600519", "--to", "tianji"])
    assert code == 0
    assert out.strip() == "600519.SH"


def test_cli_convert_to_sina() -> None:
    code, out = _run(["convert", "600519.SH", "--to", "sina"])
    assert code == 0
    assert out.strip() == "sh600519"


def test_cli_convert_lower() -> None:
    code, out = _run(["convert", "600519.SH", "--to", "prefix", "--lower"])
    assert code == 0
    assert out.strip() == "sh600519"


def test_cli_convert_upper() -> None:
    code, out = _run(["convert", "sh600519", "--to", "sina", "--upper"])
    assert code == 0
    assert out.strip() == "SH600519"


def test_cli_convert_exchange() -> None:
    code, out = _run(["convert", "000001", "--to", "tianji", "--exchange", "SSE"])
    assert code == 0
    assert out.strip() == "000001.SH"


def test_cli_convert_explicit_from() -> None:
    code, out = _run(["convert", "sh600519", "--from", "sina", "--to", "tianji"])
    assert code == 0
    assert out.strip() == "600519.SH"


def test_cli_normalize() -> None:
    code, out = _run(["normalize", "SH600519"])
    assert code == 0
    assert out.strip() == "600519.SH"


def test_cli_parse() -> None:
    code, out = _run(["parse", "600519.SH"])
    assert code == 0
    assert out.strip() == "600519.SH"


def test_cli_parse_json() -> None:
    code, out = _run(["parse", "600519.SH", "--json"])
    assert code == 0
    data = json.loads(out)
    assert data["code"] == "600519"
    assert data["exchange"] == "SSE"
    assert data["suffix"] == "SH"
    assert data["market"] == "CN_A_SHARE"
    assert data["asset_type"] == "stock"
    assert data["source_format"] == "tianji"
    assert data["normalized"] == "600519.SH"


def test_cli_detect_format() -> None:
    code, out = _run(["detect-format", "sh600519"])
    assert code == 0
    assert out.strip() == "sina"


def test_cli_detect_exchange() -> None:
    code, out = _run(["detect-exchange", "600519"])
    assert code == 0
    assert out.strip() == "SSE"


def test_cli_validate_valid() -> None:
    code, out = _run(["validate", "600519.SH"])
    assert code == 0
    assert out.strip() == "valid"


def test_cli_validate_invalid() -> None:
    code, out = _run(["validate", "bad-symbol"])
    assert code == 1
    assert out.strip() == "invalid"


def test_cli_formats() -> None:
    code, out = _run(["formats"])
    assert code == 0
    assert "tianji" in out
    assert "plain" in out
    assert "lossy, ambiguous" in out


def test_cli_formats_json() -> None:
    code, out = _run(["formats", "--json"])
    assert code == 0
    data = json.loads(out)
    assert isinstance(data, list)
    names = [item["name"] for item in data]
    assert "eastmoney" in names
    plain = [item for item in data if item["name"] == "plain"][0]
    assert plain["lossy"] is True
    assert plain["ambiguous"] is True


def test_cli_format_info() -> None:
    code, out = _run(["format-info", "eastmoney"])
    assert code == 0
    assert "Name: eastmoney" in out
    assert "Display: Eastmoney" in out
    assert "Example: 1.600519" in out
    assert "Exchanges: SSE, SZSE" in out
    assert "Lossy: no" in out


def test_cli_format_info_json() -> None:
    code, out = _run(["format-info", "eastmoney", "--json"])
    assert code == 0
    data = json.loads(out)
    assert data["name"] == "eastmoney"
    assert data["examples"]["SSE"] == "1.600519"


def test_cli_unknown_format_error() -> None:
    code, out = _run(["convert", "600519.SH", "--to", "wind"])
    assert code == 1
    assert "unknown target format 'wind'" in out


def test_cli_bse_unsupported() -> None:
    code, out = _run(["convert", "430047.BJ", "--to", "baostock"])
    assert code == 1
    assert "does not support exchange 'BSE'" in out


def test_cli_parse_garbage_error() -> None:
    code, out = _run(["parse", "abc"])
    assert code == 1
    assert "unable to parse symbol 'abc'" in out
