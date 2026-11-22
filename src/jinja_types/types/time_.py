"""The `time` namespace (`datetime.time`). Not exposed: the constants `min`, `max`, `resolution`."""

import datetime as dt
from typing import Literal

from jinja_types.core import Collection
from jinja_types.helpers import PARSERS

from .date_ import changes

collection = Collection("time", dt.time, parse=PARSERS["time"])

T = dt.time(14, 30, 5, 250)
PLUS3 = dt.time(12, 0, tzinfo=dt.timezone(dt.timedelta(hours=3)))


@collection.filter(examples=[("{{ x | time.strftime('%H.%M') }}", {"x": T}, "14.30")])
def strftime(value: dt.time, /, format: str) -> str:
    """Format the time with a `strftime` format string."""
    return value.strftime(format)


@collection.filter(
    examples=[
        ("{{ x | time.isoformat }}", {"x": T}, "14:30:05.000250"),
        ("{{ x | time.isoformat('minutes') }}", {"x": PLUS3}, "12:00+03:00"),
    ]
)
def isoformat(
    value: dt.time,
    /,
    timespec: Literal["auto", "hours", "minutes", "seconds", "milliseconds", "microseconds"] = (
        "auto"
    ),
) -> str:
    """Return the time in ISO 8601 format."""
    return value.isoformat(timespec)


@collection.filter(
    examples=[
        ("{{ x | time.replace(second=0, microsecond=0) }}", {"x": T}, "14:30:00"),
        ("{{ x | time.replace(tzinfo=none) }}", {"x": PLUS3}, "12:00:00"),
    ]
)
def replace(
    value: dt.time,
    /,
    hour: int | None = None,
    minute: int | None = None,
    second: int | None = None,
    microsecond: int | None = None,
    tzinfo: dt.tzinfo | Literal[True] | None = True,
    *,
    fold: int | None = None,
) -> dt.time:
    """Return the time with the given fields replaced. `tzinfo=none` makes it naive."""
    fields = changes(hour=hour, minute=minute, second=second, microsecond=microsecond, fold=fold)

    return value.replace(**fields, tzinfo=value.tzinfo if tzinfo is True else tzinfo)


@collection.filter(examples=[("{{ x | time.utcoffset }}", {"x": PLUS3}, "3:00:00")])
def utcoffset(value: dt.time, /) -> dt.timedelta | None:
    """Return the UTC offset, or None for a naive time."""
    return value.utcoffset()


@collection.filter(examples=[("{{ x | time.tzname }}", {"x": PLUS3}, "UTC+03:00")])
def tzname(value: dt.time, /) -> str | None:
    """Return the timezone name, or None for a naive time."""
    return value.tzname()


@collection.filter(examples=[("{{ x | time.dst }}", {"x": T}, "None")])
def dst(value: dt.time, /) -> dt.timedelta | None:
    """Return the daylight saving offset, or None if unknown."""
    return value.dst()


@collection.attribute(examples=[("{{ x | time.hour }}", {"x": T}, "14")])
def hour(value: dt.time, /) -> int:
    """The hour, 0 to 23."""
    return value.hour


@collection.attribute(examples=[("{{ x | time.minute }}", {"x": T}, "30")])
def minute(value: dt.time, /) -> int:
    """The minute."""
    return value.minute


@collection.attribute(examples=[("{{ x | time.second }}", {"x": T}, "5")])
def second(value: dt.time, /) -> int:
    """The second."""
    return value.second


@collection.attribute(examples=[("{{ x | time.microsecond }}", {"x": T}, "250")])
def microsecond(value: dt.time, /) -> int:
    """The microsecond."""
    return value.microsecond


@collection.attribute(examples=[("{{ x | time.tzinfo }}", {"x": PLUS3}, "UTC+03:00")])
def tzinfo(value: dt.time, /) -> dt.tzinfo | None:
    """The timezone, or None for a naive time."""
    return value.tzinfo


@collection.attribute(examples=[("{{ x | time.fold }}", {"x": T}, "0")])
def fold(value: dt.time, /) -> int:
    """0 or 1: which of two repeated wall times this is."""
    return value.fold


@collection.classmethod(examples=[("{{ '14:30' | time.fromisoformat }}", {}, "14:30:00")])
def fromisoformat(value: str, /) -> dt.time:
    """Parse an ISO time (classmethod; the string is piped in)."""
    return dt.time.fromisoformat(value)
