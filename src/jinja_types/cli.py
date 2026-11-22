"""Command-line interface for jinja-types (stub until Phase 9)."""

import argparse


def main(argv: list[str] | None = None) -> int:
    """Run the `jinja-types` command."""
    parser = argparse.ArgumentParser(prog="jinja-types")

    parser.parse_args(argv)

    return 0
