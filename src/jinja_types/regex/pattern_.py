"""The `pattern` namespace: members of compiled patterns, made with the `re.compile` global.

The pattern is the piped value (`self`), as in Python: `{{ word | pattern.findall(text) }}`.
`endpos` defaults to None (the end of the string): the `regex` library rejects `sys.maxsize`.
"""

import re
from collections.abc import Iterator, Mapping

from jinja_types.core import Collection

from . import engine
from .engine import Pattern
from .re_ import MACRO, Repl, substitute

collection = Collection("pattern", Pattern)

WORD = "{% set word = re.compile('\\\\w+', re.I) %}"
DATE = "{% set date = re.compile('(?P<year>\\\\d+)-(?P<month>\\\\d+)') %}"


def bounds(pos: int, endpos: int | None) -> dict[str, int]:
    """`pos` and `endpos` as keyword arguments, leaving out an `endpos` of None."""
    return {"pos": pos} if endpos is None else {"pos": pos, "endpos": endpos}


@collection.filter(
    test=True,
    examples=[
        (DATE + "{{ date | pattern.search('on 2026-11') | match.group('year') }}", {}, "2026"),
        (DATE + "{{ date is pattern.search('on 2026-11') }}", {}, "True"),
        (DATE + "{{ date | pattern.search('2026-11', 1) | match.group }}", {}, "026-11"),
    ],
)
def search(
    value: re.Pattern[str], /, string: str, pos: int = 0, endpos: int | None = None
) -> re.Match[str] | None:
    """Return the first match in `string[pos:endpos]`, or None. Also a test."""
    return engine.method(value, "search", string, **bounds(pos, endpos))


@collection.filter(
    test=True,
    examples=[
        (DATE + "{{ date | pattern.match('2026-11!') | match.group('month') }}", {}, "11"),
        (DATE + "{{ date is pattern.match('on 2026-11') }}", {}, "False"),
        (DATE + "{{ date is pattern.match('on 2026-11', 3) }}", {}, "True"),
    ],
)
def match(
    value: re.Pattern[str], /, string: str, pos: int = 0, endpos: int | None = None
) -> re.Match[str] | None:
    """Return the match at the start of `string[pos:endpos]`, or None. Also a test."""
    return engine.method(value, "match", string, **bounds(pos, endpos))


@collection.filter(
    test=True,
    examples=[
        (DATE + "{{ date is pattern.fullmatch('2026-11') }}", {}, "True"),
        (DATE + "{{ date is pattern.fullmatch('2026-11!') }}", {}, "False"),
        (DATE + "{{ date is pattern.fullmatch('2026-11!', 0, 7) }}", {}, "True"),
    ],
)
def fullmatch(
    value: re.Pattern[str], /, string: str, pos: int = 0, endpos: int | None = None
) -> re.Match[str] | None:
    """Return the match if the pattern matches all of `string[pos:endpos]`, or None. Also a test."""
    return engine.method(value, "fullmatch", string, **bounds(pos, endpos))


@collection.filter(
    examples=[
        (WORD + "{{ word | pattern.findall('Hi, you two') | join('|') }}", {}, "Hi|you|two"),
        (WORD + "{{ word | pattern.findall('Hi, you two', 3, 7) | join('|') }}", {}, "you"),
        (
            DATE + "{{ date | pattern.findall('2026-11 1999-01') | map('join', '/') | join }}",
            {},
            "2026/111999/01",
        ),
    ]
)
def findall(
    value: re.Pattern[str], /, string: str, pos: int = 0, endpos: int | None = None
) -> list[str] | list[tuple[str, ...]]:
    """Return every non-overlapping match: strings, or tuples of groups."""
    return engine.method(value, "findall", string, **bounds(pos, endpos))


@collection.filter(
    examples=[
        (
            WORD + "{{ word | pattern.finditer('ab cde') | map('match.span') "
            "| map('join', '-') | join('|') }}",
            {},
            "0-2|3-6",
        )
    ]
)
def finditer(
    value: re.Pattern[str], /, string: str, pos: int = 0, endpos: int | None = None
) -> Iterator[re.Match[str]]:
    """Return an iterator of match objects."""
    return engine.method(value, "finditer", string, **bounds(pos, endpos))


@collection.filter(
    examples=[
        (WORD + "{{ word | pattern.sub('#', 'ab, cd') }}", {}, "#, #"),
        (WORD + "{{ word | pattern.sub('[\\\\g<0>]', 'ab, cd', 1) }}", {}, "[ab], cd"),
        (MACRO + WORD + "{{ word | pattern.sub(up, 'ab, cd') }}", {}, "AB, CD"),
    ]
)
def sub(value: re.Pattern[str], /, repl: Repl, string: str, count: int = 0) -> str:
    """Replace matches in `string` with `repl`: a string (`\\1`, `\\g<name>`) or a macro."""
    return substitute(string, value, repl, count)[0]


@collection.filter(
    examples=[
        (WORD + "{{ word | pattern.subn('#', 'ab, cd') | join('|') }}", {}, "#, #|2"),
        (MACRO + WORD + "{{ word | pattern.subn(up, 'ab, cd', 1) | join('|') }}", {}, "AB, cd|1"),
    ]
)
def subn(value: re.Pattern[str], /, repl: Repl, string: str, count: int = 0) -> tuple[str, int]:
    """Like `pattern.sub`, but return `(new_string, number_of_substitutions)`."""
    return substitute(string, value, repl, count)


@collection.filter(
    examples=[
        ("{{ re.compile(',\\\\s*') | pattern.split('a, b,c') | join('|') }}", {}, "a|b|c"),
        ("{{ re.compile(',\\\\s*') | pattern.split('a, b,c', 1) | join('|') }}", {}, "a|b,c"),
    ]
)
def split(value: re.Pattern[str], /, string: str, maxsplit: int = 0) -> list[str | None]:
    """Split `string` by the matches. Groups in the pattern are kept."""
    return engine.method(value, "split", string, maxsplit=maxsplit)


@collection.attribute(examples=[(WORD + "{{ word | pattern.pattern }}", {}, "\\w+")])
def pattern(value: re.Pattern[str], /) -> str:
    """The pattern string."""
    return value.pattern


@collection.attribute(
    # the engines set different default bits, so only check re.I
    examples=[(WORD + "{{ (word | pattern.flags) // re.I % 2 }}", {}, "1")]
)
def flags(value: re.Pattern[str], /) -> int:
    """The flags the pattern was compiled with, plus the engine's defaults."""
    return value.flags


@collection.attribute(examples=[(DATE + "{{ date | pattern.groups }}", {}, "2")])
def groups(value: re.Pattern[str], /) -> int:
    """The number of capturing groups."""
    return value.groups


@collection.attribute(examples=[(DATE + "{{ (date | pattern.groupindex)['month'] }}", {}, "2")])
def groupindex(value: re.Pattern[str], /) -> Mapping[str, int]:
    """Map each named group to its number."""
    return value.groupindex
