"""The `list` namespace. Mutating members work on a copy and return it; the input is never changed.

`list.sort(key=...)` takes a Jinja macro (called with each item), or an attribute name such as
`"name"` or `"address.city"`, looked up like Jinja's `sort(attribute=...)` filter.
"""

import sys
from collections.abc import Callable, Iterable
from typing import Any, SupportsIndex

from jinja2.filters import make_attrgetter

from jinja_types.core import Collection

from .str_ import SANDBOX

collection = Collection("list", list)

XS = {"xs": [3, 1, 2]}
PEOPLE = {"people": [{"name": "Sara", "age": 31}, {"name": "Adam", "age": 25}]}

type Key = str | Callable[[Any], object] | None


def sort_key(key: Key) -> Callable[[Any], object] | None:
    """Turn an attribute name into a getter; macros and None pass through."""

    if isinstance(key, str):
        return make_attrgetter(SANDBOX, key)

    return key


@collection.filter(
    examples=[
        ("{{ xs | list.index(2) }}", XS, "2"),
        ("{{ [1, 2, 1] | list.index(1, 1) }}", {}, "2"),
    ]
)
def index(
    value: list[Any], x: object, start: SupportsIndex = 0, stop: SupportsIndex = sys.maxsize, /
) -> int:
    """Return the position of the first `x` (between `start` and `stop`)."""
    return value.index(x, start, stop)


@collection.filter(examples=[("{{ [1, 2, 2] | list.count(2) }}", {}, "2")])
def count(value: list[Any], x: object, /) -> int:
    """Return how many items equal `x`."""
    return value.count(x)


@collection.filter(examples=[("{{ xs | list.copy }}", XS, "[3, 1, 2]")])
def copy(value: list[Any], /) -> list[Any]:
    """Return a shallow copy."""
    return value.copy()


@collection.filter(examples=[("{{ xs | list.append(4) }}", XS, "[3, 1, 2, 4]")])
def append(value: list[Any], x: object, /) -> list[Any]:
    """Return a copy with `x` added at the end."""
    return [*value, x]


@collection.filter(examples=[("{{ xs | list.extend([4, 5]) }}", XS, "[3, 1, 2, 4, 5]")])
def extend(value: list[Any], iterable: Iterable[Any], /) -> list[Any]:
    """Return a copy with the items of `iterable` added at the end."""
    return [*value, *iterable]


@collection.filter(
    examples=[
        ("{{ xs | list.insert(0, 9) }}", XS, "[9, 3, 1, 2]"),
        ("{{ xs | list.insert(-1, 9) }}", XS, "[3, 1, 9, 2]"),
    ]
)
def insert(value: list[Any], index: SupportsIndex, x: object, /) -> list[Any]:
    """Return a copy with `x` inserted before `index`."""
    result = value.copy()

    result.insert(index, x)

    return result


@collection.filter(examples=[("{{ [1, 2, 1] | list.remove(1) }}", {}, "[2, 1]")])
def remove(value: list[Any], x: object, /) -> list[Any]:
    """Return a copy without the first `x`. Raises if `x` is missing."""
    result = value.copy()

    result.remove(x)

    return result


@collection.filter(examples=[("{{ xs | list.reverse }}", XS, "[2, 1, 3]")])
def reverse(value: list[Any], /) -> list[Any]:
    """Return a reversed copy."""
    return value[::-1]


@collection.filter(
    examples=[
        ("{{ xs | list.sort }}", XS, "[1, 2, 3]"),
        ("{{ xs | list.sort(reverse=true) }}", XS, "[3, 2, 1]"),
        (
            "{{ people | list.sort(key='name') | map(attribute='age') | join('|') }}",
            PEOPLE,
            "25|31",
        ),
        (
            "{% macro age(p) %}{{ p.age }}{% endmacro %}"
            "{{ people | list.sort(key=age) | map(attribute='name') | join('|') }}",
            PEOPLE,
            "Adam|Sara",
        ),
    ]
)
def sort(value: list[Any], /, *, key: Key = None, reverse: bool = False) -> list[Any]:
    """Return a sorted copy. `key` is a macro or an attribute name (a macro's result is text)."""
    return sorted(value, key=sort_key(key), reverse=reverse)  # type: ignore[arg-type]


@collection.filter(examples=[("{{ xs | list.clear }}", XS, "[]")])
def clear(value: list[Any], /) -> list[Any]:
    """Return an empty list."""
    return []


@collection.filter(
    examples=[
        ("{{ xs | list.pop }}", XS, "2"),
        ("{{ xs | list.pop(0) }}", XS, "3"),
    ]
)
def pop(value: list[Any], index: SupportsIndex = -1, /) -> object:
    """Return the item at `index` (the last by default). The input keeps it."""
    return value.copy().pop(index)
