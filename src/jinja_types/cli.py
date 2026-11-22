"""The `jinja-types` command: export the catalog and list conflict resolutions."""

import argparse
import io
import sys

from jinja_types.core import Kind, Registry


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="jinja-types", description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)

    catalog = commands.add_parser("catalog", help="print the catalog of every member")
    catalog.add_argument("--namespace", help="only this namespace ('helpers' for plain names)")
    catalog.add_argument("--kind", choices=[str(kind.name).lower() for kind in Kind])
    catalog.add_argument("--format", choices=["json", "markdown"], default="json")

    conflicts = commands.add_parser("conflicts", help="print every conflict resolution")

    for command in (catalog, conflicts):
        command.add_argument(
            "--plugins", action="store_true", help="also load 'jinja_types.plugins' entry points"
        )

    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the `jinja-types` command."""

    args = build_parser().parse_args(argv)
    registry = Registry.default(plugins=args.plugins)

    if isinstance(sys.stdout, io.TextIOWrapper):
        sys.stdout.reconfigure(encoding="utf-8")  # Windows consoles default to a legacy codepage

    if args.command == "conflicts":
        for conflict in registry.conflicts():
            print(f"{conflict.name}\t{conflict.resolution}\t{conflict.detail}")

        return 0

    catalog = registry.catalog().select(namespace=args.namespace, kind=args.kind)

    if not catalog:
        print("jinja-types: no members match the filters", file=sys.stderr)

        return 1

    print(catalog.to_json() if args.format == "json" else catalog.to_markdown())

    return 0
