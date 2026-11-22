"""The `date` namespace. `datetime` values dispatch to the `datetime` members it overrides.

Not exposed: the class constants `min`, `max`, `resolution`, and `today` (use the `today()`
global).
"""

from datetime import date, datetime
from time import struct_time

from jinja_types.core import Collection
from jinja_types.helpers import PARSERS

collection = Collection("date", date, parse=PARSERS["date"])

D = date(2026, 11, 22)
DT = datetime(2026, 11, 22, 14, 30, 5)


def changes(**fields: int | None) -> dict[str, int]:
    """Keep the fields that were given, so `replace` leaves the others unchanged."""
    return {name: value for name, value in fields.items() if value is not None}


@collection.filter(
    examples=[
        ("{{ x | date.strftime('%d/%m/%Y') }}", {"x": D}, "22/11/2026"),
        ("{{ x | date.strftime('%H:%M') }}", {"x": DT}, "14:30"),
    ]
)
def strftime(value: date, /, format: str) -> str:
    """Format the date with a `strftime` format string."""
    return value.strftime(format)


@collection.filter(
    examples=[
        ("{{ x | date.isoformat }}", {"x": D}, "2026-11-22"),
        ("{{ x | date.isoformat }}", {"x": DT}, "2026-11-22T14:30:05"),
    ]
)
def isoformat(value: date, /) -> str:
    """Return the date as `YYYY-MM-DD`."""
    return value.isoformat()


@collection.filter(examples=[("{{ x | date.isocalendar | join('-') }}", {"x": D}, "2026-47-7")])
def isocalendar(value: date, /) -> tuple[int, int, int]:
    """Return `(year, week, weekday)` of the ISO calendar."""
    return value.isocalendar()


@collection.filter(examples=[("{{ x | date.isoweekday }}", {"x": D}, "7")])
def isoweekday(value: date, /) -> int:
    """Return the day of the week, Monday is 1 and Sunday is 7."""
    return value.isoweekday()


@collection.filter(examples=[("{{ x | date.weekday }}", {"x": D}, "6")])
def weekday(value: date, /) -> int:
    """Return the day of the week, Monday is 0 and Sunday is 6."""
    return value.weekday()


@collection.filter(examples=[("{{ x | date.toordinal }}", {"x": D}, "739942")])
def toordinal(value: date, /) -> int:
    """Return the proleptic Gregorian ordinal, where 0001-01-01 is 1."""
    return value.toordinal()


@collection.filter(
    examples=[("{{ x | date.timetuple | list }}", {"x": D}, "[2026, 11, 22, 0, 0, 0, 6, 326, -1]")]
)
def timetuple(value: date, /) -> struct_time:
    """Return a `time.struct_time`."""
    return value.timetuple()


@collection.filter(examples=[("{{ x | date.ctime }}", {"x": D}, "Sun Nov 22 00:00:00 2026")])
def ctime(value: date, /) -> str:
    """Return a `ctime()` style string."""
    return value.ctime()


@collection.filter(
    examples=[
        ("{{ x | date.replace(day=1) }}", {"x": D}, "2026-11-01"),
        ("{{ x | date.replace(2027, 1) }}", {"x": D}, "2027-01-22"),
        ("{{ x | date.replace(hour=9) }}", {"x": DT}, "2026-11-22 09:30:05"),
    ]
)
def replace(
    value: date, /, year: int | None = None, month: int | None = None, day: int | None = None
) -> date:
    """Return the date with the given fields replaced."""
    return value.replace(**changes(year=year, month=month, day=day))


@collection.attribute(examples=[("{{ x | date.year }}", {"x": D}, "2026")])
def year(value: date, /) -> int:
    """The year."""
    return value.year


@collection.attribute(examples=[("{{ x | date.month }}", {"x": D}, "11")])
def month(value: date, /) -> int:
    """The month, 1 to 12."""
    return value.month


@collection.attribute(examples=[("{{ x | date.day }}", {"x": D}, "22")])
def day(value: date, /) -> int:
    """The day of the month."""
    return value.day


@collection.classmethod(examples=[("{{ '2026-11-22' | date.fromisoformat }}", {}, "2026-11-22")])
def fromisoformat(value: str, /) -> date:
    """Parse an ISO date (classmethod; the string is piped in)."""
    return date.fromisoformat(value)


@collection.classmethod(examples=[("{{ 739942 | date.fromordinal }}", {}, "2026-11-22")])
def fromordinal(value: int, /) -> date:
    """Return the date for a proleptic Gregorian ordinal (classmethod; the ordinal is piped in)."""
    return date.fromordinal(value)


@collection.classmethod(examples=[("{{ 2026 | date.fromisocalendar(47, 7) }}", {}, "2026-11-22")])
def fromisocalendar(value: int, week: int, day: int, /) -> date:
    """Return the date for an ISO year, week and weekday (classmethod; the year is piped in)."""
    return date.fromisocalendar(value, week, day)


@collection.classmethod(examples=[("{{ 100000 | date.fromtimestamp | date.year }}", {}, "1970")])
def fromtimestamp(value: float, /) -> date:
    """Return the local date for a POSIX timestamp (classmethod; the timestamp is piped in)."""
    return date.fromtimestamp(value)
