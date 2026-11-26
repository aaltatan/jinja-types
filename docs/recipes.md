# Recipes

Every recipe assumes an environment with the extension:

```python
from jinja2.sandbox import ImmutableSandboxedEnvironment

from jinja_types import TypesExtension

env = ImmutableSandboxedEnvironment(extensions=[TypesExtension])
```

## Money: round half-up, then group thousands

```jinja
{{ salary | decimal.quantize(decimal.Decimal("0.01"), rounding=decimal.ROUND_HALF_UP) | fmt(",.2f") }}
```

With `salary = Decimal("1500.005")` this gives `1,500.01`. The global `decimal` holds `Decimal`
and the `ROUND_*` constants; the filter namespace `decimal.*` holds the `Decimal` methods.

## Amounts typed by people

Strip separators and convert to `Decimal` before doing arithmetic:

```jinja
{{ "1,250" | str.replace(",", "") | to_decimal * 2 }}   {# 2500 #}
```

## Dates from strings

```jinja
{{ "2026-01-05" | to_date | date.strftime("%d/%m/%Y") }}            {# 05/01/2026 #}
{{ "05/01/2026" | to_date("%d/%m/%Y") | date.isoformat }}           {# 2026-01-05 #}
```

When most of your context is strings (JSON, CSV), configure `coerce=True` instead and skip the
`to_*` step. See [Strict values and conversion](guide/conversion.md#coercion).

## Local time in another zone

`datetime.astimezone` also takes an IANA timezone name:

```jinja
{{ moment | datetime.astimezone("Asia/Damascus") | datetime.isoformat }}
```

On Windows, install `tzdata` so the name resolves.

## Optional fields

Render a dash for missing values instead of raising:

```python
env = ImmutableSandboxedEnvironment(
    extensions=[TypesExtension.configure(none_passthrough=True)],
)
```

```jinja
{{ middle_name | str.title | default("-", true) }}
```

## Codes and padding

```jinja
{{ code | str.zfill(5) }}                                {# 42 → 00042 #}
{% if code is str.isdigit %}numeric{% endif %}
{{ code | re.search("abc-(\\d+)", flags=re.I) | match.group(1) }}
```

## Sort without touching the input

```jinja
{{ items | list.sort(reverse=true) | join(", ") }}
```

`items` is unchanged afterwards: mutating methods return a new list.

## Highlight words safely

With autoescape on, a macro replacement keeps its markup and the rest is escaped once:

```jinja
{% macro mark(m) %}<mark>{{ m.group(0) }}</mark>{% endmacro %}
{{ text | re.sub("(?i)" ~ term, mark) }}
```

## Repeatable random output

```jinja
{% set rng = random.Random(42) %}{{ rng.randint(1, 6) }}
```

## Arabic amounts in words

Define the currency in Python (see [Locales and Arabic](guide/locale.md)), then:

```jinja
{{ salary | ar.to_words(syp) }}       {# ألف وخمسمئة ليرة سورية #}
{{ salary | ar.format_money(syp) }}   {# ١٬٥٠٠ ل.س #}
```
