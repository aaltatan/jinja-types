"""The `ar` namespace: Arabic text, numbers and dates, from arapy (a runtime dependency).

Values are numbers, strings or dates depending on the member, so the namespace accepts any
value and arapy checks it. arapy ships no currencies: define a `Currency` (or `Noun`) in Python
and pass it in the context. Enum arguments (`gender`, `case`, `months`) take their string values,
e.g. `gender="feminine"`. `ar.to_hijri` needs `jinja-types[hijri]`; `ar.shape` and
`ar.reshape_only` need `jinja-types[shape]`.
"""

from collections.abc import Callable, Iterable
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Any, Literal

import arapy
from arapy import ArDate, ArDateTime, Case, Currency, Gender, HijriDate, MonthNames, Noun
from arapy.digits import DecimalMark, DigitSet
from arapy.normalize import NAMES, SEARCH, SORT, Normalizer
from jinja2.filters import make_attrgetter

from jinja_types.core import Collection

from .str_ import SANDBOX

collection = Collection("ar", object)

type Number = int | Decimal | str
type Preset = Literal["names", "search", "sort"]
type Months = Literal["levant", "egyptian", "maghreb", "levant_with_egyptian"]
type Key = str | Callable[[Any], object] | None

PRESETS: dict[str, Normalizer] = {"names": NAMES, "search": SEARCH, "sort": SORT}

QIRSH = Noun.create("قرش", "قرشان", "قروش", gender=Gender.MASCULINE)
SYP = Currency.create(
    code="SYP",
    singular="ليرة سورية",
    dual="ليرتان سوريتان",
    plural="ليرات سورية",
    gender=Gender.FEMININE,
    subunit=QIRSH,
    symbol="ل.س",
)
HOUR = Noun.create("ساعة", "ساعتان", "ساعات", gender=Gender.FEMININE)
D = {"d": date(2026, 1, 5)}
DT = {"dt": datetime(2026, 1, 5, 14, 30)}
NAMES_LIST = {"names": ["مريم", "أحمد", "باسل"]}


@collection.filter(
    examples=[
        ("{{ 1234 | ar.to_words }}", {}, "ألف ومئتان وأربعة وثلاثون"),
        ("{{ 3 | ar.to_words(hour) }}", {"hour": HOUR}, "ثلاث ساعات"),
        (
            "{{ salary | ar.to_words(syp) }}",
            {"salary": Decimal("1500.25"), "syp": SYP},
            "ألف وخمسمئة ليرة سورية وخمسة وعشرون قرشًا",
        ),
    ]
)
def to_words(value: Number, /, unit: Noun | None = None) -> str:
    """Write a number in Arabic words (تفقيط), optionally counting a noun or a currency."""
    return arapy.to_words(value, unit)


@collection.filter(
    examples=[
        (
            "{{ salary | ar.format_money(syp) }}",
            {"salary": Decimal("12500"), "syp": SYP},
            "١٢٬٥٠٠ ل.س",
        ),
        (
            "{{ salary | ar.format_money(syp, digits='latin', grouping=',', decimal='.') }}",
            {"salary": Decimal("12500.5"), "syp": SYP},
            "12,500.50 ل.س",
        ),
    ]
)
def format_money(
    value: Number,
    currency: Currency,
    /,
    *,
    digits: DigitSet = "arabic",
    grouping: str | None = "٬",
    decimal: str = "٫",
    places: int | None = None,
) -> str:
    """Format an amount with the currency symbol. Money is never rounded."""
    return arapy.format_money(
        value, currency, digits=digits, grouping=grouping, decimal=decimal, places=places
    )


@collection.filter(examples=[("{{ 'Room 2026' | ar.to_arabic_digits }}", {}, "Room ٢٠٢٦")])
def to_arabic_digits(value: str | int | Decimal, /) -> str:
    """Replace Latin and Persian digits with Arabic-Indic digits."""
    return arapy.to_arabic_digits(str(value))


@collection.filter(examples=[("{{ x | ar.to_latin_digits }}", {"x": "٢٠٢٦"}, "2026")])
def to_latin_digits(value: str | int | Decimal, /) -> str:
    """Replace Arabic-Indic and Persian digits with Latin digits."""
    return arapy.to_latin_digits(str(value))


@collection.filter(examples=[("{{ 2026 | ar.to_persian_digits }}", {}, "۲۰۲۶")])
def to_persian_digits(value: str | int | Decimal, /) -> str:
    """Replace Latin and Arabic-Indic digits with Persian digits."""
    return arapy.to_persian_digits(str(value))


