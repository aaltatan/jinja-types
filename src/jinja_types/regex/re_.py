"""The `re` namespace: the `re` module functions, with the string piped in.

`re.search("x")` on a value calls `re.search("x", value)`. Parameter names follow Python
(`pattern`, `repl`, `count`, `maxsplit`, `flags`); flags come from the `re` global (`re.I`, …).
`re.compile` is not in v1.
"""

import re
from collections.abc import Callable, Iterator

from markupsafe import Markup

from jinja_types.core import Collection

from . import engine

collection = Collection("re", str)

type Repl = str | Callable[[re.Match[str]], object]

MACRO = "{% macro up(m) %}{{ m | match.group(0) | upper }}{% endmacro %}"


@collection.filter(
    test=True,
    examples=[
        (r"{{ 'ABC-42' | re.search('abc-(\\d+)', flags=re.I) | match.group(1) }}", {}, "42"),
        (r"{{ 'ABC-42' is re.search('\\d') }}", {}, "True"),
        (r"{{ 'ABC' | re.search('\\d') }}", {}, "None"),
    ],
)
def search(value: str, /, pattern: str, flags: int = 0) -> re.Match[str] | None:
    """Return the first match of `pattern` anywhere in the value, or None. Also a test."""
    return engine.call("search", pattern, value, flags=flags)


@collection.filter(
    test=True,
    examples=[
        (r"{{ '42-ABC' | re.match('\\d+') | match.group }}", {}, "42"),
        (r"{{ 'ABC-42' is re.match('\\d') }}", {}, "False"),
    ],
)
def match(value: str, /, pattern: str, flags: int = 0) -> re.Match[str] | None:
    """Return the match of `pattern` at the start of the value, or None. Also a test."""
    return engine.call("match", pattern, value, flags=flags)


@collection.filter(
    test=True,
    examples=[
        (r"{{ '2026' is re.fullmatch('\\d{4}') }}", {}, "True"),
        (r"{{ '2026-11' is re.fullmatch('\\d{4}') }}", {}, "False"),
    ],
)
def fullmatch(value: str, /, pattern: str, flags: int = 0) -> re.Match[str] | None:
    """Return the match if `pattern` matches the whole value, or None. Also a test."""
    return engine.call("fullmatch", pattern, value, flags=flags)


@collection.filter(
    examples=[
        (r"{{ 'a1 b22 c333' | re.findall('\\d+') | join('|') }}", {}, "1|22|333"),
        (r"{{ 'a=1 b=2' | re.findall('(\\w)=(\\d)') | map('join') | join('|') }}", {}, "a1|b2"),
    ]
)
def findall(value: str, /, pattern: str, flags: int = 0) -> list[str] | list[tuple[str, ...]]:
    """Return every non-overlapping match: strings, or tuples of groups."""
    return engine.call("findall", pattern, value, flags=flags)


@collection.filter(
    examples=[
        (
            r"{{ 'a1 b22' | re.finditer('\\d+') | map('match.span') "
            r"| map('join', '-') | join('|') }}",
            {},
            "1-2|4-6",
        )
    ]
)
def finditer(value: str, /, pattern: str, flags: int = 0) -> Iterator[re.Match[str]]:
    """Return an iterator of match objects."""
    return engine.call("finditer", pattern, value, flags=flags)


def substitute(value: str, pattern: str, repl: Repl, count: int, flags: int) -> tuple[str, int]:
    """`subn`, where `repl` may also be a Jinja macro (or any callable) taking the match.

    A macro's result is Markup under autoescape: it is kept as is, and the text between matches
    is escaped once when the pieces are joined. Without autoescape everything is plain `str`.
    """

    if not callable(repl):
        result: tuple[str, int] = engine.call(
            "subn", pattern, repl, value, count=count, flags=flags
        )

        return result

    parts: list[str] = []
    end = 0
    found = 0

    for found_match in engine.call("finditer", pattern, value, flags=flags):
        if count and found == count:
            break

        replacement = repl(found_match)

        parts += [
            value[end : found_match.start()],
            replacement if isinstance(replacement, Markup) else str(replacement),
        ]

        end = found_match.end()
        found += 1

    parts.append(value[end:])

    joined = Markup("").join(parts) if any(isinstance(p, Markup) for p in parts) else "".join(parts)

    return joined, found


@collection.filter(
    examples=[
        (r"{{ 'a1 b22' | re.sub('\\d+', '#') }}", {}, "a# b#"),
        (r"{{ 'a1 b22' | re.sub('(\\w)(\\d+)', '\\2\\1', 1) }}", {}, "1a b22"),
        (
            r"{{ '2026-11-22' | re.sub('(?P<y>\\d+)-(\\d+)-(\\d+)', '\\3/\\2/\\g<y>') }}",
            {},
            "22/11/2026",
        ),
        (MACRO + r"{{ 'a1 b2' | re.sub('[a-z]', up) }}", {}, "A1 B2"),
    ]
)
def sub(value: str, /, pattern: str, repl: Repl, count: int = 0, flags: int = 0) -> str:
    """Replace matches with `repl`: a string (`\\1`, `\\g<name>`) or a macro taking the match."""
    return substitute(value, pattern, repl, count, flags)[0]


@collection.filter(
    examples=[
        (r"{{ 'a1 b22' | re.subn('\\d', '#') | join('|') }}", {}, "a# b##|3"),
        (MACRO + r"{{ 'a1 b2' | re.subn('[a-z]', up, 1) | join('|') }}", {}, "A1 b2|1"),
    ]
)
def subn(
    value: str, /, pattern: str, repl: Repl, count: int = 0, flags: int = 0
) -> tuple[str, int]:
    """Like `re.sub`, but return `(new_string, number_of_substitutions)`."""
    return substitute(value, pattern, repl, count, flags)


@collection.filter(
    examples=[
        (r"{{ 'a, b,c' | re.split(',\\s*') | join('|') }}", {}, "a|b|c"),
        (r"{{ 'a, b,c' | re.split(',\\s*', 1) | join('|') }}", {}, "a|b,c"),
        (r"{{ 'aXbxc' | re.split('x', flags=re.I) | join('|') }}", {}, "a|b|c"),
    ]
)
def split(value: str, /, pattern: str, maxsplit: int = 0, flags: int = 0) -> list[str | None]:
    """Split the value by the matches of `pattern`. Groups in the pattern are kept."""
    return engine.call("split", pattern, value, maxsplit=maxsplit, flags=flags)


@collection.filter(examples=[(r"{{ 'a.b*c' | re.escape }}", {}, r"a\.b\*c")])
def escape(value: str, /) -> str:
    """Escape every regex special character in the value."""
    return re.escape(value)
