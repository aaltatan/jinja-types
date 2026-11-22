"""A tiny demo collection set used to exercise the core (not real built-in types)."""

from datetime import date, datetime

from jinja_types import Collection, Registry

DAY = date(2026, 1, 5)
MOMENT = datetime(2026, 1, 5, 9, 30)

date_ns = Collection("date", date, parse=date.fromisoformat)


@date_ns.filter(examples=[("{{ d | date.strftime('%Y/%m') }}", {"d": DAY}, "2026/01")])
def strftime(value: date, format: str, /) -> str:
    """Return the date formatted with `format`."""
    return value.strftime(format)


@date_ns.attribute(examples=[("{{ d | date.year }}", {"d": DAY}, "2026")])
def year(value: date, /) -> int:
    """The year."""
    return value.year


datetime_ns = Collection("datetime", datetime, parse=datetime.fromisoformat)


@datetime_ns.attribute(examples=[("{{ d | datetime.hour }}", {"d": MOMENT}, "9")])
def hour(value: datetime, /) -> int:
    """The hour."""
    return value.hour


list_ns = Collection("list", list)


@list_ns.filter(examples=[("{{ xs | list.append(3) }}", {"xs": [1, 2]}, "[1, 2, 3]")])
def append(value: list[object], object: object, /) -> list[object]:
    """Return a copy of the list with `object` appended."""
    return [*value, object]


helpers = Collection()


@helpers.filter(examples=[("{{ 'hi' | shout }}", {}, "HI!")])
def shout(value: str, /) -> str:
    """Upper-case the value and add an exclamation mark."""
    return value.upper() + "!"


@helpers.filter(examples=[("{{ 4 | is_even }}", {}, "True"), ("{{ 3 is is_even }}", {}, "False")])
def is_even(value: int, /) -> bool:
    """Return True if the value is even."""
    return value % 2 == 0


@helpers.global_(examples=[("{{ answer() }}", {}, "42")])
def answer() -> int:
    """Return 42."""
    return 42


collections = [date_ns, datetime_ns, list_ns, helpers]
bad_plugin = [date_ns, "not a collection"]


def demo_registry() -> Registry:
    """The default registry plus the demo collections."""
    return Registry.default().include(*collections)