@collection.filter(
    examples=[
        ("{{ x | ar.format_number }}", {"x": Decimal("1234567.5")}, "1,234,567.5"),
        (
            "{{ x | ar.format_number(digits='arabic', grouping='٬', decimal='٫', places=2) }}",
            {"x": Decimal("1234567.5")},
            "١٬٢٣٤٬٥٦٧٫٥٠",
        ),
    ]
)
def format_number(
    value: Number,
    /,
    *,
    digits: DigitSet = "latin",
    grouping: str | None = ",",
    decimal: str = ".",
    places: int | None = None,
) -> str:
    """Format a number with a digit set, thousands separator and decimal mark."""
    return arapy.format_number(
        value, digits=digits, grouping=grouping, decimal=decimal, places=places
    )


@collection.filter(
    examples=[
        ("{{ x | ar.format_percent }}", {"x": Decimal("0.25")}, "25٪"),
        ("{{ x | ar.format_percent(digits='arabic') }}", {"x": Decimal("0.125")}, "١٢.٥٪"),
    ]
)
def format_percent(
    value: Number,
    /,
    *,
    digits: DigitSet = "latin",
    grouping: str | None = ",",
    decimal: str = ".",
    places: int | None = None,
) -> str:
    """Format a fraction as a percentage with the `٪` sign."""
    return arapy.format_percent(
        value, digits=digits, grouping=grouping, decimal=decimal, places=places
    )


@collection.filter(
    examples=[
        ("{{ x | ar.parse_number }}", {"x": "١٬٢٣٤٫٥"}, "1234.5"),
        ("{{ x | ar.parse_number(decimal=',') }}", {"x": "1.234,5"}, "1234.5"),
    ]
)
def parse_number(value: str, /, *, decimal: DecimalMark | None = None) -> Decimal:
    """Parse a number written in any digit set into an exact `Decimal`."""
    return arapy.parse_number(value, decimal=decimal)


@collection.filter(
    examples=[
        ("{{ 3 | ar.ordinal }}", {}, "الثالث"),
        ("{{ 3 | ar.ordinal('feminine') }}", {}, "الثالثة"),
        ("{{ 3 | ar.ordinal(definite=false, case='accusative') }}", {}, "ثالثًا"),
    ]
)
def ordinal(
    value: int,
    /,
    gender: Literal["masculine", "feminine"] = "masculine",
    *,
    definite: bool = True,
    case: Literal["nominative", "accusative", "genitive"] = "nominative",
) -> str:
    """The ordinal of a number from 1 to 100: «الثالث»."""
    return arapy.ordinal(value, Gender(gender), definite=definite, case=Case(case))


@collection.filter(examples=[("{{ 2 | ar.ordinal_adverb }}", {}, "ثانيًا")])
def ordinal_adverb(value: int, /) -> str:
    """The list marker for a number from 1 to 100: «أولًا»، «ثانيًا»."""
    return arapy.ordinal_adverb(value)


@collection.filter(
    examples=[
        ("{{ x | ar.normalize }}", {"x": "أَحْمَد"}, "احمد"),
        ("{{ x | ar.normalize('names') }}", {"x": "عبدالله"}, "عبد الله"),
    ]
)
def normalize(value: str, /, preset: Preset = "search") -> str:
    """Normalize Arabic text with a preset: `search`, `names` or `sort`."""
    return PRESETS[preset](value)


@collection.filter(
    examples=[
        ("{{ 'عبدالله' | ar.equals('عبد الله') }}", {}, "True"),
        ("{{ 'أحمد' is ar.equals('احمد') }}", {}, "True"),
        ("{{ 'أحمد' is ar.equals('محمد') }}", {}, "False"),
    ]
)
def equals(value: str, other: str, /, preset: Preset = "names") -> bool:
    """Return True if both strings match after normalizing them. Also a test."""
    return arapy.ar_equals(value, other, PRESETS[preset])


@collection.filter(
    examples=[
        ("{{ names | ar.sort | join('، ') }}", NAMES_LIST, "أحمد، باسل، مريم"),
        ("{{ names | ar.sort(reverse=true) | join('، ') }}", NAMES_LIST, "مريم، باسل، أحمد"),
        (
            "{{ people | ar.sort(key='name') | map(attribute='age') | join('|') }}",
            {"people": [{"name": "مريم", "age": 30}, {"name": "باسل", "age": 41}]},
            "41|30",
        ),
    ]
)
def sort(value: Iterable[Any], /, *, key: Key = None, reverse: bool = False) -> list[Any]:
    """Sort in Arabic alphabetical order. `key` is an attribute name or a macro."""
    getter = make_attrgetter(SANDBOX, key) if isinstance(key, str) else key or str

    return arapy.ar_sorted(value, key=lambda item: str(getter(item)), reverse=reverse)


