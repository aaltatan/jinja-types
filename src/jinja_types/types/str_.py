"""The `str` namespace: every public `str` method except the static `maketrans`."""

from collections.abc import Callable, Iterable, Mapping

from jinja2.sandbox import ImmutableSandboxedEnvironment

from jinja_types.core import Collection
from jinja_types.helpers import PARSERS

collection = Collection("str", str, parse=PARSERS["str"])

# str.format can reach attributes ("{0.__class__}"), so it always goes through Jinja's
# sandboxed formatter, even in a non-sandboxed environment.
SANDBOX = ImmutableSandboxedEnvironment()


def sandboxed(method: Callable[..., str]) -> Callable[..., str]:
    wrapped = SANDBOX.wrap_str_format(method)

    assert wrapped is not None  # always a str.format / str.format_map bound method

    return wrapped


# --- case ------------------------------------------------------------------------------------


@collection.filter(examples=[("{{ 'hello world' | str.capitalize }}", {}, "Hello world")])
def capitalize(value: str, /) -> str:
    """Return a copy with the first character upper-cased and the rest lower-cased."""
    return value.capitalize()


@collection.filter(examples=[("{{ 'Straße' | str.casefold }}", {}, "strasse")])
def casefold(value: str, /) -> str:
    """Return a casefolded copy, for caseless comparisons."""
    return value.casefold()


@collection.filter(examples=[("{{ 'ABC' | str.lower }}", {}, "abc")])
def lower(value: str, /) -> str:
    """Return a lower-cased copy."""
    return value.lower()


@collection.filter(examples=[("{{ 'abc' | str.upper }}", {}, "ABC")])
def upper(value: str, /) -> str:
    """Return an upper-cased copy."""
    return value.upper()


@collection.filter(examples=[("{{ 'aBc' | str.swapcase }}", {}, "AbC")])
def swapcase(value: str, /) -> str:
    """Return a copy with upper case and lower case swapped."""
    return value.swapcase()


@collection.filter(examples=[("{{ 'hello world' | str.title }}", {}, "Hello World")])
def title(value: str, /) -> str:
    """Return a title-cased copy."""
    return value.title()


# --- align and pad ---------------------------------------------------------------------------


@collection.filter(examples=[("{{ 'ab' | str.center(6, '*') }}", {}, "**ab**")])
def center(value: str, width: int, fillchar: str = " ", /) -> str:
    """Return the string centered in a field of `width`."""
    return value.center(width, fillchar)


@collection.filter(examples=[("{{ 'ab' | str.ljust(4, '.') }}", {}, "ab..")])
def ljust(value: str, width: int, fillchar: str = " ", /) -> str:
    """Return the string left-justified in a field of `width`."""
    return value.ljust(width, fillchar)


@collection.filter(examples=[("{{ '42' | str.rjust(5, '0') }}", {}, "00042")])
def rjust(value: str, width: int, fillchar: str = " ", /) -> str:
    """Return the string right-justified in a field of `width`."""
    return value.rjust(width, fillchar)


@collection.filter(
    examples=[
        ("{{ '42' | str.zfill(5) }}", {}, "00042"),
        ("{{ '-42' | str.zfill(5) }}", {}, "-0042"),
    ]
)
def zfill(value: str, width: int, /) -> str:
    """Pad a numeric string with zeros on the left, after any sign."""
    return value.zfill(width)


@collection.filter(examples=[("{{ 'a\\tb' | str.expandtabs(4) }}", {}, "a   b")])
def expandtabs(value: str, /, tabsize: int = 8) -> str:
    """Return a copy with tabs expanded to spaces."""
    return value.expandtabs(tabsize)


# --- strip -----------------------------------------------------------------------------------


@collection.filter(
    examples=[
        ("{{ '  ab  ' | str.strip ~ '|' }}", {}, "ab|"),
        ("{{ '--ab--' | str.strip('-') }}", {}, "ab"),
    ]
)
def strip(value: str, chars: str | None = None, /) -> str:
    """Return a copy with leading and trailing `chars` (default whitespace) removed."""
    return value.strip(chars)


@collection.filter(
    examples=[("{{ '  ab' | str.lstrip }}", {}, "ab"), ("{{ 'xxab' | str.lstrip('x') }}", {}, "ab")]
)
def lstrip(value: str, chars: str | None = None, /) -> str:
    """Return a copy with leading `chars` (default whitespace) removed."""
    return value.lstrip(chars)


@collection.filter(examples=[("{{ 'ab  ' | str.rstrip ~ '|' }}", {}, "ab|")])
def rstrip(value: str, chars: str | None = None, /) -> str:
    """Return a copy with trailing `chars` (default whitespace) removed."""
    return value.rstrip(chars)


@collection.filter(examples=[("{{ 'INV-001' | str.removeprefix('INV-') }}", {}, "001")])
def removeprefix(value: str, prefix: str, /) -> str:
    """Return a copy without `prefix`, if it starts with it."""
    return value.removeprefix(prefix)


@collection.filter(examples=[("{{ 'report.pdf' | str.removesuffix('.pdf') }}", {}, "report")])
def removesuffix(value: str, suffix: str, /) -> str:
    """Return a copy without `suffix`, if it ends with it."""
    return value.removesuffix(suffix)


