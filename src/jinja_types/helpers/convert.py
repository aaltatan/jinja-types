"""Plain-name helpers: `fmt` and the `to_*` converters.

Each converter also serves as its namespace's `parse` function (see `PARSERS`), which
`coerce=True` uses to turn a `str` into the namespace type.
"""

import re
from collections.abc import Callable
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from fractions import Fraction
from pathlib import PurePath
from uuid import UUID

from jinja_types.core import Collection

collection = Collection()

TRUE_STRINGS = frozenset({"true", "yes", "on", "1"})
FALSE_STRINGS = frozenset({"false", "no", "off", "0"})

# The output of str(timedelta): "[-]D day[s], H:MM:SS[.ffffff]".
TIMEDELTA_RE = re.compile(r"(?:(-?\d+) days?, )?(\d+):(\d{2}):(\d{2}(?:\.\d+)?)")


@collection.filter(
    examples=[
        ("{{ x | fmt(',.2f') }}", {"x": 1500.5}, "1,500.50"),
        ("{{ d | fmt('%d/%m/%Y') }}", {"d": date(2026, 1, 5)}, "05/01/2026"),
    ]
)
def fmt(value: object, /, spec: str = "") -> str:
    """Return `format(value, spec)`; works for numbers, Decimal and dates."""
    return format(value, spec)


@collection.filter(examples=[("{{ x | to_str }}", {"x": Decimal("1.50")}, "1.50")])
def to_str(value: object, /) -> str:
    """Return `str(value)`."""
    return str(value)


@collection.filter(
    examples=[
        ("{{ '42' | to_int + 1 }}", {}, "43"),
        ("{{ 'ff' | to_int(16) }}", {}, "255"),
        ("{{ 3.9 | to_int }}", {}, "3"),
    ]
)
def to_int(value: str | float | Decimal | Fraction, /, base: int = 10) -> int:
    """Convert to `int`. `base` applies to strings; numbers are truncated like `int()`."""
    return int(value, base) if isinstance(value, str) else int(value)


@collection.filter(examples=[("{{ '2.5' | to_float * 2 }}", {}, "5.0")])
def to_float(value: str | float | Decimal | Fraction, /) -> float:
    """Convert to `float`."""
    return float(value)


@collection.filter(
    test=False,
    examples=[
        ("{{ 'Yes' | to_bool }}", {}, "True"),
        ("{{ 'off' | to_bool }}", {}, "False"),
        ("{{ 1 | to_bool }}", {}, "True"),
    ],
)
def to_bool(value: str | int, /) -> bool:
    """Convert strictly: true/yes/on/1 or false/no/off/0 (any case), bools, and ints 0 or 1."""
    if isinstance(value, str):
        text = value.strip().lower()

        if text in TRUE_STRINGS:
            return True

        if text in FALSE_STRINGS:
            return False

        raise ValueError(f"cannot convert {value!r} to bool; use true/false, yes/no, on/off, 1/0")

    if isinstance(value, int) and value in (0, 1):
        return bool(value)

    raise ValueError(f"cannot convert {value!r} to bool; only 0 and 1 are accepted")


@collection.filter(
    examples=[
        ("{{ '1500.5' | to_decimal | fmt(',.2f') }}", {}, "1,500.50"),
        ("{{ 0.1 | to_decimal }}", {}, "0.1"),
    ]
)
def to_decimal(value: str | float | Decimal, /) -> Decimal:
    """Convert to `Decimal`. Floats go through `repr()`, so `0.1` gives `Decimal('0.1')`."""
    return Decimal(repr(value)) if isinstance(value, float) else Decimal(value)


@collection.filter(
    examples=[("{{ '3/4' | to_fraction + 1 }}", {}, "7/4"), ("{{ 0.5 | to_fraction }}", {}, "1/2")]
)
def to_fraction(value: str | float | Decimal | Fraction, /) -> Fraction:
    """Convert to `Fraction` (`'3/4'`, `'0.75'`, numbers)."""
    return Fraction(value)


