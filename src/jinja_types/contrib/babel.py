"""The `babel` namespace: locale-aware number, currency and date formatting (`[babel]` extra).

The locale is the `locale` argument, else the install's `Options.locale`, else `en_US` (so a
render never depends on the machine's environment). `numbering_system="default"` uses the
locale's own separators, e.g. `٬` and `٫` for `ar_SY`; Babel keeps Latin digits either way.

`Registry.default()` includes this collection only when Babel is importable.
"""

from datetime import date, datetime, time, timedelta, tzinfo
from decimal import Decimal
from typing import Literal

from jinja_types.core import CURRENT, Collection

try:
    from babel import dates, numbers
except ImportError as exc:  # pragma: no cover (the extra is installed in development)
    raise ImportError(
        "jinja_types.contrib.babel needs Babel: install 'jinja-types[babel]'"
    ) from exc

collection = Collection("babel", object)

DEFAULT_LOCALE = "en_US"

type Number = Decimal | float | int
type Width = Literal["full", "long", "medium", "short"] | str

X = {"x": Decimal("1234.5")}
D = {"d": date(2026, 11, 22)}
DT = {"dt": datetime(2026, 11, 22, 14, 30)}


def locale_of(locale: str | None) -> str:
    """The call's locale, else the install's, else `en_US`."""
    return locale or CURRENT.get().locale or DEFAULT_LOCALE


def zone(tz: tzinfo | str | None) -> tzinfo | None:
    """Turn an IANA name such as `Asia/Damascus` into a `tzinfo`."""
    return dates.get_timezone(tz) if isinstance(tz, str) else tz


@collection.filter(
    examples=[
        ("{{ x | babel.format_decimal }}", X, "1,234.5"),
        ("{{ x | babel.format_decimal(locale='de_DE') }}", X, "1.234,5"),
        ("{{ x | babel.format_decimal('#,##0.00') }}", X, "1,234.50"),
        (
            "{{ x | babel.format_decimal(locale='ar_SY', numbering_system='default') }}",
            X,
            "1٬234٫5",
        ),
    ]
)
def format_decimal(
    value: Number,
    /,
    format: str | None = None,
    locale: str | None = None,
    decimal_quantization: bool = True,
    group_separator: bool = True,
    *,
    numbering_system: str = "latn",
) -> str:
    """Format a number for the locale, optionally with a CLDR pattern such as `#,##0.00`."""
    return numbers.format_decimal(
        value,
        format,
        locale_of(locale),
        decimal_quantization,
        group_separator,
        numbering_system=numbering_system,
    )


@collection.filter(
    examples=[
        ("{{ x | babel.format_currency('USD') }}", X, "$1,234.50"),
        ("{{ x | babel.format_currency('USD', locale='ar_SY') }}", X, "‏1,234.50\xa0US$"),
        ("{{ x | babel.format_currency('SYP', locale='ar_SY') }}", X, "‏1,234\xa0ل.س.‏"),
        (
            "{{ x | babel.format_currency('SYP', locale='ar_SY', currency_digits=false) }}",
            X,
            "‏1,234.50\xa0ل.س.‏",
        ),
        ("{{ x | babel.format_currency('EUR', locale='de_DE') }}", X, "1.234,50\xa0€"),
    ]
)
def format_currency(
    value: Number,
    currency: str,
    /,
    format: str | None = None,
    locale: str | None = None,
    currency_digits: bool = True,
    format_type: Literal["name", "standard", "accounting"] = "standard",
    decimal_quantization: bool = True,
    group_separator: bool = True,
    *,
    numbering_system: str = "latn",
) -> str:
    """Format an amount in `currency` (ISO 4217). `currency_digits` uses the currency's decimals."""
    return numbers.format_currency(
        value,
        currency,
        format,
        locale_of(locale),
        currency_digits,
        format_type,
        decimal_quantization,
        group_separator,
        numbering_system=numbering_system,
    )


@collection.filter(
    examples=[
        ("{{ 0.256 | babel.format_percent }}", {}, "26%"),
        ("{{ 0.256 | babel.format_percent('#,##0.0%') }}", {}, "25.6%"),
    ]
)
def format_percent(
    value: Number,
    /,
    format: str | None = None,
    locale: str | None = None,
    decimal_quantization: bool = True,
    group_separator: bool = True,
    *,
    numbering_system: str = "latn",
) -> str:
    """Format a ratio as a percentage (`0.25` gives `25%`)."""
    return numbers.format_percent(
        value,
        format,
        locale_of(locale),
        decimal_quantization,
        group_separator,
        numbering_system=numbering_system,
    )


