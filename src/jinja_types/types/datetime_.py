"""The `datetime` namespace: the members `datetime` adds to `date` or overrides.

Inherited members (`year`, `weekday`, `strftime`, …) are reached through `date.*`, which accepts
datetimes. Not exposed: the class constants `min`, `max`, `resolution`, `now` / `utcnow` (use the
`now()` global) and the deprecated `utcfromtimestamp`.

Timezone names: `datetime.astimezone` also accepts an IANA name such as `"Asia/Damascus"`, which is
turned into a `zoneinfo.ZoneInfo`. On Windows this needs the `tzdata` package.
"""

import datetime as dt
from time import struct_time
from typing import Literal
from zoneinfo import ZoneInfo

from jinja_types.core import Collection
from jinja_types.helpers import PARSERS

from .date_ import changes

collection = Collection("datetime", dt.datetime, parse=PARSERS["datetime"])

DT = dt.datetime(2026, 11, 22, 14, 30, 5, 250)
UTC_DT = dt.datetime(2026, 11, 22, 12, 0, tzinfo=dt.UTC)
PLUS3 = dt.datetime(2026, 11, 22, 12, 0, tzinfo=dt.timezone(dt.timedelta(hours=3)))


@collection.filter(
    examples=[
        (
            "{{ x | datetime.astimezone('Asia/Damascus') }}",
            {"x": UTC_DT},
            "2026-11-22 15:00:00+03:00",
        ),
        (
            "{{ x | datetime.astimezone(tz) }}",
            {"x": PLUS3, "tz": dt.UTC},
            "2026-11-22 09:00:00+00:00",
        ),
    ]
)
def astimezone(value: dt.datetime, /, tz: dt.tzinfo | str | None = None) -> dt.datetime:
    """Convert to the timezone `tz`: a `tzinfo`, an IANA name, or None for local time."""
    return value.astimezone(ZoneInfo(tz) if isinstance(tz, str) else tz)


@collection.filter(examples=[("{{ x | datetime.ctime }}", {"x": DT}, "Sun Nov 22 14:30:05 2026")])
def ctime(value: dt.datetime, /) -> str:
    """Return a `ctime()` style string."""
    return value.ctime()


@collection.filter(member="date", examples=[("{{ x | datetime.date }}", {"x": DT}, "2026-11-22")])
def date_(value: dt.datetime, /) -> dt.date:
    """Return the date part."""
    return value.date()


@collection.filter(
    member="time", examples=[("{{ x | datetime.time }}", {"x": DT}, "14:30:05.000250")]
)
def time_(value: dt.datetime, /) -> dt.time:
    """Return the time part, without the timezone."""
    return value.time()


@collection.filter(examples=[("{{ x | datetime.timetz }}", {"x": PLUS3}, "12:00:00+03:00")])
def timetz(value: dt.datetime, /) -> dt.time:
    """Return the time part, with the timezone."""
    return value.timetz()


@collection.filter(examples=[("{{ x | datetime.timestamp }}", {"x": UTC_DT}, "1795348800.0")])
def timestamp(value: dt.datetime, /) -> float:
    """Return the POSIX timestamp. Naive values are taken as local time."""
    return value.timestamp()


@collection.filter(
    examples=[
        ("{{ x | datetime.isoformat }}", {"x": DT}, "2026-11-22T14:30:05.000250"),
        ("{{ x | datetime.isoformat(' ', 'minutes') }}", {"x": DT}, "2026-11-22 14:30"),
        ("{{ x | date.isoformat(timespec='seconds') }}", {"x": PLUS3}, "2026-11-22T12:00:00+03:00"),
    ]
)
def isoformat(
    value: dt.datetime,
    /,
    sep: str = "T",
    timespec: Literal["auto", "hours", "minutes", "seconds", "milliseconds", "microseconds"] = (
        "auto"
    ),
) -> str:
    """Return the datetime in ISO 8601 format."""
    return value.isoformat(sep, timespec)


@collection.filter(
    examples=[
        ("{{ x | datetime.replace(hour=9, microsecond=0) }}", {"x": DT}, "2026-11-22 09:30:05"),
        ("{{ x | datetime.replace(tzinfo=none) }}", {"x": PLUS3}, "2026-11-22 12:00:00"),
    ]
)
def replace(
    value: dt.datetime,
    /,
    year: int | None = None,
    month: int | None = None,
    day: int | None = None,
    hour: int | None = None,
    minute: int | None = None,
    second: int | None = None,
    microsecond: int | None = None,
    tzinfo: dt.tzinfo | Literal[True] | None = True,
    *,
    fold: int | None = None,
) -> dt.datetime:
    """Return the datetime with the given fields replaced. `tzinfo=none` makes it naive."""
    fields = changes(
        year=year,
        month=month,
        day=day,
        hour=hour,
        minute=minute,
        second=second,
        microsecond=microsecond,
        fold=fold,
    )

    return value.replace(**fields, tzinfo=value.tzinfo if tzinfo is True else tzinfo)


