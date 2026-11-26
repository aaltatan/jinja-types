# Strict values and conversion

jinja-types is strict by default: a missing value or a value of the wrong type raises
`JinjaTypesError` instead of rendering something surprising. Two options make it lenient where
you want it.

## Missing values

`None`, `""` and undefined values raise:

```jinja
{{ name | str.upper }}
```

```text
str.upper: got None. Hint: pass a value, or install with none_passthrough=True.
```

With `TypesExtension.configure(none_passthrough=True)`, the value is returned unchanged, so
Jinja's own `default` filter can take over:

```jinja
{{ name | str.upper | default("-", true) }}   {# - #}
```

## Wrong types and explicit conversion

A value must be an instance of the namespace type (or a subclass, see
[dispatch](index.md#dispatch-within-subclasses)). Strings from forms, JSON or CSV must be
converted first:

```jinja
{{ "2026-01-05" | date.strftime("%d/%m") }}
```

```text
date.strftime: got 'str', expected date | datetime. Hint: convert first with '| to_date' or '| date.fromisoformat'.
```

```jinja
{{ "2026-01-05" | to_date | date.strftime("%d/%m/%Y") }}   {# 05/01/2026 #}
{{ "1,250" | str.replace(",", "") | to_decimal * 2 }}      {# 2500 #}
{{ "yes" | to_bool }} {{ "3/4" | to_fraction + 1 }} {{ 90 | to_timedelta }}
{# True 7/4 0:01:30 #}
```

The `to_*` helpers are plain-name filters:

| Helper | Accepts | Notes |
|---|---|---|
| `to_str` | anything | `str(value)` |
| `to_int(base=10)` | `str`, numbers | numbers are truncated like `int()` |
| `to_float` | `str`, numbers | |
| `to_bool` | `str`, `int` | strict: true/yes/on/1 or false/no/off/0, any case |
| `to_decimal` | `str`, `float`, `Decimal` | floats go through `repr()`, so `0.1` gives `Decimal('0.1')` |
| `to_fraction` | `str`, numbers | `'3/4'`, `'0.75'` |
| `to_date(format=None)` | `str`, `date` | ISO, or `strptime` with `format`; a datetime gives its date |
| `to_datetime(format=None)` | `str`, `date` | ISO, or `strptime`; a date becomes midnight |
| `to_time(format=None)` | `str`, `time`, `datetime` | ISO, or `strptime` |
| `to_timedelta` | seconds or `str(timedelta)` text | plus `days`, `hours`, `minutes` |
| `to_uuid` | `str`, `UUID` | |
| `to_path` | `str`, `PurePath` | never touches the disk |

`fmt(spec)` is `format(value, spec)`, for numbers, `Decimal` and dates. All of them are listed
with examples on the [helpers](types/helpers.md) page.

## Coercion

With `TypesExtension.configure(coerce=True)`, a `str` is converted to the namespace type with
that namespace's `parse` function before the call:

```jinja
{{ "2026-01-05" | date.strftime("%d/%m") }}   {# 05/01 #}
{{ "42" | int.bit_length }}                   {# 6 #}
```

A string that does not parse raises `JinjaTypesError` with the same conversion hint. Parsing
filters (classmethods such as `date.fromisoformat`) and plain-name helpers are never coerced.

## Errors from the call itself

Any exception the underlying Python member raises becomes a `JinjaTypesError` that names the
member. A `TypeError` gets the member's signature as hint:

```text
str.zfill: TypeError: 'str' object cannot be interpreted as an integer. Hint: check the arguments: str.zfill(width: int).
```

See [Exceptions](../reference/exceptions.md) for the attributes the error carries.