@collection.filter(
    examples=[
        ("{{ 1234567 | babel.format_compact_decimal }}", {}, "1M"),
        ("{{ 1234567 | babel.format_compact_decimal(fraction_digits=1) }}", {}, "1.2M"),
        ("{{ 1234567 | babel.format_compact_decimal(format_type='long') }}", {}, "1 million"),
    ]
)
def format_compact_decimal(
    value: Number,
    /,
    *,
    format_type: Literal["short", "long"] = "short",
    locale: str | None = None,
    fraction_digits: int = 0,
    numbering_system: str = "latn",
) -> str:
    """Format a number in compact form, e.g. `1.2M` or `1 million`."""
    return numbers.format_compact_decimal(
        value,
        format_type=format_type,
        locale=locale_of(locale),
        fraction_digits=fraction_digits,
        numbering_system=numbering_system,
    )


@collection.filter(
    examples=[
        ("{{ d | babel.format_date }}", D, "Nov 22, 2026"),
        ("{{ d | babel.format_date('dd/MM/yyyy') }}", D, "22/11/2026"),
        ("{{ d | babel.format_date('full', locale='ar_SY') }}", D, "الأحد، 22 تشرين الثاني 2026"),
    ]
)
def format_date(value: date, /, format: Width = "medium", locale: str | None = None) -> str:
    """Format a date with a width (`short` … `full`) or a CLDR pattern such as `dd/MM/yyyy`."""
    return dates.format_date(value, format, locale_of(locale))


@collection.filter(
    examples=[
        ("{{ dt | babel.format_datetime('short') }}", DT, "11/22/26, 2:30 PM"),
        ("{{ dt | babel.format_datetime('yyyy-MM-dd HH:mm') }}", DT, "2026-11-22 14:30"),
        (
            "{{ dt | babel.format_datetime('HH:mm zzzz', tzinfo='Asia/Damascus') }}",
            {"dt": datetime.fromisoformat("2026-11-22T12:00Z")},
            "15:00 GMT+03:00",
        ),
    ]
)
def format_datetime(
    value: datetime,
    /,
    format: Width = "medium",
    tzinfo: tzinfo | str | None = None,
    locale: str | None = None,
) -> str:
    """Format a datetime; `tzinfo` (a `tzinfo` or an IANA name) converts it first."""
    return dates.format_datetime(value, format, zone(tzinfo), locale_of(locale))


@collection.filter(
    examples=[
        ("{{ t | babel.format_time('short') }}", {"t": time(14, 30)}, "2:30 PM"),
        ("{{ t | babel.format_time('HH:mm') }}", {"t": time(14, 30)}, "14:30"),
    ]
)
def format_time(
    value: time | datetime,
    /,
    format: Width = "medium",
    tzinfo: tzinfo | str | None = None,
    locale: str | None = None,
) -> str:
    """Format a time (or the time of a datetime)."""
    return dates.format_time(value, format, zone(tzinfo), locale_of(locale))


@collection.filter(
    examples=[
        ("{{ x | babel.format_timedelta }}", {"x": timedelta(hours=3)}, "3 hours"),
        ("{{ x | babel.format_timedelta(locale='ar_SY') }}", {"x": timedelta(days=2)}, "يومان"),
        (
            "{{ x | babel.format_timedelta(add_direction=true, format='short') }}",
            {"x": timedelta(minutes=-5)},
            "5 min. ago",
        ),
    ]
)
def format_timedelta(
    value: timedelta,
    /,
    granularity: Literal["year", "month", "week", "day", "hour", "minute", "second"] = "second",
    threshold: float = 0.85,
    add_direction: bool = False,
    format: Literal["narrow", "short", "medium", "long"] = "long",
    locale: str | None = None,
) -> str:
    """Format a duration in words, rounded to its largest unit (`3 hours`)."""
    return dates.format_timedelta(
        value, granularity, threshold, add_direction, format, locale_of(locale)
    )