# --- split and partition ---------------------------------------------------------------------


@collection.filter(
    examples=[
        ("{{ 'a,b,c' | str.split(',') | join('|') }}", {}, "a|b|c"),
        ("{{ ' a  b ' | str.split | join('|') }}", {}, "a|b"),
        ("{{ 'a b c' | str.split(maxsplit=1) | join('|') }}", {}, "a|b c"),
    ]
)
def split(value: str, /, sep: str | None = None, maxsplit: int = -1) -> list[str]:
    """Split on `sep` (default runs of whitespace), at most `maxsplit` times."""
    return value.split(sep, maxsplit)


@collection.filter(
    examples=[
        ("{{ 'a,b,c' | str.rsplit(',', 1) | join('|') }}", {}, "a,b|c"),
        ("{{ 'a b c' | str.rsplit(maxsplit=1) | join('|') }}", {}, "a b|c"),
    ]
)
def rsplit(value: str, /, sep: str | None = None, maxsplit: int = -1) -> list[str]:
    """Split from the right on `sep`, at most `maxsplit` times."""
    return value.rsplit(sep, maxsplit)


@collection.filter(
    examples=[
        ("{{ text | str.splitlines | join('|') }}", {"text": "one\ntwo"}, "one|two"),
        ("{{ text | str.splitlines(keepends=True) | length }}", {"text": "a\nb"}, "2"),
    ]
)
def splitlines(value: str, /, keepends: bool = False) -> list[str]:
    """Split at line boundaries."""
    return value.splitlines(keepends)


@collection.filter(
    examples=[("{{ 'key=value' | str.partition('=') | join('|') }}", {}, "key|=|value")]
)
def partition(value: str, sep: str, /) -> tuple[str, str, str]:
    """Split at the first `sep`: `(head, sep, tail)`."""
    return value.partition(sep)


@collection.filter(examples=[("{{ 'a.b.c' | str.rpartition('.') | join('|') }}", {}, "a.b|.|c")])
def rpartition(value: str, sep: str, /) -> tuple[str, str, str]:
    """Split at the last `sep`: `(head, sep, tail)`."""
    return value.rpartition(sep)


@collection.filter(
    examples=[
        ("{{ ', ' | str.join(items) }}", {"items": ["a", "b"]}, "a, b"),
        ("{{ '-' | str.join('abc') }}", {}, "a-b-c"),
    ]
)
def join(value: str, iterable: Iterable[str], /) -> str:
    """Join the strings in `iterable` with the value as separator (`sep | str.join(items)`)."""
    return value.join(iterable)


# --- search ----------------------------------------------------------------------------------


@collection.filter(
    examples=[
        ("{{ 'banana' | str.find('n') }}", {}, "2"),
        ("{{ 'banana' | str.find('x') }}", {}, "-1"),
    ]
)
def find(value: str, sub: str, start: int | None = None, end: int | None = None, /) -> int:
    """Return the lowest index of `sub`, or -1."""
    return value.find(sub, start, end)


@collection.filter(examples=[("{{ 'banana' | str.rfind('a') }}", {}, "5")])
def rfind(value: str, sub: str, start: int | None = None, end: int | None = None, /) -> int:
    """Return the highest index of `sub`, or -1."""
    return value.rfind(sub, start, end)


@collection.filter(examples=[("{{ 'banana' | str.index('n', 3) }}", {}, "4")])
def index(value: str, sub: str, start: int | None = None, end: int | None = None, /) -> int:
    """Like `find`, but raise when `sub` is not found."""
    return value.index(sub, start, end)


@collection.filter(examples=[("{{ 'banana' | str.rindex('n') }}", {}, "4")])
def rindex(value: str, sub: str, start: int | None = None, end: int | None = None, /) -> int:
    """Like `rfind`, but raise when `sub` is not found."""
    return value.rindex(sub, start, end)


@collection.filter(
    examples=[
        ("{{ 'banana' | str.count('a') }}", {}, "3"),
        ("{{ 'banana' | str.count('a', 2) }}", {}, "2"),
    ]
)
def count(value: str, sub: str, start: int | None = None, end: int | None = None, /) -> int:
    """Return the number of non-overlapping occurrences of `sub`."""
    return value.count(sub, start, end)


@collection.filter(
    examples=[
        ("{{ 'INV-001' | str.startswith('INV') }}", {}, "True"),
        ("{% if 'INV-001' is str.startswith(('INV', 'CR')) %}yes{% endif %}", {}, "yes"),
    ]
)
def startswith(
    value: str, prefix: str | tuple[str, ...], start: int | None = None, end: int | None = None, /
) -> bool:
    """Return True if the string starts with `prefix` (or any prefix in a tuple)."""
    return value.startswith(prefix, start, end)


@collection.filter(
    examples=[
        ("{{ 'report.pdf' | str.endswith('.pdf') }}", {}, "True"),
        ("{{ 'a.txt' is str.endswith(('.pdf', '.txt')) }}", {}, "True"),
    ]
)
def endswith(
    value: str, suffix: str | tuple[str, ...], start: int | None = None, end: int | None = None, /
) -> bool:
    """Return True if the string ends with `suffix` (or any suffix in a tuple)."""
    return value.endswith(suffix, start, end)