@collection.filter(
    examples=[
        ("{{ x | datetime.timetuple | list }}", {"x": DT}, "[2026, 11, 22, 14, 30, 5, 6, 326, -1]")
    ]
)
def timetuple(value: dt.datetime, /) -> struct_time:
    """Return a `time.struct_time`."""
    return value.timetuple()


@collection.filter(
    examples=[
        (
            "{{ x | datetime.utctimetuple | list }}",
            {"x": PLUS3},
            "[2026, 11, 22, 9, 0, 0, 6, 326, 0]",
        )
    ]
)
def utctimetuple(value: dt.datetime, /) -> struct_time:
    """Return a `time.struct_time` in UTC."""
    return value.utctimetuple()


@collection.filter(
    examples=[
        ("{{ x | datetime.utcoffset }}", {"x": PLUS3}, "3:00:00"),
        ("{{ x | datetime.utcoffset }}", {"x": DT}, "None"),
    ]
)
def utcoffset(value: dt.datetime, /) -> dt.timedelta | None:
    """Return the UTC offset, or None for a naive datetime."""
    return value.utcoffset()


@collection.filter(examples=[("{{ x | datetime.tzname }}", {"x": PLUS3}, "UTC+03:00")])
def tzname(value: dt.datetime, /) -> str | None:
    """Return the timezone name, or None for a naive datetime."""
    return value.tzname()


@collection.filter(examples=[("{{ x | datetime.dst }}", {"x": PLUS3}, "None")])
def dst(value: dt.datetime, /) -> dt.timedelta | None:
    """Return the daylight saving offset, or None if unknown."""
    return value.dst()


@collection.attribute(examples=[("{{ x | datetime.hour }}", {"x": DT}, "14")])
def hour(value: dt.datetime, /) -> int:
    """The hour, 0 to 23."""
    return value.hour


@collection.attribute(examples=[("{{ x | datetime.minute }}", {"x": DT}, "30")])
def minute(value: dt.datetime, /) -> int:
    """The minute."""
    return value.minute


@collection.attribute(examples=[("{{ x | datetime.second }}", {"x": DT}, "5")])
def second(value: dt.datetime, /) -> int:
    """The second."""
    return value.second


@collection.attribute(examples=[("{{ x | datetime.microsecond }}", {"x": DT}, "250")])
def microsecond(value: dt.datetime, /) -> int:
    """The microsecond."""
    return value.microsecond


@collection.attribute(examples=[("{{ x | datetime.tzinfo }}", {"x": UTC_DT}, "UTC")])
def tzinfo(value: dt.datetime, /) -> dt.tzinfo | None:
    """The timezone, or None for a naive datetime."""
    return value.tzinfo


@collection.attribute(examples=[("{{ x | datetime.fold }}", {"x": DT}, "0")])
def fold(value: dt.datetime, /) -> int:
    """0 or 1: which of two repeated wall times this is."""
    return value.fold


@collection.classmethod(
    examples=[
        (
            "{{ '22/11/2026 14:30' | datetime.strptime('%d/%m/%Y %H:%M') }}",
            {},
            "2026-11-22 14:30:00",
        )
    ]
)
def strptime(value: str, format: str, /) -> dt.datetime:
    """Parse a string with a `strptime` format (classmethod; the string is piped in)."""
    return dt.datetime.strptime(value, format)


@collection.classmethod(
    examples=[
        ("{{ '2026-11-22T14:30' | datetime.fromisoformat }}", {}, "2026-11-22 14:30:00"),
        ("{{ '2026-11-22T14:30Z' | datetime.fromisoformat }}", {}, "2026-11-22 14:30:00+00:00"),
    ]
)
def fromisoformat(value: str, /) -> dt.datetime:
    """Parse an ISO datetime (classmethod; the string is piped in)."""
    return dt.datetime.fromisoformat(value)


@collection.classmethod(
    examples=[("{{ 0 | datetime.fromtimestamp(tz) }}", {"tz": dt.UTC}, "1970-01-01 00:00:00+00:00")]
)
def fromtimestamp(value: float, /, tz: dt.tzinfo | None = None) -> dt.datetime:
    """Return the datetime for a POSIX timestamp (classmethod; the timestamp is piped in)."""
    return dt.datetime.fromtimestamp(value, tz)


@collection.classmethod(
    examples=[
        (
            "{{ d | datetime.combine(t) }}",
            {"d": DT.date(), "t": DT.time()},
            "2026-11-22 14:30:05.000250",
        ),
        (
            "{{ d | datetime.combine(t, tz) }}",
            {"d": DT.date(), "t": dt.time(9), "tz": dt.UTC},
            "2026-11-22 09:00:00+00:00",
        ),
    ]
)
def combine(
    value: dt.date, time: dt.time, /, tzinfo: dt.tzinfo | Literal[True] | None = True
) -> dt.datetime:
    """Join a date and a time (classmethod; the date is piped in)."""
    return dt.datetime.combine(value, time, time.tzinfo if tzinfo is True else tzinfo)
