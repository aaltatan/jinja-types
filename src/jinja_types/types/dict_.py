"""The `dict` namespace. Mutating members work on a copy; the input is never changed.

`update` and `clear` return the new dict. `pop`, `popitem` and `setdefault` return what Python
returns (the item), computed on a copy.
"""

from collections.abc import ItemsView, Iterable, KeysView, Mapping, ValuesView
from typing import Any

from jinja_types.core import Collection

collection = Collection("dict", dict)

PRICES = {"prices": {"tea": 2, "coffee": 3}}
PAIRS = "| dict.items | map('join', '=') | join('|') }}"


@collection.filter(
    examples=[
        ("{{ prices | dict.get('tea') }}", PRICES, "2"),
        ("{{ prices | dict.get('milk', 0) }}", PRICES, "0"),
        ("{{ prices | dict.get('milk') }}", PRICES, "None"),
    ]
)
def get(value: dict[Any, Any], key: object, default: object = None, /) -> object:
    """Return the value for `key`, or `default`."""
    return value.get(key, default)


@collection.filter(examples=[("{{ prices | dict.keys | join('|') }}", PRICES, "tea|coffee")])
def keys(value: dict[Any, Any], /) -> KeysView[Any]:
    """Return a view of the keys."""
    return value.keys()


@collection.filter(examples=[("{{ prices | dict.values | sum }}", PRICES, "5")])
def values(value: dict[Any, Any], /) -> ValuesView[Any]:
    """Return a view of the values."""
    return value.values()


@collection.filter(examples=[("{{ prices " + PAIRS, PRICES, "tea=2|coffee=3")])
def items(value: dict[Any, Any], /) -> ItemsView[Any, Any]:
    """Return a view of the `(key, value)` pairs."""
    return value.items()


@collection.filter(examples=[("{{ prices | dict.copy " + PAIRS, PRICES, "tea=2|coffee=3")])
def copy(value: dict[Any, Any], /) -> dict[Any, Any]:
    """Return a shallow copy."""
    return value.copy()


@collection.classmethod(
    examples=[
        ("{{ ['a', 'b'] | dict.fromkeys(0) " + PAIRS, {}, "a=0|b=0"),
        ("{{ 'ab' | dict.fromkeys " + PAIRS, {}, "a=None|b=None"),
    ]
)
def fromkeys(value: Iterable[Any], v: object = None, /) -> dict[Any, Any]:
    """Return a dict with the piped keys, all set to `v` (classmethod; the keys are piped in)."""
    return dict.fromkeys(value, v)


@collection.filter(
    examples=[
        ("{{ prices | dict.update({'tea': 1}) " + PAIRS, PRICES, "tea=1|coffee=3"),
        ("{{ prices | dict.update([('milk', 1)], tea=4) " + PAIRS, PRICES, "tea=4|coffee=3|milk=1"),
    ]
)
def update(
    value: dict[Any, Any],
    other: Mapping[Any, Any] | Iterable[tuple[Any, Any]] = (),
    /,
    **kwargs: object,
) -> dict[Any, Any]:
    """Return a copy updated from `other` and keyword arguments."""
    result = value.copy()

    result.update(other, **kwargs)

    return result


@collection.filter(examples=[("{{ prices | dict.clear }}", PRICES, "{}")])
def clear(value: dict[Any, Any], /) -> dict[Any, Any]:
    """Return an empty dict."""
    return {}


@collection.filter(
    examples=[
        ("{{ prices | dict.pop('tea') }}", PRICES, "2"),
        ("{{ prices | dict.pop('milk', 0) }}", PRICES, "0"),
    ]
)
def pop(value: dict[Any, Any], key: object, /, *default: object) -> object:
    """Return the value for `key` (or `default`; raises without one). The input keeps it."""
    return value.copy().pop(key, *default)


@collection.filter(examples=[("{{ prices | dict.popitem | join('=') }}", PRICES, "coffee=3")])
def popitem(value: dict[Any, Any], /) -> tuple[Any, Any]:
    """Return the last `(key, value)` pair. The input keeps it."""
    return value.copy().popitem()


@collection.filter(
    examples=[
        ("{{ prices | dict.setdefault('tea', 9) }}", PRICES, "2"),
        ("{{ prices | dict.setdefault('milk', 9) }}", PRICES, "9"),
    ]
)
def setdefault(value: dict[Any, Any], key: object, default: object = None, /) -> object:
    """Return the value for `key`, or `default` if missing. The input is unchanged."""
    return value.copy().setdefault(key, default)
