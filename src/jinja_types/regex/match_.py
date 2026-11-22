"""The `match` namespace: members of the match objects returned by `re.search` and friends.

Not exposed: the undocumented `regs` attribute.
"""

import re

from jinja_types.core import Collection

from .engine import Match

collection = Collection("match", Match)

DATE = r"{{ '2026-11' | re.search('(?P<year>\\d+)-(?P<month>\\d+)-?(\\d+)?') | "


@collection.filter(
    examples=[
        (DATE + "match.group }}", {}, "2026-11"),
        (DATE + "match.group('month') }}", {}, "11"),
        (DATE + "match.group(1, 2) | join('|') }}", {}, "2026|11"),
    ]
)
def group(value: re.Match[str], /, *groups: int | str) -> str | tuple[str | None, ...] | None:
    """Return one group (by number or name; 0 or nothing is the whole match), or a tuple."""
    return value.group(*groups)


@collection.filter(
    examples=[
        (DATE + "match.groups | join('|') }}", {}, "2026|11|None"),
        (DATE + "match.groups('-') | join('|') }}", {}, "2026|11|-"),
    ]
)
def groups(value: re.Match[str], /, default: str | None = None) -> tuple[str | None, ...]:
    """Return every group; groups that did not take part get `default`."""
    return value.groups(default)


@collection.filter(
    examples=[
        (
            DATE + "match.groupdict | dictsort | map('join', '=') | join('|') }}",
            {},
            "month=11|year=2026",
        )
    ]
)
def groupdict(value: re.Match[str], /, default: str | None = None) -> dict[str, str | None]:
    """Return the named groups as a dict."""
    return value.groupdict(default)


@collection.filter(
    examples=[
        (DATE + "match.span | join('-') }}", {}, "0-7"),
        (DATE + "match.span('month') | join('-') }}", {}, "5-7"),
    ]
)
def span(value: re.Match[str], /, group: int | str = 0) -> tuple[int, int]:
    """Return `(start, end)` of a group."""
    return value.span(group)


@collection.filter(examples=[(DATE + "match.start(2) }}", {}, "5")])
def start(value: re.Match[str], /, group: int | str = 0) -> int:
    """Return the start index of a group."""
    return value.start(group)


@collection.filter(examples=[(DATE + "match.end(1) }}", {}, "4")])
def end(value: re.Match[str], /, group: int | str = 0) -> int:
    """Return the end index of a group."""
    return value.end(group)


@collection.filter(examples=[(DATE + r"match.expand('\\2/\\g<year>') }}", {}, "11/2026")])
def expand(value: re.Match[str], /, template: str) -> str:
    """Fill a `re.sub` style template (`\\1`, `\\g<name>`) from this match."""
    return value.expand(template)


@collection.attribute(examples=[(DATE + "match.string }}", {}, "2026-11")])
def string(value: re.Match[str], /) -> str:
    """The string that was searched."""
    return value.string


@collection.attribute(member="re", examples=[(DATE + "match.re | attr('groups') }}", {}, "3")])
def re_(value: re.Match[str], /) -> re.Pattern[str]:
    """The compiled pattern that produced this match."""
    return value.re


@collection.attribute(examples=[(DATE + "match.pos }}", {}, "0")])
def pos(value: re.Match[str], /) -> int:
    """The `pos` the search started from."""
    return value.pos


@collection.attribute(examples=[(DATE + "match.endpos }}", {}, "7")])
def endpos(value: re.Match[str], /) -> int:
    """The `endpos` the search stopped at."""
    return value.endpos


@collection.attribute(
    examples=[
        (DATE + "match.lastindex }}", {}, "2"),
        ("{{ 'a' | re.search('a') | match.lastindex }}", {}, "None"),
    ]
)
def lastindex(value: re.Match[str], /) -> int | None:
    """The index of the last group that matched, or None."""
    return value.lastindex


@collection.attribute(examples=[(DATE + "match.lastgroup }}", {}, "month")])
def lastgroup(value: re.Match[str], /) -> str | None:
    """The name of the last group that matched, or None."""
    return value.lastgroup
