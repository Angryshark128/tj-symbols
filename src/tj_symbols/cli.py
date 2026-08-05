"""Command-line interface for tj-symbols (``tjsym``)."""

from __future__ import annotations

import argparse
import json
import sys

from tj_symbols.api import (
    convert,
    detect_asset_type,
    detect_exchange,
    detect_format,
    get_format_info,
    is_valid_symbol,
    list_formats,
    normalize,
    parse_symbol,
)
from tj_symbols.errors import TianjiSymbolsError


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="tjsym",
        description="Market-aware symbol parsing, normalization, and format conversion for Chinese securities.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("convert", help="Convert a symbol to a target format")
    p.add_argument("symbol")
    p.add_argument("--to", required=True)
    p.add_argument("--from", dest="from_format", default=None)
    p.add_argument("--exchange", default=None)
    p.add_argument("--asset-type", dest="asset_type", default=None)
    p.add_argument("--lower", action="store_true", help="Prefer lowercase letters in output")
    p.add_argument("--upper", action="store_true", help="Prefer uppercase letters in output")
    p.set_defaults(func=_cmd_convert)

    p = sub.add_parser("normalize", help="Normalize a symbol to the Tianji canonical format")
    p.add_argument("symbol")
    p.set_defaults(func=_cmd_normalize)

    p = sub.add_parser("parse", help="Parse a symbol and show its canonical form")
    p.add_argument("symbol")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=_cmd_parse)

    p = sub.add_parser("detect-format", help="Detect the source format of a symbol")
    p.add_argument("symbol")
    p.set_defaults(func=_cmd_detect_format)

    p = sub.add_parser("detect-exchange", help="Detect the exchange of a symbol")
    p.add_argument("symbol")
    p.set_defaults(func=_cmd_detect_exchange)

    p = sub.add_parser("detect-asset-type", help="Detect the asset type of a symbol")
    p.add_argument("symbol")
    p.set_defaults(func=_cmd_detect_asset_type)

    p = sub.add_parser("validate", help="Check whether a symbol has a valid format")
    p.add_argument("symbol")
    p.set_defaults(func=_cmd_validate)

    p = sub.add_parser("formats", help="List supported formats")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=_cmd_formats)

    p = sub.add_parser("format-info", help="Show details for one format")
    p.add_argument("format")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=_cmd_format_info)

    return parser


def _resolve_lower(args: argparse.Namespace) -> bool | None:
    if getattr(args, "lower", False):
        return True
    if getattr(args, "upper", False):
        return False
    return None


def _cmd_convert(args: argparse.Namespace) -> int:
    is_lower = _resolve_lower(args)
    out = convert(
        args.symbol,
        to=args.to,
        from_format=args.from_format,
        exchange=args.exchange,
        asset_type=args.asset_type,
        is_lower=is_lower,
    )
    print(out)
    return 0


def _cmd_normalize(args: argparse.Namespace) -> int:
    print(normalize(args.symbol))
    return 0


def _cmd_parse(args: argparse.Namespace) -> int:
    result = parse_symbol(args.symbol)
    if args.json:
        print(json.dumps(_parse_result_to_dict(result), ensure_ascii=False, indent=2))
    else:
        print(result.normalized)
    return 0


def _parse_result_to_dict(result) -> dict:
    return {
        "code": result.symbol.code,
        "exchange": result.symbol.exchange.value,
        "suffix": result.symbol.suffix,
        "market": result.symbol.market.value,
        "asset_type": result.symbol.asset_type.value,
        "source_format": result.source_format,
        "normalized": result.normalized,
    }


def _cmd_detect_format(args: argparse.Namespace) -> int:
    print(detect_format(args.symbol))
    return 0


def _cmd_detect_exchange(args: argparse.Namespace) -> int:
    print(detect_exchange(args.symbol))
    return 0


def _cmd_detect_asset_type(args: argparse.Namespace) -> int:
    print(detect_asset_type(args.symbol))
    return 0


def _cmd_validate(args: argparse.Namespace) -> int:
    valid = is_valid_symbol(args.symbol)
    print("valid" if valid else "invalid")
    return 0 if valid else 1


def _cmd_formats(args: argparse.Namespace) -> int:
    infos = [get_format_info(name) for name in list_formats()]
    if args.json:
        print(json.dumps([_format_info_to_dict(info) for info in infos], ensure_ascii=False, indent=2))
        return 0

    header = f"{'Name':<10} {'Example':<13} {'Input':<6} {'Output':<7} {'Exchanges':<15} Notes"
    print(header)
    for info in infos:
        notes_parts = []
        if info.lossy:
            notes_parts.append("lossy")
        if info.ambiguous:
            notes_parts.append("ambiguous")
        notes = ", ".join(notes_parts + list(info.notes))
        print(
            f"{info.name:<10} {info.example:<13} "
            f"{'yes' if info.input_supported else 'no':<6} "
            f"{'yes' if info.output_supported else 'no':<7} "
            f"{','.join(info.exchanges):<15} {notes}"
        )
    return 0


def _format_info_to_dict(info) -> dict:
    return {
        "name": info.name,
        "display_name": info.display_name,
        "example": info.example,
        "examples": info.examples,
        "description": info.description,
        "input_supported": info.input_supported,
        "output_supported": info.output_supported,
        "exchanges": list(info.exchanges),
        "lossy": info.lossy,
        "ambiguous": info.ambiguous,
        "notes": list(info.notes),
    }


def _cmd_format_info(args: argparse.Namespace) -> int:
    info = get_format_info(args.format)
    if args.json:
        print(json.dumps(_format_info_to_dict(info), ensure_ascii=False, indent=2))
        return 0

    print(f"Name: {info.name}")
    print(f"Display: {info.display_name}")
    print(f"Example: {info.example}")
    print("Examples:")
    for exchange, example in info.examples.items():
        print(f"  {exchange}: {example}")
    print(f"Input supported: {'yes' if info.input_supported else 'no'}")
    print(f"Output supported: {'yes' if info.output_supported else 'no'}")
    print(f"Exchanges: {', '.join(info.exchanges)}")
    print(f"Lossy: {'yes' if info.lossy else 'no'}")
    print(f"Ambiguous: {'yes' if info.ambiguous else 'no'}")
    print("Notes:")
    if info.notes:
        for note in info.notes:
            print(f"  - {note}")
    else:
        print("  (none)")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except TianjiSymbolsError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    except (ValueError, TypeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