# --- replace, format, translate, encode ------------------------------------------------------


@collection.filter(
    examples=[
        ("{{ 'a-b-c' | str.replace('-', '/') }}", {}, "a/b/c"),
        ("{{ 'a-b-c' | str.replace('-', '/', 1) }}", {}, "a/b-c"),
    ]
)
def replace(value: str, old: str, new: str, /, count: int = -1) -> str:
    """Return a copy with `old` replaced by `new` (at most `count` times)."""
    return value.replace(old, new, count)


@collection.filter(
    member="format",
    examples=[
        ("{{ '{} has {:,} items' | str.format('Cart', 1500) }}", {}, "Cart has 1,500 items"),
        ("{{ 'Hi {name}' | str.format(name='Sam') }}", {}, "Hi Sam"),
    ],
)
def format_(value: str, /, *args: object, **kwargs: object) -> str:
    """Format the string with `str.format` (sandboxed: no unsafe attribute access)."""
    return sandboxed(value.format)(*args, **kwargs)


@collection.filter(examples=[("{{ '{a}-{b}' | str.format_map({'a': 1, 'b': 2}) }}", {}, "1-2")])
def format_map(value: str, mapping: Mapping[str, object], /) -> str:
    """Format the string with values from `mapping` (sandboxed)."""
    return sandboxed(value.format_map)(mapping)


@collection.filter(examples=[("{{ 'abc' | str.translate({97: 'A', 98: none}) }}", {}, "Ac")])
def translate(value: str, table: Mapping[int, str | int | None], /) -> str:
    """Map characters through `table` (code point → string, code point or None to delete)."""
    return value.translate(table)


@collection.filter(
    examples=[
        ("{{ 'é' | str.encode | length }}", {}, "2"),
        ("{{ 'é' | str.encode('ascii', errors='replace') | length }}", {}, "1"),
    ]
)
def encode(value: str, /, encoding: str = "utf-8", errors: str = "strict") -> bytes:
    """Encode to bytes."""
    return value.encode(encoding, errors)


# --- predicates (filters and tests) ----------------------------------------------------------


@collection.filter(
    examples=[
        ("{{ 'abc123' | str.isalnum }}", {}, "True"),
        ("{{ 'a b' is str.isalnum }}", {}, "False"),
    ]
)
def isalnum(value: str, /) -> bool:
    """Return True if all characters are alphanumeric."""
    return value.isalnum()


@collection.filter(examples=[("{{ 'abc' | str.isalpha }}", {}, "True")])
def isalpha(value: str, /) -> bool:
    """Return True if all characters are alphabetic."""
    return value.isalpha()


@collection.filter(
    examples=[("{{ 'abc' | str.isascii }}", {}, "True"), ("{{ 'é' is str.isascii }}", {}, "False")]
)
def isascii(value: str, /) -> bool:
    """Return True if all characters are ASCII."""
    return value.isascii()


@collection.filter(examples=[("{{ '123' | str.isdecimal }}", {}, "True")])
def isdecimal(value: str, /) -> bool:
    """Return True if all characters are decimal characters."""
    return value.isdecimal()


@collection.filter(
    examples=[
        ("{{ '²' | str.isdigit }}", {}, "True"),
        ("{% if code is str.isdigit %}ok{% endif %}", {"code": "2026"}, "ok"),
    ]
)
def isdigit(value: str, /) -> bool:
    """Return True if all characters are digits."""
    return value.isdigit()


@collection.filter(examples=[("{{ 'my_var' | str.isidentifier }}", {}, "True")])
def isidentifier(value: str, /) -> bool:
    """Return True if the string is a valid Python identifier."""
    return value.isidentifier()


@collection.filter(examples=[("{{ 'abc' | str.islower }}", {}, "True")])
def islower(value: str, /) -> bool:
    """Return True if all cased characters are lower case."""
    return value.islower()


@collection.filter(examples=[("{{ '½' | str.isnumeric }}", {}, "True")])
def isnumeric(value: str, /) -> bool:
    """Return True if all characters are numeric."""
    return value.isnumeric()


@collection.filter(examples=[("{{ text | str.isprintable }}", {"text": "a\nb"}, "False")])
def isprintable(value: str, /) -> bool:
    """Return True if all characters are printable."""
    return value.isprintable()


@collection.filter(examples=[("{{ '  ' | str.isspace }}", {}, "True")])
def isspace(value: str, /) -> bool:
    """Return True if all characters are whitespace."""
    return value.isspace()


@collection.filter(examples=[("{{ 'Hello World' | str.istitle }}", {}, "True")])
def istitle(value: str, /) -> bool:
    """Return True if the string is title-cased."""
    return value.istitle()


@collection.filter(examples=[("{{ 'ABC' | str.isupper }}", {}, "True")])
def isupper(value: str, /) -> bool:
    """Return True if all cased characters are upper case."""
    return value.isupper()
