# jinja-types

`jinja-types` is a Jinja2 extension that exposes the methods and attributes of everyday Python
types (`str`, `int`, `float`, `bool`, `Decimal`, `Fraction`, `date`, `datetime`, `time`,
`timedelta`, `list`, `dict`, `UUID`, `PurePath`) and the `re` module as Jinja filters and tests.
Names and parameters match Python exactly, everything works in `ImmutableSandboxedEnvironment`,
and a registry makes it easy to plug in new filter sets.

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
`{{ code | re.search("abc-(\d+)", flags=re.I) | match.group(1) }}`. Jinja string literals
process backslash escapes, so write `\d` for the regex `\d`. `re.sub` also accepts a macro that
gets the match; under autoescape its output is kept as markup and the rest of the string is
escaped once. With the `[regex]` extra, the `regex` library is used and every call is limited
by `regex_timeout` (seconds, default 1.0).

The full reference is in [docs/](docs/index.md), generated from the catalog. The same catalog is
available from the command line:

```
jinja-types catalog --namespace str --format markdown
jinja-types catalog --kind test            # JSON, see schema/catalog.schema.json
jinja-types conflicts --plugins
```
