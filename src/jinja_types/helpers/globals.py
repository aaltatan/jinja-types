"""Template globals: the `decimal` and `re` namespace objects, `today()` and `now()`.

Globals and filters are separate Jinja tables, so the global `decimal` and the filter
`decimal.quantize` coexist.
"""

import decimal as _decimal
import re as _re
from datetime import UTC, date, datetime, tzinfo
from typing import ClassVar

from jinja_types.core import Collection

collection = Collection()


class DecimalNamespace:
    """The `decimal` global: `Decimal`, `Context` and every `ROUND_*` constant."""

    Decimal: ClassVar = _decimal.Decimal
    Context: ClassVar = _decimal.Context
    ROUND_UP: ClassVar = _decimal.ROUND_UP
    ROUND_DOWN: ClassVar = _decimal.ROUND_DOWN
    ROUND_CEILING: ClassVar = _decimal.ROUND_CEILING
    ROUND_FLOOR: ClassVar = _decimal.ROUND_FLOOR
    ROUND_HALF_UP: ClassVar = _decimal.ROUND_HALF_UP
    ROUND_HALF_DOWN: ClassVar = _decimal.ROUND_HALF_DOWN
    ROUND_HALF_EVEN: ClassVar = _decimal.ROUND_HALF_EVEN
    ROUND_05UP: ClassVar = _decimal.ROUND_05UP

    def __repr__(self) -> str:
        return "<jinja_types decimal>"


class ReFlags:
    """The `re` global: regex flags only, short and long names."""

    NOFLAG: ClassVar = _re.NOFLAG
    A: ClassVar = _re.A
    ASCII: ClassVar = _re.ASCII
    I: ClassVar = _re.I  # noqa: E741 (the stdlib name)
    IGNORECASE: ClassVar = _re.IGNORECASE
    L: ClassVar = _re.L
    LOCALE: ClassVar = _re.LOCALE
    M: ClassVar = _re.M
    MULTILINE: ClassVar = _re.MULTILINE
    S: ClassVar = _re.S
    DOTALL: ClassVar = _re.DOTALL
    U: ClassVar = _re.U
    UNICODE: ClassVar = _re.UNICODE
    X: ClassVar = _re.X
    VERBOSE: ClassVar = _re.VERBOSE

    def __repr__(self) -> str:
        return "<jinja_types re flags>"


DECIMAL = DecimalNamespace()
RE_FLAGS = ReFlags()


@collection.global_(
    member="decimal",
    constant=True,
    examples=[
        ("{{ decimal.Decimal('1.10') }}", {}, "1.10"),
        ("{{ decimal.ROUND_HALF_UP }}", {}, "ROUND_HALF_UP"),
    ],
)
def decimal_namespace() -> DecimalNamespace:
    """The `decimal` namespace object."""
    return DECIMAL


@collection.global_(
    member="re",
    constant=True,
    examples=[("{{ re.I == 2 and re.IGNORECASE == re.I }}", {}, "True")],
)
def re_flags() -> ReFlags:
    """The `re` flags object."""
    return RE_FLAGS


@collection.global_(examples=[("{{ today().year > 2000 }}", {}, "True")])
def today() -> date:
    """Return today's local date."""
    return date.today()


@collection.global_(
    examples=[
        ("{{ now().tzinfo }}", {}, "None"),
        ("{{ now(tz).utcoffset() }}", {"tz": UTC}, "0:00:00"),
    ]
)
def now(tz: tzinfo | None = None) -> datetime:
    """Return the current datetime, local or in `tz` (a `tzinfo`)."""
    return datetime.now(tz)
