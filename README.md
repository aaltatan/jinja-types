# jinja-types

`jinja-types` is a Jinja2 extension that exposes the methods and attributes of everyday Python
types (`str`, `int`, `float`, `bool`, `Decimal`, `Fraction`, `date`, `datetime`, `time`,
`timedelta`, `list`, `dict`, `UUID`, `PurePath`) and the `re` module as Jinja filters and tests.
Names and parameters match Python exactly, everything works in `ImmutableSandboxedEnvironment`,
and a registry makes it easy to plug in new filter sets.

## Setup

Add jinja-types as an extension on your environment:

```python
from jinja2.sandbox import ImmutableSandboxedEnvironment

from jinja_types import TypesExtension

env = ImmutableSandboxedEnvironment(extensions=[TypesExtension])

# with options: none_passthrough, coerce, regex_timeout, locale, registry
env = ImmutableSandboxedEnvironment(
    extensions=[TypesExtension.configure(none_passthrough=True, locale="ar_SY")],
)
```

The string `"jinja_types.TypesExtension"` works too, wherever Jinja takes extension names.

## Qualified names only

Every type member is reachable only as `namespace.member`, so nothing clashes with Jinja's
built-in filters (`count`, `format`, `join`, `replace`, …):

```jinja
{{ code | str.zfill(5) }}
{{ amount | decimal.quantize(decimal.Decimal("0.01")) }}
{{ invoice_date | date.strftime("%d/%m/%Y") }}
{% if code is str.isdigit %}…{% endif %}
```

Helpers that are not type members use plain names: `fmt`, `to_int`, `to_decimal`, `to_date`, …

## Example: money

Round a salary half-up to two places, then format it with thousands separators:

```jinja
{{ salary | decimal.quantize(decimal.Decimal("0.01"), rounding=decimal.ROUND_HALF_UP) | fmt(",.2f") }}
```

With `salary = Decimal("1500.005")` this gives `1,500.01`. The global `decimal` holds
`Decimal`, `Context` and the `ROUND_*` constants; the filter namespace `decimal.*` holds the
`Decimal` methods. `bool` is a subclass of `int`, so every `int.*` filter also accepts `true`
and `false`.

Dates work the same way. `date.*` filters also accept datetimes and call the `datetime` version
when one exists, so `{{ moment | date.isoformat(" ", "seconds") }}` works on a datetime. The
`datetime.*` namespace holds only what `datetime` adds or overrides. `datetime.astimezone` also
takes an IANA timezone name, e.g. `{{ moment | datetime.astimezone("Asia/Damascus") }}`; on
Windows, install the `tzdata` package for timezone names to resolve.

Regex filters take the string as the piped value and keep Python's parameter names:
`{{ code | re.search("abc-(\\d+)", flags=re.I) | match.group(1) }}`. Jinja string literals
process backslash escapes, so write `\\d` for the regex `\d`. `re.sub` also accepts a macro that
gets the match; under autoescape its output is kept as markup and the rest of the string is
escaped once. With the `[regex]` extra, the `regex` library is used and every call is limited
by `regex_timeout` (seconds, default 1.0).

`re.compile(pattern, flags)` returns a compiled pattern (cached); its members are the `pattern`
namespace, with the pattern piped in as in Python:

```jinja
{% set word = re.compile("\\w+", re.I) %}
{{ word | pattern.findall(text) | join(", ") }}
{% if word is pattern.fullmatch(name) %}one word{% endif %}
```

