# User guide

This page explains the few rules every jinja-types member follows. The other pages cover one
topic each, and [Types and namespaces](types/index.md) lists every member.

## Qualified names

Every type member is reachable only as `namespace.member`. The namespace is the lower-case type
name, and the member is the Python method or attribute name:

```jinja
{{ code | str.zfill(5) }}
{{ amount | decimal.quantize(decimal.Decimal("0.01")) }}
{{ invoice_date | date.strftime("%d/%m/%Y") }}
{{ "docs/readme.md" | to_path | path.stem }}
```

The piped value is always `self`. Parameter names and order match Python, so
`str.center(6, "*")` and `list.sort(reverse=true)` mean what they mean in Python.

Helpers that are not type members use plain names: `fmt`, `to_str`, `to_int`, `to_float`,
`to_bool`, `to_decimal`, `to_fraction`, `to_date`, `to_datetime`, `to_time`, `to_timedelta`,
`to_uuid`, `to_path`. See [helpers](types/helpers.md).

## Filters, tests, attributes and globals

| Kind | Template use | Example |
|---|---|---|
| filter | `{{ x | ns.member(...) }}` | `{{ code | str.zfill(5) }}` |
| test | `{% if x is ns.member %}` | `{% if code is str.isdigit %}` |
| attribute | `{{ x | ns.member }}` (no arguments) | `{{ moment | date.year }}` |
| global | `{{ name(...) }}` or `{{ name.attr }}` | `{{ today() }}`, `decimal.ROUND_HALF_UP` |

A member that returns `bool` is registered as a filter **and** a test. `re.search`, `re.match`
and `re.fullmatch` are tests too: the test is true when there is a match.

Classmethods are parsing filters: the piped value is their first argument, as in
`{{ "2026-01-05" | date.fromisoformat }}` or `{{ text | datetime.strptime("%d/%m/%Y") }}`.

## Globals

Constants are globals only. Globals and filters live in separate Jinja namespaces, so the global
`decimal` and the filter `decimal.quantize` coexist.

| Global | Holds |
|---|---|
| `decimal` | `Decimal`, `Context` and the `ROUND_*` constants |
| `re` | the flags (`re.I`, `re.M`, `re.S`, `re.X`, `re.A`, …) and `re.compile` |
| `random` | the `random` functions on a private generator; `random.Random(seed)` for repeatable output |
| `secrets` | `token_hex`, `token_urlsafe`, `choice`, `randbelow` |
| `today()`, `now(tz=None)` | the current date and datetime |
| `uuid1()`, `uuid4()`, `uuid5(...)` | new UUIDs |

```jinja
{% set rng = random.Random(42) %}{{ rng.randint(1, 6) }}
```

## Dispatch within subclasses

A member of a parent namespace also accepts subclass values, and calls the subclass version when
one is registered. `date.*` filters accept a `datetime`, and `date.isoformat` on a datetime calls
`datetime.isoformat`:

```jinja
{{ moment | date.isoformat(" ", "seconds") }}   {# 2026-01-05 09:30:15 #}
{{ moment | date.year }}                        {# 2026 #}
```

The `datetime.*` namespace holds only what `datetime` adds or overrides. `bool` is a subclass of
`int`, so every `int.*` filter accepts `true` and `false`. A value that is not an instance of the
namespace type raises `JinjaTypesError` (see [Strict values and conversion](conversion.md)).

## Mutating methods work on copies

`list.append`, `extend`, `insert`, `remove`, `reverse`, `sort`, `clear` and `dict.update`,
`dict.clear` return a **new** object and leave the input alone. `list.pop`, `dict.pop`,
`dict.popitem` and `dict.setdefault` return what Python returns (the item), computed on a copy.

```jinja
{{ items | list.sort(reverse=true) | join(",") }}   {# 3,2,1 #}
{{ items | join(",") }}                             {# 3,1,2: unchanged #}
{{ prices | dict.update(tax=5) | dict.keys | list }}
```

## Pure paths only

`path.*` exposes only `PurePath` members. Nothing reads or writes the disk.

## Topics

- [Setup and options](setup.md)
- [Strict values and conversion](conversion.md)
- [Regular expressions](regex.md)
- [Locales and Arabic](locale.md)
- [Registries and the catalog](registry.md)
- [Writing a plugin](plugins.md)
- [Types and namespaces](types/index.md)