@collection.filter(
    examples=[
        ("{{ x | ar.duration }}", {"x": timedelta(days=9)}, "أسبوع ويومان"),
        ("{{ x | ar.duration }}", {"x": timedelta(hours=2, minutes=30)}, "ساعتان وثلاثون دقيقةً"),
    ]
)
def duration(value: timedelta, /) -> str:
    """A duration in words, largest unit first: «أسبوع ويومان»."""
    return arapy.ar_duration(value)


@collection.filter(
    examples=[
        ("{{ dt | ar.since(now) }}", {**DT, "now": datetime(2026, 1, 8, 14, 30)}, "منذ ثلاثة أيام"),
        ("{{ dt | ar.since(now) }}", {**DT, "now": datetime(2026, 1, 5, 12, 30)}, "بعد ساعتين"),
    ]
)
def since(value: datetime, /, now: datetime | None = None) -> str:
    """How long ago (or how far ahead) the datetime is, in its largest whole unit."""
    return arapy.ar_since(value, now)


@collection.filter(
    examples=[
        ("{{ d | ar.format_date('%A %d %B %Y') }}", D, "الاثنين 05 كانون الثاني 2026"),
        (
            "{{ d | ar.format_date('%O من %B', months='egyptian', digits='arabic') }}",
            D,
            "الخامس من يناير",
        ),
        ("{{ dt | ar.format_date('%d/%m/%Y %I:%M %p') }}", DT, "05/01/2026 02:30 مساءً"),
    ]
)
def format_date(
    value: date | HijriDate,
    fmt: str,
    /,
    *,
    months: Months = "levant",
    digits: DigitSet = "latin",
) -> str:
    """Format with Arabic names: strftime directives, `%O` for the ordinal day.

    Datetimes also take `%H %I %M %S %p`. Hijri dates use Hijri month names (`months` is
    ignored).
    """
    if isinstance(value, HijriDate):
        return value.format(fmt, digits=digits)

    if isinstance(value, datetime):
        return ArDateTime.from_datetime(value).format(fmt, months=MonthNames(months), digits=digits)

    return ArDate.from_date(value).format(fmt, months=MonthNames(months), digits=digits)


@collection.filter(
    examples=[
        ("{{ d | ar.month_name }}", D, "كانون الثاني"),
        ("{{ d | ar.month_name('levant_with_egyptian') }}", D, "كانون الثاني (يناير)"),
    ]
)
def month_name(value: date, /, style: Months = "levant") -> str:
    """The month's Arabic name: «كانون الثاني», «يناير», …"""
    return ArDate.from_date(value).month_name(MonthNames(style))


@collection.filter(examples=[("{{ d | ar.weekday_name }}", D, "الاثنين")])
def weekday_name(value: date, /) -> str:
    """The weekday's Arabic name: «الاثنين» … «الأحد»."""
    return ArDate.from_date(value).weekday_name


@collection.filter(
    examples=[
        ("{{ x | ar.parse_date('%d %B %Y') }}", {"x": "٥ كانون الثاني ٢٠٢٦"}, "2026-01-05"),
        ("{{ x | ar.parse_date('%d %B %Y') | date.weekday }}", {"x": "5 يناير 2026"}, "0"),
    ]
)
def parse_date(value: str, fmt: str, /, *, months: Months | None = None) -> date:
    """Strictly parse Arabic date text, in any digit set. `months=None` accepts every style."""
    return ArDate.strptime(value, fmt, months=None if months is None else MonthNames(months))


@collection.filter(
    examples=[
        (
            "{{ x | ar.parse_datetime('%d/%m/%Y %H:%M') }}",
            {"x": "٠٥/٠١/٢٠٢٦ ١٤:٣٠"},
            "2026-01-05 14:30:00",
        )
    ]
)
def parse_datetime(value: str, fmt: str, /, *, months: Months | None = None) -> datetime:
    """Strictly parse Arabic datetime text, in any digit set."""
    return ArDateTime.strptime(value, fmt, months=None if months is None else MonthNames(months))


@collection.filter(
    examples=[
        ("{{ d | ar.to_hijri | ar.format_date('%d %B %Y') }}", D, "16 رجب 1447"),
        ("{{ d | ar.to_hijri }}", D, "1447-07-16"),
    ]
)
def to_hijri(value: date, /) -> HijriDate:
    """The same day in the Hijri (Umm al-Qura) calendar. Needs `jinja-types[hijri]`."""
    return ArDate.from_date(value).to_hijri()


@collection.filter(examples=[("{{ 'سلام' | ar.shape | length }}", {}, "3")])
def shape(value: str, /) -> str:
    """Join the letters and reorder for left-to-right drawing. Needs `jinja-types[shape]`."""
    return arapy.shape(value)


@collection.filter(examples=[("{{ 'سلام' | ar.reshape_only | length }}", {}, "3")])
def reshape_only(value: str, /) -> str:
    """Join the letters but keep the logical order. Needs `jinja-types[shape]`."""
    return arapy.reshape_only(value)