Every filter, test and global is listed with its examples in the [Reference](#reference) below,
and in more detail (signatures, types) in [docs/](docs/guide/types/index.md). Both are generated from the catalog. The same catalog is
available from the command line:

```
jinja-types catalog --namespace str --format markdown
jinja-types catalog --kind test            # JSON, see schema/catalog.schema.json
jinja-types conflicts --plugins
```

To add your own filter sets as an installable plugin, see [docs/guide/plugins.md](docs/guide/plugins.md).

With the `[babel]` extra, `babel.*` formats numbers, money and dates for a locale. The locale
is the `locale=` argument, else `TypesExtension.configure(locale="ar_SY")`, else `en_US`:

```jinja
{{ salary | babel.format_currency("USD") }}                                   {# $1,234.50 (en_US) #}
{{ salary | babel.format_currency("SYP", locale="ar_SY", currency_digits=false) }}  {# ‏1,234.50 ل.س.‏ #}
{{ salary | babel.format_decimal(locale="ar_SY", numbering_system="default") }}  {# 1٬234٫5 #}
```

`SYP` has no minor unit in CLDR, so `currency_digits=false` is needed to show piastres. `numbering_system="default"`
uses the locale's own separators (`٬` and `٫`); Babel keeps Latin digits either way, so
Arabic-Indic digits come from the arapy plugin.

Arabic text, numbers and dates come from [arapy](https://pypi.org/project/arapy/), a dependency,
under the `ar` namespace. arapy ships no currencies: define one in Python and pass it in:

```python
from arapy import Currency, Gender, Noun

qirsh = Noun.create("قرش", "قرشان", "قروش", gender=Gender.MASCULINE)
syp = Currency.create(
    code="SYP",
    singular="ليرة سورية",
    dual="ليرتان سوريتان",
    plural="ليرات سورية",
    gender=Gender.FEMININE,
    subunit=qirsh,
    symbol="ل.س",
)
```

```jinja
{{ salary | ar.to_words(syp) }}       {# ألف وخمسمئة ليرة سورية #}
{{ salary | ar.format_money(syp) }}   {# ١٬٥٠٠ ل.س #}
{{ day | ar.format_date("%A %d %B %Y", digits="arabic") }}
```

`ar.to_hijri` needs `jinja-types[hijri]`, and `ar.shape` / `ar.reshape_only` need
`jinja-types[shape]`.

<!-- reference:start (generated by scripts/gen_docs.py, do not edit) -->

## Reference

Every member (331), with every example. Generated from the catalog.

[`ar`](#ar) · [`babel`](#babel) · [`date`](#date) · [`datetime`](#datetime) · [`decimal`](#decimal) · [`dict`](#dict) · [`float`](#float) · [`fraction`](#fraction) · [`helpers`](#helpers) · [`int`](#int) · [`list`](#list) · [`match`](#match) · [`path`](#path) · [`pattern`](#pattern) · [`re`](#re) · [`str`](#str) · [`time`](#time) · [`timedelta`](#timedelta) · [`uuid`](#uuid)

### ar

| Member | Kinds | Description | Example | Result |
|---|---|---|---|---|
| `ar.duration` | filter | A duration in words, largest unit first: «أسبوع ويومان». | `` {{ x \| ar.duration }} ``<br>with `` x = datetime.timedelta(days=9) `` | `` أسبوع ويومان `` |
|  |  |  | `` {{ x \| ar.duration }} ``<br>with `` x = datetime.timedelta(seconds=9000) `` | `` ساعتان وثلاثون دقيقةً `` |
| `ar.equals(other, preset)` | filter, test | Return True if both strings match after normalizing them. Also a test. | `` {{ 'عبدالله' \| ar.equals('عبد الله') }} `` | `` True `` |
|  |  |  | `` {{ 'أحمد' is ar.equals('احمد') }} `` | `` True `` |
|  |  |  | `` {{ 'أحمد' is ar.equals('محمد') }} `` | `` False `` |
| `ar.format_date(fmt, months, digits)` | filter | Format with Arabic names: strftime directives, `%O` for the ordinal day. | `` {{ d \| ar.format_date('%A %d %B %Y') }} ``<br>with `` d = datetime.date(2026, 1, 5) `` | `` الاثنين 05 كانون الثاني 2026 `` |
|  |  |  | `` {{ d \| ar.format_date('%O من %B', months='egyptian', digits='arabic') }} ``<br>with `` d = datetime.date(2026, 1, 5) `` | `` الخامس من يناير `` |
|  |  |  | `` {{ dt \| ar.format_date('%d/%m/%Y %I:%M %p') }} ``<br>with `` dt = datetime.datetime(2026, 1, 5, 14, 30) `` | `` 05/01/2026 02:30 مساءً `` |
| `ar.format_money(currency, digits, grouping, decimal, places)` | filter | Format an amount with the currency symbol. Money is never rounded. | `` {{ salary \| ar.format_money(syp) }} ``<br>with `` salary = Decimal('12500'), syp = Currency(...) `` | `` ١٢٬٥٠٠ ل.س `` |
|  |  |  | `` {{ salary \| ar.format_money(syp, digits='latin', grouping=',', decimal='.') }} ``<br>with `` salary = Decimal('12500.5'), syp = Currency(...) `` | `` 12,500.50 ل.س `` |
| `ar.format_number(digits, grouping, decimal, places)` | filter | Format a number with a digit set, thousands separator and decimal mark. | `` {{ x \| ar.format_number }} ``<br>with `` x = Decimal('1234567.5') `` | `` 1,234,567.5 `` |
|  |  |  | `` {{ x \| ar.format_number(digits='arabic', grouping='٬', decimal='٫', places=2) }} ``<br>with `` x = Decimal('1234567.5') `` | `` ١٬٢٣٤٬٥٦٧٫٥٠ `` |
| `ar.format_percent(digits, grouping, decimal, places)` | filter | Format a fraction as a percentage with the `٪` sign. | `` {{ x \| ar.format_percent }} ``<br>with `` x = Decimal('0.25') `` | `` 25٪ `` |
|  |  |  | `` {{ x \| ar.format_percent(digits='arabic') }} ``<br>with `` x = Decimal('0.125') `` | `` ١٢.٥٪ `` |
| `ar.month_name(style)` | filter | The month's Arabic name: «كانون الثاني», «يناير», … | `` {{ d \| ar.month_name }} ``<br>with `` d = datetime.date(2026, 1, 5) `` | `` كانون الثاني `` |
|  |  |  | `` {{ d \| ar.month_name('levant_with_egyptian') }} ``<br>with `` d = datetime.date(2026, 1, 5) `` | `` كانون الثاني (يناير) `` |
| `ar.normalize(preset)` | filter | Normalize Arabic text with a preset: `search`, `names` or `sort`. | `` {{ x \| ar.normalize }} ``<br>with `` x = 'أَحْمَد' `` | `` احمد `` |
|  |  |  | `` {{ x \| ar.normalize('names') }} ``<br>with `` x = 'عبدالله' `` | `` عبد الله `` |
| `ar.ordinal(gender, definite, case)` | filter | The ordinal of a number from 1 to 100: «الثالث». | `` {{ 3 \| ar.ordinal }} `` | `` الثالث `` |
|  |  |  | `` {{ 3 \| ar.ordinal('feminine') }} `` | `` الثالثة `` |
|  |  |  | `` {{ 3 \| ar.ordinal(definite=false, case='accusative') }} `` | `` ثالثًا `` |
| `ar.ordinal_adverb` | filter | The list marker for a number from 1 to 100: «أولًا»، «ثانيًا». | `` {{ 2 \| ar.ordinal_adverb }} `` | `` ثانيًا `` |
| `ar.parse_date(fmt, months)` | filter | Strictly parse Arabic date text, in any digit set. `months=None` accepts every style. | `` {{ x \| ar.parse_date('%d %B %Y') }} ``<br>with `` x = '٥ كانون الثاني ٢٠٢٦' `` | `` 2026-01-05 `` |
|  |  |  | `` {{ x \| ar.parse_date('%d %B %Y') \| date.weekday }} ``<br>with `` x = '5 يناير 2026' `` | `` 0 `` |
| `ar.parse_datetime(fmt, months)` | filter | Strictly parse Arabic datetime text, in any digit set. | `` {{ x \| ar.parse_datetime('%d/%m/%Y %H:%M') }} ``<br>with `` x = '٠٥/٠١/٢٠٢٦ ١٤:٣٠' `` | `` 2026-01-05 14:30:00 `` |
| `ar.parse_number(decimal)` | filter | Parse a number written in any digit set into an exact `Decimal`. | `` {{ x \| ar.parse_number }} ``<br>with `` x = '١٬٢٣٤٫٥' `` | `` 1234.5 `` |
|  |  |  | `` {{ x \| ar.parse_number(decimal=',') }} ``<br>with `` x = '1.234,5' `` | `` 1234.5 `` |
| `ar.reshape_only` | filter | Join the letters but keep the logical order. Needs `jinja-types[shape]`. | `` {{ 'سلام' \| ar.reshape_only \| length }} `` | `` 3 `` |
| `ar.shape` | filter | Join the letters and reorder for left-to-right drawing. Needs `jinja-types[shape]`. | `` {{ 'سلام' \| ar.shape \| length }} `` | `` 3 `` |
| `ar.since(now)` | filter | How long ago (or how far ahead) the datetime is, in its largest whole unit. | `` {{ dt \| ar.since(now) }} ``<br>with `` dt = datetime.datetime(2026, 1, 5, 14, 30), now = datetime.datetime(2026, 1, 8, 14, 30) `` | `` منذ ثلاثة أيام `` |
|  |  |  | `` {{ dt \| ar.since(now) }} ``<br>with `` dt = datetime.datetime(2026, 1, 5, 14, 30), now = datetime.datetime(2026, 1, 5, 12, 30) `` | `` بعد ساعتين `` |
| `ar.sort(key, reverse)` | filter | Sort in Arabic alphabetical order. `key` is an attribute name or a macro. | `` {{ names \| ar.sort \| join('، ') }} ``<br>with `` names = ['مريم', 'أحمد', 'باسل'] `` | `` أحمد، باسل، مريم `` |
|  |  |  | `` {{ names \| ar.sort(reverse=true) \| join('، ') }} ``<br>with `` names = ['مريم', 'أحمد', 'باسل'] `` | `` مريم، باسل، أحمد `` |
|  |  |  | `` {{ people \| ar.sort(key='name') \| map(attribute='age') \| join('\|') }} ``<br>with `` people = [{'name': 'مريم', 'age': 30}, {'name': 'باسل', 'age': 41}] `` | `` 41\|30 `` |
| `ar.to_arabic_digits` | filter | Replace Latin and Persian digits with Arabic-Indic digits. | `` {{ 'Room 2026' \| ar.to_arabic_digits }} `` | `` Room ٢٠٢٦ `` |
| `ar.to_hijri` | filter | The same day in the Hijri (Umm al-Qura) calendar. Needs `jinja-types[hijri]`. | `` {{ d \| ar.to_hijri \| ar.format_date('%d %B %Y') }} ``<br>with `` d = datetime.date(2026, 1, 5) `` | `` 16 رجب 1447 `` |
|  |  |  | `` {{ d \| ar.to_hijri }} ``<br>with `` d = datetime.date(2026, 1, 5) `` | `` 1447-07-16 `` |
| `ar.to_latin_digits` | filter | Replace Arabic-Indic and Persian digits with Latin digits. | `` {{ x \| ar.to_latin_digits }} ``<br>with `` x = '٢٠٢٦' `` | `` 2026 `` |
| `ar.to_persian_digits` | filter | Replace Latin and Arabic-Indic digits with Persian digits. | `` {{ 2026 \| ar.to_persian_digits }} `` | `` ۲۰۲۶ `` |
| `ar.to_words(unit)` | filter | Write a number in Arabic words (تفقيط), optionally counting a noun or a currency. | `` {{ 1234 \| ar.to_words }} `` | `` ألف ومئتان وأربعة وثلاثون `` |
|  |  |  | `` {{ 3 \| ar.to_words(hour) }} ``<br>with `` hour = Noun(...) `` | `` ثلاث ساعات `` |
|  |  |  | `` {{ salary \| ar.to_words(syp) }} ``<br>with `` salary = Decimal('1500.25'), syp = Currency(...) `` | `` ألف وخمسمئة ليرة سورية وخمسة وعشرون قرشًا `` |
| `ar.weekday_name` | filter | The weekday's Arabic name: «الاثنين» … «الأحد». | `` {{ d \| ar.weekday_name }} ``<br>with `` d = datetime.date(2026, 1, 5) `` | `` الاثنين `` |

### babel

| Member | Kinds | Description | Example | Result |
|---|---|---|---|---|
| `babel.format_compact_decimal(format_type, locale, fraction_digits, numbering_system)` | filter | Format a number in compact form, e.g. `1.2M` or `1 million`. | `` {{ 1234567 \| babel.format_compact_decimal }} `` | `` 1M `` |
|  |  |  | `` {{ 1234567 \| babel.format_compact_decimal(fraction_digits=1) }} `` | `` 1.2M `` |
|  |  |  | `` {{ 1234567 \| babel.format_compact_decimal(format_type='long') }} `` | `` 1 million `` |
| `babel.format_currency(currency, format, locale, currency_digits, format_type, decimal_quantization, group_separator, numbering_system)` | filter | Format an amount in `currency` (ISO 4217). `currency_digits` uses the currency's decimals. | `` {{ x \| babel.format_currency('USD') }} ``<br>with `` x = Decimal('1234.5') `` | `` $1,234.50 `` |
|  |  |  | `` {{ x \| babel.format_currency('USD', locale='ar_SY') }} ``<br>with `` x = Decimal('1234.5') `` | `` ‏1,234.50 US$ `` |
|  |  |  | `` {{ x \| babel.format_currency('SYP', locale='ar_SY') }} ``<br>with `` x = Decimal('1234.5') `` | `` ‏1,234 ل.س.‏ `` |
|  |  |  | `` {{ x \| babel.format_currency('SYP', locale='ar_SY', currency_digits=false) }} ``<br>with `` x = Decimal('1234.5') `` | `` ‏1,234.50 ل.س.‏ `` |
|  |  |  | `` {{ x \| babel.format_currency('EUR', locale='de_DE') }} ``<br>with `` x = Decimal('1234.5') `` | `` 1.234,50 € `` |
| `babel.format_date(format, locale)` | filter | Format a date with a width (`short` … `full`) or a CLDR pattern such as `dd/MM/yyyy`. | `` {{ d \| babel.format_date }} ``<br>with `` d = datetime.date(2026, 11, 22) `` | `` Nov 22, 2026 `` |
|  |  |  | `` {{ d \| babel.format_date('dd/MM/yyyy') }} ``<br>with `` d = datetime.date(2026, 11, 22) `` | `` 22/11/2026 `` |
|  |  |  | `` {{ d \| babel.format_date('full', locale='ar_SY') }} ``<br>with `` d = datetime.date(2026, 11, 22) `` | `` الأحد، 22 تشرين الثاني 2026 `` |
| `babel.format_datetime(format, tzinfo, locale)` | filter | Format a datetime; `tzinfo` (a `tzinfo` or an IANA name) converts it first. | `` {{ dt \| babel.format_datetime('short') }} ``<br>with `` dt = datetime.datetime(2026, 11, 22, 14, 30) `` | `` 11/22/26, 2:30 PM `` |
|  |  |  | `` {{ dt \| babel.format_datetime('yyyy-MM-dd HH:mm') }} ``<br>with `` dt = datetime.datetime(2026, 11, 22, 14, 30) `` | `` 2026-11-22 14:30 `` |
|  |  |  | `` {{ dt \| babel.format_datetime('HH:mm zzzz', tzinfo='Asia/Damascus') }} ``<br>with `` dt = datetime.datetime(2026, 11, 22, 12, 0, tzinfo=datetime.timezone.utc) `` | `` 15:00 GMT+03:00 `` |
| `babel.format_decimal(format, locale, decimal_quantization, group_separator, numbering_system)` | filter | Format a number for the locale, optionally with a CLDR pattern such as `#,##0.00`. | `` {{ x \| babel.format_decimal }} ``<br>with `` x = Decimal('1234.5') `` | `` 1,234.5 `` |
|  |  |  | `` {{ x \| babel.format_decimal(locale='de_DE') }} ``<br>with `` x = Decimal('1234.5') `` | `` 1.234,5 `` |
|  |  |  | `` {{ x \| babel.format_decimal('#,##0.00') }} ``<br>with `` x = Decimal('1234.5') `` | `` 1,234.50 `` |
|  |  |  | `` {{ x \| babel.format_decimal(locale='ar_SY', numbering_system='default') }} ``<br>with `` x = Decimal('1234.5') `` | `` 1٬234٫5 `` |
| `babel.format_percent(format, locale, decimal_quantization, group_separator, numbering_system)` | filter | Format a ratio as a percentage (`0.25` gives `25%`). | `` {{ 0.256 \| babel.format_percent }} `` | `` 26% `` |
|  |  |  | `` {{ 0.256 \| babel.format_percent('#,##0.0%') }} `` | `` 25.6% `` |
| `babel.format_time(format, tzinfo, locale)` | filter | Format a time (or the time of a datetime). | `` {{ t \| babel.format_time('short') }} ``<br>with `` t = datetime.time(14, 30) `` | `` 2:30 PM `` |
|  |  |  | `` {{ t \| babel.format_time('HH:mm') }} ``<br>with `` t = datetime.time(14, 30) `` | `` 14:30 `` |
| `babel.format_timedelta(granularity, threshold, add_direction, format, locale)` | filter | Format a duration in words, rounded to its largest unit (`3 hours`). | `` {{ x \| babel.format_timedelta }} ``<br>with `` x = datetime.timedelta(seconds=10800) `` | `` 3 hours `` |
|  |  |  | `` {{ x \| babel.format_timedelta(locale='ar_SY') }} ``<br>with `` x = datetime.timedelta(days=2) `` | `` يومان `` |
|  |  |  | `` {{ x \| babel.format_timedelta(add_direction=true, format='short') }} ``<br>with `` x = datetime.timedelta(days=-1, seconds=86100) `` | `` 5 min. ago `` |

### date

| Member | Kinds | Description | Example | Result |
|---|---|---|---|---|
| `date.ctime` | filter | Return a `ctime()` style string. | `` {{ x \| date.ctime }} ``<br>with `` x = datetime.date(2026, 11, 22) `` | `` Sun Nov 22 00:00:00 2026 `` |
| `date.day` | attribute | The day of the month. | `` {{ x \| date.day }} ``<br>with `` x = datetime.date(2026, 11, 22) `` | `` 22 `` |
| `date.fromisocalendar(week, day)` | filter | Return the date for an ISO year, week and weekday (classmethod; the year is piped in). | `` {{ 2026 \| date.fromisocalendar(47, 7) }} `` | `` 2026-11-22 `` |
| `date.fromisoformat` | filter | Parse an ISO date (classmethod; the string is piped in). | `` {{ '2026-11-22' \| date.fromisoformat }} `` | `` 2026-11-22 `` |
| `date.fromordinal` | filter | Return the date for a proleptic Gregorian ordinal (classmethod; the ordinal is piped in). | `` {{ 739942 \| date.fromordinal }} `` | `` 2026-11-22 `` |
| `date.fromtimestamp` | filter | Return the local date for a POSIX timestamp (classmethod; the timestamp is piped in). | `` {{ 100000 \| date.fromtimestamp \| date.year }} `` | `` 1970 `` |
| `date.isocalendar` | filter | Return `(year, week, weekday)` of the ISO calendar. | `` {{ x \| date.isocalendar \| join('-') }} ``<br>with `` x = datetime.date(2026, 11, 22) `` | `` 2026-47-7 `` |
| `date.isoformat` | filter | Return the date as `YYYY-MM-DD`. | `` {{ x \| date.isoformat }} ``<br>with `` x = datetime.date(2026, 11, 22) `` | `` 2026-11-22 `` |
|  |  |  | `` {{ x \| date.isoformat }} ``<br>with `` x = datetime.datetime(2026, 11, 22, 14, 30, 5) `` | `` 2026-11-22T14:30:05 `` |
| `date.isoweekday` | filter | Return the day of the week, Monday is 1 and Sunday is 7. | `` {{ x \| date.isoweekday }} ``<br>with `` x = datetime.date(2026, 11, 22) `` | `` 7 `` |
| `date.month` | attribute | The month, 1 to 12. | `` {{ x \| date.month }} ``<br>with `` x = datetime.date(2026, 11, 22) `` | `` 11 `` |
| `date.replace(year, month, day)` | filter | Return the date with the given fields replaced. | `` {{ x \| date.replace(day=1) }} ``<br>with `` x = datetime.date(2026, 11, 22) `` | `` 2026-11-01 `` |
|  |  |  | `` {{ x \| date.replace(2027, 1) }} ``<br>with `` x = datetime.date(2026, 11, 22) `` | `` 2027-01-22 `` |
|  |  |  | `` {{ x \| date.replace(hour=9) }} ``<br>with `` x = datetime.datetime(2026, 11, 22, 14, 30, 5) `` | `` 2026-11-22 09:30:05 `` |
| `date.strftime(format)` | filter | Format the date with a `strftime` format string. | `` {{ x \| date.strftime('%d/%m/%Y') }} ``<br>with `` x = datetime.date(2026, 11, 22) `` | `` 22/11/2026 `` |
|  |  |  | `` {{ x \| date.strftime('%H:%M') }} ``<br>with `` x = datetime.datetime(2026, 11, 22, 14, 30, 5) `` | `` 14:30 `` |
| `date.timetuple` | filter | Return a `time.struct_time`. | `` {{ x \| date.timetuple \| list }} ``<br>with `` x = datetime.date(2026, 11, 22) `` | `` [2026, 11, 22, 0, 0, 0, 6, 326, -1] `` |
| `date.toordinal` | filter | Return the proleptic Gregorian ordinal, where 0001-01-01 is 1. | `` {{ x \| date.toordinal }} ``<br>with `` x = datetime.date(2026, 11, 22) `` | `` 739942 `` |
| `date.weekday` | filter | Return the day of the week, Monday is 0 and Sunday is 6. | `` {{ x \| date.weekday }} ``<br>with `` x = datetime.date(2026, 11, 22) `` | `` 6 `` |
| `date.year` | attribute | The year. | `` {{ x \| date.year }} ``<br>with `` x = datetime.date(2026, 11, 22) `` | `` 2026 `` |

### datetime

| Member | Kinds | Description | Example | Result |
|---|---|---|---|---|
| `datetime.astimezone(tz)` | filter | Convert to the timezone `tz`: a `tzinfo`, an IANA name, or None for local time. | `` {{ x \| datetime.astimezone('Asia/Damascus') }} ``<br>with `` x = datetime.datetime(2026, 11, 22, 12, 0, tzinfo=datetime.timezone.utc) `` | `` 2026-11-22 15:00:00+03:00 `` |
|  |  |  | `` {{ x \| datetime.astimezone(tz) }} ``<br>with `` x = datetime(...), tz = datetime.timezone.utc `` | `` 2026-11-22 09:00:00+00:00 `` |
| `datetime.combine(time, tzinfo)` | filter | Join a date and a time (classmethod; the date is piped in). | `` {{ d \| datetime.combine(t) }} ``<br>with `` d = datetime.date(2026, 11, 22), t = datetime.time(14, 30, 5, 250) `` | `` 2026-11-22 14:30:05.000250 `` |
|  |  |  | `` {{ d \| datetime.combine(t, tz) }} ``<br>with `` d = datetime.date(2026, 11, 22), t = datetime.time(9, 0), tz = datetime.timezone.utc `` | `` 2026-11-22 09:00:00+00:00 `` |
| `datetime.ctime` | filter | Return a `ctime()` style string. | `` {{ x \| datetime.ctime }} ``<br>with `` x = datetime.datetime(2026, 11, 22, 14, 30, 5, 250) `` | `` Sun Nov 22 14:30:05 2026 `` |
| `datetime.date` | filter | Return the date part. | `` {{ x \| datetime.date }} ``<br>with `` x = datetime.datetime(2026, 11, 22, 14, 30, 5, 250) `` | `` 2026-11-22 `` |
| `datetime.dst` | filter | Return the daylight saving offset, or None if unknown. | `` {{ x \| datetime.dst }} ``<br>with `` x = datetime(...) `` | `` None `` |
| `datetime.fold` | attribute | 0 or 1: which of two repeated wall times this is. | `` {{ x \| datetime.fold }} ``<br>with `` x = datetime.datetime(2026, 11, 22, 14, 30, 5, 250) `` | `` 0 `` |
| `datetime.fromisoformat` | filter | Parse an ISO datetime (classmethod; the string is piped in). | `` {{ '2026-11-22T14:30' \| datetime.fromisoformat }} `` | `` 2026-11-22 14:30:00 `` |
|  |  |  | `` {{ '2026-11-22T14:30Z' \| datetime.fromisoformat }} `` | `` 2026-11-22 14:30:00+00:00 `` |
| `datetime.fromtimestamp(tz)` | filter | Return the datetime for a POSIX timestamp (classmethod; the timestamp is piped in). | `` {{ 0 \| datetime.fromtimestamp(tz) }} ``<br>with `` tz = datetime.timezone.utc `` | `` 1970-01-01 00:00:00+00:00 `` |
| `datetime.hour` | attribute | The hour, 0 to 23. | `` {{ x \| datetime.hour }} ``<br>with `` x = datetime.datetime(2026, 11, 22, 14, 30, 5, 250) `` | `` 14 `` |
| `datetime.isoformat(sep, timespec)` | filter | Return the datetime in ISO 8601 format. | `` {{ x \| datetime.isoformat }} ``<br>with `` x = datetime.datetime(2026, 11, 22, 14, 30, 5, 250) `` | `` 2026-11-22T14:30:05.000250 `` |
|  |  |  | `` {{ x \| datetime.isoformat(' ', 'minutes') }} ``<br>with `` x = datetime.datetime(2026, 11, 22, 14, 30, 5, 250) `` | `` 2026-11-22 14:30 `` |
|  |  |  | `` {{ x \| date.isoformat(timespec='seconds') }} ``<br>with `` x = datetime(...) `` | `` 2026-11-22T12:00:00+03:00 `` |
| `datetime.microsecond` | attribute | The microsecond. | `` {{ x \| datetime.microsecond }} ``<br>with `` x = datetime.datetime(2026, 11, 22, 14, 30, 5, 250) `` | `` 250 `` |
| `datetime.minute` | attribute | The minute. | `` {{ x \| datetime.minute }} ``<br>with `` x = datetime.datetime(2026, 11, 22, 14, 30, 5, 250) `` | `` 30 `` |
| `datetime.replace(year, month, day, hour, minute, second, microsecond, tzinfo, fold)` | filter | Return the datetime with the given fields replaced. `tzinfo=none` makes it naive. | `` {{ x \| datetime.replace(hour=9, microsecond=0) }} ``<br>with `` x = datetime.datetime(2026, 11, 22, 14, 30, 5, 250) `` | `` 2026-11-22 09:30:05 `` |
|  |  |  | `` {{ x \| datetime.replace(tzinfo=none) }} ``<br>with `` x = datetime(...) `` | `` 2026-11-22 12:00:00 `` |
| `datetime.second` | attribute | The second. | `` {{ x \| datetime.second }} ``<br>with `` x = datetime.datetime(2026, 11, 22, 14, 30, 5, 250) `` | `` 5 `` |
| `datetime.strptime(format)` | filter | Parse a string with a `strptime` format (classmethod; the string is piped in). | `` {{ '22/11/2026 14:30' \| datetime.strptime('%d/%m/%Y %H:%M') }} `` | `` 2026-11-22 14:30:00 `` |
| `datetime.time` | filter | Return the time part, without the timezone. | `` {{ x \| datetime.time }} ``<br>with `` x = datetime.datetime(2026, 11, 22, 14, 30, 5, 250) `` | `` 14:30:05.000250 `` |
| `datetime.timestamp` | filter | Return the POSIX timestamp. Naive values are taken as local time. | `` {{ x \| datetime.timestamp }} ``<br>with `` x = datetime.datetime(2026, 11, 22, 12, 0, tzinfo=datetime.timezone.utc) `` | `` 1795348800.0 `` |
| `datetime.timetuple` | filter | Return a `time.struct_time`. | `` {{ x \| datetime.timetuple \| list }} ``<br>with `` x = datetime.datetime(2026, 11, 22, 14, 30, 5, 250) `` | `` [2026, 11, 22, 14, 30, 5, 6, 326, -1] `` |
| `datetime.timetz` | filter | Return the time part, with the timezone. | `` {{ x \| datetime.timetz }} ``<br>with `` x = datetime(...) `` | `` 12:00:00+03:00 `` |
| `datetime.tzinfo` | attribute | The timezone, or None for a naive datetime. | `` {{ x \| datetime.tzinfo }} ``<br>with `` x = datetime.datetime(2026, 11, 22, 12, 0, tzinfo=datetime.timezone.utc) `` | `` UTC `` |
| `datetime.tzname` | filter | Return the timezone name, or None for a naive datetime. | `` {{ x \| datetime.tzname }} ``<br>with `` x = datetime(...) `` | `` UTC+03:00 `` |
| `datetime.utcoffset` | filter | Return the UTC offset, or None for a naive datetime. | `` {{ x \| datetime.utcoffset }} ``<br>with `` x = datetime(...) `` | `` 3:00:00 `` |
|  |  |  | `` {{ x \| datetime.utcoffset }} ``<br>with `` x = datetime.datetime(2026, 11, 22, 14, 30, 5, 250) `` | `` None `` |
| `datetime.utctimetuple` | filter | Return a `time.struct_time` in UTC. | `` {{ x \| datetime.utctimetuple \| list }} ``<br>with `` x = datetime(...) `` | `` [2026, 11, 22, 9, 0, 0, 6, 326, 0] `` |

### decimal

| Member | Kinds | Description | Example | Result |
|---|---|---|---|---|
| `decimal.adjusted` | filter | Return the exponent of the most significant digit. | `` {{ x \| decimal.adjusted }} ``<br>with `` x = Decimal('123.45') `` | `` 2 `` |
| `decimal.as_integer_ratio` | filter | Return the exact ratio `(numerator, denominator)`. | `` {{ x \| decimal.as_integer_ratio \| join('/') }} ``<br>with `` x = Decimal('1.25') `` | `` 5/4 `` |
| `decimal.as_tuple` | filter | Return `(sign, digits, exponent)`. | `` {{ x \| decimal.as_tuple }} ``<br>with `` x = Decimal('-1.5') `` | `` DecimalTuple(sign=1, digits=(1, 5), exponent=-1) `` |
| `decimal.canonical` | filter | Return the canonical encoding (the value itself). | `` {{ x \| decimal.canonical }} ``<br>with `` x = Decimal('1.50') `` | `` 1.50 `` |
| `decimal.compare(other, context)` | filter | Compare numerically: -1, 0 or 1 (NaN if either is NaN). | `` {{ x \| decimal.compare(2) }} ``<br>with `` x = Decimal('1.5') `` | `` -1 `` |
|  |  |  | `` {{ x \| decimal.compare(y) }} ``<br>with `` x = Decimal('1.50'), y = Decimal('1.5') `` | `` 0 `` |
| `decimal.compare_signal(other, context)` | filter | Like `compare`, but signal on any NaN. | `` {{ x \| decimal.compare_signal(1) }} ``<br>with `` x = Decimal('2') `` | `` 1 `` |
| `decimal.compare_total(other, context)` | filter | Compare by abstract representation (1.50 sorts before 1.5). | `` {{ x \| decimal.compare_total(y) }} ``<br>with `` x = Decimal('1.50'), y = Decimal('1.5') `` | `` -1 `` |
| `decimal.compare_total_mag(other, context)` | filter | Like `compare_total`, ignoring signs. | `` {{ x \| decimal.compare_total_mag(1) }} ``<br>with `` x = Decimal('-1') `` | `` 0 `` |
| `decimal.conjugate` | filter | Return the complex conjugate (the value itself). | `` {{ x \| decimal.conjugate }} ``<br>with `` x = Decimal('2.5') `` | `` 2.5 `` |
| `decimal.copy_abs` | filter | Return the absolute value, without rounding. | `` {{ x \| decimal.copy_abs }} ``<br>with `` x = Decimal('-2.5') `` | `` 2.5 `` |
| `decimal.copy_negate` | filter | Return the negated value, without rounding. | `` {{ x \| decimal.copy_negate }} ``<br>with `` x = Decimal('2.5') `` | `` -2.5 `` |
| `decimal.copy_sign(other, context)` | filter | Return the value with the sign of `other`. | `` {{ x \| decimal.copy_sign(-1) }} ``<br>with `` x = Decimal('2.5') `` | `` -2.5 `` |
| `decimal.exp(context)` | filter | Return e raised to the value. | `` {{ x \| decimal.exp }} ``<br>with `` x = Decimal('1') `` | `` 2.718281828459045235360287471 `` |
|  |  |  | `` {{ x \| decimal.exp(decimal.Context(prec=5)) }} ``<br>with `` x = Decimal('1') `` | `` 2.7183 `` |
| `decimal.fma(other, third, context)` | filter | Fused multiply-add: `value * other + third`, rounded once. | `` {{ x \| decimal.fma(3, 1) }} ``<br>with `` x = Decimal('2') `` | `` 7 `` |
| `decimal.from_float` | filter | Return the exact Decimal for a float (classmethod; the float is piped in). | `` {{ 0.5 \| decimal.from_float }} `` | `` 0.5 `` |
| `decimal.imag` | attribute | The imaginary part (always 0). | `` {{ x \| decimal.imag }} ``<br>with `` x = Decimal('2.5') `` | `` 0 `` |
| `decimal.is_canonical` | filter, test | Return True (Decimals are always canonical). | `` {{ x \| decimal.is_canonical }} ``<br>with `` x = Decimal('1') `` | `` True `` |
| `decimal.is_finite` | filter, test | Return True if the value is neither infinite nor NaN. | `` {{ x \| decimal.is_finite }} ``<br>with `` x = Decimal('1') `` | `` True `` |
|  |  |  | `` {{ x is decimal.is_finite }} ``<br>with `` x = Decimal('Infinity') `` | `` False `` |
| `decimal.is_infinite` | filter, test | Return True if the value is infinite. | `` {{ x \| decimal.is_infinite }} ``<br>with `` x = Decimal('-Infinity') `` | `` True `` |
| `decimal.is_nan` | filter, test | Return True if the value is a NaN (quiet or signalling). | `` {{ x \| decimal.is_nan }} ``<br>with `` x = Decimal('NaN') `` | `` True `` |
| `decimal.is_normal(context)` | filter, test | Return True if the value is a normal finite non-zero number. | `` {{ x \| decimal.is_normal }} ``<br>with `` x = Decimal('1.5') `` | `` True `` |
| `decimal.is_qnan` | filter, test | Return True if the value is a quiet NaN. | `` {{ x \| decimal.is_qnan }} ``<br>with `` x = Decimal('NaN') `` | `` True `` |
| `decimal.is_signed` | filter, test | Return True if the sign is negative (including -0). | `` {{ x \| decimal.is_signed }} ``<br>with `` x = Decimal('-1') `` | `` True `` |
|  |  |  | `` {{ x is decimal.is_signed }} ``<br>with `` x = Decimal('-0') `` | `` True `` |
| `decimal.is_snan` | filter, test | Return True if the value is a signalling NaN. | `` {{ x \| decimal.is_snan }} ``<br>with `` x = Decimal('sNaN') `` | `` True `` |
| `decimal.is_subnormal(context)` | filter, test | Return True if the value is subnormal. | `` {{ x \| decimal.is_subnormal }} ``<br>with `` x = Decimal('1E-999999999') `` | `` True `` |
| `decimal.is_zero` | filter, test | Return True if the value is zero (of either sign). | `` {{ x \| decimal.is_zero }} ``<br>with `` x = Decimal('0.00') `` | `` True `` |
| `decimal.ln(context)` | filter | Return the natural logarithm. | `` {{ x \| decimal.ln(decimal.Context(prec=5)) }} ``<br>with `` x = Decimal('10') `` | `` 2.3026 `` |
| `decimal.log10(context)` | filter | Return the base-10 logarithm. | `` {{ x \| decimal.log10 }} ``<br>with `` x = Decimal('1000') `` | `` 3 `` |
| `decimal.logb(context)` | filter | Return the adjusted exponent as a Decimal. | `` {{ x \| decimal.logb }} ``<br>with `` x = Decimal('250') `` | `` 2 `` |
| `decimal.logical_and(other, context)` | filter | Digit-wise AND of two logical operands. | `` {{ x \| decimal.logical_and(1010) }} ``<br>with `` x = Decimal('1100') `` | `` 1000 `` |
| `decimal.logical_invert(context)` | filter | Digit-wise inversion of a logical operand, to the context precision. | `` {{ x \| decimal.logical_invert(decimal.Context(prec=4)) }} ``<br>with `` x = Decimal('1100') `` | `` 11 `` |
| `decimal.logical_or(other, context)` | filter | Digit-wise OR of two logical operands. | `` {{ x \| decimal.logical_or(1010) }} ``<br>with `` x = Decimal('1100') `` | `` 1110 `` |
| `decimal.logical_xor(other, context)` | filter | Digit-wise XOR of two logical operands. | `` {{ x \| decimal.logical_xor(1010) }} ``<br>with `` x = Decimal('1100') `` | `` 110 `` |
| `decimal.max(other, context)` | filter | Return the larger of the value and `other`. | `` {{ x \| decimal.max(3) }} ``<br>with `` x = Decimal('2.5') `` | `` 3 `` |
| `decimal.max_mag(other, context)` | filter | Return the one with the larger absolute value. | `` {{ x \| decimal.max_mag(2) }} ``<br>with `` x = Decimal('-3') `` | `` -3 `` |
| `decimal.min(other, context)` | filter | Return the smaller of the value and `other`. | `` {{ x \| decimal.min(3) }} ``<br>with `` x = Decimal('2.5') `` | `` 2.5 `` |
| `decimal.min_mag(other, context)` | filter | Return the one with the smaller absolute value. | `` {{ x \| decimal.min_mag(2) }} ``<br>with `` x = Decimal('-3') `` | `` 2 `` |
| `decimal.next_minus(context)` | filter | Return the largest representable number smaller than the value. | `` {{ x \| decimal.next_minus(decimal.Context(prec=3)) }} ``<br>with `` x = Decimal('1') `` | `` 0.999 `` |
| `decimal.next_plus(context)` | filter | Return the smallest representable number larger than the value. | `` {{ x \| decimal.next_plus }} ``<br>with `` x = Decimal('1') `` | `` 1.000000000000000000000000001 `` |
| `decimal.next_toward(other, context)` | filter | Return the next representable number toward `other`. | `` {{ x \| decimal.next_toward(0, decimal.Context(prec=3)) }} ``<br>with `` x = Decimal('1') `` | `` 0.999 `` |
| `decimal.normalize(context)` | filter | Strip trailing zeros (and use exponent form where needed). | `` {{ x \| decimal.normalize }} ``<br>with `` x = Decimal('120.00') `` | `` 1.2E+2 `` |
| `decimal.number_class(context)` | filter | Return the class of the number, such as `+Normal` or `-Zero`. | `` {{ x \| decimal.number_class }} ``<br>with `` x = Decimal('-1.5') `` | `` -Normal `` |
| `decimal.quantize(exp, rounding, context)` | filter | Round to the exponent of `exp` (`decimal.Decimal('0.01')` gives two places). | `` {{ x \| decimal.quantize(decimal.Decimal('0.01')) }} ``<br>with `` x = Decimal('1.005') `` | `` 1.00 `` |
|  |  |  | `` {{ x \| decimal.quantize(decimal.Decimal('0.01'), rounding=decimal.ROUND_HALF_UP) \| fmt(',.2f') }} ``<br>with `` x = Decimal('1500.005') `` | `` 1,500.01 `` |
| `decimal.radix` | filter | Return 10, the radix of Decimal arithmetic. | `` {{ x \| decimal.radix }} ``<br>with `` x = Decimal('1') `` | `` 10 `` |
| `decimal.real` | attribute | The real part (the value itself). | `` {{ x \| decimal.real }} ``<br>with `` x = Decimal('2.5') `` | `` 2.5 `` |
| `decimal.remainder_near(other, context)` | filter | Return the remainder of dividing by `other`, choosing the quotient nearest to exact. | `` {{ x \| decimal.remainder_near(3) }} ``<br>with `` x = Decimal('10') `` | `` 1 `` |
| `decimal.rotate(other, context)` | filter | Rotate the digits by `other` places, to the context precision. | `` {{ x \| decimal.rotate(1, decimal.Context(prec=4)) }} ``<br>with `` x = Decimal('1234') `` | `` 2341 `` |
| `decimal.same_quantum(other, context)` | filter, test | Return True if both have the same exponent. | `` {{ x \| decimal.same_quantum(y) }} ``<br>with `` x = Decimal('1.10'), y = Decimal('2.25') `` | `` True `` |
|  |  |  | `` {{ x is decimal.same_quantum(1) }} ``<br>with `` x = Decimal('1.1') `` | `` False `` |
| `decimal.scaleb(other, context)` | filter | Return the value with its exponent adjusted by `other`. | `` {{ x \| decimal.scaleb(2) }} ``<br>with `` x = Decimal('1.5') `` | `` 1.5E+2 `` |
| `decimal.shift(other, context)` | filter | Shift the digits by `other` places, to the context precision. | `` {{ x \| decimal.shift(1, decimal.Context(prec=4)) }} ``<br>with `` x = Decimal('1234') `` | `` 2340 `` |
| `decimal.sqrt(context)` | filter | Return the square root, to the context precision. | `` {{ x \| decimal.sqrt }} ``<br>with `` x = Decimal('2') `` | `` 1.414213562373095048801688724 `` |
| `decimal.to_eng_string(context)` | filter | Return engineering notation (exponent a multiple of 3). | `` {{ x \| decimal.to_eng_string }} ``<br>with `` x = Decimal('1.23E+5') `` | `` 123E+3 `` |
| `decimal.to_integral(rounding, context)` | filter | Round to an integer (same as `to_integral_value`). | `` {{ x \| decimal.to_integral }} ``<br>with `` x = Decimal('2.5') `` | `` 2 `` |
|  |  |  | `` {{ x \| decimal.to_integral(decimal.ROUND_HALF_UP) }} ``<br>with `` x = Decimal('2.5') `` | `` 3 `` |
| `decimal.to_integral_exact(rounding, context)` | filter | Round to an integer, signalling Inexact and Rounded when it changes. | `` {{ x \| decimal.to_integral_exact }} ``<br>with `` x = Decimal('3.7') `` | `` 4 `` |
| `decimal.to_integral_value(rounding, context)` | filter | Round to an integer without signalling Inexact or Rounded. | `` {{ x \| decimal.to_integral_value(rounding=decimal.ROUND_FLOOR) }} ``<br>with `` x = Decimal('-3.2') `` | `` -4 `` |

### dict

| Member | Kinds | Description | Example | Result |
|---|---|---|---|---|
| `dict.clear` | filter | Return an empty dict. | `` {{ prices \| dict.clear }} ``<br>with `` prices = {'tea': 2, 'coffee': 3} `` | `` {} `` |
| `dict.copy` | filter | Return a shallow copy. | `` {{ prices \| dict.copy \| dict.items \| map('join', '=') \| join('\|') }} ``<br>with `` prices = {'tea': 2, 'coffee': 3} `` | `` tea=2\|coffee=3 `` |
| `dict.fromkeys(v)` | filter | Return a dict with the piped keys, all set to `v` (classmethod; the keys are piped in). | `` {{ ['a', 'b'] \| dict.fromkeys(0) \| dict.items \| map('join', '=') \| join('\|') }} `` | `` a=0\|b=0 `` |
|  |  |  | `` {{ 'ab' \| dict.fromkeys \| dict.items \| map('join', '=') \| join('\|') }} `` | `` a=None\|b=None `` |
| `dict.get(key, default)` | filter | Return the value for `key`, or `default`. | `` {{ prices \| dict.get('tea') }} ``<br>with `` prices = {'tea': 2, 'coffee': 3} `` | `` 2 `` |
|  |  |  | `` {{ prices \| dict.get('milk', 0) }} ``<br>with `` prices = {'tea': 2, 'coffee': 3} `` | `` 0 `` |
|  |  |  | `` {{ prices \| dict.get('milk') }} ``<br>with `` prices = {'tea': 2, 'coffee': 3} `` | `` None `` |
| `dict.items` | filter | Return a view of the `(key, value)` pairs. | `` {{ prices \| dict.items \| map('join', '=') \| join('\|') }} ``<br>with `` prices = {'tea': 2, 'coffee': 3} `` | `` tea=2\|coffee=3 `` |
| `dict.keys` | filter | Return a view of the keys. | `` {{ prices \| dict.keys \| join('\|') }} ``<br>with `` prices = {'tea': 2, 'coffee': 3} `` | `` tea\|coffee `` |
| `dict.pop(key, *default)` | filter | Return the value for `key` (or `default`; raises without one). The input keeps it. | `` {{ prices \| dict.pop('tea') }} ``<br>with `` prices = {'tea': 2, 'coffee': 3} `` | `` 2 `` |
|  |  |  | `` {{ prices \| dict.pop('milk', 0) }} ``<br>with `` prices = {'tea': 2, 'coffee': 3} `` | `` 0 `` |
| `dict.popitem` | filter | Return the last `(key, value)` pair. The input keeps it. | `` {{ prices \| dict.popitem \| join('=') }} ``<br>with `` prices = {'tea': 2, 'coffee': 3} `` | `` coffee=3 `` |
| `dict.setdefault(key, default)` | filter | Return the value for `key`, or `default` if missing. The input is unchanged. | `` {{ prices \| dict.setdefault('tea', 9) }} ``<br>with `` prices = {'tea': 2, 'coffee': 3} `` | `` 2 `` |
|  |  |  | `` {{ prices \| dict.setdefault('milk', 9) }} ``<br>with `` prices = {'tea': 2, 'coffee': 3} `` | `` 9 `` |
| `dict.update(other, **kwargs)` | filter | Return a copy updated from `other` and keyword arguments. | `` {{ prices \| dict.update({'tea': 1}) \| dict.items \| map('join', '=') \| join('\|') }} ``<br>with `` prices = {'tea': 2, 'coffee': 3} `` | `` tea=1\|coffee=3 `` |
|  |  |  | `` {{ prices \| dict.update([('milk', 1)], tea=4) \| dict.items \| map('join', '=') \| join('\|') }} ``<br>with `` prices = {'tea': 2, 'coffee': 3} `` | `` tea=4\|coffee=3\|milk=1 `` |
| `dict.values` | filter | Return a view of the values. | `` {{ prices \| dict.values \| sum }} ``<br>with `` prices = {'tea': 2, 'coffee': 3} `` | `` 5 `` |

### float

| Member | Kinds | Description | Example | Result |
|---|---|---|---|---|
| `float.as_integer_ratio` | filter | Return the exact ratio `(numerator, denominator)`. | `` {{ 0.75 \| float.as_integer_ratio \| join('/') }} `` | `` 3/4 `` |
| `float.conjugate` | filter | Return the complex conjugate (the value itself). | `` {{ 2.5 \| float.conjugate }} `` | `` 2.5 `` |
| `float.fromhex` | filter | Parse a hexadecimal float string (classmethod; the string is piped in). | `` {{ '0x1.8p1' \| float.fromhex }} `` | `` 3.0 `` |
| `float.hex` | filter | Return the hexadecimal representation. | `` {{ 3.0 \| float.hex }} `` | `` 0x1.8000000000000p+1 `` |
| `float.imag` | attribute | The imaginary part (always 0.0). | `` {{ 2.5 \| float.imag }} `` | `` 0.0 `` |
| `float.is_integer` | filter, test | Return True if the float has no fractional part. | `` {{ 2.0 \| float.is_integer }} `` | `` True `` |
|  |  |  | `` {{ 2.5 is float.is_integer }} `` | `` False `` |
| `float.real` | attribute | The real part (the value itself). | `` {{ 2.5 \| float.real }} `` | `` 2.5 `` |

### fraction

| Member | Kinds | Description | Example | Result |
|---|---|---|---|---|
| `fraction.as_integer_ratio` | filter | Return `(numerator, denominator)`. | `` {{ x \| fraction.as_integer_ratio \| join('/') }} ``<br>with `` x = Fraction(1, 3) `` | `` 1/3 `` |
| `fraction.conjugate` | filter | Return the complex conjugate (the value itself). | `` {{ x \| fraction.conjugate }} ``<br>with `` x = Fraction(1, 3) `` | `` 1/3 `` |
| `fraction.denominator` | attribute | The denominator, in lowest terms. | `` {{ x \| fraction.denominator }} ``<br>with `` x = Fraction(3, 2) `` | `` 2 `` |
| `fraction.from_decimal` | filter | Return the exact fraction for a Decimal (classmethod; the Decimal is piped in). | `` {{ x \| fraction.from_decimal }} ``<br>with `` x = Decimal('1.25') `` | `` 5/4 `` |
| `fraction.from_float` | filter | Return the exact fraction for a float (classmethod; the float is piped in). | `` {{ 0.5 \| fraction.from_float }} `` | `` 1/2 `` |
| `fraction.imag` | attribute | The imaginary part (always 0). | `` {{ x \| fraction.imag }} ``<br>with `` x = Fraction(1, 3) `` | `` 0 `` |
| `fraction.is_integer` | filter, test | Return True if the fraction is a whole number. | `` {{ x \| fraction.is_integer }} ``<br>with `` x = Fraction(2, 1) `` | `` True `` |
|  |  |  | `` {{ x is fraction.is_integer }} ``<br>with `` x = Fraction(1, 3) `` | `` False `` |
| `fraction.limit_denominator(max_denominator)` | filter | Return the closest fraction with a denominator of at most `max_denominator`. | `` {{ x \| fraction.limit_denominator(10) }} ``<br>with `` x = Fraction(3141592653589793, 1000000000000000) `` | `` 22/7 `` |
|  |  |  | `` {{ x \| fraction.limit_denominator }} ``<br>with `` x = Fraction(3141592653589793, 1000000000000000) `` | `` 3126535/995207 `` |
| `fraction.numerator` | attribute | The numerator, in lowest terms. | `` {{ x \| fraction.numerator }} ``<br>with `` x = Fraction(3, 2) `` | `` 3 `` |
| `fraction.real` | attribute | The real part (the value itself). | `` {{ x \| fraction.real }} ``<br>with `` x = Fraction(1, 3) `` | `` 1/3 `` |

### helpers

| Member | Kinds | Description | Example | Result |
|---|---|---|---|---|
| `decimal` | global | The `decimal` namespace object. | `` {{ decimal.Decimal('1.10') }} `` | `` 1.10 `` |
|  |  |  | `` {{ decimal.ROUND_HALF_UP }} `` | `` ROUND_HALF_UP `` |
| `fmt(spec)` | filter | Return `format(value, spec)`; works for numbers, Decimal and dates. | `` {{ x \| fmt(',.2f') }} ``<br>with `` x = 1500.5 `` | `` 1,500.50 `` |
|  |  |  | `` {{ d \| fmt('%d/%m/%Y') }} ``<br>with `` d = datetime.date(2026, 1, 5) `` | `` 05/01/2026 `` |
| `now(tz)` | global | Return the current datetime, local or in `tz` (a `tzinfo`). | `` {{ now().tzinfo }} `` | `` None `` |
|  |  |  | `` {{ now(tz).utcoffset() }} ``<br>with `` tz = datetime.timezone.utc `` | `` 0:00:00 `` |
| `random` | global | The `random` object; `random.Random(seed)` gives a repeatable generator. | `` {{ random.random() < 1 }} `` | `` True `` |
|  |  |  | `` {{ random.Random(42).randint(1, 6) }} `` | `` 6 `` |
|  |  |  | `` {{ random.Random(42).choice(['a', 'b', 'c']) }} `` | `` c `` |
|  |  |  | `` {{ random.Random(42).shuffle([1, 2, 3, 4]) \| join }} `` | `` 3241 `` |
|  |  |  | `` {{ random.Random(42).sample(range(10), 3) \| join }} `` | `` 104 `` |
| `re` | global | The `re` flags object, with `re.compile(pattern, flags=0)` for the `pattern` namespace. | `` {{ re.I == 2 and re.IGNORECASE == re.I }} `` | `` True `` |
|  |  |  | `` {{ re.compile('a+', re.I) \| pattern.findall('aAb') \| join }} `` | `` aA `` |
| `secrets` | global | The `secrets` object: cryptographically strong tokens and choices. | `` {{ secrets.token_hex(8) \| length }} `` | `` 16 `` |
|  |  |  | `` {{ secrets.randbelow(3) < 3 }} `` | `` True `` |
| `to_bool` | filter | Convert strictly: true/yes/on/1 or false/no/off/0 (any case), bools, and ints 0 or 1. | `` {{ 'Yes' \| to_bool }} `` | `` True `` |
|  |  |  | `` {{ 'off' \| to_bool }} `` | `` False `` |
|  |  |  | `` {{ 1 \| to_bool }} `` | `` True `` |
| `to_date(format)` | filter | Parse an ISO date, or use `format` with `strptime`. A datetime gives its date. | `` {{ '2026-01-05' \| to_date \| fmt('%A') }} `` | `` Monday `` |
|  |  |  | `` {{ '05/01/2026' \| to_date(format='%d/%m/%Y') \| fmt('%A') }} `` | `` Monday `` |
|  |  |  | `` {{ d \| to_date }} ``<br>with `` d = datetime.datetime(2026, 1, 5, 9, 30) `` | `` 2026-01-05 `` |
| `to_datetime(format)` | filter | Parse an ISO datetime, or use `format` with `strptime`. A date becomes midnight. | `` {{ '2026-01-05T09:30' \| to_datetime \| fmt('%H:%M') }} `` | `` 09:30 `` |
|  |  |  | `` {{ '05/01/2026 9:30' \| to_datetime(format='%d/%m/%Y %H:%M') }} `` | `` 2026-01-05 09:30:00 `` |
|  |  |  | `` {{ d \| to_datetime }} ``<br>with `` d = datetime.date(2026, 1, 5) `` | `` 2026-01-05 00:00:00 `` |
| `to_decimal` | filter | Convert to `Decimal`. Floats go through `repr()`, so `0.1` gives `Decimal('0.1')`. | `` {{ '1500.5' \| to_decimal \| fmt(',.2f') }} `` | `` 1,500.50 `` |
|  |  |  | `` {{ 0.1 \| to_decimal }} `` | `` 0.1 `` |
| `to_float` | filter | Convert to `float`. | `` {{ '2.5' \| to_float * 2 }} `` | `` 5.0 `` |
| `to_fraction` | filter | Convert to `Fraction` (`'3/4'`, `'0.75'`, numbers). | `` {{ '3/4' \| to_fraction + 1 }} `` | `` 7/4 `` |
|  |  |  | `` {{ 0.5 \| to_fraction }} `` | `` 1/2 `` |
| `to_int(base)` | filter | Convert to `int`. `base` applies to strings; numbers are truncated like `int()`. | `` {{ '42' \| to_int + 1 }} `` | `` 43 `` |
|  |  |  | `` {{ 'ff' \| to_int(16) }} `` | `` 255 `` |
|  |  |  | `` {{ 3.9 \| to_int }} `` | `` 3 `` |
| `to_path` | filter | Convert to a `PurePath` (never touches the disk). | `` {{ 'docs/readme.md' \| to_path \| path.as_posix }} `` | `` docs/readme.md `` |
| `to_str` | filter | Return `str(value)`. | `` {{ x \| to_str }} ``<br>with `` x = Decimal('1.50') `` | `` 1.50 `` |
| `to_time(format)` | filter | Parse an ISO time, or use `format` with `strptime`. A datetime gives its time (with tz). | `` {{ '09:30' \| to_time }} `` | `` 09:30:00 `` |
|  |  |  | `` {{ '9.30 PM' \| to_time(format='%I.%M %p') }} `` | `` 21:30:00 `` |
|  |  |  | `` {{ d \| to_time }} ``<br>with `` d = datetime.datetime(2026, 1, 5, 9, 30) `` | `` 09:30:00 `` |
| `to_timedelta(days, hours, minutes)` | filter | Convert seconds (or `str(timedelta)` text) to a timedelta, plus `days`/`hours`/`minutes`. | `` {{ 90 \| to_timedelta }} `` | `` 0:01:30 `` |
|  |  |  | `` {{ 0 \| to_timedelta(days=2, hours=3) }} `` | `` 2 days, 3:00:00 `` |
|  |  |  | `` {{ '1 day, 2:30:00' \| to_timedelta }} `` | `` 1 day, 2:30:00 `` |
| `to_uuid` | filter | Convert to `UUID`. | `` {{ '12345678-1234-5678-1234-567812345678' \| to_uuid }} `` | `` 12345678-1234-5678-1234-567812345678 `` |
| `today()` | global | Return today's local date. | `` {{ today().year > 2000 }} `` | `` True `` |
| `uuid1(node, clock_seq)` | global | Return a time-based UUID; without `node`, a random node id is used, never the MAC. | `` {{ uuid1() \| uuid.version }} `` | `` 1 `` |
|  |  |  | `` {{ uuid1(node=1) \| uuid.node }} `` | `` 1 `` |
| `uuid4()` | global | Return a random UUID (different on every call). | `` {{ uuid4() \| uuid.version }} `` | `` 4 `` |
| `uuid5(namespace, name)` | global | Return the name-based (SHA-1) UUID; same input, same UUID. `namespace` may be UUID text. | `` {{ uuid5('6ba7b810-9dad-11d1-80b4-00c04fd430c8', 'example.com') }} `` | `` cfbff0d1-9375-5685-968c-48ce8b15ae17 `` |
|  |  |  | `` {{ uuid5(ns, 'example.com') \| uuid.version }} ``<br>with `` ns = UUID('6ba7b810-9dad-11d1-80b4-00c04fd430c8') `` | `` 5 `` |

### int

| Member | Kinds | Description | Example | Result |
|---|---|---|---|---|
| `int.as_integer_ratio` | filter | Return `(value, 1)`. | `` {{ 5 \| int.as_integer_ratio \| join('/') }} `` | `` 5/1 `` |
| `int.bit_count` | filter | Return the number of ones in the binary form of the absolute value. | `` {{ 255 \| int.bit_count }} `` | `` 8 `` |
| `int.bit_length` | filter | Return the number of bits needed to represent the value, without sign. | `` {{ 255 \| int.bit_length }} `` | `` 8 `` |
| `int.conjugate` | filter | Return the complex conjugate (the value itself). | `` {{ 5 \| int.conjugate }} `` | `` 5 `` |
| `int.denominator` | attribute | The denominator (always 1). | `` {{ 5 \| int.denominator }} `` | `` 1 `` |
| `int.from_bytes(byteorder, signed)` | filter | Return the integer represented by the bytes (classmethod; the bytes are piped in). | `` {{ [4, 0] \| int.from_bytes }} `` | `` 1024 `` |
|  |  |  | `` {{ [255] \| int.from_bytes(signed=True) }} `` | `` -1 `` |
|  |  |  | `` {{ data \| int.from_bytes('little') }} ``<br>with `` data = b'\x00\x04' `` | `` 1024 `` |
| `int.imag` | attribute | The imaginary part (always 0). | `` {{ 5 \| int.imag }} `` | `` 0 `` |
| `int.is_integer` | filter, test | Return True (for duck-type compatibility with float). | `` {{ 5 \| int.is_integer }} `` | `` True `` |
| `int.numerator` | attribute | The numerator (the value itself). | `` {{ 5 \| int.numerator }} `` | `` 5 `` |
| `int.real` | attribute | The real part (the value itself, as an int). | `` {{ 5 \| int.real }} `` | `` 5 `` |
|  |  |  | `` {{ true \| int.real }} `` | `` 1 `` |
| `int.to_bytes(length, byteorder, signed)` | filter | Return the bytes representing the value. | `` {{ 1024 \| int.to_bytes(2) \| list }} `` | `` [4, 0] `` |
|  |  |  | `` {{ 1024 \| int.to_bytes(2, 'little') \| list }} `` | `` [0, 4] `` |
|  |  |  | `` {{ -1 \| int.to_bytes(1, signed=True) \| list }} `` | `` [255] `` |

### list

| Member | Kinds | Description | Example | Result |
|---|---|---|---|---|
| `list.append(x)` | filter | Return a copy with `x` added at the end. | `` {{ xs \| list.append(4) }} ``<br>with `` xs = [3, 1, 2] `` | `` [3, 1, 2, 4] `` |
| `list.clear` | filter | Return an empty list. | `` {{ xs \| list.clear }} ``<br>with `` xs = [3, 1, 2] `` | `` [] `` |
| `list.copy` | filter | Return a shallow copy. | `` {{ xs \| list.copy }} ``<br>with `` xs = [3, 1, 2] `` | `` [3, 1, 2] `` |
| `list.count(x)` | filter | Return how many items equal `x`. | `` {{ [1, 2, 2] \| list.count(2) }} `` | `` 2 `` |
| `list.extend(iterable)` | filter | Return a copy with the items of `iterable` added at the end. | `` {{ xs \| list.extend([4, 5]) }} ``<br>with `` xs = [3, 1, 2] `` | `` [3, 1, 2, 4, 5] `` |
| `list.index(x, start, stop)` | filter | Return the position of the first `x` (between `start` and `stop`). | `` {{ xs \| list.index(2) }} ``<br>with `` xs = [3, 1, 2] `` | `` 2 `` |
|  |  |  | `` {{ [1, 2, 1] \| list.index(1, 1) }} `` | `` 2 `` |
| `list.insert(index, x)` | filter | Return a copy with `x` inserted before `index`. | `` {{ xs \| list.insert(0, 9) }} ``<br>with `` xs = [3, 1, 2] `` | `` [9, 3, 1, 2] `` |
|  |  |  | `` {{ xs \| list.insert(-1, 9) }} ``<br>with `` xs = [3, 1, 2] `` | `` [3, 1, 9, 2] `` |
| `list.pop(index)` | filter | Return the item at `index` (the last by default). The input keeps it. | `` {{ xs \| list.pop }} ``<br>with `` xs = [3, 1, 2] `` | `` 2 `` |
|  |  |  | `` {{ xs \| list.pop(0) }} ``<br>with `` xs = [3, 1, 2] `` | `` 3 `` |
| `list.remove(x)` | filter | Return a copy without the first `x`. Raises if `x` is missing. | `` {{ [1, 2, 1] \| list.remove(1) }} `` | `` [2, 1] `` |
| `list.reverse` | filter | Return a reversed copy. | `` {{ xs \| list.reverse }} ``<br>with `` xs = [3, 1, 2] `` | `` [2, 1, 3] `` |
| `list.sort(key, reverse)` | filter | Return a sorted copy. `key` is a macro or an attribute name (a macro's result is text). | `` {{ xs \| list.sort }} ``<br>with `` xs = [3, 1, 2] `` | `` [1, 2, 3] `` |
|  |  |  | `` {{ xs \| list.sort(reverse=true) }} ``<br>with `` xs = [3, 1, 2] `` | `` [3, 2, 1] `` |
|  |  |  | `` {{ people \| list.sort(key='name') \| map(attribute='age') \| join('\|') }} ``<br>with `` people = [{'name': 'Sara', 'age': 31}, {'name': 'Adam', 'age': 25}] `` | `` 25\|31 `` |
|  |  |  | `` {% macro age(p) %}{{ p.age }}{% endmacro %}{{ people \| list.sort(key=age) \| map(attribute='name') \| join('\|') }} ``<br>with `` people = [{'name': 'Sara', 'age': 31}, {'name': 'Adam', 'age': 25}] `` | `` Adam\|Sara `` |

### match

| Member | Kinds | Description | Example | Result |
|---|---|---|---|---|
| `match.end(group)` | filter | Return the end index of a group. | `` {{ '2026-11' \| re.search('(?P<year>\\d+)-(?P<month>\\d+)-?(\\d+)?') \| match.end(1) }} `` | `` 4 `` |
| `match.endpos` | attribute | The `endpos` the search stopped at. | `` {{ '2026-11' \| re.search('(?P<year>\\d+)-(?P<month>\\d+)-?(\\d+)?') \| match.endpos }} `` | `` 7 `` |
| `match.expand(template)` | filter | Fill a `re.sub` style template (`\1`, `\g<name>`) from this match. | `` {{ '2026-11' \| re.search('(?P<year>\\d+)-(?P<month>\\d+)-?(\\d+)?') \| match.expand('\\2/\\g<year>') }} `` | `` 11/2026 `` |
| `match.group(*groups)` | filter | Return one group (by number or name; 0 or nothing is the whole match), or a tuple. | `` {{ '2026-11' \| re.search('(?P<year>\\d+)-(?P<month>\\d+)-?(\\d+)?') \| match.group }} `` | `` 2026-11 `` |
|  |  |  | `` {{ '2026-11' \| re.search('(?P<year>\\d+)-(?P<month>\\d+)-?(\\d+)?') \| match.group('month') }} `` | `` 11 `` |
|  |  |  | `` {{ '2026-11' \| re.search('(?P<year>\\d+)-(?P<month>\\d+)-?(\\d+)?') \| match.group(1, 2) \| join('\|') }} `` | `` 2026\|11 `` |
| `match.groupdict(default)` | filter | Return the named groups as a dict. | `` {{ '2026-11' \| re.search('(?P<year>\\d+)-(?P<month>\\d+)-?(\\d+)?') \| match.groupdict \| dictsort \| map('join', '=') \| join('\|') }} `` | `` month=11\|year=2026 `` |
| `match.groups(default)` | filter | Return every group; groups that did not take part get `default`. | `` {{ '2026-11' \| re.search('(?P<year>\\d+)-(?P<month>\\d+)-?(\\d+)?') \| match.groups \| join('\|') }} `` | `` 2026\|11\|None `` |
|  |  |  | `` {{ '2026-11' \| re.search('(?P<year>\\d+)-(?P<month>\\d+)-?(\\d+)?') \| match.groups('-') \| join('\|') }} `` | `` 2026\|11\|- `` |
| `match.lastgroup` | attribute | The name of the last group that matched, or None. | `` {{ '2026-11' \| re.search('(?P<year>\\d+)-(?P<month>\\d+)-?(\\d+)?') \| match.lastgroup }} `` | `` month `` |
| `match.lastindex` | attribute | The index of the last group that matched, or None. | `` {{ '2026-11' \| re.search('(?P<year>\\d+)-(?P<month>\\d+)-?(\\d+)?') \| match.lastindex }} `` | `` 2 `` |
|  |  |  | `` {{ 'a' \| re.search('a') \| match.lastindex }} `` | `` None `` |
| `match.pos` | attribute | The `pos` the search started from. | `` {{ '2026-11' \| re.search('(?P<year>\\d+)-(?P<month>\\d+)-?(\\d+)?') \| match.pos }} `` | `` 0 `` |
| `match.re` | attribute | The compiled pattern that produced this match. | `` {{ '2026-11' \| re.search('(?P<year>\\d+)-(?P<month>\\d+)-?(\\d+)?') \| match.re \| attr('groups') }} `` | `` 3 `` |
| `match.span(group)` | filter | Return `(start, end)` of a group. | `` {{ '2026-11' \| re.search('(?P<year>\\d+)-(?P<month>\\d+)-?(\\d+)?') \| match.span \| join('-') }} `` | `` 0-7 `` |
|  |  |  | `` {{ '2026-11' \| re.search('(?P<year>\\d+)-(?P<month>\\d+)-?(\\d+)?') \| match.span('month') \| join('-') }} `` | `` 5-7 `` |
| `match.start(group)` | filter | Return the start index of a group. | `` {{ '2026-11' \| re.search('(?P<year>\\d+)-(?P<month>\\d+)-?(\\d+)?') \| match.start(2) }} `` | `` 5 `` |
| `match.string` | attribute | The string that was searched. | `` {{ '2026-11' \| re.search('(?P<year>\\d+)-(?P<month>\\d+)-?(\\d+)?') \| match.string }} `` | `` 2026-11 `` |

### path

| Member | Kinds | Description | Example | Result |
|---|---|---|---|---|
| `path.anchor` | attribute | The drive and root together. | `` {{ w \| path.anchor }} ``<br>with `` w = PureWindowsPath('C:/Users/sara/notes.txt') `` | `` C:\ `` |
| `path.as_posix` | filter | Return the path with forward slashes. | `` {{ w \| path.as_posix }} ``<br>with `` w = PureWindowsPath('C:/Users/sara/notes.txt') `` | `` C:/Users/sara/notes.txt `` |
| `path.as_uri` | filter | Return a `file:` URI. The path must be absolute. | `` {{ x \| path.as_uri }} ``<br>with `` x = PurePosixPath('/srv/a b.txt') `` | `` file:///srv/a%20b.txt `` |
| `path.drive` | attribute | The drive letter or UNC share (empty on POSIX). | `` {{ w \| path.drive }} ``<br>with `` w = PureWindowsPath('C:/Users/sara/notes.txt') `` | `` C: `` |
| `path.is_absolute` | filter, test | Return True if the path has a root (and a drive, on Windows). | `` {{ p \| path.is_absolute }} ``<br>with `` p = PurePosixPath('/srv/docs/report.tar.gz') `` | `` True `` |
|  |  |  | `` {{ x is path.is_absolute }} ``<br>with `` x = PurePosixPath('a/b') `` | `` False `` |
| `path.is_relative_to(other)` | filter, test | Return True if the path is under `other`. | `` {{ p \| path.is_relative_to('/srv') }} ``<br>with `` p = PurePosixPath('/srv/docs/report.tar.gz') `` | `` True `` |
|  |  |  | `` {{ p is path.is_relative_to('/etc') }} ``<br>with `` p = PurePosixPath('/srv/docs/report.tar.gz') `` | `` False `` |
| `path.joinpath(*pathsegments)` | filter | Return the path with the segments appended. | `` {{ p \| path.parent \| path.joinpath('a', 'b.txt') \| path.as_posix }} ``<br>with `` p = PurePosixPath('/srv/docs/report.tar.gz') `` | `` /srv/docs/a/b.txt `` |
| `path.match(path_pattern, case_sensitive)` | filter, test | Return True if the path matches the glob pattern, matched from the right. | `` {{ p \| path.match('*.gz') }} ``<br>with `` p = PurePosixPath('/srv/docs/report.tar.gz') `` | `` True `` |
|  |  |  | `` {{ p is path.match('docs/*.gz') }} ``<br>with `` p = PurePosixPath('/srv/docs/report.tar.gz') `` | `` True `` |
|  |  |  | `` {{ p is path.match('/docs/*') }} ``<br>with `` p = PurePosixPath('/srv/docs/report.tar.gz') `` | `` False `` |
| `path.name` | attribute | The final component. | `` {{ p \| path.name }} ``<br>with `` p = PurePosixPath('/srv/docs/report.tar.gz') `` | `` report.tar.gz `` |
| `path.parent` | attribute | The logical parent. | `` {{ p \| path.parent \| path.as_posix }} ``<br>with `` p = PurePosixPath('/srv/docs/report.tar.gz') `` | `` /srv/docs `` |
| `path.parents` | attribute | Every logical ancestor, nearest first. | `` {{ p \| path.parents \| map('path.as_posix') \| join('\|') }} ``<br>with `` p = PurePosixPath('/srv/docs/report.tar.gz') `` | `` /srv/docs\|/srv\|/ `` |
| `path.parts` | attribute | The components, as a tuple. | `` {{ p \| path.parts \| join('\|') }} ``<br>with `` p = PurePosixPath('/srv/docs/report.tar.gz') `` | `` /\|srv\|docs\|report.tar.gz `` |
| `path.relative_to(other, walk_up)` | filter | Return the path relative to `other`. Raises if it is not under it (unless `walk_up`). | `` {{ p \| path.relative_to('/srv') \| path.as_posix }} ``<br>with `` p = PurePosixPath('/srv/docs/report.tar.gz') `` | `` docs/report.tar.gz `` |
|  |  |  | `` {{ p \| path.relative_to('/srv/web', walk_up=true) \| path.as_posix }} ``<br>with `` p = PurePosixPath('/srv/docs/report.tar.gz') `` | `` ../docs/report.tar.gz `` |
| `path.root` | attribute | The root separator, if any. | `` {{ p \| path.root }} ``<br>with `` p = PurePosixPath('/srv/docs/report.tar.gz') `` | `` / `` |
| `path.stem` | attribute | The final component without its last suffix. | `` {{ p \| path.stem }} ``<br>with `` p = PurePosixPath('/srv/docs/report.tar.gz') `` | `` report.tar `` |
| `path.suffix` | attribute | The last suffix of the final component, with the dot. | `` {{ p \| path.suffix }} ``<br>with `` p = PurePosixPath('/srv/docs/report.tar.gz') `` | `` .gz `` |
| `path.suffixes` | attribute | Every suffix of the final component. | `` {{ p \| path.suffixes \| join }} ``<br>with `` p = PurePosixPath('/srv/docs/report.tar.gz') `` | `` .tar.gz `` |
| `path.with_name(name)` | filter | Return the path with the final component replaced. | `` {{ p \| path.with_name('data.csv') \| path.as_posix }} ``<br>with `` p = PurePosixPath('/srv/docs/report.tar.gz') `` | `` /srv/docs/data.csv `` |
| `path.with_stem(stem)` | filter | Return the path with the stem replaced. | `` {{ p \| path.with_stem('old') \| path.as_posix }} ``<br>with `` p = PurePosixPath('/srv/docs/report.tar.gz') `` | `` /srv/docs/old.gz `` |
| `path.with_suffix(suffix)` | filter | Return the path with the last suffix replaced (or removed with `''`). | `` {{ p \| path.with_suffix('.zip') \| path.as_posix }} ``<br>with `` p = PurePosixPath('/srv/docs/report.tar.gz') `` | `` /srv/docs/report.tar.zip `` |
|  |  |  | `` {{ p \| path.with_suffix('') \| path.as_posix }} ``<br>with `` p = PurePosixPath('/srv/docs/report.tar.gz') `` | `` /srv/docs/report.tar `` |

### pattern

| Member | Kinds | Description | Example | Result |
|---|---|---|---|---|
| `pattern.findall(string, pos, endpos)` | filter | Return every non-overlapping match: strings, or tuples of groups. | `` {% set word = re.compile('\\w+', re.I) %}{{ word \| pattern.findall('Hi, you two') \| join('\|') }} `` | `` Hi\|you\|two `` |
|  |  |  | `` {% set word = re.compile('\\w+', re.I) %}{{ word \| pattern.findall('Hi, you two', 3, 7) \| join('\|') }} `` | `` you `` |
|  |  |  | `` {% set date = re.compile('(?P<year>\\d+)-(?P<month>\\d+)') %}{{ date \| pattern.findall('2026-11 1999-01') \| map('join', '/') \| join }} `` | `` 2026/111999/01 `` |
| `pattern.finditer(string, pos, endpos)` | filter | Return an iterator of match objects. | `` {% set word = re.compile('\\w+', re.I) %}{{ word \| pattern.finditer('ab cde') \| map('match.span') \| map('join', '-') \| join('\|') }} `` | `` 0-2\|3-6 `` |
| `pattern.flags` | attribute | The flags the pattern was compiled with, plus the engine's defaults. | `` {% set word = re.compile('\\w+', re.I) %}{{ (word \| pattern.flags) // re.I % 2 }} `` | `` 1 `` |
| `pattern.fullmatch(string, pos, endpos)` | filter, test | Return the match if the pattern matches all of `string[pos:endpos]`, or None. Also a test. | `` {% set date = re.compile('(?P<year>\\d+)-(?P<month>\\d+)') %}{{ date is pattern.fullmatch('2026-11') }} `` | `` True `` |
|  |  |  | `` {% set date = re.compile('(?P<year>\\d+)-(?P<month>\\d+)') %}{{ date is pattern.fullmatch('2026-11!') }} `` | `` False `` |
|  |  |  | `` {% set date = re.compile('(?P<year>\\d+)-(?P<month>\\d+)') %}{{ date is pattern.fullmatch('2026-11!', 0, 7) }} `` | `` True `` |
| `pattern.groupindex` | attribute | Map each named group to its number. | `` {% set date = re.compile('(?P<year>\\d+)-(?P<month>\\d+)') %}{{ (date \| pattern.groupindex)['month'] }} `` | `` 2 `` |
| `pattern.groups` | attribute | The number of capturing groups. | `` {% set date = re.compile('(?P<year>\\d+)-(?P<month>\\d+)') %}{{ date \| pattern.groups }} `` | `` 2 `` |
| `pattern.match(string, pos, endpos)` | filter, test | Return the match at the start of `string[pos:endpos]`, or None. Also a test. | `` {% set date = re.compile('(?P<year>\\d+)-(?P<month>\\d+)') %}{{ date \| pattern.match('2026-11!') \| match.group('month') }} `` | `` 11 `` |
|  |  |  | `` {% set date = re.compile('(?P<year>\\d+)-(?P<month>\\d+)') %}{{ date is pattern.match('on 2026-11') }} `` | `` False `` |
|  |  |  | `` {% set date = re.compile('(?P<year>\\d+)-(?P<month>\\d+)') %}{{ date is pattern.match('on 2026-11', 3) }} `` | `` True `` |
| `pattern.pattern` | attribute | The pattern string. | `` {% set word = re.compile('\\w+', re.I) %}{{ word \| pattern.pattern }} `` | `` \w+ `` |
| `pattern.search(string, pos, endpos)` | filter, test | Return the first match in `string[pos:endpos]`, or None. Also a test. | `` {% set date = re.compile('(?P<year>\\d+)-(?P<month>\\d+)') %}{{ date \| pattern.search('on 2026-11') \| match.group('year') }} `` | `` 2026 `` |
|  |  |  | `` {% set date = re.compile('(?P<year>\\d+)-(?P<month>\\d+)') %}{{ date is pattern.search('on 2026-11') }} `` | `` True `` |
|  |  |  | `` {% set date = re.compile('(?P<year>\\d+)-(?P<month>\\d+)') %}{{ date \| pattern.search('2026-11', 1) \| match.group }} `` | `` 026-11 `` |
| `pattern.split(string, maxsplit)` | filter | Split `string` by the matches. Groups in the pattern are kept. | `` {{ re.compile(',\\s*') \| pattern.split('a, b,c') \| join('\|') }} `` | `` a\|b\|c `` |
|  |  |  | `` {{ re.compile(',\\s*') \| pattern.split('a, b,c', 1) \| join('\|') }} `` | `` a\|b,c `` |
| `pattern.sub(repl, string, count)` | filter | Replace matches in `string` with `repl`: a string (`\1`, `\g<name>`) or a macro. | `` {% set word = re.compile('\\w+', re.I) %}{{ word \| pattern.sub('#', 'ab, cd') }} `` | `` #, # `` |
|  |  |  | `` {% set word = re.compile('\\w+', re.I) %}{{ word \| pattern.sub('[\\g<0>]', 'ab, cd', 1) }} `` | `` [ab], cd `` |
|  |  |  | `` {% macro up(m) %}{{ m \| match.group(0) \| upper }}{% endmacro %}{% set word = re.compile('\\w+', re.I) %}{{ word \| pattern.sub(up, 'ab, cd') }} `` | `` AB, CD `` |
| `pattern.subn(repl, string, count)` | filter | Like `pattern.sub`, but return `(new_string, number_of_substitutions)`. | `` {% set word = re.compile('\\w+', re.I) %}{{ word \| pattern.subn('#', 'ab, cd') \| join('\|') }} `` | `` #, #\|2 `` |
|  |  |  | `` {% macro up(m) %}{{ m \| match.group(0) \| upper }}{% endmacro %}{% set word = re.compile('\\w+', re.I) %}{{ word \| pattern.subn(up, 'ab, cd', 1) \| join('\|') }} `` | `` AB, cd\|1 `` |

### re

| Member | Kinds | Description | Example | Result |
|---|---|---|---|---|
| `re.escape` | filter | Escape every regex special character in the value. | `` {{ 'a.b*c' \| re.escape }} `` | `` a\.b\*c `` |
| `re.findall(pattern, flags)` | filter | Return every non-overlapping match: strings, or tuples of groups. | `` {{ 'a1 b22 c333' \| re.findall('\\d+') \| join('\|') }} `` | `` 1\|22\|333 `` |
|  |  |  | `` {{ 'a=1 b=2' \| re.findall('(\\w)=(\\d)') \| map('join') \| join('\|') }} `` | `` a1\|b2 `` |
| `re.finditer(pattern, flags)` | filter | Return an iterator of match objects. | `` {{ 'a1 b22' \| re.finditer('\\d+') \| map('match.span') \| map('join', '-') \| join('\|') }} `` | `` 1-2\|4-6 `` |
| `re.fullmatch(pattern, flags)` | filter, test | Return the match if `pattern` matches the whole value, or None. Also a test. | `` {{ '2026' is re.fullmatch('\\d{4}') }} `` | `` True `` |
|  |  |  | `` {{ '2026-11' is re.fullmatch('\\d{4}') }} `` | `` False `` |
| `re.match(pattern, flags)` | filter, test | Return the match of `pattern` at the start of the value, or None. Also a test. | `` {{ '42-ABC' \| re.match('\\d+') \| match.group }} `` | `` 42 `` |
|  |  |  | `` {{ 'ABC-42' is re.match('\\d') }} `` | `` False `` |
| `re.search(pattern, flags)` | filter, test | Return the first match of `pattern` anywhere in the value, or None. Also a test. | `` {{ 'ABC-42' \| re.search('abc-(\\d+)', flags=re.I) \| match.group(1) }} `` | `` 42 `` |
|  |  |  | `` {{ 'ABC-42' is re.search('\\d') }} `` | `` True `` |
|  |  |  | `` {{ 'ABC' \| re.search('\\d') }} `` | `` None `` |
| `re.split(pattern, maxsplit, flags)` | filter | Split the value by the matches of `pattern`. Groups in the pattern are kept. | `` {{ 'a, b,c' \| re.split(',\\s*') \| join('\|') }} `` | `` a\|b\|c `` |
|  |  |  | `` {{ 'a, b,c' \| re.split(',\\s*', 1) \| join('\|') }} `` | `` a\|b,c `` |
|  |  |  | `` {{ 'aXbxc' \| re.split('x', flags=re.I) \| join('\|') }} `` | `` a\|b\|c `` |
| `re.sub(pattern, repl, count, flags)` | filter | Replace matches with `repl`: a string (`\1`, `\g<name>`) or a macro taking the match. | `` {{ 'a1 b22' \| re.sub('\\d+', '#') }} `` | `` a# b# `` |
|  |  |  | `` {{ 'a1 b22' \| re.sub('(\\w)(\\d+)', '\\2\\1', 1) }} `` | `` 1a b22 `` |
|  |  |  | `` {{ '2026-11-22' \| re.sub('(?P<y>\\d+)-(\\d+)-(\\d+)', '\\3/\\2/\\g<y>') }} `` | `` 22/11/2026 `` |
|  |  |  | `` {% macro up(m) %}{{ m \| match.group(0) \| upper }}{% endmacro %}{{ 'a1 b2' \| re.sub('[a-z]', up) }} `` | `` A1 B2 `` |
| `re.subn(pattern, repl, count, flags)` | filter | Like `re.sub`, but return `(new_string, number_of_substitutions)`. | `` {{ 'a1 b22' \| re.subn('\\d', '#') \| join('\|') }} `` | `` a# b##\|3 `` |
|  |  |  | `` {% macro up(m) %}{{ m \| match.group(0) \| upper }}{% endmacro %}{{ 'a1 b2' \| re.subn('[a-z]', up, 1) \| join('\|') }} `` | `` A1 b2\|1 `` |

### str

| Member | Kinds | Description | Example | Result |
|---|---|---|---|---|
| `str.capitalize` | filter | Return a copy with the first character upper-cased and the rest lower-cased. | `` {{ 'hello world' \| str.capitalize }} `` | `` Hello world `` |
| `str.casefold` | filter | Return a casefolded copy, for caseless comparisons. | `` {{ 'Straße' \| str.casefold }} `` | `` strasse `` |
| `str.center(width, fillchar)` | filter | Return the string centered in a field of `width`. | `` {{ 'ab' \| str.center(6, '*') }} `` | `` **ab** `` |
| `str.count(sub, start, end)` | filter | Return the number of non-overlapping occurrences of `sub`. | `` {{ 'banana' \| str.count('a') }} `` | `` 3 `` |
|  |  |  | `` {{ 'banana' \| str.count('a', 2) }} `` | `` 2 `` |
| `str.encode(encoding, errors)` | filter | Encode to bytes. | `` {{ 'é' \| str.encode \| length }} `` | `` 2 `` |
|  |  |  | `` {{ 'é' \| str.encode('ascii', errors='replace') \| length }} `` | `` 1 `` |
| `str.endswith(suffix, start, end)` | filter, test | Return True if the string ends with `suffix` (or any suffix in a tuple). | `` {{ 'report.pdf' \| str.endswith('.pdf') }} `` | `` True `` |
|  |  |  | `` {{ 'a.txt' is str.endswith(('.pdf', '.txt')) }} `` | `` True `` |
| `str.expandtabs(tabsize)` | filter | Return a copy with tabs expanded to spaces. | `` {{ 'a\tb' \| str.expandtabs(4) }} `` | `` a   b `` |
| `str.find(sub, start, end)` | filter | Return the lowest index of `sub`, or -1. | `` {{ 'banana' \| str.find('n') }} `` | `` 2 `` |
|  |  |  | `` {{ 'banana' \| str.find('x') }} `` | `` -1 `` |
| `str.format(*args, **kwargs)` | filter | Format the string with `str.format` (sandboxed: no unsafe attribute access). | `` {{ '{} has {:,} items' \| str.format('Cart', 1500) }} `` | `` Cart has 1,500 items `` |
|  |  |  | `` {{ 'Hi {name}' \| str.format(name='Sam') }} `` | `` Hi Sam `` |
| `str.format_map(mapping)` | filter | Format the string with values from `mapping` (sandboxed). | `` {{ '{a}-{b}' \| str.format_map({'a': 1, 'b': 2}) }} `` | `` 1-2 `` |
| `str.index(sub, start, end)` | filter | Like `find`, but raise when `sub` is not found. | `` {{ 'banana' \| str.index('n', 3) }} `` | `` 4 `` |
| `str.isalnum` | filter, test | Return True if all characters are alphanumeric. | `` {{ 'abc123' \| str.isalnum }} `` | `` True `` |
|  |  |  | `` {{ 'a b' is str.isalnum }} `` | `` False `` |
| `str.isalpha` | filter, test | Return True if all characters are alphabetic. | `` {{ 'abc' \| str.isalpha }} `` | `` True `` |
| `str.isascii` | filter, test | Return True if all characters are ASCII. | `` {{ 'abc' \| str.isascii }} `` | `` True `` |
|  |  |  | `` {{ 'é' is str.isascii }} `` | `` False `` |
| `str.isdecimal` | filter, test | Return True if all characters are decimal characters. | `` {{ '123' \| str.isdecimal }} `` | `` True `` |
| `str.isdigit` | filter, test | Return True if all characters are digits. | `` {{ '²' \| str.isdigit }} `` | `` True `` |
|  |  |  | `` {% if code is str.isdigit %}ok{% endif %} ``<br>with `` code = '2026' `` | `` ok `` |
| `str.isidentifier` | filter, test | Return True if the string is a valid Python identifier. | `` {{ 'my_var' \| str.isidentifier }} `` | `` True `` |
| `str.islower` | filter, test | Return True if all cased characters are lower case. | `` {{ 'abc' \| str.islower }} `` | `` True `` |
| `str.isnumeric` | filter, test | Return True if all characters are numeric. | `` {{ '½' \| str.isnumeric }} `` | `` True `` |
| `str.isprintable` | filter, test | Return True if all characters are printable. | `` {{ text \| str.isprintable }} ``<br>with `` text = 'a\nb' `` | `` False `` |
| `str.isspace` | filter, test | Return True if all characters are whitespace. | `` {{ '  ' \| str.isspace }} `` | `` True `` |
| `str.istitle` | filter, test | Return True if the string is title-cased. | `` {{ 'Hello World' \| str.istitle }} `` | `` True `` |
| `str.isupper` | filter, test | Return True if all cased characters are upper case. | `` {{ 'ABC' \| str.isupper }} `` | `` True `` |
| `str.join(iterable)` | filter | Join the strings in `iterable` with the value as separator (`sep \| str.join(items)`). | `` {{ ', ' \| str.join(items) }} ``<br>with `` items = ['a', 'b'] `` | `` a, b `` |
|  |  |  | `` {{ '-' \| str.join('abc') }} `` | `` a-b-c `` |
| `str.ljust(width, fillchar)` | filter | Return the string left-justified in a field of `width`. | `` {{ 'ab' \| str.ljust(4, '.') }} `` | `` ab.. `` |
| `str.lower` | filter | Return a lower-cased copy. | `` {{ 'ABC' \| str.lower }} `` | `` abc `` |
| `str.lstrip(chars)` | filter | Return a copy with leading `chars` (default whitespace) removed. | `` {{ '  ab' \| str.lstrip }} `` | `` ab `` |
|  |  |  | `` {{ 'xxab' \| str.lstrip('x') }} `` | `` ab `` |
| `str.partition(sep)` | filter | Split at the first `sep`: `(head, sep, tail)`. | `` {{ 'key=value' \| str.partition('=') \| join('\|') }} `` | `` key\|=\|value `` |
| `str.removeprefix(prefix)` | filter | Return a copy without `prefix`, if it starts with it. | `` {{ 'INV-001' \| str.removeprefix('INV-') }} `` | `` 001 `` |
| `str.removesuffix(suffix)` | filter | Return a copy without `suffix`, if it ends with it. | `` {{ 'report.pdf' \| str.removesuffix('.pdf') }} `` | `` report `` |
| `str.replace(old, new, count)` | filter | Return a copy with `old` replaced by `new` (at most `count` times). | `` {{ 'a-b-c' \| str.replace('-', '/') }} `` | `` a/b/c `` |
|  |  |  | `` {{ 'a-b-c' \| str.replace('-', '/', 1) }} `` | `` a/b-c `` |
| `str.rfind(sub, start, end)` | filter | Return the highest index of `sub`, or -1. | `` {{ 'banana' \| str.rfind('a') }} `` | `` 5 `` |
| `str.rindex(sub, start, end)` | filter | Like `rfind`, but raise when `sub` is not found. | `` {{ 'banana' \| str.rindex('n') }} `` | `` 4 `` |
| `str.rjust(width, fillchar)` | filter | Return the string right-justified in a field of `width`. | `` {{ '42' \| str.rjust(5, '0') }} `` | `` 00042 `` |
| `str.rpartition(sep)` | filter | Split at the last `sep`: `(head, sep, tail)`. | `` {{ 'a.b.c' \| str.rpartition('.') \| join('\|') }} `` | `` a.b\|.\|c `` |
| `str.rsplit(sep, maxsplit)` | filter | Split from the right on `sep`, at most `maxsplit` times. | `` {{ 'a,b,c' \| str.rsplit(',', 1) \| join('\|') }} `` | `` a,b\|c `` |
|  |  |  | `` {{ 'a b c' \| str.rsplit(maxsplit=1) \| join('\|') }} `` | `` a b\|c `` |
| `str.rstrip(chars)` | filter | Return a copy with trailing `chars` (default whitespace) removed. | `` {{ 'ab  ' \| str.rstrip ~ '\|' }} `` | `` ab\| `` |
| `str.split(sep, maxsplit)` | filter | Split on `sep` (default runs of whitespace), at most `maxsplit` times. | `` {{ 'a,b,c' \| str.split(',') \| join('\|') }} `` | `` a\|b\|c `` |
|  |  |  | `` {{ ' a  b ' \| str.split \| join('\|') }} `` | `` a\|b `` |
|  |  |  | `` {{ 'a b c' \| str.split(maxsplit=1) \| join('\|') }} `` | `` a\|b c `` |
| `str.splitlines(keepends)` | filter | Split at line boundaries. | `` {{ text \| str.splitlines \| join('\|') }} ``<br>with `` text = 'one\ntwo' `` | `` one\|two `` |
|  |  |  | `` {{ text \| str.splitlines(keepends=True) \| length }} ``<br>with `` text = 'a\nb' `` | `` 2 `` |
| `str.startswith(prefix, start, end)` | filter, test | Return True if the string starts with `prefix` (or any prefix in a tuple). | `` {{ 'INV-001' \| str.startswith('INV') }} `` | `` True `` |
|  |  |  | `` {% if 'INV-001' is str.startswith(('INV', 'CR')) %}yes{% endif %} `` | `` yes `` |
| `str.strip(chars)` | filter | Return a copy with leading and trailing `chars` (default whitespace) removed. | `` {{ '  ab  ' \| str.strip ~ '\|' }} `` | `` ab\| `` |
|  |  |  | `` {{ '--ab--' \| str.strip('-') }} `` | `` ab `` |
| `str.swapcase` | filter | Return a copy with upper case and lower case swapped. | `` {{ 'aBc' \| str.swapcase }} `` | `` AbC `` |
| `str.title` | filter | Return a title-cased copy. | `` {{ 'hello world' \| str.title }} `` | `` Hello World `` |
| `str.translate(table)` | filter | Map characters through `table` (code point → string, code point or None to delete). | `` {{ 'abc' \| str.translate({97: 'A', 98: none}) }} `` | `` Ac `` |
| `str.upper` | filter | Return an upper-cased copy. | `` {{ 'abc' \| str.upper }} `` | `` ABC `` |
| `str.zfill(width)` | filter | Pad a numeric string with zeros on the left, after any sign. | `` {{ '42' \| str.zfill(5) }} `` | `` 00042 `` |
|  |  |  | `` {{ '-42' \| str.zfill(5) }} `` | `` -0042 `` |

### time

| Member | Kinds | Description | Example | Result |
|---|---|---|---|---|
| `time.dst` | filter | Return the daylight saving offset, or None if unknown. | `` {{ x \| time.dst }} ``<br>with `` x = datetime.time(14, 30, 5, 250) `` | `` None `` |
| `time.fold` | attribute | 0 or 1: which of two repeated wall times this is. | `` {{ x \| time.fold }} ``<br>with `` x = datetime.time(14, 30, 5, 250) `` | `` 0 `` |
| `time.fromisoformat` | filter | Parse an ISO time (classmethod; the string is piped in). | `` {{ '14:30' \| time.fromisoformat }} `` | `` 14:30:00 `` |
| `time.hour` | attribute | The hour, 0 to 23. | `` {{ x \| time.hour }} ``<br>with `` x = datetime.time(14, 30, 5, 250) `` | `` 14 `` |
| `time.isoformat(timespec)` | filter | Return the time in ISO 8601 format. | `` {{ x \| time.isoformat }} ``<br>with `` x = datetime.time(14, 30, 5, 250) `` | `` 14:30:05.000250 `` |
|  |  |  | `` {{ x \| time.isoformat('minutes') }} ``<br>with `` x = time(...) `` | `` 12:00+03:00 `` |
| `time.microsecond` | attribute | The microsecond. | `` {{ x \| time.microsecond }} ``<br>with `` x = datetime.time(14, 30, 5, 250) `` | `` 250 `` |
| `time.minute` | attribute | The minute. | `` {{ x \| time.minute }} ``<br>with `` x = datetime.time(14, 30, 5, 250) `` | `` 30 `` |
| `time.replace(hour, minute, second, microsecond, tzinfo, fold)` | filter | Return the time with the given fields replaced. `tzinfo=none` makes it naive. | `` {{ x \| time.replace(second=0, microsecond=0) }} ``<br>with `` x = datetime.time(14, 30, 5, 250) `` | `` 14:30:00 `` |
|  |  |  | `` {{ x \| time.replace(tzinfo=none) }} ``<br>with `` x = time(...) `` | `` 12:00:00 `` |
| `time.second` | attribute | The second. | `` {{ x \| time.second }} ``<br>with `` x = datetime.time(14, 30, 5, 250) `` | `` 5 `` |
| `time.strftime(format)` | filter | Format the time with a `strftime` format string. | `` {{ x \| time.strftime('%H.%M') }} ``<br>with `` x = datetime.time(14, 30, 5, 250) `` | `` 14.30 `` |
| `time.tzinfo` | attribute | The timezone, or None for a naive time. | `` {{ x \| time.tzinfo }} ``<br>with `` x = time(...) `` | `` UTC+03:00 `` |
| `time.tzname` | filter | Return the timezone name, or None for a naive time. | `` {{ x \| time.tzname }} ``<br>with `` x = time(...) `` | `` UTC+03:00 `` |
| `time.utcoffset` | filter | Return the UTC offset, or None for a naive time. | `` {{ x \| time.utcoffset }} ``<br>with `` x = time(...) `` | `` 3:00:00 `` |

### timedelta

| Member | Kinds | Description | Example | Result |
|---|---|---|---|---|
| `timedelta.days` | attribute | The days part. | `` {{ x \| timedelta.days }} ``<br>with `` x = datetime.timedelta(days=1, seconds=3601, microseconds=500) `` | `` 1 `` |
| `timedelta.microseconds` | attribute | The microseconds part, below one second. | `` {{ x \| timedelta.microseconds }} ``<br>with `` x = datetime.timedelta(days=1, seconds=3601, microseconds=500) `` | `` 500 `` |
| `timedelta.seconds` | attribute | The seconds part, below one day. | `` {{ x \| timedelta.seconds }} ``<br>with `` x = datetime.timedelta(days=1, seconds=3601, microseconds=500) `` | `` 3601 `` |
| `timedelta.total_seconds` | filter | Return the whole duration in seconds. | `` {{ x \| timedelta.total_seconds }} ``<br>with `` x = datetime.timedelta(days=1, seconds=3601, microseconds=500) `` | `` 90001.0005 `` |

### uuid

| Member | Kinds | Description | Example | Result |
|---|---|---|---|---|
| `uuid.bytes` | attribute | The 16 bytes, big-endian. | `` {{ u \| uuid.bytes \| list \| first }} ``<br>with `` u = UUID('c232ab00-9414-11ec-b3c8-9f6bdeced846') `` | `` 194 `` |
| `uuid.bytes_le` | attribute | The 16 bytes, with the first three fields little-endian. | `` {{ u \| uuid.bytes_le \| list \| first }} ``<br>with `` u = UUID('c232ab00-9414-11ec-b3c8-9f6bdeced846') `` | `` 0 `` |
| `uuid.clock_seq` | attribute | The 14-bit clock sequence. | `` {{ u \| uuid.clock_seq }} ``<br>with `` u = UUID('c232ab00-9414-11ec-b3c8-9f6bdeced846') `` | `` 13256 `` |
| `uuid.clock_seq_hi_variant` | attribute | The high byte of the clock sequence, with the variant bits. | `` {{ u \| uuid.clock_seq_hi_variant }} ``<br>with `` u = UUID('c232ab00-9414-11ec-b3c8-9f6bdeced846') `` | `` 179 `` |
| `uuid.clock_seq_low` | attribute | The low byte of the clock sequence. | `` {{ u \| uuid.clock_seq_low }} ``<br>with `` u = UUID('c232ab00-9414-11ec-b3c8-9f6bdeced846') `` | `` 200 `` |
| `uuid.fields` | attribute | The six integer fields. | `` {{ u \| uuid.fields \| join('\|') }} ``<br>with `` u = UUID('c232ab00-9414-11ec-b3c8-9f6bdeced846') `` | `` 3258100480\|37908\|4588\|179\|200\|175285648414790 `` |
| `uuid.hex` | attribute | The 32 hex digits, without dashes. | `` {{ u \| uuid.hex }} ``<br>with `` u = UUID('c232ab00-9414-11ec-b3c8-9f6bdeced846') `` | `` c232ab00941411ecb3c89f6bdeced846 `` |
| `uuid.int` | attribute | The UUID as a 128-bit integer. | `` {{ u \| uuid.int }} ``<br>with `` u = UUID('c232ab00-9414-11ec-b3c8-9f6bdeced846') `` | `` 258133314363070689776975542038781941830 `` |
| `uuid.is_safe` | attribute | Whether the UUID was generated in a multiprocessing-safe way. | `` {{ u \| uuid.is_safe }} ``<br>with `` u = UUID('c232ab00-9414-11ec-b3c8-9f6bdeced846') `` | `` SafeUUID.unknown `` |
| `uuid.node` | attribute | The 48-bit node id (meaningful for version 1). | `` {{ u \| uuid.node }} ``<br>with `` u = UUID('c232ab00-9414-11ec-b3c8-9f6bdeced846') `` | `` 175285648414790 `` |
| `uuid.time` | attribute | The 60-bit timestamp (meaningful for version 1). | `` {{ u \| uuid.time }} ``<br>with `` u = UUID('c232ab00-9414-11ec-b3c8-9f6bdeced846') `` | `` 138648505420000000 `` |
| `uuid.time_hi_version` | attribute | The next 16 bits, with the version bits. | `` {{ u \| uuid.time_hi_version }} ``<br>with `` u = UUID('c232ab00-9414-11ec-b3c8-9f6bdeced846') `` | `` 4588 `` |
| `uuid.time_low` | attribute | The first 32 bits of the UUID. | `` {{ u \| uuid.time_low }} ``<br>with `` u = UUID('c232ab00-9414-11ec-b3c8-9f6bdeced846') `` | `` 3258100480 `` |
| `uuid.time_mid` | attribute | The next 16 bits of the UUID. | `` {{ u \| uuid.time_mid }} ``<br>with `` u = UUID('c232ab00-9414-11ec-b3c8-9f6bdeced846') `` | `` 37908 `` |
| `uuid.urn` | attribute | The UUID as a URN. | `` {{ u \| uuid.urn }} ``<br>with `` u = UUID('c232ab00-9414-11ec-b3c8-9f6bdeced846') `` | `` urn:uuid:c232ab00-9414-11ec-b3c8-9f6bdeced846 `` |
| `uuid.variant` | attribute | The variant, as one of the `uuid.RESERVED_*` / `uuid.RFC_4122` strings. | `` {{ u \| uuid.variant }} ``<br>with `` u = UUID('c232ab00-9414-11ec-b3c8-9f6bdeced846') `` | `` specified in RFC 4122 `` |
| `uuid.version` | attribute | The version number (1 to 8), or None if the variant is not RFC 4122. | `` {{ u \| uuid.version }} ``<br>with `` u = UUID('c232ab00-9414-11ec-b3c8-9f6bdeced846') `` | `` 1 `` |

<!-- reference:end -->
