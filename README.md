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

The full reference is in [docs/](docs/index.md), generated from the catalog. The same catalog is
available from the command line:

```
jinja-types catalog --namespace str --format markdown
jinja-types catalog --kind test            # JSON, see schema/catalog.schema.json
jinja-types conflicts --plugins
```

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