@collection.filter(
    examples=[
        ("{{ '2026-01-05' | to_date | fmt('%A') }}", {}, "Monday"),
        ("{{ '05/01/2026' | to_date(format='%d/%m/%Y') | fmt('%A') }}", {}, "Monday"),
        ("{{ d | to_date }}", {"d": datetime(2026, 1, 5, 9, 30)}, "2026-01-05"),
    ]
)
def to_date(value: str | date, /, format: str | None = None) -> date:
    """Parse an ISO date, or use `format` with `strptime`. A datetime gives its date."""
    if isinstance(value, datetime):
        return value.date()

    if isinstance(value, date):
        return value

    if format is not None:
        return datetime.strptime(value, format).date()

    return date.fromisoformat(value)


@collection.filter(
    examples=[
        ("{{ '2026-01-05T09:30' | to_datetime | fmt('%H:%M') }}", {}, "09:30"),
        (
            "{{ '05/01/2026 9:30' | to_datetime(format='%d/%m/%Y %H:%M') }}",
            {},
            "2026-01-05 09:30:00",
        ),
        ("{{ d | to_datetime }}", {"d": date(2026, 1, 5)}, "2026-01-05 00:00:00"),
    ]
)
def to_datetime(value: str | date, /, format: str | None = None) -> datetime:
    """Parse an ISO datetime, or use `format` with `strptime`. A date becomes midnight."""
    if isinstance(value, datetime):
        return value

    if isinstance(value, date):
        return datetime.combine(value, time())

    if format is not None:
        return datetime.strptime(value, format)

    return datetime.fromisoformat(value)


@collection.filter(
    examples=[
        ("{{ '09:30' | to_time }}", {}, "09:30:00"),
        ("{{ '9.30 PM' | to_time(format='%I.%M %p') }}", {}, "21:30:00"),
        ("{{ d | to_time }}", {"d": datetime(2026, 1, 5, 9, 30)}, "09:30:00"),
    ]
)
def to_time(value: str | time | datetime, /, format: str | None = None) -> time:
    """Parse an ISO time, or use `format` with `strptime`. A datetime gives its time (with tz)."""
    if isinstance(value, datetime):
        return value.timetz()

    if isinstance(value, time):
        return value

    if format is not None:
        return datetime.strptime(value, format).time()

    return time.fromisoformat(value)


@collection.filter(
    examples=[
        ("{{ 90 | to_timedelta }}", {}, "0:01:30"),
        ("{{ 0 | to_timedelta(days=2, hours=3) }}", {}, "2 days, 3:00:00"),
        ("{{ '1 day, 2:30:00' | to_timedelta }}", {}, "1 day, 2:30:00"),
    ]
)
def to_timedelta(
    value: str | float | timedelta,
    /,
    *,
    days: float = 0,
    hours: float = 0,
    minutes: float = 0,
) -> timedelta:
    """Convert seconds (or `str(timedelta)` text) to a timedelta, plus `days`/`hours`/`minutes`."""
    extra = timedelta(days=days, hours=hours, minutes=minutes)

    if isinstance(value, timedelta):
        return value + extra

    if isinstance(value, str):
        match = TIMEDELTA_RE.fullmatch(value.strip())

        if match is None:
            return timedelta(seconds=float(value)) + extra

        day, hour, minute, second = match.groups()
        parsed = timedelta(
            days=int(day or 0), hours=int(hour), minutes=int(minute), seconds=float(second)
        )

        return parsed + extra

    return timedelta(seconds=value) + extra


@collection.filter(
    examples=[
        (
            "{{ '12345678-1234-5678-1234-567812345678' | to_uuid }}",
            {},
            "12345678-1234-5678-1234-567812345678",
        )
    ]
)
def to_uuid(value: str | UUID, /) -> UUID:
    """Convert to `UUID`."""
    return value if isinstance(value, UUID) else UUID(value)


@collection.filter(
    # path.as_posix: the platform's separator would make the generated docs differ per OS
    examples=[("{{ 'docs/readme.md' | to_path | path.as_posix }}", {}, "docs/readme.md")]
)
def to_path(value: str | PurePath, /) -> PurePath:
    """Convert to a `PurePath` (never touches the disk)."""
    return PurePath(value)


PARSERS: dict[str, Callable[[str], object]] = {
    "str": to_str,
    "int": to_int,
    "float": to_float,
    "bool": to_bool,
    "decimal": to_decimal,
    "fraction": to_fraction,
    "date": to_date,
    "datetime": to_datetime,
    "time": to_time,
    "timedelta": to_timedelta,
    "uuid": to_uuid,
    "path": to_path,
}
"""The `parse` function of each built-in namespace, used by `coerce=True`."""
